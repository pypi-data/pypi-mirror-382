from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SnippetFacet(BaseModel):
    """Snippet facet aligned with Snowflake CODE_SNIPPETS schema."""

    snippet_hash_id: str = Field(..., min_length=1, description="Unique SHA-256 hash identifier")
    group_name: str = Field(..., min_length=1, description="Name of the group or project")
    root_nickname: str = Field(..., min_length=1, description="Root nickname identifier")
    commit: str = Field(..., min_length=1, description="Git commit hash")
    path: str = Field(..., min_length=1, description="File path of the snippet")
    start_byte: int = Field(..., ge=0, description="Starting byte position")
    end_byte: int = Field(..., ge=0, description="Ending byte position")
    start_line: int = Field(..., ge=0, description="Starting line number")
    start_column: int = Field(..., ge=0, description="Starting column number")
    end_line: int = Field(..., ge=0, description="Ending line number")
    end_column: int = Field(..., ge=0, description="Ending column number")
    node_type: str = Field(..., min_length=1, description="Type of the AST node")
    code_sha256: str = Field(..., min_length=1, description="SHA-256 hash of normalized code")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    # Optional fields for backward compatibility
    text: str | None = Field(None, description="Snippet content text")
    language: str | None = Field(None, description="Programming language")
    name: str | None = Field(None, description="Optional snippet name")


class _BaseFacet(BaseModel):
    group_name: str
    root_nickname: str
    version: str
    commit: str
    code_hash: str
    snippet_hash_id: str
    analyzed_at: datetime
    path: str
    cost: float

    candidate_index: int | None = None
    trace_id: str | None = None


class VulnerableFacet(_BaseFacet):
    vulnerable: Literal[True] = True

    vulnerability_id_candidates: list[str]
    vulnerable_lines: list[int]
    ranking_score: float
    reason: str
    input_tokens: int
    output_tokens: int
    total_tokens: int

    suggested_criteria_code: str | None = None
    suggested_finding_title: str | None = None


class SafeFacet(_BaseFacet):
    vulnerable: Literal[False] = False
    input_tokens: int
    output_tokens: int
    total_tokens: int
    reason: str
    vulnerability_id_candidates: list[str]

    vulnerable_lines: list[int] | None = None
    ranking_score: float | None = None
    suggested_criteria_code: str | None = None
    suggested_finding_title: str | None = None


AnalysisFacet = VulnerableFacet | SafeFacet
