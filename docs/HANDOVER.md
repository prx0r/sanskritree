# Sanskritree Handover

## What the project is

Sanskritree is a **typed heterogeneous evidence graph for Sanskrit philology** — not a machine translation system. It represents thousands of competing, mutually supporting, mutually excluding philological hypotheses about a Sanskrit text, then lets confidence flow through the network while preserving exact provenance.

The ideal scientific description:

> A provenance-aware, tradition-scoped, heterogeneous factor graph for joint philological inference, using energy minimization and formal constraints to select globally coherent interpretations, with language models restricted to proposing hypotheses and realizing accepted semantic structures into English.

## What the project is NOT

- ❌ Not a Sanskrit→English MT system (no sequence-to-sequence training)
- ❌ Not a model to fine-tune on 400K pairs (Mitrasamgraha is for evaluation and lexical evidence, not training)
- ❌ Not a single authoritative translation engine (preserves competing hypotheses)
- ❌ Not a string-to-string pipeline (every decision is a typed graph node)
- ❌ Not a system that collapses multi-engine analyses into one answer (records differences)

## Architecture: three coupled graphs

```
1. Philological graph — what the Sanskrit text says
2. Translation graph — which English rendering best preserves it
3. Formal graph — what consequences follow from one interpretation
```

Lean at three layers:
```
Layer A — decision objects: morphological choices as typed structures
Layer B — frame consistency: semantic roles, agent/object/location
Layer C — philosophical proposition: truth-apt claims as theorems
```

## Architecture: five interoperating subgraphs

```
G₀ — Textual witness graph (externally recoverable textual facts)
G₁ — Linguistic hypothesis graph (segmentation, morphology, syntax, compounds)
G₂ — Semantic and lexical graph (lexemes, senses, tradition scope, frames)
G₃ — Translation evidence graph (alignments, additions, omissions)
G₄ — Formal and explanatory graph (Lean decision objects, propositions)
```

## Division of labour

| Layer | Role |
|-------|------|
| **Lean** | Hard constraint verification (admissibility) — does not select the most probable sense |
| **Graph** | Evidential support propagation (confidence) — factor graph, not neural net |
| **Human** | Acceptance decisions (sparse supervision) — the only source of truth |
| **LLM** | English rendering (graph-to-text) — renderer, not knowledge base |

## Key principle: evidence support ≠ acceptance status

A common but mistaken interpretation can accumulate enormous graph weight through repetition alone. These two values are kept separate:

```
propagated_score: 0.91  (what the graph calculates)
human_status: "accepted" (what the philologist decides)
lean_status: "consistent" (what Lean verifies)
```

## What's been built (this session)

### Database
- V2 SQLite: 23 tables, 592K rows, 3 works, 8,634 passages
- 401,936 token analyses, 5,465 unique lemmas (Vidyut)
- Migrations: 0001 (foundation), 0002 (comparison), 0003 (decision graph)

### Data ingested
- **MBT** (Manthānabhairavatantra): 5,436 verses OCR'd from legacy-font PDF via Google Vision API, ~$0.47, 0 errors
- **Mitrasamgraha**: 402,680 SK-EN pairs (CC BY 4.0) — 391K train, 5,587 val, 5,552 test
- **Bhairavastava** (Abhinavagupta, 9 verses): GRETIL IAST, structural gold corpus
- **Spandakārikā**: GRETIL source downloaded, not yet ingested

### Lean
- `lean/Sanskritree/Decision.lean` — Layer A: typed decision objects, 7 theorems, compiles
- `lean/Sanskritree/Core/Entity.lean` — InterpretationContext structure
- `lean/Sanskritree/Semantics/Relation.lean` — 8 relation axioms

### Translation workflow (Bhairavastava v1)
- 3 corrected candidates (construal, philological, interpretive)
- 6 token alignments, 3 error annotations (COMPOUND_BOUNDARY ×2, DOCTRINAL_ADDITION)
- Layer B SemanticFrame stored, Lean axiom compiled
- 24 blind candidates for verses 2-9

### Reference library (`ref/`)
| File | Content |
|------|---------|
| `ref/README.md` | Index + quick decision tree for all references |
| `ref/sourceref.md` | HF datasets + source repositories (GRETIL, SARIT, Muktabodha, DSBC) |
| `ref/targetslogic.md` | 30+ specific GRETIL texts by tradition (Nyāya, Mīmāṃsā, Buddhist logic, etc.) |
| `ref/archiveref.md` | Archive.org collections (KSTS, TSS, Navya-Nyāya, Gadādhara manuscripts) |
| `ref/graphref.md` | Graph architecture, sheaf theory, geometric deep learning references |
| `ref/mechanicsref.md` | Factor graphs, 5 subgraphs (G₀–G₄), V3 DB schema, Sanskrit NLP literature |
| `ref/goldfeedback.md` | 14 architecture corrections from review |
| `ref/factor_graph_spec.md` | Concrete factor graph implementation spec |

