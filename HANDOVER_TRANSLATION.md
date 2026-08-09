# HANDOVER — the translation pipeline, for the next agent

*2026-08-09. Read this, then the Craft (`translations/_meta/REF_NOTES.md`), then the Leapfrog Map (`corpus/targets/leapfrog_map.md`), then the STATUS board (`translations/STATUS.md`). Everything is committed; the binaries are on disk.*

---

## 1. Where we are

**Six complete works in T1** (Śivasūtra+Bhāskara 78 sūtras · Akulavīratantra 155 vv · Kulānanda · Unmattabhairavahṛdaya · Kubjikātantra 17 paṭalas · Kaulajñānanirṇaya 24 paṭalas) **+ 9 openings** (the 10-text batch + the Spanda Vivṛti). **~1,600–1,800 verses** total. **60 pipeline docs** across the six layers; **~189 verses fully adjudicated** through the whole stack.

The pipeline: `translations/01_t1_working → 02_r1_review → 03_t2_alternate → 04_r2_adjudication → 05_t3_final → 06_c1_interpretation` (+ `_meta`: the protocol, the glossary, the audits, REF_NOTES, SELF_REVIEW). The flow: T1 → R1 → T2 (alternative-reading, blind) → R2 (full reasoning chains) → T3 (final) → C1 (plain-English).

## 2. Where to leapfrog from — the batch order (per the map)

1. **Hop 1 finish** — the bundle's last texts (Jñānakārikā, Kaulopaniṣad, Kaularahasya), then the kula-manuals — with the **Bagchi collation** (`sources/round2/bagchi_kjn_1934.txt`) resolving the [X]-backlog as you go.
2. **Hop 10's entry** — the **Tarkasaṃgraha full translation** — the anchors are IN (the 1872 English translation, Athalye's text-layer): the Navya hop's on-ramp.
3. **Hop 3 (the Krama)** — the **Mahānayaprakāśa** (M00033/34), the crown — the highest-value untranslated philosophy in the corpus; start while Hop 1's collation runs.
4. Then: the Kubjikā complex (Hop 2) → the Trika chain (Hop 4) → the late Kālīkula (Hop 5) → the Bhairava substrate (Hop 6) → the Siddhānta (Hop 7) → classical Nyāya (Hop 9: the Nyāyasāra!) → the Navya crown (Hop 10: Tattvacintāmaṇi — the whole text on disk).

## 3. The immediate first tasks (the highest-value, in order)

1. **The error-measurement** (SELF_REVIEW gap #1): sample 20–30 verses per anchored text (ŚS vs Dyczkowski; Akulavīra vs the archive translation), classify every mismatch (agree/lexical/doctrinal/error), publish the rates in STATUS. This converts "we think it's fine" into a number.
2. **The Bagchi collation**: every corrupt pāda in the KJN/Akulavīra/Kulānanda files against `bagchi_kjn_1934.txt` (the print is OCR-noisey — verify against the page-images in the same archive item). Resolve the [X]-flags; record in the R2s.
3. **The Chandrikā OCR**: the Kulānanda's own commentary (`round2/jivananda/kulayananda_chandrika_1877.pdf`) via Google Vision — a new anchor for the Kulānanda.
4. **The Tarkasaṃgraha full translation** (the Hop-10 entry) — the anchors are in; run it through the full stack.
5. **The Mahānayaprakāśa start** — the crown's opening paṭala through T1.

## 4. The quality bar (what the handover demands)

- **The Craft** (`_meta/REF_NOTES.md`) — read before every session: the attitude per pass, the context-stack, the gems, the objectivity protocol.
- **The Self-Review** (`_meta/SELF_REVIEW.md`) — the per-layer audit: what's weak and the fixes. The next agent's first act: apply the fixes (the coverage-lines, the C1 [X]-markers, the T3 sweeps).
- **No silent edits.** Corrections live in the next phase's docs or the audits — never in-place rewrites of earlier phases.
- **The flow's law:** T2 explores alternative interpretations (engineered agreement is a failure mode); R2 must be able to overturn both sides; the anchor-quote, not memory; the [X]-honesty; the honest coverage-lines.
- **The slop-law** in C1: no NARR-frames, no meta, each word carrying.
- **The measurements:** coverage-lines everywhere; the error-rates published; the OPEN-counts per text.

## 5. The gotchas (operational)

- `PYTHONPATH=src` for the scripts; `scripts/` is not a package.
- `/tmp/opencode` is ephemeral — persist everything to `sources/`.
- The archive.org pattern: the metadata-API → the djvu.txt/PDF → `sources/round2/`; the Jīvānanda scans are image-only (OCR via Google Vision; the key is in the env).
- The GRETIL URLs in `targetslogic.md` are partly stale — use the GRETIL catalogue.
- The Muktabodha corpus is fully local (`sources/muktabodha-lib/`) — no re-downloading.
- Disk: `/mnt` at ~86% — clean `/tmp/hf` before big pulls.
- The Bagchi text is OCR-noisey; the anchor-books (KJN 2012, Torella, Jaideva Singh) are the pending acquisitions.

## 6. The state of the evidence (what verifies what)

| Anchor | On disk | Verifies |
|--------|---------|----------|
| Dyczkowski: TĀ 11 vols + Spanda-4-commentaries + Aphorisms + Doctrine of Vibration | ✅ | the ŚS, the Spanda-stack, all doctrine |
| Lakshmanjoo VB + Chakravarty Tantrasāra + MBT ch. 1–7 | ✅ | VB, the Kaula-geography |
| Sanderson's Śaiva Age + Avalon's Hymns + Jhā's Nyāyasūtras + Stein's Rājataraṅgiṇī | ✅ | the period, the Kālīkula, the Nyāya, the Kashmir history |
| **Bagchi 1934** (the bundle's print) | ✅ | the KJN/Akulavīra/Kulānanda collation |
| **The 1872 English Tarkasaṃgraha + Athalye** | ✅ | Hop 10 |
| **The Chandrikā + the Navya prints** | ✅ (OCR-pending) | the Kulānanda, Hop 10 |
| The KJN-book (2012), Torella, Jaideva Singh | [ACQ] | the KJN, Hop 4 |

## 7. The open items (the honest ledger)

1. The T3 full-sweeps (the crux-set is done; the corpus is not).
2. The error-measurement (never produced).
3. The [X]-collation (unblocked — the Bagchi print is in).
4. The anchors (the KJN-book, Torella, Jaideva Singh, Dyczkowski's Journey).
5. The C2 comparative layer (specced in the flow spec §8).
6. **A human Sanskritist's pass on one text** (the ŚS — anchored, complete) — the only real calibration; nothing replaces it.
7. The C1s' [X]-markers (per SELF_REVIEW).

*The last line of the handover: the pipeline is sound and the evidence is in; the work ahead is the sweeps, the collation, the measurements, and — eventually — the human. Leapfrog from Hop 1's finish, with the Bagchi print open.*
