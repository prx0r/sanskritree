# Checkpoint 1 — Ingestion Workflow for Next Agent

## Primary Text: Spandakārikā (53 verses)

Already ingested. Ready for translation pipeline.

### Current status
- 53 verses in DB at 67% coverage
- 41 Kṣemarāja commentary blocks, 370 passage_relation links
- Multiple English translations exist (Dyczkowski, Singh, etc.)
- **Missing**: aligned English reference translations in the DB

### Step 1: Ingest reference translations

The key gap is that we have Dyczkowski's English in the `translations` table for the MBT, but NOT for the Spandakārikā. We need to add reference translations.

For each reference translation, create a manifest entry:

```yaml
passages:
  - id: "spk.1.1"
    translations:
      - translator_id: "dyczkowski.mark"
        type: "published_reference"
        text: "We praise that Śaṅkara who is the source..."
        source_page: "p.74"
```

Translation data rights: Dyczkowski's translation is copyrighted — use for internal evaluation only. Publish only short excerpts, metrics, and Sanskritree's own translation.

### Step 2: Select dev/holdout split

```
Development: 35 verses (indices 0-34)
Frozen holdout: 18 verses (indices 35-52)
```

Save in `data/manifests/spanda_dev_split.json`.

### Step 3: Run blind translation

```bash
PYTHONPATH=src python3 scripts/t1_translation_pilot.py --work spandakarika --verses 53
```

This generates the Sanskritree translation for all 53 verses.

### Step 4: Compare and classify

For each verse, compare Sanskritree output against each reference translation. Classify every disagreement as:

```
SANSKRITREE_ERROR
REFERENCE_DEPENDENT_READING
REFERENCE_INTERPRETIVE_EXPANSION
BOTH_DEFENSIBLE
TEXTUAL_VARIANT
UNRESOLVED
```

### Step 5: Fix and repeat

Identify top 3 systematic error classes. Fix the pipeline component responsible. Re-run blind translation. Measure improvement against holdout.

---

## Secondary Text: Vijñānabhairava (162 verses)

Already ingested at 40% coverage. Multiple translations exist (Dyczkowski, Singh, Wallis, Odier).

Use only AFTER Spandakārikā pipeline is stable. The 40% coverage means significant vocabulary work needed first (Heritage/ByT5 batch on remaining verses).

---

## Tertiary Text: Bhairavastava (9 verses)

Already ingested at 90% coverage with gold corpus status. Too short for a complete-text milestone but excellent for quick validation of pipeline changes.

---

## Data Sources (from ref/sourceref.md)

| Source | Best for | Access |
|--------|----------|--------|
| GRETIL | Clean IAST texts | Public |
| Ambuda | Browser-readable Sanskrit | Public |
| Muktabodha | Śaiva/Śākta Tantra texts | Some require access |
| Archive.org | Printed editions, rare texts | Public (KSTS, TSS) |

## Key Files for Next Agent

| File | What it does |
|------|-------------|
| `docs/pipeline_checkpoint1.md` | Full pipeline specification |
| `docs/immediatevision.md` | Strategic rationale |
| `HANDOVER.md` | Project onboarding |
| `scripts/t1_translation_pilot.py` | Benchmark generation (adapt for full-text) |
| `scripts/recall_ci.py` | Candidate-recall CI |
| `scripts/t2_ab_evaluation.py` | A/B comparison + error annotation |
| `scripts/v04_experiment.py` | B2-vs-C experiment framework |
| `proof/translation_pilot_v1.json` | Current benchmark data |

## Quick Start

```bash
# 1. Check Spandakārikā coverage
PYTHONPATH=src python3 scripts/recall_ci.py | grep spanda

# 2. Run candidate-recall CI
PYTHONPATH=src python3 scripts/recall_ci.py

# 3. Run pipeline tests
PYTHONPATH=src python3 -m unittest tests.test_pipeline -v

# 4. Build Lean
cd lean && lake build Sanskritree && cd ..

# 5. Generate blind translation
PYTHONPATH=src python3 scripts/t1_translation_pilot.py
```

## Spandakārikā-Specific Commands

```bash
# Check per-verse coverage
PYTHONPATH=src python3 -c "
from pathlib import Path; import sys
sys.path.insert(0, str(Path('/root/projects/sanskritree/src')))
from sanskritree.database import connect
conn = connect(str(Path('/root/projects/sanskritree/data/sanskritree-v2.db')))
for r in conn.execute('''
    SELECT p.verse_start, p.sequence_index,
           (SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            LEFT JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
            WHERE tocc.passage_reading_id IN (SELECT reading_id FROM passage_readings WHERE passage_id=p.passage_id)
            AND mat.lexeme_id != '' AND mat.lexeme_id != 'lex_unknown') as covered_tokens,
           (SELECT count(*) FROM token_occurrence tocc2 WHERE tocc2.passage_reading_id IN
            (SELECT reading_id FROM passage_readings WHERE passage_id=p.passage_id)) as total_tokens
    FROM passages p WHERE p.work_id='spandakarika' AND p.passage_type='verse'
    ORDER BY p.sequence_index
''').fetchall():
    pct = r[2]/max(r[3],1)*100
    print(f'  [{r[1]:2d}] v{r[0]:3s}: {r[2]:2d}/{r[3]:2d} ({pct:.0f}%)')
conn.close()
"
```
