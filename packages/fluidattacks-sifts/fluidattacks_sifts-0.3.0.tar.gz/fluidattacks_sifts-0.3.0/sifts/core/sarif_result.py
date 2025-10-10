import json
from typing import Any

import sarif_om
from sarif_om import SarifLog

from sifts.analysis.criteria_data import DEFINES_REQUIREMENTS, DEFINES_VULNERABILITIES
from sifts.config import SiftsConfig
from sifts.core.repository import get_repo_branch, get_repo_head_hash, get_repo_remote

# Removed direct import - will use database backend from config
from sifts.io.db.types import AnalysisFacet, SnippetFacet

type SarifReportComponent = (
    SarifLog
    | list["SarifReportComponent"]
    | dict[str, "SarifReportComponent"]
    | tuple["SarifReportComponent"]
    | set["SarifReportComponent"]
    | str
    | int
)


def _get_rule(vuln_id: str) -> sarif_om.ReportingDescriptor:
    content = DEFINES_VULNERABILITIES[vuln_id]

    return sarif_om.ReportingDescriptor(
        id=vuln_id,
        name=content["en"]["title"],
        full_description=sarif_om.MultiformatMessageString(
            text=content["en"]["description"],
        ),
        help_uri=(f"https://db.fluidattacks.com/wek/{vuln_id}"),
        help=sarif_om.MultiformatMessageString(
            text=content["en"]["recommendation"],
        ),
        properties={"auto_approve": True},
    )


def _rule_is_present(base: sarif_om.SarifLog, rule_id: str) -> bool:
    return any(rule.id == rule_id for rule in base.runs[0].tool.driver.rules)


def _taxa_is_present(base: sarif_om.SarifLog, taxa_id: str) -> bool:
    return any(rule.id == taxa_id for rule in base.runs[0].taxonomies[0].taxa)


def render_snippet(snippet: SnippetFacet, focus_line: int) -> str:
    snippet_content: str = snippet.text or ""
    # Format snippet highlighting the focus line and limiting the context to a
    # maximum of 10 lines above and 10 lines below the focus line.
    start_line = snippet.start_line

    # Enumerate all lines with their absolute line numbers.
    indexed_lines = list(enumerate(snippet_content.split("\n"), start=start_line))

    # Keep only the lines that are within the desired window.
    indexed_lines = [
        (idx, line) for idx, line in indexed_lines if focus_line - 10 <= idx <= focus_line + 10
    ]

    # Build the final snippet string, marking the focus line.
    return "\n".join(
        f"> {idx} | {line[:120]}" if idx == focus_line else f"  {idx} | {line[:120]}"
        for idx, line in indexed_lines
    )


async def _get_context_region(
    vulnerability: AnalysisFacet,
    vulnerable_line: int,
    config: SiftsConfig,
) -> sarif_om.Region:
    db_backend = config.get_database()
    snippet = await db_backend.get_snippet_by_hash(
        group_name=vulnerability.group_name,
        root_nickname=vulnerability.root_nickname,
        path=vulnerability.path,
        code_sha256=vulnerability.snippet_hash_id,
    )
    if snippet:
        region = sarif_om.Region(
            start_line=snippet.start_line,
            end_line=snippet.end_line,
            snippet=sarif_om.ArtifactContent(
                rendered={"text": render_snippet(snippet, vulnerable_line)},
                text=snippet.text or "",
            ),
            start_column=snippet.start_column,
            end_column=snippet.end_column,
            source_language=snippet.language,
        )
    else:
        region = sarif_om.Region()

    return region


def _get_taxa(requirement_id: str) -> sarif_om.ReportingDescriptor:
    content = DEFINES_REQUIREMENTS[requirement_id]
    return sarif_om.ReportingDescriptor(
        id=requirement_id,
        name=content["en"]["title"],
        short_description=sarif_om.MultiformatMessageString(
            text=content["en"]["summary"],
        ),
        full_description=sarif_om.MultiformatMessageString(
            text=content["en"]["description"],
        ),
        help_uri=(f"https://db.fluidattacks.com/req/{requirement_id}"),
    )


