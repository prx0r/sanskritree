# saivamap — the tradition-ordered working tree

*The reference map (`corpus/targets/canonical_reference_map.md`) made operational. Each tradition gets a folder; each folder collects the texts we hold, the anchors that referee them, and the dossier-entries its lemmas feed. The **triangle** — Kramasadbhāva ↔ Kubjikāmata ↔ Tantrāloka — is the map's prescribed comparative core; the goal is **anchors per tradition first**, then assigning works to traditions, then the site architecture.*

## The tradition folders

| Folder | Tradition | The map's node | Core texts (anchored ✓ / to acquire [ACQ]) |
|---|---|---|---|
| `trika/` | Trika | the calibration layer | Tantrāloka ✓ (GRETIL + Dyczkowski 11v), Spandakārikā ✓, Parātriṃśikā ✓ (M00042–44), Mālinīvijayottara ✓ (M00160), Īśvarapratyabhijñā ✓ (M00019–22), Śivadṛṣṭi ✓ |
| `krama_kalikula/` | Krama/Kālīkula | the first leap | Mahānayaprakāśa ✓ (M00033/34), Mahārthamañjarī ✓ (M00035), Kramasadbhāva [ACQ], Devīpañcaśataka [ACQ], Kālīkulakramārcana [ACQ] |
| `kubjika/` | Kubjikā/Paścimāmnāya | the specialist corpus | **Kubjikāmata ✓ (GRETIL, `sources/gretil2/raw_kubjikamata.txt`)**, Kubjikātantra ✓ (M00030), liturgy ✓ (M00547–51), Ṣaṭsāhasra [ACQ], Śrīmatottara [ACQ], Ciñciṇīmata [ACQ], Manthānabhairava ✓ (Dyczkowski) |
| `kaula/` | Kaula (the bundle) | the reformulation node | KJN ✓ (M00027 + Bagchi), Akulavīra ✓ (M00003 + archive), Jñānakārikā ✓, Kulārṇava ✓ (M00031), the kula-manuals ✓ |
| `spanda_pratyabhijna/` | Spanda/Pratyabhijñā | the control corpus (sideways) | Spandakārikā ✓ (Dyczkowski), Ajaḍapramātṛsiddhi ✓ (M00502), Īśvarasiddhi ✓ (M00023), Vākyapadīya ✓ (GRETIL), Nyāyasūtra ✓ (gretil2 + Jhā) |
| `sarvamnyaya/` | Sarvāmnāya/Newar | the endgame synthesis | Newar paddhatis [R2, later] |

## The triangle (the map's prescribed core)

```text
KRAMASADBHĀVA ──↘
                semantic comparison
KUBJIKĀMATA ←──→ TANTRĀLOKA
```

**Current state:** Kramasadbhāva is [ACQ] (not on GRETIL or local); Kubjikāmata ✓ (GRETIL anchor saved); Tantrāloka ✓ (GRETIL + the Dyczkowski anchor). So the triangle's *active* legs are KMT ↔ TĀ; Kramasadbhāva joins when acquired.

## How a translation flows through here

1. Pick a text in its tradition folder (start: **Kubjikāmata paṭala 1**).
2. Consult the **dossier** for its technical terms (`dossiers/` + `translations/_meta/period_glossary_pass1.md` + the reference map's glossary) — the sense is tradition-conditional.
3. Run the pipeline (T1 → R1 → T2 → R2 → T3), citing the tradition's anchor (for KMT: the GRETIL edition + the report's dossiers).
4. Dossier the lemmas the text touches (with our attestations + the report's scholarly senses).
5. Update STATUS.md.

## The folder contents

- `anchors/` — one line per anchor: what we hold (path), what it referees (tradition/text), status.
- `dossiers/` — the 24-lemma backlog (the report's list), one file per lemma as they're built.
- each tradition folder — the texts' working files (or symlinks/paths to the translations).
