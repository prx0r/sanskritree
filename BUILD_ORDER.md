# Build Order: Consciousness Theory Map

**Goal:** Define a set system that interprets all consciousness studies, map them on a mindmap, see where the most commonalities are.

**Strategy:** Start with what's already proved (Mathlib + PhysLean). Work outward. IIT and GWT anchor the coordinate system. Everything else gets placed relative to them.

---

## Ground Truth Structure (Three Tiers)

| Tier | Source | Content |
|------|--------|---------|
| **Tier 1** | Mathlib, PhysLean | Specific theorems with signatures. Fully proved. |
| **Tier 2** | primitives_tier2.json | Functional primitives. Cross-tradition, yes/no definitions. |
| **Tier 3** | Claim files | Tradition-anchored axioms (IIT, GWT, Dharmakīrti, Nyāya). |

**Decompositions table:** Each claim component maps to a primitive or leaves residue. The residue is where new primitives come from and where HOLLOW happens.

**Negative controls:** Known non-bridges. If the system produces these as bridges, it's broken.

---

## Week 1: Catalog Mathlib + PhysLean

**Task:** Catalog specific theorems with signatures. Not modules — items.

**Mathlib** (mathlib_catalog.json): logic (modus_ponens, contrapositive), sets (Set.partition, subset_iff), measure_theory (ProbabilityMeasure, conditional_probability, mutual_information), order (PartialOrder, Lattice), **graph_theory** (SimpleGraph.connected, partition) — IIT φ is a graph operation, GWT broadcast is reachability.

**PhysLean** (physlean_catalog.json): causal_structure (CausalOrder, CausalCone, Intervention), information (ShannonEntropy, KLDivergence, MutualInformation), quantum (DensityMatrix, VonNeumannEntropy, Entanglement) — IIT 4.0 quantum φ, Kashmir Shaivism non-separability.

**Output:** ~21 Mathlib items, ~9 PhysLean items. Run `python run_ground_truth.py`.

---

## Week 2: IIT Qualitative → Lean Types

**Task:** Express IIT's five qualitative postulates as Lean types using only Mathlib primitives.

| Postulate | Plain terms | Lean attempt |
|-----------|-------------|--------------|
| Existence | System has causal power on itself | `axiom CausalPower : Type → Prop` |
| Intrinsicality | Causal power from system's own perspective | `axiom Intrinsic : ...` |
| Information | System specifies particular cause-effect state | |
| Integration | Irreducible over partitions | `axiom Irreducible : Type → Prop` + partition_loss |
| Exclusion | One system, one level wins | max over overlapping systems |

**Question:** Which connect cleanly? Which don't? The ones that don't = first real finding.

**Output:** `IIT.lean` with qualitative axioms. Nodes in graph.

---

## Week 3: GWT → Lean Types, Check IIT Tension

**Task:** Formalize GWT. Test IIT overlap/contradiction.

**GWT core:**
```
Conscious r ↔ ∃ w, WinsCompetition r w ∧ ∀ m, Broadcasts w m
```

**Tension:** IIT Integration = irreducible. GWT = broadcast to independent modules. Formally contradictory? Encode in Lean.

**Output:** `GWT.lean`. Edges: IIT–GWT CONTRADICTS or OVERLAPS.

---

## Week 4: Dharmakīrti arthakriyā

**Task:** First cross-tradition placement.

**Claim:** x exists iff x has causal efficacy (arthakriyā).

**IIT Existence:** x is conscious iff x has causal power on itself.

**Primitive:** CausalPower appears in both. OVERLAPS relation. Same primitive, different domain.

**Output:** Node for arthakriyā. Edge to IIT Existence. bridge_axioms: [] if pure, else list.

---

## Week 5: Nyāya pramāṇa

**Task:** Map onto same space.

**Claim:** Valid cognition produces true belief.

**Output:** Node. Edges to existing primitives.

---

## Week 6: First Esoteric Step

**Pick one:** Vedānta svaprakāśa OR Kashmir Shaivism spanda.

**Spanda:** Decompose by primitive-matching.
- Constitutive dynamism → CausalPower? partial
- Periodic alternation → PeriodicProcess?
- Self-luminous substrate → Intrinsicality?
- Manifestation/withdrawal → no existing primitive → new candidate or HOLLOW

**Output:** Precision map. Which primitives used, which don't fit.

---

## Week 7+: Expand, Stabilize

- Add more traditions
- Primitive library stabilizes
- Boundary view: PROVED → AXIOM → HOLLOW transition visible

---

## Core Question at Each Step

> Which existing primitives does this claim use, and what's left over that doesn't fit?

The leftover is always the interesting part.

---

## Files

| File | Purpose |
|------|---------|
| `ground_truth/mathlib_catalog.json` | Specific theorems with signatures (logic, sets, measure, order, graph) |
| `ground_truth/physlean_catalog.json` | Causal, information, quantum items |
| `ground_truth/primitives_tier2.json` | Functional primitives only (Tier 2) |
| `ground_truth/iit_claims.json` | IIT 6 postulates |
| `ground_truth/gwt_claims.json` | GWT core claims |
| `ground_truth/dharmakirti_claims.json` | arthakriyā, svalakṣaṇa, pratyakṣa |
| `ground_truth/nyaya_claims.json` | pramāṇa, vyāpti, anumāna |
| `ground_truth/negative_controls.json` | Known non-bridges for testing |
| `proof_engine/ground_truth.py` | Loader, seed functions |
| `run_ground_truth.py` | CLI to seed |

**Decompositions table:** claim_id, component_text, primitive_id, maps_cleanly, residue. Populated when claims run through pipeline.

---

## ProofResult (for Pantograph)

```
PROVED       — Lean accepted the proof
UNPROVABLE   — Lean rejected; no proof with current axioms
TIMEOUT      — Lean didn't terminate
COMPILE_ERROR — Type didn't check; formalization wrong
```

COMPILE_ERROR → fix morphology/TRS. UNPROVABLE → possibly independence result.
