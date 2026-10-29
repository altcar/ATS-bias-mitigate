import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
s = p.read_text()

# 1. Light-first: remove the automatic dark block.
s2 = re.sub(
    r"  @media \(prefers-color-scheme: dark\) \{.*?\n  \}\n\n  :root\[data-theme=\"dark\"\] \{",
    "  :root[data-theme=\"dark\"] {",
    s,
    flags=re.S,
)
print("dark media removed:", s2 != s)
s = s2

# 2. Default to light; keep the manual toggle.
s = s.replace(
    '    const media = window.matchMedia("(prefers-color-scheme: dark)");\n\n    const current = () => root.dataset.theme || (media.matches ? "dark" : "light");',
    '    const current = () => root.dataset.theme || "light";',
)
s = s.replace('\n    if (media.addEventListener) media.addEventListener("change", paint);\n', '\n')

# 3. Tighten the product-page type and spacing.
s = s.replace('font-size: clamp(3.4rem, 8.2vw, 7.2rem);', 'font-size: clamp(3rem, 6.2vw, 5.8rem);')
s = s.replace('font-size: clamp(2.05rem, 3.7vw, 3.2rem);', 'font-size: clamp(1.9rem, 3.1vw, 2.75rem);')
s = s.replace('padding-block: clamp(58px, 8vw, 104px);', 'padding-block: clamp(44px, 6vw, 78px);')
s = s.replace('padding-block: clamp(48px, 7vw, 94px) clamp(38px, 5vw, 62px);', 'padding-block: clamp(38px, 5.5vw, 74px) clamp(30px, 4vw, 50px);')
s = s.replace('gap: clamp(32px, 6vw, 72px);', 'gap: clamp(28px, 5vw, 58px);')

# 4. Eager images so the first full-page paint is complete.
s = s.replace(' loading="lazy"', '')

# 5. Activation layout classes.
s = s.replace(
    '.activation-grid { display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr); gap: clamp(22px, 4vw, 44px); align-items: start; margin-top: clamp(24px, 4vw, 38px); }',
    '.activation-grid { display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr); gap: clamp(22px, 4vw, 44px); align-items: start; margin-top: clamp(24px, 4vw, 38px); }\n'
    '  .activation-top { grid-template-columns: minmax(0, 1.2fr) minmax(0, .8fr); margin-top: 0; }\n'
    '  .activation-bottom { grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); }'
)

# 6. Activation markup: two compact rows instead of two full-width blocks.
old = '''    <figure class="plate-figure">
      <img src="assets/activation_pca.png" alt="PCA plots of layer-6 MiniLM embeddings before and after LEACE. Female and male points separate before and overlap after." decoding="async">
      <figcaption><strong>Deck plate.</strong> Layer-6 MiniLM embeddings, held-out CVs. Before: probe 100%, relative bias 0.77. After: probe 57.8%, relative bias 0.05.</figcaption>
    </figure>

    <div class="activation-grid">
      <div>
        <table class="data-table">
          <thead>
            <tr><th>Metric</th><th>Before</th><th>After LEACE</th></tr>
          </thead>
          <tbody>
            <tr><td>Relative bias magnitude</td><td>0.773</td><td class="good">0.047</td></tr>
            <tr><td>Presence</td><td>0.238</td><td class="good">0.013</td></tr>
            <tr><td>Gender probe accuracy</td><td>100%</td><td class="good">57.8%</td></tr>
            <tr><td>Retention vs full baseline</td><td>—</td><td class="good">4.7%</td></tr>
            <tr><td>Ranking AUC</td><td>0.742</td><td>0.735</td></tr>
          </tbody>
        </table>
        <p class="aside-note"><strong>The residual matters.</strong> A 57.8% probe is closer to chance than 100%, but not chance. LEACE removes the linear mean; the gate is the backstop for what remains.</p>
      </div>
      <figure class="figure-card">
        <img src="assets/notebook/cell20_0.png" alt="Heatmap of linear gender probe accuracy by layer. Full and name-masked CVs are 100 percent from layer 1; proxy-scrubbed is 50 percent at every layer." decoding="async">
        <figcaption><strong>Notebook figure.</strong> Probe accuracy by layer and text condition; chance is 50%. Masking the name does not remove the signal.</figcaption>
      </figure>
    </div>'''
