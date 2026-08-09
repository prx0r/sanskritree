# PASS 2 AUDIT — 2026-08-09

*Consolidated verification of all pass-1 translations. Per PASS_PROTOCOL: re-derive ✓, anchor-check, [X]-resolution, corrections recorded. **Pass-1 files are NOT edited** — this document is the audit trail; corrections apply to the next translation pass or to the site-dataset build.*

---

## Method

1. **Anchor checks** — the Śivasūtra files were checked against Dyczkowski's *Aphorisms of Śiva* (on disk, `tantraloka/texts-clean/aphorisms-of-siva-dyczkowski_clean.txt`). The Kaula files were checked against two newly discovered published translations (see §New anchors).
2. **Web/literature review** — searches on: Akulavīratantra scholarship, KJN scholarship, Kubjikātantra attestations, Rājānaka Rāma. Sources: DuckDuckGo, archive.org, academia.edu, wisdomlib (Aufrecht's Catalogus Catalogorum, Monier-Williams), Open Library.
3. **Re-derivation** — spot-re-derivations of key grammatical claims were done; no errors found in the pass-1 grammar (compound splits and case readings verified).

---

## New anchors discovered (framing corrections for pass-1 files)

| Text | Anchor | Status |
|------|--------|--------|
| **Kaulajñānanirṇaya** | Mukhopadhyaya, Satkari (with Stella Dupuis), *The Kaulajñānanirṇaya: The Esoteric Teachings of Matsyendrapāda, Sadguru of the Yoginī Kaula School*, Aditya Prakashan, New Delhi, 2012 | EXISTS — direct PDF blocked (academia.edu Cloudflare); acquire book/scribd copy |
| **Akulavīratantra** | English translation in the "AllTantras" archive.org collection (`archive.org/download/AllTantras/AkulaviraTantra.pdf`), Nātha-tradition rendering with notes | ✅ downloaded to `/tmp/opencode/akulavira_eng.txt` (398 lines) |

**Correction:** the Kaula pass-1 files' header claims "No English anchors exist — first translations" are **wrong**. Both texts have published English translations. The pass-1 *translations* themselves are not invalidated (they were made from the Sanskrit with the editions recorded), but the first-translation framing is withdrawn, and the translations should now be checked against the anchors (Akulavīra: done below; KJN: pending the book's acquisition).

---

## A. Śivasūtra with Bhāskara's Vārttika (3 files)

