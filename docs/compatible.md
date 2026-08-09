# Sanskritree Compatibility Architecture

## Principle

Use existing projects as authorities for the things they already do well.
Sanskritree adds translation, lexical senses, linguistic annotations, confidence,
and cross-resource resolution. Do not import everything into one giant proprietary
schema. Build a federated registry with source adapters and external identifiers.

## What each resource should do for Sanskritree

| Resource | Use for | Access | Don't use for |
|----------|---------|--------|---------------|
| SARIT | Structured texts, editions, root/commentary | Public Git, TEI XML | Universal bibliography |
| GRETIL | Broad Sanskrit e-text corpus | Public Git mirror, TEI XML | Fully reliable classifications |
| Muktabodha | Tantra, Śaiva, Śākta, Āgama texts | Searchable e-texts | Unlicensed bulk harvesting |
| PANDiT | Works, people, dates, relationships | Stable web records | Full-text corpus |
| UCCIK/NCC | Variant titles, authors, classifications | Searchable database | Machine-readable text |
| DCS | Lemmas, morphology, segmented Sanskrit | Annotated corpus | Work-level authority |
| Sanskrit eBooks | Scans of missing editions | PDFs/torrents | Canonical metadata |

## Acquisition levels

- Level 1: Ingest directly — SARIT, GRETIL, downloadable datasets
- Level 2: Link and reconcile metadata — PANDiT, UCCIK, Sangrah/Samagra
- Level 3: OCR only when no e-text exists — Sanskrit eBooks, Archive.org, manuscript scans

## Entity model

WORK → PART → EXPRESSION → MANIFESTATION → ITEM

Relationships: COMMENTARY_ON, SUBCOMMENTARY_ON, TRANSLATION_OF, EDITION_OF,
QUOTES, ATTRIBUTED_TO, BELONGS_TO_TRADITION

## Provenance principle

Every claim needs source, retrieval date, confidence, status.

Bad: `{ "date": "900" }`
Good: `{ "value": {"earliest": 900, "latest": 975}, "source": {"provider": "pandit"}, "status": "IMPORTED_ASSERTION" }`

## Adapter architecture

```
src/sanskritree/federation/
├── base.py
├── registry.py
├── reconciliation.py
├── provenance.py
└── adapters/
    ├── sarit.py
    ├── gretil.py
    ├── muktabodha.py
    ├── pandit.py
    ├── uccik.py
    ├── dcs.py
    └── sanskrit_ebooks.py
```

## Standards

- Textual structure: TEI P5
- Linguistic annotation: Universal Dependencies / CoNLL-U
- Language/script: BCP 47 tags (sa-Deva, sa-Latn)
- Transliteration: ISO 15919 internally
- Bibliography: CSL JSON/BibTeX

## Implementation sequence

1. PR 17 — Standards and entity model
2. PR 18 — SARIT importer
3. PR 19 — GRETIL importer
4. PR 20 — Source resolver
5. PR 21 — External metadata mappings
6. PR 22 — Muktabodha collaboration adapter
7. PR 23 — Linguistic interchange
