from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
s = p.read_text()

# Navigation entry
s = s.replace(
    '      <a href="#proof">Proof</a>\n',
    '      <a href="#proof">Proof</a>\n      <a href="#answers">Answers</a>\n',
    1,
)

# CSS for the answers section
css_anchor = '  .files code { color: var(--ink); }\n'
css_new = '''  .files code { color: var(--ink); }

  .answers-grid { display: grid; grid-template-columns: minmax(0, .72fr) minmax(0, 1.28fr); gap: clamp(28px, 5vw, 64px); align-items: start; }
  .answers-lead { position: sticky; top: 88px; }
  .answer-quote { margin: 0 0 18px; padding-left: 18px; border-left: 3px solid var(--orange); font-family: var(--display); font-size: clamp(1.25rem, 2.1vw, 1.75rem); line-height: 1.22; letter-spacing: -.03em; color: var(--ink); }
  .answer-list { border-top: 1px solid var(--line); }
  .answer { padding: 18px 0 19px; border-bottom: 1px solid var(--line); }
  .answer h3 { margin-bottom: 8px; font-size: 1.05rem; }
  .answer p, .answer li { color: var(--muted); font-size: 13px; line-height: 1.62; }
  .answer p:last-child { margin-bottom: 0; }
  .answer ul { margin: 8px 0 0; padding-left: 18px; }
  .answer li { margin-bottom: 4px; }
  .answer strong { color: var(--ink); font-weight: 600; }
  .answer-callout { margin-top: 12px; padding: 10px 12px; border: 1px solid var(--line); background: var(--card); color: var(--ink); font-size: 12px; line-height: 1.55; }
  .answer-callout strong { color: var(--orange); }
  .mini-formula { margin-top: 10px; padding: 10px 12px; border: 1px solid var(--line); background: var(--card); overflow-x: auto; color: var(--ink); font-size: 12px; }
  .mini-formula mjx-container { margin: 0 !important; }
  .answer-matrix { display: grid; grid-template-columns: 1fr 1fr 1.2fr; margin-top: 12px; border-top: 1px solid var(--line); }
  .answer-matrix div { padding: 8px 8px 8px 0; border-bottom: 1px solid var(--line); color: var(--muted); font-size: 11.5px; line-height: 1.45; }
  .answer-matrix div:nth-child(3n) { padding-right: 0; }
  .positioning { margin-top: clamp(28px, 4vw, 42px); padding: 20px 22px; border-left: 3px solid var(--orange); background: var(--card); }
  .positioning p:last-child { margin: 0; font-family: var(--display); font-size: clamp(1.2rem, 2.2vw, 1.7rem); line-height: 1.25; letter-spacing: -.025em; color: var(--ink); }
  mjx-container { color: var(--ink); }
  mjx-container svg { max-width: 100%; }
'''
if css_anchor not in s:
    raise SystemExit("CSS anchor not found")
s = s.replace(css_anchor, css_new, 1)

# Mobile rules
s = s.replace(
    '    .uk-insight, .sources { grid-template-columns: 1fr; }\n',
    '    .uk-insight, .sources { grid-template-columns: 1fr; }\n    .answers-grid { grid-template-columns: 1fr; }\n    .answers-lead { position: static; }\n',
    1,
)
s = s.replace(
    '    .footer { flex-direction: column; gap: 10px; }\n',
    '    .answer-matrix { grid-template-columns: 1fr; }\n    .answer-matrix div:nth-child(3n) { padding-right: 8px; }\n    .footer { flex-direction: column; gap: 10px; }\n',
    1,
)

# Answers section inserted after Proof and before closing main
proof_tail = '''    <p class="files">Evidence book: <code>ats-bias-audit/analysis.ipynb</code> · rendered: <code>analysis.html</code> · deck: <code>presentation.pptx</code></p>
  </section>
</main>'''
if proof_tail not in s:
    raise SystemExit("Proof tail not found")

