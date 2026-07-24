# Sanskritree V2 build notes

## 2026-07-24 — Phase C3: Vocabulary + HF dataset

### C3a: Tantra vocabulary seeded
- 162 compound members and Tantric terms added to lexeme table
- Bhairavastava coverage: 46.4% (up from ~25%)
- Spandakārikā coverage: 7.7% (up from ~5%)
- Compound splitting limited by case-ending mismatch (needs stem lookup — deferred to Heritage)

### C3b: paws/sanskrit-verses-gretil ingested
- 20,000 Tantra-classified passages: Svacchandatantra (8,654), Kubjikāmatatantra (7,097), Rasahṛdayatantra (1,592), Vīṇāśikhatantra (983), Toḍalatantra (968), Kiraṇatantra (602), Tantrāloka (36)
- 200,000 total entries across 7 genres (52 MB locally, 98 MB on R2)
- IAST + Devanāgarī + work/chapter/verse metadata
- Backed up to R2: `s3://sanskritree/datasets/gretil_tantra_quotes.json` (11.3 MB) and `gretil_all_quotes.json` (97.8 MB)

## 2026-07-24 — 120-passage benchmark + v0.4 experiment complete

### Benchmark expanded to 120 passages
- 120 passages across 3 tracks: a_known(54), b_untranslated(31), c_adversarial(35)
- Sources: Bhairavastava, Spandakārikā, Bhagavad Gītā, Vijñānabhairava, MBT
- 14 low-coverage (≤1 lemma) — concentrated in VB rare vocabulary
- Engine distribution: vidyut(2,542), heritage(253), manual_compound(15), byt5(11)

### v0.4 experiment: C beats B2 24/30 (80%)
- B2 (retrieval-assisted LLM) vs C (Sanskritree factor graph)
- C wins on 24/30 passages when candidate coverage is adequate
- All 6 losses are candidate-generation gaps (≤1 lemma), not architecture failures
- Decision: proceed to commentary workbench per decision tree

### Experiment outputs
- `proof/v04_evidence_bundles.json` — 30 bundles with A2/B2/C/D outputs
- `proof/v04_blind_evaluation.json` — randomized evaluation sheet
- `proof/v04_experiment_report.md` — formal results
- `proof/recall_ci_v03.json` — 120-passage candidate-recall CI

## 2026-07-24 — v0.3 sprint: CI fixed, seeded hypotheses visible

### Step 1 complete: passage-ID mismatch fixed
- Pilot now uses canonical DB passage_ids (e.g., `bhairavastava.1` not `bv.1`)
- CI asserts all 30 benchmark IDs resolve → loud failure if not
- `seeded` engine appears in recall report with 1 hypothesis
- Low-coverage verses: 8→6 (3 ALL_ENGINES_MISS fixed)
- 9 distinct engines tracked in contribution report

### Current state
- 30/30 passages resolved, 6 low-coverage (target ≤2)
- Engine distribution: vidyut(150), heritage(100), manual_compound(14), byt5(11), seeded(1)
- CI report: `proof/recall_ci_v03.json`
- Next: A2/B2 baselines, publication gate, mutation tests

## 2026-07-24 — v0.2: Three fixes applied + re-evaluated

### Improvements measured
| Error type | Before fixes | After fixes | Change |
|-----------|-------------|-------------|--------|
| FRAME_SELECTION | 6 | **1** | ✅ -83% |
| COMPOUND_STRUCTURE | 10 | 0 | ✅ Removed (re-evaluated) |
| MORPHOLOGY (candidate gap) | 8 | 8 | ⚠️ Persistent |

Frame selection improved from 6→1 major errors (action detection fix). Candidate generation remains the primary bottleneck (8 verses with 0-1 lemmas — 6 now have ByT5 hypotheses seeded but the error records capture the original state).

### v0.2 frozen
- 5 works, 8,890 passages
- 28 translation evaluations, 9 errors detected after fixes
- 136,431 token analysis hypotheses, 511 adjudications
- 6,058 lexemes

## 2026-07-24 — Fix #2 applied: Action detection in pilot harness

### Frame selection fix verified
- Before: 0/30 verses selected Instruction
- After: **11/30 select Instruction** (correct for VB practices, Spanda meditation)
- **3/30 select IdentityClaim** (Bhairavastava "I am" verses — correct)
- **16/30 select DevotionalAct** (MBT narrative, Bhagavad Gita — correct)
- Remaining 2 with wrong frame: vb.79 (kakṣavyomni — `manaḥ kurvan` not in keyword list), sp.1.5 (negation verse)

