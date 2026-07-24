# Reference Library — Future Translate Prima Materia

These are the source reference materials, organized by type. Consult these before making decisions about corpus acquisition, architecture, or research direction.

---

## Corpus sources (where to get texts)

| File | What it covers | Use when |
|------|----------------|----------|
| `sourceref.md` | Hugging Face datasets + GRETIL/SARIT/Muktabodha/DSBC/BDRC repositories | Looking for clean e-texts or bulk datasets |
| `targetslogic.md` | 30+ specific GRETIL texts by tradition (Nyāya, Bhartṛhari, Mīmāṃsā, Buddhist logic, Vaiśeṣika, Śaiva) | Targeting a specific logical or philosophical text |
| `archiveref.md` | Archive.org collections (KSTS, TSS, Navya-Nyāya, Gadādhara manuscripts, eGangotri) | Need printed editions/manuscripts unavailable as e-texts |

## Architecture references (how to build the system)

| File | What it covers | Use when |
|------|----------------|----------|
| `graphref.md` | Three coupled graphs, sheaf theory, geometric deep learning, knowledge sheaves, NBFNet, ULTRA | Understanding the theoretical graph architecture |
| `mechanicsref.md` | Factor graphs, 5 subgraphs (G₀–G₄), V3 DB schema, Sanskrit NLP literature (Krishna et al.) | Designing inference algorithms and DB schema |
| `goldfeedback.md` | 14 specific architecture corrections (propagation, exclusion, G1-G4 ordering, Lean corrections) | Validating approach against known pitfalls |
| `factor_graph_spec.md` | Concrete factor graph implementation (7 factor types, energy functions, beam search, Bhairavastava test) | Implementing the factor graph (in `src/sanskritree/inference/`) |

## Strategic planning

| File | What it covers | Use when |
|------|----------------|----------|
| `docs/dev-plan.md` | Full 1,405-line development plan with timelines | Planning next implementation phases |
| `docs/RESEARCH_PROGRAMME.md` | 12-stage text progression (BG → Vijñānabhairava → Krama → Kubjikā → MBT) | Deciding which text to translate next |
| `docs/HANDOVER.md` | Complete project handover (what's built, what's not, key principles) | Onboarding or resuming after break |
| `docs/V2_PROGRESS.md` | Current implementation status by phase | Checking what's done vs pending |
| `docs/V2_BUILD_NOTES.md` | Chronological build log | Understanding what was built when and why |

---

## Session summary (2026-07-24)

**Accomplished:** Pipeline from corpus to Lean verification. 5 works, 8,890 passages, 136K hypotheses, 6K lexemes, 511 adjudications, 28 translation evaluations. v0.2 frozen with frame selection errors reduced 83% (6→1).

**Key lesson:** The evaluation loop works — measure → fix → re-measure. Three fixes applied (ByT5 candidates, action detection, staged fallback). Primary remaining bottleneck: candidate recall for rare Tantric vocabulary (8/30 low-coverage verses).

**Next sprint (v0.3):** LLM baselines (A2/B2), publication gate making D≠C, mutation tests for Lean. Prove Sanskritree beats a strong LLM before any further architecture work.

**Files to pick up for next session:**
- `scripts/recall_ci.py` — candidate-recall CI (needs A2/B2 integration)
- `scripts/t33_ab_comparison.py` — 4-system comparison (needs real LLM calls)
- `proof/translation_pilot_v1.json` — frozen 30-passage benchmark
- `proof/recall_ci_v03.json` — latest candidate-recall report

## Quick decision tree

```
Need a clean e-text?
  ├── Tantric/Śaiva/Śākta? → Muktabodha first (sourceref.md)
  ├── Buddhist? → DSBC first (sourceref.md)
  ├── Nyāya/Mīmāṃsā/grammar? → GRETIL first (targetslogic.md)
  ├── Need TEI XML? → SARIT (sourceref.md)
  └── Not in any of the above? → Archive.org (archiveref.md)

Need to understand the architecture?
  ├── Overall design? → graphref.md
  ├── Inference algorithms? → mechanicsref.md
  ├── Implementation details? → factor_graph_spec.md
  └── What not to do? → goldfeedback.md

Need to plan next work?
  ├── What's the priority? → docs/V2_PROGRESS.md
  ├── What's the full timeline? → docs/dev-plan.md
  ├── Which text to translate? → docs/RESEARCH_PROGRAMME.md
  └── What's been built already? → docs/HANDOVER.md
```
