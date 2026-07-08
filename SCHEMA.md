# SANSKRIT PROOF ENGINE — SCHEMA

Typed deductive DB. Fixed-point status semantics over term algebra (§6). Lean = formal oracle; human = semantic oracle.

---

## §0 PARIBHĀṢĀ

```
0.1 Schema = source of truth
0.2 Lean: structural validity. Human: semantic faithfulness
0.3 LLM: sayability, registry, template select, kāṇḍa — never proof
0.4 IAST canonical
0.5 Anuvrtti: inherit parent; delta only
0.6 Kāṇḍa: 1 (siddha) | 2 (vidhi) | 3 (asiddha). Kāṇḍa 3 invisible to 1
0.7 Template conflict: SOI → apavāda wins; DOI → para wins
0.8 DEFINITION = axiom, PROVED by stipulation
0.9 No infinite loop → HOLLOW
```

---

## §1 SAṂJÑĀ

| Term | Def |
|------|-----|
| Node | Falsifiable unit; truth conditions; not splittable |
| Anchor | source_text (IAST); immutable |
| Tradition | provenance.tradition; same IAST, diff tradition → diff nodes |
| Bridge | Same Lean type, independent decomposition |
| CONTRADICTION | Two PROVED, contradictory types |

---

## §2 VIDHI

```
2.1  Anchor immutable
2.2  Same IAST, diff tradition → diff nodes
2.3  Same Lean type → reuse_count++
2.4  Decomposition faithful; no provability bias
2.5  lean_type from template only
2.6  Registry terms only
2.7  Abhāva: absence_type; human decides
2.8  logic_foundation ∈ {classical, FDE, intuitionistic}
2.9  Circular: vicious (no external PROVED) → HOLLOW; coherentist → axiom+review
```

---

## §3 ALGORITHM

**PRECONDITION:** validation_set_pass_rate = 1.0 ∨ DEV_MODE

```
proc process(C):
  if ¬sayable(C): return HOLLOW
  if match(Library): import; return
  lean_type ← formalize(C, template, SOI/DOI)
  if DEFINITION: return PROVED
  if structural: prove(lean_type); return result
  if FDE: fde_eval(lean_type); return result
  children ← decompose(C)  // 4a commentary | 4b secondary | 4c llm
  for c in children: process(c)
  return propagate(C)
```

**propagate(n):**
```
  if ∃child REFUTED: return REFUTED
  if ∀child ∈ {UNSAYABLE,HOLLOW}: return HOLLOW
  if ∃PROVED ∧ ∃{UNSAYABLE,HOLLOW}: return PARTIAL_HOLLOW
  if ∀child ∈ {PROVED,DEFINITION}: return PROVED
  if ∃child ∈ {UNPROVED,PLACEHOLDER}: return UNPROVED
  return PARTIAL
```

---

## §4 SCHEMA

**Node:** id, parent_id, inherited_from, delta_terms, kanda, statement, sanskrit, provenance, logic_foundation, node_type, status, lean_type, lean_proof, retry_count, human_review, decomp_source, absence_type

**Edges:** parent_id, child_id, edge_type (decomposition|dependency|bridge|contradiction)

**Terms:** tid, iast, tradition, lean_type_repr, definition_node_id. Same IAST, diff tradition → diff tid.

**Contradictions:** node_a, node_b, contradiction_scope, defeat_argument, resolution

**Bridge index:** lean_type_hash, node_id, tradition. Populated on PROVED.

**Traces:** trace_id, node_id, anchor, tradition, layer0–5, metadata. Emitted on PROVED.

**Status:** PROVED | UNPROVED | PARTIAL | HOLLOW | OUTSIDE_FORMAL | REFUTED (no PLACEHOLDER)

---

## §5 §6 TEMPLATES

abheda→a=b | vyapti→∀x,Hx→Sx | sambandha→Ra b | avacchedaka→∀{x:α},Px | pratiyogin→Counterpositive | anuyogin→Bearer | nirupaka→Definer | nirupya→Defined | samavaya→Inheres | anyonyabhava→a≠b | samsargabhava→¬(Ra b) | property→P:α→Prop | negation paryudasa→{x//¬Px} | negation prasajya→¬P | fde_val,fde_neg (Priest 2010)

---

## §7 ROLES

LLM: sayability, registry, template, kāṇḍa. Forbidden: Lean gen, prove, unregistered.
Lean: type, proof, no sorry.
Human: semantic faithfulness, registry, CONTRADICTION, bridge promotion.

---

## §8 INVARIANTS

Anchor immutable | Tradition-scoped | reuse_count on shared type | Faithful decomposition | Template-only | Registry only | validation_set ∨ DEV_MODE | warningAsError | Kāṇḍa 3 ⊄ deps of Kāṇḍa 1/2

## §9 PIPELINE

Sanskrit → Heritage/ByT5 → NN parse → Template(SOI/DOI) → §3. DCS, GRETIL, Sembank.

## §10 PHASES

1: Dharmakīrti (Pramāṇavārttika III). 2: Nyāya-Sūtras. 3: Shiva Sūtras. 4: Tantrāloka crossover.

---

## FORMAL SYSTEM ASSESSMENT

**Not a complete formal system** in the logician’s sense (axioms + inference rules + language). We are a **hybrid oracle system**:

- **Formal parts:** Term algebra (§6), fixed-point propagation, template TRS, typed schema
- **Oracle parts:** Lean (proof), human (semantics), LLM (decomposition)
- **Relation to known systems:**
  - Deductive DBs: fixed-point semantics, recursion — similar
  - TRS: §6 templates as rewrite rules — similar
  - Type theory: Lean as oracle — we use, don’t define
  - Category theory: nodes≈objects, edges≈morphisms; CONTRADICTION→preorder — partial
  - Geometric logic / topology: none
  - Number theory: none (math.md is separate)

**Original:** The combination is novel: tradition-parametric terms, kāṇḍa-scoped visibility, NN template TRS, Lean+human oracles, Sanskrit domain. No prior system unifies these.
