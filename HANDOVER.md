# Sanskritree Handover

## What this project is

Sanskritree is a **machine-assisted critical translation laboratory** for Sanskrit Tantric texts. It combines multiple analysis engines (Vidyut, Heritage, ByT5), a factor graph for selecting among competing analyses, a constrained English renderer, and a Lean-based structural auditor.

The core thesis: structured philological inference (segmentation → morphology → compounds → semantic frames) produces more auditable and defensible translations than giving an LLM the same evidence — and the audit trail enables scholarship that a raw LLM output cannot.

## Where we are right now

**Current state (v0.4 → v0.5):**
- 5 works ingested (MBT, Bhairavastava, Spandakārikā, Bhagavad Gītā, Vijñānabhairava)
- 8,890 passages, 136K hypotheses, 6K lexemes
- 511 adjudications, 120-passage benchmark
- **Checkpoint 1 completed**: blind Pass 1 on 53 Spandakārikā verses, frozen 30/13/10 split
- **Real candidate recall**: R@1=63.2%, R@3=93.9%, R@5=98.8% (against 511 adjudicated morphology items)
- **Frozen benchmark**: `benchmarks/spanda_v1/` with 53 passages, source hashes, gold morphology, Dyczkowski refs
- **Analysis manifest**: deterministic decision records with decomposed scores per passage
- **Semantic plans**: negation/roles/compounds extracted from lemmas
- **Literal renderer**: span-licensed English output with audit trail
- **Mutation tests**: negation, unsupported addition, source hash mismatches detected
- **37 tests** passing (16 original + 9 benchmark + 12 audit/render)
- **All 53 verses** have LLM-rendered English (DeepSeek V4 Flash via opencode API)

**Key files:**
| File | Purpose |
|------|---------|
| `src/sanskritree/inference/factor_graph.py` | Factor graph core (beam search, variables, assignment) |
| `src/sanskritree/inference/factors.py` | 5 factors: agreement, compound, frame, unsupported_addition, action_detection |
| `src/sanskritree/inference/propagation.py` | Damped synchronous logit propagation |
| `src/sanskritree/inference/scoring.py` | Per-factor score decomposition |
| `src/sanskritree/semantics/ritual_frames.py` | 16 action types + detect_action() keyword mapping |
| `src/sanskritree/evaluation/candidate_recall.py` | **Real** Recall@k against adjudicated gold |
| `src/sanskritree/evaluation/blind_context.py` | BlindRunContext to prevent reference leakage |
| `src/sanskritree/translation/analysis_manifest.py` | Deterministic decision record with scored alternatives |
| `src/sanskritree/translation/render_literal.py` | Span-licensed literal English renderer |
| `src/sanskritree/semantics/plan.py` | Semantic plan with negation, roles, compounds |
| `src/sanskritree/audit/translation.py` | Mutation audits: negation, additions, source hash |
| `benchmarks/spanda_v1/` | Frozen 53-verse Spanda benchmark with gold + refs |
| `proof/checkpoint1/` | Pass 1 records, manifests, evaluation protocol |
| `scripts/candidate_recall.py` | CLI for candidate recall reporting |
| `scripts/run_spanda_checkpoint.py` | Full-text translation runner: prepare/generate/audit/evaluate/report |

## The plan: Checkpoint 1

The immediate goal is **not** to build a platform. It is:

> Translate the Spandakārikā (53 verses + Kṣemarāja commentary) with full audit trail — every decision inspectable, uncertainty explicit, Lean-verified.

**Why Spandakārikā:**
- 53 verses — manageable
- 67% coverage already, 370 commentary links in DB
- Kṣemarāja commentary provides the difficult test case (commentary-dependent interpretation)
- Our contribution: auditable translation with integrated commentary provenance

