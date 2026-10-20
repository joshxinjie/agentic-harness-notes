"""Sequential vs parallel tool calls on turn 2 of the investigator (lesson 5.6).

Illustrative numbers from the lesson: each model call ~4 s; tools take
metrics 1.5 s, weather 6 s, pipeline 0.8 s.
Sequential: 3 model calls + 8.3 s of tools (~20 s).
Parallel:   1 model call + the slowest tool (~10 s).
Writes diagrams/parallel-tool-timeline.svg with a white background.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "parallel-tool-timeline.svg")
MODEL, TOOLS = 4.0, [("metrics", 1.5), ("weather", 6.0), ("pipeline", 0.8)]
C_MODEL, C_TOOL = "#3b6fd4", "#e0a030"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 14})
fig, ax = plt.subplots(figsize=(7.2, 4.2), facecolor="white")
ax.set_facecolor("white")

# Sequential row (y = 3): model, tool, model, tool, model, tool
t = 0.0
for name, d in TOOLS:
    ax.barh(3, MODEL, left=t, height=0.6, color=C_MODEL, edgecolor="white")
    t += MODEL
    ax.barh(3, d, left=t, height=0.6, color=C_TOOL, edgecolor="white")
    t += d
seq_end = t
ax.text(seq_end + 0.3, 3, f"≈ {seq_end:.0f} s", va="center", fontsize=13, weight="bold")

# Parallel rows: one model call, then the three tools side by side
ax.barh(1, MODEL, left=0, height=0.6, color=C_MODEL, edgecolor="white")
for i, (name, d) in enumerate(TOOLS):
    y = 1.6 - i * 0.6
    ax.barh(y, d, left=MODEL, height=0.45, color=C_TOOL)
    ax.text(MODEL + d + 0.2, y, name, va="center", fontsize=12)
par_end = MODEL + max(d for _, d in TOOLS)
ax.text(par_end + 4.2, 1.0, f"≈ {par_end:.0f} s", va="center", fontsize=13, weight="bold")

ax.set_yticks([3, 1])
ax.set_yticklabels(["Sequential\n(3 model calls)", "Parallel\n(1 model call)"])
ax.set_xlabel("seconds (illustrative)")
ax.set_xlim(0, 24)
ax.set_ylim(0.2, 3.6)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)

from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C_MODEL, label="model call (~4 s)"),
                   Patch(color=C_TOOL, label="tool")],
          loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=False)
fig.tight_layout()
fig.savefig(OUT, facecolor="white")
