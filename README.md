# Sanskrit Proof Engine

Truth compressor: decomposes Sanskrit philosophical claims into Lean4 proofs or honest boundary findings. Per `proofenginge.md` and `instruction.md`.

## What It Does

- Takes claims from Sanskrit texts (Nyaya, Shiva Sutras, Tantraloka)
- Recursively decomposes until: **PROVED** (Lean4), **OUTSIDE_FORMAL** (empirical), or **HOLLOW** (unsayable)
- Output: node graph with traceable paths. High `reuse_count` = centre nodes.

**Critical**: No bias toward proofs. PARTIAL and OUTSIDE_FORMAL are correct when the text doesn't support formalization.

## Quick Start

```bash
pip install -r requirements.txt
python run_proof_engine.py
```

## Structure

```
proof_engine/
  db.py           - SQLite schema, node CRUD
  api.py          - LeanSearch, Loogle HTTP clients
  lean_checker.py - Pantograph/fallback Lean4 checker
  fol_lean_bridge.py - FOL -> Lean4 (Navya-Nyaya operators)
  algorithm.py    - 5-step core: Sayability -> Library -> Formalize -> Prove -> Decompose
  sanskrit_pipeline.py - Heritage/SanskritShala pipeline
  phase1_nyaya.py - Phase 1: Nyaya-Sutras validation
run_proof_engine.py - CLI entry point
```

## Phase 1 Terms (Nyaya)

1. **pramana** - valid means of cognition
2. **samsaya** - doubt
3. **vyapti** - universal concomitance (core inference principle)
4. **anumana** - five-membered inference
5. **nigrahasthana** - grounds for defeat

## Tool Stack (per spec)

| Tool | Role |
|------|------|
| LeanSearch | NL -> Lean declaration |
| Loogle | Type signature -> theorem |
| Pantograph | Python <-> Lean4 REPL |
| Heritage Engine | Sanskrit morphology, sandhi |
| SanskritShala | Pre-Heritage (faster) |
| GRETIL | Machine-readable texts |

## Pantograph (Lean4 REPL)

For real Lean4 proof checking, build Pantograph:

```bash
git clone https://github.com/leanprover/Pantograph.git
cd Pantograph
lake build
```

Executable: `.lake/build/bin/repl`. Run via `lake exe repl Init`. The proof engine auto-detects `Pantograph/` and uses `lake env lean` for typechecking.

## Ground Truth (Build Order)

**Strategy:** Start with what's proved (Mathlib + PhysLean), work outward. Three-tier structure. See `BUILD_ORDER.md`.

```bash
python run_ground_truth.py          # Full seed (~51 entries)
python run_ground_truth.py --catalog-only   # Tables only, no graph nodes
```

- **Tier 1:** Mathlib (~12 theorems), PhysLean (~9 items) — specific signatures
- **Tier 2:** Functional primitives (CausalPower, Integration, Broadcast, etc.) — `primitives_tier2.json`
- **Tier 3:** IIT, GWT, Dharmakīrti, Nyāya claims
- **Negative controls:** ~8 known non-bridges for testing
- **Decompositions table:** component → primitive mapping, residue for HOLLOW

## Resources

Curated reading for IIT/GWT/Dharmakīrti formalization: Kleiner & Tull (IIT in category theory), IIT 4.0, PyPhi (validation oracle), PhysLean. See `RESOURCES.md`.

## Next Steps

1. Add Mathlib to a Lean project: `require mathlib from "..."` then `lake exe cache get`
2. Run Shiva Sutras (Phase 2): `citiḥ śaktiḥ`
3. Phase 3: Tantraloka crossover hypotheses
