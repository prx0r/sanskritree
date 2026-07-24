"""Two-stage constrained English realization from factor graph assignments.

Stage A: Generate JSON semantic plan from selected hypotheses.
Stage B: Render fluent English from the plan (currently returns plan for LLM).
"""
from __future__ import annotations

import json
from typing import Any


def semantic_plan_from_assignment(
    assignment: dict,
    passage_text: str = "",
) -> dict[str, Any]:
    """Stage A: Convert a factor graph assignment into a structured JSON plan.

    Args:
        assignment: dict of var_name → VariableChoice (from best.choices)
        passage_text: original Sanskrit for reference

    Returns:
        dict with segments, ordering, additions, omissions, uncertainties
    """
    segments = []
    uncertain = []
    additions = []
    omissions = []

    # Collect token analyses in order
    token_vars = [(n, c) for n, c in assignment.items() if n.startswith("token_")]
    token_vars.sort(key=lambda x: int(x[0].split("_")[1]))

    for var_name, choice in token_vars:
        payload = choice.payload
        lemma = payload.get("lemma", "")
        features = payload.get("features", {})
        surface = payload.get("surface", "")
        engine = payload.get("engine", "")

        # Determine English gloss from lemma
        gloss_map = {
            "vand": "praise/worship",
            "hfd": "heart",
            "nATa": "lord",
            "anATa": "helpless",
            "saraRya": "refuge",
            "tvanmaya": "consisting of you",
            "citta": "mind",
            "BErava": "Bhairava",
            "mah": "great",
            "dEva": "lord/god",
            "tena": "by that",
            "mA": "my",
            "a": "",
            "ca": "and",
            "sUrya": "sun",
            "api": "even/also",
            "na": "not",
            "jAtu": "ever/at all",
            "aha": "I",
            "nirvf": "peace/bliss",
            "i": "to go",
            "udi": "arise",
            "eva": "indeed",
            "syand": "flow",
            "cit": "consciousness",
            "f": "",
            "prI": "beloved",
            "Ap": "to obtain",
            "sudarSana": "beautiful vision",
            "dus": "difficult",
            "aYji": "other people",
            "samayajJa": "knower of the right time",
        }
        gloss = gloss_map.get(lemma, lemma)

        if lemma and lemma != "__unknown__":
            segments.append({
                "segment_id": f"s{var_name}",
                "source_nodes": [f"token:{choice.hypothesis_id}"],
                "realization": gloss,
                "realization_type": "direct",
            })
        elif surface:
            # Compound or unknown token — note as uncertain
            uncertain.append({
                "token": surface,
                "hypothesis_id": choice.hypothesis_id,
                "reason": "no lemma mapping available",
            })

    # Add compound info
    compound = assignment.get("compound")
    if compound:
        rel = compound.payload.get("relation", "")
        gloss = compound.payload.get("gloss", "")
        segments.append({
            "segment_id": "s_compound",
            "source_nodes": [f"compound:{compound.hypothesis_id}"],
            "realization": gloss or rel,
            "realization_type": "direct",
        })

    # Add frame info
    frame = assignment.get("frame")
    if frame:
        ft = frame.payload.get("frame_type", "")
        segments.append({
            "segment_id": "s_frame",
            "source_nodes": [f"frame:{frame.hypothesis_id}"],
            "realization": f"[frame: {ft}]",
            "realization_type": "implicit",
        })

    # Build ordering
    ordering = [s["segment_id"] for s in segments]

    plan = {
        "source": passage_text[:100] if passage_text else "",
        "segments": segments,
        "ordering": ordering,
        "additions": additions,
        "omissions": omissions,
        "uncertainties": uncertain,
    }

    return plan


def validate_plan(plan: dict[str, Any]) -> list[str]:
    """Validate that a semantic plan is internally consistent.

    Returns list of validation errors (empty = valid).
    """
    errors = []
    seen_ids = set()
    for seg in plan.get("segments", []):
        sid = seg.get("segment_id", "")
        if sid in seen_ids:
            errors.append(f"Duplicate segment_id: {sid}")
        seen_ids.add(sid)
        if not seg.get("source_nodes"):
            errors.append(f"Segment {sid} has no source_nodes")
        if not seg.get("realization"):
            errors.append(f"Segment {sid} has no realization")

    # Check all ordering refs exist
    for oid in plan.get("ordering", []):
        if oid not in seen_ids:
            errors.append(f"Ordering references unknown segment: {oid}")

    return errors


def render_english(plan: dict[str, Any]) -> str:
    """Stage B: Produce fluent English from a validated plan.

    Currently a simple concatenation. In production, this would be
    an LLM call constrained to use only approved segments.
    """
    segments = {s["segment_id"]: s for s in plan.get("segments", [])}
    ordered = []
    for oid in plan.get("ordering", []):
        if oid in segments:
            text = segments[oid]["realization"]
            if not text.startswith("[frame:"):
                ordered.append(text)

    # Simple heuristics for fluency
    text = ", ".join(ordered)
    text = text[0].upper() + text[1:] if text else ""
    text += "."
    return text
