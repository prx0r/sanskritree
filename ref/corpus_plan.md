# Sanskritree High-Signal Corpus v1

## Source
Derived from: https://www.sanskritebooks.org/2013/12/complete-works-of-jibananda-vidyasagara/
Plus Trivandrum Sanskrit Series, Tantric Texts Series, Bibliotheca Indica,
Ānandāśrama Sanskrit Series, Kāvyamālā.

## Corpus Architecture

```
sources/raw/             immutable downloads
registry/works.jsonl     intellectual-work records
registry/editions.jsonl  edition-specific records
registry/files.jsonl     scan/file records
derived/ocr/             raw OCR
derived/normalized/      corrected Sanskrit
annotations/             linguistic and scholastic layers
references/sealed/       translations used only for evaluation
```

## Layer Structure

Layer 1 — Canonical clean texts (GRETIL, Muktabodha, SARIT, Heritage, DCS)
Layer 2 — Historical scan archive (6 collections)
Layer 3 — OCR derivatives (page image → raw OCR → normalized → IAST)
Layer 4 — Work structure (work → chapter → verse/sūtra → commentary unit)
Layer 5 — Linguistic annotations (tokens, morphology, compounds, syntax)
Layer 6 — Scholastic evidence (school, author, date, genre, technical senses)
Layer 7 — Evaluation references (sealed English translations)

## Six Collections

1. Complete Works of Jīvānanda Vidyāsāgara (~200 items) — core Nyāya/Navya
2. Trivandrum Sanskrit Series — rare manuscript editions, Śaiva Āgama
3. Tantric Texts Series (22 units) — tantric dictionary + commentaries
4. Bibliotheca Indica (277 titles) — Buddhist logic, Nyāya, translations
5. Ānandāśrama Sanskrit Series (144 books) — deep commentary alignment
6. Kāvyamālā (109 volumes) — linguistic control corpus

## 30-Work Processed Seed

### Existing tantric checkpoints
1. Spandakārikā (in DB)
2. Vijñānabhairava (in DB, C2 rendering)
3. Spandanirṇaya selections (not yet acquired)
4. Śivasūtra with commentaries (not yet acquired)

### Nyāya/Navya
5-15: Tarkasaṅgraha, Bhāṣāpariccheda, Muktāvalī, Dinakarī,
Nyāyasūtra, Vaiśeṣikasūtra, Sāmānyanirukti, Śabdaśaktiprakāśikā,
Anumānacintāmaṇi slice

### Mīmāṃsā/semantic contrast
16-21: Mīmāṃsāparibhāṣā, Mīmāṃsānyāyaprakāśa, Mānameyodaya,
Ślokavārttika selections, Sphoṭasiddhi, Vākyapadīya selections

### Tantric expansion
22-30: Tantrābhidhāna, Śāradātilaka, Tantrarāja, Kāmakalāvilāsa,
Kulārṇavatantra, Mahārthamañjarī, Tattvaprakāśa, Tantrasamuccaya,
Īśānaśivagurudevapaddhati

## Download Priorities

| Collection | Download | OCR Now | Process First |
|---|---|---|---|
| Jīvānanda | Yes | No | Nyāya/Navya/Tantra |
| Trivandrum | Yes | No | Śaiva, Nyāya, Mīmāṃsā |
| Tantric Texts | Yes | Nearly all | Dictionary + commentaries |
| Bibliotheca Indica | Yes | No | Logic and translations |
| Ānandāśrama | Yes | No | Commentary structures |
| Kāvyamālā | Yes | No | Linguistic controls |
