# The Craft — Reference Notes for the Translation Pipeline

*The accumulated know-how of running the pipeline: the attitude for each pass, how to find context, the techniques that proved themselves, the objectivity protocol, the failure-modes. Written from the 2026-08-09 session — every gem here was earned by an actual catch or an actual mistake. Read before every session.*

---

## 0. The governing attitude

- **A great translation is great context.** The text is not translated in isolation; it is translated *into* the web of everything else (the period, the corpus, the anchors, the scholarship). Context first, words second.
- **You are producing candidates with honesty markers, not verified translations.** The pipeline moves things up the ladder; nothing is "done" until T3, and T3 is still one model's reading until a human and the prints confirm it.
- **Every layer can overturn the layer before.** If a session never corrects an earlier phase, the session was not run properly. The two R2 self-corrections (ŚS 1.7, 3.40 — caught against the anchor) are the model of this.
- **The word "complete" is radioactive.** A text is T3-FINAL only after the full sweep; a "complete" pass-1 is a candidate, not a translation.

## 1. How to find context (the stack, in order)

1. **The period-cluster first** — read the other texts of the same period in the corpus before translating a new one. The 10th-c. Kaula lexicon (the glossary's terms) is the entry ticket.
2. **The glossary** — check every technical term's attested senses (range, not default). If a term is unregistered, register it with its first attestation.
3. **The anchors** — the published translations, quoted, not paraphrased. The Dyczkowski stack is the master; the round-2 sources (Sanderson's Śaiva Age, the Rājataraṅgiṇī) are the period-context.
4. **The TĀ as the doctrinal oracle** — every doctrine in the corpus has a TĀ-treatment; check it (the mātṛkā in TĀ 3–4, the pañcāmṛta in TĀ 29, the four-speech in TĀ 15). The oracle is on disk.
5. **The colophons and the geography** — the Candra-dvīpa, Kāmarūpa, Vārāṇasī of the colophons are the transmission's self-location; the pīṭha-lists map it.
6. **The biographies** — the author's lineage, dates, teachers (the Rājānaka Rāma biography in Dyczkowski's Stanzas is the model; the Matsyendranāth biography — the Kaivarta-origin — explains the fish-myth).
7. **The prints** — the last resort and the only resolution of the [X]-flags. The e-texts are the base; the prints decide.

**The gem:** the cross-text check is the highest-yield context-move. The gamāgame-correction (the KJN 14/136 parallel settling the Akulavīra's misreading) cost nothing and caught a real error. Always ask: does this collocation appear elsewhere in the corpus?

## 2. The attitude per pass

**T1 (the working translation)** — *the builder.* Patient, syntax-bound, every [X] flagged. No heroics; the goal is the honest first pass that R1 can attack. Record the time-place-context block BEFORE translating.

**R1 (the review)** — *the prosecutor.* Assume T1 is wrong somewhere and find where. For each crux-verse: what are the real alternatives? What would the anchor say (quoted, not remembered)? The verdicts are provisional — R2 can overturn them.

**T2 (the alternative-reading)** — *the explorer.* The question is not "what did T1 say?" but **"what else can this mean?"** Re-derive from the IAST; check the compound's other faces (active vs passive, noun vs adjective, genitive vs apposition); check the cross-text; check the register (technical vs plain, ritual vs epistemic). **Engineered agreement is a failure mode** — if T2 agrees everywhere, it was not exploring. The agreement that survives genuine exploration is the hard core — that is the only agreement worth having.

**R2 (the adjudication)** — *the judge.* Full reasoning chains: the form → the grammar → the anchor-quote → the parallel → the doctrine → the verdict. Every divergence is either adjudicated or marked OPEN — nothing dropped. **The judge must be willing to overturn both sides** (the Akulavīra R2 overturned T1 twice and corrected its own earlier adoption once).

**T3 (the final)** — *the surgeon.* Apply the adjudications precisely; carry the OPEN-flags inline; the apparatus (provenance, the R2-summary, the notes) ships with the text.

**C1 (the interpretation)** — *the plain-speaker.* The Dyczkowski-Exposition register: lucid, sharp, no assumed technical prowess. **The anti-slop law applies** (from the essay-writer skill): no NARR-frames ("the image is...", "read plainly"), no meta-commentary, each word carrying. If a sentence tells the reader how to take the content, cut it — the content should take itself.

## 3. The techniques that proved themselves

- **The cross-text parallel as the tie-breaker** — a collocation in a sibling text settles a reading (gamāgame).
- **The title-word split** — "akule vīre" = the title akulavīra in sandhi-split; check the colophon and the text's own compound-patterns before reading a pair.
- **The ring-structures** — a text's question and its answer (Kubjikā 1.2↔9.15, 1.12↔6.67) are the commentary's master-key; find the rings before adjudicating.
- **The emendation-discipline** — three levels: (1) the construal (read the print so it works — mataṃ as "held as" — the cheapest fix); (2) the emendation with the anuprāsa/register as evidence (nirlakṣaṇam); (3) the emendation with the text's epistemology as evidence (yena jñātaṃ). Never emend without the pattern; always carry the print-flag.
- **The anchor-quote** — quoting the anchor verbatim (not from memory) is what caught the ŚS 1.7 and 3.40 self-corrections. Memory is the enemy; the quote is the referee.
- **The register-fork** — most "alternatives" are register, not meaning (technical vs plain, name vs rendered, blunt vs softened). Classify the fork before adjudicating: a register-fork is a note; a meaning-fork is a decision.
- **The [X]-honesty** — a flag upgraded only with evidence, never with patience. The flags are the pipeline's conscience.
- **The hard-core honesty** — report the real agreement count, not the flattering one. The first Akulavīra R2 claimed 14/18 hard-core; the honest re-run found ~10/18 fixed, 2 errors, 4 forks, 2 OPEN. The honest number is the useful one.

## 4. The objectivity protocol (against the flaws)

1. **The self-review bias is real** — the same model reviewing its own work confirms it. Counter: the anchors as the referee (quote them); the T2-exploration (the alternatives forced); the two-model review (a different LLM reading the R2s cold); and — the only real fix — a human pass on one text, which calibrates the whole pipeline's error-profile.
2. **The blind-translation rule** — T2 is composed without re-reading T1's sentences; T1 itself should have been composed before reading the anchors (admitted violation in the early session — the anchors were quoted in; the docs now state this).
3. **The verification coverage must be stated** — every doc carries its coverage ("10 of 78 sūtras anchor-checked"), not an implied completeness.
4. **The error-measurement is the missing number** — sample N verses per anchored text, classify every mismatch (agree/lexical/doctrinal/error), publish the rate. Until it exists, the pipeline's accuracy is unknown, and the docs should say so.
5. **The glossary as range, not default** — a registered default pre-loads every future text; record the attested senses with their contexts (nirañjana: "Stainless" and "Uncoloured," each in its context).
6. **The slop-law** — NARR, NEG, meta-frames, hedging: all forbidden in C1; the essay-writer skill's anti-slop checklist is the law.
7. **Never flatter the corpus** — the "6 complete texts" claim is T1-complete; the language must distinguish candidate from verified at every mention.

## 5. The failure-modes and their signs

| Failure | Sign | Fix |
|---------|------|-----|
| Engineered agreement | T2 agrees everywhere; no forks | Re-derive with "what else can this mean?"; force the register-fork |
| Self-confirmation | R2 never overturns T1 | Bring the anchor-quote; the two-model review |
| Translation-through-corruption | a [X]-verse rendered smoothly | Flag it as reconstruction; the print resolves it |
| Slop in C1 | "The image is...", "read plainly", hedging | The anti-slop checklist; cut meta |
| Glossary echo | a term forced into the default sense | Range-not-default; the context-check |
| Unstated coverage | "P2 complete" for 10% checked | The coverage-line in every doc |
| Missing OPENs | no verse marked OPEN in a whole text | An OPEN-free text is suspicious — the interpretation-space exists |

## 6. The session-rhythm that works

1. Read the STATUS board and the atlas's run-logs (where is everything?).
2. Re-read the glossary + the relevant _meta docs (the audit backlog).
3. Pick one text-group; read its T1, R1, T2 in sequence (the context is hot).
4. Run the next phase; update STATUS; commit with the phase in the message.
5. Record the gems and the mistakes in this doc — the craft grows with the corpus.

*The last line of the craft: a translation is only as good as the evidence it cites, and the evidence is only as good as the honesty of the record.*
