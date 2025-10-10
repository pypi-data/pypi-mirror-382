from collections.abc import Iterable
from typing import Any, Literal, ParamSpec, TypedDict, cast

import boto3
import opensearchpy
from litellm import aembedding
from opensearchpy import (
    AsyncHttpConnection,
    AsyncOpenSearch,
    AsyncTransport,
    AWSV4SignerAsyncAuth,
    JSONSerializer,
)
from pydantic import BaseModel, Field

from sifts.common_types.snippets import SnippetHit
from sifts.config.settings import (
    FI_AWS_OPENSEARCH_HOST,
    FI_AWS_REGION_NAME,
)
from sifts.core.retry_utils import retry_on_exceptions
from sifts.llm.config_data import TOP_FINDINGS


class SearchCriteria(TypedDict):
    """Search criteria for OpenSearch queries."""

    search_type: Literal["knn", "bm25"]
    field_name: str  # For BM25 search or field name for KNN
    search_value: str  # Snippet content for KNN or field value for BM25


class SearchParameters(BaseModel):
    include_vulnerabilities: list[str] = Field(default_factory=list)
    exclude_vulnerabilities: list[str] = Field(default_factory=list)
    group_name: str | None = None


class SetEncoder(JSONSerializer):
    def default(self, data: Any) -> Any:  # noqa: ANN401
        if isinstance(data, set):
            return list(data)
        return JSONSerializer.default(self, data)


FINDING_ELUSION_OPENSEARCH_QUERY = [
    {
        "terms": {
            "metadata.organization_id.keyword": [
                "ORG#a23457e2-f81f-44a2-867f-230082af676c",
                "ORG#0d6d8f9d-3814-48f8-ba2c-f4fb9f8d4ffa",
                "ORG#bb56815e-a8de-4fc7-a984-fe572ef5e4f1",
            ],
        },
    },
]


P = ParamSpec("P")


SEARCH_TOP_N = 30


SOURCE = [
    "metadata.criteria_code",
    "metadata.vulnerability_id",
    "metadata.finding_title",
    "vulnerable_function_code",
]


def get_exclusion_vulnerabilities(
    params: SearchParameters,
) -> list[dict[str, dict[str, list[str] | str]]]:
    result: list[dict[str, dict[str, list[str] | str]]] = []
    exclude_defines_codes = []
    exclude_defines_titles = []
    for exclusion in params.exclude_vulnerabilities:
        if exclusion.isdigit():
            exclude_defines_codes.append(exclusion)
        else:
            exclude_defines_titles.append(exclusion)
    if exclude_defines_codes:
        result.append({"terms": {"metadata.criteria_code": exclude_defines_codes}})
    if exclude_defines_titles:
        result.extend(
            {"match_phrase": {"metadata.finding_title": exclusion}}
            for exclusion in exclude_defines_titles
        )
    if params.group_name:
        result.append({"term": {"metadata.group.keyword": params.group_name}})

    return result


def get_inclusion_vulnerabilities(
    params: SearchParameters,
) -> dict[str, list[dict[str, dict[str, list[str] | str]]]]:
    result: dict[str, list[dict[str, dict[str, list[str] | str]]]] = {"must": [], "should": []}
    include_defines_codes = []
    include_defines_titles = []
    for inclusion in params.include_vulnerabilities:
        if inclusion.isdigit():
            include_defines_codes.append(inclusion)
        else:
            include_defines_titles.append(inclusion)

    if include_defines_codes:
        result["must"].append({"terms": {"metadata.criteria_code": include_defines_codes}})
    if include_defines_titles:
        result["should"].extend(
            {"match_phrase": {"metadata.finding_title": inclusion}}
            for inclusion in include_defines_titles
        )

    return result


