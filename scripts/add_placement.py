from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
s = p.read_text()

# CSS for the "supplement" band and three deployment modes
anchor = '  .implementation { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; margin-top: clamp(28px, 4vw, 44px); border-top: 1px solid var(--line); }\n'
css = '''  .fit-band { display: grid; grid-template-columns: 1fr 1.15fr; gap: clamp(22px, 4vw, 44px); align-items: center; margin-top: clamp(26px, 4vw, 40px); padding: 16px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
  .fit-band h3 { margin-bottom: 6px; font-size: 1.15rem; }
  .fit-band p { margin: 0; color: var(--muted); font-size: 12px; line-height: 1.55; }
  .fit-flow { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; font-family: var(--mono); font-size: 9px; letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }
  .fit-flow span { border: 1px solid var(--line); padding: 5px 7px; background: var(--card); }
  .fit-flow .hot { border-color: var(--orange); color: var(--orange); }
  .fit-flow i { font-style: normal; color: var(--muted); }
  .fit-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; margin-top: 18px; border-top: 1px solid var(--line); }
  .fit-item { padding: 14px 20px 0 0; }
  .fit-item + .fit-item { padding-left: 20px; border-left: 1px solid var(--line); }
  .fit-item h3 { margin-bottom: 4px; font-size: 1rem; }
  .fit-item p { margin: 0; color: var(--muted); font-size: 11.5px; line-height: 1.5; }
  .implementation { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; margin-top: clamp(28px, 4vw, 44px); border-top: 1px solid var(--line); }
'''
if anchor not in s:
    raise SystemExit("implementation CSS anchor not found")
s = s.replace(anchor, css, 1)

# Mobile rules
s = s.replace(
    '    .corporate-grid { grid-template-columns: 1fr; }\n',
    '    .corporate-grid { grid-template-columns: 1fr; }\n    .fit-band { grid-template-columns: 1fr; }\n    .fit-grid { grid-template-columns: 1fr; }\n    .fit-item + .fit-item { border-left: 0; padding-left: 0; }\n    .fit-item:nth-child(n+2) { margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--line); }\n',
    1,
)

# Insert before implementation row
anchor2 = '    <div class="implementation">\n'
block = '''    <div class="fit-band">
      <div>
        <p class="eyebrow">Supplement, not replacement</p>
        <h3>It sits inside the model path and around the release gate.</h3>
        <p>The ATS still owns requisitions, parsing, workflow, candidate records and human review. The audit layer owns bias measurement, representation editing, release evidence and re-audit.</p>
      </div>
      <div class="fit-flow" aria-label="Where the audit layer fits">
        <span>Parse</span><i>→</i><span>Represent</span><i>→</i><span class="hot">Bias control</span><i>→</i><span>Rank</span><i>→</i><span>Shortlist</span><i>→</i><span>Human review</span>
      </div>
    </div>

    <div class="fit-grid">
      <article class="fit-item">
        <h3>White-box ATS</h3>
        <p>Insert LEACE after the encoder and before the scoring head. Recalibrate the head and gate the release.</p>
      </article>
      <article class="fit-item">
        <h3>Vendor ATS</h3>
        <p>No layer access: run the paired behavioural audit externally, make remediation a procurement condition, and re-audit on change.</p>
      </article>
      <article class="fit-item">
        <h3>ATS builder</h3>
        <p>Ship the audit as a module or SDK. The ATS keeps its workflow; the module adds the control layer.</p>
      </article>
    </div>

    <div class="implementation">
'''
if anchor2 not in s:
    raise SystemExit("implementation HTML anchor not found")
s = s.replace(anchor2, block, 1)

p.write_text(s)
print("supplement/placement block added; bytes:", len(s.encode("utf-8")))
