#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_dispatch_lib import (
    DEFAULT_DECISIONS,
    DEFAULT_DELEGATION_OUT,
    DEFAULT_TRACKER,
    build_intake_payload,
    normalize_paths,
    render_delegation_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerar plano de delegacao em Markdown.")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--paths", default="")
    parser.add_argument("--risk", default="medium")
    parser.add_argument("--pending-action", default="")
    parser.add_argument("--worklog-file", default=str(DEFAULT_TRACKER))
    parser.add_argument("--worklog-id", default="")
    parser.add_argument("--decisions-file", default=str(DEFAULT_DECISIONS))
    parser.add_argument("--out", default=str(DEFAULT_DELEGATION_OUT))
    args = parser.parse_args()

    payload = build_intake_payload(
        message=args.intent,
        paths=normalize_paths(args.paths),
        risk=args.risk,
        route=True,
        pending_action=args.pending_action,
        tracker_file=Path(args.worklog_file),
        worklog_id=args.worklog_id,
        decisions_file=Path(args.decisions_file),
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_delegation_markdown(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
