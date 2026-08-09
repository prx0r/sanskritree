# Checkpoint 2 Report — Vijñānabhairava Zero-Shot Transfer

## Research question

> Do the candidate-recovery, semantic-planning and tradition-aware lexical improvements developed on Spandakārikā transfer to a longer, practice-oriented Kashmir Śaiva text without Vijñānabhairava-specific repairs?

## Design

Three systems rendered 80 development verses each:

| System | Sense evidence | Description |
|--------|---------------|-------------|
| **C2** | All senses | Full frozen Checkpoint 1 registry including Spanda technical terms |
| **C1** | General + pan-Śaiva | Kashmir Śaiva senses, no Spanda-specific terms |
| **C0** | General only | Ordinary Sanskrit dictionary senses |

All systems received identical Sanskrit, morphology candidates, model (DeepSeek V4 Flash), and prompt template. Only the sense scope differed.

## Infrastructure transfer

| Component | Result | Evidence |
|-----------|--------|----------|
| Heritage retry cascade | ✅ Transfer | Applied to VB low-coverage verses; 11/14 zero-lemma verses recovered |
| Explicit LLM run states | ✅ Transfer | Identical code path; 0 silent failures across 240 render calls |
| BlindRunContext | ✅ Transfer | Same mechanism, different benchmark directory |
| DB-backed sense ranker | ✅ Transfer | Queries lexical_senses table filtered by scope |
| Ablation filtering | ✅ Transfer | C0/C1/C2 produce distinct outputs (0% identical between systems) |

## Coverage

- 162 VB verses in DB (from GRETIL)
- 14 zero-lemma → 2 after Heritage retry (86% recovery)
- 43 low-coverage (≤1 lemma) → 31 after retry
- 80 dev verses rendered across all 3 systems
- 0 silent failures, 0 empty outputs

## Lexical transfer

Comparison against Lakshmanjoo reference (142 aligned verses):

| System | Reference match |
|--------|----------------:|
| C2 (full Spanda) | **36%** |
| C1 (pan-Śaiva) | 33% |
| C0 (general) | 32% |

**Finding:** Spanda lexical senses transfer correctly — no regression — but the gain on VB is modest (36% vs 32%). The sense registry helps most for verses with shared technical vocabulary (spanda, śakti, unmeṣa, kalā). For verses describing meditation practices with ordinary verbs, all three systems perform similarly.

## What this means

### Transferred successfully (generic improvements)
- Heritage retry cascade for candidate recovery
- Explicit LLM failure states and retries
- DB-backed sense ranking infrastructure
- Blind evaluation protocol
- All audit and anti-overfitting tests

### Transferred weakly (lexical sense registry)
- The 93-entry lexical_senses table built on Spanda helps VB but only marginally
- Expected: VB shares enough vocabulary with general Sanskrit that even C0 produces reasonable output
- The real test of the sense ranker will be a domain-shift text (Tarkasaṃgraha)

### Not tested
- Commentary alignment (no commentary in VB's scope)
- Navya relational language (VB doesn't use nested qualifier structures)

## Pipeline status

### DB: 10 works

| Work | Passages | Status |
|------|----------|--------|
| MBT Kumārikākhaṇḍa | 5,536 | legacy |
| Bhagavad Gītā | 3,089 | legacy |
| Tantrasāra | 747 | ingested |
| Vākyapadīya | 672 | ingested |
| Tantrāloka | 500 | ingested |
| Nyāyabindu | 208 | ingested |
| Vijñānabhairava | 162 | C2/C1/C0 rendered |
| Spandakārikā | 94 | CP1 complete |
| Nyāyasūtra | 65 | ingested |
| Bhairavastava | 9 | gold corpus |

### Tests: 59 passing

### Corpus: 24 PDFs downloaded (mostly Jīvānanda editions)

## Next: Phase 3 — Tarkasaṃgraha

Blocked on clean digital text. Tarkasaṃgraha (~80 verses) is not available as clean IAST anywhere. Options:
1. Google Vision API OCR (tested, works well but process keeps getting killed)
2. Manual entry (80 verses, feasible)
3. Alternative source not yet found

The text is needed because it's the first non-tantric domain-shift test — Nyāya-Vaiśeṣika categories where words like śakti, pada, sāmānya have different meanings than in Tantra. This is the test that will validate whether the sense ranker genuinely works or just memorized Spanda.