def attrs_serializer(obj: SarifReportComponent) -> SarifReportComponent:
    return (
        {
            attribute.metadata["schema_property_name"]: attrs_serializer(
                obj.__dict__[attribute.name],
            )
            for attribute in obj.__attrs_attrs__
            if obj.__dict__[attribute.name] != attribute.default
        }
        if hasattr(obj, "__attrs_attrs__")
        else obj
    )


def simplify_sarif(sarif_obj: SarifLog) -> dict[str, Any]:
    result: dict[str, Any] = json.loads(json.dumps(sarif_obj, default=attrs_serializer))
    return result


async def _get_base(config: SiftsConfig, vulns: list[AnalysisFacet]) -> SarifLog:
    base = SarifLog(
        version="2.1.0",
        schema_uri=("https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json"),
        runs=[
            sarif_om.Run(
                tool=sarif_om.Tool(
                    driver=sarif_om.ToolComponent(
                        name="smells",
                        rules=[
                            _get_rule(check) for check in config.analysis.include_vulnerabilities
                        ],
                        version="1.0.0",
                        semantic_version="1.0.0",
                    ),
                ),
                results=[],
                version_control_provenance=[
                    sarif_om.VersionControlDetails(
                        repository_uri=get_repo_remote(config.analysis.working_dir),
                        revision_id=get_repo_head_hash(
                            config.analysis.working_dir,
                        ),
                        branch=get_repo_branch(config.analysis.working_dir),
                    ),
                ],
                taxonomies=[
                    sarif_om.ToolComponent(
                        name="criteria",
                        version="1",
                        information_uri=("https://db.fluidattacks.com/req/"),
                        organization="Fluidattacks",
                        short_description=sarif_om.MultiformatMessageString(
                            text="The fluidattacks security requirements",
                        ),
                        taxa=[],
                        is_comprehensive=False,
                    ),
                ],
                web_responses=[],
            ),
        ],
    )
    for vulnerability in vulns:
        rule_id = vulnerability.suggested_criteria_code
        if not rule_id:
            continue
        db_backend = config.get_database()
        snippet = await db_backend.get_snippet_by_hash(
            group_name=vulnerability.group_name,
            root_nickname=vulnerability.root_nickname,
            path=vulnerability.path,
            code_sha256=vulnerability.snippet_hash_id,
        )
        if not snippet:
            continue

        result = sarif_om.Result(
            rule_id=rule_id,
            level="note",
            message=sarif_om.MultiformatMessageString(
                text=vulnerability.reason,
                properties={},
            ),
            locations=[
                sarif_om.Location(
                    physical_location=sarif_om.PhysicalLocation(
                        artifact_location=sarif_om.ArtifactLocation(
                            uri=vulnerability.path,
                        ),
                        region=sarif_om.Region(
                            start_line=x,
                            source_language=snippet.language,
                        ),
                        context_region=await _get_context_region(vulnerability, x, config),
                    ),
                )
                for x in vulnerability.vulnerable_lines or []
            ],
            taxa=[],
        )
        # append rule if not is present
        if not _rule_is_present(base, rule_id):
            base.runs[0].tool.driver.rules.append(_get_rule(rule_id))

        for taxa_id in DEFINES_VULNERABILITIES[rule_id]["requirements"]:
            if not _taxa_is_present(base, taxa_id):
                base.runs[0].taxonomies[0].taxa.append(_get_taxa(taxa_id))

        result.taxa = [
            sarif_om.ReportingDescriptorReference(
                id=taxa_id,
                tool_component=sarif_om.ToolComponentReference(name="criteria"),
            )
            for taxa_id in DEFINES_VULNERABILITIES[rule_id]["requirements"]
        ]
        base.runs[0].results.append(result)
    return base


async def get_sarif(vulns: list[AnalysisFacet], config: SiftsConfig) -> dict[str, Any]:
    return simplify_sarif(await _get_base(config, vulns))
