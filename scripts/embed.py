import json, time
from pathlib import Path
import numpy as np, torch
from transformers import AutoTokenizer, AutoModel
from data import make_base, make_cv, label

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
N_BASE = 800
SEED = 7
rng = np.random.default_rng(SEED)

bases = [make_base(i) for i in range(N_BASE)]
rows = []
for i, b in enumerate(bases):
    for g in ["F", "M"]:
        y, p = label(b, g, seed=90000 + i * 2 + (g == "M"))
        rows.append(
            dict(base=i, gender=g, y=int(y), p=float(p), q=float(b["q"]), job=b["job"],
                 name_idx=b["name_idx"], text=make_cv(b, g))
        )

print("rows", len(rows), "female label rate", np.mean([r["y"] for r in rows if r["gender"] == "F"]),
      "male", np.mean([r["y"] for r in rows if r["gender"] == "M"]))

tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", output_hidden_states=True).eval()

texts = [r["text"] for r in rows]
t0 = time.time()
with torch.no_grad():
    enc = tok(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
    out = model(**enc)
print("encoded in", round(time.time() - t0, 1), "s")

H = torch.stack(out.hidden_states, dim=1).numpy()  # n, layers, seq, dim
Hcls = H[:, :, 0, :].astype(np.float32)            # CLS token per layer
np.savez_compressed(
    OUT / "embeddings.npz",
    Hcls=Hcls,
    y=np.array([r["y"] for r in rows]),
    gender=np.array([1 if r["gender"] == "M" else 0 for r in rows]),
    base=np.array([r["base"] for r in rows]),
    q=np.array([r["q"] for r in rows]),
)
with open(OUT / "rows.json", "w", encoding="utf-8") as f:
    json.dump(rows, f)
print("saved", Hcls.shape, OUT / "embeddings.npz")