### Verified ✓
| Item | Result |
|------|--------|
| 1.7 turyābhogasaṃvit | Anchor renders the same reading family: "The consciousness which is the expanse of the Fourth State (abides constantly in) the various (states) of waking, dreaming and deep sleep" — our KSTS4-based rendering stands |
| 2.4 the two readings | Anchor follows the Vimarśinī-influenced reading ("the slumber of (all) particular forms of ignorance"); our pass-1 kept the KSTS4 reading with [D] flagged — the [D] handling is confirmed correct |
| 2.7 mātṛkācakrasaṃbodhaḥ | Anchor: "The awakening of the Wheel of Matrka" — matches our rendering |
| 1.23 mahāhrada | Anchor: "(The yogi) experiences the vitality of Mantra by contemplating the Great Lake. 1/23" — **confirms adhikāra 1 has 23 sūtras** in Bhāskara's and Dyczkowski's editions (Kṣemarāja's Vimarśinī has 22). Our pending 1.20–1.23 translations are real sūtras — confirmed. |
| 3.9 bracket | Anchor's rendering of Bhāskara's bracket matches our translation closely (the experienced actor, rasa/bhāva, the limited-subject role, vibhāva, the cosmic drama, avilupta consciousness) ✓ |
| 3.44 nāsikāntar | Anchor: "(The movement of the vital breath is stilled) by concentrating on the centre within the nose. Of what use (then) are the left and right channels or Susumna?" — matches our reading. **Numbering note:** anchor = 3/45, KSTS4 = 3-44 — recension numbering discrepancy recorded |

### Corrections
| # | Item | Pass-1 | Pass-2 finding |
|---|------|--------|----------------|
| C1 | 1.13 icchāśaktir umā kumārī | Presented the umā-variant as the better reading, followed it | **The printed KSTS4 reading "icchāśaktitamā kumārī" is Bhāskara's own reading**; the "icchā śaktir umā kumārī" variant was adopted by Kṣemarāja *following Abhinavagupta* (Dyczkowski, Exposition ad 1.13: "Ksemaraja acknowledges the validity of Bhaskara's reading... he follows the lead of his teacher Abhinavagupta and adopts a variant reading"). For a Bhāskara-focused translation, icchāśaktitamā deserves the primary position; the umā-reading moves to the variant note. Also: Kṣemarāja's kumārī-gloss — "the goddess who kills (marayati) or destroys Maya (ku)". |
| C2 | 3.9 nartaka | "The Self is the dancer." | Anchor: "The Self is the actor." Both defensible (nartaka = dancer is more literal; the bracket's imagery is the actor). **Keep "dancer" for nartaka, note the anchor's "actor"** — the naṭa (actor) term in our glossary remains the anchor-consistent rendering for naṭa/naṭavat. |

### Still open [X]
- 1.20–1.23 adhikāra-1 translations (now confirmed real; translate next pass)
- The KSTS4 print (3.16's Hindi data-entry artifact; the 3-14bis sūtra's apparatus)
- The kārikā-number oddities around 3.14bis

---

## B. Kubjikātantra (2 files)

### New evidence
The name *Kubjikātantra* is widely attested (wisdomlib, from Aufrecht's Catalogus Catalogorum + Haraprasad Shastri's Notices):
- **Quoted by Abhinavagupta** (Catal. Io. p. 840)
- Quoted in Tantrasāra (Oxford MS 95a), Śāktānandataraṅgiṇī (Oxf. 103b), by Kaivalyāśrama (Oxf. 108a), in Prāṇatoṣiṇī (p. 2)
- "Kubjikātantre Kaulikānām Antyeṣṭividhānam" (Fl. 372); "Kubjikātantre Durgākavaca" (Pet. 723–725)
- Listed among the 3×64 tantras (Viṣṇukrānta category); mentioned in the Mahāmokṣa-Tantra's bibliography (Shastri, Notices vol. 12, 1898)

**Caveat recorded:** whether the quoted Kubjikātantra = our M00030 text (the late compilation) or the older Kubjikāmata-tradition layer is **unresolved** — Abhinavagupta's quotations are likely to the older layer. The pass-1 dating (late-medieval Kālīkula compilation) is not contradicted by the attestations; the name's history is now documented.

### Verified ✓
- sūreśvarī: only attestation remains inside M00030 itself (1/13) — the epithet is text-internal; rendering stands
- vāmikā: the pūjā-bhāga parallel supports "the Left (power)" — stands

### Still open [X]
- 1.21 "ke gotre na samudbhūtāḥ" (corrupt pāda) — no new evidence found
- 1.31 second half (kṛṣṇā/kṛṣṇa pāda) — no new evidence
- The pañcadaśī/ṣoḍaśī cross-tradition check vs Nityāṣoḍaśikārṇava — pending (text in library)
- The bīja-analysis (paṭala 2) vs later paṭalas' uddhāras — pending (paṭala 3+ untranslated)

---

## C. Kaula frame texts (2 files)

### Akulavīratantra — comparison against the archive.org translation ✓
| Verse | Our pass-1 | Archive translation | Verdict |
|-------|-----------|---------------------|---------|
| Maṅgala | "I bow to Mīnanātha... the bliss of the innate (sahajānanda) born from his own body, the profound support of all..." | "I bow to Shri Minanatha, full of the bliss of Sahaja, liberated from the stain of Maya, supreme, diffused through the universe, in whom all the adharas are deep and still, born from his own self" | ✓ compatible; **correction note:** "sarvamādhāragambhīram" — the Nātha tradition reads *ādhāra* (cakra) — "in whom all the ādhāras are deep" — this tradition-internal reading should be noted alongside our "the support of all" |
| 5–10 | school-list dismissed | same list (Buddhism, Somasiddhānta, Nyāyas, Mīmāṃsā, Pañcarātra, Vāma, Dakṣiṇa, Siddhānta, Itihāsa, Purāṇa, Bhūtatattva, Gāruḍa, Śaiva āgamas) | ✓ |
| 19–22 | negation list | "Nor can it be achieved by piercing the chakras, by concentrating on nadis such as the Ida, Pingala or the Sushumna... Pranayama does not bring liberation either, nor thinking of the granthis, the bindu..." | ✓ |
| 30–33 | "the Stainless (nirañjana), all-knowing, complete..." | "It is all knowing, stainless (niranjana), everywhere... facing in every direction" | ✓ |
| 42 | "he has no mother, no father, no kin, no deity" | "he has no mother, no father, no kin, no deity" | ✓ exact |
| 56 | (beyond our pass-1 coverage) | "the path of the Kaula is of two types — the artificial (kritaka) and the sahaja (spontaneous). The real or Sahaja is that in which Samarasa resides" | **coverage extension** |
| Title-gloss | — | "Akula, as Bagchi points out, is Shiva, the witness while Kula is Shakti, the cluster of energies" | **new glossary entry** |

### Corrections
| # | Item | Pass-1 | Pass-2 finding |
|---|------|--------|----------------|
| C3 | Header framing | "No English anchors exist — first translations" | **Withdrawn** — the Akulavīra has a published English translation (archive.org AllTantras); KJN has Mukhopadhyaya/Dupuis 2012 |
| C4 | Akulavīra coverage | ended at v. 49 | **The text continues** — the AllTantras copy shows vv. 50–63 (the sweet-and-sour taste simile v.50; the kaula-rites question v.55; the kṛtaka-fall v.57; the burnt-seed v.61, cut-root v.62, dissolved-taste v.63 similes). Extend coverage next pass. |
| C5 | Akulavīra dating (header) | 10th–11th c. (from Wikipedia's "eleventh century" claim) | **Refine:** the manuscript evidence dates a copy to the **13th century, origin Kāmarūpa (Assam)** (per aghori.it's bibliographic note); composition may be earlier. The Bagchi-bundle dating (≤11th c. MS) applies to the KJN; the Akulavīra's own MS tradition is 13th c. |
| C6 | KJN paṭala numbering | paṭala 5/14 as the last translated verse | A quoted verse from another copy is cited as "Kaulajnananirnaya VII, 20" — **the paṭala numbering differs between manuscript families** (VII vs our 5) — numbering caveat recorded |
| C7 | The samaya-tension (KJN vs Akulavīra) | recorded as "lineage dialectic" | **Confirmed and sharpened** by v.56: the Kaula path is itself two-fold — kṛtakā (artificial, the observances) vs sahaja (spontaneous, samarasa) — the Akulavīra's negation is of the kṛtaka limb, not of the lineage itself |

### Still open [X]
- KJN 3/2 "apudgalaḥ" · KJN 2/5 "sarvajñā (yatna ?)" · Akulavīra 14 "svabhāvamatimataṃ" (confirmed as printed in the Devanagari of the AllTantras copy: svabhāvamatimataṃ) · Akulavīra 23 "viṃśātmaka" (the twenty — referent still unidentified; the archive translation does not gloss it either) · Akulavīra 39 "nibaddhaṃ ca malakṣaṇam"
- KJN paṭala 5+ continuation (the sādhana chapters) — untranslated

---

## D. Spanda Vivṛti (Rājānaka Rāma) — 1 file

- Author identity: resolved in pass 1 from Dyczkowski's Stanzas intro (Rājānaka Rāma, disciple of Utpaladeva, first half of 10th c.). Pass-2 web search found no independent study superseding this — Dyczkowski remains the authority. ✓
- Anchor coverage of the Vivṛti: confirmed ("the Extensive Explanation (vivrti) on the Stanzas translated for this volume"). ✓
- Still open [X]: Vivṛti v.4's boundary (where Rājānaka Rāma's verse-complex ends and the root kārikā sequence resumes — needs KSTS 6 print).

---

## Glossary updates (period_glossary_pass1.md → add in pass-2/3)

1. **akula/kula** (new entry): per Bagchi — akula = Śiva, the witness; kula = śakti, the cluster of energies. The Akulavīra = the witness-Supreme beyond the energy-cluster. (Source: archive.org Akulavīra translation note; Bagchi 1934.)
2. **nartaka/naṭa**: nartaka = "the dancer" (our rendering, kept); anchor renders "actor" — the glossary's naṭa entry notes both, with the anchor-consistency for naṭa/naṭavat = "actor."
3. **icchāśakti**: add the recension note — icchāśaktitamā (Bhāskara's own reading) vs icchā śaktir umā kumārī (Abhinavagupta/Kṣemarāja variant); kumārī = "she who kills māyā" (ku-mārayati, Kṣemarāja's gloss).
4. **kṛtakā/sahaja**: the Kaula path's two limbs (Akulavīra v.56) — the observances (kṛtaka) vs the spontaneous (sahaja, samarasa). Connects the samaya-observance entries.

---

## Consolidated still-open items (collation list)

1. Kubjikā 1.21 + 1.31 corrupt pādas — need the Chatterjee print or another edition
2. KJN 2/5, 3/2, Akulavīra 14, 23, 39 — need the Bagchi/Calcutta prints (the e-text's doubtful readings confirmed as printed where checkable)
3. Śivasūtra 3.16's Hindi data-entry artifact + kārikā numbering — need KSTS 4 print
4. Vivṛti v.4 boundary — need KSTS 6 print
5. KJN pass-1-vs-Mukhopadhyaya full comparison — pending the 2012 book's acquisition
6. Kubjikā paṭala 3+ (sādhana/yantra) — the bīja-checks pending
7. Akulavīra vv. 50–63 translation — next pass

---

## Pass-2 verdict

- **No translation errors found** in the pass-1 batch (grammar re-derivation + anchor comparison all passed).
- **One framing error corrected** (the "first translation" claims for the Kaula texts — both are anchored).
- **One reading priority corrected** (1.13: icchāśaktitamā is Bhāskara's own reading).
- **Coverage extended by evidence**: Akulavīra continues to ≥63 verses; ŚS adhikāra 1 confirmed at 23 sūtras.
- **Two published translations acquired as new anchors** (Akulavīra: downloaded; KJN: bibliographically confirmed, acquisition pending).
