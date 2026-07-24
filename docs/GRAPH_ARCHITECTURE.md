# Sanskritree Graph Architecture

## Core reframe

Sanskritree is not a translation model. It is a **typed heterogeneous evidence graph** with:

```
signed message passing
sheaf-style consistency constraints
path-based inference
optional graph diffusion
```

The system represents thousands of **competing, mutually supporting, mutually excluding philological hypotheses**, then lets confidence flow through the network while preserving exact provenance.

## The graph structure

For one passage:

```
Passage
├── Reading
│   ├── Token span
│   ├── Sandhi split A
│   └── Sandhi split B
├── Morphological analysis
│   ├── accusative singular
│   └── nominative singular
├── Compound analysis
│   ├── karmadhāraya
│   └── tatpuruṣa
├── Lexical sense
│   ├── general Sanskrit sense
│   ├── Trika sense
│   └── Kubjikā sense
├── Semantic frame
│   ├── devotional action
│   ├── identity claim
│   └── ritual instruction
└── Translation spans
```

## Edge types with meaning

| Edge | Meaning |
|------|---------|
| `SUPPORTS` | Evidence strengthens hypothesis |
| `REQUIRES` | Hypothesis depends on prior decision |
| `EXCLUDES` | Mutually incompatible with alternative |
| `CONTRADICTS` | Logically inconsistent |
| `ALIGNS_WITH` | Corresponding spans across languages |
| `ATTESTED_IN` | Lemma/sense found in text |
| `QUOTED_BY` | Source cited in commentary |
| `COMMENTED_AS` | Gloss/explanation of source |
| `SAME_LEMMA` | Same lexical root |
| `SAME_TRADITION` | Same doctrinal context |
| `PARALLEL_PASSAGE` | Cognate text elsewhere |
| `DERIVED_FROM` | Genealogical dependence |

## Key distinction: evidence support ≠ acceptance status

```
propagated_score: 0.91   (what the graph says)
human_status: "accepted" (what the philologist says)
lean_status: "consistent" (what Lean verifies)
```

A common but mistaken interpretation can accumulate high graph weight through repetition alone. The two values are kept separate.

## Division of labour

| Layer | What it does |
|-------|-------------|
| **Lean** | Decides admissibility (hard constraints) |
| **Graph** | Computes evidential support (weighted propagation) |
| **Human** | Decides acceptance (sparse supervision) |
| **LLM** | Produces readable English (renderer, not database) |

## Evidence-conditioned weight update

```
w_e^{t+1} = clip(w_e^t + η·r_e - λ·c_e - μ·d_e)
```

Where:
- r_e = reward from human adjudication
- c_e = contradiction penalty
- d_e = dependency discount
- η, λ, μ = controlled rates

## Implementation phases

### Phase G0 — no neural model (immediate)
Weighted signed propagation in Python/SQLite. Add edge_type, weight, polarity, provenance_strength, independence_group to schema. Traverse typed edges up to depth 3, decay confidence, combine evidence, suppress excluded alternatives. Returns ranked hypotheses + full paths.

### Phase G1 — relational message passing
Export graph neighborhoods to PyTorch Geometric. R-GCN and Heterogeneous Graph Transformer baselines. NBFNet-style path ranking.

### Phase G2 — sheaf prototype
9-verse Bhairavastava graph with hand-specified restriction maps: TokenAnalysis→SyntacticRole, CompoundReading→EntityInterpretation, SemanticFrame→EnglishAlignment. Calculate consistency energy per candidate.

### Phase G3 — learn pathway reliability
Train small relation parameters (engine reliability, transformation, attenuation, source calibration) against human adjudication.

### Phase G4 — constrained English realization
LLM renders final semantic graph as English. Graph supplies: predicate, agent, object, epithets, location, manner, forbidden_additions. Output is aligned back to graph.

## References

- [Geometric Deep Learning](https://arxiv.org/abs/2104.13478) — symmetries and structure
- [Knowledge Sheaves](https://arxiv.org/abs/2110.03789) — typed consistency constraints
- [Neural Sheaf Diffusion](https://github.com/twitter-research/neural-sheaf-diffusion) — heterophilic message passing
- [NBFNet](https://github.com/DeepGraphLearning/NBFNet) — path-based inference
- [ULTRA](https://github.com/DeepGraphLearning/ULTRA) — inductive KG reasoning
- [Graph-constrained Reasoning](https://github.com/RManLuo/graph-constrained-reasoning) — LLM constrained to valid graph paths
- [Heterogeneous Graph Transformer](https://arxiv.org/abs/2003.01332) — type-dependent attention
- [Think-on-Graph](https://arxiv.org/abs/2307.07697) — LLM graph traversal
- [Logic Diffusion](https://arxiv.org/abs/2306.03515) — relation diffusion for KG reasoning
- [PyKEEN](https://github.com/pykeen/pykeen) — KG embedding baselines
