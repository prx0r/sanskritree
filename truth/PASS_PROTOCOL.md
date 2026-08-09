# Pass Protocol — how pass-1 translations are built and how pass 2 validates them

*The translation pipeline runs in passes. Pass 1 = working translations, produced in context-groups, with reasoning embedded. Pass 2+ = validation, correction, deepening (three-readings treatments, divergence tables, collation). This file defines the conventions so any agent can follow the reasoning and correct it.*

---

## 1. How a pass-1 file is structured

Every pass-1 file contains:

1. **Header (provenance)** — text, author, dates, edition, digital source, anchor translation held on disk. If an anchor exists, the file says so and names it. If not (first translation), it says so explicitly.
2. **Working translation per verse** — one careful translation, not three (three-readings treatments are pass 2+).
3. **Notes** — where the reasoning lives. Three kinds of note:
   - **Grammar note**: sandhi/compound/case/voice justifications ("jagadākhyātaṃ — nom. sg. n., predicate of tadeva").
   - **Vocabulary note**: why a specialist term was rendered so, with cross-corpus evidence (e.g., "nirañjana = stainless + unmanifest, per TĀ 3.172/Dyczkowski vol. 2").
   - **Anchor note**: what the published translation on disk says (quoted or cited), when it disagrees.
4. **[X] flags** — provisional readings, doubtful edition passages, variants. An [X] is an admission: "I could not settle this from the material on disk."

## 2. Reasoning conventions (what counts as a justified choice)

A translation choice is **justified** if it cites one of:

- **(G)** grammar: the form itself (case, number, voice, compound type) — cite it.
- **(P)** parallel usage: the same term rendered the same way in another text of the same period in our corpus — cite the text.
- **(A)** anchor: the published translation on disk agrees or is knowingly diverged from — cite the divergence ("Dyczkowski renders X; I render Y because [G/P]").
- **(R)** reconstruction: interpretation not directly forced by the text — must be labeled as such and kept separate from [G] claims.

A choice is **unjustified** if it is pure paraphrase without any of the above. Pass 2 should flag it.

## 3. The pass-2 validation workflow (for the next agent)

For every verse in a pass-1 file:

1. **Re-derive from the Sanskrit.** Re-do the sandhi, the compound analysis, the case relations. If the pass-1 reading survives independently, mark `✓ derived`.
2. **Check against the anchor** (when one exists). Open the anchor file, find the verse, compare. Differences are not automatically errors — but each difference must be explainable by [G]/[P]/[R]. If it isn't, correct it.
3. **Resolve [X] flags.** For each flagged item, either (a) settle it from another edition/manuscript (record which), (b) settle it from a parallel passage, or (c) keep the flag with an added note on what evidence is missing.
4. **Record corrections, never rewrite silently.** Append a correction block to the file:

```
## Pass 2 corrections (YYYY-MM-DD)
| Verse | Pass-1 reading | Correction | Reason (G/P/A/R + evidence) |
|-------|----------------|------------|------------------------------|
```

5. **Update the glossary.** When pass 2 settles or changes a specialist term's rendering, update the relevant `period-glossary-*.md` (create if absent).

## 4. What pass 2 must NOT do

- Do not "improve" translations cosmetically — only correct on evidence.
- Do not remove [X] flags without recording the resolving evidence.
- Do not merge the three readings (in pass 2+ files) — they stay separate.
- Do not trust the anchor blindly: anchors are diagnostic, not ground truth (their editions differ from ours; their readings are themselves interpretations).

## 5. Status vocabulary

| Status | Meaning |
|--------|---------|
| `✓` | verified: derived independently from Sanskrit + anchor agreement |
| `[X]` | provisional: awaiting collation/parallel evidence |
| `[R]` | reconstruction: interpretive, not forced by the text |
| `[D]` | divergent-from-anchor: kept deliberately, reason recorded |

## 6. Cross-file continuity

Specialist terms are tracked across files. When a term appears in a new file, the note should cite its previous renderings (e.g., "nirañjana — see kubjika v2 file, sivasutra file, kaula file"). This is the compounding-context engine: each pass-1 batch extends the vocabulary base for the next batch.

---

## 7. Time-place-context assessment (REQUIRED header block in every pass-1 file)

Every file's header must contain an explicit four-field block, filled before translation begins:

```
### Time-place-context assessment
- PERIOD:        (dating of the text; dating basis; stratification note — which layers the vocabulary belongs to)
- PLACE/PATH:    (region of composition + transmission path: Kashmir / Bengal / Nepal / West-India; script and dialectal markers — e.g., v/b wobbles in Bengali prints, Kashmir unvoiced consonants)
- GENRE/REGISTER:(mantraśāstra / philosophical śāstra / stotra / ritual paddhati / dialogue-frame — the lexical defaults that follow)
- FRAME:         (commentarial frame: which commentary layer we translate against; the author's intertextual web — who quotes whom, which earlier works they cite)
```

**Why:** Sanskrit terms are chronologically and regionally stratified. A 10th-c. Kaula *nirañjana* is not the Buddhist one; a 16th-c. Bengal print of a Kaula text is not a Kashmir codex. The four fields force the translator to state which layer they are reading in, so a pass-2 agent can test it.

## 8. Register conventions (from translation-methodology literature, surveyed 2026-08-09)

Rules adopted from the guides (Stcherbatsky/Rosenberg on philosophical translation; the "three questions" classroom method; śāstra-translation practice; van Bijlert on translating with the original commentary):

1. **Compound-splitting first.** Every compound is resolved and recorded before any rendering (the single most cited error source). Our word-lab tables already do this; pass-2 must verify every split.
2. **Gradual transliteration-acclimation.** First occurrences of a technical term: transliteration + English gloss; later occurrences: transliteration alone (Stcherbatsky's reader-accustoming technique — also the right pattern for the future site).
3. **Technical-term capitalization policy.** Terms functioning as names/principles (Consciousness, the Power, the Stainless) are capitalized; ordinary senses are not. Divergences from Dyczkowski's capitalization are noted.
4. **The commentary is the frame.** No verse is translated without its commentary layer in view (Vṛtti/Vivṛti/Vārttika/Vimarśinī). The three-readings format keeps root and commentary separate; pass-2 checks that no commentarial content leaks into the "literal" reading.
5. **The three-questions test** (what should the reader be able to *do* with this translation?): every file states its intended use — e.g., "working translation for later scholarly verification" (pass 1) vs "teaching/display" (site, later).
6. **Essence-vs-context polarity.** The literal reading serves Stcherbatsky (the thought), the doctrinal reading serves Rosenberg (the cultural/commentarial context); the gap between them is reported, never collapsed.

## 9. Applying this to the existing pass-1 files

The four pass-1 files written on 2026-08-09 contain time-place-context material inside their provenance headers but not as the structured four-field block. Pass 2 must add the block to each (the material is already present; it needs restructuring).
