# ATS Bias Audit — Reproducible Evidence Book

This folder is self-contained: data, scripts, assets, the presentation, a Python virtual environment (`.venv`), and the executed notebook `analysis.ipynb`.

## View it online

Live site: **https://altcar.github.io/ATS-bias-mitigate/**

- The one-page site (`index.html`) is served at the site root.
- Evidence book: `https://altcar.github.io/ATS-bias-mitigate/ats-bias-audit/analysis.html`
- Deck: `https://altcar.github.io/ATS-bias-mitigate/ats-bias-audit/presentation.pptx` (downloads; browsers do not render PowerPoint)

Published by `.github/workflows/pages.yml` at the repository root on every push to `main`, using GitHub Pages. Nothing is uploaded to a separate host and there are no extra secrets.

## What is here

- `analysis.ipynb` — the main deliverable. Executed end-to-end. It walks from raw CV text → name extraction → 10 structured features → MiniLM states → behavioural gap → activation probe → LEACE → heatmaps and UK ATS analysis.
- `analysis.html` — rendered read-only copy of the executed notebook, for quick viewing without Jupyter.
- `presentation.pptx` — 19-slide pitch deck.
- `index.html` — one-page website tying the analysis and presentation together, including a plain-English answers section and rendered equations.
- `data/` — 1,600 synthetic CVs (`rows.json`), MiniLM embeddings for three text conditions, results, feature ablations, activation geometry, and the UK ATS landscape table.
- `scripts/` — the original reproducible pipeline (`embed.py`, `analyze.py`, `ablate.py`, `make_conditions.py`, `make_charts.py`).
- `assets/` — charts and screenshots used in the deck.
- `requirements.txt` — exact versions used by the notebook.

## Run it

From this folder:

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name ats-audit --display-name "Python (ATS audit)"
.\.venv\Scripts\python.exe -m jupyter lab
```

Open `analysis.ipynb` and select the **Python (ATS audit)** kernel. Or open it in VS Code and select `.venv\Scripts\python.exe`.

## Important caveat

The 1,600 CVs are **synthetic**, with a known injected gender-linked penalty. The benchmark is a validation harness for the audit method, not an estimate of any commercial ATS. The notebook says this repeatedly and labels every result accordingly. The UK ATS section is a public-documentation review, not a vendor audit.

## Environment note

The packages installed earlier in the user-level Python site-packages were left in place. This project uses its own `.venv`, so nothing here depends on them; removing them could break other Python work on the machine.
