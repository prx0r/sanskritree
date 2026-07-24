# Sanskritree Handover

## What this project is

Sanskritree is a **machine-assisted critical translation laboratory** for Sanskrit Tantric texts. It combines multiple analysis engines (Vidyut, Heritage, ByT5), a factor graph for selecting among competing analyses, a constrained English renderer, and a Lean-based structural auditor.

The core thesis: structured philological inference (segmentation → morphology → compounds → semantic frames) produces more auditable and defensible translations than giving an LLM the same evidence — and the audit trail enables scholarship that a raw LLM output cannot.

## Where we are right now

**Current state (v0.4):**
- 5 works ingested (MBT, Bhairavastava, Spandakārikā, Bhagavad Gītā, Vijñānabhairava)
- 8,890 passages, 136K hypotheses, 6K lexemes
- 511 adjudications, 120-passage benchmark
- 4-system comparison: C (Sanskritree) beats B2 (retrieval LLM) 24/30 (80%)
- Frame selection errors reduced 83% (6→1)
- D publication gate: PASS/REJECT with 100% mutation detection

**Key files:**
| File | Purpose |
|------|---------|
| `src/sanskritree/inference/factor_graph.py` | Factor graph core (beam search, variables, assignment) |
| `src/sanskritree/inference/factors.py` | 5 factors: agreement, compound, frame, unsupported_addition, action_detection |
| `src/sanskritree/inference/propagation.py` | Damped synchronous logit propagation |
| `src/sanskritree/inference/scoring.py` | Per-factor score decomposition |
| `src/sanskritree/semantics/ritual_frames.py` | 16 action types + detect_action() keyword mapping |
| `proof/translation_pilot_v1.json` | 30-passage benchmark (being expanded to 120) |
| `proof/recall_ci_v03.json` | Candidate-recall CI report |
| `proof/v04_evidence_bundles.json` | A2/B2/C/D outputs for B2-vs-C experiment |

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

**4. Passage IDs don't match between benchmark and DB**
The pilot uses short IDs like `bv.1` but the DB uses full IDs like `bhairavastava.1`. The fix was applied in v0.3 — the recall CI now uses canonical DB IDs. If you regenerate the pilot, it uses DB IDs.

### Spandakārikā: current state

- 53 verses in DB
- 67% token coverage (163/246 tokens)
- 41 commentary blocks linked via 370 passage_relation links
- 3 ALL_ENGINES_MISS verses fixed via staged fallback
- Remaining low-coverage: 8 verses with ≤1 lemma (mostly VB rare vocabulary)

**The 3 ALL_ENGINES_MISS verses that were fixed:**
- `sp.1.5` (na cāsti mūḍhabhāvo'pi) — now has `seeded` hypotheses
- `sp.3.4` (niyacchan bhoktṛtām eti) — now has `seeded` hypotheses  
- `sp.3.9` (same as 3.4 — duplicate in pilot)

**To push coverage higher:** Run Heritage retry on the 8 low-coverage verses. The web API is flaky but usually works on retry. Each verse takes ~2-5s.

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
| Evaluation tables | `scripts/t2_ab_evaluation.py` |
| Candidate CI | `scripts/recall_ci.py` |
| B2 vs C experiment | `scripts/v04_experiment.py` |
| Lean modules | `lean/Sanskritree/Decision.lean`, `LayerB.lean` |
| All reference docs | `ref/README.md` (there's a decision tree) |
| Checkpoint 1 plan | `docs/guidenow.md` |

### The actual execution for this week

If I were picking this up right now, I would:

1. **Day 1:** Run `recall_ci.py` to get baseline coverage. Run `v04_experiment.py --report` to see the B2 vs C comparison. Read `docs/guidenow.md` carefully.
2. **Day 2:** Ingest reference translations for Spandakārikā. Dyczkowski and Singh are the two main ones. Add them to the DB with verse-level alignment.
3. **Day 3:** Run blind translation on all 53 verses. Save everything. Don't look at references yet.
4. **Day 4:** Compare against references. Classify disagreements. Find the top 3 systematic error classes.
5. **Day 5:** Fix the #1 error class. Re-run blind translation. Measure improvement.

The most important rule: **blind translate first, compare after.** If you peek at the references before generating, the whole evaluation is contaminated.
