# Source Extraction Plan

## Current Sources (Ingested)
| Source | Format | Status | Coverage |
|--------|--------|--------|----------|
| GRETIL Spandakārikā | YAML | ✅ Ingested | 53 verses |
| GRETIL Bhairavastava | YAML | ✅ Ingested | 9 verses |
| GRETIL Bhagavad Gītā | YAML | ✅ Ingested | 3089 verses |
| GRETIL Vijñānabhairava | YAML | ✅ Ingested | 162 verses |
| Dyczkowski Spandakārikā | PDF | ✅ Extracted (34/53) | Reference only |
| Heritage/Vidyut/ByT5 | API | ✅ Ingested | 136K hypotheses |
| Mitrasamgraha | JSON | ✅ Ingested | Evaluation harness |

## Available Sources (Not Yet Ingested)
| Source | Location | Format | Notes |
|--------|----------|--------|-------|
| Tantrāloka 11 vols | sources/ | PDF | Dyczkowski translation |
| Aphorisms of Śiva | sources/ | PDF | Dyczkowski |
| MBT Kumārikākhaṇḍa | sources/ | ZIP | Dyczkowski |
| The Doctrine of Vibration | sources/ | PDF | Dyczkowski |

## Planned Sources (To Acquire)
| Source | Repository | Priority | Justification |
|--------|------------|----------|---------------|
| Singh Spandakārikā | Archive.org | HIGH | Second reference for CP1 |
| Singh Vijñānabhairava | Archive.org | HIGH | Reference for Phase 2 |
| GRETIL Nyāyasūtra | GRETIL | MEDIUM | Phase 3: first logic text |
| GRETIL Tarkasaṃgraha | GRETIL | MEDIUM | Shortest logic primer |
| GRETIL Kiraṇatantra | GRETIL | MEDIUM | Phase 3 candidate |
| Ratnatrayaparīkṣā | GRETIL | LOW | Phase 3 (untranslated) |
| Muktabodha corpus | Muktabodha | LOW | Deep untranslated Tantra |

## Extraction Pipeline

For new PDF sources:
```bash
pdftotext source.pdf source.txt          # Basic extraction
# OR use Google Vision API for OCR:
curl -X POST -H "Authorization: Bearer $GOOGLE_VISION_API_KEY" ...
```

For GRETIL sources:
```bash
PYTHONPATH=src python3 scripts/seed_gretil.py --manifest data/manifests/work.yaml
```

For Heritage retry (used in CP1 for spk.3.3):
```bash
PYTHONPATH=src python3 scripts/heritage_mapping.py
```
