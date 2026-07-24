# Vision Others — Peer Review of External Tools and Standards

> Sanskritree is an integration, adjudication, and verification layer, not another parser or corpus host.

## Current stage

Research Kernel v0.1 frozen, 511 BRONZE adjudications, 30-passage pilot, 5 passages evaluated, C/D comparison scaffolded, A/B LLM baselines not yet integrated.

**Chief uncertainty: does Sanskritree actually improve translation accuracy and reduce expert work?**

## Verdicts on proposed tools

| Tool | Verdict | Action |
|------|---------|--------|
| **Lean** | ✅ Accept now | Finite projection of accepted data; certificate over deterministic manifest |
| **STAM** | ⚠️ Pilot later | Build a round-trip experiment after T3/T4; do not migrate now |
| **STAM-Translate** | ⚠️ Evaluate | Eventual serialization for T3 translation alignments |
| **Ambuda TEI** | ⚠️ Use selectively | Build import manifest with licence status; after translation pilot |
| **GRETIL TEI** | ⚠️ Keep present corpus | Add manifests and validation incrementally; heterogeneous data |
| **DCS** | ⚠️ Limited scope | Only exact or reviewed normalized matches enter candidate lattice |
| **Vidyut** | ✅ Retain | Fast independent candidate source; measure per task |
| **Universal Dependencies** | ❌ Defer | Domain mismatch with Tantric technical verse |
| **Tesserae** | ❌ Reject as dependency | Reproduce scoring method first; methodological precedent only |
| **AIF** | ❌ Defer | First annotate 10-20 arguments in minimal format |
| **Nanopublications** | ⚠️ Adopt shape now | Internal assertion/provenance/publication structure; defer RDF publication |

## Recommended treatment of STAM

Do not migrate the current kernel. Build a small round-trip experiment:

- One work, 30 pilot passages, existing spans, hypotheses, adjudications, alignments
- Test: PostgreSQL → STAM JSON → PostgreSQL
- Required: zero source/provenance/adjudication loss, deterministic IDs, acceptable performance
- Then decide: interchange format, annotation library, or canonical representation?

## GRETIL TEI caution

GRETIL TEI should be treated as **heterogeneous imported data**, not a clean universal schema. The README notes subsequent work correcting files to make them valid XML and TEI. Validate per file: XML well-formed? TEI schema valid? work identity resolved? verse structure reliable? licence known?

## DCS alignment statuses

DCS analyses must be aligned to the exact Sanskritree edition. Use:
- DCS_EXACT_SPAN_MATCH
- DCS_NORMALIZED_MATCH
- DCS_APPROXIMATE_MATCH
- DCS_UNALIGNED

## Vidyut experimental modules

`vidyut.cheda` segmentation and `vidyut.sandhi` are marked as experimental in current documentation. Vidyut supplies a fast independent candidate source whose output must be measured per task — not assumed reliable.

## Clean architecture for present stage

```
PostgreSQL (canonical)
├── corpus passages, parser hypotheses, factor scores
├── adjudications, semantic plans, translation outputs
├── evaluations, errors, post-edits

R2 (storage)
├── immutable datasets, corpus snapshots
├── benchmark outputs, release bundles

Lean
└── generated finite manifests and certificates
```

Standards through adapters, not migration: PostgreSQL → export STAM pilot, TEI release, CoNLL-U, claim JSON, Lean manifest.

## Immediate development plan

### T3.1 — Finish error-origin schema
Every translation error records: passage_id, output_id, source span, English span, error type, severity, corrected English, responsible stage, responsible hypothesis IDs, correct candidate present?, selected candidate correct?, semantic plan correct?, renderer faithful?, Lean detectability, reviewer confidence.

Origin enum: SOURCE_IMPORT, NORMALIZATION, SEGMENTATION, MORPHOLOGY, COMPOUND_GENERATION, COMPOUND_RANKING, SYNTAX, LEXICAL_SENSE, FRAME_SELECTION, FRAME_ROLE, SEMANTIC_PLAN, RENDERER, EVIDENCE_POLICY, UNKNOWN, MULTIPLE.

### T3.2 — Causal diagnostic decision tree
For every major/critical error:
```
Was correct output in semantic plan?
├── yes → renderer failure
└── no → Was correct candidate generated?
    ├── yes → ranking/propagation failure
    └── no → candidate-generation or source failure
```

### T3.3 — Integrate systems A and B
A: plain LLM. B: evidence-assisted LLM without graph selection. Freeze model, prompt, temperature, context window, retrieved evidence, seed, date, provider.

### T3.4 — Complete full 30-passage review
Capture: blind pairwise preference, critical/major/minor errors, post-edit, error origin, candidate presence, Lean detectability, review time.

### T3.5 — Produce first causal report
Partition errors into: correct candidate absent, correct candidate lost, correct analysis but wrong plan, correct plan but wrong rendering, correct but awkward, unsupported content caught by audit, unsupported content missed by audit.

## Decision rules after 30 passages

| Condition | Action |
|-----------|--------|
| Candidate-absence errors common + Heritage timeouts explain share + local stress test retrieves candidates | Build local Heritage |
| Correct candidate exists but FactorGraphV2 selects wrong one | Train ranker |
| Morphology/structure correct but technical lexical interpretation fails | Expand lexical senses |
| Actions/participant roles systematically wrong | Improve frames |
| Semantic plans correct but English distorts | Improve rendering |
| Structural error formally detectable but passes certification | Expand Lean audits |

## Revised sequence

```
NOW
├── T3 error-origin pipeline
├── integrate A/B LLM baselines
├── finish all 30 evaluations
├── Translation Quality Report v0.1
▼
DIAGNOSIS (candidate generation? ranking? frames? rendering? audit?)
▼
ONE TARGETED IMPROVEMENT (local Heritage / ranker / senses / renderer / Lean)
▼
RERUN FROZEN 30
▼
Expand benchmark to 120
▼
STAM round-trip pilot
▼
Commentary intervention vertical slice
▼
Claim publication / nanopublication export
```

The clean next milestone is not "Ambuda → STAM → nanopublication." It is: **complete the 30-passage controlled comparison, trace every consequential error to its originating pipeline stage, make one evidence-driven technical improvement, and prove on the frozen benchmark that translation quality improved without weakening the Lean audit.**
