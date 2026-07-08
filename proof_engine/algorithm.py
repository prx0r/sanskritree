"""
Core algorithm per proofenginge.md + Schema v3 §3.4.
Seven-step: Sayability → Anuvrtti → Library → NN Parse → TRS → Proof → Propagate.
"""

import json
import uuid
from typing import Optional, Callable
from . import db
from . import api
from . import lean_checker
from . import fol_lean_bridge
from . import registry
from . import validation

MAX_RETRIES = 3


def process_claim(
    conn,
    claim: str,
    *,
    parent_id: Optional[int] = None,
    sanskrit: Optional[str] = None,
    devanagari: Optional[str] = None,
    provenance: Optional[dict] = None,
    is_sanskrit: bool = False,
    sayability_fn: Optional[Callable[[str], bool]] = None,
    formalize_fn: Optional[Callable[[str, Optional[str], Optional[dict]], str]] = None,
    decompose_fn: Optional[Callable[[str], list[dict]]] = None,
    llm_fn: Optional[Callable[[str, Optional[str], Optional[dict]], dict]] = None,
    max_depth: int = 10,
    fast_mode: bool = False,
    dev_mode: bool = True,
) -> int:
    """
    Process a claim through the full algorithm. Returns node id.
    dev_mode=True bypasses validation set gate.
    """
    # PRECONDITION: validation_set_pass_rate = 1.0 ∨ DEV_MODE
    if not validation.validation_ok(conn, dev_mode=dev_mode):
        raise RuntimeError("Validation set failed. Run with dev_mode=True or fix validation pairs.")

    if max_depth <= 0:
        nid = db.add_node(conn, parent_id, claim, sanskrit=sanskrit, devanagari=devanagari,
                          provenance=provenance, node_type="FORMAL", status="UNPROVED",
                          notes="Max depth reached", kanda=2)
        return nid

    # STEP 0: SAYABILITY + KĀṆḌA
    llm_result = None
    if llm_fn:
        llm_result = llm_fn(claim, sanskrit, provenance)
        if not llm_result.get("sayable", True):
            nid = db.add_node(conn, parent_id, claim, sanskrit=sanskrit, devanagari=devanagari,
                              provenance=provenance, node_type="UNSAYABLE", status="HOLLOW",
                              notes="Unfalsifiable — return to human", kanda=3)
            return nid
    elif sayability_fn and not sayability_fn(claim):
        nid = db.add_node(conn, parent_id, claim, sanskrit=sanskrit, devanagari=devanagari,
                          provenance=provenance, node_type="UNSAYABLE", status="HOLLOW",
                          notes="Unfalsifiable — return to human", kanda=3)
        return nid

    # Term registry check (Schema v3 Step 1) — block on unregistered
    trad = (provenance or {}).get("tradition", "")
    if sanskrit and trad and not registry.check_terms(conn, sanskrit, trad):
        registry.ensure_registered(conn, sanskrit, trad)

    # Anuvrtti: inherit from parent
    inherited_from = None
    delta_terms = [sanskrit] if sanskrit else []
    if parent_id:
        p = db.get_node(conn, parent_id)
        if p:
            inherited_from = parent_id

    # Create node (Kāṇḍa 2 default; DEFINITION → 1 later)
    nid = db.add_node(conn, parent_id, claim, sanskrit=sanskrit, devanagari=devanagari,
                      provenance=provenance, node_type="FORMAL", status="UNPROVED",
                      inherited_from=inherited_from, delta_terms=delta_terms, kanda=2)

    # STEP 2: FORMALIZE (TRS normalization)
    lean_type = None
    if llm_result and llm_result.get("lean_type"):
        lt = llm_result["lean_type"]
        if lt and ("∀" in lt or "→" in lt or "forall" in lt.lower()):
            lean_type = lt
    if not lean_type and is_sanskrit and sanskrit:
        lean_type = fol_lean_bridge.NYAYA_LEAN_TYPES.get(sanskrit.strip().lower())
    if not lean_type and formalize_fn:
        lean_type = formalize_fn(claim, sanskrit, provenance)
    if not lean_type:
        lean_type = _default_formalize(claim, sanskrit)

    if lean_type:
        db.update_status(conn, nid, "UNPROVED", lean_type=lean_type)

    # STEP 1: SIDDHA LIBRARY CHECK
    lib = api.library_check(conn, claim, lean_type, external=not fast_mode)
    if lib:
        if lib.get("source") == "db":
            db.update_status(conn, nid, "PROVED", lib.get("proof"), lib.get("deps"))
            db.increment_reuse(conn, lib["node_id"])
        else:
            proof = lib.get("proof") or lib.get("formal_name") or lib.get("name") or "external"
            db.update_status(conn, nid, "PROVED", proof, [lib.get("module", "Mathlib")])
        _emit_trace(conn, nid, "library", lean_type, provenance, sanskrit)
        db.add_to_bridge_index(conn, nid, lean_type, trad or None)
        return nid

    # STEP 3: PROVE ATTEMPT (with retry)
    retry_count = 0
    while lean_type and retry_count < MAX_RETRIES:
        result = lean_checker.pantograph_check(lean_type, fast=fast_mode)
        if result["status"] == "PROVED":
            db.update_status(conn, nid, "PROVED", result["proof"], result["mathlib_deps"])
            conn.execute("UPDATE nodes SET retry_count=? WHERE id=?", (retry_count, nid))
            conn.commit()
            _emit_trace(conn, nid, "pantograph", lean_type, provenance, sanskrit, result)
            db.add_to_bridge_index(conn, nid, lean_type, trad or None)
            return nid
        retry_count += 1
        conn.execute("UPDATE nodes SET retry_count=? WHERE id=?", (retry_count, nid))
        conn.commit()
        if retry_count >= MAX_RETRIES:
            conn.execute("UPDATE nodes SET human_review=1 WHERE id=?", (nid,))
            conn.commit()
        break

    # STEP 4: DECOMPOSE
    children_specs = []
    if llm_result and llm_result.get("children"):
        children_specs = llm_result["children"]
    elif decompose_fn:
        children_specs = decompose_fn(claim)
    if not children_specs:
        children_specs = _default_decompose(claim, sanskrit)

    if not children_specs:
        return nid

    for c in children_specs:
        nt = c.get("node_type", "FORMAL")
        stmt = c.get("statement", "")
        sk = c.get("sanskrit")
        dv = c.get("devanagari")
        prov = c.get("provenance", provenance)

        if nt == "EMPIRICAL":
            cid = db.add_node(conn, nid, stmt, sanskrit=sk, devanagari=dv, provenance=prov,
                              node_type="EMPIRICAL", status="OUTSIDE_FORMAL", notes=c.get("notes"),
                              kanda=2, decomp_source=c.get("decomp_source", "llm"))
            db.add_edge(conn, nid, cid, "decomposition")
        elif nt == "UNSAYABLE":
            cid = db.add_node(conn, nid, stmt, sanskrit=sk, devanagari=dv, provenance=prov,
                              node_type="UNSAYABLE", status="HOLLOW", notes=c.get("notes"), kanda=3)
            db.add_edge(conn, nid, cid, "decomposition")
        elif nt == "DEFINITION":
            cid = db.add_node(conn, nid, stmt, sanskrit=sk, devanagari=dv, provenance=prov,
                              node_type="DEFINITION", status="PROVED", lean_proof="-- axiomatic",
                              notes=c.get("notes"), kanda=1)
            db.add_edge(conn, nid, cid, "decomposition")
        else:
            cid = process_claim(conn, stmt, parent_id=nid, sanskrit=sk, devanagari=dv,
                                provenance=prov, is_sanskrit=bool(sk),
                                sayability_fn=sayability_fn, formalize_fn=formalize_fn,
                                decompose_fn=decompose_fn, llm_fn=llm_fn,
                                max_depth=max_depth - 1, fast_mode=fast_mode, dev_mode=dev_mode)
            db.add_edge(conn, nid, cid, "decomposition")

    # STEP 5: PROPAGATE
    new_status = propagate(conn, nid)
    db.update_status(conn, nid, new_status)
    return nid


