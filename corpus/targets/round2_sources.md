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
