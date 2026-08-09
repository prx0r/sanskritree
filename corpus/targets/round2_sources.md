# Round-2 Sources — the verification + commentary layer

*Status 2026-08-09: ✅ = already on disk · 🟢 = free on archive.org (download-now) · 📚 = buy/book.*

## Already downloaded this session (`sources/round2/`)

| File | What it anchors | Size |
|------|-----------------|------|
| `saiva_age_sanderson_2009.txt` (+pdf) | **Sanderson, "The Śaiva Age" (2009)** — the period-context master-source: the rise and dominance of Śaivism, the Kaula/Atimārga/Mantramārga taxonomy, the domestication narrative — the commentary's historical frame | 1.0 MB |
| `avalon_hymns_to_goddess_1913.txt` | **Avalon, *Hymns to the Goddess* (1913)** — contains the **Karpūrādistotra translation** (the Kālīkula anchor; line 18021 "Karpuradistotra") | 527 KB |
| `jha_nyayasutras_vol1.txt` | **Jhā, *The Nyāya Sūtras of Gautama with Vātsyāyana's Bhāṣya and Uddyotakara's Vārttika*** (Indian Thought Series) — the N1/N2-hop anchor (even includes the Vārttika!) | 1.4 MB |
| `kalhana_rajatarangini_stein.txt` | **Stein's *Rājataraṅgiṇī* translation (1961 reprint)** — the Kashmir political history for the period-essays (the Kārkoṭa/Utpala dynasties, Avantivarman's court, the Śaiva patronage) | 1.9 MB |

## Prioritized acquisitions

### Tier 1 — anchors for our complete texts (the pass-2 verification backbone)
| Item | For | Where |
|------|-----|-------|
| **Mukhopadhyaya & Dupuis, *The Kaulajñānanirṇaya: The Esoteric Teachings of Matsyendrapāda*** (Aditya Prakashan, New Delhi, 2012) | the KJN's published translation — the full per-verse comparison | 📚 (Cloudflare-blocked online; the book is the reliable route) |
| **Torella, *The Īśvarapratyabhijñākārikā of Utpaladeva with the Author's Vṛtti*** (Motilal Banarsidass; 2nd ed. 2021) | the Hop-5 anchor (we hold partial Torella-volume chapters) | 📚 |
| **Jaideva Singh, *Śiva Sūtras: The Yoga of Supreme Identity*** (Motilal, 1979) | the Kṣemarāja-Vimarśinī anchor (Hop 1 stage 2) | 📚 — alternative: OCR the **Lakshmanjoo *Shiva Sutras: The Supreme Awakening*** scan we already have (`blog/library/pdfs/tantra/`) via Google Vision |
| **Dyczkowski, *A Journey in the World of the Tantras*** (Indica Books, 2004) | the Kaula/T1-T2 commentary goldmine (the Cīnācāra, the Kaula cults, the Kālīkula) | 📚 |

### Tier 2 — period-context and commentary sources
| Item | For | Where |
|------|-----|-------|
| **Sanderson, "Śaivism and the Tantric Traditions"** (in *The Religions of Asia*, 1988/2015) | the systemic taxonomy (Atimārga/Mantramārga, the Kaula subdivisions) | 🟢/📚 (check archive.org) |
| **Goudriaan & Schoterman, *The Kubjikāmata-tantra*** (Groningen, 1988) | the Kubjikā-cluster comparative root-text | 📚 |
| **Heilijgers-Seelen, *The System of Five Cakras in Kubjikāmatatantra 14–16*** (Groningen, 1994) | the Kubjikā-cakra scholarship (our paṭala-6 cakra-yoga) | 📚 |
| **Mallinson & Szántó, *Roots of Yoga*** (Penguin, 2017) | the early-haṭha context (the Akulavīra/KJN's practices in the wider literature) | 📚 |
| **Goodall et al., *The Niśvāsatattvasaṃhitā*** (EFEO, 2015) | the T1-cluster's earliest layer | 📚 |
| **Kalhana's Rājataraṅgiṇī** — ✅ downloaded (Stein) | the Kashmir period-essays | — |
| **The Mahānayaprakāśa studies** (Krama) | the T4-cluster — check for partial translations/editions (Dezső? the KSTS) | 🔍 to verify |

### Tier 3 — Nyāya hop anchors (public domain — all 🟢)
| Item | Where |
|------|-------|
| **Jhā, *Nyāyasūtras with Bhāṣya and Vārttika*** — ✅ downloaded | — |
| **Athalye & Bodas, *Tarkasaṃgraha with Dīpikā* translation** (Bombay, 1897/1930) | 🟢 archive.org |
| **Ghoṣa's Tarkasaṃgraha translation** (the older one, with the Dīpikā) | 🟢 archive.org |

## The commentary's new evidence base (just downloaded)

1. **The Śaiva Age** gives the commentary its historical skeleton: the three-age schema, the Kaula subdivisions, the domestication narrative (the "wild" vs the "domesticated" registers our batch spans).
2. **Avalon's Karpūrādistotra** anchors the Kālīkula hop properly (the hymn's translation + Avalon's notes on the Kālī-vidyā).
3. **Jhā's Nyāyasūtras** anchors the N-hops (the Bhāṣya + the Vārttika in English — the whole classical layer).
4. **Stein's Rājataraṅgiṇī** supplies the Kashmir history for the period-essays (the kings, the courts, the Śaiva patronage — e.g., Avantivarman's court, the Kaula circles).

