from typing import TypedDict


class AgentPrompt(TypedDict):
    system: str
    instructions: str


class AgentPrompts(TypedDict):
    vuln_strict: AgentPrompt
    vuln_loose: AgentPrompt
    classify: AgentPrompt


class Prompts(TypedDict):
    agents: AgentPrompts