async def search_similar_vulnerabilities_by_knn_code(
    *,
    open_client: AsyncOpenSearch,
    snippet_content: str,
    search_parameters: SearchParameters,
) -> Iterable[SnippetHit]:
    must_clauses = get_inclusion_vulnerabilities(search_parameters)
    must_not_clauses = get_exclusion_vulnerabilities(search_parameters)
    embedding = (
        await aembedding(
            model="voyage/voyage-code-3",
            input=[snippet_content],
            caching=True,
        )
    ).data[0]["embedding"]
    body = {
        "size": SEARCH_TOP_N,
        "min_score": 0.7,
        "query": {
            "bool": {
                "must": [
                    {
                        "knn": {
                            "embeddings.vulnerable_function": {
                                "vector": embedding,
                                "k": SEARCH_TOP_N,
                            },
                        },
                    },
                ],
                "filter": {
                    "bool": {
                        "must": [
                            *must_clauses["must"],
                        ],
                    },
                },
                "must_not": [
                    *must_not_clauses,
                    *FINDING_ELUSION_OPENSEARCH_QUERY,
                ],
                **(
                    {"should": must_clauses["should"], "minimum_should_match": 1}
                    if must_clauses["should"]
                    else {}
                ),
            },
        },
        "_source": SOURCE,
    }
    result = await retry_on_exceptions(
        exceptions=(
            opensearchpy.exceptions.ConnectionError,
            opensearchpy.exceptions.ConnectionTimeout,
        ),
        sleep_seconds=10,
    )(open_client.search)(
        index="vulnerabilities_candidates_v1",
        body=body,
    )
    return cast(
        "list[SnippetHit]",
        result["hits"]["hits"],
    )


async def create_index(open_client: AsyncOpenSearch, index_name: str) -> None:
    await open_client.indices.create(
        index=index_name,
        body={
            "settings": {
                "number_of_replicas": 2,
                "analysis": {
                    "analyzer": {"my_analyzer": {"type": "standard", "stopwords": "_none_"}},
                },
                "index": {
                    "knn.algo_param": {"ef_search": 512},
                    "knn": True,
                    "similarity": {"my_bm25": {"type": "BM25", "k1": 1.2, "b": 0.75}},
                },
            },
            "mappings": {
                "properties": {
                    "abstract_propose": {
                        "type": "text",
                        "analyzer": "my_analyzer",
                        "similarity": "my_bm25",
                    },
                    "detailed_behavior": {
                        "type": "text",
                        "analyzer": "my_analyzer",
                        "similarity": "my_bm25",
                    },
                    "embeddings": {
                        "properties": {
                            "vulnerable_function": {
                                "type": "knn_vector",
                                "dimension": 1024,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "nmslib",
                                    "parameters": {"ef_construction": 100, "m": 16},
                                },
                            },
                            "abstract_propose": {
                                "type": "knn_vector",
                                "dimension": 1024,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "nmslib",
                                    "parameters": {"ef_construction": 100, "m": 16},
                                },
                            },
                            "detailed_behavior": {
                                "type": "knn_vector",
                                "dimension": 1024,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "nmslib",
                                    "parameters": {"ef_construction": 100, "m": 16},
                                },
                            },
                        },
                    },
                },
            },
        },
        timeout=60,
    )


async def search_similar_vulnerabilities_by_field_name_bm25(
    *,
    open_client: AsyncOpenSearch,
    field_value: str,
    field_name: str,
    search_parameters: SearchParameters,
) -> Iterable[SnippetHit]:
    must_clauses = get_inclusion_vulnerabilities(search_parameters)
    must_not_clauses = get_exclusion_vulnerabilities(search_parameters)
    result = await retry_on_exceptions(
        exceptions=(opensearchpy.exceptions.ConnectionError,),
        sleep_seconds=5,
    )(open_client.search)(
        index="vulnerabilities_candidates_v1",
        body={
            "size": SEARCH_TOP_N,
            "query": {
                "bool": {
                    "must": [{"match": {field_name: field_value}}],
                    "filter": {
                        "bool": {
                            "must": [
                                *must_clauses["must"],
                            ],
                        },
                    },
                    "must_not": [
                        *must_not_clauses,
                        *FINDING_ELUSION_OPENSEARCH_QUERY,
                    ],
                    **(
                        {
                            "minimum_should_match": 1,
                            "should": must_clauses["should"],
                        }
                        if must_clauses["should"]
                        else {}
                    ),
                },
            },
            "_source": SOURCE,
        },
        timeout=120,
    )
    return cast("list[SnippetHit]", result["hits"]["hits"])