### Architecture docs (`docs/`)
| File | Content |
|------|---------|
| `docs/RESEARCH_PROGRAMME.md` | 12-stage progression plan + lexicon proposal |
| `docs/V2_PROGRESS.md` | Current state, revised implementation order |
| `docs/V2_BUILD_NOTES.md` | Architecture decisions |
| `docs/V2_SOURCE_AUDIT.md` | Data provenance protocol |
| `docs/V2_RESEARCH_MAP.md` | Resource integration map |
| `docs/GRAPH_ARCHITECTURE.md` | Three coupled graphs, sheaf theory reference |
| `docs/dev-plan.md` | Full 1,405-line development plan from subagent |

### Key code files
| File | Content |
|------|---------|
| `src/sanskritree/philology/adapters.py` | Vidyut morphology adapter (modified this session) |
| `src/sanskritree/philology/analysis_lattice.py` | Multi-engine analysis container |
| `src/sanskritree/translation/candidates.py` | Blind translation workflow |
| `src/sanskritree/semantics/schema.py` | SemanticFrame dataclass |
| `src/sanskritree/formal/compiler.py` | SemanticFrame → Lean compiler |
| `src/sanskritree/corpus/ingestion.py` | Manifest-driven import |
| `src/sanskritree/database.py` | SQLite connection + migration runner |
| `migrations/0001_v2_foundation.sql` | Core schema (16 tables) |
| `migrations/0002_v2_comparison.sql` | Formal relations |
| `migrations/0003_v2_decision_graph.sql` | analysis_hypothesis, hypothesis_dependency, translation_alignment, formalization_candidate |

### Key scripts created this session
| Script | Purpose |
|--------|---------|
| `scripts/mbt_ocr_full.py` | Batch OCR of 1,314 MBT Sanskrit pages via Vision API |
| `scripts/build_mbt_dataset.py` | Extract verses, align SK-EN from OCR output |
| `scripts/v2_activate_full.py` | Full V2 pipeline: ingest → analyze → blind translate |
| `scripts/v2_activate.py` | Pipeline activation helper |
| `scripts/seed_gretil.py` | GRETIL text fetcher + ingestion |
| `scripts/bhairavastava_pipeline.py` | Bhairavastava: correct v1, blind translate v2-9, Layer B frame |

### Key datasets
| File | Size | Content |
|------|------|---------|
| `data/datasets/mitrasamgraha_train.json` | 126 MB | 391,541 SK-EN pairs (CC BY 4.0) |
| `data/datasets/mitrasamgraha_test.json` | 2.1 MB | 5,552 test pairs (CC BY 4.0) |
| `data/datasets/mitrasamgraha_validation.json` | 2.0 MB | 5,587 val pairs (CC BY 4.0) |
| `data/datasets/mbt_verses.jsonl` | 5.5 MB | 6,367 MBT extracted verses |
| `data/datasets/mbt_page_aligned.jsonl` | 6.3 MB | 1,314 SK-EN page pairs |
| `data/ocr/mbt_ocr_full_state.json` | 4.9 MB | Raw OCR output per page |
| `data/manifests/mbt_kumarikakhanda_ocr_pilot.yaml` | 5.3 MB | Full OCR manifest |
| `data/manifests/mbt_v2_full.yaml` | 15 MB | Full V2 MBT manifest |
| `data/sanskritree-v2.db` | 232 MB | Main V2 database |

## Current state (v0.2 — 2026-07-24)

### Database
- **5 works**, 8,890 passages, 368 MB
- 136,431 token analysis hypotheses, 6,058 lexemes
- 511 adjudication decisions, 28 translation evaluations
- 4 Lean modules compiling (15 theorems), 16/16 pipeline tests

### Benchmark results (30 passages, 4 systems)
| Metric | v0.1 | v0.2 | Change |
|--------|------|------|--------|
| Frame selection errors | 6 | **1** | **-83%** |
| Candidate gap verses | 9 | 8 (+6 ByT5-seeded) | -11% |
| Evaluations completed | 5 | **28** | +460% |
| Compounds detected | 10 | 0 | resolved |

