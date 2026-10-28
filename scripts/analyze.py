import json, re
from pathlib import Path
import numpy as np, torch
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.metrics import roc_auc_score, balanced_accuracy_score
from concept_erasure import LeaceEraser

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "data" / "rows.json").read_text(encoding="utf-8"))
D = np.load(ROOT / "data" / "embeddings_conditions.npz")
y = np.array([r["y"] for r in rows])
g = np.array([1 if r["gender"] == "M" else 0 for r in rows])
base = np.array([r["base"] for r in rows])
n_base = base.max() + 1
rng = np.random.default_rng(11)
perm = rng.permutation(n_base)
train_bases = set(perm[: int(0.8 * n_base)].tolist())
tr = np.array([i for i, b in enumerate(base) if b in train_bases])
ho = np.array([i for i, b in enumerate(base) if b not in train_bases])

def fit_head(X, idx):
    pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=0.1))
    pipe.fit(X[idx], y[idx])
    return pipe

def metrics(pipe, X, idx, label=""):
    p = pipe.predict_proba(X[idx])[:, 1]
    yy, gg = y[idx], g[idx]
    auc = roc_auc_score(yy, p)
    bacc = balanced_accuracy_score(yy, p >= 0.5)
    f, m = p[gg == 0].mean(), p[gg == 1].mean()
    gap = f - m
    # paired male>female win rate
    by_base = {}
    for pi, bi, gi in zip(p, base[idx], gg):
        by_base.setdefault(int(bi), {})[int(gi)] = pi
    wins = [v[1] > v[0] for v in by_base.values() if 0 in v and 1 in v]
    win = float(np.mean(wins)) if wins else float("nan")
    # shortlist: top 20% overall
    thr = np.quantile(p, 0.80)
    sf, sm = (p[gg == 0] >= thr).mean(), (p[gg == 1] >= thr).mean()
    return dict(
        label=label, auc=float(auc), balanced_acc=float(bacc),
        score_f=float(f), score_m=float(m), gap_pp=float(gap * 100),
        male_win_rate=float(win), shortlist_f=float(sf), shortlist_m=float(sm),
        shortlist_gap_pp=float((sf - sm) * 100), threshold=float(thr),
    )

def probe_acc(X, idx, groups):
    pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=0.5))
    cv = GroupKFold(n_splits=5)
    scores = cross_val_score(pipe, X[idx], g[idx], cv=cv, groups=groups[idx], scoring="accuracy")
    return float(scores.mean()), float(scores.std())

L = 6
results = {"splits": {"train_rows": len(tr), "test_rows": len(ho), "train_bases": len(train_bases),
                      "test_bases": int(n_base - len(train_bases))}, "head": {}, "probe": {}, "activation": {}}

# per-condition heads
for c in ["full", "name_masked", "proxy_scrubbed"]:
    X = D[c + "_mean"][:, 0, :]
    pipe = fit_head(X, tr)
    results["head"][c] = metrics(pipe, X, ho, c)
    acc, sd = probe_acc(X, ho, base)
    results["probe"][c] = {"acc": acc, "sd": sd, "layer": L}

# LEACE on name_masked and proxy_scrubbed, layer 6 only
for c in ["name_masked", "proxy_scrubbed"]:
    X = D[c + "_mean"][:, 0, :]
    sc = StandardScaler().fit(X[tr])
    Xs = sc.transform(X)
    Xtr = torch.tensor(Xs[tr], dtype=torch.float32)
    ztr = torch.tensor(g[tr], dtype=torch.int64)
    er = LeaceEraser.fit(Xtr, ztr)
    Xe = er(torch.tensor(Xs, dtype=torch.float32)).numpy()
    key = c + "+leace"
    pipe = fit_head(Xe, tr)
    results["head"][key] = metrics(pipe, Xe, ho, key)
    acc, sd = probe_acc(Xe, ho, base)
    results["probe"][key] = {"acc": acc, "sd": sd, "layer": L}
    # activation geometry
    Xh = X[ho]
    v_before = Xh[g[ho] == 0].mean(0) - Xh[g[ho] == 1].mean(0)
    Xeh = Xe[ho]
    v_after = Xeh[g[ho] == 0].mean(0) - Xeh[g[ho] == 1].mean(0)
    cov = np.cov(Xh, rowvar=False)
    spec = np.linalg.norm(cov, 2)
    results["activation"][key] = {
        "norm_before": float(np.linalg.norm(v_before)),
        "norm_after": float(np.linalg.norm(v_after)),
        "mean_norm": float(np.mean(np.linalg.norm(Xh, axis=1))),
        "relative_before": float(np.linalg.norm(v_before) / np.mean(np.linalg.norm(Xh, axis=1))),
        "relative_after": float(np.linalg.norm(v_after) / np.mean(np.linalg.norm(Xeh, axis=1))),
        "presence_before": float(np.linalg.norm(v_before) / spec),
        "presence_after": float(np.linalg.norm(v_after) / spec),
        "cosine": float(np.dot(v_before, v_after) / (np.linalg.norm(v_before) * np.linalg.norm(v_after) + 1e-12)),
    }

# probe by layer on full
layer_probe = []
for l in range(D["full"].shape[1]):
    acc, sd = probe_acc(D["full"][:, l, :], ho, base)
    layer_probe.append({"layer": l, "acc": acc, "sd": sd})
results["layer_probe_full"] = layer_probe

# activation geometry for full and name_masked vs proxy floor
for c in ["full", "name_masked", "proxy_scrubbed"]:
    Xh = D[c + "_mean"][ho, 0, :]
    v = Xh[g[ho] == 0].mean(0) - Xh[g[ho] == 1].mean(0)
    cov = np.cov(Xh, rowvar=False)
    results["activation"][c] = {
        "norm": float(np.linalg.norm(v)),
        "mean_norm": float(np.mean(np.linalg.norm(Xh, axis=1))),
        "relative": float(np.linalg.norm(v) / np.mean(np.linalg.norm(Xh, axis=1))),
        "presence": float(np.linalg.norm(v) / np.linalg.norm(cov, 2)),
    }

# retention: proxy floor B, full biased Mb, name_masked+leace M'
B = results["activation"]["proxy_scrubbed"]["presence"]
Mb = results["activation"]["full"]["presence"]
Mp = results["activation"]["name_masked+leace"]["presence_after"]
results["retention"] = float((Mp - B) / (Mb - B)) if abs(Mb - B) > 1e-12 else None

with open(ROOT / "data" / "results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
