from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
s = p.read_text()

# Nav
s = s.replace(
    '      <a href="#uk-ats">UK ATS</a>\n      <a href="#proof">Proof</a>\n',
    '      <a href="#uk-ats">UK ATS</a>\n      <a href="#corporate">Corporate</a>\n      <a href="#proof">Proof</a>\n',
    1,
)

# CSS
css_anchor = '  .footer { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; padding-block: 24px 34px; border-top: 1px solid var(--line); }\n'
css_new = '''  .corporate-grid { display: grid; grid-template-columns: 1fr 1fr; gap: clamp(24px, 4vw, 48px); align-items: start; }
  .corp-label { margin-bottom: 12px; font-family: var(--mono); font-size: 9px; letter-spacing: .09em; text-transform: uppercase; color: var(--muted); font-weight: 400; }
  .benefit-list, .deliverable-list { border-top: 1px solid var(--line); }
  .benefit, .deliverable { display: grid; grid-template-columns: 26px minmax(0, 1fr); gap: 10px; padding: 13px 0 14px; border-bottom: 1px solid var(--line); }
  .benefit .n, .deliverable .n { padding-top: 2px; font-family: var(--mono); font-size: 8px; color: var(--orange); }
  .deliverable .n { color: var(--blue); }
  .benefit h3, .deliverable h3 { margin: 0 0 3px; font-size: 1rem; }
  .benefit p, .deliverable p { margin: 0; color: var(--muted); font-size: 12px; line-height: 1.55; }
  .implementation { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; margin-top: clamp(28px, 4vw, 44px); border-top: 1px solid var(--line); }
  .impl-step { padding: 15px 18px 0 0; }
  .impl-step + .impl-step { padding-left: 18px; border-left: 1px solid var(--line); }
  .impl-step .n { display: block; margin-bottom: 16px; font-family: var(--mono); font-size: 8px; letter-spacing: .08em; color: var(--orange); }
  .impl-step h3 { margin-bottom: 5px; font-size: 1rem; }
  .impl-step p { margin: 0; color: var(--muted); font-size: 11.5px; line-height: 1.5; }
  .corporate-callout { display: grid; grid-template-columns: 1.05fr .95fr; gap: clamp(22px, 4vw, 44px); margin-top: clamp(28px, 4vw, 44px); padding: 20px 22px; background: var(--ink); color: var(--paper); }
  .corporate-callout .eyebrow { color: var(--paper); opacity: .65; }
  .corporate-callout h3 { margin-bottom: 6px; color: var(--paper); font-size: 1.15rem; }
  .corporate-callout p { margin: 0; color: var(--paper); opacity: .78; font-size: 12px; line-height: 1.55; }
  .corporate-callout .needs { font-family: var(--mono); font-size: 9px; line-height: 1.65; letter-spacing: .02em; }
  .corp-caveat { margin-top: 12px; color: var(--muted); font-family: var(--mono); font-size: 8px; line-height: 1.55; }
  .footer { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; padding-block: 24px 34px; border-top: 1px solid var(--line); }
'''
if css_anchor not in s:
    raise SystemExit("CSS anchor not found")
s = s.replace(css_anchor, css_new, 1)

# Mobile
s = s.replace(
    '    .uk-insight, .sources { grid-template-columns: 1fr; }\n',
    '    .uk-insight, .sources { grid-template-columns: 1fr; }\n    .corporate-grid { grid-template-columns: 1fr; }\n    .implementation { grid-template-columns: 1fr 1fr; }\n    .impl-step:nth-child(3) { border-left: 0; padding-left: 0; }\n    .impl-step:nth-child(n+3) { margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--line); }\n    .corporate-callout { grid-template-columns: 1fr; }\n',
    1,
)
s = s.replace(
    '    .answer-matrix { grid-template-columns: 1fr; }\n',
    '    .implementation { grid-template-columns: 1fr; }\n    .impl-step + .impl-step { border-left: 0; padding-left: 0; }\n    .impl-step:nth-child(n+2) { margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--line); }\n    .answer-matrix { grid-template-columns: 1fr; }\n',
    1,
)

