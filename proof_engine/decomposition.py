"""
Decomposition Loop. AxiomMath-style: raw claim → auto-formalize → primitive check → Lean assembly.
Core of the proof engine. Everything else depends on it.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from . import db
from . import failure_taxonomy
from .failure_taxonomy import FailureType, log_failure, add_primitive_candidate
from . import lean_checker
from . import informalization


class DecompositionResult(Enum):
    PLACED = "placed"   # Claim compiled, status = AXIOM
    FAILED = "failed"   # COMPILE_ERROR or other, logged


@dataclass
class DecompositionComponent:
    text: str
    primitive_candidate: str
    maps_cleanly: bool = True
    residue: Optional[str] = None
    mathlib_anchor: Optional[str] = None


def auto_formalize(statement: str, primitives: list[dict], *, llm_fn=None) -> list[DecompositionComponent]:
    """
    LLM: Given claim, what Lean type does it want? What primitives from the list does it use?
    Returns components. Strict: only map to primitives in list; list unmapped separately.
    """
    if llm_fn:
        return _llm_auto_formalize(statement, primitives, llm_fn)
    return _fallback_auto_formalize(statement, primitives)


def _fallback_auto_formalize(statement: str, primitives: list[dict]) -> list[DecompositionComponent]:
    """When no LLM: simple keyword match against primitive_ids."""
    prim_ids = [p["primitive_id"] for p in primitives]
    components = []
    stmt_lower = statement.lower()
    for pid in prim_ids:
        if pid.lower() in stmt_lower or _hint_match(pid, statement, primitives):
            components.append(DecompositionComponent(
                text=f"uses {pid}",
                primitive_candidate=pid,
                maps_cleanly=True,
            ))
    if not components:
        components.append(DecompositionComponent(
            text=statement,
            primitive_candidate="",
            maps_cleanly=False,
            residue=statement,
        ))
    return components


def _hint_match(pid: str, statement: str, primitives: list[dict]) -> bool:
    p = next((x for x in primitives if x["primitive_id"] == pid), None)
    if not p:
        return False
    defn = (p.get("definition") or "").lower()
    for w in statement.lower().split():
        if len(w) > 4 and w in defn:
            return True
    return False


def _llm_auto_formalize(statement: str, primitives: list[dict], llm_fn) -> list[DecompositionComponent]:
    """LLM call. Strict prompt: only primitives from list."""
    prim_list = "\n".join(f"- {p['primitive_id']}: {p.get('definition', '')}" for p in primitives)
    prompt = f"""Given this claim, list components that map to primitives from the list below.
Return ONLY components that map to primitives in this list. Do NOT hallucinate matches.
For anything that does not map, put it in "unmapped" with the residue.

Claim: {statement}

Primitives (use ONLY these):
{prim_list}

