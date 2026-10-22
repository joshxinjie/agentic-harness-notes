#!/usr/bin/env python3
"""Build the contents list at the top of each week file, and "back to contents" links.

Usage:
  python3 tools/make_toc.py            # rewrite weeks/*.md in place
  python3 tools/make_toc.py --check    # exit 1 if any file is out of date (changes nothing)

What it writes, for every file in weeks/:
- Right under the "# Week N — ..." title, a block between <!-- toc --> and <!-- /toc -->:
  a "## Contents" heading, then one line per lesson ("## " heading) with links to that
  lesson's sections ("### " headings) on the line below, using short labels.
- A "[↑ Contents](#contents)" line before every later "## " heading, so you can jump back
  up from anywhere on a phone.
Anchors follow GitHub's rules (lowercase, punctuation dropped, spaces to hyphens, -1/-2
suffixes for repeated headings), the same rules tools/check_links.py checks against.
Run it after any change to headings; it is idempotent.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, END = "<!-- toc -->", "<!-- /toc -->"
BACK = "[↑ Contents](#contents)"

# Short labels for the lesson-template sections; anything else keeps its own text.
SHORT = {
    "the idea": "Idea",
    "an example": "Example",
    "where it lives in the harness": "In the harness",
    "common mistakes": "Mistakes",
    "why it matters": "Why it matters",
    "try it": "Try it",
    "worked answer": "Answer",
    "sources": "Sources",
    "recap": "Recap",
    "the week in six paragraphs": "Recap",
    "self-quiz": "Self-quiz",
    "self-quiz answers": "Quiz answers",
    "integrative exercise": "Exercise",
    "integrative answer": "Exercise answer",
    "integrative exercise — worked answer": "Exercise answer",  # Week 2's heading for the answer
}


def slug(text):
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # link text only
    t = t.strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def label(text):
    t = re.sub(r"`", "", text).strip()
    key = t.lower()
    if key in SHORT:
        return SHORT[key]
    for k, v in SHORT.items():  # "Sources (the week's anchors)", "Integrative exercise — run_site …"
        if key.startswith(k + " ") or key.startswith(k + "("):
            return v
    return re.split(r" — | \(", t)[0]


def strip_generated(lines):
    out, skip, drop_blank = [], False, False
    for ln in lines:
        s = ln.rstrip("\n")
        if drop_blank:
            drop_blank = False
            if s == "":
                continue
        if s == START:
            skip = True
            continue
        if s == END:
            skip = False
            drop_blank = True  # and one after the block
            continue
        if skip:
            continue
        if s == BACK:
            drop_blank = True  # the generator writes one blank line after it
            continue
        out.append(ln)
    if skip:
        raise ValueError(f"{START} has no matching {END}; fix it by hand (this file was not written)")
    return out


def headings(lines):
    """(index, level, text, anchor) for every #, ## and ### heading outside code fences."""
    res, counts, fence = [], {}, False
    for i, ln in enumerate(lines):
        if ln.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"(#{1,6}) (.*)", ln.rstrip("\n"))
        if not m:
            continue
        a = slug(m.group(2))
        if a in counts:
            counts[a] += 1
            a = f"{a}-{counts[a]}"
        else:
            counts[a] = 0
        res.append((i, len(m.group(1)), m.group(2), a))
    return res


def build(text):
    lines = strip_generated(text.splitlines(keepends=True))
    if not lines or not lines[0].startswith("# "):
        return text
    # Anchors as they will be once "## Contents" sits right after the title.
    probe = [lines[0], "\n", "## Contents\n"] + lines[1:]
    hs = headings(probe)
    toc = [START + "\n", "## Contents\n", "\n"]
    lessons = [h for h in hs if h[1] == 2 and h[2] != "Contents"]
    for n, (i, _, text_, a) in enumerate(lessons):
        end = lessons[n + 1][0] if n + 1 < len(lessons) else len(probe)
        subs = [h for h in hs if h[1] == 3 and i < h[0] < end]
        toc.append(f"- **[{re.sub(r'`', '', text_)}](#{a})**")
        if subs:
            toc.append("  \n  " + " · ".join(f"[{label(t)}](#{s})" for _, _, t, s in subs))
        toc.append("\n")
    toc += ["\n", END + "\n"]

    body = lines[1:]
    while body and body[0].strip() == "":
        body = body[1:]
    out = [lines[0], "\n"] + toc + ["\n"]
    first_lesson = True
    fence = False
    for ln in body:
        if ln.startswith("```"):
            fence = not fence
        if not fence and ln.startswith("## "):
            if first_lesson:
                first_lesson = False
            else:
                while out and out[-1].strip() in ("", "---"):
                    if out[-1].strip() == "---":
                        break
                    out.pop()
                out += ["\n", BACK + "\n", "\n"]
        out.append(ln)
    return "".join(out)


def main():
    check = "--check" in sys.argv
    stale = []
    for f in sorted(glob.glob(os.path.join(ROOT, "weeks", "*.md"))):
        old = open(f, encoding="utf-8").read()
        try:
            new = build(old)
        except ValueError as e:
            sys.exit(f"{os.path.relpath(f, ROOT)}: {e}")
        if new != old:
            stale.append(os.path.relpath(f, ROOT))
            if not check:
                open(f, "w", encoding="utf-8").write(new)
    if check and stale:
        print("contents out of date:", ", ".join(stale), "- run python3 tools/make_toc.py")
        sys.exit(1)
    print(("checked" if check else "updated"), len(stale) if not check else "ok")


if __name__ == "__main__":
    main()
