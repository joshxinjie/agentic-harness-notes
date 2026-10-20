# pass@k vs pass^k as k grows, for one task with n = 10 trials.
# Uses the estimators from lesson 6.4:
#   pass@k = 1 - C(n-c, k) / C(n, k)      pass^k = C(c, k) / C(n, k)
# c = 8 and c = 5 are the task results lesson 6.4/6.5 and the self-quiz use.
from math import comb
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

n = 10
ks = list(range(1, n + 1))

def pass_at_k(n, c, k):
    return 1.0 if n - c < k else 1 - comb(n - c, k) / comb(n, k)

def pass_hat_k(n, c, k):
    return comb(c, k) / comb(n, k)

plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(7, 6.2), dpi=100)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

blue, orange = "#2a6fdb", "#d9731a"
for c, color in [(8, blue), (5, orange)]:
    ax.plot(ks, [pass_at_k(n, c, k) for k in ks], color=color, lw=2.6,
            marker="o", ms=6, label=f"pass@k, {c}/10 passed")
    ax.plot(ks, [pass_hat_k(n, c, k) for k in ks], color=color, lw=2.6,
            ls="--", marker="s", ms=6, label=f"pass^k, {c}/10 passed")

ax.annotate("pass^3 = 0.47", xy=(3, pass_hat_k(n, 8, 3)), xytext=(4.6, 0.62),
            fontsize=14, color="#222",
            arrowprops=dict(arrowstyle="->", color="#444"))
ax.set_xlabel("k (trials that must pass / tries allowed)")
ax.set_ylabel("Score")
ax.set_xticks(ks)
ax.set_ylim(-0.03, 1.05)
ax.grid(alpha=0.3)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
          frameon=False, fontsize=13)
ax.set_title("One task, 10 trials", fontsize=16)
fig.tight_layout()
out = Path(__file__).resolve().parents[1] / "pass-at-k-vs-pass-hat-k.svg"
fig.savefig(out, format="svg", facecolor="white")
print("ok  ", out)
