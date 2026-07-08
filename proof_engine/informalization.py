"""
Auto-informalization Gate. Runs before committing any formalized claim.
Lean type -> natural language -> compare to original. Prevents plausible garbage.
"""

from dataclasses import dataclass
from typing import Optional

from . import db
from .failure_taxonomy import FailureType, log_failure


@dataclass
class ValidationResult:
    matches: bool
    discrepancy: Optional[str] = None


def lean_to_natural_language(lean_type: str, *, llm_fn=None) -> str:
    """
    Render Lean type back to natural language.
    LLM: "Translate this Lean type to a single clear English sentence."
    """
    if llm_fn:
        return _llm_lean_to_nl(lean_type, llm_fn)
    return _fallback_lean_to_nl(lean_type)


def _fallback_lean_to_nl(lean_type: str) -> str:
    """When no LLM: simple structural mapping."""
    t = lean_type.strip()
    if "→" in t:
        parts = t.split("→", 1)
        return f"If {parts[0].strip()} then {parts[1].strip()}"
    if "∧" in t:
        parts = t.split("∧")
        return " and ".join(p.strip().strip("()") for p in parts)
    if "∀" in t or "forall" in t.lower():
        return t.replace("∀", "For all ").replace("forall", "for all")
    return t


def _llm_lean_to_nl(lean_type: str, llm_fn) -> str:
    prompt = f"""Translate this Lean 4 type to a single clear English sentence. No jargon.
Lean type: {lean_type}
English:"""
    try:
        resp = llm_fn(prompt)
        if resp and len(resp.strip()) > 10:
            return resp.strip()[:500]
    except Exception:
        pass
    return _fallback_lean_to_nl(lean_type)


def compare_meanings(original: str, nl_rendering: str, *, llm_fn=None) -> ValidationResult:
    """
    LLM: "Original claim: X. Formal rendering: Y. Does Y capture the meaning of X?
    If not, what is lost or distorted? Answer YES or NO first."
    """
    if llm_fn:
        return _llm_compare(original, nl_rendering, llm_fn)
    return _fallback_compare(original, nl_rendering)


def _fallback_compare(original: str, nl_rendering: str) -> ValidationResult:
    """When no LLM: simple word overlap heuristic."""
    o_words = set(original.lower().split())
    r_words = set(nl_rendering.lower().split())
    overlap = len(o_words & r_words) / max(len(o_words), 1)
    if overlap >= 0.3:
        return ValidationResult(matches=True)
    return ValidationResult(
        matches=False,
        discrepancy=f"Low overlap. Original: {original[:80]}... Rendering: {nl_rendering[:80]}...",
    )


def _llm_compare(original: str, nl_rendering: str, llm_fn) -> ValidationResult:
    prompt = f"""Original claim: {original}
Formal rendering: {nl_rendering}

Does the formal rendering capture the meaning of the original claim?
Answer YES or NO first. If NO, briefly state what is lost or distorted."""
    try:
        resp = llm_fn(prompt)
        if not resp:
            return _fallback_compare(original, nl_rendering)
        r = resp.strip().upper()
        if r.startswith("YES"):
            return ValidationResult(matches=True)
        discrepancy = resp.strip()
        if r.startswith("NO"):
            lines = resp.strip().split("\n")
            if len(lines) > 1:
                discrepancy = "\n".join(lines[1:]).strip()
        return ValidationResult(matches=False, discrepancy=discrepancy)
    except Exception:
        return _fallback_compare(original, nl_rendering)


def validate_before_commit(
    conn,
    claim_id: str,
    lean_type: str,
    *,
    llm_fn=None,
) -> bool:
    """
    Auto-informalization gate. Before committing formalized claim:
    Lean type -> natural language -> compare to original.
    Returns True if match, False otherwise. On mismatch, logs failure.
    """
    claim = db.get_claim(conn, claim_id)
    if not claim:
        return False

    original = claim.get("statement", "")
    nl_rendering = lean_to_natural_language(lean_type, llm_fn=llm_fn)
    validation = compare_meanings(original, nl_rendering, llm_fn=llm_fn)

    if validation.matches:
        db.update_claim_status(conn, claim_id, "AXIOM", lean_type)
        return True
    else:
        log_failure(
            conn,
            failure_type=FailureType.COMPILE_ERROR,
            claim_id=claim_id,
            context=f"Informalization mismatch: {validation.discrepancy}",
            lean_output=nl_rendering,
        )
        return False
