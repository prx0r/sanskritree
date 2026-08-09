# START HERE — New Agent Entry Point (updated 2026-08-09)

> Read this first. Then the linked files. Everything a new agent needs to resume the **leapfrog translation program** is reachable from this page.

---

## 1. Where the project lives

| Path | What it is |
|------|-----------|
| `/mnt/HC_Volume_106427611/sanskritree/` | **Main project** (this dir): pipeline code, corpus, references, truth/ translations, atlas |
| `/root/projects/tantraloka/` | **Dyczkowski reference stack**: `texts-clean/` = 11 vols TĀ translation (340K lines) + Spanda w/ 4 commentaries + Aphorisms of Śiva + Doctrine of Vibration |
| `/root/projects/clean/` | Truthmap claim engine (Nyāya gate, contention benchmarks) — used to machine-verify philosophical claims |
| `/root/.hermes/skills/research/` | Hermes skills: `truthmap-enquiry`, `truthmap-research`, `source-first-research` (note: `sanskritree-translate/` exists but is EMPTY — protocol lives in `truth/truthagent`) |

## 2. The mission right now

**Leapfrog translation**: translate period-clusters of Sanskrit Tantra + Nyāya, where every hop starts from (a) a text we already translated and (b) a published English translation on disk as verification anchor. Vocabulary compounds across the corpus. Never translate unanchored material until the period-glossary is grown.

**The master plan file: `corpus/targets/translation_atlas.md`**
- Period-organized corpus (T1 early Bhairava → T7 late Kaula; N1–N3 Nyāya)
- The LEAPFROG EXPANSION MAP (hops 1–7, ordered by anchor strength)
- The full audit of English reference translations on disk (10 anchors + partials)
- Acquisition list for missing references

## 3. The verification anchor stack (published English translations on disk)

| Anchor | Coverage | Location |
|--------|----------|----------|
| Tantrāloka + Jayaratha's Viveka (Dyczkowski, 11 vols) | TĀ ch. 1–37 full | `tantraloka/texts-clean/tantraloka-vol{1..11}-dyczkowski_clean.txt` |
| Spandakārikā + 4 commentaries (Dyczkowski) | 53 vv + Vṛtti/Vivṛti/Nirṇaya/Saṃdoha | `tantraloka/texts-clean/spandakarika-dyczkowski_clean.txt` |
| Śiva Sūtras + Bhāskara's Vārttika (Dyczkowski) | all sūtras | `tantraloka/texts-clean/aphorisms-of-siva-dyczkowski_clean.txt` |
| Doctrine of Vibration (Dyczkowski) | Spanda/Krama doctrine | `tantraloka/texts-clean/doctrine-of-vibration-dyczkowski_clean.txt` |
| Vijñānabhairava (Lakshmanjoo) | 112 meditations, 142 vv aligned | `references/vb_lakshmanjoo.json` + epub in `blog/library/ebooks/` |
| Tantrasāra (Chakravarty, ed. Marjanovic) | 22 āhnikas | `references/tantrasara_chakravarty.md` + full PDF in `CX-Train/blog/density/EssayViz/` |
| **MBT Kumārikākhaṇḍa ch. 1–7 (Dyczkowski, ed. + transl.)** | ch. 1–7 translated | `sources/mbt/mbt_kumarika_ch1-7_dyczkowski_translation.txt` (+ intro vol, + full Sanskrit `sources/mbt_sanskrit/mbt_sanskrit_full.txt`) |
| Torella volume chapters | IPK studies (intro, apoha, memory; Ratié on Īśvarasiddhi) | `truth/torella_book/` (10 files) |
| Lakshmanjoo, Shiva Sutras (Vimarśinī) | image scan — **OCR needed** | `blog/library/pdfs/tantra/Swami-Lakshmanjoo.-Shiva-Sutras...pdf` |
| Abhinavagupta scholar bundles | 40+ papers, passage translations | `abhinavagupta/` (43 zips, 802 files) |

## 4. Corpus assets (Sanskrit)