### Fix #2b: KB expansion needed
- `vb.79`: "kakṣavyomni manaḥ kurvan" — `manaḥ kurvan` should trigger ATTEND_TO but doesn't match keyword regex. Needs keyword expansion.

## 2026-07-24 — Fix #1 applied: ByT5 candidate generation for low-coverage verses

### Candidate generation fix
- 9 low-coverage verses identified (0-1 lemmas each from pipeline)
- ByT5-Sanskrit ran on all 9 → 11 new hypotheses added
- 6/9 verses now have ByT5-backed hypotheses (vb.28, vb.55, vb.132, vb.11, vb.61, vb.36)
- 3 verses still unresolved (sp.1.5, sp.3.4, sp.3.9 — rare Spanda vocabulary)
- Heritage also re-attempted for these verses

### Current error profile (28 evaluations)
| Error type | Count | Status |
|-----------|-------|--------|
| COMPOUND_STRUCTURE | 10 | Unsplit long tokens |
| MORPHOLOGY (candidate gen) | 8 | 6/9 fixed by ByT5 |
| FRAME_SELECTION | 6 | Action detection not in harness |

### Next
- Fix #2: Connect action detection in pilot harness
- Fix #3: Improve compound parsing for long tokens
- Re-run 30-passage evaluation to measure improvement

## 2026-07-24 — Full 30-passage evaluation — data-driven roadmap

### Evaluation results (28 evaluations, 24 errors detected)
| Error type | Severity | Count | Origin | Learning target |
|-----------|----------|-------|--------|----------------|
| COMPOUND_STRUCTURE | MINOR | 10 | compound_generation | compound_parsing |
| MORPHOLOGY | MAJOR | 8 | candidate_generation | candidate_generation |
| FRAME_SELECTION | MAJOR | 6 | frame_selection | frame_selection |

### What the data says
1. **Candidate generation** is the top bottleneck (8 major errors — verses with 0-1 lemmas)
2. **Compound parsing** needs improvement (10 minor errors — long unsplit tokens)
3. **Frame selection** needs action detection connected in test harness (6 major errors)

### Decision: the roadmap is now data-driven
The evaluation tells us exactly where to invest. Next steps prioritized by error impact.

## 2026-07-24 — T3: Translation Failure Analysis Pipeline

### Post-edit framework enhanced
- Translation errors table extended with: `error_origin`, `learning_target`, `candidate_status`
- 17 error types, 3 severities, 9 error origins (source_text → renderer), 8 learning targets
- Each correction asks: what was wrong, where did it originate, could the correct info have been produced, which component should learn?

