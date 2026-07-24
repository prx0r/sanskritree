# v0.4 Sprint — Decisive B2-vs-C Experiment

## Goal
Prove whether structured inference (C) adds value beyond giving a strong LLM the same evidence (B2).

## Tasks

### 1. Replace approximations with real LLM baselines
Same fixed model for both A2 and B2. B2 strictly isolated from factor graph scores, selected hypotheses, semantic plan, Lean result, C output. Freeze model ID, prompt, temperature, evidence bundle, raw output, token use, cost.

### 2. Evaluate B2 vs C blindly
Randomize labels per passage. Record: accuracy preference, critical errors, major errors, unsupported additions, omissions, technical-term errors, post-edit time, post-edit distance. Also mark: correct candidate absent/present-but-misranked/semantic-plan-failure/renderer-failure/LLM-hallucination.

### 3. Defensible untranslated-track judgments
For 10 untranslated passages: human grammatical reconstruction, commentary where available, parallel passages, explicit unresolved/ambiguous labels. Do not treat fluency or agreement with C as correctness.

### 4. Report results by track
Known translation, Untranslated, Adversarial — separately. Adversarial track critical for negation, role assignment, technical vocabulary, unsupported additions.

### 5. Predefined decision rule
C succeeds if: fewer critical errors than B2, lower or equal post-edit time, lower unsupported-addition rate, no major regression on readability.

## Decision tree after v0.4

| Result | Next step |
|--------|-----------|
| C beats B2 clearly | Expand to 120 passages, begin commentary workbench |
| B2 equal but C more auditable | Position as verified translation infrastructure |
| B2 beats C (candidates present) | Improve ranking + semantic planning |
| Both fail (candidates absent) | Candidate-generation sprint |
| C accurate but slower to post-edit | Renderer + English realization sprint |

## Caution
A2 is useful context, but B2 is the real control. The scientific claim is not that Sanskritree beats dictionary glosses. It is that structured inference adds value beyond giving a strong LLM the same evidence.