| Asset | Content | Location |
|-------|---------|----------|
| **Muktabodha e-text library** | 499 IAST texts (all periods; Kaula/Kubjikā/Krama/Kālīkula/Siddhānta/Navya-Nyāya) | `sources/muktabodha-lib/` (172M; zip also kept here) |
| GRETIL texts | Nyāyasūtra, Nyāyabindu, Tantrāloka, Tantrasāra, Tarkasaṃgraha, Vākyapadīya | `sources/gretil_*.txt` |
| MBT Sanskrit | whole Kumārikākhaṇḍa | `sources/mbt_sanskrit/mbt_sanskrit_full.txt` (5.5M) |
| Pipeline DB | 10 works, 136K hypotheses, 6K lexemes, 511 adjudications | `data/sanskritree-v2.db` (353M) |
| corpus/ PDFs (25) | **image scans, no text layer — OCR needed** (mostly duplicates of muktabodha-lib texts; low priority) | `corpus/` |

## 5. Translation state

**Done (ours):** Spandakārikā 53 vv (CP1) · Vijñānabhairava 162 vv (CP2) · Siddhitrayī 61 vv (`truth/truthtranslation`, `truth/sambandhasiddhi_translation.md`, `truth/isvarasiddhi_translation.md`) · Kubjikātantra 1.1–1.8 with trails (`truth/kubjika_tantra_v2_three_readings_with_trails.md`) · Nyāyasūtra render (`proof/checkpoint3/runs/ns_c2.jsonl`)

**In progress:** Kubjikātantra paṭala 1 continuation · next hop = **Hop 1: Śivasūtravārttika (Bhāskara) vs the Aphorisms anchor** (Vimarśinī stage 2 waits on Lakshmanjoo OCR)

## 6. Translation protocol (the legit apparatus)

- **`truth/truthagent`** — the full protocol: establish text → parse before interpreting → three kept-separate translations (literal/contextual/doctrinal) → risk terms → argument reconstruction → anti-hallucination rules
- **`truth/kubjika_tantra_v2_three_readings_with_trails.md`** — the working example of the standard: provenance, text-history, per-verse grammar tables with usage parallels, three translations each with choice-trails, synthesis with explicit unresolved items
- **`truth/process_notes.md`** — source-discovery + truthmap ingestion gotchas
- **`truth/torella_book/`** — reference chapters for the Pratyabhijñā hops
- Status markers: [T] textual / [V] vṛtti / [R] reconstruction / [X] needs check

## 7. Gotchas (from HANDOVER + later sessions)

- `scripts/` is NOT a package: always `PYTHONPATH=src python3 scripts/x.py`
- **`/tmp/opencode/` is ephemeral** — never leave assets there; persist to `sources/`
- **OCR garbage traps**: `tarkasamgraha_root.txt`, `Tarkasamgraha_Khemraj_Vision.txt` are glyph soup; blog/library PDFs + corpus/ PDFs are image-only (no text layer)
- Muktabodha legacy site: `muktalib7.com/DL_CATALOG_ROOT/` serves plain HTTP downloads (the new UI is JS/Turnstile-gated); the full library zip is on disk, no need to re-download
- Heritage API timeouts → retry cascade exists; `j~na` IAST tildes break Heritage — normalize first
- Do NOT train a neural ranker (511 adjudications, not 5k); report qualitative failure patterns instead
- Blind-translate first, compare after — no peeking at references before rendering
- Disk: `/` 81% used, `/mnt` 86% — clean `/tmp/hf` before big downloads

## 8. History pointers (older state)

- `HANDOVER.md` (root) — CP1-era state, still valid for pipeline mechanics
- `ref/README.md` — decision tree for corpus acquisition + architecture refs
- `docs/guidenow.md`, `docs/next_steps.md` — milestone tracking
- `devplan.md` — post-mortem of the philosophy phase (Siddhitrayī → perspectival partition reframe)
- `truth/agent_handoff.md` — the philosophy-track handoff (2026-07-28)
