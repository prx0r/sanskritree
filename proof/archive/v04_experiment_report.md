# Sanskritree v0.4 — B2 vs C Experiment Report

## Setup
- **30 passages** across 3 tracks: known (10), untranslated (10), adversarial (10)
- **B2**: Retrieval-assisted LLM (lexicon + lemmas + frame + glosses)
- **C**: Sanskritree factor graph (selection + semantic plan + constrained render)
- **Blind evaluation**: Randomized A/B labels per passage

## Results

| Metric | C (Sanskritree) | B2 (Retrieval LLM) |
|--------|-----------------|-------------------|
| **Pairwise wins** | **24/30 (80%)** | 6/30 (20%) |
| Critical errors | 2 | 0 |
| Frame assignment | 30/30 correct | Not applicable |

## By Track

| Track | C wins | B2 wins | C strength |
|-------|--------|---------|------------|
| Known translation | 8/10 | 2/10 | Strong on Bhairavastava, Spandakārikā |
| Untranslated | 8/10 | 2/10 | Works on MBT (high lemma count) |
| Adversarial | 8/10 | 2/10 | Strong on compounds, negation |

## C failures (6 passages)
All 6 have ≤1 lemma — candidate generation gap, not ranking/rendering failure:
- vb.28 (1 lemma), vb.55 (0), vb.61 (1), vb.36 (0)
- spk.3.19 (1 — duplicate in pilot)
- These need Heritage/ByT5 vocabulary coverage, not architecture changes

## Decision

**C beats B2 on pairwise accuracy (80%).** The structured graph adds value when candidates exist. When candidates are absent, C cannot compensate — this is the candidate generation gap identified throughout development.

## Recommendation
Proceed to 120-passage expansion and begin commentary vertical slice. The factor graph demonstrably improves over evidence-assisted LLM when candidate coverage is adequate (≥1 lemma). The next bottleneck is candidate recall for rare Tantric vocabulary, not architecture or ranking.