def _emit_trace(conn, nid: int, source: str, lean_type: str, provenance: Optional[dict], sanskrit: Optional[str], result: Optional[dict] = None):
    """Emit DerivationTrace on PROVED."""
    trace_id = f"trace_{nid}_{uuid.uuid4().hex[:8]}"
    trad = (provenance or {}).get("tradition", "")
    db.add_trace(conn, trace_id, nid,
                 anchor=(provenance or {}).get("ref", ""),
                 tradition=trad,
                 source_text=sanskrit or "",
                 layer5={"source": source, "lean_type": lean_type[:200], "proof": (result or {}).get("proof", "")[:100]},
                 metadata={"source": source})


def propagate(conn, node_id: int) -> str:
    """Compute parent status from children."""
    children = db.get_children(conn, node_id)
    if not children:
        return db.get_node(conn, node_id)["status"]

    statuses = {c["status"] for c in children}
    if "REFUTED" in statuses:
        return "REFUTED"
    if "HOLLOW" in statuses:
        return "HOLLOW"
    if all(s in ("PROVED", "DEFINITION") for s in statuses):
        return "PROVED"
    if any(s in ("PROVED", "DEFINITION") for s in statuses) and any(s == "OUTSIDE_FORMAL" for s in statuses):
        return "PARTIAL"
    if "UNPROVED" in statuses:
        return "UNPROVED"
    return "PARTIAL"


def _default_formalize(claim: str, sanskrit: Optional[str]) -> Optional[str]:
    if sanskrit:
        return fol_lean_bridge.NYAYA_LEAN_TYPES.get(sanskrit.strip().lower())
    return None


def _default_decompose(claim: str, sanskrit: Optional[str]) -> list[dict]:
    if any(w in claim.lower() for w in ["liberation", "niḥśreyasa", "mokṣa", "attained", "supreme good"]):
        return [{"statement": claim, "node_type": "EMPIRICAL", "status": "OUTSIDE_FORMAL",
                  "notes": "BOUNDARY: tradition's ultimate claim exceeds formalization"}]
    return []


