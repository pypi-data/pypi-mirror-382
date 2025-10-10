"""DynamoDB backend implementation."""

from contextlib import AsyncExitStack
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, cast, override

import aioboto3
from asyncache import cached
from boto3.dynamodb.conditions import Attr
from cachetools import Cache
from types_aiobotocore_dynamodb import DynamoDBServiceResource
from types_aiobotocore_dynamodb.service_resource import Table as DynamoTable

from sifts.io.db.base import DatabaseBackend
from sifts.io.db.types import AnalysisFacet, SafeFacet, SnippetFacet, VulnerableFacet


class DynamoDBBackend(DatabaseBackend):
    """DynamoDB implementation of the database backend."""

    def __init__(self) -> None:
        """Initialize DynamoDB backend."""
        self.session = aioboto3.Session()
        self.context_stack: AsyncExitStack | None = None
        self.resource: DynamoDBServiceResource | None = None
        self.table_resources: dict[str, DynamoTable] = {}
        self._startup_complete = False

    @override
    async def startup(self) -> None:
        """Initialize the DynamoDB connection."""
        if self._startup_complete:
            return

        self.context_stack = AsyncExitStack()
        self.resource = await self.context_stack.enter_async_context(
            self.session.resource(
                service_name="dynamodb",
                use_ssl=True,
                verify=True,
            ),
        )
        self._startup_complete = True

    @override
    async def shutdown(self) -> None:
        """Close the DynamoDB connection."""
        if self.context_stack:
            await self.context_stack.aclose()
            self.context_stack = None
            self.resource = None
            self._startup_complete = False

    async def _get_resource(self) -> DynamoDBServiceResource:
        """Get the DynamoDB resource, initializing if necessary."""
        if self.resource is None:
            await self.startup()
        return cast(DynamoDBServiceResource, self.resource)

    async def _get_table(self, table_name: str) -> DynamoTable:
        """Get a DynamoDB table resource."""
        if table_name not in self.table_resources:
            resource = await self._get_resource()
            self.table_resources[table_name] = await resource.Table(table_name)
        return self.table_resources[table_name]

    @staticmethod
    def _serialize(object_: object) -> Any:  # noqa: ANN401
        """Serialize objects for DynamoDB storage."""
        # Mappings
        if isinstance(object_, dict):
            return {k: DynamoDBBackend._serialize(v) for k, v in object_.items()}

        if isinstance(object_, (list, tuple, set)):
            return [DynamoDBBackend._serialize(o) for o in object_]

        # Scalars
        if isinstance(object_, datetime):
            return object_.astimezone(tz=UTC).isoformat()
        if isinstance(object_, float):
            return Decimal(str(object_))
        if isinstance(object_, Enum):
            return object_.value

        return object_

    @override
    async def insert_snippet(self, snippet: SnippetFacet) -> None:
        """Insert a snippet into DynamoDB using unified format aligned with Snowflake."""
        table = await self._get_table("sifts_state")
        pk = f"GROUP#{snippet.group_name}#ROOT#{snippet.root_nickname}"
        sk = f"SNIPPET#PATH#{snippet.path}#HASH#{snippet.code_sha256}"
        item = snippet.model_dump()
        item["pk"] = pk
        item["sk"] = sk
        await table.put_item(Item=self._serialize(item))

    @override
    async def insert_analysis(self, analysis: AnalysisFacet) -> None:
        """Insert an analysis result into DynamoDB."""
        table = await self._get_table("sifts_state")
        pk = f"GROUP#{analysis.group_name}#ROOT#{analysis.root_nickname}"
        candidates_ids = "-".join(sorted(analysis.vulnerability_id_candidates))
        sk = (
            f"ANALYSIS#VERSION#{analysis.version}#PATH#{analysis.path}#SNIPPET#{analysis.snippet_hash_id}"
            f"#VULNERABILITY#{candidates_ids}"
        )
        item = analysis.model_dump()
        item["pk"] = pk
        item["sk"] = sk
        await table.put_item(Item=self._serialize(item))

    @override
    async def get_snippets_by_root(self, group_name: str, root_nickname: str) -> list[SnippetFacet]:
        """Get all snippets for a specific root."""
        table = await self._get_table("sifts_state")
        pk = f"GROUP#{group_name}#ROOT#{root_nickname}"
        response = await table.query(
            KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": pk,
                ":sk_prefix": "SNIPPET#",
            },
        )
        return [SnippetFacet.model_validate(item) for item in response["Items"]]

    @override
    async def get_snippets_by_file_path(
        self,
        group_name: str,
        root_nickname: str,
        path: str,
    ) -> list[SnippetFacet]:
        """Get all snippets for a specific file path."""
        table = await self._get_table("sifts_state")
        pk = f"GROUP#{group_name}#ROOT#{root_nickname}"
        response = await table.query(
            KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": pk,
                ":sk_prefix": f"SNIPPET#PATH#{path}",
            },
        )
        return [SnippetFacet.model_validate(item) for item in response["Items"]]

    async def _query_analyses_pk_prefix(
        self,
        table: DynamoTable,
        pk: str,
        sk_prefix: str,
        filter_expression: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Query analyses with a specific pk and sk prefix."""
        kwargs: dict[str, Any] = {
            "KeyConditionExpression": "pk = :pk AND begins_with(sk, :sk_prefix)",
            "ExpressionAttributeValues": {
                ":pk": pk,
                ":sk_prefix": sk_prefix,
            },
        }
        if filter_expression:
            kwargs["FilterExpression"] = filter_expression["expression"]
            kwargs["ExpressionAttributeValues"].update(filter_expression["values"])

        response = await table.query(**kwargs)
        return response["Items"]

    @override
    async def get_analyses_for_snippet(
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        path: str,
        code_sha256: str,
    ) -> list[AnalysisFacet]:
        """Get all analyses for a specific snippet and version."""
        table = await self._get_table("sifts_state")
        pk = f"GROUP#{group_name}#ROOT#{root_nickname}"
        sk_prefix = f"ANALYSIS#VERSION#{version}#PATH#{path}#SNIPPET#{code_sha256}#"

        items = await self._query_analyses_pk_prefix(table, pk, sk_prefix)
        return [
            (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
            for item in items
        ]

    @override
    async def get_analyses_by_file_path_version(
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        path: str,
    ) -> list[AnalysisFacet]:
        """Get all analyses for a file path within a given version."""
        table = await self._get_table("sifts_state")
        pk = f"GROUP#{group_name}#ROOT#{root_nickname}"
        sk_prefix = f"ANALYSIS#VERSION#{version}#PATH#{path}#"

        items = await self._query_analyses_pk_prefix(table, pk, sk_prefix)
        return [
            (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
            for item in items
        ]

    @override
    async def get_analyses_for_snippet_vulnerability(
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        path: str,
        code_sha256: str,
        vulnerability_id: str,
    ) -> list[AnalysisFacet]:
        """Get analyses for a specific snippet and vulnerability."""
        table = await self._get_table("sifts_state")
        pk = f"GROUP#{group_name}#ROOT#{root_nickname}"
        sk_prefix = (
            f"ANALYSIS#VERSION#{version}#PATH#{path}#SNIPPET#{code_sha256}"
            f"#VULNERABILITY#{vulnerability_id}#"
        )

        items = await self._query_analyses_pk_prefix(table, pk, sk_prefix)
        return [
            (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
            for item in items
        ]

    @cached(cache=Cache(maxsize=1000))  # type: ignore[misc]
    @override
    async def get_snippet_by_hash(
        self,
        group_name: str,
        root_nickname: str,
        path: str,
        code_sha256: str,
    ) -> SnippetFacet | None:
        """Get a specific snippet by its hash."""
        table = await self._get_table("sifts_state")

        pk = f"GROUP#{group_name}#ROOT#{root_nickname}"
        sk = f"SNIPPET#PATH#{path}#HASH#{code_sha256}"

        response = await table.get_item(Key={"pk": pk, "sk": sk})

        item = response.get("Item")
        if item is None:
            return None

        return SnippetFacet.model_validate(item)

    @override
    async def get_analyses_by_root(
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        commit: str | None = None,
    ) -> list[AnalysisFacet]:
        """Get all analyses for a root, optionally filtered by commit."""
        table = await self._get_table("sifts_state")

        pk = f"GROUP#{group_name}#ROOT#{root_nickname}"
        sk_prefix = f"ANALYSIS#VERSION#{version}#"
        if commit:
            filter_expression = Attr("vulnerable").eq(value=True) & Attr("commit").eq(commit)
        else:
            filter_expression = Attr("vulnerable").eq(value=True)  # type: ignore[assignment]

        response = await table.query(
            KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
            FilterExpression=filter_expression,
            ExpressionAttributeValues={
                ":pk": pk,
                ":sk_prefix": sk_prefix,
            },
        )

        return [
            (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
            for item in response["Items"]
        ]
