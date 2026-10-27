"""Every internal link and anchor resolves (tools/check_links.py). Run by CI and by reviewers through pytest."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_links_and_anchors_resolve():
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "check_links.py"), str(ROOT)],
                         capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.strip().endswith("bad 0"), out.stdout
