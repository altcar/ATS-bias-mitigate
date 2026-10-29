import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(exist_ok=True)

QUERIES = {
    "resume_bias": "Gender, Race, and Intersectional Bias in Resume Screening via Language Model Retrieval",
    "jobfair": "JobFair benchmarking gender hiring bias large language models",
    "goldin": "Orchestrating Impartiality Impact Blind Auditions Female Musicians",
    "name_blind": "name blind recruitment field experiment",
    "ats_audit": "automated resume screening gender bias audit",
}

def abstract_text(inv):
    if not inv:
        return ""
    pairs = []
    for word, positions in inv.items():
        for pos in positions:
            pairs.append((pos, word))
    return " ".join(w for _, w in sorted(pairs))

def fetch(query):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": query, "per-page": "5", "mailto": "research@example.org"}
    )
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.load(r)
    rows = []
    for w in data.get("results", []):
        rows.append(
            {
                "title": w.get("title"),
                "year": w.get("publication_year"),
                "doi": w.get("doi"),
                "cited_by": w.get("cited_by_count"),
                "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
                "abstract": abstract_text(w.get("abstract_inverted_index")),
            }
        )
    return rows

all_data = {}
for key, q in QUERIES.items():
    try:
        rows = fetch(q)
        all_data[key] = rows
        print(f"\n=== {key} ===")
        for r in rows[:3]:
            print(f"{r['year']} | {r['title']} | {r['doi']} | cited {r['cited_by']}")
            print(f"  {', '.join(r['authors'])}")
            print(f"  {r['abstract'][:500]}")
    except Exception as e:
        print(f"ERROR {key}: {e}")

(OUT / "openalex.json").write_text(json.dumps(all_data, indent=2), encoding="utf-8")
