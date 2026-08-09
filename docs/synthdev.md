# Synthetic Development Plan

Derived from: guidenow.md, dev-plan.md, RESEARCH_PROGRAMME.md, pipeline_checkpoint1.md,
immediatevision.md, graphref.md, mechanicsref.md, goldfeedback.md, targetslogic.md,
sourceref.md, phase2_vijnanabhairava.md

## Core Principle

> Translation pulls architecture into existence. Every capability is built in response to a
> real translation failure, not a planned ontology. References are evaluation signals, not
> ground truth.

## Phase Structure

```
PHASE 0 — FOUNDATION (completed v0.1-v0.4)
  → 120-passage benchmark, 511 adjudications, factor graph, Lean modules

PHASE 1 — COMPLETE-TEXT RECONSTRUCTION (COMPLETED ✅)
  → Spandakārikā 53 verses: blind translate → compare → diagnose → repair → verify
  → Result: 0 critical errors, 90% defensible rate, 59 tests, 53/53 verses

PHASE 2 — CROSS-TEXT TRANSFER (IN PROGRESS)
  → Vijñānabhairava 162 verses zero-shot
  → Ablation: C0 (general), C1 (pan-Śaiva), C2 (full Spanda senses)

PHASE 3 — SCHOLASTIC PROSE BASELINE (NEXT)
  → Tarkasaṅgraha + Dīpikā (Nyāya-Vaiśeṣika manual)
  → First non-tantric sense domain: controlled domain shift

PHASE 4 — COMMENTARIAL TANTRA
  → Spandanirṇaya selected passages (dense commentary prose)
  → Root/commentary alignment

PHASE 5 — LATER NYĀYA GATEWAY
  → Bhāṣāpariccheda + Muktāvalī (Navya-Nyāya categories)
  → Qualifier-qualificand structures, absence, inference

PHASE 6 — CLASSICAL NYĀYA CONTRAST
  → Nyāyasūtra Book 1 + Vātsyāyana Bhāṣya
  → Diachronic sense differentiation

PHASE 7 — NAVYA-NYĀYA VERTICAL SLICE
  → Selected Tattvacintāmaṇi module (vyāpti, pakṣatā, absence)
  → Nested relational representations

PHASE 8 — CROSS-SCHOOL TANTRA
  → Selected Kiraṇatantra or Parākhyatantra (Śaiva Siddhānta)
  → Pati-paśu-pāśa ontology

PHASE 9 — FIRST UNTRANSLATED WORK
  → Genuinely untranslated tantric text (50-200 verses)
  → No English ground truth; independent review

PHASE 10 — HARD NAVYA-NYĀYA
  → Larger Tattvacintāmaṇi section or Navya-Nyāya commentary
  → Untranslated first translation
```

## Stress Ladder

| Phase | New Difficulty | Transfer Type |
|-------|---------------|---------------|
| CP1 | Condensed doctrinal verse | Baseline |
| CP2 | Operational meditation language | genre |
| CP3 | Controlled scholastic prose + domain shift | school |
| CP4 | Dense commentarial Tantra | genre |
| CP5 | Compressed later-Nyāya categories | school |
| CP6 | Historical/domain variation | diachronic |
| CP7 | Nested Navya relational language | complexity |
| CP8 | Ritual and rival Śaiva ontology | school |
| CP9 | No English ground truth | evaluation |
| CP10 | First Navya-Nyāya translation | original |

## Pipeline Architecture

```
Sanskrit source (IAST)
  → Normalization
    → Candidate generation (vidyut, heritage, byt5)
      → Factor graph (beam search over morphology, compounds, frames)
        → Semantic plan (predicates, roles, polarity, modality)
          → Evidence bundle (DB-backed sense ranking with tradition proximity)
            → Literal renderer (span-licensed, deterministic)
              → LLM readable renderer (DeepSeek V4 Flash, constrained)
                → Audit (mutation tests, source hash, licence verification)
                  → Blind evaluation (identity-blinded, error taxonomy)
```

## Current State

| Metric | CP1 | Target | Phase 2 Target |
|--------|-----|--------|----------------|
| R@5 | 98.8% | ≥95% | ≥90% |
| Critical errors | 0 | 0 | 0 |
| Major errors | 0 | ≤2 | — |
| Defensible rate | 90% | ≥90% | — |
| Tests | 59 | — | 59+ |
| Works ingested | 5 | — | 5+ |
| Heritage retry | proven | generic | VB applied |

