# Phase 2: Vijñānabhairava — Starting State

## Benchmark
- 162 verses in benchmarks/vijnanabhairava_v1/
- Source hashes frozen
- 0 gold adjudications (will be earned)

## Coverage
- Zero lemmas: 14 (9%) — candidate gap, Heritage API unreliable for some
- ≤1 lemma: 43 (27%) — comparable to Spanda's starting state
- Pipeline runs on all verses (verified)

## Heritage retry
- Applied to ~10 low-coverage verses
- ~50% success rate (timeout on IAST tilde characters: `j~na`, `~sr` etc.)
- 5 verses improved from 0→6+ lemmas
- For remaining gaps: accept as honest limitation for zero-shot transfer

## Phase 2 systems

| System | Senses | Status |
|--------|--------|--------|
| C2 (full) | all senses | ready for generation |
| C0 (ablated) | general only | needs sense filter |
| B2 baseline | LLM only | needs prompt design |

## Next
- Generate C2 output for 80 dev verses (LLM rendering via DeepSeek)
- Generate C0 for ablation comparison
- Then: evaluate transfer classification
