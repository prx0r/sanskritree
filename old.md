# SANSKRIT PROOF ENGINE — FORMAL SCHEMA

Pāṇini-style: paribhāṣā → saṃjñā → vidhi → niyama → schema. No redundancy.

---

## §0 PARIBHĀṢĀ

0.1 Schema = sole source of truth. 0.2 Lean = formal oracle; human = semantic oracle. 0.3 LLM decomposes/classifies only; template-only formalization. 0.4 IAST canonical; English display only.

---

## §1 SAṂJÑĀ

| Term | Definition |
|------|------------|
| Node | Smallest falsifiable unit; identifiable truth conditions; not splittable |
| Statement | "{Subject} {copula} {predicate}" — registry terms only |
| Anchor | source_text (IAST) or (sanskrit + provenance.ref); immutable |
| Tradition | provenance.tradition; scopes axioms; same claim, different tradition → different nodes |
| Centre node | High reuse_count; emerges, not declared |
| Bridge | Same Lean type from independent decomposition; found, not constructed |
| CONTRADICTION | Two PROVED nodes, contradictory Lean types; resolution: axiom_choice \| term_disambiguation \| tradition_scope |

---

## §2 VIDHI

| # | Axiom |
|---|-------|
| 2.1 | Anchor immutable |
| 2.2 | Same IAST term, different tradition → different nodes |
| 2.3 | Same Lean type → shared proof, reuse_count++ |
| 2.4 | Decomposition follows source; no provability bias |
| 2.5 | PARTIAL, OUTSIDE_FORMAL are valid outputs |
| 2.6 | Bridges by independent convergence only |
| 2.7 | lean_type from schema template only |
| 2.8 | Registry terms only |
| 2.9 | Abhāva: require absence_type; flag; human decides OUTSIDE_FORMAL or custom |
| 2.10 | Prose → human validation; kārikā/sūtra → automated |
| 2.11 | logic_foundation ∈ {classical, FDE, intuitionistic}; default classical. Nāgārjuna: FDE. Dharmakīrti: classical. |
| 2.12 | Circular definitions: detect cycles; classify well_founded \| vicious \| coherentist; vicious→HOLLOW, coherentist→axiom+review |

---

## §3 NIYAMA

### 3.1 Sayability

P is candidate ⟺ falsifiable ∧ identifiable truth conditions ∧ not splittable. Test: Can you write Lean type? Two independent in type ⟹ two nodes.

### 3.2 Granularity

| Text | Unit |
|------|------|
| kārikā, sūtra | one verse/sūtra |
| prose | one sentence, one claim |
| TA | one śloka |

### 3.3 Kārikā edge cases

| Case | Action |
|------|--------|
| Conditional + objection + response | Split → 3 nodes |
| Purely rhetorical | CONTRADICTION pointer only |
| Term defined elsewhere | Placeholder + dependency link |
| Svavṛtti contradicts kārikā | Two nodes + CONTRADICTION |

### 3.4 Algorithm

PRECONDITION: validation_set_pass_rate = 1.0 ∨ status = DEV_MODE

```
INPUT: claim C
0. SAYABILITY: ¬C coherent? NO → UNSAYABLE, HOLLOW, stop.
1. LIBRARY: LeanSearch, Loogle, DB. Match → import, reuse_count++, done.
2. FORMALIZE: C → lean_type via template. Template ID required.
3. PROVE: lake env lean, warningAsError true. No sorry → PROVED. Sorry → PLACEHOLDER. Fail → 4.
4. DECOMPOSE: 4a IF commentary → extract, decomposition_source=commentary
              4b ELSE IF secondary → extract, decomposition_source=secondary
              4c ELSE → LLM, decomposition_source=llm, flag human_review
              Classify each: DEFINITION|EMPIRICAL|UNSAYABLE|FORMAL. FORMAL → recurse 0.
5. PROPAGATE: PROVED ⟺ all PROVED|DEFINITION. PARTIAL ⟺ some PROVED ∧ some OUTSIDE_FORMAL. UNPROVED ⟺ any UNPROVED|PLACEHOLDER. HOLLOW ⟺ any UNSAYABLE. REFUTED ⟺ any REFUTED.
```

### 3.5 Propagation

```
status(n) = REFUTED   if ∃child REFUTED
          | HOLLOW    if ∃child ∈ {UNSAYABLE, HOLLOW}
          | PROVED    if ∀child ∈ {PROVED, DEFINITION}
          | UNPROVED  if ∃child ∈ {UNPROVED, PLACEHOLDER}
          | PARTIAL   otherwise
```

---

## §4 SCHEMA (Data structures)

### 4.1 Node

| Field | Type | Mut | Constraint |
|-------|------|-----|------------|
| id | INT | — | PK |
| parent_id | INT | — | NULL = root |
| source_text | TEXT | — | IAST |
| source_ref | TEXT | — | e.g. PV III.3 |
| created_at | TEXT | — | ISO 8601 |
| anchor_terms | JSON | — | [IAST] |
| statement | TEXT | V | Registry only |
| sanskrit | TEXT | V | IAST |
| devanagari | TEXT | V | Display |
| provenance | JSON | V | §4.2 |
| logic_foundation | ENUM | V | classical \| FDE \| intuitionistic |
| node_type | ENUM | V | FORMAL \| EMPIRICAL \| DEFINITION \| UNSAYABLE |
| status | ENUM | V | §4.3 |
| lean_type | TEXT | V | From template |
| lean_template_id | TEXT | V | Required |
| formalization_rationale | TEXT | V | Required |
| lean_proof | TEXT | V | |
| mathlib_deps | JSON | V | |
| reuse_count | INT | D | Derived |
| decomposition_source | ENUM | V | commentary \| secondary \| llm |
| circular | ENUM | V | null \| well_founded \| vicious \| coherentist |
| notes | TEXT | V | |
| version | INT | V | |
| updated_at | TEXT | V | |
| edit_history | JSON | A | Audit |

