# Visionary — Translation Manifold + Verification Architecture

## Audit boundary principle

> The model may propose interpretations, but it cannot publish prose unless every content-bearing span is licensed by an approved semantic node and provenance path.

## Lean certifies the chain, not the Sanskrit meaning

```
Human/graph system: Is this interpretation philologically defensible?
Lean: Given these declared decisions, is the resulting bundle complete, consistent, grounded and correctly labelled?
```

## Epistemic status taxonomy (replace all generic PROVED fields)

Use three separate dimensions:

```text
proposal_status: MODEL_PROPOSED | HUMAN_ACCEPTED | HUMAN_REJECTED | UNRESOLVED
formal_status: KERNEL_PROVED | CONDITIONALLY_PROVED | STRUCTURALLY_VERIFIED | TYPECHECKED_WITH_SORRY | UNVERIFIED  
evidence_status: ROOT_EXPLICIT | GRAMMAR_REQUIRED | DIRECT_COMMENTARY | PARALLEL_INFERENCE | EDITORIAL_INFERENCE
```

Example: `HUMAN_ACCEPTED | CONDITIONALLY_PROVED | DIRECT_COMMENTARY`

## Trusted architecture

```
untrusted model output → strict schema → deterministic canonicalizer → finite decidable predicates → native_decide → Lean kernel certificate
```

Generated Lean should be boring. Boring is good.

## Mutation testing

For every accepted bundle, generate corrupt versions: delete span, overlap segments, reverse agent/patient, remove negation, add unsupported content, use rejected sense. All must fail.

## Independent validators at every boundary

| Boundary | Check 1 | Check 2 |
|----------|---------|---------|
| Candidate generation | engine output | independent normalization validation |
| Morphology | factor score | grammatical constraint checker |
| Semantic frame | model proposal | source-role grounding checker |
| Rendering | LLM prose | deterministic span licensing |
| Formal certificate | generated theorem | CI inspection for axioms/sorry/unsafe |

## Assumption firewall

```json
{
  "trusted_inputs": ["source_text_hash", "human_selected_reading", "human_selected_morphology"],
  "derived_objects": ["segmentation_coverage", "semantic_plan", "translation_alignment"],
  "formal_consequences": ["all_required_nodes_realized", "no_rejected_nodes_realized"]
}
```

CI should run `#print axioms` on every bundle and compare against the allowlist.

## Forbidden constructs in generated Lean

`sorry | admit | axiom | unsafe | implemented_by | opaque placeholder | untrusted external oracles`

## English span realization relations

```
DIRECT_TRANSLATION | GRAMMATICAL_SUPPLEMENT | PARAPHRASE | TECHNICAL_GLOSS | COMMENTARIAL_EXPLICATION | EDITORIAL_TRANSITION
```

## Information-flow typing

Evidence levels as security labels:

```text
ROOT_EXPLICIT ≤ LITERAL
GRAMMAR_REQUIRED ≤ LITERAL  
DIRECT_COMMENTARY ≰ LITERAL
SYSTEM_INFERENCE ≰ LITERAL
```

## Negative evidence

Every proof bundle should expose strongest rejected alternative + rejection reasons + margin.

## Release levels

```
DRAFT — Machine-generated, structurally audited
ADJUDICATED — Core decisions human-reviewed
CERTIFIED — No unsupported spans, complete provenance, Lean kernel check
DUAL_REVIEWED — Two qualified readers
PUBLICATION_READY — Textual, linguistic, semantic and translation review complete
```

## Critical implementation order

1. Remove all ambiguous PROVED outputs
2. CI rejects sorry, undeclared axioms, unsafe constructs
3. Assumptions manifest + trusted-base report
4. Formalize source coverage, selection exclusivity, node-to-English coverage
5. Mutation testing
6. Information-flow rules for literal/commentarial/editorial claims
7. Human-readable certificate page
8. Adversarial tests: wrong plan + valid Lean proof = STRUCTURALLY_VERIFIED, PHILOLOGICALLY_UNREVIEWED

## The precise promise

Not: "This machine has proved the uniquely correct translation."

But: "Every published claim is traceable to an immutable source, declared philological judgment or explicitly labelled inference. Every Sanskrit span and English content span is accounted for. No rejected or undeclared claim enters the selected publication layer, and the resulting evidence chain has been independently checked by deterministic validators and the Lean kernel."

---

# Translation Manifold

> Different interpretive paths through a shared Sanskrit evidence graph.

## Core concept

A translation is not stored as "Sanskrit verse → English sentence." It becomes:

```text
edition reading
+ segmentation choices
+ morphological choices
+ compound bracketing
+ lexical senses
+ supplied ellipses
+ doctrinal assumptions
+ English realization policy
= translation path
```

Two translators can differ at precisely identifiable points.

## Translation-difference taxonomy

```
TEXTUAL_VARIANT | SEGMENTATION_DIFFERENCE | MORPHOLOGICAL_DIFFERENCE
SYNTACTIC_DIFFERENCE | COMPOUND_BRACKETING | LEXICAL_SENSE
REFERENT_RESOLUTION | ELLIPSIS_SUPPLIED | DOCTRINAL_INTERPRETATION
COMMENTARIAL_INFLUENCE | TARGET_STYLE | TERMINOLOGY_POLICY
```

## Translation policies

| Policy | Optimizes for |
|--------|--------------|
| Scholarly literal | source structure, technical precision, minimal supplied material |
| Philological readable | accuracy, natural English, moderate explicitation |
| Practitioner | experiential clarity, instructional usability |
| Philosophical | ontological distinctions, argument structure |
| Poetic | rhythm, imagery, emotional force |
| Commentary-integrated | root text + declared commentarial interpretation |

## Comparison engine

Per-verse structured output:

```text
Shared core proposition
Textual divergence
Grammatical divergence
Lexical divergence
Interpretive divergence
Assessment
```

## Translation genome

```json
{
  "literalness": 0.82,
  "commentary_dependence": 0.71,
  "sanskrit_term_retention": 0.64,
  "doctrinal_explication": 0.81,
  "ambiguity_preservation": 0.43
}
```

## Evaluation dimensions

source_fidelity | grammatical_defensibility | lexical_evidence | commentary_fidelity | terminological_consistency | clarity | literary_force | uncertainty_honesty

## Development phases

```
T1 — Translation ingestion (align to chapter/verse/reading)
T2 — Difference decomposition (classify divergences)
T3 — Translation policy model (controllable dimensions)
T4 — Comparative critic (rank per dimension)
T5 — Commentary synthesis (from approved evidence classes)
T6 — Preference learning (multi-dimensional reward)
T7 — Translation manifold explorer (interactive branching UI)
```

## Final architecture

```
Layer 1 — Textual criticism (What Sanskrit text?)
Layer 2 — Linguistic analysis (How constructed?)
Layer 3 — Semantic interpretation (What propositions?)
Layer 4 — Translation manifold (What legitimate renderings?)
Layer 5 — Comparative criticism (Why do translations differ?)
Layer 6 — Commentary synthesis (Doctrinal context)
Layer 7 — Adaptive translation policy (For this reader/purpose)
```

The visionary result: **A navigable atlas of every defensible route from Sanskrit textual evidence to English understanding.**
