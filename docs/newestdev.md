# Newest Development Plan — Scientific Validation

> The architecture is real now. The next work should convert it from an impressive pipeline into a defensible experimental system.

## Progress assessment

| Component | Completion |
|-----------|-----------|
| Infrastructure | ~85% |
| Candidate generation | ~75% |
| Morphological graph | ~80% |
| Compound semantics | ~30% |
| Lexical semantics | ~10% |
| Frame semantics | ~15% |
| Formal verification | ~50% |
| Translation control | ~25% |
| Scientific evaluation | ~15% |
| Learned graph models | ~0% (appropriately) |

## Sprint plan

### Sprint 1 — Scientific foundation
1. Freeze Bhairavastava Gold v1.0 ✅
2. Exhaustively annotate 15-20 Spandakārikā dev verses
3. Add candidate-level decision and reason tables
4. Build layer-specific evaluation scripts
5. Establish held-out passages

**Exit condition:** every claimed improvement can be measured.

### Sprint 2 — Candidate recall
1. Add ByT5-Sanskrit inference
2. Compare Heritage/Vidyut/ByT5 recall
3. Resolve remaining rare Spanda vocabulary
4. Build concordances from 200K corpus
5. Report unique contribution + false-candidate burden per engine

### Sprint 3 — Compound semantics
1. Add nested compound-tree ontology
2. Import DepNeCTI labels/fixtures
3. Generate alternative trees
4. Annotate Tantric compound examples
5. Evaluate labeled-span + compound-relation accuracy

### Sprint 4 — FactorGraphV2
1. Explicit factor contribution scoring
2. Exact decoding on small graphs
3. Compare beam search with exact assignments
4. Provenance-family discounting
5. Full score explanations + ablations

### Sprint 5 — Translation renderer
1. JSON semantic plans
2. Graph-constrained node/path generation
3. Fluency-only second pass
4. Coverage/addition/omission auditor
5. Compare with unconstrained LLM generation

### Sprint 6 — Vijñānabhairava (after foundation validated)
### Sprint 7 — Learned ranking (after ≥100 adjudications)
### Sprint 8 — Sheaf research (after gold data exists)

## Priority ranking

**Must do now:**
1. Gold annotation and evaluation framework
2. Nested compound-tree representation
3. Candidate-generator comparison
4. Explicit factor scoring + exact-reference inference
5. Graph-constrained rendering

**Do after more real judgments:**
- Logistic/path reliability learning
- R-GCN/HGT
- Learned sheaf maps
- Large-scale semantic graph population

**Avoid:**
- Training SK→EN end to end
- Increasing corpus size for headline counts
- Treating compiled Lean proofs as translation accuracy
- Assigning one global belief to a lemma/sense
- Propagating across all 200K passages
- Training on simulated judgments
- Evaluating on passages used to tune factors

## Layer-specific metrics

| Layer | Metric |
|-------|--------|
| Segmentation | exact match, boundary F1 |
| Morphology | lemma accuracy, feature F1 |
| Candidate generation | gold recall@K |
| Compound tree | labeled span F1 |
| Factor ranking | MRR, top-1, top-3 |
| Calibration | Brier score, ECE |
| Frames | role F1 |
| Alignment | span precision/recall |
| Rendering | unsupported-addition rate, omission rate |
| Whole pipeline | fully correct passage rate |
| Human workflow | correction time per verse |
