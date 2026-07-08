# Consciousness Theory Pipeline

Three loops adapted from AxiomMath. Order matters.

## 1. Decomposition Loop (`proof_engine/decomposition.py`)

```
Input: raw claim C
  ↓
Auto-formalize (LLM + primitive list) → components
  ↓
For each component: in DB? YES → use; NO → flag as primitive_candidate
  ↓
Assemble Lean type from components
  ↓
Pantograph attempt
  ↓
SUCCESS → validate_before_commit (gate) → AXIOM
FAILURE → log_failure, classify (COMPILE_ERROR | UNPROVABLE | TIMEOUT | MISSING_PRIMITIVE)
  ↓
DecompositionResult.PLACED | FAILED
```

**Pre-decomposed**: Use `iit_integration_decomposed.json` components directly (no LLM).

## 2. Bridge Probe (`proof_engine/bridge_probe.py`)

Only on pairs sharing ≥1 primitive. Skip negative controls.

```
For each (A, B) with shared primitive:
  Try A → B, B → A, A → ¬B
  ↓
  classify_relation:
    both proved     → BRIDGES
    A→B only        → SUBSUMES (A subsumes B)
    B→A only        → SUBSUMES (B subsumes A)
    A→¬B proved    → CONTRADICTS
    else            → OVERLAPS
  ↓
  Store in claim_relations
```

## 3. Auto-Informalization Gate (`proof_engine/informalization.py`)

Runs inside decomposition, before committing.

```
Lean type → lean_to_natural_language (LLM)
  ↓
compare_meanings(original, rendering)
  ↓
MATCH → commit to DB
MISMATCH → log_failure(COMPILE_ERROR), return False
```

## Failure Taxonomy (`proof_engine/failure_taxonomy.py`)

| FailureType       | Action                                      |
|-------------------|---------------------------------------------|
| COMPILE_ERROR     | Re-decompose, re-formalize                  |
| UNPROVABLE        | Log axioms that would make it provable      |
| TIMEOUT           | Split into smaller claims                   |
| MISSING_PRIMITIVE | Add to primitive_candidates, retry after review |

## Run Order

1. `python run_ground_truth.py` — seed catalogs
2. `python run_decomposition.py` — IIT Integration first (pre-decomposed)
3. `python run_decomposition.py --all` — all claims
4. `python run_pipeline.py` — decomposition + bridge probe
5. `python report_graph.py` — print knowledge tree to stdout
6. `python report_graph.py --json frontend/data/export.json` — export for graph view

## View the Graph

After exporting: open `frontend/index.html` in a browser (or serve the frontend folder).
The app loads `data/export.json` when present, else `data/sample.json`.

## Expected First Run

- Decomposition: 2–3 components placed cleanly, 1–2 primitive candidates logged
- Bridge probe: nothing to probe yet (only one claim placed)
- Auto-informalization: may catch mistranslation

Failures are real and actionable. The probe hitting the floor is the finding.