# Insert corporate section after UK ATS and before Proof
proof_start = '  <section id="proof" class="section wrap">'
corporate = '''  <section id="corporate" class="section wrap">
    <div class="section-head">
      <div>
        <p class="eyebrow">08 / Corporate deployment</p>
        <h2>What the company gets — and how it lands.</h2>
      </div>
      <p class="section-intro">A bias-controlled structure is not an ethics report. It is a repeatable assurance product: measure the gap, edit the representation, gate the release, monitor the model.</p>
    </div>

    <div class="corporate-grid">
      <div>
        <h3 class="corp-label">Why a company does this</h3>
        <div class="benefit-list">
          <article class="benefit">
            <span class="n">01</span>
            <div><h3>Lower legal and reputational risk</h3><p>Supports Equality Act and ICO expectations, and EU AI Act high-risk employment reviews. It creates a defensible evidence trail instead of a policy statement.</p></div>
          </article>
          <article class="benefit">
            <span class="n">02</span>
            <div><h3>Better talent decisions</h3><p>Less proxy-driven shortlisting. Name, pronouns and affiliation stop doing work they should not do, and human reviewers get clearer evidence.</p></div>
          </article>
          <article class="benefit">
            <span class="n">03</span>
            <div><h3>Procurement advantage</h3><p>A scorecard buyers can request: behaviour + activation + gate. Evidence, not a vendor’s one-line “AI is fair” claim.</p></div>
          </article>
          <article class="benefit">
            <span class="n">04</span>
            <div><h3>Reusable assurance IP</h3><p>For Synoptix, a billable white-box assurance line for clients in aerospace, defence, energy, healthcare and transport. For the client, a repeatable control.</p></div>
          </article>
        </div>
      </div>

      <div>
        <h3 class="corp-label">What the solution is</h3>
        <div class="deliverable-list">
          <article class="deliverable">
            <span class="n">01</span>
            <div><h3>Paired-candidate audit</h3><p>Score and shortlist gap on matched CVs, feature attribution, and a layer-wise probe heatmap.</p></div>
          </article>
          <article class="deliverable">
            <span class="n">02</span>
            <div><h3>Representation edit</h3><p>LEACE at the encoder layer, a recalibrated scoring head, and a quality check so ranking AUC survives.</p></div>
          </article>
          <article class="deliverable">
            <span class="n">03</span>
            <div><h3>Deployment gate</h3><p>Four checks: behavioural gap, gender probe, ranking AUC and bias retention. All must pass before release.</p></div>
          </article>
          <article class="deliverable">
            <span class="n">04</span>
            <div><h3>Monitoring</h3><p>Quarterly re-audit and a re-run on every model, prompt or ranking change. The control does not go stale.</p></div>
          </article>
        </div>
      </div>
    </div>

    <div class="implementation">
      <article class="impl-step">
        <span class="n">01 / Scope</span>
        <h3>Pick the surface</h3>
        <p>One or two job families, the real cutoff, the protected attributes, DPIA and legal review.</p>
      </article>
      <article class="impl-step">
        <span class="n">02 / Baseline</span>
        <h3>Measure the gap</h3>
        <p>Run the paired audit and the probe. Quantify score, shortlist and activation bias.</p>
      </article>
      <article class="impl-step">
        <span class="n">03 / Remediate</span>
        <h3>Edit and recalibrate</h3>
        <p>Integrate LEACE at the encoder, retrain the head, and verify AUC and ranking quality.</p>
      </article>
      <article class="impl-step">
        <span class="n">04 / Gate &amp; monitor</span>
        <h3>Ship or block</h3>
        <p>Deploy only if all four checks pass. Re-audit quarterly and on every model change.</p>
      </article>
    </div>

    <div class="corporate-callout">
      <div>
        <p class="eyebrow">For Synoptix</p>
        <h3>Productise the audit as a 2–4 week sprint, then a quarterly assurance retainer.</h3>
        <p>Use it on your own hiring first to prove the method, then offer it to clients in regulated sectors as a white-box assurance service. The differentiator is access to the representation, not another questionnaire.</p>
      </div>
      <div>
        <p class="eyebrow">What you need from the company</p>
        <p class="needs">Score API or shortlist logs<br>Model access or vendor cooperation<br>Job families and the real cutoff<br>Legal review and candidate notice<br>An owner for quarterly re-audit</p>
      </div>
    </div>
    <p class="corp-caveat">Prototype benchmark. The claim is not “zero bias”; it is measured, reduced and gated. Production work requires client data, legal review and validation.</p>
  </section>

  <section id="proof" class="section wrap">'''
if proof_start not in s:
    raise SystemExit("Proof section not found")
s = s.replace(proof_start, corporate, 1)

# Renumber later sections
s = s.replace('<p class="eyebrow">08 / Proof</p>', '<p class="eyebrow">09 / Proof</p>', 1)
s = s.replace('<p class="eyebrow">09 / Plain-English answers</p>', '<p class="eyebrow">10 / Plain-English answers</p>', 1)

p.write_text(s)
print("corporate section added; bytes:", len(s.encode("utf-8")))
