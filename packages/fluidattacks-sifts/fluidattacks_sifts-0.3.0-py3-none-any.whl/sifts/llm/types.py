from typing import Literal, TypedDict

from sifts.llm.prompts import Prompts


class ModelParameters(TypedDict):
    top_findings: list[str]
    finding_candidates_exclusion: list[str]
    exclusion_candidates_finding_title: list[str]
    prompts: Prompts


class AnalyzeVulnerabilityParams(TypedDict):
    isVulnerable: Literal["true", "false", "unknown"]
    vulnerabilityType: str
    confidence: Literal["high", "medium", "low"]
    explanation: str
    vulnerableFunction: str


class FinishAnalysisParams(TypedDict):
    isVulnerable: Literal["true", "false", "unknown"]
    vulnerabilityType: str
    confidence: Literal["high", "medium", "low"]
    explanation: str
    analyzedFunctions: list[str]
    vulnerabilityChain: list[str]
    vulnerableFunction: str
    method_id: str
    additionalProperties: bool
