# Proof Engine Lean

Lean 4 foundation and IIT scaffolding for the Sanskrit Proof Engine.

## Structure

| File | Content |
|------|---------|
| **Foundation.lean** | Proved theorems from Mathlib: modus_ponens, forall_imp, contrapositive, Set.IsPartition |
| **IIT.lean** | Kleiner & Tull structures: System, ExperienceSpace, cause/effect repertoire, integration, Concept, Φ |
| **Sanskrit.lean** | Dharmakīrti axioms: Cognition, Svalaksana, Perceives, Kalpana |

## Setup

```bash
# From proof_engine_lean/
curl -o lean-toolchain https://raw.githubusercontent.com/leanprover-community/mathlib4/master/lean-toolchain
lake update
lake exe cache get   # Download precompiled Mathlib (recommended)
lake build
```

## IIT Scaffolding (Kleiner & Tull arXiv:2002.07655)

- **System**: stateSpace, subsystems, decompositions, cutSystem, cutState
- **ExperienceSpace**: carrier, intensity, distance, scale
- **Integration**: integrationLevel φ, integrationScaling ι
- **Cause-effect**: causeRepertoire, effectRepertoire, ProtoExperience
- **Concept, Q-shape, E(S,s), Φ**

Placeholders (axiom/sorry) where full proofs are needed. Replace with constructive definitions as we formalize.

## Foundation

- `modus_ponens`, `forall_imp`, `contrapositive` — proved
- `Set.IsPartition` — for IIT decompositions
- Used by lean_checker fallback when Pantograph unavailable
