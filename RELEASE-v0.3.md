# Sanskritree v0.3 Release

## Improvements from v0.2

| Metric | v0.2 | v0.3 | Change |
|--------|------|------|--------|
| Frame selection errors | 1 | 1 | same |
| Low-coverage verses | 8 | **6** | **-25%** |
| Passage-ID mismatch | yes | **none** | **fixed** |
| Mutation detection | — | **100%** | **new** |
| Publication gate | — | **28/30 PASS** | **new** |
| Candidate engines tracked | 7 | **9** | **+2** |

## What's New

- **D publication gate**: 28 PASS, 2 REJECT (coverage threshold). Adds structured PASS/REJECT with violation reporting.
- **Mutation test suite**: 5/5 (100%) detection rate. CI-enforceable.
- **Recall CI**: Passage-ID mismatch fixed. 30/30 benchmark IDs resolve. Loud failure on mismatch.
- **Seeded hypotheses**: `seeded` engine visible in recall report. 3 previously ALL_ENGINES_MISS verses now have candidates.
- **A2/B2 baselines**: Framework integrated — literal and retrieval baselines generated for all 30 passages.

## Remaining

6 low-coverage passages (target ≤2). Candidate generation gap persists for rare Tantric vocabulary. Next priority: expand candidate coverage via Heritage batch and ByT5 for the remaining 6 passages, then A2/B2 vs C comparison.
