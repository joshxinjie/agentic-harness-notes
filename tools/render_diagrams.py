#!/usr/bin/env python3
"""Render every diagrams/src/*.mmd to diagrams/<name>.svg.

Usage: python3 tools/render_diagrams.py [name ...]
Needs mermaid-cli (`npm i -g @mermaid-js/mermaid-cli`) and a Chromium.
SVGs use plain <text> labels (no HTML) and get a solid white, rounded
background so they stay readable in GitHub dark mode and the mobile app.
"""
import glob, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, "diagrams", "src"), os.path.join(ROOT, "diagrams")
CFG = os.path.join(ROOT, "tools", "mermaid-config.json")
# PUPPETEER_CONFIG overrides the Chromium path (the review workflow points it at the runner's Chrome).
PUP = os.environ.get("PUPPETEER_CONFIG") or os.path.join(ROOT, "tools", "puppeteer.json")

def add_background(path):
    svg = open(path, encoding="utf-8").read()
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg)
    if not m or 'id="bg-card"' in svg:
        return
    x, y, w, h = map(float, m.groups())
    pad = 16
    nx, ny, nw, nh = x - pad, y - pad, w + 2 * pad, h + 2 * pad
    svg = svg.replace(m.group(0), f'viewBox="{nx} {ny} {nw} {nh}"', 1)
    svg = re.sub(r'max-width:\s*[\d.]+px', f"max-width: {nw:.0f}px", svg, count=1)
    rect = f'<rect id="bg-card" x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="10" fill="#ffffff"/>'
    svg = re.sub(r"(<svg[^>]*>)", r"\1" + rect, svg, count=1)
    open(path, "w", encoding="utf-8").write(svg)

def main(names):
    files = [os.path.join(SRC, n + ".mmd") for n in names] if names else sorted(glob.glob(os.path.join(SRC, "*.mmd")))
    bad = 0
    for f in files:
        out = os.path.join(OUT, os.path.basename(f)[:-4] + ".svg")
        r = subprocess.run(["mmdc", "-q", "-i", f, "-o", out, "-c", CFG, "-p", PUP, "-b", "white"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL", f, r.stderr.strip()[-400:]); bad += 1; continue
        if "foreignObject" in open(out, encoding="utf-8").read():
            print("WARN html labels in", out)
        add_background(out)
        print("ok  ", os.path.relpath(out, ROOT))
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main(sys.argv[1:])
