# Manthānabhairavatantra pilot audit

## Local supplied source

- Archive: `sources/Manthanabhairavatantram Kumarikakhandah_ The section -- Mark Dyczkowski -- d43562aff914418103f70f0175695938 -- Anna’s Archive.zip`
- User confirmed permission for Sanskritree use on 2026-07-23.
- SHA-256: `ff929b10809b334c5f22cbb6a01c4f01c19062f42eb1b46593f9ea4257ba1803`
- Contents: `Text and Translation.pdf` (3,655 pages) and `Introduction Volume.pdf` (1,874 pages).

## Candidate pilot

The smallest coherent calibration unit begins with **Kumārikākhaṇḍa, Chapter 1, “Śrīnātha's Inquiry”**. PDF page 17 contains Sanskrit verses 1–4 and PDF page 18 contains the aligned Dyczkowski translation; the following page pair continues the inquiry. This is appropriate for source/translation/commentary separation and blind–reveal evaluation.

## Ingestion decision: blocked pending a faithful Sanskrit representation

The English layer extracts cleanly. The Sanskrit PDF text layer is encoded through a legacy embedded font and extracts as glyph-code text rather than IAST or Unicode Devanāgarī. The available renderer produced a blank Sanskrit page, and installed OCR has no Sanskrit language model. Therefore V2 must not ingest the extracted glyph stream as a Sanskrit reading.

## Follow-up font diagnosis

The Chapter 1 Sanskrit page declares `TimesNewRomanPSMT`, with neither an embedded font program nor a Unicode map. Its extracted ASCII-like stream is consistent with a legacy Devanāgarī-font workflow, but it cannot safely be identified as standard Kruti Dev from this PDF alone. A generic Kruti Dev converter is therefore only a hypothesis and must not be applied corpus-wide without calibration against a known source reading.

The reliable recovery workflow is:

1. acquire the original font or authoring source from the editor/publisher and create a font-specific Unicode mapping;
2. validate that mapping on the printed Chapter 1 heading and a manually checked set of at least 50 grapheme clusters/verse lines;
3. retain raw glyph codes and page coordinates beside every transcoded reading;
4. route low-confidence lines to human review, never directly to morphology or alignment.

Permitted next paths, in order:

1. obtain the editor's Unicode/IAST electronic source or a source-authorized plain-text edition with the same reading;
2. install an approved Sanskrit OCR model and manually validate each passage against page images;
3. ingest the translation, notes, and page-level provenance as a calibration-only record while leaving `reading_id` absent—never pretending it aligns to a reconstructed Sanskrit text.

This protects V2 invariants: raw source remains immutable, every translation ultimately references an exact reading, and uncertainty is visible.
