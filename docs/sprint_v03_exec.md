# v0.3 Execution Plan

## Immediate steps

### 1. Fix recall CI passage-ID mismatch
Use canonical_passage_id throughout. Assert benchmark IDs match DB IDs. Regenerate `proof/recall_ci_v03.json` with seeded hypotheses visible.

### 2. Integrate A2/B2 baselines
```
A2 — plain Sanskrit-to-English translation
B2 — Sanskrit + parser candidates + glosses + local context
```
Store: model, provider, prompt, temperature, evidence, raw response, timestamp, cost/tokens. Freeze outputs once.

### 3. Define D publication contract
D evaluates C and returns PASS / PASS_WITH_WARNINGS / REJECT.
Rejection rules: missing node, unlicensed span, rejected hypothesis used, invalid selector, hash mismatch, undeclared commentary import.
Machine-readable failure report.

### 4. Mutation tests
Create from known-valid benchmark objects: remove node, drop negation, insert unsupported clause, reference rejected hypothesis, change source hash, delete alignment, mark commentary as literal.
CI metric: detectable_mutations_rejected / total_detectable_mutations → 100%.

### 5. Re-run complete benchmark
A2, B2, C, D publication result. Blind evaluation of all 30.
Core comparison: B2 vs C (accuracy, errors, additions, post-edit, uncertainty, D rejection rate).

## v0.3 freeze criteria
- passage-ID mismatch fixed
- seeded hypotheses visible in recall CI
- ≤2 genuinely low-coverage passages
- A2/B2 outputs frozen
- all 30 passages evaluated
- publication gate operational
- 100% detectable mutation rejection
- quality report generated

## Output files
```
proof/llm_baselines_v03.json
proof/publication_gate_v03.json
proof/mutation_results_v03.json
proof/translation_quality_v03.md
RELEASE-v0.3.md
```

## Decisive question
> Does C outperform evidence-assisted LLM B2, and does D prevent structurally unsupported translations from being published?
