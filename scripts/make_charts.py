import json
from pathlib import Path
import numpy as np, torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from matplotlib.lines import Line2D
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from concept_erasure import LeaceEraser

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
res = json.loads((ROOT / "data/results.json").read_text())
abl = json.loads((ROOT / "data/ablations.json").read_text())
geo = json.loads((ROOT / "data/geometry.json").read_text())
D = np.load(ROOT / "data/embeddings_conditions.npz")
rows = json.loads((ROOT / "data/rows.json").read_text())

BG = "#0B0F17"
PANEL = "#121826"
INK = "#F0EFEC"
INK2 = "#C3C2B7"
MUTED = "#898781"
GRID = "#2C2C2A"
BORDER = "#2A3242"
BLUE = "#3987E5"
ORANGE = "#D95926"
GREEN = "#0CA30C"
RED = "#D03B3B"
AQUA = "#199E70"
GRAY = "#6F7682"

plt.rcParams.update({
    "font.family": "Segoe UI",
    "font.size": 12,
    "text.color": INK,
    "axes.labelcolor": INK2,
    "xtick.color": MUTED,
    "ytick.color": INK2,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
})

def rounded_barh(ax, y, width, height, color, radius=None):
    if abs(width) < 1e-9:
        ax.plot([0], [y], marker="o", markersize=5, color=color, zorder=3)
        return
    x0 = min(0, width)
    w = abs(width)
    r = min(height * 0.42, w * 0.42) if radius is None else radius
    p = FancyBboxPatch((x0, y - height / 2), w, height,
                       boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=color, ec="none", zorder=3)
    ax.add_patch(p)

def style_ax(ax):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, pad=8)

# ---------- 1. Behavioral gap ----------
fig, axes = plt.subplots(1, 2, figsize=(12.8, 7.2), dpi=220)
fig.subplots_adjust(left=0.18, right=0.97, top=0.72, bottom=0.16, wspace=0.16)
labels = ["Full CV", "Name masked", "Name masked\n+ LEACE", "All identity\ncues scrubbed"]
mean_gap = [res["head"]["full"]["gap_pp"], res["head"]["name_masked"]["gap_pp"],
            res["head"]["name_masked+leace"]["gap_pp"], res["head"]["proxy_scrubbed"]["gap_pp"]]
short_gap = [res["head"]["full"]["shortlist_gap_pp"], res["head"]["name_masked"]["shortlist_gap_pp"],
             res["head"]["name_masked+leace"]["shortlist_gap_pp"], res["head"]["proxy_scrubbed"]["shortlist_gap_pp"]]
colors = [RED, RED, GREEN, GRAY]
ypos = np.arange(len(labels))[::-1]
for ax, vals, title in [(axes[0], mean_gap, "Mean score gap"), (axes[1], short_gap, "Shortlist-rate gap")]:
    style_ax(ax)
    ax.axvline(0, color=INK2, lw=1.0, zorder=1)
    for y, v, c in zip(ypos, vals, colors):
        rounded_barh(ax, y, v, 0.48, c)
        if abs(v) < 0.08:
            ax.text(0.25, y, "0.0", ha="left", va="center", color=MUTED, fontsize=12)
        else:
            ax.text(v - 0.28, y, f"{v:.1f}", ha="right", va="center", color=INK, fontsize=12, fontweight="bold")
    ax.set_xlim(-16, 3)
    ax.set_ylim(-0.55, len(labels) - 0.45)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels if ax is axes[0] else [""] * len(labels), fontsize=11)
    ax.set_xticks([-16, -12, -8, -4, 0])
    ax.set_xticklabels(["−16", "−12", "−8", "−4", "0"], fontsize=10)
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_title(title, loc="left", color=INK, fontsize=15, fontweight="bold", pad=14)
fig.text(0.18, 0.925, "The gap survives anonymization", color=INK, fontsize=24, fontweight="bold")
fig.text(0.18, 0.875, "Female − male, percentage points. Held-out pairs, n = 320 CVs.", color=INK2, fontsize=11)
fig.text(0.18, 0.055, "Negative = female candidates score lower. 87% of the mean gap remains after the name is removed.",
         color=MUTED, fontsize=10)
