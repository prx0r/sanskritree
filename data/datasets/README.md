# Sanskritree Datasets

## Manthānabhairavatantra — Kumārikākhaṇḍa

### Source
Dyczkowski edition (IGNCA, 2009). Sanskrit OCR'd via Google Vision API. English extracted from PDF text layer.

### Files

| File | Format | Description |
|------|--------|-------------|
| `mbt_page_aligned.jsonl` | JSONL | 1,314 page-level Sanskrit-English pairs |
| `mbt_verses.jsonl` | JSONL | 6,367 extracted verses with chapter/verse metadata |
| `mbt_manifest.yaml` | YAML | Full OCR manifest matching Spandakārikā format |

### Schema

**mbt_page_aligned.jsonl:**
```json
{
  "id": "mbt.page.0018",
  "sanskrit_page": 18,
  "english_page": 19,
  "sanskrit": "देवनागरी text...",
  "english": "English translation...",
  "source": "Manthānabhairavatantra — Kumārikākhaṇḍa"
}
```

**mbt_verses.jsonl:**
```json
{
  "id": "mbt.ch1.v6",
  "chapter": 1,
  "verse_number": 6,
  "sanskrit": "श्रीनाथ उवाच...",
  "source_page": 20,
  "source": "Manthānabhairavatantra — Kumārikākhaṇḍa"
}
```

### Stats
- Sanskrit pages: 1,314
- English pages: 2,308
- Extracted verses: 6,367 (5,436 numbered)
- Total Sanskrit chars: 2,332,123
- Chapters: 1-10
- OCR engine: Google Vision API (DOCUMENT_TEXT_DETECTION)
- Cost: ~$0.47
