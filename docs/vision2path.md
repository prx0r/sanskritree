# Vision 2 — Path from Current State to Endgame

> You get there by treating the current system as the **first vertical slice**, not as a prototype to throw away.

The existing pipeline is:
```
immutable-ish corpus → parser ensemble → hypothesis graph → adjudication → semantic plan → constrained rendering → Lean audit
```

The endgame adds four things around that spine:
1. A durable annotation kernel
2. Commentary and claim graphs
3. Translation/concept/intertextual research products
4. A research agent that can only write from accepted evidence

---

## Phase 0 — Freeze Research Kernel v0.1

Before expanding architecture, create a reproducible baseline.

Freeze: database schema, 5 corpora, source hashes, FactorGraphV2 version, ByT5 version, Heritage wrapper, ontology, adjudications, VB test set, Lean environment, evaluation scripts.

```bash
make reproduce-v0.1
```

Should recreate: 16/16 tests, coverage table, M9 transfer metrics, Lean theorems, sample translations.

**Exit:** a fresh machine can reproduce current results from pinned inputs.

---

## Phase 1 — Finish empirical core

1.1 Fix known defects (action_detection → factor graph) — done
1.2 Heritage stress benchmark — done (18/20 success, defer local)
1.3 Complete M10.3: 150 adjudications → expand to 500
1.4 Gold/Silver v1 quality labels: GOLD (independent review), SILVER (one human), BRONZE (model-assisted), AUTO (unreviewed)

**Exit:** 500+ decisions with clean train/dev/test split and explicit provenance.

---

## Phase 2 — Annotation kernel

Introduce canonical primitives alongside existing tables:

```
Resource | ResourceVersion | Selector | Annotation | Relation | Agent | Activity | Adjudication
```

Special objects become typed annotations:
```
MorphAnalysis = Annotation
CompoundTree = Annotation
SemanticFrame = Annotation
CommentaryIntervention = Annotation + Claim
```

Store selectors with version hash + text + prefix/suffix + token IDs + canonical location, not offsets alone.

Build adapters from existing tables → canonical views. Run both representations until round-trip tests pass.

**Exit:** current corpora can be exported into the annotation kernel and reconstructed without loss.

---

## Phase 3 — Event sourcing

Every meaningful mutation becomes an event:
```
RESOURCE_IMPORTED | VERSION_CREATED | ANNOTATION_PROPOSED
ANNOTATION_REJECTED | ANNOTATION_ACCEPTED | CLAIM_CREATED
EVIDENCE_LINKED | CERTIFICATE_ISSUED | RELEASE_PUBLISHED
```

```bash
sanskritree replay --until EVENT_ID
```

Rebuilds database at any historical point.

**Exit:** full accepted state reconstructable from resource snapshots + event log.

---

## Phase 4 — Verification boundary

Formalize: exact source coverage, non-overlapping segmentation, one reading per exclusive locus, morphological compatibility, semantic-node grounding, required-node translation coverage, no rejected node realization, evidence-level publication rules.

Assumption manifest per certificate: human inputs vs parser proposals vs formal consequences vs foundational dependencies.

Mutation suite: every certified bundle generates corruptions (negation dropped, agent/patient swapped, source hash changed, unsupported prose inserted) — all must fail.

**Exit:** 100 reviewed passages produce reproducible Lean-backed audit bundles.

---

## Phase 5 — Commentary intervention corpus (first flagship)

Choose one root-text/commentary pair (stable Sanskrit, clear alignment, meaningful commentary, manageable, legal).

Start with: 100 root passages, 100-300 commentary units.

Intervention classes:
```
GLOSSES_WORD | GLOSSES_COMPOUND | SUPPLIES_ELLIPSIS | RESOLVES_REFERENCE
PROPOSES_SYNTAX | IDENTIFIES_DOCTRINE | QUOTES_TEXT | CITES_GRAMMAR
GIVES_EXAMPLE | REJECTS_READING | EXPANDS_RITUAL | PRESERVES_VARIANT | HISTORICAL_NOTE
```

Workbench: root passage, commentary passage, target highlighting, intervention type, structured claim, evidence links, accept/reject.

Target: 500-1,000 reviewed interventions, 10-15 classes, double annotation on 10-20%, agreement statistics.

**Exit:** publishable Commentary Intervention Benchmark v1.

---

## Phase 6 — Claims and nanopublications

Each accepted claim: Assertion + Provenance + Publication info.

Core claim relations: SUPPORTS | CONTRADICTS | QUALIFIES | DERIVES_FROM | EXPLAINS | REJECTS | PRESUPPOSES | SAME_AS | DISTINGUISHES

Evidence classes: ROOT_EXPLICIT | GRAMMATICALLY_REQUIRED | DIRECT_COMMENTARY | SAME_AUTHOR_PARALLEL | TRADITIONAL_DEVELOPMENT | MODERN_SCHOLARSHIP | SYSTEM_INFERENCE | EDITORIAL_SYNTHESIS

Export RDF/nanopublications later. Keep PostgreSQL internally.

**Exit:** every accepted commentary intervention exports as citable atomic claim with complete provenance.

---

## Phase 7 — Translation divergence engine

Pick one work with multiple legally usable translations.

Per unit store: Sanskrit source, selected analysis, English span, realized/omitted/added nodes, commentary-derived nodes, translation policy.

Difference taxonomy: TEXTUAL_READING | SEGMENTATION | MORPHOLOGY | COMPOUND_BRACKETING | SYNTAX | LEXICAL_SENSE | ELLIPSIS | COMMENTARY_IMPORT | OMISSION | EXPLICITATION | STYLE