fig.savefig(ASSETS / "gap_by_mitigation.png", bbox_inches=None, pad_inches=0)
plt.close(fig)

# ---------- 2. Feature contribution ----------
fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=220)
fig.subplots_adjust(left=0.24, right=0.96, top=0.72, bottom=0.14)
feat_labels = ["Name", "Pronouns", "Affiliation", "Career-gap reason", "All four cues"]
feat_vals = [3.75, 2.72, 0.43, 0.0, 8.83]
feat_pct = [42, 31, 5, 0, 100]
feat_colors = [ORANGE, BLUE, BLUE, BLUE, AQUA]
yf = np.array([4, 3, 2, 1, -0.6])
style_ax(ax)
for y, v, c, pct in zip(yf, feat_vals, feat_colors, feat_pct):
    rounded_barh(ax, y, v, 0.52, c)
    if v == 0:
        ax.text(0.22, y, "0.0 pp", ha="left", va="center", color=MUTED, fontsize=11)
    else:
        ax.text(v + 0.18, y, f"{v:.1f} pp  ·  {pct}%", ha="left", va="center", color=INK, fontsize=11, fontweight="bold")
ax.axhline(0.55, color=BORDER, lw=1.0)
ax.set_yticks(yf)
ax.set_yticklabels(feat_labels, fontsize=12)
ax.set_xlim(0, 10.6)
ax.set_ylim(-1.3, 4.75)
ax.set_xticks([0, 2, 4, 6, 8, 10])
ax.set_xticklabels(["0", "2", "4", "6", "8", "10"], fontsize=10)
ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
ax.set_title("Gap removed when one cue is ablated", loc="left", color=INK, fontsize=15, fontweight="bold", pad=14)
fig.text(0.24, 0.925, "Name is the largest single channel — not the whole gap", color=INK, fontsize=24, fontweight="bold")
fig.text(0.24, 0.875, "Percentage points removed from the 8.8 pp baseline gap; same ranker, held-out CVs.", color=INK2, fontsize=11)
fig.text(0.24, 0.055, "Cues overlap: individual bars do not add to the combined 8.8 pp. Removing all four is the only clean cut.",
         color=MUTED, fontsize=10)
fig.savefig(ASSETS / "feature_gap.png", bbox_inches=None, pad_inches=0)
plt.close(fig)

# ---------- 3. Activation PCA ----------
X = D["name_masked_mean"][:, 0, :]
y = np.array([r["y"] for r in rows]); g = np.array([r["gender"] == "M" for r in rows]).astype(int)
base = np.array([r["base"] for r in rows]); n = base.max() + 1
rng = np.random.default_rng(11); perm = rng.permutation(n)
trb = set(perm[: int(0.8 * n)].tolist())
tr = np.array([i for i, b in enumerate(base) if b in trb])
ho = np.array([i for i, b in enumerate(base) if b not in trb])
sc = StandardScaler().fit(X[tr]); Xs = sc.transform(X)
er = LeaceEraser.fit(torch.tensor(Xs[tr], dtype=torch.float32), torch.tensor(g[tr], dtype=torch.int64))
Xe = er(torch.tensor(Xs, dtype=torch.float32)).numpy()

def pca2(A):
    Z = PCA(n_components=2, random_state=0).fit_transform(A[ho])
    return Z

Z0, Z1 = pca2(Xs), pca2(Xe)
fig, axes = plt.subplots(1, 2, figsize=(12.8, 7.2), dpi=220)
fig.subplots_adjust(left=0.035, right=0.975, top=0.70, bottom=0.11, wspace=0.08)
for ax, Z, title, probe, rel in [
    (axes[0], Z0, "Before LEACE", 100.0, geo["name_masked"]["relative"]),
    (axes[1], Z1, "After LEACE", 57.8, geo["leace"]["relative_after"]),
]:
    ax.set_facecolor(BG)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.axhline(0, color=GRID, lw=0.8); ax.axvline(0, color=GRID, lw=0.8)
    for gi, c, lab in [(0, BLUE, "Female"), (1, ORANGE, "Male")]:
        pts = Z[g[ho] == gi]
        ax.scatter(pts[:, 0], pts[:, 1], s=22, color=c, alpha=0.58, edgecolors=BG, linewidths=0.5, zorder=2)
        m = pts.mean(0)
        ax.scatter([m[0]], [m[1]], s=150, color=c, edgecolors=INK, linewidths=1.8, zorder=4)
    # mean-difference line
    mf = Z[g[ho] == 0].mean(0); mm = Z[g[ho] == 1].mean(0)
    ax.annotate("", xy=mm, xytext=mf, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, shrinkA=4, shrinkB=4), zorder=3)
    ax.set_title(title, loc="left", color=INK, fontsize=14, fontweight="bold", pad=20)
    ax.text(0.025, 0.955, f"probe {probe:.0f}%  ·  ‖v‖/mean‖h‖ = {rel:.2f}", transform=ax.transAxes,
            color=INK2, fontsize=10, va="top", bbox=dict(facecolor=BG, edgecolor="none", pad=2.5, alpha=0.95))
