import logging
from typing import TypedDict

import tiktoken
from more_itertools import mark_ends


class Metadata(TypedDict):
    finding_id: str
    criteria_code: str
    vulnerability_id: str
    organization_id: str
    finding_title: str
    where: str
    specific: int
    group: str
    snippet_offset: int
    vulnerable_function_code_hash: str


class Embeddings(TypedDict):
    vulnerable_function: list[float]
    abstract_propose: list[float]
    detailed_behavior: list[float]


class Source(TypedDict):
    metadata: Metadata
    vulnerable_function_code: str
    fixed_function_code: str | None
    vulnerability_knowledge: str | None
    vulnerable_line_content: str
    abstract_propose: str
    detailed_behavior: str
    embeddings: Embeddings


class SnippetHit(TypedDict):
    _index: str
    _id: str
    _score: float
    _source: Source
    ReRankingScore: float


LOGGER = logging.getLogger(__name__)


def extract_function_content(
    lines: list[str],
    line_number_start: int,
    line_number_end: int,
    column_number_start: int,
    column_number_end: int,
) -> str | None:
    function_content = []
    try:
        for is_first, is_last, line in mark_ends(lines[line_number_start - 1 : line_number_end]):
            if is_first:
                function_content.append(line[column_number_start - 1 :])
            elif is_last:
                function_content.append(line[:column_number_end])
            else:
                function_content.append(line)
    except IndexError:
        return None
    return "\n".join(function_content).replace("\t", "  ")


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(string))