async def count_candidates_by_finding(
    *,
    open_client: AsyncOpenSearch,
    criteria_code: str | None,
    group_name: str,
) -> int:
    if not criteria_code:
        return 0
    result = await open_client.count(
        index="vulnerabilities_candidates_v1",
        body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "metadata.criteria_code.keyword": criteria_code,
                            },
                        },
                    ],
                    "must_not": [
                        {
                            "term": {
                                "metadata.group.keyword": group_name,
                            },
                        },
                        *FINDING_ELUSION_OPENSEARCH_QUERY,
                    ],
                },
            },
            "_source": SOURCE,
        },
        timeout=120,
    )
    return cast("int", result["count"])


async def count_by_criteria_code(
    *,
    open_client: AsyncOpenSearch,
    criteria_code: str,
    group_name: str | None = None,
) -> int:
    must_not_clauses = []
    if group_name:
        must_not_clauses.append(
            {
                "term": {
                    "metadata.group.keyword": group_name,
                },
            },
        )

    result = await open_client.count(
        index="vulnerabilities_candidates_v1",
        body={
            "query": {
                "bool": {
                    "must": [{"terms": {"metadata.criteria_code": [criteria_code]}}],
                    "must_not": must_not_clauses,
                },
            },
        },
        timeout=120,
    )

    return cast("int", result["count"])


async def search_similar_vulnerabilities_by_field_name_vector(
    *,
    open_client: AsyncOpenSearch,
    field_name: str,
    embedding: list[float],
    group_name: str | None = None,
) -> Iterable[SnippetHit]:
    result = await retry_on_exceptions(
        exceptions=(opensearchpy.exceptions.ConnectionError,),
        sleep_seconds=5,
    )(open_client.search)(
        index="vulnerabilities_candidates_v1",
        body={
            "size": SEARCH_TOP_N,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                f"embeddings.{field_name}": {
                                    "vector": embedding,
                                    "k": SEARCH_TOP_N,
                                },
                            },
                        },
                        *(
                            [{"terms": {"metadata.criteria_code": TOP_FINDINGS}}]
                            if TOP_FINDINGS
                            else []
                        ),
                    ],
                    "must_not": [
                        *(
                            [
                                {
                                    "term": {
                                        "metadata.group.keyword": group_name,
                                    },
                                },
                            ]
                            if group_name
                            else []
                        ),
                        *FINDING_ELUSION_OPENSEARCH_QUERY,
                    ],
                },
            },
            "_source": SOURCE,
        },
        timeout=120,
    )
    return cast("list[SnippetHit]", result["hits"]["hits"])


async def setup_opensearch_client(new_index: bool = False) -> AsyncOpenSearch:  # noqa: ARG001, FBT001, FBT002
    session = boto3.Session()
    return AsyncOpenSearch(
        transport_class=AsyncTransport,
        connection_class=AsyncHttpConnection,
        hosts=[FI_AWS_OPENSEARCH_HOST],
        http_auth=AWSV4SignerAsyncAuth(
            credentials=session.get_credentials(),
            region=FI_AWS_REGION_NAME,
            service="es",
        ),
        http_compress=True,
        max_retries=15,
        timeout=10,
        retry_on_status=(429, 502, 503, 504),
        retry_on_timeout=True,
        serializer=SetEncoder(),
        use_ssl=True,
        verify_certs=True,
    )
