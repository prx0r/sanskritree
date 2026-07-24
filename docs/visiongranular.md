# Vision Granular — Evaluation-First Development

> The immediate question is not "how do we build Mathlib for Sanskrit?" It is: **Does the current pipeline produce translations that are more accurate, more auditable, and more useful than simpler baselines—and what structured human data would improve it fastest?**

## Where we are

We have a functioning experimental translation system but have not yet demonstrated translation quality. Coverage, parser throughput, graph convergence and Lean compilation are infrastructure metrics — not evidence that the English translation is correct.

## The correct next programme

Build three connected assets:
1. **Sanskritree Translation Benchmark** — frozen passages with multi-system comparison
2. **Human Post-Editing and Adjudication Pipeline** — error-linked correction workflow
3. **Iterative Training and Evaluation Loop** — learn from observed failures

## Benchmark structure (~120 passages, three tracks)

| Track | Passages | Purpose |
|-------|----------|---------|
| A: Known translation | 60 | Compare against scholarly translations |
| B: Blind untranslated | 30 | Genuinely new translation challenge |
| C: Adversarial | 30 | Negation, agent/patient ambiguity, ellipsis, long compounds, technical terms |

## Systems to compare

| System | Description |
|--------|-------------|
| A: Unassisted LLM | Sanskrit passage → translate accurately |
| B: Retrieval-assisted LLM | + dictionary, parser candidates, context |
| C: Sanskritree w/o Lean | Factor graph → semantic plan → constrained render |
| D: Full Sanskritree | + publication constraints + Lean certificate |
| E: Human literal | Deliberately close, non-literary translation (30-50 passages) |

## A/B test questions

- A vs B: Does evidence retrieval reduce hallucination?
- B vs C: Does structured selection improve interpretation?
- C vs D: Does formal gating reduce unsupported content?
- D vs human: How far from usable scholarly translation?

## Evaluation layers

1. **Pairwise preference** — accuracy, readability, scholarly usefulness
2. **Span-level error annotation** — MINOR/MAJOR/CRITICAL with error type
3. **Sanskrit-specific error taxonomy** — SOURCE_TEXT, SEGMENTATION, MORPHOLOGY, COMPOUND_STRUCTURE, SYNTACTIC_ROLE, NEGATION, LEXICAL_SENSE, FRAME_SELECTION, etc.
4. **Post-editing effort** — original → corrected, editing time, edit count, reason codes

## Key metric: SCHOLARLY_USABILITY_RATE

A passage passes if: no critical errors, ≤ agreed major-error threshold, all major content represented, no unlabeled commentary insertion, uncertainties disclosed, post-edit less work than translating from scratch.

## What to train (in order)

1. **Candidate ranker** — logistic → pairwise → gradient-boosted (from component adjudications)
2. **Missing-candidate predictor** — is correct analysis absent?
3. **Error-risk estimator** — will translation likely contain critical error?
4. **Translation preference model** — preferred realization from pairwise judgments
5. **Minimal post-editor** — diagnosis-constrained correction (much later)

## Active learning priority score

P(x) = 0.20U + 0.15D + 0.15M + 0.15T + 0.10L + 0.10C + 0.10R + 0.05F

Where: U=uncertainty, D=system disagreement, M=missing-candidate, T=error risk, L=lexical novelty, C=compound novelty, R=recurrence, F=frame novelty

## Revised near-term roadmap

```
T0  Freeze current system baseline                     ✅ v0.1
T1  Build 30-passage translation pilot                 📝 Next
T2  Blind A/B evaluation                               📝
T3  Post-edit and map errors to graph nodes            📝
T4  Redesign M10.3 sampling from observed failures     📝
T5  Complete 150 high-value adjudications              📝
T6  Train simple rankers and risk models               📝
T7  Re-run frozen pilot                                 📝
T8  Expand benchmark to 120 passages                   📝
T9  Reach 500+ targeted decisions                      📝
T10 Publish Translation Benchmark v1                   📝
```

## Decision gates

1. **Is Sanskritree better than an LLM?** — fewer critical errors, fewer additions, higher win rate, lower post-edit time
2. **Is the factor graph useful?** — compare D with B; if no gain, identify why
3. **Does Lean add practical value?** — fewer unsupported additions, omissions, unlabeled commentary imports
4. **Does post-editing save time?** — correction must be faster than translating from scratch
