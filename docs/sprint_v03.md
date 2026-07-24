# v0.3 Sprint Plan — Proving Translation Value

> Prove that Sanskritree beats or usefully constrains a strong LLM baseline on the frozen 30-passage set.

## Sprint goals

1. **Candidate-recall CI** — Recall@1/3/5 per passage, engine contribution, low-coverage flag
2. **Staged fallback with provenance** — Vidyut→Heritage→ByT5→corpus→manual, independent engine tracking
3. **Real LLM baselines** — A2 (plain), B2 (retrieval-assisted), C (Sanskritree), D (+audit)
4. **Publication gate** — D either PASS/PASS_WITH_WARNINGS/REJECT, not another generator
5. **Mutation tests** — synthetic failures with expected-detectable rejection rate target 100%

## v0.3 freeze requirements

- vb.79 re-evaluated and passing (frame error resolved)
- ≤2 low-coverage passages with ≤1 lemma
- Candidate Recall@k in CI pipeline
- A2 and B2 fully integrated
- All 30 passages blindly evaluated
- D rejects all formally detectable mutations
- C vs B2 quality report completed

## Decision tree after v0.3

| Result | Next step |
|--------|-----------|
| C beats B2 on accuracy/post-edit | Expand to 120 passages |
| B2 matches/beats C (candidates exist) | Improve ranking + semantic planning |
| Both fail (candidates absent) | Invest in parser/lexicon/corpus |
| C accurate but awkward | Improve rendering |
| D catches little | Redesign audited semantic contract |

## Distinction

> Do not set "Lean visibly changes output" as success. Set "Lean reliably blocks structurally unsupported publication" as the condition.
