# Sanskritree V2 build notes

## 2026-07-23 — foundation audit

The legacy `proof_engine` is preserved as a legacy subsystem. Its audit found the following V2 blockers:

- `proof_engine/sanskrit_pipeline.py` returns a placeholder morphology result and treats two tokens as a possible identity relation.
- `proof_engine/algorithm.py` accepts an LLM-provided `lean_type`, labels decomposed definitions `PROVED`, and exits its retry loop after one failure.
- Existing status semantics conflate textual assumptions with Lean-proved theorems.

The V2 implementation does not use those behaviours. It introduces a new `src/sanskritree` package and SQLite migration set alongside the legacy engine.

## Vertical slice boundary

The first pilot ingests one fixture verse, preserves raw and NFC-normalised readings, stores ambiguity-preserving analysis candidates, creates a reviewed-capable span alignment, records an immutable blind translation candidate with evidence, persists an explicit Semantic IR frame, and deterministically emits a registered Lean template. A textual assertion is stored as `formal_role=textual_axiom`, `lean_status=uncompiled`; it is never reported as a theorem.

## Toolchain status

Python 3.11.2 is available. The repository pins Lean `v4.29.0-rc4`, but `lean` and `lake` were not on `PATH` during the audit. The V2 compiler therefore has deterministic generation/safety tests now; full Lean checking is a pipeline activation prerequisite, not silently simulated success.

## Corpus policy

No copyrighted edition, large Hugging Face corpus, or model is imported by this foundation commit. Imports must be manifest-driven and must record source URL, source hash, edition, licence, and critical method. This is necessary before any public redistribution, and avoids consuming the remaining ~17 GB volume capacity with unvetted multi-million-row datasets.

## Next implementation increments

1. install the pinned Lean toolchain and make `lean/Sanskritree` compile;
2. add adapters for Heritage, DCS, Vidyut, and process-sanskrit behind a shared lattice protocol;
3. add importer-specific licence/provenance adapters after source-card audits;
4. turn remaining CLI scaffold commands into reviewed-workflow operations;
5. add entailment/equivalence probes that preserve bridge assumptions.
