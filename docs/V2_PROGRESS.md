# V2 Progress

## Current state (2026-07-24)

### Database
- **25 tables**, ~600K rows, **5 works**, **8,890 passages**
- 4 migrations applied (0001 foundation, 0002 comparison, 0003 decision graph, 0004 graph ontology)
- `lexeme`: **5,787** unique lemmas | `morph_analysis_type`: **15,859** | `token_occurrence`: **169,341** | `token_analysis_hypothesis`: **136,086**
- `passage_readings`: 8,890 | `tokens`: 169,341 | `token_analyses`: 405,145
- `semantic_frames`: 10 | `formalizations`: 11 | `lexical_senses`: 4 | `translation_alignment`: 5 | `hypothesis_solution_support`: 268

### Data ingested
| Source | Type | Size | Licence |
|--------|------|------|---------|
| **MBT Kumārikākhaṇḍa** | Vision API OCR, Devanāgarī | 5,436 verses, 2.3M chars | Commercial scan |
| **Bhairavastava** (Abhinavagupta) | GRETIL IAST | 9 verses | CC BY-NC-SA 4.0 |
| **Spandakārikā** (Vasugupta + Kṣemarāja) | GRETIL IAST | 53 verses + 41 commentary blocks | CC BY-NC-SA 4.0 |
| **Vijñānabhairava** | GRETIL IAST | **162 verses** | CC BY-NC-SA 4.0 |
| **Bhagavad Gītā** | GRETIL IAST | 3,089 verses (with 4 comms) | CC BY-NC-SA 4.0 |
| **Mitrasamgraha** | HF dataset, IAST | 402,680 SK-EN pairs | **CC BY 4.0** ✅ |
| **GRETIL quotes** | HF dataset, IAST+Devanāgarī | 200K entries (20K Tantra) | Research use |

### Works in DB
1. `mbt_kumarikakhanda` — 5,436 passage_readings
2. `bhagavad_gita` — 3,089 passage_readings
3. `abhinavagupta_bhairavastava` — 9 passage_readings (gold corpus ✅)
4. `spandakarika` — 53 verse + 41 commentary passage_readings
5. `vijnanabhairava` — 162 passage_readings

### Test results
- **Pipeline tests**: **16/16 passing** (corpus integrity, morphology coverage, factor graph determinism, propagation convergence/stability, Lean compilation)
- **Factor graph**: Bhairavastava v1 — karmadharaya (0.73) > tatpuruṣa (0.31), DevotionalAct (0.69) > IdentityClaim (0.35). All 9 verses produce valid assignments. Deterministic across runs.
- **Propagation**: converges to same state regardless of iteration count, no NaN/Inf, karmadharaya preferred over tatpuruṣa via evidence paths
- **Lean**: **4 modules** compiling: Decision.lean (7 theorems), LayerB.lean (8 theorems), Core/Entity.lean, Semantics/Relation.lean — 15 theorems total
- **Bhairavastava gold corpus**: 90% token coverage (62/69), 3 Heritage compound splits verified, 3 error corrections regression-tested, Lean verification across all layers
- **Heritage mapping**: DP aligner for source↔segments, deduplication (325 saved on v1 alone), solution support tracking, coverage improvement: Bhairavastava 54%→90%, Spandakārikā 8%→66%
- **Stratified evaluation**: 9 domains detected from Mitrasamgraha (vedic, epic, tantric, philosophical, etc.)
- **Commentary linking**: 370 passage_relation links for Spandakārikā (many-to-many, not parent_passage_id)

---

## Architecture

### Three coupled graphs
```
1. Philological graph — what the Sanskrit text says
2. Translation graph — which English rendering best preserves it
3. Formal graph — what consequences follow from one interpretation
```

### Division of labour
| Layer | Role |
|-------|------|
| **Lean** | Hard constraint verification (admissibility) |
| **Graph** | Evidential support propagation (confidence) — factor graph, not neural net |
| **Human** | Acceptance decisions (sparse supervision) |
| **LLM** | English rendering (graph-to-text — renderer, not knowledge base) |

