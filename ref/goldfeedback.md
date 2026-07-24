# Gold Feedback — Sanskritree Architecture Corrections

> Do not treat the entire persistent evidence graph as one neural-style activation network. Construct a small, passage-local **factor graph** for each inference run, with canonical evidence retrieved from the larger corpus graph.

## Overall verdict

| Component | Verdict |
|-----------|---------|
| Weighted evidence graph | Yes |
| Convert 401,936 analyses into graph records | Yes, but not 401,936 independent semantic nodes |
| Naive additive tanh propagation | No |
| Binary polarity plus continuous magnitude | Yes |
| Hard and soft exclusion | Both, at different stages |
| Spanda verse/commentary separation | Yes, but use many-to-many anchors |
| PyG after nine verses | Too early |
| Hand-specified sheaf prototype | Yes |
| Learn weights from 27 simulated judgments | No |
| Structured LLM rendering | Yes, but two-stage JSON→English |
| Mitrasamgraha full aggregate score | No; stratify |
| Lean Layer B | Yes, with schema correction |
| Lean Layer C as written | Needs redesign |

---

## 1. Correct G0 architecture

### Do not duplicate canonical morphology 401,936 times

Need at least:

```
TOKEN_OCCURRENCE
LEXEME
MORPH_ANALYSIS_TYPE
TOKEN_ANALYSIS_HYPOTHESIS
```

Example:

```
TOKEN_OCCURRENCE
  bhairavanātham in Bhairavastava 1

TOKEN_ANALYSIS_HYPOTHESIS
  occurrence 103 analyzes as analysis type 482

MORPH_ANALYSIS_TYPE
  lemma=nātha
  gender=masculine
  number=singular
  case=accusative

LEXEME
  nātha
```

Thus:

```
TOKEN_OCCURRENCE
    └── HAS_HYPOTHESIS
          └── TOKEN_ANALYSIS_HYPOTHESIS
                    ├── INSTANCE_OF → MORPH_ANALYSIS_TYPE
                    ├── PROPOSED_BY → VIDYUT
                    └── RESOLVES_TO → LEXEME
```

### Separate the persistent graph from inference graphs

**Corpus evidence graph** (large, persistent):
- all passages, all token occurrences, all generated analyses
- all lexical senses, all commentaries, all parallel passages
- all provenance

**Passage factor graph** (small, generated for one run):
- one passage, its competing segmentations, its morphology candidates
- relevant compound trees, retrieved lexical senses
- relevant commentary evidence, semantic-frame alternatives
- translation candidates

Only the passage graph receives iterative belief inference.

---

## 2. Replace the proposed propagation function

### Problem A: order dependence

```python
target.belief += message  # WRONG — inside edge loop
```

Use synchronous updates:

```python
previous = beliefs.copy()
messages = compute_all_messages(previous)
next_beliefs = combine(priors, messages)
beliefs = damp(previous, next_beliefs)
```

### Problem B: uncontrolled accumulation

Belief should be recomputed from `fixed prior + current incoming messages`, not incremented forever.

### Problem C: double application of negative polarity

Your pseudocode computes `msg = tanh(source * weight * polarity)` then subtracts again. That penalizes negative edges twice.

### Problem D: MSE is not energy

Store both: `residual = mean((b_next - b_prev)²)` and `objective_energy = factor incompatibility score`.

### Better G0 update

Use log-odds or logits internally rather than raw probabilities. Use damping, clamping, and convergence tolerance.

```python
from dataclasses import dataclass
from math import exp
from typing import Iterable


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    polarity: int       # exactly -1 or +1
    magnitude: float    # [0, 1]
    reliability: float  # [0, 1]
    attenuation: float  # [0, 1]


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + exp(-x))


def propagate(
    nodes: Iterable[str],
    edges: Iterable[Edge],
    priors: dict[str, float],
    *,
    max_iter: int = 50,
    tolerance: float = 1e-6,
    damping: float = 0.35,
    clamp: float = 8.0,
) -> dict[str, float]:
    logits = {node: priors.get(node, 0.0) for node in nodes}
    edge_list = list(edges)

    for _ in range(max_iter):
        incoming = {node: 0.0 for node in nodes}

        for edge in edge_list:
            source_signal = 2.0 * sigmoid(logits[edge.source]) - 1.0
            message = (
                source_signal
                * edge.polarity
                * edge.magnitude
                * edge.reliability
                * edge.attenuation
            )
            incoming[edge.target] += message

        proposed = {
            node: max(
                -clamp,
                min(clamp, priors.get(node, 0.0) + incoming[node]),
            )
            for node in nodes
        }

        updated = {
            node: (1.0 - damping) * logits[node] + damping * proposed[node]
            for node in nodes
        }

        residual = max(abs(updated[n] - logits[n]) for n in nodes)
        logits = updated

        if residual < tolerance:
            break

    return {node: sigmoid(value) for node, value in logits.items()}
```