## Key Tests by Module

### Candidate Recall
```python
def test_recall_at_k_is_monotonic(): assert r1 <= r3 <= r5
def test_accepted_candidate_at_rank_one_counts_for_all_k()
def test_duplicate_equivalent_candidates_do_not_change_rank()
def test_recall_uses_frozen_pre_adjudication_candidates()
```

### Benchmark Integrity
```python
def test_all_53_passages_present()
def test_passage_ids_are_unique()
def test_split_sizes_are_30_13_10()
def test_splits_do_not_overlap()
def test_blind_runtime_cannot_open_reference_directory()
```

### Analysis Manifest
```python
def test_same_input_produces_identical_manifest()
def test_scores_equal_sum_of_named_components()
def test_mutually_exclusive_candidates_cannot_both_be_selected()
```

### Semantic Plan
```python
def test_negation_is_preserved_in_plan()
def test_agent_and_patient_do_not_swap()
def test_unresolved_pronoun_stays_unresolved()
```

### Literal Renderer + Audit
```python
def test_every_content_span_has_semantic_licence()
def test_negation_mutation_detected()
def test_unsupported_addition_detected()
def test_source_hash_mismatch_detected()
```

### Anti-Overfitting
```python
def test_no_translation_rule_mentions_passage_id()
def test_lexical_glossary_is_not_verse_specific()
def test_heritage_candidates_record_provenance()
```

### Transfer (Phase 2)
```python
def test_spanda_regression_tests_still_pass()
def test_vb_sense_ablation_shows_c1_helps()
def test_c2_does_not_cause_critical_errors()
```

## Data Sources and Justification

| Source | Contents | Justification |
|--------|----------|---------------|
| GRETIL | Clean IAST texts | Best provenance, citation-standard |
| Mitrasamgraha | Sanskrit-English parallel | CC BY 4.0, evaluation harness |
| Muktabodha | Śaiva/Śākta Tantra | Deepest for untranslated works |
| Heritage/Vidyut/ByT5 | Morphological analysis | High-recall candidate generators |
| Cologne Dictionaries | MW, Apte, etc. | Sense inventory |
| Dyczkowski (SUNY) | Spandakārikā translation | Evaluation reference (copyrighted, internal) |
| Archive.org | Rare editions | KSTS, TSS series |
| SARIT | TEI XML editions | Structured, citation-tracked |

## Immediate Roadmap

### Phase 2 completion (Vijñānabhairava)

1. ✅ Heritage transport hardened (timeout 10→120s, failure classes)
2. ✅ VB benchmark frozen (162 verses, source hashes)
3. ✅ Sense-scope ablation infrastructure (C0/C1/C2 filters)
4. ✅ C2 blind rendering (80/80 dev verses complete)
5. 🔄 C1 blind rendering (80 dev verses, running in background)
6. ⬜ C0 blind rendering (80 dev verses)
7. ✅ Lakshmanjoo reference aligned (142/162 verses mapped)
8. ✅ C2 vs reference comparison structure built
9. ⬜ Transfer classification (TRANSFERRED_SUCCESS vs SPANDA_OVERFIT)
10. ⬜ Holdout unseal and final report

### Phase 3 (Tarkasaṅgraha)

1. ✅ Downloaded from Archive.org (multiple editions)
2. ⬜ Clean up OCR / find clean digital text
3. ⬜ Create YAML manifest with sutra-level passages
4. ⬜ Ingest into DB, run morphology
5. ⬜ Create Nyāya-Vaiśeṣika sense entries in lexical_senses
6. ⬜ Blind generate with school-aware ranker

### Corpus acquisition

1. ✅ Jīvānanda: 22 core PDFs downloaded (490 MB)
2. ✅ Tantric Texts Series: partially downloaded
3. ⬜ Remaining Tantric Texts volumes
4. ⬜ Trivandrum Sanskrit Series
5. ⬜ Bibliotheca Indica, Ānandāśrama, Kāvyamālā

## Confidence Calibration (Phase 3 prerequisite)

Before Phase 3, implement:
- Brier score measurement
- Expected Calibration Error
- Risk-coverage curve
- Low-confidence error rate tracking

## Commentary-Aware Planning (deferred to Phase 4)

Currently planned but not built:
- Commentary dependency classification
- Commentary provenance labelling
- Commentary-aware semantic plan expansion
