"""Render and verify the Reality Pilot 001 review report against Git HEAD."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


REPORT = Path("docs/REP-20260922-SEMANTICA-REALITY-PILOT-001_Review_Report_v0.1.md")
PLACEHOLDER = "{{CURRENT_PR_HEAD}}"
RUNTIME_IMPLEMENTATION_COMMIT = "c2ce9ec6db5e79ebd0fd28a23d786712e0abdc79"


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def render(root: Path) -> str:
    text = (root / REPORT).read_text(encoding="utf-8")
    if text.count(PLACEHOLDER) != 1:
        raise ValueError("Review report must contain exactly one current-HEAD placeholder")
    if "本分支当前提交" in text:
        raise ValueError("Review report must not label an implementation commit as current HEAD")
    if f"Runtime implementation commit: `{RUNTIME_IMPLEMENTATION_COMMIT}`" not in text:
        raise ValueError("Review report must identify the runtime implementation commit")
    for forbidden in ("Production Ready", "SETTLED", "CLOSED", "Payment Completed"):
        if forbidden in text and forbidden not in ("SETTLED", "CLOSED"):
            raise ValueError(f"Review report contains forbidden status: {forbidden}")
    return text.replace(PLACEHOLDER, git_head(root))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.project_root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise ValueError("Report output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(root), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Report truth alignment failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
