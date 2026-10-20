"""Build the context pack a reviewer reads: which files, in what order, within a token budget."""

import fnmatch
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

TEXT_SUFFIXES = {".py", ".md", ".mmd", ".yaml", ".yml", ".json", ".toml", ".txt", ".cfg", ".ini"}
MAX_FILE_BYTES = 200_000
MAX_DEPENDENTS = 10
CHARS_PER_TOKEN = 4          # rough; good enough for a budget, not for billing

# Lines that would tell the reviewer which model wrote the work (independence rule 1). Best effort only: the
# repo's own docs mention Claude in places, so blindness is partial.
ATTRIBUTION = re.compile(
    r"^.*(Co-Authored-By:|Claude-Session:|Generated with \[Claude Code\]|claude\.ai/code/session_).*$\n?",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class Item:
    label: str           # path, or a name such as "DIFF"
    text: str
    priority: int        # 0 kept first; higher numbers are dropped first when over budget

    @property
    def tokens(self) -> int:
        return len(self.text) // CHARS_PER_TOKEN + 1


def sanitize(text: str) -> str:
    return ATTRIBUTION.sub("", text)


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN + 1


def matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/"):
        return path.startswith(pattern) or fnmatch.fnmatch(path, pattern + "*")
    return fnmatch.fnmatch(path, pattern)


def readable(root: Path, rel: str, exclude: list[str]) -> str | None:
    p = root / rel
    if not p.is_file() or p.suffix not in TEXT_SUFFIXES or any(matches(rel, x) for x in exclude):
        return None
    if p.stat().st_size > MAX_FILE_BYTES:
        return p.read_text(errors="replace")[:MAX_FILE_BYTES] + "\n[... truncated by the review harness ...]\n"
    return p.read_text(errors="replace")


def pathspec_excludes(exclude: list[str]) -> list[str]:
    """Config exclude patterns as git pathspecs ('data/raw/' -> ':(exclude,glob)data/raw/**')."""
    out = []
    for x in exclude:
        pattern = x + "**" if x.endswith("/") else x
        out.append(f":(exclude,glob){pattern}")
    return out


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def find_dependents(root: Path, changed: list[str], limit: int = MAX_DEPENDENTS) -> list[str]:
    """Files that depend on the changed ones: Markdown pages that link to a changed page (their links and anchors
    can break), the page that embeds a changed diagram, and Python files that import a changed module or name a
    changed data file."""
    needles = []
    for rel in changed:
        p = Path(rel)
        if p.suffix == ".py" and p.stem != "__init__":
            mod = re.escape(p.stem)
            needles.append(re.compile(rf"^\s*(?:from\s+(?:[\w.]*\.)?{mod}\s+import|import\s+(?:[\w.]*\.)?{mod}\b)",
                                      re.MULTILINE))
        elif p.suffix in {".csv", ".json", ".parquet", ".yaml", ".yml", ".xlsx", ".txt"}:
            needles.append(re.compile(re.escape(p.name)))
    md_needles = []
    for rel in changed:
        p = Path(rel)
        if p.suffix == ".md":
            md_needles.append(re.compile(rf"\]\((?:[\w./-]*/)?{re.escape(p.name)}(?:#[^)]*)?\)"))
        elif p.suffix == ".mmd":                  # diagrams/src/x.mmd is embedded as diagrams/x.svg
            md_needles.append(re.compile(rf"{re.escape(p.stem)}\.svg"))
    found = []
    if md_needles:
        for md in sorted(root.rglob("*.md")):
            rel = md.relative_to(root).as_posix()
            if rel in changed or rel.startswith(".git/"):
                continue
            text = md.read_text(errors="replace")
            if any(n.search(text) for n in md_needles):
                found.append(rel)
                if len(found) >= limit:
                    return found
    for py in sorted(root.rglob("*.py")):
        rel = py.relative_to(root).as_posix()
        if rel in changed or rel.startswith((".git/", "data/raw/", "data/vintages/")):
            continue
        try:
            text = py.read_text(errors="replace")
        except OSError:
            continue
        if any(n.search(text) for n in needles):
            found.append(rel)
            if len(found) >= limit:
                break
    return found


def fit_to_budget(items: list[Item], budget: int) -> tuple[list[Item], list[str]]:
    """Drop the lowest-priority, largest items until the pack fits; return kept items and dropped labels."""
    kept = sorted(items, key=lambda it: it.priority)
    dropped = []
    while sum(it.tokens for it in kept) > budget and kept:
        worst = max(range(len(kept)), key=lambda k: (kept[k].priority, kept[k].tokens))
        if kept[worst].priority == 0:
            # Never drop instructions or the diff; truncate the largest priority-0 item instead.
            big = max(range(len(kept)), key=lambda k: kept[k].tokens)
            excess = sum(it.tokens for it in kept) - budget
            keep_chars = max(2000, (kept[big].tokens - excess) * CHARS_PER_TOKEN)
            kept[big] = Item(kept[big].label, kept[big].text[:keep_chars]
                             + "\n[... truncated by the review harness to fit the budget ...]\n", 0)
            dropped.append(f"{kept[big].label} (truncated)")
            break
        dropped.append(kept.pop(worst).label)
    return kept, dropped


def render(items: list[Item]) -> str:
    return "\n".join(f"===== {it.label} =====\n{it.text.rstrip()}\n" for it in items)


def build_pr_pack(root: Path, cfg: dict, base: str, head: str = "HEAD",
                  title: str = "", body: str = "") -> dict:
    ctx = cfg["context"]["pr"]
    exclude = cfg["context"]["project"]["exclude"]
    full_stat = git(root, "diff", "--numstat", f"{base}...{head}")
    diff = git(root, "diff", "--unified=3", f"{base}...{head}", "--", ".", *pathspec_excludes(exclude))
    omitted = [line.split("\t")[-1] for line in full_stat.splitlines()
               if line and any(matches(line.split("\t")[-1], x) for x in exclude)]
    if omitted:
        diff += ("\n[review harness: data and generated output files changed but left out of this diff: "
                 + ", ".join(omitted[:40]) + (" …" if len(omitted) > 40 else "") + "]\n")
    changed = [p for p in git(root, "diff", "--name-only", "--diff-filter=d", f"{base}...{head}").split() if p]
    items = [Item("PULL REQUEST", sanitize(f"Title: {title}\n\n{body}".strip()), 0),
             Item("DIFF", diff, 0)]
    for rel in ctx["always"]:
        if rel != cfg["instructions"] and (t := readable(root, rel, [])) is not None:   # instructions go in the system prompt
            items.append(Item(rel, t, 0))
    for rel in changed:
        if rel in ctx["always"]:
            continue
        if (t := readable(root, rel, exclude)) is not None:
            items.append(Item(rel, t, 1))
    deps = find_dependents(root, changed) if ctx.get("include_dependents") else []
    for rel in deps:
        if rel in ctx["always"]:                  # already in the pack
            continue
        if (t := readable(root, rel, exclude)) is not None:
            items.append(Item(rel, t, 2))
    kept, dropped = fit_to_budget(items, cfg["limits"]["max_input_tokens"]["pr"])
    return {"scope": "pr", "text": render(kept), "diff": diff, "changed": changed, "dependents": deps,
            "files": [it.label for it in kept], "dropped": dropped,
            "tokens": sum(it.tokens for it in kept)}


def build_project_pack(root: Path, cfg: dict, areas: list[str] | None = None) -> dict:
    ctx = cfg["context"]["project"]
    exclude = ctx["exclude"]
    items = []
    for rel in ctx["always"]:
        if rel != cfg["instructions"] and (t := readable(root, rel, [])) is not None:
            items.append(Item(rel, t, 0))
    seen = set(ctx["always"])
    for k, area in enumerate(areas or ctx["default_areas"]):
        hits = [root / area] if (root / area).is_file() else sorted((root / area.rstrip("/")).rglob("*")) \
            if (root / area.rstrip("/")).is_dir() else sorted(root.glob(area))
        for p in hits:
            rel = p.relative_to(root).as_posix()
            if rel in seen:
                continue
            if (t := readable(root, rel, exclude)) is not None:
                items.append(Item(rel, t, 1 + k))     # earlier areas matter more
                seen.add(rel)
    kept, dropped = fit_to_budget(items, cfg["limits"]["max_input_tokens"]["project"])
    return {"scope": "project", "text": render(kept), "diff": "", "changed": [], "dependents": [],
            "files": [it.label for it in kept], "dropped": dropped,
            "tokens": sum(it.tokens for it in kept)}
