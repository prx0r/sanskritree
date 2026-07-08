# Sanskrit Proof Engine - Installation Status

**Last tested:** 2026-03-03

## Test Results: 15 OK, 0 FAIL, 1 WARN

Run `python test_installation.py` to verify.

---

## Installed & Working

| Component | Status | Notes |
|-----------|--------|-------|
| **requests** | OK | HTTP for APIs |
| **anthropic** | OK | LLM API |
| **heritage** | OK | Sanskrit Heritage Engine (web fallback) |
| **transformers** | OK | ByT5-Sanskrit |
| **torch** | OK | PyTorch |
| **sqlite3** | OK | Built-in |
| **pantograph** (pip) | OK | PyPI package (unrelated). |
| **Pantograph** (Lean4) | OK | Built at `Pantograph/`. Run `lake exe repl Init` from that dir. Executable: `.lake/build/bin/repl` |
| **elan** | OK | Lean version manager |
| **lake** | OK | Lean package manager |
| **lean** | OK | Lean 4.28.0 |
| **Loogle API** | OK | loogle.lean-lang.org |
| **HeritagePlatform** | OK | Sanskrit morphology (web method) |
| **proof_engine** | OK | Full pipeline runs |
| **lake build** | OK | Lean project compiles |

---

## Known Issues

| Component | Status | Notes |
|-----------|--------|-------|
| **LeanSearch** | WARN 403 | leansearch.net returns HTTP 403 (rate limit or auth). Proof engine falls back to Loogle + DB. |
| **PyPantograph** | N/A | No Python bindings. Use `lake exe repl` subprocess from `Pantograph/` directory. |

---

## Not Installed (Optional)

Per proofenginge.md + instruction.md:

- **Mathlib4** - Add to Lean project: `require mathlib from "https://github.com/leanprover-community/mathlib4"` then `lake exe cache get` (~2GB)
- **ReProver** - LeanDojo retrieval-augmented prover
- **ByT5-Sanskrit** - Model loads on first use via HuggingFace
- **panini-nlp** - github.com/akulasairohit/panini-nlp
- **pramana-nlp** - github.com/tylergneill/pramana-nlp
- **DCS Sanskrit Sembank** - github.com/OliverHellwig/sanskrit

---

## Quick Verify

```powershell
# Add elan to PATH (if needed)
$env:Path = "$env:USERPROFILE\.elan\bin;$env:Path"

# Run tests
python test_installation.py

# Run proof engine
python run_proof_engine.py
```
