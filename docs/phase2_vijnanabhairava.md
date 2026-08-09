# Phase 2: Vijñānabhairava Zero-Shot Transfer

## Research question

> Do the generic candidate-recovery, semantic-planning, and tradition-aware lexical improvements developed on Spandakārikā transfer to a longer, practice-oriented Kashmir Śaiva text without Vijñānabhairava-specific repairs?

## Design principles

1. **Freeze before looking.** Establish source, verse IDs, and hashes before any reference inspection.
2. **No VB-specific tuning.** The Checkpoint 1 pipeline runs as-is. Any improvement must be a generic change that also helps Spanda.
3. **Ablation is the test.** C0 = pipeline before Spanda sense layer, C1 = pan-Śaiva senses, C2 = full Spanda senses. This distinguishes structured-inference value from domain-sense overfitting.
4. **162 verses is large.** Stratify by compound length, practice type, negation, technical vocabulary.

## Systems

| ID | Description | Evidence tier | Status |
|----|-------------|---------------|--------|
| B2 | LLM + lexical/morphological evidence | none | baseline |
| C0 | Checkpoint 1 pipeline, no Spanda senses | general only | ablated |
| C1 | Checkpoint 1 pipeline, pan-Śaiva senses | general + pan-Śaiva | mid |
| C2 | Checkpoint 1 pipeline, all senses | full | target |

## Partitions

| Split | Verses | Purpose |
|-------|--------|---------|
| Development | 80 | inspect references after blind generation |
| Holdout | 42 | measure without overfitting |
| Challenge | 40 | sealed until v1.0 candidate |

Stratify by: compound length, instruction type, negation, technical vocabulary, chapter.

## Gates (preregistered)

Before any VB-specific fixes:

- 53/53 Spanda regression tests still pass
- 162/162 VB outputs complete
- Lemma R@5 ≥ 90%
- Critical system failures = 0
- Unsupported additions < 5%
- C beats B2 on ≥ 65% of adjudicated development cases
- Spanda-specific senses cause no critical errors

## Transfer classification

After zero-shot evaluation, classify every failure into:

| Class | Meaning |
|-------|---------|
| TRANSFERRED_SUCCESS | Improvement from Spanda pipeline carries over |
| SHARED_SAIVA_ERROR | Error shared by both texts (candidate gap, syntax, etc.) |
| SPANDA_OVERFIT | Spanda-specific sense actively misleads VB translation |
| VB_SPECIFIC_LEXICAL_GAP | VB uses vocabulary absent from Spanda evidence |
| PRACTICE_INSTRUCTION_ERROR | VB's yoga instructions misread (new genre challenge) |
| SYNTACTIC_ERROR | Different sentence structures cause misparse |
| RENDERER_ERROR | English realization fails despite correct analysis |
| REFERENCE_DEPENDENCE | VB reference is interpretive rather than literal |

## Implementation

```bash
# Phase 0: freeze
PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py freeze --work vijnanabhairava

# Phase 1: generate all 162 verses (3 systems × 162 = 486 runs)
PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py generate --system c0
PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py generate --system c1
PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py generate --system c2

# Phase 2: audit and compare
PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py audit --run RUN_ID
PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py compare --reference dyck --reference singh
```

## References

- Jaideva Singh: Vijñānabhairava or Divine Consciousness (Motilal Banarsidass, 1979)
- Mark Dyczkowski: Vijñānabhairava translation (if available)
- Christopher Wallis: Tantra Illuminated (selected verses)

## Current VB status

From `recall_ci.py`: 40% token coverage in DB. Likely needs Heritage retry cascade for compound-heavy verses.

## Expected timeline

| Week | Deliverable |
|------|-------------|
| 1 | Source manifest, reference alignment, 162-verse split, recall report |
| 2 | Blind generation (C0, C1, C2), leakage audit, environment freeze |
| 3 | Dev evaluation (80 verses), transfer classification |
| 4 | Fix top transferable cause, rerun, holdout evaluation |
| 5 | Challenge unseal, v1.0 candidate |
