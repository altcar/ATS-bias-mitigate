# Responsible AI Hackathon — ATS Gender Bias

Live site: **https://altcar.github.io/ATS-bias-mitigate/**

## View it online

- **One-page site** — https://altcar.github.io/ATS-bias-mitigate/
- **Evidence book (rendered)** — https://altcar.github.io/ATS-bias-mitigate/ats-bias-audit/analysis.html
- **Deck** — https://altcar.github.io/ATS-bias-mitigate/presentation.pptx (downloads; browsers do not render PowerPoint)
- **PDF export** — https://altcar.github.io/ATS-bias-mitigate/ats-bias-audit.pdf
- **Written report (DOCX)** — https://altcar.github.io/ATS-bias-mitigate/A%20lightweight%20API%20that%20route%20AI%20requests.docx

The site is published by `.github/workflows/pages.yml` on every push to `main`, using GitHub Pages. Nothing is uploaded to a separate host and there are no extra secrets. The build stages the whole folder and serves `ats-bias-audit/index.html` as the site root.

## Files

- `presentation.pptx` — 19-slide deck.
- `ats-bias-audit/` — self-contained evidence book and environment.
  - `analysis.ipynb` — executed notebook: name extraction, 10 features, behavioural gaps, activation probes, heatmaps, LEACE, UK ATS analysis.
  - `analysis.html` — read-only rendered copy.
  - `.venv/` — project Python environment with all dependencies (git-ignored, never published).
  - `data/`, `scripts/`, `assets/`.

## Open first

1. `analysis.html` for a quick read.
2. `analysis.ipynb` for the runnable proof.
3. `presentation.pptx` for the pitch.

## Important

The 1,600 CVs are synthetic with a known injected gender-linked penalty. The notebook validates the audit method; it is not a production audit of any commercial ATS. The UK ATS section is a public-documentation review.