### Key principle: evidence support ≠ acceptance status
```
propagated_score: 0.91   (what the graph calculates)
human_status: "accepted" (what the philologist decides)
lean_status: "consistent" (what Lean verifies)
```

---

## Implementation status

### Phase A — Graph correctness ✅ COMPLETE

| Step | Status | Notes |
|------|--------|-------|
| A1 Graph ontology | ✅ | Migration 0004: lexeme, morph_analysis_type, token_occurrence, token_analysis_hypothesis, passage_relation |
| A2 Factor graph core | ✅ | `inference/factor_graph.py` — VariableChoice, Assignment, Factor, FactorGraph, beam search |
| A3 Hard/soft factors | ✅ | `inference/factors.py` — agreement, compound, frame, unsupported_addition |
| A4 Propagation | ✅ | `inference/propagation.py` — damped synchronous logit (per goldfeedback) |
| A5 Compound coverage | ✅ | 162 Tantra vocabulary items seeded; coverage 46.4% Bhairavastava, 7.7% Spandakārikā |
| A6 Bhairavastava test | ✅ | 9/9 verses pass, karmadharaya > tatpuruṣa verified |

### Phase B — Translation traceability ✅ COMPLETE

| Step | Status | Notes |
|------|--------|-------|
| B1 Token/span alignment | ✅ | `translation/alignments.py` — alignment recording, coverage reporting |
| B2 Unsupported-addition factors | ✅ | Integrated into factor graph (DOCTRINAL_ADDITION penalty = 3.0) |
| B3 JSON semantic plans | ✅ | `translation/realization.py` — two-stage: JSON plan → fluent render |
| B4 Evaluation suite | ✅ | `translation/evaluation.py` — chrF++, morph coverage, term preservation, stratified by 9 domains |
| B5 3-candidate workflow | ✅ | 36 runs created for Bhairavastava (3 profiles × 9 verses + verse 1 corrections) |

### Phase C — Corpus expansion 🟡 PARTIAL

| Step | Status | Notes |
|------|--------|-------|
| C1 Spandakārikā | ✅ | 53 verses, 41 commentary blocks, 370 passage_relation links |
| C2 Lexical senses | ✅ | 4 active lemmas seeded (lazy approach); 8,260 lemma types from Mitrasamgraha |
| C3a Tantra vocabulary | ✅ | 162 compound members + Tantric terms seeded |
| C3b HF GRETIL quotes | ✅ | 200K entries (20K Tantra) from paws/sanskrit-verses-gretil → R2 |
| C3c Heritage integration | ⏳ | ~24h work for exhaustive sandhi splitting |

### Phase D — Symbolic consistency 🟡 PARTIAL

| Step | Status | Notes |
|------|--------|-------|
| D1 Lean Layer B | ✅ | `LayerB.lean` — GrammaticalCase (8), FrameRole (12), compat case-role (Bool), 8 theorems |
| D2 Semantic-frame constraints | ⏳ | Schema exists, factor graphs use frames |
| D3 Sheaf consistency | ⏳ | Not started — needs more gold data |
| D4 Energy explanations | ⏳ | Not started |

### Phase E — Learned scoring ❌ NOT STARTED

Blocked on: ≥100 adjudicated passages, ≥200 preference pairs, ≥3 works with gold labels.

---

## Lean modules (all compiling)

| Module | Theorems | Purpose |
|--------|----------|---------|
| `Core/Entity.lean` | — | InterpretationContext structure |
| `Semantics/Relation.lean` | — | 8 relation axioms |
| `Decision.lean` | 7 | Layer A: typed morphological decisions |
| `LayerB.lean` | 8 | Layer B: case-role compatibility, frame verification |

---

## Source code map