# shared legend
handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, markeredgecolor=BLUE, markersize=8, label="Female"),
           Line2D([0], [0], marker="o", color="none", markerfacecolor=ORANGE, markeredgecolor=ORANGE, markersize=8, label="Male")]
fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.975, 0.925), ncol=2, frameon=False,
           fontsize=10, labelcolor=INK2, handletextpad=0.4, columnspacing=1.4)
fig.text(0.035, 0.94, "The gender direction is mostly erased", color=INK, fontsize=24, fontweight="bold")
fig.text(0.035, 0.885, "PCA of layer-6 MiniLM embeddings, held-out CVs. Probe = 5-fold group CV; chance = 50%.", color=INK2, fontsize=11)
fig.text(0.035, 0.025, "LEACE is fit on the training split only, then applied to held-out representations.", color=MUTED, fontsize=9.5)
fig.savefig(ASSETS / "activation_pca.png", bbox_inches=None, pad_inches=0)
plt.close(fig)

# ---------- 4. ATS compare mock ----------
fig = plt.figure(figsize=(16, 9), dpi=200)
fig.patch.set_facecolor("#070A0F")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
ax.add_patch(Rectangle((0, 0), 16, 9, color="#070A0F", zorder=0))
# header
ax.text(0.65, 8.45, "TALENTSCAN", color=INK, fontsize=13, fontweight="bold", va="center")
ax.text(0.65, 8.12, "CANDIDATE RANKING  /  SALES MANAGER  /  REQ #2041", color=MUTED, fontsize=8.5, va="center")
ax.text(15.35, 8.42, "ILLUSTRATIVE INTERFACE", color=GRAY, fontsize=8, ha="right", va="center")
ax.plot([0.65, 15.35], [7.95, 7.95], color=BORDER, lw=1)

def card(x, name, pron, score, accent, aff, rank):
    w, h, y0 = 6.35, 5.3, 1.75
    ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0,rounding_size=0.14",
                                fc=PANEL, ec=BORDER, lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x, y0 + h - 0.12), w, 0.12, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=accent, ec="none", zorder=3))
    ax.text(x + 0.35, y0 + h - 0.45, f"#{rank}", color=GRAY, fontsize=10, fontweight="bold")
    ax.text(x + 0.35, y0 + h - 0.95, name, color=INK, fontsize=21, fontweight="bold")
    ax.text(x + 0.35, y0 + h - 1.32, pron + "  ·  Bristol, UK", color=INK2, fontsize=10)
    ax.plot([x + 0.35, x + w - 0.35], [y0 + h - 1.58, y0 + h - 1.58], color=BORDER, lw=1)
    ax.text(x + 0.35, y0 + h - 1.98, "Senior Sales Manager  ·  5 years", color=INK, fontsize=11)
    ax.text(x + 0.35, y0 + h - 2.30, "MSc Public Health  ·  CRM, negotiation, pipeline", color=INK2, fontsize=9.5)
    ax.text(x + 0.35, y0 + h - 2.62, "8 projects  ·  27% KPI improvement", color=INK2, fontsize=9.5)
    ax.text(x + 0.35, y0 + h - 3.02, "AFFILIATION", color=GRAY, fontsize=7.5, fontweight="bold")
    ax.text(x + 0.35, y0 + h - 3.25, aff, color=INK2, fontsize=9.5)
    # score
    ax.text(x + 0.35, y0 + 0.90, "PREDICTED SHORTLIST PROBABILITY", color=GRAY, fontsize=7.5, fontweight="bold")
    ax.text(x + 0.35, y0 + 0.22, f"{score:.1f}%", color=accent, fontsize=42, fontweight="bold", va="bottom")
    # meter track
    ax.add_patch(FancyBboxPatch((x + 0.35, y0 + 0.12), w - 0.7, 0.09, boxstyle="round,pad=0,rounding_size=0.045",
                                fc="#222A38", ec="none", zorder=3))
    ax.add_patch(FancyBboxPatch((x + 0.35, y0 + 0.12), (w - 0.7) * score / 100, 0.09,
                                boxstyle="round,pad=0,rounding_size=0.045", fc=accent, ec="none", zorder=4))

