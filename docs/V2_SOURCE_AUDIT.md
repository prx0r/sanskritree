# Sanskritree V2 source audit protocol

The research brief lists scholarly papers, source portals, GitHub projects, and Hugging Face datasets. They are leads, not automatically redistributable dependencies.

For every external source before download or ingest, record:

1. canonical URL and retrieval timestamp;
2. work, edition, witness, translator, and exact source page where applicable;
3. licence and redistribution permission;
4. text date/domain and normalisation/transliteration scheme;
5. checksums for downloaded artefacts;
6. whether translations, notes, commentary, apparatus, and generated annotations are separated;
7. contamination and benchmark-split risks.

Priority integration order is: (1) V2 pilot source with explicit permission, (2) DCS/Heritage/Vidyut cross-analysis, (3) MITRA/Mitrasamgraha retrieval and translation data after card audit, (4) Tantric editions and translations after bibliographic/licence review, (5) Lean ecosystem tools after toolchain compatibility confirmation. Corpus-scale downloads are intentionally deferred: the container has ~17 GB free and the listed Sanskrit corpus alone is potentially too large for an unreviewed import.

The precise link inventory and implementation mapping belongs in `docs/V2_RESEARCH_MAP.md` as each source is checked; no source’s generated fields are treated as ground truth.

## Initial availability checks — 2026-07-23

- MITRA (arXiv 2601.06400) is available as a parallel corpus/model and semantic-retrieval resource. It is an appropriate retrieval evaluation candidate, but Buddhist domain coverage must remain distinct from Tantric calibration.
- Mitrasamgraha (arXiv 2601.07314) reports 391,548 Sanskrit–English pairs and explicitly retains compounds, philosophical concepts, and multilayered metaphor as difficult cases. It is a calibration candidate, not a source of target-text ground truth.
- `CodeIsAbstract/sanskrit-morpho-sequences` is available as an approximately 82 MB Parquet resource with 710,785 sentence rows and a declared CC BY-SA 4.0 combined licence. It can fit on this volume, but its SLP1 representation and its upstream attribution/share-alike obligations require a dedicated importer and provenance record before download.
- Pantograph’s repository confirms its Lean 4 REPL/environment-inspection role and Apache-2.0 licence. The existing checkout is retained; toolchain installation must match its checked-in `lean-toolchain` before activation.
