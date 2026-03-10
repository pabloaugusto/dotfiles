from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.ai_control_plane_lib import load_ai_control_plane, resolve_atlassian_platform
from scripts.atlassian_platform_lib import (
    AtlassianHttpClient,
    JiraAdapter,
    adf_to_text,
    canonicalize_workflow_status,
)

STRUCTURED_COMMENT_ALIASES = {
    "agent": "agent",
    "agente": "agent",
    "interaction type": "interaction_type",
    "tipo de interacao": "interaction_type",
    "status": "status",
    "status atual": "status",
    "contexto": "contexto",
    "evidencias": "evidencias",
    "proximo passo": "proximo_passo",
}
STRUCTURED_LIST_KEYS = {"contexto", "evidencias", "proximo_passo"}
ACTIVE_STATUS_NAMES = {
    "refinement",
    "ready",
    "doing",
    "testing",
    "review",
    "changes requested",
    "paused",
}
DELIVERY_ISSUE_TYPES = {"task", "story", "bug", "sub-task"}
BUILDER_ROLES = (
    "ai-documentation-agent",
    "ai-developer",
    "ai-developer-",
    "ai-devops",
    "ai-tech-lead",
    "ai-engineering-architect",
)
REVIEWER_ROLES = {"ai-reviewer", "pascoalete"}
REVIEWER_ROLE_PREFIXES = ("ai-reviewer-",)
REVIEWER_ROLE_SUFFIXES = ("-reviewer",)
QA_ROLES = {"ai-qa"}
QA_ROLE_PREFIXES = ("ai-qa-",)


def normalize_status_name(value: str) -> str:
    normalized = re.sub(r"\s+", " ", str(value or "").strip()).casefold()
    return canonicalize_workflow_status(normalized)


def normalize_text(value: str) -> str:
    return " ".join(str(value or "").split())


def extract_option_value(raw_value: Any) -> str:
    if isinstance(raw_value, dict):
        return str(raw_value.get("value", "")).strip()
    return str(raw_value or "").strip()


def parse_structured_comment(raw_text: str) -> dict[str, Any] | None:
    parsed: dict[str, Any] = {}
    current_key = ""
    for raw_line in raw_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        matched_key = ""
        value = ""
        for label, key in STRUCTURED_COMMENT_ALIASES.items():
            normalized_label = label.casefold()
            if stripped.casefold() == normalized_label:
                matched_key = key
                break
            prefix = f"{label}:"
            if stripped.casefold().startswith(prefix):
                matched_key = key
                value = stripped.split(":", 1)[1].strip()
                break
        if matched_key:
            current_key = matched_key
            if current_key in STRUCTURED_LIST_KEYS:
                parsed[current_key] = [value] if value else []
            else:
                parsed[current_key] = value
            continue
        heading = stripped
        if heading.startswith("##"):
            heading = heading[2:].strip()
            matched_key = STRUCTURED_COMMENT_ALIASES.get(heading.casefold(), "")
            if matched_key:
                current_key = matched_key
                parsed[current_key] = []
                continue
        if not current_key:
            continue
        item = stripped[2:].strip() if stripped.startswith("- ") else stripped
        if not item:
            continue
        if current_key in STRUCTURED_LIST_KEYS:
            parsed.setdefault(current_key, []).append(item)
        else:
            existing = str(parsed.get(current_key, "")).strip()
            parsed[current_key] = f"{existing} {item}".strip() if existing else item
    return parsed or None


def is_builder_role(agent: str) -> bool:
    normalized = str(agent or "").strip().casefold()
    return any(normalized == prefix or normalized.startswith(prefix) for prefix in BUILDER_ROLES)


def is_reviewer_role(agent: str) -> bool:
    normalized = str(agent or "").strip().casefold()
    if normalized in REVIEWER_ROLES:
        return True
    if any(normalized.startswith(prefix) for prefix in REVIEWER_ROLE_PREFIXES):
        return True
    return any(normalized.endswith(suffix) for suffix in REVIEWER_ROLE_SUFFIXES)