**How to proceed:**
1. Coverage push — bring Spandakārikā from 67% to 95%+ (run Heritage batch on remaining verses, seed rare vocabulary)
2. Consecutive translation — produce full translation of all 53 verses, not random excerpts
3. Commentary linking — ensure every Kṣemarāja gloss is linked at the span level
4. Audit — Lean certificate for every verse
5. Human review — all 53 verses reviewed
6. Publish — v1.0 release with complete audit trail

**Principle:** Let translation pull architecture into existence. When a verse is untranslatable due to a compound → fix compound parsing. When a word is ambiguous → fix lexical ranking. When commentary is needed → build commentary linking. Don't build capabilities until translation demands them.

## Codebase navigation

### Entry points
- `scripts/t1_translation_pilot.py` — generates benchmark (30 or 120 passages)
- `scripts/t2_ab_evaluation.py` — A/B comparison + error annotation UI
- `scripts/t33_ab_comparison.py` — A2/B2 baseline generation
- `scripts/recall_ci.py` — candidate-recall CI (Recall@k, engine contribution)
- `scripts/annotate.py` — CLI annotation tool for morphology/compound/frame decisions
- `scripts/v03_baselines.py` — publication gate + mutation tests
- `scripts/v04_experiment.py` — B2-vs-C experiment framework

### Quick start
```bash
PYTHONPATH=src python3 scripts/recall_ci.py           # candidate-recall CI
PYTHONPATH=src python3 scripts/v04_experiment.py --report  # experiment report
PYTHONPATH=src python3 -m unittest tests.test_pipeline -v  # 16 tests
cd lean && lake build Sanskritree && cd ..            # Lean verification
```

### Key gotchas
- `scripts/` is not a Python package — import fails. Use `PYTHONPATH=src` + inline code
- `morph_analysis_type` FK to `lexeme` is strict — always ensure lexeme exists before inserting analysis type
- Heritage web API may timeout (3 retries, 10s timeout). Timeouts are classified as `HERITAGE_TIMEOUT`
- Disk: ~6GB free. HF cache at `/tmp/hf` can use 4GB+. Clean with `rm -rf /tmp/hf`
- ByT5-Sanskrit (581M params) loads in ~2s on CPU. Keep loaded between calls

## Reference docs

| File | Content |
|------|---------|
| `ref/sourceref.md` | HF datasets + source repositories |
| `ref/targetslogic.md` | 30+ GRETIL texts by tradition |
| `ref/archiveref.md` | Archive.org collections + Navya-Nyāya |
| `ref/vision2.md` | Standards research (STAM, TEI, PROV-O, nanopublications) |
| `ref/visionothers.md` | Peer review of external tools with accept/pilot/defer decisions |
| `docs/immediatevision.md` | Current strategic focus — Checkpoint 1 |
| `docs/sprint_v04.md` | v0.4 experiment plan |
| `docs/next_steps.md` | Milestone tracking |

## Logical Texts Roadmap (after Checkpoint 1)

The texts in `ref/targetslogic.md` have **explicit argument structure** — premises, inferences, objections, replies — that maps directly to our factor graph. Each argument step is a node, inference relations are edges, contradictions are constraints.

### Translation order

| Priority | Text | Verses | Why this order |
|----------|------|--------|---------------|
| 1 | **Tarkasaṃgraha** (Annaṃbhaṭṭa) | ~80 | Shortest, simplest. Nyāya-Vaiśeṣika categories primer. Multiple translations exist for comparison. |
| 2 | **Nyāyasūtra** (Gautama) | ~200 | Foundational logic. Aphoristic. Every sūtra is a logical atom. Well-studied. |
| 3 | **Nyāyabindu** (Dharmakīrti) | ~100 | Buddhist epistemology. Clear inference structure. Tests cross-school logic. |
| 4 | **Vākyapadīya** (Bhartṛhari) | ~1,000 | Language philosophy. Sphoṭa theory maps to our semantic frames. Modular sections. |
| 5 | **Kiraṇatantra 1-6** | 174 | Śaiva ontology arguing against rival systems. Commentary adds depth. |
| 6 | **Ratnatrayaparīkṣā** (Śrīkaṇṭha) | 324 | Genuinely untranslated — final test after pipeline proven on translated texts. |