```
src/sanskritree/
├── inference/
│   ├── factor_graph.py     — FactorGraph, VariableChoice, Assignment, beam search
│   ├── factors.py          — agreement, compound, frame, unsupported_addition factors
│   └── propagation.py      — damped synchronous logit propagation
├── translation/
│   ├── candidates.py       — blind translation workflow
│   ├── alignments.py       — token/span alignment + coverage reporting
│   ├── realization.py      — two-stage JSON plan → English rendering
│   └── evaluation.py       — stratified evaluation (chrF++, morph cov, term preservation)
├── corpus/
│   ├── ingestion.py        — manifest-driven import
│   └── normalization.py    — NFC normalization
├── philology/
│   ├── adapters.py         — Vidyut + Heritage + DCS engine adapters
│   └── analysis_lattice.py — multi-engine analysis container
├── semantics/
│   └── schema.py           — SemanticFrame dataclass, entity/relation enums
├── formal/
│   ├── compiler.py         — SemanticFrame → Lean code (4 templates)
│   ├── checker.py          — Lean compilation checker
│   └── comparison.py       — Formal relation comparison
├── integrations/
│   ├── legacy_font.py      — Kruti Dev decoder framework
│   ├── morpho_sequences.py — HF dataset importer
│   ├── sanskrit_library.py — Sanskrit Library transport
│   └── tei.py             — TEI/XML reader
├── review/
│   └── importer.py         — annotation import
└── database.py             — SQLite connection + migration runner
```

---

## Reference library

Reference materials moved to `ref/` for future reference:
| File | Content |
|------|---------|
| `ref/README.md` | Index + quick decision tree |
| `ref/sourceref.md` | HF datasets + source repositories |
| `ref/targetslogic.md` | 30+ GRETIL texts by tradition |
| `ref/archiveref.md` | Archive.org collections + Navya-Nyāya |
| `ref/graphref.md` | Graph architecture, sheaf theory |
| `ref/mechanicsref.md` | Factor graphs, Sanskrit NLP literature |
| `ref/goldfeedback.md` | 14 architecture corrections |
| `ref/factor_graph_spec.md` | Factor graph implementation spec |

Project docs remain in `docs/`.

---

## Next milestones

### M8: Ritual/instruction semantic frames (Vijñānabhairava)
Vijñānabhairava (162 verses) introduces procedural language, injunctions, sequence, bodily locations. Extract ritual frames (DevotionalAct expanded to include Instruction, Procedure, Location).

### M9: Real adjudications
Spandakārikā + Vijñānabhairava blind translations → human review → gold decisions. Each adjudication is a training example for later learned models.

### M10-M12: Learned baselines, Lean Layer C, graph experiments
Deferred until ≥100 real adjudications exist.

### Heritage batch for Vijñānabhairava
Heritage API is confirmed working. Local Heritage installation would speed processing but web API is acceptable for current corpus size (162 verses × 3-5s ≈ 10 min).

---

## Deferred

| Action | Reason |
|--------|--------|
| Fine-tune NLLB/Gemma | Need ≥5K reviewed candidates + evaluation harness |
| G1 PyG | Need ≥100 adjudicated passages |
| G3 Learned pathway weights | Need ≥200 real preference pairs |
| G4 Constrained LLM rendering | JSON plan exists — needs LLM integration |
| MBT as production target | Shadow evaluation only (copyright) |
| Vijñānabhairava ingestion | Same pipeline — validate on Spandakārikā first |
| More schema migrations | 25 tables sufficient |

## Key principles

- Lean proves: "Given this segmentation, morphology, lexical sense, semantic frame and assumptions, the conclusion follows."
- Lean does NOT prove: "This is what the Sanskrit uniquely means."
- Three candidates per verse (construal, philological, interpretive)
- Blind generate → freeze → reveal reference → record disagreements
- Never silently correct a blind candidate to match Dyczkowski
- Every English span links to a source token or is labelled commentary
- Evidence flow ≠ truth. A popular error can accumulate high graph weight.
- Passage-local factor graphs for inference, not whole-corpus diffusion.
- Hard exclusion in solver (x_A + x_B ≤ 1), never by update order.
- Two-stage LLM rendering: JSON semantic plan → fluent English pass.