def is_qa_role(agent: str) -> bool:
    normalized = str(agent or "").strip().casefold()
    if normalized in QA_ROLES:
        return True
    return any(normalized.startswith(prefix) for prefix in QA_ROLE_PREFIXES)


def evaluate_issue_comment_contract(
    issue: dict[str, Any],
    comments: list[dict[str, Any]],
    *,
    current_agent_field_id: str,
    next_required_field_id: str,
) -> dict[str, Any]:
    fields = issue.get("fields") or {}
    issue_key = str(issue.get("key", "")).strip()
    status_name = str(((fields.get("status") or {}).get("name")) or "").strip()
    status_normalized = normalize_status_name(status_name)
    issue_type = str(((fields.get("issuetype") or {}).get("name")) or "").strip()
    current_agent = (
        extract_option_value(fields.get(current_agent_field_id)) if current_agent_field_id else ""
    )
    next_required_role = (
        extract_option_value(fields.get(next_required_field_id)) if next_required_field_id else ""
    )

    structured_comments: list[dict[str, Any]] = []
    for comment in comments:
        raw_text = adf_to_text(comment.get("body")).strip()
        parsed = parse_structured_comment(raw_text)
        if not parsed or not str(parsed.get("agent", "")).strip():
            continue
        structured_comments.append(
            {
                "id": str(comment.get("id", "")).strip(),
                "created": str(comment.get("created", "")).strip(),
                "updated": str(comment.get("updated", "")).strip(),
                "agent": str(parsed.get("agent", "")).strip(),
                "status": canonicalize_workflow_status(str(parsed.get("status", "")).strip()),
                "interaction_type": str(parsed.get("interaction_type", "")).strip(),
            }
        )

    agents_seen = sorted(
        {entry["agent"] for entry in structured_comments if str(entry.get("agent", "")).strip()}
    )
    latest = structured_comments[-1] if structured_comments else {}
    latest_status = str(latest.get("status", "")).strip()
    latest_agent = str(latest.get("agent", "")).strip()

    findings: list[dict[str, str]] = []
    if status_normalized in ACTIVE_STATUS_NAMES and not structured_comments:
        findings.append(
            {
                "code": "missing_structured_comments",
                "severity": "high",
                "message": "A issue esta ativa, mas nao possui comentarios estruturados de agentes.",
            }
        )
    if current_agent and current_agent not in agents_seen:
        findings.append(
            {
                "code": "missing_current_agent_comment",
                "severity": "high",
                "message": f'O campo "Current Agent Role" aponta para {current_agent}, mas nao existe comentario estruturado desse agente.',
            }
        )
    if latest_status and normalize_status_name(latest_status) != status_normalized:
        findings.append(
            {
                "code": "latest_comment_status_mismatch",
                "severity": "high",
                "message": f'O comentario estruturado mais recente informa status "{latest_status}", mas a issue esta em "{status_name}".',
            }
        )
    if (
        current_agent
        and latest_agent
        and latest_agent != current_agent
        and status_normalized in ACTIVE_STATUS_NAMES
    ):
        findings.append(
            {
                "code": "latest_comment_agent_mismatch",
                "severity": "medium",
                "message": f"O comentario estruturado mais recente e de {latest_agent}, mas o agente atual da issue e {current_agent}.",
            }
        )

    if status_normalized == "done" and issue_type.casefold() in DELIVERY_ISSUE_TYPES:
        has_builder = any(is_builder_role(agent) for agent in agents_seen)
        has_qa = any(is_qa_role(agent) for agent in agents_seen)
        has_reviewer = any(is_reviewer_role(agent) for agent in agents_seen)
        if not has_builder:
            findings.append(
                {
                    "code": "missing_delivery_agent_comment",
                    "severity": "medium",
                    "message": "A issue concluida nao possui comentario estruturado de entrega tecnica.",
                }
            )
        if not has_qa:
            findings.append(
                {
                    "code": "missing_qa_comment",
                    "severity": "medium",
                    "message": "A issue concluida nao possui comentario estruturado de QA.",
                }
            )
        if not has_reviewer:
            findings.append(
                {
                    "code": "missing_reviewer_comment",
                    "severity": "medium",
                    "message": "A issue concluida nao possui comentario estruturado de reviewer.",
                }
            )

    return {
        "issue_key": issue_key,
        "summary": str(fields.get("summary", "")).strip(),
        "issue_type": issue_type,
        "status": status_name,
        "priority": str(((fields.get("priority") or {}).get("name")) or "").strip(),
        "current_agent_role": current_agent,
        "next_required_role": next_required_role,
        "agents_seen": agents_seen,
        "structured_comment_count": len(structured_comments),
        "latest_structured_comment_agent": latest_agent,
        "latest_structured_comment_status": latest_status,
        "findings": findings,
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Auditoria de comentarios por agente",
        "",
        f"- Projeto: `{report['project_key']}`",
        f"- JQL: `{report['jql']}`",
        f"- Issues auditadas: `{report['summary']['issues_audited']}`",
        f"- Issues com achados: `{report['summary']['issues_with_findings']}`",
        "",
        "## Achados por issue",
        "",
        "| Issue | Status | Agente atual | Comentarios estruturados | Achados |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report["issues"]:
        findings = item.get("findings") or []
        findings_text = (
            "<br>".join(f"`{entry['code']}`: {entry['message']}" for entry in findings) or "-"
        )
        lines.append(
            f"| {item['issue_key']} | {item['status']} | {item['current_agent_role'] or '-'} | "
            f"{item['structured_comment_count']} | {findings_text} |"
        )
    issues_with_findings = [entry for entry in report["issues"] if entry.get("findings")]
    if issues_with_findings:
        lines.extend(
            [
                "",
                "## Foco imediato",
                "",
            ]
        )
        for item in issues_with_findings[:10]:
            lines.append(
                f"- `{item['issue_key']}`: {', '.join(finding['code'] for finding in item['findings'])}"
            )
    return "\n".join(lines) + "\n"


def audit_issue_comments(
    repo_root: str | Path | None = None,
    *,
    jql: str = "",
    max_results: int = 100,
) -> dict[str, Any]:
    control = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control.atlassian_definition(), repo_root=control.repo_root
    )
    client = AtlassianHttpClient(resolved)
    jira = JiraAdapter(client)

    current_agent_field_id = jira.field_id_by_name("Current Agent Role")
    next_required_field_id = jira.field_id_by_name("Next Required Role")
    effective_jql = jql.strip() or f'project = "{resolved.jira_project_key}" ORDER BY updated DESC'
    issues = jira.search_issues(
        effective_jql,
        fields=[
            "summary",
            "status",
            "priority",
            "issuetype",
            current_agent_field_id,
            next_required_field_id,
        ],
        max_results=max_results,
    )
    evaluated = []
    for issue in issues:
        comments = jira.list_comments(str(issue.get("key", "")).strip(), max_results=500)
        evaluated.append(
            evaluate_issue_comment_contract(
                issue,
                comments,
                current_agent_field_id=current_agent_field_id,
                next_required_field_id=next_required_field_id,
            )
        )
    issues_with_findings = [item for item in evaluated if item.get("findings")]
    return {
        "project_key": resolved.jira_project_key,
        "jql": effective_jql,
        "summary": {
            "issues_audited": len(evaluated),
            "issues_with_findings": len(issues_with_findings),
        },
        "issues": evaluated,
    }


def write_report_files(
    report: dict[str, Any], *, json_out: Path | None, markdown_out: Path | None
) -> None:
    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if markdown_out:
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(render_markdown_report(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audita cobertura e paridade de comentarios por agente no Jira."
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--jql", default="")
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--json-out", default="")
    parser.add_argument("--markdown-out", default="")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    report = audit_issue_comments(
        args.repo_root,
        jql=args.jql,
        max_results=args.max_results,
    )
    write_report_files(
        report,
        json_out=Path(args.json_out).resolve() if args.json_out else None,
        markdown_out=Path(args.markdown_out).resolve() if args.markdown_out else None,
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
