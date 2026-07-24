# Sanskritree Research Kernel v0.1 — Release Notes

## Baseline

The first frozen release of the Sanskritree research kernel. This is not a deployment package — it is a reproducible baseline of the working translation pipeline, intended to be frozen before architectural refactoring begins.

## Contents

5 works, 8,890 passages, 368 MB database.

| Work | Verses | Coverage |
|------|--------|----------|
| MBT Kumārikākhaṇḍa | 5,436 | 40% |
| Bhagavad Gītā | 3,089 | 63% |
| Bhairavastava (gold) | 9 | **90%** |
| Spandakārikā | 53 + 41 commentary | 66% |
| Vijñānabhairava | 162 | 39% |

## Pipeline

```
Corpus → Heritage/Vidyut/ByT5 → Factor graph → Beam search → Semantic plan → Constrained render → Lean audit
```

## Verification

- **16/16 pipeline tests** pass (corpus integrity, morphology, factor graph, propagation, Lean)
- **2 Lean modules** compile (15 theorems): `Decision.lean` (Layer A), `LayerB.lean` (Layer B)
- **511 adjudication decisions** across 63 sessions (BRONZE level)
- **Transfer test**: 42.6% coverage on held-out Vijñānabhairava verses
- **Action detection**: 0/10 → 10/10 Instruction frame selection
- **Heritage benchmark**: 18/20 success on hard Tantric cases (defer local installation)

## Engine distribution

| Engine | Hypotheses |
|--------|-----------|
| Vidyut | 135,781 |
| Heritage | 600 |
| Compound splitter | 22 |
| Manual compound | 9 |
| Heritage compound | 5 |

## Key file hashes

```
factor_graph.py      17d207cd71e45d8b
factors.py           f7f6f2335f490217
propagation.py       faeb192ac9898fdb
scoring.py           572159427268f488
Decision.lean        5cfa6baa4f8ec20a
LayerB.lean          68df43a3ed23d289
test_pipeline.py     9728c57bf334fb0b
```

## How to reproduce

```bash
git checkout <v0.1-tag>
pip install -r requirements.txt
cd lean && lake build Sanskritree
cd ..
PYTHONPATH=src python3 -m unittest tests.test_pipeline -v
PYTHONPATH=src python3 scripts/freeze_v0.1.py
```

## Limitations

- Heritage integration via web API only (slow: 2.2s/verse)
- Lexical senses nearly empty (4 senses for 5,787 lemmas)
- Compound trees limited to 6 manual entries
- All adjudications are BRONZE (model-assisted, no independent review)
- Vijñānabhairava coverage at 39% — lexical coverage bottleneck
- MBT at 40% — OCR legacy font quality
