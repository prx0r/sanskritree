# Pipeline Status Board

*The live registry. Each text's row shows its phase-files and status. Update at every phase-completion. Status vocabulary: `done` (phase complete) · `partial` (crux-verses done, full sweep pending) · `pending` (not started) · `in-place` (kept in its original location).*

## The 15 pipeline works

| Work | T1 | R1 | T2 | R2 | T3 | C1 | Anchor |
|------|----|----|----|----|----|----|--------|
| Śivasūtra + Bhāskara's Vārttika (78 sūtras) | done (4 files) | done | done | done | partial (8 sūtras) | done | Dyczkowski ✓ |
| Akulavīratantra (155 vv) | done (3 files) | done | done | done | partial (1–18 + 7 vv) | done | archive.org ✓ |
| Kulānanda | done (2 files) | done | done | done | partial (3 vv) | done | none |
| Unmattabhairavahṛdaya | done (2 files) | done | done | done | partial (2 vv) | done | none |
| Kubjikātantra (17 paṭalas) | done (6 files) | done | done | done | partial (4 vv) | done | none |
| Kaulajñānanirṇaya (24 paṭalas) | done (4 files) | done | done | done | partial (6 vv) | done | book pending |
| Jñānasaṅkalinītantra | partial (opening) | done | done | done | partial (1 v) | done | none |
| Kulasāra | partial (opening) | done | done | done | partial (1 v) | done | none |
| Azeṣakulavallarī | partial (opening) | done | done | done | partial | done | none |
| Kākacaṇḍeśvarīmata | partial (opening) | done | done | done | partial | done | none |
| Kulacūḍāmaṇi | partial (opening) | done | done | done | partial | done | none |
| Nareśvaraparīkṣā | partial (opening) | done | done | done | partial | done | none |
| Kaulāvalīnirṇaya | partial (opening) | done | done | done | partial | done | none |
| Nityākaulatantra | partial (opening) | done | done | done | partial | done | none |
| Spanda Vivṛti (Rājānaka Rāma) | partial (opening) | done | done | done | partial | done | Dyczkowski ✓ |
| **Jñānakārikā** (the Matsyendra bundle) | **done (3 paṭalas — 2026-08-09)** | pending | pending | pending | pending | pending | none — the bundle-network |
| **Kaularahasya** (the rahasya-genre) | partial (paṭalas 1–3 opening) | pending | pending | pending | pending | pending | none |
| **Kulapradīpa** (Śivānandācārya, 7 prakāśas) | partial (prakāśa 1 vv. 1–72) | pending | pending | pending | pending | pending | none — the Kulārṇava-intertext (M00031) |
| **Kulālaśāstra** (the Potter-ṛṣi's ritual manual) | partial (paṭalas 1–2) | pending | pending | pending | pending | pending | none — Dyczkowski's note (the deity = śāstṛ/Skanda) |
| **Kaulārcanadīpikā** (Totakaula, Jñānatantra) | partial (the opening — the kulācāra/yoni-doctrine) | pending | pending | pending | pending | pending | none |
| **Kuladīpikā** (uttaraṣaṭkam, ṣaḍvidyāprakāśikā) | partial (paṭala 1 + paṭala 2's opening) | pending | pending | pending | pending | pending | none |
| **Nityākaulatantra** (the pre-Śrīvidyā fragment) | **done — readable coverage (the lacunae preserved)** | pending | pending | pending | pending | pending | none — Dyczkowski's e-text note |
| **Tarkasaṃgraha** (Annaṃbhaṭṭa — Hop 10 entry) | partial (the opening, AnTs 1–56 sample) | pending | pending | pending | pending | pending | the 1872-English + Athalye (reading-layer pending) |

## The pre-pipeline works (in-place, 00_legacy)

| Work | Location | Status |
|------|----------|--------|
| Ajadapramātṛsiddhi (27 vv) | `truth/truthtranslation` | complete (manual, 2026-07-28) |
| Sambandhasiddhi (21 vv) | `truth/sambandhasiddhi_translation.md` | complete (manual) |
| Īśvarasiddhi (13 vv) | `truth/isvarasiddhi_translation.md` | complete (manual) |
| Spandakārikā (53 vv) | `SPANDAKARIKA_TRANSLATION_V1.md` | complete (CP1, pipeline) |
| Vijñānabhairava (162 vv) | CP2 benchmark + Lakshmanjoo-aligned | complete (CP2) |
| Nyāyasūtra | `proof/checkpoint3/runs/ns_c2.jsonl` | rendered (CP3) |

## The open items (the pipeline's next work)

1. **The full sweeps** — every text's T3-FINAL across all verses (the crux-set is done; the pattern is mechanical).
2. **The prints** — the Bagchi 1934 (archive.org) + the Chatterjee + the KSTS 4/6: the [X]-collation backlog (`_meta/PASS2_ROUND2_AUDIT.md` §3).
3. **The anchors** — the KJN book (Mukhopadhyaya/Dupuis 2012), Torella, Jaideva Singh (or the Lakshmanjoo OCR): the unanchored texts' R2 three-way checks.
4. **The C2 phase** — the comparative commentary (the TĀ-treatment of each doctrine), specced in the flow spec §8.
5. **A human pass on one text** — the ŚS (anchored, complete): calibrates the whole pipeline's error-profile.

## The counts

- 68 pipeline docs (25 T1 + 7 R1 + 7 T2 + 7 R2 + 7 T3 + 6 C1 + 4 _meta + the README/STATUS)
- 189 verses adjudicated and interpreted (the crux-set)
- ~1,600–1,800 verses in T1 across 15 works (+ ~340 legacy) + **the Hop-1 kula-batch openings (2026-08-09): Jñānakārikā 2–3 complete, Kaularahasya 1–3, Kulapradīpa 1.1–72, Kulālaśāstra 1–2, Kaulārcanadīpikā opening, Kuladīpikā 1–2 opening, Nityākaulatantra readable-complete**

## ERROR-MEASUREMENT (2026-08-09 — see `_meta/ERROR_MEASUREMENT.md`)

| Text | Sample | agree | lexical | doctrinal | error |
|------|--------|-------|---------|-----------|-------|
| Śivasūtra vs Dyczkowski | 19 sūtras | 42% | 32% | 26% | **0%** |
| Akulavīra vs archive | 6 regions | 100% | 0% | 0% | 0% |

**Collation resolved (the Bagchi print):** Akulavīra v. 14 (svabhāvamati-mataṃ confirmed — the no-emendation construal) · v. 23 (viṃśātmakaḥ confirmed — "the twenty-formed") · v. 39 (unresolved — OCR-noisey, page-image check pending). Recorded in `04_r2_adjudication/r2_akulavira.md`.
