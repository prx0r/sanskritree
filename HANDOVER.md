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

## What to do next

1. **Coverage push on Spandakārikā** — run Heritage batch on remaining unanalyzed verses, seed rare vocabulary via ByT5
2. **Consecutive translation** — translate all 53 verses, tracking which verses expose new failure modes
3. **Commentary integration** — link Kṣemarāja glosses at span level for verses where commentary disambiguates
4. **Human review loop** — present translations for correction, record error origins
5. **Freeze Checkpoint 1** — publish Spandakārikā v1.0 with complete audit trail