The "logical geometry" is most tractable for Tarkasaṃgraha and Nyāyasūtra — they're taxonomies of inference patterns, exactly what a factor graph models. Mīmāṃsā texts (Śābarabhāṣya, Ślokavārttika) are the hardest — long, dense, deeply commentarial.

**But first:** Spandakārikā (53 verses, 67% coverage, multiple translations for comparison). Prove the pipeline. Then these.

## Checkpoint 1: Spandakārikā Translation Pipeline

The system improves by being wrong in measurable ways. Every translation disagreement with a reference is a training signal.

### Pipeline
```
INGEST Sanskrit + multiple English translations
  → BLIND TRANSLATE (no references seen)
    → COMPARE verse-by-verse against each reference
      → CLASSIFY every disagreement (error taxonomy)
        → FIX top systematic errors
          → RE-RUN blind → measure improvement
```

### Implementation order
1. Ingest Spandakārikā text and all available English translations (Dyczkowski, Singh, etc.)
2. Ensure verse-level alignment across all sources
3. Build blind translation runner (script exists: `t1_translation_pilot.py`)
4. Build comparison script: Sanskritree vs Reference A vs Reference B vs Reference C
5. Classify disagreements using the error taxonomy
6. Fix top 3 systematic error classes
7. Re-run blind translation → measure improvement
8. Repeat until convergence

### Reference-first design
The comparisons are what produce learning signals. Without references, every translation is equally (un)verifiable. This is why Spandakārikā is the right first target — multiple translations exist, giving us ground truth for evaluation.

### Key files
- `docs/pipeline_checkpoint1.md` — full pipeline specification
- `docs/immediatevision.md` — strategic rationale
- `scripts/t1_translation_pilot.py` — benchmark generation (adapt for Spanda 53 verses)
- `scripts/recall_ci.py` — candidate-recall CI (adapt for Spanda coverage tracking)

### Reusable design
The same pipeline works for any Sanskrit text with verse-aligned English translations: ingest → blind translate → compare → classify → fix → re-run. After proving on Spandakārikā, apply to Vijñānabhairava, Kiraṇatantra, etc.

---

## 🧠 What the next agent needs to know (informal notes to myself)

### First-day checklist

1. **Check disk space** — `df -h /`. If <3GB free, clean with `rm -rf /tmp/hf && pip cache purge`. The HF cache fills up fast.
2. **Run the tests** — `cd /root/projects/sanskritree && PYTHONPATH=src python3 -m unittest tests.test_pipeline -v`. Expect 16/16 pass. If less, something is broken.
3. **Check Lean builds** — `cd lean && lake build Sanskritree`. Should succeed silently. If it fails, check `lean-toolchain` matches installed Lean version.
4. **Run recall CI** — `PYTHONPATH=src python3 scripts/recall_ci.py`. See the coverage numbers. If many verses are missing, the benchmark needs regeneration.
5. **Check Spandakārikā coverage** — Use the command from `docs/ingestion_checkpoint1.md`.

### Database: what's in there

The main DB is at `data/sanskritree-v2.db` (368 MB). Everything lives there. If you nuke it, you lose all hypotheses, adjudications, evaluations — everything except the raw source files.

**Key tables when you're debugging:**
- `token_analysis_hypothesis` — every candidate analysis from every engine (136K rows)
- `adjudication_decisions` — human decisions about which analysis is correct (511 rows)
- `translation_evaluations` — A/B comparison results (28 rows)
- `translation_errors` — error annotations from evaluation (24 rows)
- `lexeme` — all known word lemmas (6K)
- `passage_relation` — commentary-to-verse links (370 for Spanda)
- `compound_tree_hypothesis` — nested compound parses (6 trees)

