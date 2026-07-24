# Spandakārikā Translation Pipeline — Checkpoint 1

## Design Principle

> The system improves by being wrong in measurable ways. Every translation disagreement with a reference is a training signal. Without reference translations, there is no signal.

## Pipeline Overview

```
1. INGEST
   Sanskrit text (GRETIL IAST)
   Multiple English translations (aligned verse-by-verse)
   Commentary (if available)
   
2. BLIND TRANSLATE
   Sanskritree produces translation WITHOUT seeing any reference
   → morphology → factor graph → semantic plan → render → Lean audit
   
3. COMPARE
   Verse-by-verse: Sanskritree vs Reference A vs Reference B vs Reference C
   For each pair: classify every disagreement
   
4. ANALYZE
   Error taxonomy: textual, grammatical, lexical, doctrinal, stylistic
   Trace each error to pipeline stage
   
5. IMPROVE
   Feed disagreements back: fix ranking, add vocabulary, improve rendering
   
6. REPEAT
   Re-run blind translation → measure improvement
```

---

## Step 1: Reference Ingestion

For each reference translation, store:

```json
{
  "translator": "Mark Dyczkowski",
  "work": "Spandakārikā",
  "year": 1992,
  "alignment": "verse",
  "rights": "copyrighted_internal",
  "verses": {
    "1.1": "We praise that Śaṅkara...",
    "1.2": "..."
  }
}
```

Build an alignment table that maps each Sanskrit verse ID to all available translations.

## Step 2: Blind Translation Protocol

**Critical rule:** The Sanskritree pipeline must NOT access any reference translation during generation.

The blind run creates a frozen record:
- Sanskrit input
- Morphology candidates
- Factor graph selection
- Semantic plan
- English output
- Lean certificate
- Timestamp + version

This record is immutable. If we improve the pipeline and re-run, the old record stays for comparison.

## Step 3: Comparison Engine

For each verse, for each pair (Sanskritree vs Reference):

```json
{
  "verse": "1.1",
  "sanskritree": "...",
  "reference_a": "...",
  "reference_b": "...",
  "agreements": ["verb choice", "subject identification"],
  "disagreements": [
    {
      "type": "LEXICAL_SENSE",
      "span": "śakti",
      "sanskritree": "power",
      "reference_a": "Energy",
      "reference_b": "Energy",
      "probable_cause": "trika_lexicon_not_loaded"
    }
  ],
  "errors": []
}
```

## Step 4: Error Taxonomy

```
TEXTUAL        — different source reading
GRAMMATICAL    — case, tense, person, number
COMPOUND      — compound boundary or relation
LEXICAL       — word sense
DOCTRINAL     — tradition-specific interpretation
STYLE         — natural vs literal wording
COMMENTARY    — commentary influence
OMISSION      — content missing
ADDITION      — unsupported content
AMBIGUITY     — genuinely ambiguous, both defensible
```

## Step 5: Learning Loop

Every disagreement is a potential training example:

- **Lexical disagreements** → improve sense ranking
- **Compound disagreements** → improve compound parsing
- **Grammatical disagreements** → improve factor graph features
- **Style differences** → improve rendering

## Step 6: ML Integration

Build a disagreement database:

```
disagreement_id | verse | system | reference | error_type | pipeline_stage | feature_vector | resolved?
```

When we have enough (500+), train:
- Ranker: given features, which candidate does the reference prefer?
- Renderer: given semantic plan, which English phrasing matches scholarly style?

## Implementation Order

1. Ingest Spandakārikā text and Dyczkowski translation (already have)
2. Add Singh/Kṣemarāja-based translations if available
3. Build blind translation runner (already have `t1_translation_pilot.py`)
4. Build comparison/analysis scripts
5. Run on all 53 verses
6. Classify disagreements
7. Fix top 3 systematic error classes
8. Re-run blind, measure improvement

## Reusable Across Texts

The same pipeline works for any text with:
- Clean IAST Sanskrit (via GRETIL)
- One or more English translations
- Verse-level alignment

To add a new text:
```bash
python3 ingest_text.py --sanskrit text.txt --references refs.json
python3 blind_translate.py --work new_text
python3 compare.py --work new_text --references refs.json
python3 analyze.py --work new_text
```