This is still only a baseline. Eventually, factors should score **joint assignments**, not merely nodes independently.

---

## 3. Polarity

Use:

```text
polarity ∈ {-1, +1}
magnitude ∈ [0, 1]
```

Do **not** use a single continuous field from -1 to 1.

Separate:
- source reliability
- passage-local applicability
- edge magnitude
- dependency discount

Edge fields:

```sql
polarity INTEGER CHECK (polarity IN (-1, 1)),
base_magnitude REAL CHECK (base_magnitude BETWEEN 0 AND 1),
source_reliability REAL CHECK (source_reliability BETWEEN 0 AND 1),
applicability REAL CHECK (applicability BETWEEN 0 AND 1),
independence_discount REAL CHECK (independence_discount BETWEEN 0 AND 1)
```

---

## 4. Exclusion edges

### Hard exclusion

For logically incompatible hypotheses:

```text
overlapping segmentations of the same character span
same token simultaneously accusative and nominative
karmadhāraya and tatpuruṣa as the committed compound
accepted and rejected status simultaneously
```

Represent as: `x_A + x_B ≤ 1` or `NOT (x_A AND x_B)`.

Do not implement as "set the other node's belief to zero." That makes whichever node updates first win.

Instead:
1. propagate evidence
2. calculate candidate scores
3. solve the constrained assignment
4. enforce exclusion in the solver

### Soft competition

For alternatives that can both remain plausible:

```text
vand = praise  vs  vand = worship
hṛdi = in the heart  vs  hṛdi = inwardly
```

Statuses: `accepted | acceptable_alternative | rejected | unresolved`

---

## 5. G0.5 checkpoint is too weak

"karmadharaya belief > tatpurusa belief" can pass for the wrong reason (e.g., manually seeded priors).

Require explanation audit:

```text
karmadhāraya ranks first
AND no direct answer was encoded in its prior
AND at least two independent evidence families support it
AND removing morphological compatibility lowers its margin
AND removing tradition/context evidence changes the score predictably
AND no excluded hypothesis survives the selected assignment
```

Ablation tests:

```text
full graph
minus Vidyut evidence
minus agreement factors
minus lexical evidence
minus human priors
```

Measure: `margin = score(correct) - score(best_incorrect)`

Real G0 gate covers all nine verses:

```text
top-1 accepted analysis accuracy
top-3 accepted recall
constraint violation rate
calibration
ablation sensitivity
```

---

## 6. Do not immediately graph all 401,936 analyses

Persist in normalized tables. Materialize only passage-local graphs on demand.

```text
SQLite canonical graph
→ SQL neighborhood query
→ passage-local graph projection
→ inference
→ save run and assignments
```

Query scope:

```text
current passage
+ its token analyses
+ selected same-work parallels
+ top-k lexical senses
+ commentary anchors
+ up to N independent external evidence paths
```

---

## 7. Spandakārikā commentary structure

Use commentary blocks plus many-to-many anchors. Not a single `parent_passage_id`.

```sql
passage_relations (
    source_passage_id TEXT,
    target_passage_id TEXT,
    relation_type TEXT,
    source_span_start INTEGER,
    source_span_end INTEGER,
    target_span_start INTEGER,
    target_span_end INTEGER,
    confidence REAL,
    provenance TEXT
);
```

Relation types: `COMMENTARY_ON | COMMENTS_ON_SPAN | INTRODUCES_SECTION | QUOTES | PARAPHRASES | EXPLAINS_TERM | APPLIES_TO_RANGE`

Example:

```text
commentary block C1
├── COMMENTARY_ON → SK 1.1
├── COMMENTARY_ON → SK 1.2
└── EXPLAINS_TERM → spanda in SK 1.2
```

---

## 8. G1 PyG should be delayed

Nine verses are insufficient. Labels are not independent (many nodes belong to same verse, analyses share surface forms).

### G1 activation gate

Do not train G1 until:

```text
≥100–200 adjudicated passages
≥1,000–3,000 candidate hypotheses
≥200 genuine positive/negative preference pairs
multiple works or registers
passage-level train/test splits
```

Before G1, run:
```text
hand-weighted factor scorer
logistic regression
gradient-boosted trees
pairwise ranking model
path-ranking baseline
```

Split strategy: leave-one-verse-out for Bhairavastava, leave-one-work-out for multiple works. Never randomly split nodes from same passage.

---

## 9. G2 sheaf consistency — hand-specify first

But not as dense linear matrices. Use sparse compatibility relations:

```python
CASE_ROLE_COMPATIBILITY = {
    ("nominative", "agent"): 0.8,
    ("nominative", "predicate"): 0.7,
    ("accusative", "object"): 0.9,
    ("accusative", "goal"): 0.5,
    ("instrumental", "instrument"): 0.8,
    ("instrumental", "manner"): 0.9,
    ("instrumental", "agent_passive"): 0.7,
    ("locative", "location"): 0.9,
    ("locative", "domain"): 0.6,
}
```

Condition on selected predicate/frame.

### Sheaf prototype structure

```text
Morphology stalk: case, number, gender, person, voice, tense/mood
Syntactic-role stalk: agent, patient, object, instrument, manner, location, qualifier
Semantic-frame stalk: predicate, participants, circumstance, modality
Translation-alignment stalk: direct, implicit, paraphrastic, contextual, omitted, unsupported
```

### Do not combine belief and energy problematically

This formula is wrong:

```text
α·G0_belief + (1-α)·(1-energy)
```

Normalize at candidate-set level:

```text
score(h) = evidence_logit(h) - λ × normalized_consistency_energy(h)
P(h) = softmax(score(h))
```

Report evidence and consistency separately.

### G2 checkpoint

```text
correct candidate has lowest normalized energy
correct candidate remains lowest under reasonable λ range
energy decomposition identifies the expected incompatible edge
incorrect candidate fails for an interpretable reason
```

For "lord of Bhairava":

```text
compound interpretation implies two related entities
+ selected semantic frame supplies one entity as worship object
+ no passage-local evidence supplies a second Bhairava possessor
= high entity-consistency energy
```

---

## 10. G3 pathway reliability

### Do not train on simulated human judgments

Simulated judgments create a closed loop: you define the answer → simulation repeats it → model learns it → checkpoint says it agrees.

Use simulated labels only as software fixtures.

### 27 judgments are too few

With 9 verses × 3 candidates, pairwise ranking examples are heavily dependent. A single rank reversal changes Spearman radically.

### Correct G3 target

Start with source and relation calibration:

```text
engine reliability by feature category
relation reliability
distance attenuation
provenance-family discount
```

Use hierarchical model:

```text
global source reliability
+ register-specific deviation
+ analysis-type-specific deviation
```

### G3 activation gate

```text
≥200 real adjudicated preference pairs
≥3 works
≥2 registers
no passage leakage
confidence intervals on learned weights
```

### Evaluation

```text
pairwise accuracy
mean reciprocal rank
NDCG
top-1 accepted rate
Brier score
expected calibration error
```

---

## 11. G4 constrained rendering — use JSON mode first, then fluent

Two stages.

### Stage A — constrained semantic realization plan

```json
{
  "segments": [
    {
      "segment_id": "s1",
      "source_nodes": ["compound:bhairavanatha:karmadharaya"],
      "realization": "Lord Bhairava",
      "realization_type": "direct"
    },
    {
      "segment_id": "s2",
      "source_nodes": ["compound:anathasaranya"],
      "realization": "refuge of the helpless",
      "realization_type": "direct"
    }
  ],
  "ordering": ["s1", "s2", "s4", "s3", "s5"],
  "additions": [],
  "omissions": [],
  "uncertainties": []
}
```

Validate:

```text
every source-required node is represented
every output segment cites valid nodes
no rejected node is cited
all additions are explicitly typed
no segment is unattached
```

### Stage B — fluent rendering

Use a second renderer to produce fluent English using **only the approved segments**.

Post-hoc NER is validation only, not source of truth. NER fails on paraphrases, implicit subjects, discontinuous spans, fused realizations.

