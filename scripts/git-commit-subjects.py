from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from git_commit_subjects_lib import collect_commit_subjects
else:
    from scripts.git_commit_subjects_lib import collect_commit_subjects


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Coleta subjects de commits para validacao de convencoes Git."
    )
    parser.add_argument("--repo-root", default="", help="Raiz do repositorio Git.")
    parser.add_argument("--remote", default="origin", help="Remoto alvo da validacao.")
    parser.add_argument(
        "--range",
        dest="range_spec",
        default="",
        help="Range explicito de commits. Quando omitido, usa apenas commits exclusivos ao remoto.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()
    subjects = collect_commit_subjects(
        repo_root,
        remote=args.remote,
        range_spec=args.range_spec,
    )
    print(json.dumps(subjects, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
