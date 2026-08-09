# Sanskritree Translation Benchmark — Formal Results v0.2

## Test Configuration

**Date:** 2026-07-24
**Kernel:** v0.2 (Research Kernel with Fix #1 ByT5 candidates + Fix #2 action detection)
**Passages:** 30 across 3 tracks (10 known-translation, 10 untranslated, 10 adversarial)
**Systems:** A (literal gloss), B (retrieval-assisted), C (Sanskritree no Lean), D (full Sanskritree)

## Results

| Metric | All 30 | Known | Untranslated | Adversarial |
|--------|--------|-------|-------------|-------------|
| Avg lemmas/verse | 4.3 | 4.5 | 4.6 | 3.9 |
| Frame assigned | 30/30 | 10/10 | 10/10 | 10/10 |
| ≥3 lemmas | 18/30 | 7/10 | 6/10 | 5/10 |
| 0 lemmas | 2/30 | 1/10 | 0/10 | 1/10 |

## Improvements from v0.1

| Metric | v0.1 | v0.2 | Change |
|--------|------|------|--------|
| Frame selection errors | 6 | 1 | **-83%** |
| Compound errors | 10 | 0 | removed |
| Verses with ByT5 hyps | 0 | 6 | +6 |
| Evaluations completed | 5 | 28 | +460% |

## Residual error profile

| Type | Count | Severity | Origin | Status |
|------|-------|----------|--------|--------|
| MORPHOLOGY (candidate gap) | 8 | MAJOR | candidate_generation | 6/9 seeded, 3 unresolved |
| FRAME_SELECTION | 1 | MAJOR | keyword coverage | vb.79 needs keyword expansion |

## Key findings

1. Frame selection now works correctly (83% error reduction)
2. Candidate generation is the primary bottleneck (8 verses with ≤1 lemma)
3. Systems C and D are identical (Lean gate doesn't constrain factor graph output yet)
4. The evaluation loop is operational — measure → fix → re-measure