### Remaining gaps
1. **8 low-coverage verses** with ≤1 lemma (3 heritage_timeout, 5 compound/partial)
2. **1 frame selection miss** (vb.79 — now fixed but needs re-evaluation)
3. **No real LLM baselines** (A/B are gloss-based)
4. **Lean gate doesn't constrain** (C and D identical)
5. **No candidate-recall diagnostic automated** (script built, not integrated into CI)

### Works
- MBT Kumārikākhaṇḍa: 5,436 verses, 40% coverage (OCR legacy font)
- Bhagavad Gītā: 3,089 verses, 63% (with 4 commentaries)
- **Bhairavastava: 9 verses, 90% coverage (gold corpus)** 🏆
- Spandakārikā: 53 verses + 41 commentary, 66% coverage
- Vijñānabhairava: 162 verses, 39% coverage

### Key architecture decisions (from visionothers.md)
- ✅ Lean as finite projection — adopt now
- ⚠️ STAM — pilot later, not migrate now
- ❌ Local Heritage — deferred (90% remote success)
- ❌ Tesserae/AIF/nanopublications — too early
- ✅ PostgreSQL canonical, standards through adapters

## Consolidated development plan

### Current sprint: candidate recall
1. ✅ Fix frame detection (expanded keywords)
2. ✅ Candidate-recall diagnostic (8 low-coverage verses classified)
3. 📝 Staged fallback (Vidyut→Heritage→ByT5→corpus→manual)
4. ❌ Local Heritage benchmark on 8 failures (blocked on priority)
5. 📝 Real LLM baselines (A2/B2)
6. 📝 Lean mutation tests (make C≠D)
7. 📝 v0.3 report

### Next after recall sprint
- Expand benchmark to 120 passages
- STAM round-trip pilot
- Commentary intervention vertical slice

## What the validation literature says

Three key papers validate our approach:

1. **Krishna et al. (EMNLP 2018)** — "Free as in Free Word Order"
   - Graph-based joint inference (segmentation + morphology) beats sequential by 12.6% F-score
   - Uses < 1/10 the training data of neural models
   - Sanskrit's free word order makes local decisions unreliable — global inference required

2. **Krishna et al. (CL 2020)** — "A Graph-Based Framework"
   - Unified arc-factored energy model for segmentation, morphology, dependency, linearization, prosody
   - Language-agnostic (works for Czech too)
   - Language-specific constraints prune search space
   - This paper is the closest existing blueprint — Sanskritree extends it upward into semantics and translation

3. **Krishnan et al. (2020)** — "Validation of DCS using Heritage Tools"
   - Multi-engine disagreement is a feature, not a bug
   - Record differences, don't collapse them
   - Validates our analysis_lattice design

## Critical corrections from review (goldfeedback.md)

| Previous thinking | Corrected |
|-------------------|-----------|
| Naive tanh additive propagation | Damped synchronous logit propagation |
| Single ±1 edge weight | Binary polarity + separate magnitude/reliability/applicability |
| Hard exclusion by update order | Hard exclusion in solver (x_A + x_B ≤ 1) |
| Materialize all 401K analyses as graph | Passage-local projection from SQLite |
| Spanda: parent_passage_id for commentary | Many-to-many passage_relations table |
| G1 PyG after 9 verses | Delay until ≥100 adjudicated passages |
| G3 train on 27 simulated judgments | Never; use real adjudication only |
| G4: [NODE:X] markers in prose | Two-stage: JSON semantic plan → fluent render |
| Lexical senses: bulk for all lemmas | Lazy induction per active work |
| Lean: Float confidence in propositions | Evidence in DB, Lean verifies structure |
| Mitrasamgraha: single aggregate score | Stratified by domain, register, ambiguity |
| Combine belief + energy as α·G0 + (1-α)·(1-E) | Normalize: score = evidence_logit - λ·energy |
| Bhairavastava is the evaluation target | Structural gold only — Mitrasamgraha is the evaluation set (CC BY) |

## Revised implementation order

### Phase A — graph correctness (NOW)
```
A1. Correct graph ontology: TOKEN_OCCURRENCE ≠ MORPH_ANALYSIS_TYPE ≠ LEXEME
A2. Passage-local graph projection (SQL neighborhood query → local factor graph)
A3. Hard constraint factors (surface coverage, exclusivity)
A4. Stable synchronous propagation (logit-based, damped, clamped)
A5. Full Bhairavastava annotation (9 verses)
A6. Ablation and calibration report
```

### Phase B — translation traceability
```
B1. Token/span alignment infrastructure
B2. Unsupported-addition factors
B3. Structured JSON realization plans (G4-style, two-stage)
B4. Final fluent renderer
B5. Evaluation suite
```
Do this **before PyG**.

