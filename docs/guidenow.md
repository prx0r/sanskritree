# Guide Now — Checkpoint 1 Execution Plan

> Validate the plan, but rename the milestones honestly: Spandakārikā is the **complete-text reconstruction checkpoint**. Vijñānabhairava is the **transfer checkpoint**. The first untranslated work is the **actual first-translation checkpoint**.

## Corrected phase structure

```
PHASE 0 — FOUNDATION ✅
  v0.1-v0.4 complete. 120-passage benchmark. B2 vs C: C wins 24/30.
  
PHASE 1 — COMPLETE-TEXT RECONSTRUCTION (NEXT)
  Spandakārikā (53 verses). Blind translate → compare → diagnose → repair → verify.
  
PHASE 2 — CROSS-TEXT TRANSFER
  Vijñānabhairava zero-shot. Measure which gains transfer.
  
PHASE 3 — FIRST UNTRANSLATED WORK
  Stable text without English reference. Independent review.
  
PHASE 4 — SCHOLARLY INFRASTRUCTURE
  Commentary workbench, STAM, claims, intertext — only after translation value proven.
```

## What Checkpoint 1 proves

✅ Consecutive whole-text translation
✅ Term consistency across verses
✅ Systematic error diagnosis
✅ Improvement through targeted repairs
✅ Resistance to holdout regression
✅ Traceable disagreement with scholars
✅ Formal evidence and publication constraints

## What it does not prove

❌ Successful translation without references
❌ Generalization across genres
❌ Manuscript-level textual criticism
❌ Human-scholar equivalence

## Split design

```
Development:       30 verses  (inspect references after blind generation)
Internal holdout:  13 verses  (sealed until iteration frozen)
Final challenge:   10 verses  (sealed until v1.0 candidate)
```

Select final challenge verses deliberately: negation, long compounds, technical terms, ambiguous roles, ellipsis, cross-verse dependencies, doctrinally loaded statements.

## Reference ingestion protocol

1. Freeze Sanskrit source first — edition, verse boundaries, hash
2. Store each reference independently — Dyczkowski, Singh, etc.
3. Prevent leakage — blind generation env must not retrieve reference English
4. Record that commercial LLMs may have seen published translations in pretraining

## Comparison taxonomy

### Disagreement outcome
```
SANSKRITREE_ERROR | REFERENCE_ERROR | REFERENCE_INTERPRETIVE | TEXTUAL_VARIANT
BOTH_DEFENSIBLE | COMMENTARY_DEPENDENT | UNRESOLVED
```

### Causal origin
```
SOURCE_NORMALIZATION | SEGMENTATION | MORPHOLOGY | COMPOUND_ANALYSIS
SYNTAX | COREFERENCE | NEGATION | LEXICAL_SENSE | TECHNICAL_TERM
FRAME_SELECTION | FRAME_ROLE | SEMANTIC_PLAN | RENDERER
DISCOURSE_CONTEXT | UNSUPPORTED_ADDITION | OMISSION
```

### Severity
```
MINOR | MAJOR | CRITICAL
```

## Checkpoint 1 benchmarks

### Candidate generation
- Gold lemma Recall@5: ≥95%
- Correct compound candidate: ≥90%
- Verses with catastrophic gap: ≤2/53

### Translation adequacy (final challenge)
- Critical errors: 0
- Major grammatical errors: ≤2 total
- Unsupported doctrinal additions: 0
- Negation preservation: 100%
- Required semantic-node realization: ≥98%

### Reference disagreement
- Unresolved major disagreements: ≤10%
- Defensible reading rate: ≥90%

### Post-edit effort
- Median post-edit time ≥25% lower than B2

### Consistency
- Technical-term consistency: ≥95%
- Named-entity consistency: 100%
- Cross-verse terminology drift: ≤5%

### Lean publication gate
- Mutation rejection: 100%
- Source hash integrity: 100%
- Rejected-candidate leakage: 0
- Unlabelled commentary imports: 0

## 5-week schedule

| Week | Deliverables | Gate |
|------|-------------|------|
| **1** | Source manifest, reference manifest, 53/53 alignment, variant table, 30/13/10 split, recall report | No unresolved alignment; ≥90% candidate recall; leakage tests pass |
| **2** | Blind pass 1: all 53 verses with full evidence manifests. Classify 30 dev disagreements. | 53/53 outputs; all manifests complete; top error causes ranked |
| **3** | Fix top 3 error causes. Add regression tests. No holdout references inspected. | Every repair linked to observed errors; new tests added; all versions frozen |
| **4** | Pass 2. Compare dev + 13-verse holdout. Measure critical/major errors, recall, defensible rate, post-edit, term consistency, audit failures. | Dev improves; holdout doesn't regress; no new critical errors; audit 100% |
| **5** | Unseal final 10 references. Run Sanskritree C, B2, external baselines. Blind review. | 53/53 complete; 0 critical on final challenge; ≥90% defensible; ≥25% lower post-edit than B2; 100% mutation rejection |

## v1.0 engineering release gate

```
53/53 complete translations
0 critical errors on final challenge
≥90% defensible reading rate
≤10% unresolved major disagreements
≥95% technical-term consistency
≥25% lower median post-edit time than B2
100% formally detectable mutation rejection
all departures from references documented
```

## What to add to CI

- `translation_regression` — 53 Spanda verses, semantic plan hashes, term consistency
- `grammar_probes` — minimal pairs for case-role, active/passive, negation, compounds, etc.
- `candidate_recall` — Recall@1/3/5, engine contribution, all-engine-miss count
- `audit_mutations` — extend existing mutations with term inconsistency, commentary leakage, textual-variant mismatch

## Key principle

> The most important adjustment is to avoid optimizing toward agreement with famous translators. The release should reward grammatical correctness, semantic completeness, doctrinal restraint, explicit uncertainty, whole-text consistency, post-edit efficiency, and formal traceability — not imitation.