answers = '''    <p class="files">Evidence book: <code>ats-bias-audit/analysis.ipynb</code> · rendered: <code>analysis.html</code> · deck: <code>presentation.pptx</code></p>
  </section>

  <section id="answers" class="section wrap">
    <div class="section-head">
      <div>
        <p class="eyebrow">09 / Plain-English answers</p>
        <h2>The questions people actually ask.</h2>
      </div>
      <p class="section-intro">Short answers you can say out loud. The evidence book has the code and the full detail.</p>
    </div>

    <div class="answers-grid">
      <aside class="answers-lead">
        <p class="eyebrow">The 30-second answer</p>
        <p class="answer-quote">Most ATS audits only look at the output. We audit both the output and the model’s internal representation.</p>
        <p class="micro">Matched CV pairs measure the score and shortlist gap. A linear probe tests whether gender is still decodable inside the model. LEACE removes the linear gender direction. The gate only passes if both behaviour and representation improve without damaging ranking quality.</p>
      </aside>

      <div class="answer-list">
        <article class="answer">
          <h3>What did you actually build?</h3>
          <p>A six-step pipeline: generate matched CV pairs, parse 10 controlled attributes, encode the text with MiniLM, train a simple linear scoring head, audit the behavioural gap, then audit and edit the activation space.</p>
          <p>The point is the counterfactual. Each pair is the same candidate on merit. Only the identity cues change. That lets us attribute the score difference to the cues, not to qualifications.</p>
        </article>

        <article class="answer">
          <h3>What are the 10 features?</h3>
          <p><strong>Four identity-linked:</strong> name, pronouns, affiliation, career-gap reason. <strong>Six merit:</strong> skills match, years experience, education, seniority, certifications, projects.</p>
          <div class="answer-callout"><strong>Be precise:</strong> the ranker’s input is the CV text through MiniLM embeddings. The 10 features are the audit’s controlled variables, parsed so we can verify pairs are matched and ablate one cue at a time. They are not 10 hand-coded tabular inputs.</div>
          <p>Name is the largest single channel: 3.75 pp, or 42% of the 8.8 pp gap. Pronouns add 2.72 pp, or 31%. All four identity cues together remove the full 8.8 pp.</p>
        </article>

        <article class="answer">
          <h3>What does the score gap do?</h3>
          <p>It answers: if I show the model the same CV twice, changing only the identity cues, does the score move?</p>
          <div class="mini-formula">\\[ d_{ij} = s(\\mathrm{CV}^{f}_{i}, \\mathrm{job}_{j}) - s(\\mathrm{CV}^{m}_{i}, \\mathrm{job}_{j}) \\]</div>
          <p>Average that paired difference over the benchmark. In our model, female scores average 14.5% and male scores 23.3%, so the score gap is <strong>−8.8 pp</strong>. Negative means the female version scores lower.</p>
          <p>It is a behavioural measurement, not proof of illegal discrimination in a commercial ATS. It is a controlled bias audit. The shortlist gap matters too: <strong>−12.5 pp</strong> at the top-20% cutoff, and <strong>−13.7 pp</strong> after name masking. Thresholds amplify small score shifts.</p>
        </article>

        <article class="answer">
          <h3>What does the probe do?</h3>
          <p>A probe asks a different question: can I recover gender from the model’s hidden representation?</p>
          <p>It is a linear classifier trained on layer-6 activations to predict gender. It is a diagnostic, not a deployed model. If the output scores are equal but the probe is 100%, gender information is still stored in the representation.</p>
          <p>In our benchmark: <strong>50% at layer 0</strong>, <strong>100% from layer 1 onward</strong>, <strong>still 100% after name masking</strong>, and <strong>50% after proxy-scrubbing all explicit cues</strong>. After LEACE it falls to <strong>57.8%</strong>.</p>
        </article>

        <article class="answer">
          <h3>How does LEACE actually work?</h3>
          <p>LEACE finds the direction in the hidden state that predicts gender and projects it out, while changing the rest of the representation as little as possible.</p>
          <div class="mini-formula">\\[ r(h) = h - W^{\\top}(WW^{\\top})^{-1}Wh \\]</div>
          <p><strong>W</strong> defines the concept subspace. <strong>Wh</strong> is the part of the state inside that subspace. The projection removes that part.</p>
          <p>It is not “delete the gender neuron.” The direction is distributed across many dimensions. LEACE finds a subspace from data, solves the projection in closed form rather than with gradient descent, and is designed so linear probes cannot recover the concept.</p>
          <p>We standardise the layer-6 states first, fit LEACE on the training split only, apply it to held-out states, then recalibrate the scoring head. The results: score gap <strong>7.7 → 0.18 pp</strong>, probe <strong>100% → 57.8%</strong>, relative bias <strong>0.773 → 0.047</strong>, retention <strong>4.7%</strong>, AUC <strong>0.742 → 0.735</strong>.</p>
          <p>It does not remove every possible gender signal. The residual 57.8% probe is why the deployment gate exists.</p>
        </article>

        <article class="answer">
          <h3>Why score gap for behaviour, but probe and LEACE for activation?</h3>
          <div class="answer-matrix">
            <div><strong>Question</strong></div><div><strong>Tool</strong></div><div><strong>Role</strong></div>
            <div>Do identical candidates get different decisions?</div><div>Score gap</div><div>Behavioural measurement</div>
            <div>Is gender still readable inside the model?</div><div>Probe</div><div>Activation-space measurement</div>
            <div>Can we remove the linear gender direction?</div><div>LEACE</div><div>Activation-space intervention</div>
            <div>Did the fix work downstream?</div><div>Score gap again</div><div>Behavioural verification</div>
          </div>
          <p>They are not alternatives. They are measurement, diagnosis, intervention, verification. A model can look fair at the output and still fail the probe; a model can pass the probe and still fail the score gap because of thresholds or other features.</p>
        </article>

        <article class="answer">
          <h3>Are you the first to use LEACE for this?</h3>
          <p><strong>Do not claim first.</strong> LEACE is from 2023 and the paper itself evaluates gender bias in BERT embeddings. Concept erasure has an earlier literature, including INLP in 2020.</p>
          <p>The defensible claim is: <em>“Our contribution is applying LEACE inside a dual behavioural and activation-space audit for ATS ranking, with a gate that checks both. We are not claiming to invent concept erasure.”</em></p>
        </article>

        <article class="answer">
          <h3>Why isn’t this used in production ATS?</h3>
          <ul>
            <li>Most ATS are black boxes. They return a score, not layer activations.</li>
            <li>Many are not end-to-end neural: parsers, knockout questions, keyword match, gradient-boosted models, or LLM APIs.</li>
            <li>Procurement and legal review focus on outcomes and adverse-impact reports, not representation geometry.</li>
            <li>Erasing a concept can remove useful signal; you must prove ranking quality survives.</li>
            <li>Over-debiasing is a real risk. JobFair found reverse bias in 7/10 LLMs.</li>
            <li>There is no standard certification path for “probe and erase,” so vendors carry the validation burden.</li>
          </ul>
          <p>The accurate line is: <em>“It is a known research method, not a common production ATS feature, because most vendors cannot access the representation and most buyers audit outcomes rather than internals.”</em></p>
        </article>
      </div>
    </div>

    <div class="positioning">
      <p class="eyebrow">If you only get one sentence</p>
      <p>“I built a dual audit for ATS gender bias: paired CVs measure the behavioural score gap, a linear probe measures whether gender is still decodable in the model’s activations, and LEACE removes the linear gender direction. The gate only passes if both the output and the representation improve without damaging ranking quality.”</p>
    </div>
  </section>
</main>'''

s = s.replace(proof_tail, answers, 1)

# Replace the plain-ASCII solution formula with MathJax
s = s.replace(
    '<div class="formula">r(h) = h − Wᵀ(WWᵀ)⁻¹Wh</div>',
    '<div class="formula">\\[ r(h) = h - W^{\\top}(WW^{\\top})^{-1}Wh \\]</div>',
    1,
)

# MathJax: SVG output avoids font loading; script is on the allowed CDN.
math_scripts = '''
<script>
  window.MathJax = {
    tex: {
      inlineMath: [["\\\\(", "\\\\)"]],
      displayMath: [["\\\\[", "\\\\]"]]
    },
    svg: { fontCache: "global" }
  };
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.js" async></script>
'''
if '</script>\n' in s:
    # append after the existing theme script, before the final body close (skeleton supplies body)
    s = s.rstrip() + "\n" + math_scripts
else:
    s = s.rstrip() + "\n" + math_scripts

p.write_text(s)
print("answers + MathJax added; bytes:", len(s.encode("utf-8")))