### Phase C — corpus expansion
```
C1. Spandakārikā ingestion (many-to-many commentary anchors, not parent_passage_id)
C2. Human adjudication interface
C3. Lazy lexical-sense inventory (only for lemmas in active works)
C4. Gold decision accumulation
```

### Phase D — symbolic consistency
```
D1. Lean Layer B (corrected schema without Float in propositions)
D2. Semantic-frame constraints
D3. Hand-specified sheaf/compatibility energy (sparse, relation-conditioned maps)
D4. Candidate-level energy explanations
```

### Phase E — learned scoring
Only after ≥100 adjudicated passages, ≥200 preference pairs, ≥3 works:
```
E1. Logistic and tree baselines
E2. Pairwise pathway-reliability model
E3. Path-ranking model
E4. R-GCN baseline
E5. HGT baseline
E6. Learned sheaf maps
```

## Things to remember

### General tips
1. **Don't train models early.** Structured rendering produces useful translations and gold decisions. A GNN trained on 9 verses learns your hand-coded assumptions in a less interpretable form.
2. **Dyczkowski is copyrighted.** Internal reference only. Never in public git, HF datasets, or model training. Mitrasamgraha (CC BY 4.0) is the evaluation set.
3. **Multi-engine disagreement is a feature.** Vidyut, Heritage, DCS will disagree. Record differences, don't collapse them.
4. **Evidence ≠ truth.** A popular error can have high graph weight. Propagated_score, human_status, and lean_status are separate fields.
5. **Passage-local factor graphs, not whole-corpus diffusion.** Build a small graph per inference run from SQLite neighborhood queries.
6. **Exact inference where possible.** Chu-Liu/Edmonds for dependency, CKY for compounds, ILP for global constraints. Use beam search only for scales where exact is impossible.
7. **Hard exclusion in the solver, not in update order.** Never let "which node updates first" decide exclusion.
8. **Two-stage LLM rendering.** JSON semantic plan first, then fluent English from approved segments. Post-hoc NER is validation only.
9. **Lazy lexical senses.** Don't create senses for all 5,465 lemmas. Create per active work.
10. **Stratify everything.** Mitrasamgraha scores by domain, register, ambiguity. A single aggregate number hides the problems we're solving.

### Data status
- MBT: Shadow evaluation corpus only. Don't make it the first production target just because the OCR is available.
- Bhairavastava: Structural gold (morphology + Lean + error taxonomy). No reveal step — no CC-BY reference.
- Mitrasamgraha: CC BY 4.0 evaluation set. Stratify by domain. Build separate Tantric challenge set.
- Spandakārikā: Next text. Use many-to-many passage_relations for commentary, not parent_passage_id.

### Lean integration
- Layer A: Decision objects ✅ (Decision.lean compiles)
- Layer B: Frame consistency (corrected: use GrammaticalCase, FrameRole, RoleBinding — no Float in propositions)
- Layer C: Propositions (corrected: use Polarity affirmed/denied, contradicts = sameContent ∧ oppositePolarity)
- Lean verifies "given these decisions, the conclusion follows" — NOT "this is what the Sanskrit means"

### Codebase navigation for the next agent

### Entry points
- `scripts/t1_translation_pilot.py` — generates 30-passage benchmark with 4 system outputs
- `scripts/t2_ab_evaluation.py` — A/B comparison + error annotation UI
- `scripts/t33_ab_comparison.py` — generates Systems A/B baselines + comparison report
- `scripts/annotate.py` — CLI annotation tool for morphology/compound/frame decisions
- `scripts/freeze_v0.1.py` — reproducible baseline freeze (corpus stats, tests, Lean, hashes)
- `scripts/m65_heritage_mapping.py` — Heritage compound→occurrence mapping with DP aligner

### Quick start for running evaluation
```bash
PYTHONPATH=src python3 scripts/t1_translation_pilot.py   # generate 30-passage pilot
PYTHONPATH=src python3 scripts/t33_ab_comparison.py       # 4-system comparison
PYTHONPATH=src python3 scripts/t2_ab_evaluation.py --stats # evaluation stats
PYTHONPATH=src python3 -m unittest tests.test_pipeline -v  # 16 tests
cd lean && lake build Sanskritree && cd ..                  # Lean verification
```