card(0.65, "Sarah Nguyen", "she/her", 51.8, ORANGE, "Girls Who Code mentor", 2)
card(8.95, "Michael Nguyen", "he/him", 60.6, GREEN, "Sigma Chi fraternity", 1)
# delta
ax.add_patch(FancyBboxPatch((7.15, 4.15), 1.65, 0.55, boxstyle="round,pad=0,rounding_size=0.12",
                            fc="#2A1714", ec=ORANGE, lw=1.0, zorder=5))
ax.text(7.975, 4.425, "−8.8 pp", color=ORANGE, fontsize=12, fontweight="bold", ha="center", va="center", zorder=6)
ax.text(0.65, 0.85, "Same qualifications. Different identity cues. The ranker moves the male candidate ahead.",
        color=INK2, fontsize=10.5)
ax.text(0.65, 0.50, "Scores are real outputs from the prototype ranker; names and layout are a mock ATS view.",
        color=MUTED, fontsize=8.5)
fig.savefig(ASSETS / "ats_compare.png", bbox_inches="tight", pad_inches=0, facecolor=fig.get_facecolor())
plt.close(fig)

# ---------- 5. Audit console ----------
fig = plt.figure(figsize=(16, 9), dpi=200)
fig.patch.set_facecolor("#070A0F")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
ax.add_patch(Rectangle((0, 0), 16, 9, color="#070A0F", zorder=0))
# chrome
ax.add_patch(FancyBboxPatch((0.45, 0.35), 15.1, 8.3, boxstyle="round,pad=0,rounding_size=0.12",
                            fc="#0C111A", ec=BORDER, lw=1.0, zorder=1))
for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
    ax.add_patch(Circle((0.78 + i * 0.22, 8.28), 0.055, color=c, zorder=4))
ax.text(1.55, 8.28, "ATS BIAS AUDIT  /  RUN 004", color=INK, fontsize=10, fontweight="bold", va="center")
ax.text(15.15, 8.28, "PROTOTYPE  ·  MINILM-L6  ·  1,600 CVs", color=GRAY, fontsize=7.5, ha="right", va="center")
ax.plot([0.65, 15.35], [8.02, 8.02], color=BORDER, lw=1)

def panel(x, y, w, h, title, kicker=""):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.1",
                                fc=PANEL, ec=BORDER, lw=1.0, zorder=2))
    ax.text(x + 0.28, y + h - 0.32, title, color=INK, fontsize=10, fontweight="bold", va="center")
    if kicker:
        ax.text(x + 0.28, y + h - 0.57, kicker, color=GRAY, fontsize=7.2, va="center")

# panel 1: behavior gap
panel(0.85, 4.65, 6.75, 2.95, "BEHAVIORAL GAP", "female − male score, pp")
vals = [(-8.83, "Full CV", RED), (-7.70, "Name masked", RED), (-0.18, "Name masked + LEACE", GREEN)]
for i, (v, lab, c) in enumerate(vals):
    yy = 6.55 - i * 0.62
    ax.text(1.15, yy, lab, color=INK2, fontsize=8.5, va="center")
    ax.add_patch(FancyBboxPatch((3.15, yy - 0.12), abs(v) / 9.0 * 3.85, 0.24,
                                boxstyle="round,pad=0,rounding_size=0.08", fc=c, ec="none", zorder=3))
    ax.text(3.15 + abs(v) / 9.0 * 3.85 + 0.10, yy, f"{v:.1f}", color=INK, fontsize=9, fontweight="bold", va="center")
