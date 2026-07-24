# Vision 2 — Standards, Precedents and Architecture

> Nearly every difficult component already has a precedent. Nobody appears to have assembled them into the exact Sanskrit intellectual-history system you are imagining, but we do not need to invent the underlying machinery.

## Core principle

Sanskritree should not begin as one giant knowledge graph. It should begin as a **versioned annotation system over immutable text**, from which several graphs can be derived.

---

## Closest existing projects

| Project | Relevance | Lesson |
|---------|-----------|--------|
| **STAM** (Stand-off Text Annotation Model) | Annotation over immutable text, higher-order annotations, JSON serialization | Almost the foundation you independently designed. Consider using STAM internally or borrowing its object model. |
| **Coptic Scriptorium** | Linguistically annotated ancient-language corpus, annotation quality by layer | Version and score annotation layers independently. A passage may have gold text but silver morphology. |
| **OpenITI** | Large historical corpus management | Correction workflow is the permanent heart of the system, not a one-time preprocessing job. |
| **FoJin** | Buddhist text knowledge graph, cross-canon alignment | LLM should not be the final verifier. Add deterministic lexical evidence + human adjudication. |
| **EleutherIA** | Ancient philosophy GraphRAG platform | Product and interface reference. Sanskritree requires finer granularity (below the word). |
| **SPIRE** | Multi-agent humanities research framework | Validates the research-agent endgame. Phase 6 or 7, not the substrate. |

---

## Standards to adopt

| Standard | Use Case |
|----------|----------|
| **TEI XML** | Corpus interchange, critical editions, archival publication. Not the live application database. |
| **W3C Web Annotation** | Annotation export format. Body + target + motivation + provenance. |
| **PROV-O** | Provenance ontology: wasDerivedFrom, wasGeneratedBy, wasAttributedTo, used, etc. |
| **Nanopublications** | Atomic scholarly claims: assertion + provenance + publication info. Each accepted claim should be nanopublication-shaped. |
| **AIF** (Argument Interchange Format) | Argument representation. Extend with Indian philosophical forms (dṛṣṭānta, pūrvapakṣa, siddhānta, etc.). |

---

## Six canonical primitives

1. **Resource** — Immutable textual or visual object (work, edition, witness, transcription, commentary, etc.)
2. **Selector** — Stable target within a resource (character span, token range, verse, page region)
3. **Annotation** — Something asserted about one or more selectors (morphology, compound, gloss, translation)
4. **Claim** — A proposition that may be supported, contradicted, qualified or inferred
5. **Activity** — The process that produced an object (OCR, parser run, LLM extraction, human adjudication)
6. **Agent** — Person, model, parser, institution, editorial team

Specialized types become typed views: `MorphAnalysis = Annotation`, `CommentaryIntervention = Annotation + Claim`, etc.

---

## Architecture decisions

| Decision | Recommendation |
|----------|---------------|
| Graph database | Postpone Neo4j. PostgreSQL with recursive CTEs suffices until hundreds of thousands of accepted relations with stable edge semantics. |
| Selector anchoring | Never hash offsets alone. Store resource version hash + start/end + exact text + prefix + suffix + token IDs + canonical location. |
| LLM role | LLM may propose candidates, classify, search for counterevidence. Human adjudication is the final step. |
| Commentary | First academically distinctive project: a machine-auditable commentary intervention corpus for one root text + commentary. |
| Intertextuality | 8-stage pipeline: exact n-gram → sandhi-aware → lemma → compound → embedding → cross-encoder → LLM → human. Use strong relation labels (LEXICAL_OVERLAP, PROBABLE_QUOTATION, etc.), not "influence." |

---

## First publishable research objects

1. **Commentary Intervention Benchmark** — 500-1,000 units, 10-15 intervention classes, double annotation
2. **Translation Divergence Corpus** — source spans, translation spans, alignment, difference classification
3. **Intertextual Retrieval Benchmark** — verified quotations, near quotations, formula reuse, hard negatives
4. **Formal Argument Reconstructions** — 20 arguments in AIF + Lean

---

## Build order

### Milestone 1: Annotation kernel
Resource, ResourceVersion, Selector, Annotation, Agent, Activity, Adjudication, Relation. Immutable versions, source hashes, discontinuous spans, annotations targeting annotations.

### Milestone 2: One commentary workbench
One root text, one commentary, ~100 passages. Interface: highlight target → choose intervention type → structured claim → link evidence → accept/reject → view history.

### Milestone 3: Controlled retrieval
Exact search, lemma search, morphology-aware search, BM25, embedding candidates.

### Milestone 4: Claims and nanopublication export
Every accepted intervention → assertion + provenance + publication info + integrity hash. Published citable corpus with DOI.

### Milestone 5: Translation alignment
Semantic units + English-span realization. Lean certifies: all source claims realized, all translation spans licensed, commentary additions labelled.

### Milestone 6: Research agent
After hundreds of accepted annotations. Agent may retrieve, compare, identify disagreement, propose claims, draft from accepted claims. May not silently promote its output to accepted knowledge.

---

## Repository structure

```
sanskritree/
├── packages/
│   ├── textcore/          # resources, versions, selectors
│   ├── annotations/       # STAM-like annotation model
│   ├── provenance/        # PROV-inspired activities and agents
│   ├── claims/            # nanopublication-shaped claims
│   ├── sanskrit/          # morphology, sandhi, compounds, syntax
│   ├── commentary/        # intervention ontology
│   ├── translation/       # semantic and span alignment
│   ├── intertext/         # retrieval and adjudication
│   ├── arguments/         # AIF extension and Lean export
│   └── research/          # evidence-bound synthesis
├── apps/
│   ├── api/
│   ├── worker/
│   ├── workbench/
│   └── cli/
├── schemas/
│   ├── jsonschema/
│   ├── tei/
│   ├── rdf/
│   └── lean/
├── corpora/
│   └── manifests/
└── tests/
    ├── fixtures/
    ├── mutation/
    ├── roundtrip/
    └── certificates/
```
