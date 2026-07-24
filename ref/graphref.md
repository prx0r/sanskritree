# Sanskritree Graph Architecture Reference

> A typed heterogeneous evidence graph with signed message passing, sheaf-style consistency constraints, path-based inference, and optional graph diffusion.

## What the graph represents

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

## Edge types

Each edge means something specific:

```
SUPPORTS
REQUIRES
EXCLUDES
CONTRADICTS
ALIGNS_WITH
ATTESTED_IN
QUOTED_BY
COMMENTED_AS
SAME_LEMMA
SAME_TRADITION
PARALLEL_PASSAGE
DERIVED_FROM
```

Each edge has strength with provenance:

```json
{
  "edge_type": "SUPPORTS",
  "weight": 0.83,
  "source": "Vidyut",
  "evidence_kind": "morphological_analysis",
  "scope": "passage",
  "learned": false
}
```

## Key distinction: diffusion versus truth

Graph diffusion can answer:

> "Given the currently accepted evidence, which interpretation receives the most support?"

It cannot answer:

> "Which interpretation is philologically true?"

A common but mistaken interpretation can accumulate enormous graph weight because it is repeated across secondary sources. Therefore preserve two separate values:

```text
evidence support
≠
acceptance status
```

Example:

```json
{
  "hypothesis": "bhairavanātham is karmadhāraya",
  "propagated_score": 0.91,
  "human_status": "accepted",
  "lean_status": "consistent",
  "direct_evidence_count": 4,
  "dependent_evidence_count": 17
}
```

Lean verifies hard constraints. Diffusion ranks alternatives inside those constraints.

## Why geometric deep learning applies