new = '''    <div class="activation-grid activation-top">
      <figure class="plate-figure">
        <img src="assets/activation_pca.png" alt="PCA plots of layer-6 MiniLM embeddings before and after LEACE. Female and male points separate before and overlap after." decoding="async">
        <figcaption><strong>Deck plate.</strong> Layer-6 MiniLM embeddings, held-out CVs. Before: probe 100%, relative bias 0.77. After: probe 57.8%, relative bias 0.05.</figcaption>
      </figure>
      <div>
        <table class="data-table">
          <thead>
            <tr><th>Metric</th><th>Before</th><th>After LEACE</th></tr>
          </thead>
          <tbody>
            <tr><td>Relative bias magnitude</td><td>0.773</td><td class="good">0.047</td></tr>
            <tr><td>Presence</td><td>0.238</td><td class="good">0.013</td></tr>
            <tr><td>Gender probe accuracy</td><td>100%</td><td class="good">57.8%</td></tr>
            <tr><td>Retention vs full baseline</td><td>—</td><td class="good">4.7%</td></tr>
            <tr><td>Ranking AUC</td><td>0.742</td><td>0.735</td></tr>
          </tbody>
        </table>
        <p class="aside-note"><strong>The residual matters.</strong> A 57.8% probe is closer to chance than 100%, but not chance. LEACE removes the linear mean; the gate is the backstop for what remains.</p>
      </div>
    </div>

    <div class="activation-grid activation-bottom">
      <figure class="figure-card">
        <img src="assets/notebook/cell20_0.png" alt="Heatmap of linear gender probe accuracy by layer. Full and name-masked CVs are 100 percent from layer 1; proxy-scrubbed is 50 percent at every layer." decoding="async">
        <figcaption><strong>Notebook figure.</strong> Probe accuracy by layer and text condition; chance is 50%. Masking the name does not remove the signal.</figcaption>
      </figure>
      <div class="prose">
        <h3>Distributed, not one neuron.</h3>
        <p>The layer-wise heatmap shows the difference spread across many coordinates. There is no single “gender neuron” to switch off. The direction is stable enough to estimate, which is why a projection can remove it.</p>
        <p>After masking, the probe remains at 100% from layer 1 onward. After LEACE it falls to 57.8%. That is a large reduction, and a useful reminder that linear erasure is not total erasure.</p>
      </div>
    </div>'''
if old not in s:
    print("ACTIVATION BLOCK NOT FOUND")
else:
    s = s.replace(old, new)
    print("activation replaced")

# 7. Built-with strip.
old = '''  </section>

  <section id="problem" class="section wrap">'''
new = '''  </section>

  <div class="wrap built-with" aria-label="Built with">
    <span>Built with</span>
    <span>MiniLM-L6</span>
    <span>LEACE</span>
    <span>scikit-learn</span>
    <span>Jupyter</span>
  </div>

  <section id="problem" class="section wrap">'''
if old in s:
    s = s.replace(old, new, 1)
    print("built-with added")

# 8. CTA band before footer.
old = '<footer class="wrap footer">'
new = '''<section class="cta-band">
  <div class="wrap cta-inner">
    <div>
      <p class="eyebrow">The takeaway</p>
      <h2>Audit the model, not the applicant.</h2>
    </div>
    <div class="cta-actions">
      <a class="button cta-primary" href="#proof">Read the evidence</a>
      <a class="button cta-ghost" href="#top">Back to top</a>
    </div>
  </div>
</section>

<footer class="wrap footer">'''
if old in s:
    s = s.replace(old, new, 1)
    print("cta added")

# 9. CSS for the new strips and CTA.
s = s.replace(
    '  .section { padding-block: clamp(44px, 6vw, 78px); border-top: 1px solid var(--line); scroll-margin-top: 74px; }',
    '  .built-with { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding-block: 12px 14px; border-bottom: 1px solid var(--line); font-family: var(--mono); font-size: 8px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }\n'
    '  .built-with span { border: 1px solid var(--line); padding: 5px 7px; }\n'
    '  .built-with span:first-child { border: 0; padding-left: 0; color: var(--muted); }\n'
    '  .section { padding-block: clamp(44px, 6vw, 78px); border-top: 1px solid var(--line); scroll-margin-top: 74px; }'
)
s = s.replace(
    '  .footer { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; padding-block: 24px 34px; border-top: 1px solid var(--line); }',
    '  .cta-band { background: var(--ink); color: var(--paper); }\n'
    '  .cta-inner { display: flex; align-items: flex-end; justify-content: space-between; gap: 32px; padding-block: clamp(34px, 5vw, 54px); }\n'
    '  .cta-band .eyebrow { color: var(--paper); opacity: .65; }\n'
    '  .cta-band h2 { color: var(--paper); max-width: 18ch; }\n'
    '  .cta-actions { display: flex; flex-wrap: wrap; gap: 9px; flex: 0 0 auto; }\n'
    '  .cta-primary { background: var(--paper); color: var(--ink); border-color: var(--paper); }\n'
    '  .cta-primary:hover { background: var(--orange); border-color: var(--orange); color: var(--on-accent); }\n'
    '  .cta-ghost { background: transparent; color: var(--paper); border-color: var(--paper); }\n'
    '  .cta-ghost:hover { color: var(--orange); border-color: var(--orange); }\n'
    '  .footer { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; padding-block: 24px 34px; border-top: 1px solid var(--line); }'
)
s = s.replace(
    '    .uk-insight, .sources { grid-template-columns: 1fr; }',
    '    .uk-insight, .sources { grid-template-columns: 1fr; }\n'
    '    .cta-inner { flex-direction: column; align-items: flex-start; }'
)
s = s.replace(
    '    .two-col, .feature-layout, .result-grid, .result-grid.reverse, .activation-grid, .solution-grid { grid-template-columns: 1fr; }',
    '    .two-col, .feature-layout, .result-grid, .result-grid.reverse, .activation-grid, .activation-top, .activation-bottom, .solution-grid { grid-template-columns: 1fr; }'
)

p.write_text(s)
print("wrote", p)
