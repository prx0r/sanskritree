"""
Bridge Probe. Only runs on claim pairs that share >= 1 primitive.
Tries A -> B, B -> A, A -> ¬B. Classifies: SUBSUMES | BRIDGES | CONTRADICTS | OVERLAPS.
"""

from enum import Enum
from dataclasses import dataclass

from . import db
from . import lean_checker


class RelationType(Enum):
    SUBSUMES = "subsumes"      # A implies B, not vice versa
    BRIDGES = "bridges"        # A <-> B (same formal structure)
    CONTRADICTS = "contradicts"
    OVERLAPS = "overlaps"      # share primitives, no formal connection


@dataclass
class ProbeResult:
    proved: bool
    note: str


def pantograph_attempt(lean_type: str, *, fast: bool = True) -> ProbeResult:
    """Attempt to prove the given Lean type."""
    r = lean_checker.pantograph_check(lean_type, fast=fast)
    return ProbeResult(
        proved=(r["status"] == "PROVED"),
        note=r.get("note", ""),
    )


def probe_pair(conn, a: dict, b: dict, *, fast: bool = True) -> RelationType:
    """
    Probe relation between claims a and b. Both must have lean_type.
    Returns RelationType.
    """
    lt_a = a.get("lean_type")
    lt_b = b.get("lean_type")
    if not lt_a or not lt_b:
        return RelationType.OVERLAPS

    # Try A -> B
    result_ab = pantograph_attempt(f"{lt_a} → {lt_b}", fast=fast)
    # Try B -> A
    result_ba = pantograph_attempt(f"{lt_b} → {lt_a}", fast=fast)
    # Try A -> ¬B
    result_contra = pantograph_attempt(f"{lt_a} → ¬{lt_b}", fast=fast)

    return classify_relation(result_ab, result_ba, result_contra)


def classify_relation(ab: ProbeResult, ba: ProbeResult, contra: ProbeResult) -> RelationType:
    if ab.proved and ba.proved:
        return RelationType.BRIDGES
    if ab.proved and not ba.proved:
        return RelationType.SUBSUMES
    if ba.proved and not ab.proved:
        return RelationType.SUBSUMES  # B subsumes A; we store (source, target) so we'd need to swap
    if contra.proved:
        return RelationType.CONTRADICTS
    return RelationType.OVERLAPS


def extract_bridge_axioms(ab: ProbeResult, ba: ProbeResult) -> str:
    """If proved with extra axioms, extract them. Placeholder."""
    if ab.proved and ba.proved:
        return ""
    if ab.proved:
        return ab.note or ""
    if ba.proved:
        return ba.note or ""
    return ""


def probe_all_bridges(conn, *, fast: bool = True) -> list[dict]:
    """
    Run bridge probe on all pairs sharing >= 1 primitive.
    Skip negative controls. Store relations.
    Returns list of {a, b, relation_type, bridge_axioms}.
    """
    pairs = db.get_claims_sharing_primitives(conn)
    results = []

    for a, b in pairs:
        if db.is_negative_control(conn, a["id"], b["id"]):
            continue

        lt_a = a.get("lean_type")
        lt_b = b.get("lean_type")
        if not lt_a or not lt_b:
            continue

        result_ab = pantograph_attempt(f"{lt_a} → {lt_b}", fast=fast)
        result_ba = pantograph_attempt(f"{lt_b} → {lt_a}", fast=fast)
        result_contra = pantograph_attempt(f"{lt_a} → ¬{lt_b}", fast=fast)

        relation = classify_relation(result_ab, result_ba, result_contra)
        bridge_axioms = extract_bridge_axioms(result_ab, result_ba)

        # Store: for SUBSUMES, source is the stronger one (the one that implies the other)
        if relation == RelationType.SUBSUMES:
            if result_ab.proved:
                source_id, target_id = a["id"], b["id"]
                evidence = f"Lean: A -> B proved. {result_ab.note}"
            else:
                source_id, target_id = b["id"], a["id"]
                evidence = f"Lean: B -> A proved. {result_ba.note}"
        else:
            source_id, target_id = a["id"], b["id"]
            evidence = f"Lean probe: ab={result_ab.note}, ba={result_ba.note}, contra={result_contra.note}"

        db.add_claim_relation(
            conn,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation.value,
            bridge_axioms=bridge_axioms or None,
            evidence=evidence,
            verified_by="lean",
        )
        results.append({
            "a": a["id"],
            "b": b["id"],
            "relation_type": relation.value,
            "bridge_axioms": bridge_axioms,
        })

    return results
