# Sanskritree Audit — 2026-07-24

## Codebase
- 47 source files (src/)
- 13 test files (59 passing)
- 48 scripts
- ~2.2MB project size

## Database (sanskritree-v2.db, 351MB)
- 40 tables
- 136K token analysis hypotheses
- 6K lexemes
- 16K morph analysis types
- 169K token occurrences
- 8.8K passages across 5 works
- 511 morphology adjudications
- 43 translation runs

## Coverage
| Work | Verses | Covered | Rate |
|------|--------|---------|------|
| Bhairavastava | 9 | 9 | 100% |
| Spandakārikā | 53 | 52 | 98% |
| Vijñānabhairava | 162 | 160 | 99% |
| Bhagavad Gītā | 3089 | 1138 | 37% |

## Candidate Engines
| Engine | Hypotheses |
|--------|-----------|
| vidyut | 135,781 |
| heritage | 600 |
| heritage_hc (hardened) | 94 |
| heritage_retry | 62 |
| byt5 | 11 |

## Lexical Senses
- 93 total (46 SPANDA_TRADITION, 43 GENERAL_SANSKRIT, 4 PAN_SAIVA)
- C0/C1/C2 ablation scopes implemented

## Benchmarks
- spanda_v1: 53 passages (frozen)
- vijnanabhairava_v1: 162 passages (frozen)

## Runs
- 2026-07-24_pass-1_spandakarika: 53 verses, factor graph + LLM rendering
- 2026-07-24_dev-spanda: analysis manifests for 30 dev verses
- Phase 2 VB C2 render: in progress (~18/80 dev verses done)

## Release Gates
- ✅ R@5 = 98.8%
- ✅ Critical errors = 0
- ✅ Major errors = 0 (2 REFERENCE_ALIGNMENT_ERROR excluded)
- ✅ Defensible rate = 90% (100% on valid comparisons)
- ✅ 59 tests passing
- ✅ Heritage transport hardening applied
- ⏳ Phase 2 VB zero-shot transfer in progress
- ⏳ C0/C1/C2 ablation rendering
- ⏳ Singh reference acquisition

## Key Files (SHA256)
- CHECKPOINT1_REPORT.md: e70668bb78a1aaa6
- SPANDAKARIKA_TRANSLATION_V1.md: e35e0d5558ff2f97
- HANDOVER.md: f8bcc01ddf634bc9