## Workflow note

- The archive.org items were fetched via the metadata-API + direct download (djvu.txt = the text layer). Same pattern for any future item: `archive.org/metadata/{id}` → the djvu.txt/PDF → `sources/round2/`.
- The 🟢 items can be downloaded on request; the 📚 items need the user's purchase (or the OCR-route for the Lakshmanjoo scan).

---

# DOWNLOAD RUN 2026-08-09 (the acquisition sweep)

## GRETIL (sources/gretil2/ — 6 texts)
nyayasutra · nyayasutra_bhasya (Vātsyāyana) · nyayasutra_tika · **tattvacintamani** (Gaṅgeśa!) · nyayabindu · pramanavarttika. (The 4 URL-404s — Tarkasaṃgraha, Vaiśeṣikasūtra, Padārthadharmasaṃgraha, Vākyapadīya — are already held in the earlier `sources/gretil_*.txt` set; the targetslogic URLs are stale.)

## Archive.org — Bagchi 1934 (the collation crown)
`sources/round2/bagchi_kjn_1934.txt` (14,368 lines) — the full KJN-bundle print (KJN + Akulavīra + Kulānanda + Jñānakārikā): the corrupt-pāda collation item, secured.

## Archive.org — the Jīvānanda Vidyāsāgara collection (sources/round2/jivananda/)
The 19th-c. Bengali scholar-editions — the Navya-Nyāya crown in its original prints:
| Item | For |
|------|-----|
| `tarkasamgraha_english_1872.pdf` | **an 1872 English translation of the Tarkasaṃgraha** — the Hop-10 anchor, predates Athalye! |
| `tattvacintamani_upamanakhanda_1872.pdf` | the Tattvacintāmaṇi's Upamāna-khaṇḍa (Jīvānanda's edition) |
| `anumanachintamani_didhiti_1872.pdf` | the Anumāna-khaṇḍa **with Raghunātha's Dīdhiti** — the Navya crown's core |
| `anumanachintamani_parisishta_1875.pdf` | the Anumāna parisiṣṭa |
| `kevalanvayi_tika_1897.pdf` | the Kevalānvayi with ṭīkā |
| `bhasapariccheda_1902.pdf` | Viśvanātha's Bhāṣāpariccheda (the Muktāvalī's root) |
| `nyayadarsana_bhasya_1874.pdf` | the Nyāyadarśana with the Bhāṣya (collation) |
| `kularnava_tantra_1898.pdf` | the Kulārṇava's Bengali print (Hop 1 collation) |
| `kulayananda_chandrika_1877.pdf` | **the Kulānanda with the Chandrikā commentary** — our text's own commentary! |
- All image-scans (no text layers) — OCR via Google Vision when used for collation.

## Archive.org — Athalye (dli.ministry.27265)
`sources/round2/athalye_tarkasamgraha.txt` — the Tarkasaṃgraha edition with the English introduction/translation (the standard anchor).

## What the sweep resolved
- **The KJN's corrupt pādas now have their collation source** (the Bagchi print).
- **The Kulānanda's own commentary exists** (the Chandrikā — 1877).
- **The Navya-Nyāya hop's anchors are in** (the 1872 English Tarkasaṃgraha, the Dīdhiti, Athalye).