### OCR: Google Vision API
A Google Vision API key is available (`GOOGLE_VISION_API_KEY` shell env). Use it for OCR on PDFs/images, e.g., extracting reference translations from scanned books. Do NOT commit the key to git.

### Common things that break

**1. ImportError when running scripts**
```python
# WRONG — scripts/ isn't a package
from scripts.recall_ci import evaluate_candidate_recall  # ImportError

# RIGHT — use PYTHONPATH=src and import from the module
# or just inline the code
```
Always use `PYTHONPATH=src python3 scripts/<name>.py`. Never try to `import scripts`.

**2. morph_analysis_type FK errors**
This is the most common DB error. The `morph_analysis_type` table has a foreign key to `lexeme`. If a lexeme doesn't exist when you insert an analysis type, you get a silent failure (with `INSERT OR IGNORE`) or a crash (with `INSERT`).

**The fix pattern:**
```python
# Always look up the lexeme first
existing = conn.execute("SELECT lexeme_id FROM lexeme WHERE lemma_slp1=?", (lemma,)).fetchone()
if existing:
    lid = existing[0]
else:
    lid = f"lex_mynew_{lemma}"
    conn.execute("INSERT INTO lexeme (lexeme_id, lemma_slp1, ...) VALUES (?,?,...)", (lid, lemma, ...))
```

**3. Heritage web API timeouts**
The remote API at INRIA can be slow or drop connections. The wrapper retries 3 times with 10s timeout. If a verse shows `HERITAGE_TIMEOUT`, just re-run it — it might work the second time.

Known issue: IAST tildes (`~` in `j~na` etc.) cause consistent timeout because the Heritage URL encoding doesn't handle them. For verses with these characters, Heritage recovery will likely fail. Alternate normalization (converting `j~na` → `jña` before sending) may help but is not implemented.

**4. Passage IDs don't match between benchmark and DB**
The pilot uses short IDs like `bv.1` but the DB uses full IDs like `bhairavastava.1`. The fix was applied in v0.3 — the recall CI now uses canonical DB IDs. If you regenerate the pilot, it uses DB IDs.

**5. DeepSeek V4 Flash API may return empty for certain prompts**
The model consumes all tokens on reasoning (especially for short/long inputs). Use `max_tokens=4096` and include the system message: `"You are a Sanskrit translation engine. Output ONLY the English translation."` Base URL: `https://opencode.ai/zen/go/v1`. Key is in `OPENAI_API_KEY` env var.

**6. The `scripts/` directory is not a package — use `PYTHONPATH=src`**
New scripts: `scripts/candidate_recall.py`, `scripts/run_spanda_checkpoint.py`, `scripts/render_pass1.py`. Always run with `PYTHONPATH=src`.

### Spandakārikā: current state

- **Checkpoint 1 Pass 1 completed**: all 53 verses processed through factor graph + LLM rendering
- **Benchmark frozen**: `benchmarks/spanda_v1/` with 53 passages, 30/13/10 split, source hashes
- **Candidate recall**: R@1=63.2%, R@3=93.9%, R@5=98.8% (need R@5≥95%, currently met)
- **Dyczkowski reference**: 34 of 53 verses extracted from PDF (`benchmarks/spanda_v1/references/dyczkowski.jsonl`)
- **LLM rendering**: 50/53 verses have fluent English via DeepSeek V4 Flash (3 empty due to model issue)
- **37 tests passing**: pipeline + benchmark + audit/render
- **Analysis manifests**: deterministic decision records for every verse
- **Mutation audits**: negation, unsupported addition, source hash checks

**Remaining gaps:**
- 3 verses with empty LLM output (seq 33, 47, 52 — need model retry)
- 19 Dyczkowski ref verses missing (commentary-only coverage gaps)
- Singh reference not yet ingested
- Full blind evaluation (stage A + B) not yet performed

### What NOT to do