Geometric deep learning is about designing learning systems around the actual symmetries and structure of the domain rather than treating all inputs as unstructured sequences. Bronstein, Bruna, Cohen and Veličković describe this as exploiting known structural regularities to construct suitable architectures. Sanskritree has unusually strong pre-existing structure: passages, token order, morphology, agreement, dependency, textual genealogy, commentarial relations and tradition-scoped senses. ([arXiv](https://arxiv.org/abs/2104.13478))

A Transformer sees:

```text
bhairavanātham anāthaśaraṇyaṃ ...
```

The graph sees:

```text
surface form
→ possible segmentation
→ lemma
→ inflection
→ syntactic role
→ compound member
→ lexical evidence
→ doctrinal register
→ English realization
```

## Knowledge sheaves

A cellular sheaf associates potentially different data spaces with different node and edge types, then defines mappings that express how locally different representations must agree. It explicitly supports typed representations, local consistency, global consistency and multi-hop reasoning. ([arXiv](https://arxiv.org/abs/2110.03789))

| Sanskritree object | Sheaf interpretation |
|--------------------|----------------------|
| Sanskrit token | Node with morphology space |
| Compound hypothesis | Node with compound-analysis space |
| English span | Node with translation space |
| `ALIGNS_WITH` edge | Restriction map between spaces |
| Case agreement | Local consistency constraint |
| Complete translation | Approximate global section |
| Contradictory choices | High inconsistency energy |
| Best interpretation | Low-energy globally coherent assignment |

Consistency over an edge is defined by mapping the information attached to each endpoint into a common edge space and measuring disagreement. The sheaf Laplacian then quantifies the total inconsistency of an assignment.

A simplified objective:

```
E(H) = Σ_{e=(u,v)} w_e |R_{u→e} h_u − R_{v→e} h_v|² + hard-constraint penalties
```

Where:
- h_u is the current state of a hypothesis
- R_{u→e} converts it into the representational space appropriate to the relation
- w_e is evidence strength
- Low energy means the interpretation is mutually coherent

## Why ordinary graph diffusion is not enough

Ordinary Laplacian diffusion assumes connected nodes should become similar. That is dangerous for a Sanskritree graph which is highly **heterophilic**:

```text
token ≠ lemma
lemma ≠ lexical sense
Sanskrit span ≠ English span
accepted hypothesis ≠ rejected alternative
commentary ≠ primary text
```

Connected nodes often have different types and must transform rather than converge. This is why **Neural Sheaf Diffusion** is relevant — it generalizes graph diffusion by learning edge-specific maps instead of merely averaging neighboring vectors, developed specifically for heterophily and oversmoothing. ([GitHub](https://github.com/twitter-research/neural-sheaf-diffusion))

The target should not be:

```python
new_state[node] = average(neighbor_states)
```

It should resemble:

```python
message = relation_map[edge_type](
    source_state,
    source_type,
    target_type,
)
```

Then aggregate only messages transformed into the correct target space.

## Evidence-conditioned weight update

```
w_e^{t+1} = clip(w_e^t + η·r_e − λ·c_e − μ·d_e)
```

Where:
- r_e = reward from later human adjudication
- c_e = contradiction or failed-consistency penalty
- d_e = dependency discount
- η, λ, μ = controlled rates

Concretely:

```text
Human accepts analysis        → strong reinforcement
Lean verifies consistency     → moderate reinforcement
Published translation agrees  → evidence, but source-weighted
Same LLM repeats output       → almost no reinforcement
Dependent commentary agrees   → discounted reinforcement
Human rejects analysis        → strong penalty
Contradicts morphology        → hard exclusion
```

The system learns **which evidence pathways are reliable**, not simply which translation output occurred most frequently.

## Recommended architecture

### Layer 1: immutable evidence graph

SQLite remains the source of truth.

Nodes:
```
WORK | EDITION | PASSAGE | READING | TOKEN
MORPH_ANALYSIS | SEGMENTATION | COMPOUND_ANALYSIS
LEXICAL_SENSE | SEMANTIC_FRAME
TRANSLATION_CANDIDATE | TRANSLATION_SPAN
COMMENTARY_PASSAGE | FORMALIZATION
```

Edges:
```
CONTAINS | ANALYZES_AS | SUPPORTS | REQUIRES | EXCLUDES
ALIGNS | ATTESTS | PARALLEL_TO | QUOTES | COMMENT_ON | DERIVES_FROM
```

Never replace this with an embedding store.

### Layer 2: hard constraint engine

Handled through Python rules and Lean:

```text
surface coverage
non-overlapping tokenization
case agreement
number agreement
compound-member validity
verb-person compatibility
frame-role compatibility
translation-token coverage
no unsupported source span
```

Impossible graph states receive zero probability or infinite energy.

### Layer 3: weighted belief propagation

Start without neural training. Use deterministic propagation:

```python
support(target) += (
    source_confidence
    * edge_weight
    * provenance_weight
    * independence_discount
)
```

Add signed propagation:

```text
positive edge → raises support
negative edge → suppresses support
exclusion edge → prevents joint activation
```

### Layer 4: path reasoning

Path-based GNNs may be more useful than generic node classification. **Neural Bellman–Ford Networks** learn representations by propagating information along relational paths and retain path interpretability. ([GitHub](https://github.com/DeepGraphLearning/NBFNet))

A Sanskritree query:

> Which sense of kula is best supported here?

Relevant paths:

```text
passage
→ same lemma
→ parallel Kubjikā passage
→ commentary gloss
→ accepted translation

passage
→ cited by Tantrāloka
→ explained by Jayaratha
→ lexical sense
```

The **path itself** is the explanation.

### Layer 5: sheaf consistency

Once the deterministic graph works, add sheaf-style restriction maps for:

```text
morphology → syntax
syntax → semantic frame
semantic frame → translation
lemma sense → English span
```

The best interpretation is one with:

```text
high evidence support
+ low sheaf inconsistency
+ no hard-constraint violations
```

### Layer 6: constrained candidate generation

The LLM should only verbalize graph-approved paths. **Graph-constrained Reasoning** integrates graph structure directly into decoding so generated reasoning paths remain grounded in the knowledge graph. ([arXiv](https://arxiv.org/abs/2410.13080), [GitHub](https://github.com/RManLuo/graph-constrained-reasoning))

For Sanskritree:

```text
graph selects:
  lemma senses
  compound interpretation
  semantic roles
  context allowances
        ↓
LLM realizes these as English
```

The LLM is the renderer, not the philological database.

## What graph diffusion contributes

1. **Confidence propagation** — A manually accepted sense strengthens related hypotheses through parallel passages and quoted occurrences, with decay over distance and provenance dependence.

2. **Retrieval** — Activate the current passage and diffuse outward to retrieve the highest-value neighborhood (tokens → lemmas → senses → parallel passages → commentaries → translations). Better than embedding-only top-k because the path is visible.

3. **Global coherence** — A full hymn translation optimized jointly. If nātha is consistently translated "Lord" in verses 1–8, verse 9 receives some pressure toward the same choice — but direct verse evidence may override it.

## What Logic Diffusion contributes

Introduces relation diffusion and random-walk sampling of nearby sub-logics so a knowledge-graph reasoner can generalize beyond patterns seen during training. Relevant later for discovering untested combinations of known relations, not as the base architecture. ([arXiv](https://arxiv.org/abs/2306.03515))

If Sanskritree already knows `A parallel_to B`, `B glossed_by C`, `C supports sense S`, Logic Diffusion can propose the composite route `A may support S`. This remains a **candidate edge**, never an asserted fact.

## What ULTRA contributes

Zero-shot reasoning over new multi-relational graphs without learning fixed embeddings for each entity or relation vocabulary. Derives relative relation representations from interactions among relations and supports complex logical queries through UltraQuery. ([GitHub](https://github.com/DeepGraphLearning/ULTRA))

This matters because Sanskritree continually adds new texts, lemmas, commentators, traditions, and relation types. However, ULTRA is a substantial model — do not begin there. Use it after establishing a benchmark.

## A concrete scoring model

For a hypothesis h:

```
S(h) = α·D(h) + β·P(h) + γ·C(h) + δ·T(h) − ε·X(h) − ζ·U(h)
```

Where:
- D = direct textual evidence
- P = propagated independent support
- C = global consistency
- T = tradition/register compatibility
- X = contradiction energy
- U = unsupported assumptions

Then:

```text
Lean decides admissibility.
The graph computes evidential support.
The human decides acceptance.
The LLM produces readable English.
```

## Implementation phases

### Phase G0 — no neural model

Implement weighted signed propagation in ordinary Python/SQLite.

Add to schema:
```sql
edge_type  weight  polarity  provenance_strength
independence_group  learned_weight  human_weight  last_updated
```

Implement:
```text
activate passage
→ traverse typed edges up to depth 3
→ decay confidence
→ combine independent evidence
→ suppress excluded alternatives
→ return ranked hypotheses and full paths
```

### Phase G1 — relational message passing

Export graph neighborhoods to PyTorch Geometric. Start with R-GCN baseline, Heterogeneous Graph Transformer baseline, NBFNet-style path baseline. HGT uses node-type- and edge-type-dependent attention, which matches Sanskritree's heterogeneous schema. ([arXiv](https://arxiv.org/abs/2003.01332))

### Phase G2 — sheaf prototype

Small graph for all nine Bhairavastava verses. Define restriction maps manually for:

```text
TokenAnalysis → SyntacticRole
CompoundReading → EntityInterpretation
SemanticFrame → EnglishAlignment
```

Calculate consistency energy for each full candidate translation. Hand-specify restriction maps initially; see whether the correct candidate receives lower energy before learning them.

### Phase G3 — learn pathway reliability

Train only small relation parameters:
```text
engine reliability
relation transformation
edge attenuation
evidence-source calibration
```

Training target is human adjudication: `accepted hypothesis > rejected hypothesis`. This is radically smaller than training a translator.

### Phase G4 — constrained English realization

Provide final selected semantic graph to an API LLM:

```json
{
  "predicate": "vande",
  "agent": "implicit_first_person",
  "object": "Lord Bhairava",
  "epithet": "refuge of the helpless",
  "location": "in the heart",
  "manner": "with the mind absorbed in you",
  "forbidden_additions": true
}
```

## Recommended GitHub projects

| Project | Use | Link |
|---------|-----|------|
| Neural Sheaf Diffusion | Relation-specific diffusion, heterophily | [GitHub](https://github.com/twitter-research/neural-sheaf-diffusion) |
| NBFNet | Interpretable relational path propagation | [GitHub](https://github.com/DeepGraphLearning/NBFNet) |
| ULTRA / UltraQuery | Inductive reasoning across unseen KGs | [GitHub](https://github.com/DeepGraphLearning/ULTRA) |
| Graph-constrained Reasoning | Constraining LLM outputs to valid graph paths | [GitHub](https://github.com/RManLuo/graph-constrained-reasoning) |
| PyKEEN | Quick baselines for typed message passing | [GitHub](https://github.com/pykeen/pykeen) |
| Think-on-Graph | Training-free LLM graph traversal with beam search | [arXiv](https://arxiv.org/abs/2307.07697) |

## Final recommendation

Do **not** fine-tune a Sanskrit translation model yet.

Build:

```text
Sanskritree Evidence Graph
        +
Hard Lean Constraints
        +
Signed Typed Diffusion
        +
Sheaf Consistency Energy
        +
Path-Based Retrieval
        +
LLM English Renderer
```

The novel research contribution is not "a better Sanskrit translator." It is:

> **Translation as globally constrained inference over a provenance-preserving philological graph.**

The strongest mathematical framing:

> **A learned cellular sheaf over a heterogeneous textual-evidence graph, with formal constraints supplied by Lean and human adjudication supplying sparse supervision.**