Return JSON: {{"components": [{{"text": "...", "primitive_candidate": "ID", "maps_cleanly": true/false, "residue": null or "..."}}], "unmapped": [{{"text": "...", "residue": "..."}}]}}"""

    try:
        resp = llm_fn(prompt)
        if not resp:
            return _fallback_auto_formalize(statement, primitives)
        import json
        start = resp.find("{")
        end = resp.rfind("}") + 1
        if start >= 0 and end > start:
            d = json.loads(resp[start:end])
            out = []
            for c in d.get("components", []):
                out.append(DecompositionComponent(
                    text=c.get("text", ""),
                    primitive_candidate=c.get("primitive_candidate", ""),
                    maps_cleanly=c.get("maps_cleanly", True),
                    residue=c.get("residue"),
                ))
            for u in d.get("unmapped", []):
                out.append(DecompositionComponent(
                    text=u.get("text", ""),
                    primitive_candidate="",
                    maps_cleanly=False,
                    residue=u.get("residue", u.get("text", "")),
                ))
            if out:
                return out
    except Exception:
        pass
    return _fallback_auto_formalize(statement, primitives)


def assemble_lean_type(components: list[DecompositionComponent], conn) -> str:
    """
    Build Lean type from components. Use primitive lean_hints where available.
    Simple conjunction for now.
    """
    parts = []
    for c in components:
        if not c.primitive_candidate:
            continue
        prim = db.find_primitive(conn, c.primitive_candidate)
        if prim and prim.get("lean_hint"):
            hint = prim["lean_hint"]
            if ":" in hint:
                parts.append(hint.split(":")[-1].strip())
            else:
                parts.append(hint)
    if not parts:
        return "True"  # placeholder
    if len(parts) == 1:
        return parts[0]
    return " ∧ ".join(f"({p})" for p in parts)


def pantograph_attempt(lean_type: str, *, fast: bool = True) -> "PantographResult":
    """Attempt Lean compilation. Returns result with success, error, missing_type."""
    r = lean_checker.pantograph_check(lean_type, fast=fast)
    return PantographResult(
        success=r["status"] == "PROVED",
        error=r.get("note", ""),
        missing_type=_extract_missing_type(r.get("note", "")),
    )


def _extract_missing_type(note: str) -> Optional[str]:
    """Heuristic: extract type name from Lean error if MISSING_PRIMITIVE."""
    for s in ("unknown identifier", "unknown constant", "unknown '"):
        if s in note.lower():
            # Try to extract identifier
            for word in note.replace("'", " ").split():
                if word[0].isupper() and len(word) > 2:
                    return word
    return None


@dataclass
class PantographResult:
    success: bool
    error: str
    missing_type: Optional[str] = None


def classify_failure(result: PantographResult) -> FailureType:
    """Map pantograph result to FailureType."""
    err = (result.error or "").lower()
    if result.missing_type:
        return FailureType.MISSING_PRIMITIVE
    if "timeout" in err or "time out" in err:
        return FailureType.TIMEOUT
    if "unknown" in err or "identifier" in err or "constant" in err or "type" in err:
        return FailureType.COMPILE_ERROR
    return FailureType.UNPROVABLE


def decompose_claim(
    conn,
    claim_id: str,
    *,
    pre_decomposed: Optional[list[dict]] = None,
    llm_fn=None,
    fast: bool = True,
) -> DecompositionResult:
    """
    Decomposition loop. Returns PLACED or FAILED.
    pre_decomposed: use these components instead of auto_formalize (e.g. from iit_integration_decomposed.json).
    """
    claim = db.get_claim(conn, claim_id)
    if not claim:
        return DecompositionResult.FAILED

    # Clear prior decompositions for idempotency
    conn.execute("DELETE FROM decompositions WHERE claim_id=?", (claim_id,))
    conn.commit()

    statement = claim.get("statement", "")
    primitives = db.get_primitives(conn)

    # Step 1: Get components (LLM or pre-decomposed)
    if pre_decomposed:
        components = [
            DecompositionComponent(
                text=c.get("text", ""),
                primitive_candidate=c.get("primitive_candidate", ""),
                maps_cleanly=c.get("maps_cleanly", True),
                residue=c.get("residue"),
                mathlib_anchor=c.get("mathlib_anchor"),
            )
            for c in pre_decomposed
        ]
    else:
        components = auto_formalize(statement, primitives, llm_fn=llm_fn)

    # Step 2: For each component, check against primitive library
    for c in components:
        primitive = db.find_primitive(conn, c.primitive_candidate) if c.primitive_candidate else None

        if primitive:
            db.add_decomposition(
                conn, claim_id=claim_id, component_text=c.text,
                primitive_id=c.primitive_candidate, maps_cleanly=True, residue=None,
            )
        else:
            residue = c.residue or c.text
            db.add_decomposition(
                conn, claim_id=claim_id, component_text=c.text,
                primitive_id=None, maps_cleanly=False, residue=residue,
            )
            if c.primitive_candidate:
                add_primitive_candidate(
                    conn,
                    candidate_id=c.primitive_candidate,
                    definition=c.text,
                    source_claim_id=claim_id,
                    source_residue=residue,
                )
            elif residue:
                cand_id = f"Candidate_{claim_id}_{hash(residue) % 10000}"
                add_primitive_candidate(
                    conn, candidate_id=cand_id, definition=residue,
                    source_claim_id=claim_id, source_residue=residue,
                )

    # Step 3: Attempt Lean assembly
    lean_type = assemble_lean_type(components, conn)
    result = pantograph_attempt(lean_type, fast=fast)

    if result.success:
        if informalization.validate_before_commit(conn, claim_id, lean_type):
            return DecompositionResult.PLACED
        return DecompositionResult.FAILED
    else:
        log_failure(
            conn,
            failure_type=classify_failure(result),
            claim_id=claim_id,
            lean_output=result.error,
            primitive_candidate=result.missing_type,
            context=f"assemble_lean_type produced: {lean_type}",
        )
        if result.missing_type:
            add_primitive_candidate(
                conn,
                candidate_id=result.missing_type,
                definition=result.error or "",
                source_claim_id=claim_id,
                source_residue=result.error,
            )
        return DecompositionResult.FAILED
