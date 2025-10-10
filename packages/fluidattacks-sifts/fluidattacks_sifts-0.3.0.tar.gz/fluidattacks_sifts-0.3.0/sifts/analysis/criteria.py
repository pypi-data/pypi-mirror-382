import logging
from collections import deque
from collections.abc import Iterable
from contextlib import suppress
from typing import Any

import numpy as np
from litellm import aembedding

from sifts.analysis.criteria_data import DEFINES_VULNERABILITIES
from sifts.common_types.snippets import SnippetHit
from sifts.io.db.data_loaders import KNN_DATA
from sifts.llm.router import RouterStrict

SIMILARITY_THRESHOLD = 0.7
LOGGER = logging.getLogger(__name__)


def compare_vectors(vector1: list[float], vector2: list[float]) -> float:
    return float(np.dot(vector1, vector2))


def compare_two_keys(key1: str, key2: str) -> float:
    with suppress(KeyError):
        vector1 = KNN_DATA[key1][0]
        vector2 = KNN_DATA[key2][0]
        return compare_vectors(vector1, vector2)

    with suppress(KeyError):
        vector1 = KNN_DATA[DEFINES_VULNERABILITIES[key1]["en"]["title"]][0]
        vector2 = KNN_DATA[DEFINES_VULNERABILITIES[key2]["en"]["title"]][0]
        return compare_vectors(vector1, vector2)

    return 0.0


def generate_vuln_context_markdown(vuln_criteria: dict[str, Any]) -> str:
    return f"### {vuln_criteria['en']['title']}\n{vuln_criteria['en']['description']}"


def get_vuln_criteria(finding_code: str) -> dict[str, Any]:
    return DEFINES_VULNERABILITIES[finding_code]


def connected_components_by_threshold(
    embeddings: tuple[list[float], ...],
    threshold: float,
) -> list[tuple[int, ...]]:
    similar_matrix = np.array(embeddings) @ np.array(embeddings).T
    m_length = len(embeddings)
    # Boolean matrix: True if similar
    boolean_matrix = threshold <= similar_matrix

    visited = np.zeros(m_length, dtype=bool)
    groups: list[tuple[int, ...]] = []

    for i in range(m_length):
        if not visited[i]:
            # BFS/DFS to find all nodes connected to i
            queue = deque([i])
            visited[i] = True
            component = [i]

            while queue:
                x = queue.popleft()
                # look at all nodes j connected to x
                neighbors = np.nonzero(boolean_matrix[x])[0]  # indices where M[x, j] == True
                for j in neighbors:
                    if not visited[j]:
                        visited[j] = True
                        queue.append(j)
                        component.append(j)

            groups.append(tuple(sorted(component)))

    return groups


def _get_title(x: SnippetHit) -> str:
    return DEFINES_VULNERABILITIES[x["_source"]["metadata"]["criteria_code"]]["en"]["title"]


def filter_unique_candidates(candidates: list[SnippetHit]) -> list[SnippetHit]:
    codes: set[str] = set()
    unique_candidates: list[SnippetHit] = []
    for candidate in candidates:
        code = candidate["_source"]["metadata"]["criteria_code"]
        if code in DEFINES_VULNERABILITIES and code not in codes:
            codes.add(code)
            unique_candidates.append(candidate)
    return unique_candidates


async def calculate_embeddings(candidates: list[SnippetHit]) -> tuple[list[float], ...]:
    response = await aembedding(
        model="voyage/voyage-3",
        input=[
            candidate["_source"]["metadata"]["finding_title"].split(".")[-1].strip()
            for candidate in candidates
        ],
        caching=True,
    )
    return tuple(x["embedding"] for x in response.data)


async def group_candidates(
    candidates: list[SnippetHit],
    embeddings: tuple[list[float], ...],
) -> tuple[tuple[SnippetHit, ...], ...]:
    groups: tuple[tuple[SnippetHit, ...], ...] = tuple(
        tuple(candidates[i] for i in _group)
        for _group in connected_components_by_threshold(embeddings, 0.7)
    )
    for group in groups:
        if len(group) > 1:
            titles = tuple(_get_title(candidate) for candidate in group)
            LOGGER.debug("Group with %s candidates: %s", len(group), titles)
    return groups


async def filter_candidate_codes(
    candidates: list[SnippetHit],
) -> tuple[tuple[SnippetHit, ...], ...]:
    unique_candidates = filter_unique_candidates(candidates)
    if not unique_candidates:
        return ()
    embeddings = await calculate_embeddings(unique_candidates)
    return await group_candidates(unique_candidates, embeddings)


def generate_candidate_text(defines_codes: Iterable[str]) -> str:
    return "\n".join(
        [
            generate_vuln_context_markdown(get_vuln_criteria(x))
            for x in defines_codes
            if x in DEFINES_VULNERABILITIES
        ],
    )


def top_k_similar(
    embeddings: list[list[float]],
    x: list[float],
    k: int = 3,
) -> tuple[list[int], list[float]]:
    # 1. Calculate similarities using dot product (cosine, since they are normalized)
    #    embeddings @ x gives a vector of size N with cosines between each row and x.
    similarities = np.array(embeddings) @ np.array(x)  # shape (N,)

    # 2. Find the indices of the k highest values in 'similarities'
    #    We use argpartition for better efficiency than full argsort.
    if k >= len(similarities):
        # If k >= N, return all sorted from highest to lowest
        sorted_idx = np.argsort(similarities)[::-1]
        top_k_idx = sorted_idx
    else:
        # np.argpartition places the k highest values in the last k positions, without sorting
        # the rest. Then we sort those k positions from highest to lowest.
        partitioned = np.argpartition(similarities, -k)[-k:]
        top_k_idx = partitioned[np.argsort(similarities[partitioned])[::-1]]

    # 3. Retrieve the corresponding similarity values
    top_k_sims = similarities[top_k_idx]

    return top_k_idx.tolist(), top_k_sims.tolist()


async def find_most_similar_finding(
    router: RouterStrict,
    title: str,
    description: str,
) -> str | None:
    response = await router.aembedding(
        "voyage-3",
        [f"{title}\n{description}"],
        caching=True,
    )
    embedding = response["data"][0]["embedding"]
    embeddings = [KNN_DATA[finding_title][0] for finding_title in KNN_DATA]
    keys = list(KNN_DATA.keys())
    top_k_idx, _ = top_k_similar(embeddings, embedding)
    top_k_titles = [keys[i] for i in top_k_idx]

    finding_title = top_k_titles[0] if top_k_titles else ""
    try:
        return next(
            x
            for x in DEFINES_VULNERABILITIES
            if DEFINES_VULNERABILITIES[x]["en"]["title"] == finding_title
        )
    except StopIteration:
        return None
