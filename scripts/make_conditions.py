import json, re, time
from pathlib import Path
import numpy as np, torch
from transformers import AutoTokenizer, AutoModel

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "data" / "rows.json").read_text(encoding="utf-8"))

def name_masked(text):
    lines = text.split("\n")
    lines[0] = "Candidate"
    return "\n".join(lines)

def proxy_scrubbed(text):
    t = name_masked(text)
    t = re.sub(r"^(she/her|he/him) \| ", "", t, flags=re.M)
    t = re.sub(r"\nAFFILIATIONS\n.*?(?=\nCAREER NOTE|\Z)", "", t, flags=re.S)
    t = t.replace("(parental leave)", "(career break)").replace("(sabbatical)", "(career break)")
    return t

CONDS = {
    "full": lambda t: t,
    "name_masked": name_masked,
    "proxy_scrubbed": proxy_scrubbed,
}

tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", output_hidden_states=True).eval()

out = {}
for cname, fn in CONDS.items():
    texts = [fn(r["text"]) for r in rows]
    hs = []; means = []
    t0 = time.time()
    for i in range(0, len(texts), 64):
        batch = texts[i:i+64]
        with torch.no_grad():
            enc = tok(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            o = model(**enc)
            h = torch.stack(o.hidden_states, dim=1)[:, :, 0, :].numpy().astype(np.float32)
            mask = enc["attention_mask"].unsqueeze(-1).float()
            m = (o.hidden_states[-1] * mask).sum(1) / mask.sum(1).clamp(min=1)
        hs.append(h); means.append(m.numpy().astype(np.float32))
    out[cname] = np.concatenate(hs, axis=0)
    out[cname + "_mean"] = np.concatenate(means, axis=0)[:, None, :]
    print(cname, out[cname].shape, out[cname+"_mean"].shape, "in", round(time.time()-t0,1), "s")

np.savez_compressed(ROOT / "data" / "embeddings_conditions.npz", **out)
print("saved")
