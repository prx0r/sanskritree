# Next Steps — Proving the system works as a system

## Milestone status

```
M1   Pipeline tests                                  ✅  16/16
M2   Bhairavastava 1 proof bundle                   ✅  proof/bhairavastava_1.json
M3   9 Bhairavastava verses adjudicated              ✅
M4   Tables populated                               ✅
M5   5 Spanda verses blind translated                ✅
M6   Full Spandakārikā processed                    ⚠️  Structural only (0.4 tokens/verse)
M6.5 Heritage occurrence mapping                    📝  CURRENT
M6.6 Reprocess + audit Spandakārikā                 📝  After M6.5
M7   Vijñānabhairava ingestion                      📝  After Spanda coverage >95%
M8   Ritual/instruction frames                       📝
M9   Real adjudications                              📝
M10  Logistic/path-ranking baselines                 📝
M11  Lean Layer C                                    📝
M12  R-GCN/HGT/sheaf                                📝
```

## M6.5 — Heritage normalization and occurrence mapping

Convert each Heritage solution into occurrence-level hypotheses.

### Required objects

```
SEGMENTATION_HYPOTHESIS
  ├── contains TOKEN_OCCURRENCE candidates
  ├── contains TOKEN_ANALYSIS_HYPOTHESIS candidates
  ├── covers exact source character spans
  ├── proposed_by Heritage
  └── excludes incompatible segmentations
```

### Alignment strategy

Use ordered dynamic-programming aligner between:
```text
normalized source character sequence
Heritage reconstructed segment sequence
```

Store per-occurrence:
```json
{
  "source_start": 0,
  "source_end": 14,
  "segment_index": 0,
  "surface_original": "bhairavanātham",
  "surface_reconstructed": "bhairava",
  "normalization": "IAST",
  "engine": "heritage",
  "solution_id": "...",
  "engine_rank": 17
}
```

### Deduplication

- Canonical analysis: lemma + POS + case + number + gender + tense/mood + person + derivation
- Occurrence hypothesis: passage + source span + canonical analysis
- Join table: `hypothesis_solution_support(hypothesis_id, heritage_solution_id, local_segment_index)`

### Exclusion structure (not quadratic)

```
SEGMENTATION_CHOICE_GROUP (passage_id, exactly_one=true)
TOKEN_ANALYSIS_CHOICE_GROUP (occurrence_id, at_most_one=true)
```

### Acceptance gate for M7

Spandakārikā must reach:
- Combined candidate coverage: >95% of source spans
- Gold-analysis recall: >90%
- Unexplained spans: <2%
- Hard segmentation violations: 0

### Then rerun M6

Regenerate all 53 passage graphs, re-run beam search, compare old vs new, audit 5 blind translations.

Produce ablation: Vidyut only / Heritage only / combined / combined minus propagation / combined plus commentary.

Tests (A–F):
- A. Corpus integrity — passage count, no orphans, no corruption
- B. Morphology candidates — Vidyut+Heritage coverage, OOV rate, candidate recall
- C. Segmentation/compounds — fixture-based (bhairavanātham etc.)
- D. Factor-graph determinism — same graph hash for same input
- E. Propagation — synthetic micrographs (positive/negative support, exclusion, order invariance, convergence)
- F. Lean interface — valid compiles, invalid fixtures fail

## M2: Bhairavastava 1 proof bundle

One reproducible command producing one complete evidence graph + accepted interpretation + aligned translation + Lean proof + audit report.

### Required artifact
```
source reading
all segmentations
all morphological hypotheses
all compound trees
accepted/rejected decisions
factor scores
evidence paths
semantic frame
translation plan
English realization
token/span alignment
Lean verification
human adjudication
```

### Accepted interpretation
```
bhairavanātham     → karmadhāraya → "Lord Bhairava"
anāthaśaraṇyam     → epithet      → "refuge of the helpless"
tvanmayacittatayā  → instrumental  → "with my mind absorbed in you"
hṛdi               → locative      → "in the heart"
vande              → 1sg present   → "I praise/worship"
```

### Verification targets
- 100% required semantic-role coverage
- 0 rejected-node leakage
- 0 unsupported doctrinal additions
- 0 unattached English spans
- All implicit content labelled

### Edge cases to test
- `bhairavanātham`: karmadhāraya beats tatpuruṣa via evidence paths
- `tvanmayacittatayā`: bahuvrīhi rejected or ranked below accepted
- `vande`: 1sg only; 3sg or imperative must fail

## Key principle: error-driven development

Every failure → permanent regression fixture in `tests/fixtures/`.

## Heritage integration

Heritage API confirmed working (102 solutions/verse). Next: map Heritage compound splits to occurrence-level hypotheses with exact source spans, encoding provenance, segmentation IDs, solution rank, engine version.
