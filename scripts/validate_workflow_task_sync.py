#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
TASKFILE_PATH = ROOT / "Taskfile.yml"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
TASKS_DOC = ROOT / "docs" / "TASKS.md"
WORKFLOWS_DOC = ROOT / "docs" / "WORKFLOWS.md"
TASK_COMMAND_RE = re.compile(r"\btask\s+([A-Za-z0-9:_-]+)\b")
TASK_DOC_RE = re.compile(r"^### `([^`]+)`$", re.MULTILINE)
WORKFLOW_DOC_RE = re.compile(r"^### `([^`]+)`$(.*?)^(?=### |\Z)", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
ADDITIONAL_REQUIRED_DOCS = {
    "ai:chat:intake",
    "ai:route",
    "ai:delegate",
    "ai:eval:smoke",
    "ci:workflow:sync:check",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} nao parseou como objeto YAML")
    return payload


def collect_task_names(path: Path, prefix: str = "") -> set[str]:
    payload = load_yaml(path)
    names: set[str] = set()
    tasks = payload.get("tasks", {})
    if isinstance(tasks, dict):
        for task_name in tasks:
            names.add(f"{prefix}:{task_name}" if prefix else str(task_name))

    includes = payload.get("includes", {})
    if not isinstance(includes, dict):
        return names

    for namespace, include in includes.items():
        include_path: str | None = None
        if isinstance(include, str):
            include_path = include
        elif isinstance(include, dict):
            candidate = include.get("taskfile") or include.get("path")
            if isinstance(candidate, str):
                include_path = candidate
        if include_path is None:
            continue
        names.update(collect_task_names((path.parent / include_path).resolve(), str(namespace)))
    return names


def collect_workflow_task_usage() -> dict[str, set[str]]:
    usage: dict[str, set[str]] = {}
    for workflow_path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        payload = load_yaml(workflow_path)
        tasks: set[str] = set()
        jobs = payload.get("jobs", {})
        if not isinstance(jobs, dict):
            raise ValueError(f"{workflow_path.name}: jobs deve ser objeto")
        for job in jobs.values():
            if not isinstance(job, dict):
                continue
            steps = job.get("steps", [])
            if not isinstance(steps, list):
                continue
            for step in steps:
                if not isinstance(step, dict):
                    continue
                run = step.get("run")
                if not isinstance(run, str):
                    continue
                for line in run.splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    for match in TASK_COMMAND_RE.finditer(stripped):
                        tasks.add(match.group(1))
        usage[workflow_path.name] = tasks
    return usage


def parse_task_docs() -> set[str]:
    return set(TASK_DOC_RE.findall(TASKS_DOC.read_text(encoding="utf-8")))


def parse_workflow_docs() -> dict[str, set[str]]:
    content = WORKFLOWS_DOC.read_text(encoding="utf-8")
    parsed: dict[str, set[str]] = {}
    for workflow_name, block in WORKFLOW_DOC_RE.findall(content):
        block_tasks: set[str] = set()
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped.startswith("- Tasks"):
                continue
            block_tasks.update(token for token in INLINE_CODE_RE.findall(stripped) if ":" in token)
        parsed[workflow_name] = block_tasks
    return parsed


def validate_sync() -> list[str]:
    errors: list[str] = []
    task_names = collect_task_names(TASKFILE_PATH)
    workflow_usage = collect_workflow_task_usage()
    documented_tasks = parse_task_docs()
    documented_workflows = parse_workflow_docs()

    for required in sorted(ADDITIONAL_REQUIRED_DOCS):
        if required not in documented_tasks:
            errors.append(f"docs/TASKS.md sem task obrigatoria documentada: {required}")

    for workflow_name, referenced_tasks in workflow_usage.items():
        if workflow_name not in documented_workflows:
            errors.append(f"docs/WORKFLOWS.md sem secao para workflow: {workflow_name}")
            continue
        for task in sorted(referenced_tasks):
            if task not in task_names:
                errors.append(f"{workflow_name} referencia task inexistente: {task}")
            if task not in documented_tasks:
                errors.append(f"docs/TASKS.md sem task usada em workflow: {task}")
        documented_in_block = documented_workflows[workflow_name]
        missing_from_block = sorted(referenced_tasks - documented_in_block)
        extra_in_block = sorted(documented_in_block - referenced_tasks)
        if missing_from_block:
            errors.append(
                f"docs/WORKFLOWS.md sem tasks referenciadas por {workflow_name}: {', '.join(missing_from_block)}"
            )
        if extra_in_block:
            errors.append(
                f"docs/WORKFLOWS.md lista tasks extras em {workflow_name}: {', '.join(extra_in_block)}"
            )
    return errors


def main() -> int:
    errors = validate_sync()
    if errors:
        print("[FAIL] Erros de sincronismo workflow-task-doc:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("[OK] Workflows, tasks e catalogos estao sincronizados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