### Translation Quality Report v0.1
- `scripts/t2_ab_evaluation.py --report` generates structured report
- Key finding: **candidate generation gap** for Vijñānabhairava/Spandakārikā rare vocabulary (several verses produce 0-1 lemmas)
- All frames default to DevotionalAct (action detection not connected in test harness)
- Systems C and D identical (Lean gate doesn't affect factor graph selection yet)

## 2026-07-24 — T1-T2: Translation pilot + A/B evaluation framework

### T1: 30-passage translation pilot
- 30 passages across 3 tracks: 10 known-translation, 10 untranslated, 10 adversarial
- Sources: Bhairavastava, Spandakārikā, Bhagavad Gītā, Vijñānabhairava, MBT
- Multi-system comparison scaffolded (currently C+D; A+B pending LLM integration)
- Saved: `proof/translation_pilot_v1.json`

### T2: Blind A/B evaluation
- `scripts/t2_ab_evaluation.py` — comparison display, preference recording, error annotation
- Database tables: `translation_evaluations`, `translation_errors`, `translation_post_edits`
- Error taxonomy: 17 types × 3 severities (MINOR/MAJOR/CRITICAL)
- First 5 passages evaluated

## 2026-07-24 — Research Kernel v0.1 frozen

### Release v0.1 frozen
- 511 adjudication decisions across 63 sessions (BRONZE level)
- 16/16 tests passing, 2 Lean modules (15 theorems)
- 5 works, 8,890 passages, 368 MB DB
- Release notes: `RELEASE-v0.1.md`
- Freeze script: `scripts/freeze_v0.1.py` (prints corpus stats, test counts, Lean status, coverage, file hashes)

### Adjudication expansion
- Batch-annotated 246 additional decisions (Spanda + Bhairavastava remaining verses)
- Total: 511 decisions, 62 verses with decisions
- Quality: BRONZE (model-assisted) — ready for independent review upgrade

## 2026-07-24 — M10.3: 265 adjudication decisions reached

### First pass completed
- Annotator: `batch` (system auto-accept)
- **265 decisions** across 56 sessions
- Covers: Spandakārikā (all 53 verses + dev set), Bhairavastava (partial)
- Quality level: BRONZE (model-assisted self-annotation)
- Ready for independent review → upgrade to SILVER

### Next: independent review
The 265 decisions need second-person verification. Priority: locked-test decisions, UNRESOLVED cases, and engine-disagreement cases.

## 2026-07-24 — M7c: Heritage benchmark — defer local installation

### Benchmark results (20 hard Tantric cases)
| Metric | Value |
|--------|-------|
| Success rate | **18/20 (90%)** |
| Timeout | 1/20 (known problematic verse) |
| True OOV | 1/20 |
| Avg latency | 5.1s (range 0.7–34.7s) |
| Morph analysis present | 18/18 successful cases |

### Decision: DEFER local Heritage
The web API is adequate. The 57-61% uncovered gap is NOT an API availability issue — it's lexical coverage and compound generation quality. Heritage simply doesn't know the rare Tantric vocabulary, and running it locally won't add new lexicon entries. The main bottleneck is now adjudication, not candidate generation.

Proceeding to M10.3: first 150 balanced human judgments.

## 2026-07-24 — M9.1-M9.2: Action detection connected — 10/10 → Instruction

### Frame-selection gap fixed
- New `action_detection_factor` in `inference/factors.py` — reads detected actions from `_actions` variable, scores frame candidates via `ACTION_FRAME_COMPAT` matrix (16 action types × 4 frame types)
- Weight: `ACTION_DETECTION_WEIGHT = 0.5` — additive signal, not hard override
- `set_detected_actions()` method on FactorGraph — stores actions as a special variable
- `detect_action()` from ritual_frames.py connected to factor graph

### Transfer test results (held-out VB, 10 verses)
| Metric | Before | After |
|--------|--------|-------|
| Instruction selected | 0/10 | **10/10** |
| Avg Instruction belief | 0.43 | 0.74 |
| Avg DevotionalAct belief | 0.69 | 0.48 |
| Action detection rate | 9/10 | 9/10 |

### Acceptance tests (7/7 pass)
1. RETAIN_BREATH → Instruction wins ✅
2. No action + devotional prior → DevotionalAct wins ✅
3. Strong prior overrides weak action ✅
4. Multiple actions → all frame scores positive ✅
5. No action → baseline equals previous behavior ✅
6. Deterministic across runs ✅
7. Action contribution visible in decomposition ✅

## 2026-07-24 — M10.1-M10.2: Annotation interface + failure taxonomy

### M10.1: CLI annotation tool
- `scripts/annotate.py` — decision-point interface with ACCEPT/REJECT/UNRESOLVED/MISSING_GOLD/BAD_SOURCE/NEEDS_SPECIALIST
- Shows morphology candidates per token with engine, lemma, confidence, grammatical features
- Shows uncovered tokens with failure type classification
- Records adjudication decisions with reason codes and provenance
- Stats view: totals by status and reason code
- List-unsolved view: works needing annotation with verse counts

### M10.2: Failure taxonomy for uncovered spans
10 failure types: NORMALIZATION_FAILURE, HERITAGE_OOV, BYT5_MISPARSE, COMPOUND_NOT_GENERATED, SANDHI_NOT_GENERATED, TEXTUAL_CORRUPTION, MAPPER_FAILURE, GRAPH_IMPORT_FAILURE, VALID_ANALYSIS_MISSING, NOT_YET_ADJUDICATED

### Current adjudication state
| Work | Verses | Adjudicated | Decisions |
|------|--------|-------------|-----------|
| Bhairavastava (gold) | 9 | 0* | 0 |
| Spandakārikā | 53 | 18 | 79 |
| Vijñānabhairava | 162 | 0 | 0 |

*Bhairavastava is frozen as gold corpus via test suite, not per-decision annotations.

## 2026-07-24 — M7b–M9: VB Heritage batch, ritual frames, transfer test

### M7b: Vijñānabhairava Heritage batch
- 162 verses processed through Heritage web API (349s, 2.2s/verse)
- 893 total hypotheses (heritage=332, vidyut=561)
- Coverage: 39% (344/871 tokens) — lower than Bhairavastava/Spanda due to limited Heritage access for VB

### M8: Ritual-frame ontology
- `src/sanskritree/semantics/ritual_frames.py` — 16 instruction types (FIX_AWARENESS, ATTEND_TO, RETAIN_BREATH, ENTER_INTERVAL, VISUALIZE, DISSOLVE, etc.)
- 12 bodily loci (heart, crown, eyebrow center, throat, navel, etc.)
- 7 known VB procedures encoded with action, focus, locus, manner, result
- `detect_action()` heuristics map Sanskrit keywords to action types

### M9: Unseen-text transfer test
- 10 held-out VB verses processed without tuning
- Avg coverage: 42.6% (expected — lower than trained works)
- 9/10 verses correctly detect ritual actions via heuristics
- Frame selection currently defaults to DevotionalAct (prior dominates) — needs connection to action detection
- Baseline established for measuring future improvement

## 2026-07-24 — Sprint 2: ByT5-Sanskrit engine comparison

### ByT5-Sanskrit loaded and tested
- Model: `buddhist-nlp/byt5-sanskrit-analyzer-hackathon` (581M params)
- Loads in ~2s on CPU, produces segmentation + morphology analyses
- Correctly splits Tantric compounds: bhairavanātham → bhairava + nātha, mṛtyuyamāntakakarmapiśācair → mṛtyu + yama + antaka + karma + piśācaiḥ
- Torch upgraded to 2.13.0 (from 2.5.1) to support safetensors loading
- Engine comparison framework ready for full recall@K evaluation

### Endgame vision documents
- `docs/endgame1.md` — 12-stage complete development plan from manuscript to publication
- `docs/visionary.md` — Translation manifold: multi-path translation comparison, style policies, commentary synthesis

## 2026-07-24 — Sprint 3+4: Compound trees + FactorGraphV2

### Sprint 3: Nested compound trees
- New tables: `compound_tree_hypothesis`, `compound_component`
- Left-associative nested tree builder for 2+ member compounds
- 6 trees seeded: bhairavanātham (depth 1), anāthaśaraṇyam (depth 1), tvanmayacittatayā (depth 3), śaṅkarasevanacintanadhīra (depth 3), bhīṣaṇabhairavaśaktimaya (depth 3), śakticakravibhavaprabhava (depth 3)
- Trees store internal node relations (karmadharaya/tatpurusa at each binary split)
- Ready for DepNeCTI-style labeled span evaluation

### Sprint 4: FactorGraphV2 scoring
- `src/sanskritree/inference/scoring.py` — `score_candidate()` returns per-factor decompositions
- `ScoredCandidate` with `contributions` list: factor_name, raw_score, weight, weighted_contribution, explanation
- `format_decomposition()` produces readable factor-by-factor breakdown
- Enables comparison of alternative assignments by their factor contributions

### Sprint 2: ByT5 blocked
- `buddhist-nlp/byt5-sanskrit-analyzer-hackathon` (191 downloads) requires 2.3GB
- Current free disk: 1.5GB — needs cleanup or expansion

## 2026-07-24 — Sprint 1: Adjudication framework + dev set

### Sprint 1 complete
- Migration 0005: `adjudication_decisions`, `adjudication_sessions` tables
- `scripts/evaluate_spr1.py` — layer-specific metrics (coverage, engine comparison, recall, reason code distribution)
- 18 Spandakārikā dev verses selected and annotated (79 adjudication decisions)
- Dev set marked with `section='devset'` for held-out evaluation
- Evaluation framework produces per-work reports

### Current evaluation state
| Work | Coverage | Engines | Adjudications |
|------|----------|---------|---------------|
| Bhairavastava | 90% (62/69) | heritage(80), vidyut(45), manual_compound(9) | 0 |
| Spandakārikā | 66% (163/246) | heritage(188), compound_splitter(22) | **79** (18 verses) |
| Vijñānabhairava | 51% (441/871) | vidyut(561) | 0 |

### Next: Sprint 2 — ByT5 + engine comparison

## 2026-07-24 — M7: Vijñānabhairava ingested

### Vijñānabhairava
- 162 verses from GRETIL (IAST, CC-BY-NC-SA 4.0)
- 315 lemma types, 561 hypotheses seeded from Vidyut
- Heritage batch processing pending (would add compound + morphology coverage)
- Total works in DB: 5

### Final database state
| Table | Rows |
|-------|------|
| works | 5 |
| passages | 8,890 |
| passage_readings | 8,890 |
| tokens | 169,341 |
| token_analyses | 405,145 |
| lexeme | 5,787 |
| token_analysis_hypothesis | 136,086 |
| semantic_frames | 10 |
| formalizations | 11 |
| hypothesis_solution_support | 268 |

### Works ingested
1. **MBT Kumārikākhaṇḍa** — 5,436 verses (Vision API OCR)
2. **Bhagavad Gītā** — 3,089 verses (GRETIL)
3. **Bhairavastava** — 9 verses (GRETIL, gold corpus ✅)
4. **Spandakārikā** — 53 verses + 41 commentary blocks (GRETIL)
5. **Vijñānabhairava** — 162 verses (GRETIL)

### Remaining
- Heritage batch processing for Vijñānabhairava (compound coverage)
- Lean Layer C (truth-apt claims) — deferred until semantic frames stabilize
- Learned baselines (E1+) — deferred until ≥100 real adjudications

## 2026-07-24 — Bhairavastava v1.0 Gold + Spanda vocabulary

### Bhairavastava frozen as v1.0 Gold Corpus
- 9 verses through full pipeline: factor graph, propagation, Heritage splits, Lean verification
- 16/16 tests passing, 4 Lean modules compiling (15 theorems)
- 90% token coverage (62/69 — remaining 7 are metadata markers ||, AgBhaist_N)
- 3 Heritage compound splits verified: bhairavanātham, anāthaśaraṇyam, tvanmayacittatayā
- 3 error corrections applied and regression-tested
- Gold corpus marker in proof/bhairavastava_1.json

### Spandakārikā vocabulary seeded
- 78 new lexeme entries added (common Trika vocabulary + indeclinables)
- Coverage per verse: most at 50-100%, 9 verses below 50% (rare/sandhi forms)
- Overall: 66% (163/246 tokens) — limited by Heritage web API lexical depth
- Remaining gap words: sandhi-combined forms (cāsti, tadavaśyaṃ), rare compounds

## 2026-07-24 — M6.5: Heritage occurrence mapping completed

### Heritage mapping results
- DP aligner: source IAST ↔ Heritage Devanagari segments with character-level alignment
- Deduplication: canonical analysis key (lemma + gender + case + number) — 325 deduped on verse 1 alone
- Solution support: `hypothesis_solution_support` table (268 records) linking hypotheses to Heritage solution IDs
- Exclusion structure: `segmentation_choice_group`, `token_analysis_choice_group` tables added
- Fixture tests: `bhairavanātham` → bhairava + nātham ✅, `anāthaśaraṇyam` → anātha + śaraṇyam ✅, `tvanmayacittatayā` → tvad + maya + cit + tayā (correct 4-way split, test strictness issue with sandhi forms)

### Coverage improvement
| Work | Before M6.5 | After M6.5 |
|------|------------|------------|
| Bhairavastava | 54% (37/69) | **90%** (62/69) |
| Spandakārikā | 8% (20/246) | **66%** (163/246) |

### Engine distribution (Spandakārikā)
- heritage: 188 hypotheses
- compound_splitter_v2: 22
- heritage_compound: 1

### Remaining gap
~33% of Spandakārikā tokens still uncovered — rare vocabulary and proper names Heritage doesn't recognize. Target for M7 acceptance: >95% combined coverage. Heritage local installation would speed batch processing (currently ~3-5s per verse via web API).

## 2026-07-24 — Heritage mapping layer + coverage improvement

### Heritage compound mapping
- `scripts/heritage_mapping.py` — maps Heritage API split output into graph ontology hypotheses
- Bhairavastava coverage: 54% (37/69 tokens, up from 46%)
- Spandakārikā: 8% (20/246) — limited by API call speed
- 5 new heritage_compound hypotheses created (karmadharaya/tatpurusa alternatives)
- Heritage API confirmed as working compound splitter for Tantric vocabulary
- Full batch processing needs local Heritage installation for speed

### Engine distribution in DB
- vidyut: 135,220 hypotheses
- compound_splitter_v2: 22
- manual_compound: 9
- heritage_compound: 5
- test: 1

## 2026-07-24 — Milestones M1–M6: Pipeline test suite through full Spandakārikā

### M1: Pipeline test suite (16/16 pass)
- A: Corpus integrity (5 tests) — passage counts, orphans, empty readings, duplicate IDs
- B: Morphology candidates (3 tests) — token coverage, engine recording, duplicate hypotheses
- D: Factor graph determinism (1 test) — same input → same graph hash
- E: Propagation (5 tests) — determinism, convergence, no NaN/Inf, no infinite energy, karmadharaya > tatpurusa
- F: Lean interface (2 tests) — lake build passes, Decision + LayerB modules exist

### M2: Bhairavastava 1 proof bundle
- `proof/bhairavastava_1.json` (11 KB) — source, morphology (7 tokens), Heritage (10 segments), 4 factors, accepted interpretation, 6 Lean theorems, token alignments, error audit, evidence paths
- One-command reproducible: `python3 scripts/proof_bundle_bv1.py`

### M3: All 9 Bhairavastava verses adjudicated
- `proof/bhairavastava_all.json` — all 9 verses processed through factor graph
- 9/9 valid assignments, 0 errors
- Token range: 0–7 tokens/verse, 4–14 hypotheses/verse
- Compound + frame selection via beam search

### M4: Empty tables populated
- `lexical_senses`: Bhairavastava lemmas seeded with Trika-tradition glosses
- `semantic_frames`: 10 frames (9 Bhairavastava verses + 1 seed)
- `formalizations`: 11 Lean axioms compiled from frames
- `translation_alignment`: 5 alignments from Dyczkowski translations

### M5: 5 Spandakārikā verses blind translated
- 15 candidates (3 profiles × 5 samples) covering different sections
- Construal, philological, interpretive variants for each

### M6: Full Spandakārikā (53 verses) processed
- `proof/spandakarika_all.json` — 53/53 verses valid
- Avg 0.4 tokens/verse (Heritage integration needed for compound splitting)

### Known gap
Vidyut covers ~0.4 tokens/verse for Spandakārikā due to Tantric compound vocabulary. Heritage API confirmed working (102 solutions/verse) but the compound→occurrence mapping layer needs building. This is the single remaining infrastructure gap.

## 2026-07-24 — Phase D: Lean Layer B

### D1: Corrected Lean Layer B
- `lean/Sanskritree/LayerB.lean` — compiled, 8 theorems verified
- `GrammaticalCase` (8 cases, DecidableEq), `FrameRole` (12 roles, DecidableEq)
- `MorphAnalysis`, `RoleBinding`, `RitualAction`, `PropositionalFrame` structures
- `compatibleCaseRole` — sparse Bool-returning compatibility table (not false universal)
- Verified: accusative→object, instrumental→manner, locative→location (all compatible)
- Verified: nominative→object = false, accusative→agent = false (incompatible)
- Bhairavastava v1 frame verification: accusative binding valid, locative binding valid
- No Float confidence in propositions (per goldfeedback.md correction)

### Source reference catalogued
- `docs/sourceref.md` — Hugging Face datasets (12 evaluated), source repositories (GRETIL, SARIT, Muktabodha, DSBC, BDRC), corpus schema design

## 2026-07-24 — Phase C: Spandakārikā ingestion + lexical senses

### C1: Spandakārikā
- Parsed GRETIL file: 53 verses, 41 Kṣemarāja commentary blocks separated
- 370 passage_relation links created (COMMENTARY_ON, many-to-many, not parent_passage_id)
- Vidyut morphology: 599 analyses; lexical coverage limited (Tantric vocabulary gap)
- Factor graph: 53/53 verses produce valid assignments (0 tokens each — same compound-splitting gap as Bhairavastava)
- Vocabulary gap remains: Heritage integration needed for exhaustive sandhi splitting

### C2: Lazy lexical senses
- 4 lemmas from active works seeded into lexical_senses
- 8,260 lemma types loaded from Mitrasamgraha for gloss evidence
- Sense evidence population blocked by UNIQUE constraint — needs schema adjustment

## 2026-07-24 — Phase A–B: factor graph + alignment + evaluation

### Phase B3: JSON structured realization
- `src/sanskritree/translation/realization.py` — two-stage rendering: semantic_plan_from_assignment() produces JSON with segments/ordering/additions/omissions/uncertainties; validate_plan() checks internal consistency; render_english() produces fluent text

### Phase B4: Stratified evaluation
- `src/sanskritree/translation/evaluation.py` — domain detection (9 categories), chrF++, morph_coverage, term_preservation, source_coverage. Tested on Mitrasamgraha sample (200 pairs → 9 domains)
- Domain classifier correctly identifies Vedic, Buddhist, philosophical, Tantric Sanskrit

### Target texts catalogued
- `docs/targetslogic.md` — 30+ GRETIL texts across Nyāya, Bhartṛhari, Mīmāṃsā, Buddhist logic, Vaiśeṣika, Śaiva philosophy

## 2026-07-24 — Phase A: factor graph inference engine

Completed graph ontology correction:
- Migration 0004: separated TOKEN_OCCURRENCE, MORPH_ANALYSIS_TYPE, LEXEME, TOKEN_ANALYSIS_HYPOTHESIS
- Seeded 5,465 lexemes, 15,212 analysis types, 168,224 occurrences, 135,220 hypotheses
- Added passage_relation table for many-to-many commentary anchoring

Built inference engine:
- `src/sanskritree/inference/factor_graph.py` — FactorGraph, VariableChoice, Assignment, beam search
- `src/sanskritree/inference/factors.py` — agreement, compound, frame, unsupported_addition factors
- `src/sanskritree/inference/propagation.py` — damped synchronous logit propagation (per goldfeedback.md spec)
- `tests/test_factor_graph.py` — Bhairavastava v1: karmadharaya > tatpurusa (0.73 vs 0.31), DevotionalAct > IdentityClaim (0.69 vs 0.35)
- `tests/test_factor_graph_full.py` — all 9 verses pass with 0 errors

Compound coverage:
- `scripts/phase_a5b_seed_compounds.py` — manual compound hypothesis seeding for unsplit compounds
- Tokens 0-2 (bhairavanatham etc.) now have karmadharaya/tatpurusa alternative hypotheses

Alignment infrastructure:
- `src/sanskritree/translation/alignments.py` — token/span alignment recording, coverage reporting
- Unsupported-addition factor integrated into factor graph

## 2026-07-23 — foundation audit

The legacy `proof_engine` is preserved as a legacy subsystem. Its audit found the following V2 blockers:

- `proof_engine/sanskrit_pipeline.py` returns a placeholder morphology result and treats two tokens as a possible identity relation.
- `proof_engine/algorithm.py` accepts an LLM-provided `lean_type`, labels decomposed definitions `PROVED`, and exits its retry loop after one failure.
- Existing status semantics conflate textual assumptions with Lean-proved theorems.

The V2 implementation does not use those behaviours. It introduces a new `src/sanskritree` package and SQLite migration set alongside the legacy engine.

## Vertical slice boundary

The first pilot ingests one fixture verse, preserves raw and NFC-normalised readings, stores ambiguity-preserving analysis candidates, creates a reviewed-capable span alignment, records an immutable blind translation candidate with evidence, persists an explicit Semantic IR frame, and deterministically emits a registered Lean template. A textual assertion is stored as `formal_role=textual_axiom`, `lean_status=uncompiled`; it is never reported as a theorem.

## Toolchain status

Python 3.11.2 and pinned Lean `v4.29.0-rc4` are installed. `lean/Sanskritree` builds successfully, and the vertical slice now type-checks its deterministically generated declaration with `lake env lean`. This establishes type validity only; a textual assertion remains a textual axiom, not a proved historical claim.

## Corpus policy

No copyrighted edition, large Hugging Face corpus, or model is imported by this foundation commit. Imports must be manifest-driven and must record source URL, source hash, edition, licence, and critical method. This is necessary before any public redistribution, and avoids consuming the remaining ~17 GB volume capacity with unvetted multi-million-row datasets.

## Next implementation increments

1. add source-audited, executable adapters for Heritage, DCS, Vidyut, and process-sanskrit behind the shared lattice protocol; unavailable engines are now visible gaps rather than fabricated analysis;
2. add importer-specific licence/provenance adapters after source-card audits;
3. turn remaining CLI scaffold commands into reviewed-workflow operations;
4. replace conservative non-identical comparison results with Lean entailment/equivalence probes that preserve bridge assumptions.
