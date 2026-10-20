# Turn-9 input of the SG-03 investigator, from the numbers in lesson 2.1 (An example).
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

parts = [("Prompt + tools", 3, "#9db7e8"),
         ("Turn 1:\nmetrics, 30 days", 6, "#c9d8f3"),
         ("Turn 2: weather,\nsix stations", 9, "#f2b968"),
         ("Turns 3–8:\nre-queries", 13, "#c9d8f3")]
fig, ax = plt.subplots(figsize=(4.3, 4.4), dpi=100)
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
bottom = 0
for label, v, c in parts:
    ax.bar(0, v, bottom=bottom, width=0.55, color=c, edgecolor="#333333", linewidth=0.8)
    ax.text(0.33, bottom + v / 2, f"{label}  ({v}k)", va="center", ha="left", fontsize=11.5, color="#1a1a1a")
    bottom += v
ax.annotate("the one row\nthat matters\nis in here,\namong 143\nnear-identical\nrows",
            xy=(-0.29, 13.5), xytext=(-1.55, 13.5), va="center", ha="left", fontsize=10.5, color="#1a1a1a",
            arrowprops=dict(arrowstyle="->", color="#555555"))
ax.text(0, bottom + 0.8, "≈ 31k input tokens\non turn 9", ha="center", va="bottom", fontsize=11.5, weight="bold", color="#1a1a1a")
ax.set_xlim(-1.6, 1.75); ax.set_ylim(0, 37)
ax.set_ylabel("input tokens (thousands)", fontsize=10, color="#1a1a1a")
ax.set_xticks([]); ax.tick_params(colors="#1a1a1a", labelsize=10)
for s in ("top", "right", "bottom"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "investigator-context-budget.svg")
fig.savefig(out, format="svg", facecolor="white")