ax.plot([3.15, 3.15], [5.35, 7.05], color=INK2, lw=0.8)
ax.text(6.15, 5.02, "87% of gap survives name masking", color=ORANGE, fontsize=8, ha="right")

# panel 2: probe
panel(7.95, 4.65, 6.2, 2.95, "REPRESENTATION PROBE", "linear gender classifier, layer 6")
ax.text(8.3, 6.30, "100%", color=RED, fontsize=34, fontweight="bold", va="center")
ax.text(9.72, 6.34, "→", color=GRAY, fontsize=22, va="center")
ax.text(10.16, 6.30, "57.8%", color=GREEN, fontsize=34, fontweight="bold", va="center")
ax.text(8.3, 5.55, "before", color=MUTED, fontsize=8)
ax.text(10.16, 5.55, "after LEACE", color=MUTED, fontsize=8)
ax.plot([8.3, 13.75], [5.18, 5.18], color=GRID, lw=1.0)
ax.plot([8.3 + (50 / 100) * 5.45, 8.3 + (50 / 100) * 5.45], [5.06, 5.30], color=INK2, lw=1.0)
ax.text(8.3 + (50 / 100) * 5.45, 4.92, "chance 50%", color=MUTED, fontsize=7, ha="center")

# panel 3: features
panel(0.85, 1.05, 6.75, 3.25, "FEATURE CONTRIBUTION", "gap removed when cue is ablated, pp")
ff = [("Name", 3.75, ORANGE), ("Pronouns", 2.72, BLUE), ("Affiliation", 0.43, BLUE)]
for i, (lab, v, c) in enumerate(ff):
    yy = 3.27 - i * 0.62
    ax.text(1.15, yy, lab, color=INK2, fontsize=8.5, va="center")
    ax.add_patch(FancyBboxPatch((3.15, yy - 0.12), v / 4.1 * 3.4, 0.24,
                                boxstyle="round,pad=0,rounding_size=0.08", fc=c, ec="none", zorder=3))
    ax.text(3.15 + v / 4.1 * 3.4 + 0.10, yy, f"{v:.1f}", color=INK, fontsize=9, fontweight="bold", va="center")
ax.text(1.15, 1.38, "All four identity cues", color=INK2, fontsize=8.5, va="center")
ax.add_patch(FancyBboxPatch((3.15, 1.26), 3.4, 0.24, boxstyle="round,pad=0,rounding_size=0.08", fc=AQUA, ec="none", zorder=3))
ax.text(3.15 + 3.4 + 0.10, 1.38, "8.8", color=INK, fontsize=9, fontweight="bold", va="center")

# panel 4: gate
panel(7.95, 1.05, 6.2, 3.25, "DEPLOYMENT GATE", "all checks must pass together")
checks = [("Behavioral gap", "0.2 pp", GREEN), ("Gender probe", "57.8%", GREEN),
          ("Ranking AUC", "0.735", GREEN), ("Bias retention", "4.7%", GREEN)]
for i, (lab, val, c) in enumerate(checks):
    yy = 3.55 - i * 0.58
    ax.add_patch(Circle((8.35, yy), 0.075, color=c, zorder=3))
    ax.text(8.58, yy, lab, color=INK2, fontsize=8.5, va="center")
    ax.text(13.55, yy, val, color=INK, fontsize=8.5, fontweight="bold", ha="right", va="center")
ax.add_patch(FancyBboxPatch((11.65, 1.28), 2.12, 0.38, boxstyle="round,pad=0,rounding_size=0.10",
                            fc="#0B2414", ec=GREEN, lw=1.0, zorder=4))
ax.text(12.71, 1.47, "PASS  /  SHIP", color=GREEN, fontsize=9, fontweight="bold", ha="center", va="center", zorder=6)

ax.text(0.85, 0.62, "Synthetic benchmark with known ground truth. Absolute scores are not a production claim.",
        color=MUTED, fontsize=7.5)
ax.text(15.15, 0.62, "seed 7  ·  8 job families  ·  10 features", color=GRAY, fontsize=7.5, ha="right")
fig.savefig(ASSETS / "audit_console.png", bbox_inches="tight", pad_inches=0, facecolor=fig.get_facecolor())
plt.close(fig)

print("charts written to", ASSETS)