Use [Outlines](https://github.com/dottxt-ai/outlines) or similar for JSON schema-constrained generation.

### G4 checkpoint

Measure:

```text
unsupported addition precision
unsupported addition recall
source-node coverage
rejected-node leakage
alignment validity
human fluency
human adequacy
```

Compare:
```text
unconstrained prompt
JSON-planned graph-constrained rendering
graph-constrained rendering with final fluency pass
```

Ensure reducing additions does not cause omissions.

---

## 12. Lexical sense inventory — lazy, not bulk

Do not create senses for all 5,465 lemmas immediately.

### Lazy sense induction

```text
sense entry is created when a lemma appears in an active work
or when enough evidence requires a distinction
```

Sequence:
1. Retrieve Mitrasamgraha glosses
2. Normalize inflection and English variants
3. Separate gloss, paraphrase, contextual expansion
4. Cluster provisionally
5. Partition evidence by source/register/tradition
6. Create a sense only when evidence supports a meaningful distinction
7. Human-curate high-centrality and high-ambiguity terms first

Prioritize by: `frequency × ambiguity × downstream centrality × translation risk`

### Important distinction

Store separately:

```text
English gloss observation
lexical sense hypothesis
translation realization
```

These are not interchangeable.

---

## 13. Lean Layer B correction

Use:

```lean
inductive GrammaticalCase
  | nominative | accusative | instrumental | dative
  | ablative | genitive | locative | vocative

inductive FrameRole
  | agent | patient | object | instrument
  | manner | location | beneficiary | qualifier

structure MorphAnalysis where
  tokenId : Nat
  lemma : String
  grammaticalCase : Option GrammaticalCase

structure RoleBinding where
  role : FrameRole
  entityId : Nat
  evidenceTokenIds : List Nat

structure RitualAction where
  action : String
  bindings : List RoleBinding
  sequenceIndex : Nat
```

Define compatibility over a selected analysis environment:

```lean
def compatibleCaseRole :
    GrammaticalCase → FrameRole → Prop
  | .accusative, .object => True
  | .instrumental, .instrument => True
  | .instrumental, .manner => True
  | .locative, .location => True
  | _, _ => False
```

Do not theoremize the false universal "praise + object → object must always be accusative." The theorem should verify that the **chosen binding has an explicitly licensed case-role compatibility under the selected construction grammar**.

---

## 14. Lean Layer C correction

```lean
inductive Polarity
  | affirmed
  | denied

structure Proposition where
  subject : Entity
  relation : RelationType
  object : Entity
  modality : Modality
  polarity : Polarity
  evidenceChain : List EvidenceId
```

Then:

```lean
def sameContent (p q : Proposition) : Prop :=
  p.subject = q.subject ∧
  p.relation = q.relation ∧
  p.object = q.object ∧
  p.modality = q.modality

def contradicts (p q : Proposition) : Prop :=
  sameContent p q ∧ p.polarity ≠ q.polarity
```

Avoid putting `Float` confidence inside the logical proposition. Confidence belongs in the evidence database. Lean should verify proposition structure and contradiction relations, not pretend a floating score is epistemically proved.

---

## 15. Stratify Mitrasamgraha

Stratify by:

```text
register/domain
sentence versus verse
source length
compound density
morphological ambiguity
technical-term density
reference literalness
reference age/style
presence of contextual additions
```

Domain labels:

```text
vedic | epic | purāṇic | philosophical | buddhist | jain
grammar/śāstra | stotra/devotional | narrative
tantric or tantra-adjacent | unknown
```

Score: `overall macro-average across strata`, `micro-average`, `per-domain`, `per-ambiguity bucket`.

Build a separate manually reviewed **Tantric challenge set**.

---

## 16. Revised implementation order

### Phase A — graph correctness

```
A1. Correct graph ontology and migration
A2. Canonical/occurrence node separation
A3. Passage-local graph projection
A4. Hard constraint factors
A5. Stable synchronous propagation
A6. Full Bhairavastava annotation
A7. Ablation and calibration report
```

### Phase B — translation traceability

```
B1. Token/span alignment
B2. Unsupported-addition factors
B3. Structured JSON realization plans
B4. Final fluent renderer
B5. Evaluation suite
```

Do this **before PyG**.

### Phase C — corpus expansion

```
C1. Spandakārikā ingestion
C2. Commentary many-to-many anchoring
C3. Human adjudication interface
C4. Lazy lexical-sense inventory
C5. Gold decision accumulation
```

### Phase D — symbolic consistency

```
D1. Lean Layer B
D2. Semantic-frame constraints
D3. Hand-specified sheaf/compatibility energy
D4. Candidate-level energy explanations
```

### Phase E — learned scoring

Only after enough gold data:

```
E1. Logistic and tree baselines
E2. Pairwise pathway-reliability model
E3. Path-ranking model
E4. R-GCN baseline
E5. HGT baseline
E6. Learned sheaf maps
```

---

## 17. Final answers

1. **Polarity:** binary ±1. Put strength in separate continuous fields.
2. **Exclusion:** hard constraints for logically incompatible analyses; soft competition for acceptable alternatives. Never let update order decide exclusion.
3. **Spanda commentary:** preserve paragraph/block units and link many-to-many to verses and spans. Do not rely only on `parent_passage_id`.
4. **Sheaf maps:** hand-specified first. Use sparse, relation-conditioned compatibility maps. Learn only after substantial real adjudication.
5. **LLM rendering:** constrained JSON realization plan first, then separate fluent-English pass. Post-hoc NER is validation only.
6. **Mitrasamgraha:** score all pairs, report stratified macro and micro. Build separate manually reviewed Tantra challenge set.
7. **Move G4 before G1. Move G1/G3 after corpus adjudication.**

> Structured rendering produces useful translations and valuable gold decisions. A GNN trained on nine verses and simulated preferences mainly learns your initial hand-coded assumptions in a less interpretable form.
