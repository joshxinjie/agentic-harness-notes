"""tools/make_toc.py: contents lists are current, stable, reversible, and use the same anchors as check_links.py."""

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("make_toc", ROOT / "tools" / "make_toc.py")
toc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toc)

WEEKS = sorted((ROOT / "weeks").glob("*.md"))

FIXTURE = """# Week 9 — Fixture

Intro line.

## 9.1 First lesson

### The idea

Text.

### Try it

```
## not a heading
```

### Worked answer

---

## 9.2 Second lesson

### The idea

### Sources (the week's anchors)

## Week 9 review

### Integrative exercise — `run_site`, week-3 edition

### Integrative exercise — worked answer
"""


def test_build_is_idempotent_and_reversible():
    once = toc.build(FIXTURE)
    assert once != FIXTURE
    assert toc.build(once) == once
    assert "".join(toc.strip_generated(once.splitlines(True))) == FIXTURE


@pytest.mark.parametrize("heading, short", [
    ("Sources (the week's anchors)", "Sources"),
    ("Integrative exercise — `run_site`, week-3 edition", "Exercise"),
    ("Integrative exercise — worked answer", "Exercise answer"),
    ("Worked answer", "Answer"),
    ("Something else — with a tail", "Something else"),
])
def test_label(heading, short):
    assert toc.label(heading) == short


def test_unclosed_marker_raises_instead_of_truncating():
    broken = toc.build(FIXTURE).replace(toc.END + "\n", "")
    with pytest.raises(ValueError):
        toc.build(broken)


def check_links_anchors(lines):
    """Anchors exactly as tools/check_links.py computes them (its slug() is copied out of the script)."""
    src = (ROOT / "tools" / "check_links.py").read_text()
    ns = {"re": re}
    exec(re.search(r"def slug\(h\):\n(?:    .*\n)+", src).group(0), ns)
    res, cnt, inc = [], {}, False
    for line in lines:
        if line.startswith("```"):
            inc = not inc
        if inc:
            continue
        m = re.match(r"#+ (.*)", line)
        if m:
            a = ns["slug"](m.group(1))
            if a in cnt:
                cnt[a] += 1
                a = f"{a}-{cnt[a]}"
            else:
                cnt[a] = 0
            res.append(a)
    return res


@pytest.mark.parametrize("path", [None] + WEEKS, ids=lambda p: p.name if p else "fixture")
def test_anchors_match_check_links(path):
    text = path.read_text(encoding="utf-8") if path else toc.build(FIXTURE + "## Week 9 review\n")
    lines = text.splitlines(True)
    assert [h[3] for h in toc.headings(lines)] == check_links_anchors(lines)


@pytest.mark.parametrize("path", WEEKS, ids=lambda p: p.name)
def test_week_contents_are_current(path):
    """The --check invariant, run in CI through pytest so a stale list fails the pull request."""
    text = path.read_text(encoding="utf-8")
    assert toc.build(text) == text, f"{path.name}: run python3 tools/make_toc.py"
