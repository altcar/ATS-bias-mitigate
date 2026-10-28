import json, re, time
from pathlib import Path
import numpy as np, torch
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from transformers import AutoTokenizer, AutoModel

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "data" / "rows.json").read_text(encoding="utf-8"))
D = np.load(ROOT / "data" / "embeddings_conditions.npz")
y = np.array([r["y"] for r in rows]); g = np.array([r["gender"] == "M" for r in rows]).astype(int)
base = np.array([r["base"] for r in rows]); n_base = base.max() + 1
rng = np.random.default_rng(11); perm = rng.permutation(n_base)
train_bases = set(perm[: int(0.8 * n_base)].tolist())
tr = np.array([i for i, b in enumerate(base) if b in train_bases])
ho = np.array([i for i, b in enumerate(base) if b not in train_bases])

# Full model, mean-pooled layer 6
X = D["full_mean"][:, 0, :]
head = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=0.1)).fit(X[tr], y[tr])

def gap(p, idx):
    f, m = p[g[idx] == 0].mean(), p[g[idx] == 1].mean()
    thr = np.quantile(p, 0.80)
    sf, sm = (p[g[idx] == 0] >= thr).mean(), (p[g[idx] == 1] >= thr).mean()
    return float((f - m) * 100), float((sf - sm) * 100)

def ablate_name(t):
    ls = t.split("\n"); ls[0] = "Candidate"; return "\n".join(ls)

def ablate_pronoun(t):
    return re.sub(r"^(she/her|he/him) \| ", "", t, flags=re.M)

def ablate_affiliation(t):
    return re.sub(r"\nAFFILIATIONS\n.*?(?=\nCAREER NOTE|\Z)", "", t, flags=re.S)

def ablate_gap(t):
    return t.replace("(parental leave)", "(career break)").replace("(sabbatical)", "(career break)")

def ablate_skills(t):
    return re.sub(r"(CORE SKILLS\n).*?(\n\nEXPERIENCE)", r"\1Relevant professional skills\2", t, flags=re.S)

def ablate_years(t):
    return re.sub(r"\b\d+ years\b", "several years", t)

def ablate_education(t):
    return re.sub(r"(EDUCATION\n).*?(\n\nAFFILIATIONS|\Z)", r"\1Relevant degree\2", t, flags=re.S)

def ablate_seniority(t):
    return re.sub(r"\b(Junior|Mid-level|Senior|Lead)\b", "Professional", t)

def ablate_certs(t):
    return re.sub(r"\n- Held \d+ professional certification(s)?\.", "", t)

def ablate_projects(t):
    return re.sub(r"\n- Delivered \d+ projects; improved key performance metric by \d+%\.", "\n- Delivered projects on time and within budget.", t)

FEATURES = {
    "name": ablate_name,
    "pronouns": ablate_pronoun,
    "affiliation": ablate_affiliation,
    "career-gap reason": ablate_gap,
    "skills match": ablate_skills,
    "years experience": ablate_years,
    "education": ablate_education,
    "seniority": ablate_seniority,
    "certifications": ablate_certs,
    "project count": ablate_projects,
}

def group_identity(t):
    for f in [ablate_name, ablate_pronoun, ablate_affiliation, ablate_gap]: t = f(t)
    return t

def group_quals(t):
    for f in [ablate_skills, ablate_years, ablate_education, ablate_seniority, ablate_certs, ablate_projects]: t = f(t)
    return t

FEATURES["ALL identity cues"] = group_identity
FEATURES["ALL qualification cues"] = group_quals

tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2").eval()

def encode(texts):
    out = []
    for i in range(0, len(texts), 64):
        batch = texts[i:i+64]
        with torch.no_grad():
            enc = tok(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            h = model(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1).float()
            out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).numpy().astype(np.float32))
    return np.concatenate(out, axis=0)

base_texts = [rows[i]["text"] for i in ho]
p0 = head.predict_proba(X[ho])[:, 1]
gap0, sg0 = gap(p0, ho)
res = {"baseline": {"gap_pp": gap0, "shortlist_gap_pp": sg0, "mean_score": float(p0.mean())}, "features": {}}
print("baseline", res["baseline"])

for name, fn in FEATURES.items():
    t0 = time.time()
    texts = [fn(t) for t in base_texts]
    Xa = encode(texts)
    p = head.predict_proba(Xa)[:, 1]
    gg, sg = gap(p, ho)
    res["features"][name] = {
        "gap_pp": gg, "shortlist_gap_pp": sg,
        "gap_removed_pp": gap0 - gg,
        "gap_removed_pct": (gap0 - gg) / gap0 * 100 if gap0 else 0,
        "mean_score_change_pp": float((p.mean() - p0.mean()) * 100),
        "auc": float(roc_auc_score(y[ho], p)),
    }
    print(f"{name:24s} gap {gg:6.2f} pp  removed {gap0-gg:6.2f} pp  score {res['features'][name]['mean_score_change_pp']:6.2f} pp  ({time.time()-t0:.0f}s)")

with open(ROOT / "data" / "ablations.json", "w", encoding="utf-8") as f:
    json.dump(res, f, indent=2)
print("saved")
