# Sanskritree — Source Corpus Reference

> Hugging Face is better as a bulk-processing layer than as the definitive source. Most Sanskrit datasets are generic mixtures with weak provenance. For untranslated Tantra and technical logic, the best strategy is to combine GRETIL, SARIT, Muktabodha and DSBC, then mirror the cleaned corpus onto Hugging Face.

---

## Most useful Hugging Face datasets

| Dataset | URL | Notes |
|---------|-----|-------|
| paws/sanskrit-verses-gretil | [HF](https://huggingface.co/datasets/paws/sanskrit-verses-gretil) | Strongest ready-made dataset. Hundreds of thousands of passages from GRETIL TEI files, IAST + Devanāgarī, source work/author/chapter/verse metadata. ~16,000 passages classified as Tantra. Verse-oriented — prose commentaries may be fragmented. |
| Anamavajra-Labs/sanskrit-corpus | [HF](https://huggingface.co/datasets/Anamavajra-Labs/sanskrit-corpus) | Recent Sanskrit corpus. Inspect provenance and licensing before treating as authoritative edition. |
| Anamavajra-Labs/tantraloka-pipeline | [HF](https://huggingface.co/datasets/Anamavajra-Labs/tantraloka-pipeline) | Organized around processing Tantrāloka. Likely segmented passages/translations/pipeline data. |
| Anamavajra-Labs/tantraloka-dyczkowski-raw | [HF](https://huggingface.co/datasets/Anamavajra-Labs/tantraloka-dyczkowski-raw) | Raw Dyczkowski-related Tantrāloka data. Translated/secondary material. Underlying publication remains copyrighted. Treat as research-processing data only. |
| joyboseroy/bengal-dharma-corpus | [HF](https://huggingface.co/datasets/joyboseroy/bengal-dharma-corpus) | Small but well-labelled Buddhist–Śākta corpus. Vajrayoginī, Tārā, Hevajratantra, Bṛhannīlatantra, Kālī texts. Scripts vary IAST/Devanāgarī. |
| buddhist-nlp/mitrasamgraha-released-data-only | [HF](https://huggingface.co/datasets/buddhist-nlp/mitrasamgraha-released-data-only) | Buddhist Sanskrit with English counterparts. CC BY 4.0. Already ingested. |
| surajp/sanskrit_classic | [HF](https://huggingface.co/datasets/surajp/sanskrit_classic) | 342K line-level classical Sanskrit. Poor documentation — no source text identification. Useful for language modelling, risky for scholarship. |
| chronbmm/sanskrit-monolingual-pretraining | [HF](https://huggingface.co/datasets/chronbmm/sanskrit-monolingual-pretraining) | Large monolingual pretraining collection. Suitable for tokenizers/LMs, limited bibliographic metadata. |
| shunyasea/vedic-sanskrit | [HF](https://huggingface.co/datasets/shunyasea/vedic-sanskrit) | Primarily Vedic. Useful as historical linguistic control corpus. |
| harshalJk/guru-sanskrit-corpus | [HF](https://huggingface.co/datasets/harshalJk/guru-sanskrit-corpus) | ~225K records, 704 MB. Empty README. Do not assume textual accuracy without inspection. |
| snskrt (org) | [HF](https://huggingface.co/snskrt) | HF organization collecting Sanskrit datasets. Browsing hub. |
| HF Sanskrit tag | [HF](https://huggingface.co/datasets?other=sanskrit) | Live index of Sanskrit-tagged datasets. Noisy but reveals new uploads. |

## OCR and manuscript-processing datasets

| Dataset | URL | Notes |
|---------|-----|-------|
| Sanskrit-OCR-Typed-Dataset | [HF](https://huggingface.co/datasets/Process-Venue/Sanskrit-OCR-Typed-Dataset) | Images + typed Sanskrit labels for OCR training. |
| Shiv_puran_OCR | [HF](https://huggingface.co/datasets/snskrt/Shiv_puran_OCR) | Śivapurāṇa page/region data. Verse vs non-verse layout detection. |
| Sanskrit-Qwen2.5-VL-7B-Instruct-OCR | [HF](https://huggingface.co/diabolic6045/Sanskrit-Qwen2.5-VL-7B-Instruct-OCR) | Vision-language model for Sanskrit page images → text. |
| Post-OCR correction benchmark | [HF](https://huggingface.co/papers/2211.07980) | Research + dataset for post-OCR correction (broken conjuncts, vowel marks, word segmentation). |

## What Hugging Face is missing

No trustworthy, comprehensive HF dataset for complete editions of:

- Śaiva Āgamas
- Bhairava tantras
- Kubjikā tantras
- Krama texts
- Trika commentarial literature
- Complete Tattvacintāmaṇi and Navya-Nyāya commentarial chain
- Prabhākara Mīmāṃsā works
- Bhartṛhari's complete commentarial tradition
- Complete Buddhist pramāṇa collections with reliable work-level metadata

Individual examples may occur inside generic corpora but are not exposed as clean, audited, work-by-work collections.

---

## Best source repositories to convert into a corpus

| Repository | URL | Best for |
|------------|-----|----------|
| GRETIL UTF-8 catalogue | [GRETIL](https://gretil.sub.uni-goettingen.de/gret_utfbk.htm) | Best general source for clean electronic Sanskrit — logic, grammar, Mīmāṃsā, Buddhist philosophy, some Tantra |
| GRETIL corpus source | [GitHub](https://github.com/gretil/corpus) | Machine-readable corpus source; better than extracting from webpages |
| SARIT | [SARIT](https://sarit.indology.info/) | Structured TEI editions with preserved textual divisions, apparatus, metadata |
| SARIT corpus download | [GitHub](https://github.com/sarit/SARIT-corpus) | Direct downloadable corpus, suitable for Parquet/JSONL conversion |
| Muktabodha Digital Library | [Muktabodha](https://muktabodha.org/digital-library/) | Deepest major source for untranslated Śaiva and Śākta material |
| Muktabodha e-texts | [Muktabodha etexts](https://etexts.muktabodha.org/) | Electronic-text interface for complete Sanskrit texts |
| DSBC | [DSBC](https://www.dsbcproject.org/) | Best large source for Buddhist Sanskrit, tantric and epistemological works |
| BDRC | [BDRC](https://library.bdrc.io/) | Sanskrit and Tibetan manuscript scans, cataloguing, Buddhist scholastic materials |
| Internet Archive Indology | [Archive](https://archive.org/details/indologicalbooks) | Huge scanned Indological collection. Rare Navya-Nyāya, Śaiva, tantric editions. OCR varies radically. |

---

## The corpus worth building

A genuinely useful Hugging Face dataset would preserve **whole works**, not shuffled lines:

```json
{
  "tradition": "",
  "school": "",
  "subschool": "",
  "author": "",
  "work": "",
  "commentary_on": "",
  "approximate_date": "",
  "language": "",
  "script_original": "",
  "iast_normalized": "",
  "chapter": "",
  "section": "",
  "verse_or_prose_unit": "",
  "sanskrit": "",
  "editor": "",
  "edition": "",
  "source_url": "",
  "page_reference": "",
  "ocr_status": "",
  "proofreading_status": "",
  "license": ""
}
```

Division into categories:

```text
tantra/saiva_siddhanta
tantra/trika
tantra/krama
tantra/kubjika
tantra/kaula
tantra/sakta
tantra/buddhist_vajrayana
logic/nyaya
logic/navya_nyaya
logic/vaisesika
logic/buddhist_pramana
logic/jaina
language/vyakarana_sphota
language/mimamsa_semantics
cross_school_polemics
```

---

## Key distinction

| Source type | Best for |
|-------------|----------|
| **Hugging Face corpora** | Convenient downloading and modelling |
| **GRETIL/SARIT electronic editions** | Citation and provenance |
| **Muktabodha/BDRC/Internet Archive scans** | Genuinely untranslated, niche material |
| **Rare tantric and Navya-Nyāya texts** | Will require OCR + manual correction |
