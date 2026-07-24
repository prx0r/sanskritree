# Sanskritree Mechanics Reference

> A provenance-aware, tradition-scoped, heterogeneous factor graph for joint philological inference, using energy minimization and formal constraints to select globally coherent interpretations, with language models restricted to proposing hypotheses and realizing accepted semantic structures into English.

## The closest existing Sanskrit blueprint

Krishna et al., "A Graph-Based Framework for Structured Prediction Tasks in Sanskrit" ([ACL Anthology](https://aclanthology.org/2020.cl-4.4/)):

1. Sanskrit Heritage enumerates possible segmentations
2. Each unique candidate analysis becomes a graph node
3. Edges connect analyses that may coexist
4. Conflicting segmentations are not connected
5. An energy function scores possible global structures
6. Inference selects the lowest-energy valid structure
7. Sanskrit grammatical constraints prune impossible structures

The paper stresses why this is necessary: a short Sanskrit string can generate segmentation, morphological and syntactic ambiguity simultaneously, and these levels constrain one another. One example required selecting one correct segmentation from **59,616 exhaustive segmentations**.

That implies the correct conceptual object is not:
```
sentence → tokenization → morphology → syntax
```
It is:
```
sentence → graph of possible complete analyses → globally consistent solution
```

## What Sanskritree adds beyond that paper

Their graph ends at: segmentation, morphology, dependency structure, word order, prosody.

Your graph continues through: compound structure, lexical sense, tradition-specific sense, semantic frame, parallel passage, commentarial gloss, translation alignment, English realization, formal proposition.

Sanskritree = **The Krishna graph architecture expanded from morphosyntax into critical philology and translation.**

## The ideal is five interoperating graphs

```
G₀  Textual witness graph    — externally recoverable textual facts
G₁  Linguistic hypothesis graph — segmentation, morphology, syntax, compounds
G₂  Semantic and lexical graph — lexemes, senses, tradition scope, frames
G₃  Translation evidence graph — alignments, additions, omissions
G₄  Formal and explanatory graph — Lean decision objects, propositions
```

### G₀ — Textual witness graph

Nodes: WORK, RECENSION, EDITION, MANUSCRIPT, PAGE, PASSAGE, PASSAGE_READING, CHARACTER_SPAN, OCR_OBSERVATION, EDITORIAL_EMENDATION

Edges: HAS_EDITION, HAS_PASSAGE, WITNESSES, VARIANT_OF, EMENDS, OCR_DERIVED_FROM, PARALLEL_TO, QUOTED_IN

Nothing learned or inferred overwrites this layer. All readings coexist; a user selects a working reading.

### G₁ — Linguistic hypothesis graph

Nodes: SPAN_HYPOTHESIS, SEGMENTATION_HYPOTHESIS, TOKEN_OCCURRENCE, MORPH_ANALYSIS, LEMMA_ANALYSIS, SANDHI_DERIVATION, DEPENDENCY_ARC, KARAKA_ROLE, COMPOUND_PARSE, ANVAYA_ORDER

**Key design: separate occurrences from analyses.** The same surface token has multiple ANALYZES_AS edges. This mirrors the multigraph improvement in joint Sanskrit morphology/dependency parsing ([ACL Anthology](https://aclanthology.org/2020.emnlp-main.388.pdf)) — merging analyses at the surface-token level while retaining distinct edges simplified inference and enabled exact minimum-spanning-tree search.

Hard incompatibility edges: EXCLUDES, OVERLAPS_INVALIDLY, REQUIRES, AGREES_WITH, GOVERNS, LICENSES.

### G₂ — Semantic and lexical graph

Nodes: LEXEME, LEXICAL_SENSE, TRADITION_SCOPED_SENSE, CONCEPT, ENTITY, EVENT, STATE, SEMANTIC_FRAME, FRAME_ROLE, RITUAL_OPERATOR, DOCTRINAL_PROPOSITION, METAPHOR_INTERPRETATION

**Do not create one universal sense for a word.** Use: lemma → sense → tradition-scoped realization → passage evidence.

Example:
```
kula
├── ordinary: family, clan
├── grammatical: aggregate/class
├── Śākta: power complex
├── Kaula: initiated lineage/body-totality
└── Kubjikā: system-specific technical sense
```

Each sense needs: ATTESTED_BY_PASSAGE, GLOSSED_BY_COMMENTARY, USED_BY_AUTHOR, SUPPORTED_BY_PARALLEL, CONTRASTED_WITH.

The sanitized [Ambuda DCS data](https://github.com/ambuda-org/dcs) (CC-BY) is useful for general lexical distributions, but must not overwhelm rarer tradition-specific evidence.

### G₃ — Translation evidence graph

Translations are not strings attached to passages. They are structured claims about alignments.

Nodes: TRANSLATION, TRANSLATION_SPAN, GLOSS, EXPLICIT_ADDITION, IMPLICIT_REALIZATION, OMISSION, PARAPHRASE, INTERPRETIVE_NOTE

Edges: ALIGNS_TO_TOKEN, REALIZES_SENSE, REALIZES_FRAME_ROLE, ADDS_FROM_CONTEXT, OMITS, PARAPHRASES, DEPENDS_ON, CONTRADICTS_READING

Candidate C from Bhairavastava:
```
"the one consciousness"
    └── ADDS_FROM_CONTEXT
        └── no verse-local evidence
```

### G₄ — Formal and explanatory graph

Lean operates here. Nodes: DECISION_OBJECT, CONSISTENCY_CONSTRAINT, SEMANTIC_PROPOSITION, LEAN_TYPE, LEAN_PROOF, PROOF_FAILURE, ASSUMPTION.

## Use a factor graph before a GNN

Variables:
```
S_i = segmentation choice
M_i = morphology choice
D_ij = dependency relation
C_i = compound parse
L_i = lexical sense
F = semantic frame
T_j = translation alignment
```

Factors encode compatibility:
```
φ_surface(S)
φ_morph(S, M)
φ_agreement(M_i, M_j)
φ_dependency(M, D)
φ_compound(C, M, context)
φ_sense(L, tradition, context)
φ_frame(F, D, L)
φ_translation(T, F, L)
φ_commentary(L, commentary)
```

Score of a complete interpretation y:

```
E(y) = Σ_f E_f(y_f)
```

Preferred interpretation:
```
y* = argmin_{y ∈ Y_valid} E(y)
```

This is the energy-based Sanskrit framework expanded to higher philological layers.

**Why this precedes graph diffusion:** A factor graph tells you what the variables are, which combinations are legal, what evidence contributes, and what global configuration is being optimized. A GNN without this structure merely learns correlations over your database graph.

## Exact inference where possible

| Problem | Structure | Suggested inference |
|---------|-----------|-------------------|
| Character segmentation | lattice/DAG | shortest path / DP |
| Morphology selection | factor graph | belief propagation / ILP |
| Dependency parsing | directed graph | Chu–Liu/Edmonds MST |
| Compound parsing | constituency tree | CKY/chart parsing |
| Nested compounds | dependency tree | DepNeCTI-style parsing |
| Sense selection | heterogeneous evidence graph | weighted ranking / BP |
| Complete translation | constrained factor graph | beam search, ILP or MaxSAT |
| Formal consistency | typed terms | Lean |

The joint Sanskrit parser switched to a multigraph so exact Chu–Liu/Edmonds inference could replace approximate search. Use exact symbolic inference whenever the subproblem has a known combinatorial structure.

## Nested compounds need their own subgraph

DepNeCTI demonstrates that a Sanskrit compound is not adequately represented by a flat label like `tatpuruṣa`. Multi-member compounds require a nested tree. ([ACL Anthology](https://aclanthology.org/2023.findings-emnlp.914/))

Represent `tvan-maya-citta-tā` as alternative trees:
```
A: [[tvan-maya] citta] tā
B: [tvan [maya-citta]] tā
C: [tvan-maya [citta-tā]]
```

Each internal node: `{span, relation, head, confidence, context_evidence, grammar_evidence}`.

SaCTI found compound classification improves when morphology and dependency parsing are learned jointly as auxiliary tasks. ([ACL Anthology](https://aclanthology.org/2022.coling-1.358/))

## Sanskrit-specific systems to incorporate

| System | Role | Access |
|--------|------|--------|
| **Vidyut** | High-speed candidate generator | ✅ Integrated |
| **Sanskrit Heritage Reader** | High-recall candidate generator + derivational evidence | [Python wrapper](https://github.com/hrishikeshrt/heritage) |
| **DCS** | General lexical distribution evidence | [Ambuda CC-BY](https://github.com/ambuda-org/dcs) |
| **SanskritShala** | Additional hypothesis engine + comparison baseline | [ACL](https://aclanthology.org/2023.acl-demo.10/) |
| **Saṃsādhanī** | Paninian kāraka/śābdabodha constraints | [ACL](https://aclanthology.org/W19-7502/) |

## The graph should be heterogeneous and hypergraphic

Binary edges are insufficient for many Sanskrit decisions. Agreement involves adjective + noun + case + number + gender + compound analysis — an n-ary relationship.

Use either explicit factor nodes or hyperedges:
```
ANALYSIS NODE ─┐
ANALYSIS NODE ─┼→ AGREEMENT_FACTOR
ANALYSIS NODE ─┘
```

## Separate four kinds of strength

| Weight | What | Example |
|--------|------|---------|
| `prior_weight` | Plausibility before local evidence | Frequency of instrumental manner |
| `evidence_weight` | Direct evidence here | Commentary glosses the compound |
| `compatibility_weight` | Fit with adjacent decisions | Accusative agrees with object role |
| `reliability_weight` | Historical trustworthiness | Vidyut 91% correct on reviewed forms |

```
score(h) = w_p·P(h) + w_e·E(h) + w_c·C(h) + w_r·R(h) − penalties(h)
```

## Provenance independence

Ten dependent sources are not ten pieces of evidence. If translation B copies A, dictionary C derives from A, article D quotes B — the graph sees one evidence family, not four confirmations.

Add `evidence_family_id`, `derived_from_source_id`, `independence_depth`. Discount correlated support:

```
E_combined = 1 − Π_{g∈independent groups} (1 − E_g)
```

Within one dependent group, use the strongest item rather than summing.

## Where graph diffusion belongs

1. **Retrieval diffusion** — activate current passage + lemmas + tradition, diffuse through PARALLEL_TO / QUOTED_IN / GLOSSED_BY / SAME_SENSE, return strongest explanatory paths.

2. **Confidence diffusion** — accepted decision updates related hypotheses with distance decay: `m = a_u · w_uv · r_uv · λ^d`, only through explicitly propagating relation types.

3. **Global consistency diffusion** — sheaf-style or relation-specific diffusion so morphology, syntax and translation states map into compatible spaces rather than averaging blindly. Experimental layer only.

## Where a GNN belongs

Eventually train a small heterogeneous GNN to estimate factor energies. Input: candidate graph for a passage. Output: score for each hypothesis + compatibility relation.

Recommended order:
1. **Logistic factor scorer** — engine identity, lemma frequency, case compatibility, distance, tradition, commentary support, parallel support, compound class
2. **Path Ranking Algorithm** — learned typed paths (passage → lemma → same-tradition passage → accepted sense)
3. **Relational GNN** — R-GCN, HGT, NBFNet-style path reasoning
4. **Sheaf diffusion** — only after sufficient gold decisions exist

## Proposed V3 database structure

Keep V2 tables. Add graph-normalized layer:

```sql
graph_nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    payload_ref_table TEXT,
    payload_ref_id TEXT,
    immutable BOOLEAN,
    created_at TEXT
);

graph_edges (
    edge_id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    polarity INTEGER NOT NULL,
    prior_weight REAL,
    evidence_weight REAL,
    compatibility_weight REAL,
    learned_reliability REAL,
    provenance_id TEXT,
    evidence_family_id TEXT,
    status TEXT,
    created_at TEXT
);

factor_nodes (
    factor_id TEXT PRIMARY KEY,
    factor_type TEXT NOT NULL,
    hard_constraint BOOLEAN NOT NULL,
    energy_function TEXT,
    parameters_json TEXT
);

factor_members (
    factor_id TEXT,
    node_id TEXT,
    role TEXT,
    PRIMARY KEY (factor_id, node_id, role)
);

inference_runs (
    run_id TEXT PRIMARY KEY,
    passage_id TEXT,
    algorithm TEXT,
    model_version TEXT,
    constraint_version TEXT,
    created_at TEXT
);

inference_assignments (
    run_id TEXT,
    variable_node_id TEXT,
    selected_hypothesis_id TEXT,
    score REAL,
    rank INTEGER,
    explanation_json TEXT
);
```

Do not replace normalized relational schema with Neo4j. SQLite/PostgreSQL remains canonical; export projected graph for algorithms.

## Ideal repository architecture

```
src/sanskritree/
├── corpus/
│   ├── ingestion.py
│   ├── witnesses.py
│   └── provenance.py
├── generators/
│   ├── vidyut.py
│   ├── heritage.py
│   ├── dcs.py
│   ├── sanskritshala.py
│   └── samsadhani.py
├── graph/
│   ├── types.py
│   ├── builder.py
│   ├── factors.py
│   ├── compatibility.py
│   ├── provenance.py
│   └── projection.py
├── inference/
│   ├── exact.py
│   ├── belief_propagation.py
│   ├── ilp.py
│   ├── path_ranking.py
│   ├── diffusion.py
│   └── explanations.py
├── semantics/
│   ├── senses.py
│   ├── compounds.py
│   ├── karaka.py
│   ├── frames.py
│   └── tradition_scope.py
├── translation/
│   ├── alignments.py
│   ├── realization.py
│   ├── candidate_audit.py
│   └── evaluation.py
└── formal/
    ├── export_lean.py
    ├── decision_objects.py
    └── compile.py
```

## The first practical experiment

All nine verses of Bhairavastava.

**Build candidate graphs:** all Vidyut analyses, Heritage analyses, dependency alternatives, compound trees, 2–5 lexical senses per important lemma, semantic-frame candidates, three translation candidates.

**Human gold labels:** accepted, acceptable alternative, rejected, undecidable. Do not force every ambiguity into one answer.

**Compare four inference systems:**
- A. Engine confidence only
- B. Hand-weighted factor graph
- C. Learned logistic energy scorer
- D. Path-ranking scorer

**Measure:** top-1 accepted rate, top-3 recall, global valid-analysis rate, unsupported-addition detection, calibration, human correction time.

## The most important design principle

The ideal Sanskritree object is not a translation. It is a **complete interpretation state**:

```json
{
  "textual_reading": "...",
  "segmentation": [],
  "morphology": [],
  "dependency_graph": [],
  "compound_trees": [],
  "lexical_senses": [],
  "semantic_frame": {},
  "translation_alignment": [],
  "english_realization": "...",
  "formal_constraints": [],
  "unresolved_alternatives": [],
  "evidence_paths": []
}
```

A translation is one human-readable projection of that state.

## Bottom line

**Do now:**
- Heterogeneous factor graph
- Energy-based structured inference
- Exact algorithms where available
- Paninian constraints
- Competing hypothesis preservation
- Path-based evidence

**Add later:**
- Relation-specific GNN scoring
- Graph diffusion for retrieval
- Sheaf consistency
- Learned source/path reliability

**Avoid:**
- One giant graph embedding
- One confidence number per edge
- End-to-end Sanskrit→English fine-tuning
- Sequential irreversible pipeline
- Majority-vote tool fusion
- LLM-generated analysis without candidate provenance

## References

- Krishna et al., "A Graph-Based Framework for Structured Prediction Tasks in Sanskrit" ([ACL](https://aclanthology.org/2020.cl-4.4/))
- "Keep it Surprisingly Simple: A Simple First Order Graph Based Parsing Model for Joint Morphosyntactic Parsing in Sanskrit" ([ACL](https://aclanthology.org/2020.emnlp-main.388.pdf))
- "Free as in Free Word Order: An Energy Based Model for Word Segmentation and Morphological Tagging in Sanskrit" ([ACL](https://aclanthology.org/D18-1276/))
- DepNeCTI: Dependency-based Nested Compound Type Identification ([ACL](https://aclanthology.org/2023.findings-emnlp.914/))
- SaCTI: Multi-Task Learning for Compound Type Identification ([ACL](https://aclanthology.org/2022.coling-1.358/))
- SanskritShala: Neural Sanskrit NLP Toolkit ([ACL](https://aclanthology.org/2023.acl-demo.10/))
- Heritage.py Python Interface ([GitHub](https://github.com/hrishikeshrt/heritage))
- Ambuda DCS sanitized data ([GitHub](https://github.com/ambuda-org/dcs))
- Validation of DCS using Heritage tools ([arXiv](https://arxiv.org/abs/2005.06545))
- Dependency Parser for Sanskrit Verses ([ACL](https://aclanthology.org/W19-7502/))
