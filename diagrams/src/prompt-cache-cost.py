"""Cost of one 10-turn investigator run (lesson 4.6): 4k prefix, +1.5k per turn.
Costs in thousands of base-input-token equivalents; reads 0.1x, writes 1.25x."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

no_cache = 40 + 1.5 * 45                      # 107.5k
auto = 4 * 1.25 + 90 * 0.1 + 9 * 1.5 * 1.25   # ~31k
broken = no_cache * 1.25                      # ~134k

labels = ["No caching", "Automatic\ncaching", "Timestamp at\ntop (broken)"]
values = [no_cache, auto, broken]
colors = ["#8a8f98", "#2f6db5", "#c4472f"]

plt.rcParams.update({"font.size": 15})
fig, ax = plt.subplots(figsize=(6.4, 4.6), facecolor="white")
ax.set_facecolor("white")
bars = ax.bar(labels, values, color=colors, width=0.6)
for b, v in zip(bars, values):
    ax.text(b.get_x() + b.get_width() / 2, v + 2.5, f"≈{v:.0f}k" if v != no_cache else "107.5k",
            ha="center", va="bottom", fontsize=15)
ax.set_ylabel("Cost (k base-input tokens)")
ax.set_ylim(0, 155)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("One 10-turn run", fontsize=16)
fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompt-cache-cost.svg")
fig.savefig(out, format="svg", facecolor="white")
print("ok", out)