For every verse: shared interpretation + disagreements + research dataset (500+ aligned units).

**Exit:** system explains why translations differ, not only displays different wording.

---

## Phase 8 — Concept history

Start with 5 concepts: vimarśa, spanda, śakti, ābhāsa, pratyabhijñā.

Per occurrence: lexeme, sense, syntactic frame, nearby concepts, predicate relations, commentary gloss, translation equivalent, date, author, school, confidence.

Concept page shows: timeline, occurrences, sense clusters, definitions, commentarial disagreements, translation history, related concepts, supporting passages, uncertainty.

**Exit:** one concept history reconstructable entirely from accepted passages and claims.

---

## Phase 9 — Intertextual discovery

Pipeline: exact n-grams → lemma sequence → sandhi-aware → rare compound/formula → BM25 → embeddings → cross-encoder → LLM → human adjudication.

Cautious relations: LEXICAL_OVERLAP | FORMULA_PARALLEL | PROBABLE_QUOTATION | EXPLICIT_QUOTATION | PARAPHRASE_CANDIDATE | POSSIBLE_DEPENDENCE | HISTORICALLY_PLAUSIBLE_DEPENDENCE

**Exit:** measured precision/recall on human-verified Sanskrit parallels.

---

## Phase 10 — Argument reconstruction + Lean

AIF-like objects: Claim, Premise, Inference, Conclusion, Conflict, Objection, Reply.

Indian extensions: pratijñā, hetu, dṛṣṭānta, upanaya, nigamana, vyāpti, pūrvapakṣa, siddhānta, hetvābhāsa, prasaṅga.

Start with 10-20 compact arguments. Lean proves formal conclusion follows from accepted reconstruction — does not prove Sanskrit correctness.

**Exit:** small corpus of formally reconstructed arguments with explicit assumptions.

---

## Phase 11 — Research services

Query services over accepted objects:
- every use of vimarśa with sense X
- where Jayaratha supplies missing syntax
- translations importing commentary into root
- all claims contradicted by another commentator
- probable quotations of a given verse

Stack: PostgreSQL (truth) + FTS/Tantivy + pgvector (semantic candidates) + object storage + Lean.

Postpone Neo4j until traversal is measurably painful.

**Exit:** common scholarly questions answered through graph/query operations, not free-form LLM inference.

---

## Phase 12 — Evidence-bound research agent

Only after thousands of accepted annotations.

Agent pipeline: research question → scope → retrieve primary passages + commentary + counterevidence → cluster claims → construct argument graph → evidence packet → adversarial review → human review → prose rendering.

Agent may propose claims, retrieve evidence, draft prose, flag contradictions. It may NOT accept claims, alter sources, mark publication-ready, issue certificates, or silently merge interpretations.

Multi-agent adversarial roles: citation checker, Sanskrit critic, chronology critic, counterevidence searcher, translation critic, logic critic.

Term: "multi-agent adversarial validation followed by expert review" — not "AI peer review."

**Exit:** every sentence in generated research links to accepted claims and exact evidence spans.

---

## Phase 13 — Standards and releases

Export: TEI XML, W3C Web Annotation, PROV-O, Nanopublication RDF, AIF, CoNLL-U, JSON-LD.

Each layer has its own quality status:
```
source text: gold
segmentation: gold
morphology: silver
syntax: model-proposed
commentary interventions: reviewed
concept links: experimental
```

**Exit:** third party can download, inspect and cite a stable corpus release.

---

## Concrete roadmap

| Release | What | Timeline |
|---------|------|----------|
| **0.1** Translation kernel | Frame wiring, Heritage benchmark, 500 adjudications, ranking baseline | Current |
| **0.2** Annotation substrate | Resource/Selector/Annotation model, event history, round-trip adapters | Next |
| **0.3** Commentary workbench | One root/commentary pair, 100 passages, intervention ontology, review UI | After 0.2 |
| **0.4** Claim corpus | Atomic claims, evidence links, nanopublication export, DOI | After 0.3 |
| **0.5** Translation criticism | Multiple translations, span alignment, difference taxonomy | After 0.4 |
| **0.6** Concept history | 5 concepts, sense adjudication, timelines | After 0.5 |
| **0.7** Intertextual retrieval | Quotation benchmark, retrieval pipeline, human-reviewed links | After 0.6 |
| **0.8** Argument formalization | AIF extension, 20 arguments, Lean reconstructions | After 0.7 |
| **1.0** Scholarship platform | Research query, claim graph, counterevidence, agent draft, audit | After 0.8 |

## What not to build yet

Neo4j | universal ontology | all traditions | autonomous agents | RLHF translator personalities | full Tantrāloka commentary | thousands of auto-generated senses

They become useful only after the annotation and claim substrate is proven.

## The best next vertical slice

From the exact current state:
1. Complete 150 adjudications → 500
2. Freeze Research Kernel v0.1
3. Introduce canonical Resource/Selector/Annotation primitives
4. Build one commentary workbench
5. Annotate 100 root/commentary passages
6. Publish first commentary-intervention dataset

That path moves directly from "working Sanskrit translation pipeline" to "academically distinctive research infrastructure."

The long-term product is not a translator and not a chatbot. It is:

> a versioned corpus of immutable sources, competing analyses, adjudicated interpretations, atomic claims, commentary interventions, translation decisions, concept histories and formal argument reconstructions—where every assertion is inspectable, attributable and reversible.