### Understanding the factor graph
- `src/sanskritree/inference/factor_graph.py` — FactorGraph, VariableChoice, Assignment, beam search
- `src/sanskritree/inference/factors.py` — 5 factors: agreement, compound, frame, unsupported_addition, action_detection
- `src/sanskritree/inference/propagation.py` — damped synchronous logit propagation + `compute_beliefs()`
- `src/sanskritree/inference/scoring.py` — FactorGraphV2 with per-factor decomposition

### Understanding the evaluation pipeline
- `src/sanskritree/translation/realization.py` — semantic_plan_from_assignment(), validate_plan(), render_english()
- `src/sanskritree/translation/evaluation.py` — chrF, morph_coverage, term_preservation, stratified domains
- `src/sanskritree/translation/alignments.py` — token/span alignment recording

### Understanding ritual frames (Vijñānabhairava)
- `src/sanskritree/semantics/ritual_frames.py` — 16 instruction types, 12 loci, detect_action() with keyword mapping
- `semantics/schema.py` — SemanticFrame dataclass with entity/relation enums
- `formal/compiler.py` — SemanticFrame → Lean code compiler

### Key gotchas
- **scripts/ imports fail** — the `scripts/` directory is not a Python package. Import inline code or use `PYTHONPATH=src` and import from the module
- **Heritage web API timeouts** — the remote API can timeout on long verses. The wrapper retries 3 times with 10s timeout. If it fails, the verse gets `HERITAGE_TIMEOUT`
- **morph_analysis_type FK issues** — `INSERT OR IGNORE` silently skips FK violations. Always check that lexeme exists before inserting analysis type
- **token_occurrence != original tokens** — Heritage may split one compound token into multiple segments, but token_occurrence has one entry per original whitespace-delimited token. The mapper aligns them
- **Tests import by subprocess** — `freeze_v0.1.py` runs tests via Python's unittest loader, not subprocess. The subprocess approach fails because `scripts/` isn't a package
- **Disk space** — 6.6GB free on `/`. HF cache at `/tmp/hf` may use 4GB+. Clean with `rm -rf /tmp/hf` and `pip cache purge`

### v0.4 experiment: B2 vs C decisive comparison
The key files for the next session:
- `proof/v04_evidence_bundles.json` — 30 bundles with frozen prompts, ready for LLM
- `proof/v04_prompts/a2_*.txt` — 30 plain translation prompts
- `proof/v04_prompts/b2_*.txt` — 30 retrieval-assisted prompts (lexicon + frame + gloss)
- `proof/v04_blind_evaluation.json` — randomized A/B evaluation sheet per passage
- `scripts/v04_experiment.py` — framework: `--generate`, `--evaluate`, `--report`

To run the experiment:
1. Send prompts to an LLM (Claude, GPT, etc.)
2. Store responses in `v04_evidence_bundles.json` under `llm_output_a2`/`llm_output_b2`
3. `python3 scripts/v04_experiment.py --evaluate` — generates blind comparison
4. Evaluate each passage: which is more accurate? Note critical errors.
5. `python3 scripts/v04_experiment.py --report` — see results by track

Decision rule (predefined): C succeeds if fewer critical errors than B2, lower post-edit time, lower unsupported-addition rate, no major regression on readability.

### Reference docs indexed in ref/README.md
The `ref/` directory contains all source references with a decision tree:
- `sourceref.md` — HF datasets + source repositories
- `targetslogic.md` — 30+ GRETIL texts by tradition
- `archiveref.md` — Archive.org collections + Navya-Nyāya
- `vision2.md` — Standards research (STAM, TEI, PROV-O, nanopublications)
- `visionothers.md` — Peer review of external tools with accept/pilot/defer decisions

## Key contacts for inference design
- Krishna et al. (CL 2020) — arc-factored energy model
- Neural Sheaf Diffusion — relation-specific diffusion for heterophilic graphs
- NBFNet — path-based inference with interpretable paths
- Outlines — JSON-schema-constrained LLM generation
- PyKEEN — KG embedding baselines (experimental only)

### File locations to remember
```
docs/                  — all architecture docs
src/sanskritree/       — V2 package
migrations/            — SQLite schema (3 migrations applied)
scripts/               — pipeline scripts
data/datasets/         — all datasets (MBT, Mitrasamgraha)
data/manifests/        — YAML import manifests
data/ocr/              — Vision API OCR output
data/sanskritree-v2.db — main database (232 MB)
lean/Sanskritree/      — Lean4 project
sources/               — PDF source files (untracked, 693 MB)
```

### Disk status
- 11 GB free
- Biggest consumers: data/ (486 MB), sources/ (693 MB, untracked)
- Upgrade only when: free < 3 GB, or starting local model fine-tuning
