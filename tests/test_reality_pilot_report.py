"""Keep the rendered Reality Pilot report aligned with the checkout being reviewed."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_review_report_head_matches_git_head(tmp_path):
    output = tmp_path / "review-report.md"
    completed = subprocess.run(
        [sys.executable, "scripts/check_reality_pilot_report.py", "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    rendered = output.read_text(encoding="utf-8")
    assert f"Current PR/report HEAD: `{head}`" in rendered
    assert "本分支当前提交" not in rendered
    assert "Runtime implementation commit: `c2ce9ec6db5e79ebd0fd28a23d786712e0abdc79`" in rendered
