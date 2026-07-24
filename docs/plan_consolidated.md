# Consolidated Development Plan

Based on review of all prior plans (dev-plan, goldfeedback, newestdev, endgame1, vision2, vision2path, visiongranular, visionothers) and 28 benchmark evaluations.

## What we've learned

| Lesson | Evidence | Source |
|--------|----------|--------|
| GNNs are premature without gold data | Only 511 BRONZE decisions | goldfeedback, vision2 |
| Frame selection is fixable | 6→1 errors in one sprint | benchmark v0.1→v0.2 |
| Candidate generation is the bottleneck | 8/30 verses have ≤1 lemma | benchmark v0.2 |
| Standards migration is premature | STAM/TEI/nanopubs before evaluation is risky | visionothers |
| The evaluation loop works | measure → fix → re-measure → improve | v0.1→v0.2 delta |
| Systems C and D are identical | Lean gate doesn't constrain output yet | four-system comparison |

## What NOT to do next

1. **Don't migrate to STAM/nanopublications** — premature while ontology is unstable
2. **Don't train GNNs** — insufficient gold data (need 1,000+ real decisions)
3. **Don't build local Heritage** — benchmark showed 90% success on hard cases via web API
4. **Don't expand to 120 passages** — fix the 8 low-coverage verses first
5. **Don't build commentary workbench** — need stable evaluation loop first

## What TO do next (prioritized)

### Priority 1: Close the candidate generation gap
The single largest measurable error source. 8 verses produce ≤1 lemma, making translation impossible regardless of system.

**Approach:** Targeted vocabulary seeding for the specific lemmas missing from those 8 verses. Use ByT5 output (already run) and Heritage retry to seed missing lexemes.

**Exit:** All 30 pilot verses have ≥3 lemmas.

### Priority 2: Add real LLM baselines (Systems A and B)
Without A/B comparison against a real LLM, we cannot prove Sanskritree adds value. Current A/B are gloss-based.

**Approach:** Run the 30 pilot passages through an LLM API with controlled prompts. System A: "Translate this Sanskrit verse." System B: "Translate this Sanskrit verse given these dictionary entries and morphological analyses."

**Exit:** Four-system comparison with real LLM baselines against Sanskritree C and D.

### Priority 3: Make the Lean gate actually constrain something
Systems C and D are currently identical. The Lean certificate verifies structural consistency but never fails because the factor graph never produces structurally invalid output.

**Approach:** Add publication-constraint rules to the Lean manifest: (a) minimum lemma coverage threshold, (b) required semantic-role coverage, (c) unsupported-addition prohibition. When these fail, the certificate distinguishes C from D.

**Exit:** At least 5/30 passages fail the Lean gate, demonstrating a measurable difference between C and D.

### Priority 4: Expand benchmark to 120 passages
Only after the above three are stable. Use the same 3-track structure (40 known, 40 untranslated, 40 adversarial).

**Exit:** 120-passage frozen benchmark with automated evaluation script.

### Priority 5: STAM round-trip pilot
One bounded experiment: export 30 passages → STAM JSON → re-import. Test zero-loss round-trip.

**Exit:** Decision: STAM as export format vs annotation library vs canonical representation.

### Priority 6: Commentary intervention vertical slice
One root-text/commentary pair, 100 passages, intervention ontology with review UI.

**Exit:** Publishable Commentary Intervention Benchmark v0.1.

## Decision tree

```
Which component to improve next?
│
├── Candidate generation gap? (8 verses ≤1 lemma)
│   → Priority 1: Seed vocabulary
│
├── No LLM baseline for comparison?
│   → Priority 2: Add Systems A/B
│
├── Lean gate doesn't distinguish C from D?
│   → Priority 3: Add constraining rules
│
├── Benchmark too small for reliable conclusions?
│   → Priority 4: Expand to 120
│
├── Need standards-based corpus export?
│   → Priority 5: STAM pilot
│
├── Need publishable academic product?
│   → Priority 6: Commentary workbench
│
└── None of the above?
    → Re-run evaluation, let new data drive priorities
```

## Timeline estimate

| Priority | Effort | Dependencies |
|----------|--------|--------------|
| P1: Seed vocabulary | 2-4 hours | None |
| P2: LLM baselines | 4-8 hours | API access |
| P3: Lean constraints | 4-8 hours | P1 (need coverage to constrain) |
| P4: 120-passage benchmark | 8-16 hours | P1, P2, P3 |
| P5: STAM pilot | 8-16 hours | P4 (stable corpus) |
| P6: Commentary workbench | 40-80 hours | P5 |