### 4.2 Provenance

```json
{"tradition","period","text","register","author","ref"}
```

### 4.3 Status

PROVED | PLACEHOLDER | UNPROVED | PARTIAL | OUTSIDE_FORMAL | HOLLOW | REFUTED

### 4.4 Term registry (required before node 50)

| Field | Type |
|-------|------|
| id | INT |
| iast | TEXT |
| devanagari | TEXT |
| tradition_scope | TEXT \| NULL |
| definition_nodes | JSON | `[{tradition, node_id}]` |
| aliases | JSON |
| first_appears | TEXT |

### 4.5 CONTRADICTION

| Field | Type |
|-------|------|
| id | INT |
| node_a | INT |
| node_b | INT |
| defeat_argument | INT \| NULL |
| contradiction_scope | intra_author \| intra_tradition \| inter_tradition |
| resolution | axiom_choice \| term_disambiguation \| tradition_scope \| NULL |

### 4.6 Bridge

| Field | Type |
|-------|------|
| id | INT |
| node_a | INT |
| node_b | INT |
| lean_type_hash | TEXT |
| human_confirmed | BOOL |
| formalization_rationale_match | BOOL \| NULL |

### 4.7 Lean template

| Field | Type |
|-------|------|
| id | TEXT |
| nn_operator | §6 kind |
| lean_pattern | TEXT |
| args | JSON |

### 4.8 Validation set (20 claims, required before production)

| Field | Type |
|-------|------|
| id | INT |
| claim | TEXT |
| expected_status | PROVED \| OUTSIDE_FORMAL \| HOLLOW \| PARTIAL |
| expected_divergence | BOOL |

---

## §5 ADHIKĀRA

| Role | Permitted | Forbidden |
|------|-----------|----------|
| LLM | Decompose, classify, select template, map→registry | Generate Lean, invent lemmas, prove, unregistered terms, provability bias |
| Lean | Type correctness, proof validity, no sorry | — |
| Human | Semantic faithfulness, prose validation, registry, CONTRADICTION resolution | — |

---

## §6 NNExpr → Lean (templates)

| kind | negation_type | Lean pattern |
|------|---------------|--------------|
| abheda | — | a = b |
| vyapti | — | ∀ x, H x → S x |
| sambandha | — | R a b |
| avacchedaka | — | ∀ {x : α}, P x |
| avacchedaka_limitor | — | ∀ {x : α}, Limitor P x |
| pratiyogin | — | Counterpositive P x |
| anuyogin | — | Bearer P x |
| nirupaka | — | Definer P Q |
| nirupya | — | Defined P Q |
| samavaya | — | Inheres a b |
| anyonyabhava | — | a ≠ b |
| samsargabhava | — | ¬(R a b) |
| property | — | P : α → Prop |
| negation | paryudasa | {x // ¬ P x} |
| negation | prasajya | ¬ P |

All formalization via these. No other patterns.

---

## §7 PROGRAMS

elan, lake, lean | Pantograph (repl) | Heritage, SanskritShala, sanskrit_parser, ByT5 | Loogle, LeanSearch | Mathlib4

---

## §8 DATA SOURCES

GRETIL | Muktabodha | Archive.org | DCS Sembank | pramana-nlp

---

## §9 PIPELINE

```
Sanskrit → Heritage (sandhi, morph) → ByT5 (POS, dep) → NN parse → Template select → lean_type → §3.4
```

Prose: +human. Kārikā/sūtra: automated.

---

## §10 PĀṆINI LAYER

Heritage/panini-nlp traces Aṣṭādhyāyī. Rule application = sub-node, DEFINITION, PROVED.

---

## §11 PHASE 3 CROSSOVER

Extract proved component → search scientific lit → run claim independently (no Sanskrit) → compare node IDs. Sanskrit baseline immutable.

---

## §12 TEXT PHASES

| Phase | Text | Terms |
|-------|------|-------|
| 1 | Nyāya-Sūtras 1.1 | pramāṇa, saṃśaya, vyāpti, anumāna, nigrahasthāna |
| 2 | Shiva Sūtras + Vimarśinī | citiḥ śaktiḥ |
| 3 | Tantrāloka ĀH 1,3,6,9 | Crossover |

---

## §13 INVARIANTS

1. Anchor immutable 2. Tradition-scoped nodes 3. reuse_count on shared type 4. Decomposition faithful 5. PARTIAL/OUTSIDE_FORMAL valid 6. Bridges found not made 7. Template-only 8. Registry only 9. Abhāva: absence_type + human 10. validation_set_pass_rate = 1.0 ∨ DEV_MODE 11. warningAsError 12. Pantograph fallback: lake build + parse

---

## §14 REFERENCES

Briggs (1985) AI Magazine 6.1 — Sanskrit & AI. Priest (2010) Comparative Philosophy — FDE, catuskoti. Guhe (2017) Springer Handbook — NN property-theoretic framework. Ganeri (2008) College Publications — NN formal regimentation.
