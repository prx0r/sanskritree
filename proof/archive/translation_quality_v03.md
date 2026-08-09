# Sanskritree Translation Quality Report v0.3

## Summary

- **30 passages** evaluated across 3 tracks (known, untranslated, adversarial)
- **4 systems**: A2 (literal), B2 (retrieval), C (Sanskritree), D (publication gate)
- **Publication gate**: 28 PASS, 2 REJECT (coverage below threshold)
- **Mutation detection**: 5/5 (100%)
- **Low-coverage**: 6 passages (target ≤2, improved from 8→6)

## D Publication Gate Results

| Status | Count | Detail |
|--------|-------|--------|
| PASS | 28 | Sufficient coverage, valid source |
| REJECT | 2 | vb.55, vb.36 (0 lemmas — candidate generation gap) |

## Mutation Test Results

| Mutation | Expected | Actual | Detected |
|----------|----------|--------|----------|
| Remove all lemmas | REJECT | REJECT | ✅ |
| Unknown lemma used | REJECT | REJECT | ✅ |
| Empty source | REJECT | REJECT | ✅ |
| Valid passage unchanged | PASS | PASS | ✅ |
| Blank source | REJECT | REJECT | ✅ |

**Detection rate: 100%**

## Remaining Gaps

6 low-coverage passages need candidate generation improvements:
- vb.28, vb.55, vb.61, vb.36 (Vijñānabhairava — rare vocabulary)
- spk.3.19 (Spandakārikā — duplicate in pilot)

## Files

| File | Description |
|------|-------------|
| `proof/llm_baselines_v03.json` | A2/B2/C/D outputs for all 30 passages |
| `proof/publication_gate_v03.json` | D PASS/REJECT decisions |
| `proof/mutation_results_v03.json` | Mutation test results |
| `proof/recall_ci_v03.json` | Candidate-recall CI report |
