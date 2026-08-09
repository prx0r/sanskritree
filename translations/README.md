# The Translation Pipeline

*The pipeline organizes the lab's work into phases. Every text enters at phase 01 and moves rightward as it is processed. A text is "final" only at T3; C1 is its plain-English interpretation. The status board (`STATUS.md`) is the live registry — update it whenever a phase completes.*

## The flow

```
01_t1_working → 02_r1_review → 03_t2_alternate → 04_r2_adjudication → 05_t3_final → 06_c1_interpretation
   T1              R1               T2                  R2                 T3              C1
 (the first     (the peer       (the fresh,         (the full-        (the final      (the plain-
 translation)    review,        alternative-         reasoning-        synthesis)      English
                 varieties,     reading, blind       chain adjudi-                     interpretation,
                 verdicts)      of T1's sentences)   cations)                          lean register)
```

## Folder map

| Folder | Phase | Contents |
|--------|-------|----------|
| `00_legacy/` | pre-pipeline | the earlier phases' works (kept in place: see STATUS) |
| `01_t1_working/` | T1 | the working translations (18 files, 15 works) |
| `02_r1_review/` | R1 | the peer-reviews (7 files) |
| `03_t2_alternate/` | T2 | the alternative-reading translations (7 files) |
| `04_r2_adjudication/` | R2 | the full-reasoning-chain adjudications (7 files) |
| `05_t3_final/` | T3 | the final syntheses (7 files) |
| `06_c1_interpretation/` | C1 | the plain-English interpretations (6 files) |
| `_meta/` | cross-cutting | the protocol, the glossary, the audits, **REF_NOTES (the craft)** |

## Expansion rules

1. **A new text enters at `01_t1_working/`** with the naming `{text}_{scope}_{phase}.md` (e.g. `newtext_patala1_pass1.md`), its provenance header, time-place-context block, and [X]-flags per PASS_PROTOCOL.
2. **It progresses rightward** — each phase's doc goes in that phase's folder; the phase-names in the filenames stay (they make cross-phase navigation trivial).
3. **A new phase** (e.g. C2, the comparative commentary) gets a new numbered folder (`07_c2_...`) — the numbering is the pipeline's backbone.
4. **Update `STATUS.md`** at every phase-completion: the text's row, the phase column, the file reference.
5. **The craft-reference** (`_meta/REF_NOTES.md`) — the attitude per pass, the context-stack, the gems, the objectivity protocol. Read it before every session.
5b. **The self-review** (`_meta/SELF_REVIEW.md`) — the per-layer audit; apply its fixes before expanding.
6. **No silent edits**: a correction to any phase's reading lives in the next phase's doc or the audits in `_meta/` — never an in-place rewrite of an earlier phase.
6. **The strategic docs stay put** (the atlas, the flow spec, the flaws audit, START_HERE, the lab index at the repo root) — the pipeline is the production line; the strategic docs are the control room.

## Where the rest lives

- The **anchors and evidence**: `sources/round2/` + `/root/projects/tantraloka/texts-clean/` + the reference list in `corpus/targets/round2_sources.md`
- The **corpus**: `sources/muktabodha-lib/` (499 texts)
- The **strategy**: `corpus/targets/translation_atlas.md` + `corpus/targets/translation_flow_spec.md` + `corpus/targets/atlasflaws.md`
- The **master index**: `TRANSLATION_LAB_INDEX.md` (repo root)
