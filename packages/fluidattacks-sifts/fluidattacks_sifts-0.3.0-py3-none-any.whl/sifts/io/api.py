import asyncio
import os
from typing import Any, TypedDict

import aiohttp
import diskcache
from asyncache import cached
from cachetools import Cache
from platformdirs import user_cache_dir

from sifts.core.retry_utils import retry_on_exceptions

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=60)


class RootInfo(TypedDict):
    id: str
    nickname: str


class RootInfoResponse(TypedDict):
    root: RootInfo | None


class RootQueryResponse(TypedDict):
    data: RootInfoResponse


class CloningStatus(TypedDict):
    status: str
    commit: str | None


class GitRoot(TypedDict):
    nickname: str
    id: str
    state: str
    gitignore: str
    cloningStatus: CloningStatus | None


class GroupRoots(TypedDict):
    roots: list[GitRoot]


class GroupResponse(TypedDict):
    group: GroupRoots


class GroupRootsResponse(TypedDict):
    data: GroupResponse


# TypedDicts for root vulnerabilities query
class Vulnerability(TypedDict):
    id: str
    findingId: str
    where: str
    specific: str
    state: str
    source: str
    technique: str


class RootVulnerabilities(TypedDict):
    vulnerabilities: list[Vulnerability]


class RootVulnerabilitiesResponseData(TypedDict):
    root: RootVulnerabilities | None


class RootVulnerabilitiesResponse(TypedDict):
    data: RootVulnerabilitiesResponseData


# TypedDicts for finding query
class Finding(TypedDict):
    title: str
    id: str


class FindingResponseData(TypedDict):
    finding: Finding | None


class FindingResponse(TypedDict):
    data: FindingResponseData


class VulnerabilityResponseData(TypedDict):
    vulnerability: Vulnerability | None


class GraphQLApiError(Exception):
    """Raised when the GraphQL API returns errors."""


class VulnerabilityResponse(TypedDict):
    data: VulnerabilityResponseData


if os.environ.get("CACHE_ENABLED") == "true":
    CACHE = diskcache.Cache(user_cache_dir("sifts", "fluidattacks"))
else:
    CACHE = Cache(maxsize=100000)

# GraphQL query for root info
ROOT_QUERY = """
query GetRoot($groupName: String!, $rootId: ID!) {
  root(groupName: $groupName, rootId: $rootId) {
    ... on GitRoot {
      groupName
      id
      nickname
      state
      gitignore
      cloningStatus {
        commit
      }
    }
  }
}
"""

GROUP_ROOTS_QUERY = """
query GroupRoots($groupName: String!) {
  group(groupName: $groupName) {
    roots {
      ... on GitRoot {
        nickname
        id
        state
        gitignore
        cloningStatus {
          status
        }
      }
    }
  }
}
"""

ROOT_VULNERABILITIES_QUERY = """
query GetRootVulnerabilities($groupName: String!, $rootId: ID!) {
  root(groupName: $groupName, rootId: $rootId) {
    ... on GitRoot {
      vulnerabilities {
        id
        findingId
        where
        specific
        state
        source
        technique
      }
    }
  }
}
"""

FINDING_QUERY = """
query GetFinding($identifier: String!) {
  finding(identifier: $identifier) {
    title
    id
  }
}
"""

VULNERABILITY_QUERY = """
query GetVulnerability($uuid: String!) {
  vulnerability(uuid: $uuid) {
    id
    technique
  }
}
"""


def initialize_session() -> tuple[aiohttp.ClientSession, str]:
    # Get the API token from environment variable
    api_token = os.environ.get("INTEGRATES_API_TOKEN")
    if not api_token:
        msg = "INTEGRATES_API_TOKEN environment variable is not set"
        raise ValueError(msg)

    # Set the base URL and authorization headers for the session
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

    return aiohttp.ClientSession(
        base_url="https://app.fluidattacks.com",
        headers=headers,
    ), api_token


@retry_on_exceptions(
    exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
    max_attempts=5,
)
async def execute_graphql_query(
    session: aiohttp.ClientSession,
    query: str,
    variables: dict[str, Any],
) -> dict[str, Any]:
    payload = {"query": query, "variables": variables}
    async with session.post(
        "/api",
        json=payload,
        timeout=DEFAULT_TIMEOUT,
    ) as response:
        response.raise_for_status()
        result = await response.json()
        if "errors" in result:
            raise GraphQLApiError(result["errors"])
        return result  # type: ignore[no-any-return]


@cached(cache=CACHE, key=lambda *params: f"root-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_root(
    session: aiohttp.ClientSession,
    group_name: str,
    root_id: str,
) -> RootQueryResponse:
    variables = {"groupName": group_name, "rootId": root_id}
    response: RootQueryResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        ROOT_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"group_roots-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_group_roots(
    session: aiohttp.ClientSession,
    group_name: str,
) -> GroupRootsResponse:
    variables = {"groupName": group_name}
    response: GroupRootsResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        GROUP_ROOTS_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"group_roots-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_root_vulnerabilities(
    session: aiohttp.ClientSession,
    group_name: str,
    root_id: str,
) -> RootVulnerabilitiesResponse:
    variables = {"groupName": group_name, "rootId": root_id}
    response: RootVulnerabilitiesResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        ROOT_VULNERABILITIES_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"finding-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_finding(
    session: aiohttp.ClientSession,
    finding_id: str,
) -> FindingResponse:
    variables = {"identifier": finding_id}
    response: FindingResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        FINDING_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"vulnerability-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_vulnerability(
    session: aiohttp.ClientSession,
    uuid: str,
) -> VulnerabilityResponse:
    variables = {"uuid": uuid}
    response: VulnerabilityResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        VULNERABILITY_QUERY,
        variables,
    )
    return response
