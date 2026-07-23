# V2 pipeline activation checklist

The foundation is safe-by-default. Complete these gates before corpus-scale runs or public releases.

## Environment

1. Create a Python 3.11 environment and install `requirements-v2.txt`.
2. Install the exact Lean version in `lean/lean-toolchain` and run `lake build` in `lean/`.
3. Build the existing Pantograph checkout with its own pinned toolchain.
4. Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` and record versions.

## Source and review

1. Audit every downloaded artefact for URL, timestamp, licence, hash, edition, and redistribution decision.
2. Put immutable inputs under `data/raw/<source-id>/`; use a manifest to ingest them.
3. Configure two independent morphology engines before asserting coverage.
4. Keep rejected parse/alignment alternatives and reasons; keep blind candidates immutable.

## Formal

1. Use only the deterministic Semantic IR compiler; reject raw Lean from models and imported data.
2. Persist real Lean output; textual assertions are `textual_axiom`, and only derivations are theorems.
3. Run two-way entailment and contradiction probes, retaining bridge assumptions and failures.

The first operational target is a permission-cleared, contiguous ~100-passage Manthanabhairavatantra pilot. The included one-verse fixture proves mechanics only.