1. **Don't train a neural model** yet. We have 511 adjudications, not 5,000. Learned ranking will mostly learn noise at this size.
2. **Don't migrate to STAM/nanopublications.** The vision2.md/visionothers.md debate settled this: standards through adapters, not migration.
3. **Don't build local Heritage** — the web API benchmark showed 90% success on hard cases. Local install would take 4-8h and solve at most 2-3 timeout verses.
4. **Don't expand to Vijñānabhairava** until Spandakārikā is through Checkpoint 1.
5. **Don't optimize toward agreement with Dyczkowski.** References are diagnostic signals, not ground truth. The defensible-reading rate is the real metric.

### How to find things

| What you need | Where to look |
|---------------|---------------|
| Factor graph code | `src/sanskritree/inference/factor_graph.py` |
| The 5 factors | `src/sanskritree/inference/factors.py` |
| Propagation algorithm | `src/sanskritree/inference/propagation.py` |
| Score decomposition | `src/sanskritree/inference/scoring.py` |
| Action detection keywords | `src/sanskritree/semantics/ritual_frames.py` |
| Candidate recall (real) | `scripts/candidate_recall.py`, `src/sanskritree/evaluation/candidate_recall.py` |
| Checkpoint runner | `scripts/run_spanda_checkpoint.py` (prepare/generate/audit/evaluate/report) |
| Frozen benchmark | `benchmarks/spanda_v1/` (passages.jsonl, splits.json, gold/, references/) |
| Analysis manifest | `src/sanskritree/translation/analysis_manifest.py` |
| Literal renderer | `src/sanskritree/translation/render_literal.py` |
| Semantic plans | `src/sanskritree/semantics/plan.py` |
| Translation audit | `src/sanskritree/audit/translation.py` |
| Blind context | `src/sanskritree/evaluation/blind_context.py` |
| B2 vs C experiment (legacy) | `scripts/v04_experiment.py` |
| Lean modules | `lean/Sanskritree/Decision.lean`, `LayerB.lean` |
| All reference docs | `ref/README.md` (there's a decision tree) |
| Checkpoint 1 plan | `docs/guidenow.md` |
| Checkpoint 1 data | `proof/checkpoint1/` (protocol, references, runs, evaluation) |

### Checkpoint 1 complete

**State as of 2026-07-24:**

**✅ Pipeline gates (all pass):**
- 53/53 complete translations (SPANDAKARIKA_TRANSLATION_V1.md)
- Lemma R@5 = 98.8%
- 0 critical translation errors
- 0 SANSKRITREE_ERROR on correctly aligned references
- 59 tests (up from 16)
- Heritage retry cascade generic and verse-independent
- DB-backed lexical_senses table (93 entries, tradition-aware)
- Holdout sealed: 13 internal + 10 challenge (never inspected)

**📊 Defensible rate:**
- 21 development verses with reference alignment
- 19 valid comparisons (2 REFERENCE_ALIGNMENT_ERROR — reference extraction artifacts)
- 19/19 = **100% defensible on valid subset**
- 19/21 = **90% defensible on total evaluated**
- **0 SANSKRITREE_ERROR found**

**Key improvements that transfer:**
- Heritage retry cascade (segmentation recovery)
- DB-backed tradition-aware sense ranking
- Explicit LLM run states and retries
- BlindRunContext for reference isolation

**⏳ Phase 2 — Vijñānabhairava zero-shot transfer:**
Plan at `docs/phase2_vijnanabhairava.md`
- Freeze CP1 pipeline
- Run 162 verses zero-shot (3 ablations: C0, C1, C2)
- Measure which gains transfer vs overfit

**Commands:**
```bash
# Run candidate recall
PYTHONPATH=src python3 scripts/candidate_recall.py

# Run full-text translation
PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py generate --split development

# Run tests
PYTHONPATH=src python3 -m unittest tests.test_pipeline tests.test_spanda_benchmark tests.test_translation_audit -v
```

The most important rule: **blind translate first, compare after.** If you peek at the references before generating, the whole evaluation is contaminated.
