"""Sprint 5: Graph-constrained rendering — JSON plan → auditable English.

Pipeline:
  Factor graph assignment → Semantic plan → Node-constrained JSON → Fluent English → Audit
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score

DB = str(BASE / "data" / "sanskritree-v2.db")


def build_semantic_plan(assignment: dict, passage_text: str = "") -> dict:
    """Convert factor graph assignment to a constrained semantic plan (Stage A)."""
    segments = []
    node_registry = set()
    uncertainties = []

    # Extract token analyses in order
    token_vars = [(n, c) for n, c in assignment.items() if n.startswith("token_")]
    token_vars.sort(key=lambda x: int(x[0].split("_")[1]))

    lemma_gloss = {
        "vand": "praise/worship", "hfd": "heart", "nATa": "lord",
        "anATa": "helpless", "saraRya": "refuge", "tvanmaya": "consisting of you",
        "citta": "mind", "BErava": "Bhairava", "mft": "death",
        "nIr": "lead", "deva": "god", "zaktI": "power", "Sambu": "Siva",
    }

    for var_name, choice in token_vars:
        payload = choice.payload
        lemma = payload.get("lemma", "")
        surface = payload.get("surface", "")
        engine = payload.get("engine", "")

        if lemma and lemma != "__unknown__":
            gloss = lemma_gloss.get(lemma, lemma)
            node_id = f"tok:{choice.hypothesis_id[:16]}"
            node_registry.add(node_id)
            segments.append({
                "segment_id": f"s{var_name}",
                "source_nodes": [node_id],
                "realization": gloss,
                "realization_type": "direct",
                "lemma": lemma,
                "surface": surface,
            })
        elif surface:
            uncertainties.append({
                "token": surface,
                "hypothesis_id": choice.hypothesis_id[:20],
                "reason": "no lemma available",
            })

    # Add compound info
    compound = assignment.get("compound")
    if compound:
        rel = compound.payload.get("relation", "")
        node_id = f"cmp:{compound.hypothesis_id[:16]}"
        node_registry.add(node_id)
        segments.append({
            "segment_id": "s_compound",
            "source_nodes": [node_id],
            "realization": rel or "compound",
            "realization_type": "direct",
        })

    # Add frame info  
    frame = assignment.get("frame")
    if frame:
        ft = frame.payload.get("frame_type", "")
        node_id = f"frm:{frame.hypothesis_id[:16]}"
        node_registry.add(node_id)
        segments.append({
            "segment_id": "s_frame",
            "source_nodes": [node_id],
            "realization": f"[frame: {ft}]",
            "realization_type": "implicit",
        })

    # Add implicit agent from verb morphology
    for var_name, choice in token_vars:
        feat = choice.payload.get("features", {})
        if feat.get("purusha") == "uttama":
            node_id = "implicit:agent_1sg"
            node_registry.add(node_id)
            segments.append({
                "segment_id": "s_agent",
                "source_nodes": [node_id],
                "realization": "I",
                "realization_type": "implicit",
                "evidence": "verb morphology (1st person)",
            })
            break

    ordering = [s["segment_id"] for s in segments]

    return {
        "source": passage_text[:100] if passage_text else "",
        "segments": segments,
        "ordering": ordering,
        "additions": [],
        "omissions": [],
        "uncertainties": uncertainties,
        "node_registry": list(node_registry),
    }


def validate_plan(plan: dict) -> list[str]:
    """Stage C: deterministic audit of a semantic plan."""
    errors = []
    seen_ids = set()
    all_nodes = set(plan.get("node_registry", []))

    for seg in plan.get("segments", []):
        sid = seg.get("segment_id", "")
        if sid in seen_ids:
            errors.append(f"Duplicate segment: {sid}")
        seen_ids.add(sid)

        for nid in seg.get("source_nodes", []):
            if nid not in all_nodes:
                errors.append(f"Node {nid} referenced but not registered")

        if not seg.get("realization"):
            errors.append(f"Segment {sid} has empty realization")

    # Check ordering
    for oid in plan.get("ordering", []):
        if oid not in seen_ids:
            errors.append(f"Ordering refs unknown segment: {oid}")

    # Check additions are declared
    for add in plan.get("additions", []):
        if not add.get("evidence"):
            errors.append(f"Addition '{add}' missing evidence")

    return errors


def render_english(plan: dict, style: str = "philological") -> str:
    """Stage B: render fluent English from a validated plan."""
    segments = {s["segment_id"]: s for s in plan.get("segments", [])}
    
    style_configs = {
        "construal": {"connect": ", ", "frame_tags": True},
        "philological": {"connect": " ", "frame_tags": False},
        "interpretive": {"connect": " ", "frame_tags": False, "expand": True},
    }
    cfg = style_configs.get(style, style_configs["philological"])

    ordered = []
    for oid in plan.get("ordering", []):
        seg = segments.get(oid)
        if not seg:
            continue
        text = seg["realization"]
        if text.startswith("[frame:") and cfg.get("frame_tags"):
            ordered.append(text)
        elif not text.startswith("[frame:"):
            ordered.append(text)

    result = cfg["connect"].join(ordered)
    result = result[0].upper() + result[1:] if result else ""
    if not result.endswith((".", "!", "?")):
        result += "."
    return result


def full_pipeline(passage_id: str, reading_id: str, conn) -> dict:
    """Run full graph-constrained rendering pipeline."""
    from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
    from sanskritree.inference.factors import register_graph
    from sanskritree.inference.propagation import propagate_and_score

    g = FactorGraph(passage_id)
    g.neighborhood(conn, reading_id)
    g.add_variable("compound", [
        VariableChoice("k", {"relation": "karmadharaya"}, 0.3),
        VariableChoice("t", {"relation": "tatpurusa"}, -0.3),
    ])
    g.add_variable("frame", [
        VariableChoice("d", {"frame_type": "DevotionalAct"}, 0.3),
        VariableChoice("i", {"frame_type": "IdentityClaim"}, -0.3),
    ])
    register_graph(g)

    best, beliefs, energy = propagate_and_score(g)
    source = conn.execute("SELECT sanskrit_raw FROM passage_readings WHERE reading_id=?", (reading_id,)).fetchone()
    source_text = source[0] if source else ""

    plan = build_semantic_plan(best.choices, source_text)
    errors = validate_plan(plan)

    translations = {}
    for style in ["construal", "philological", "interpretive"]:
        translations[style] = render_english(plan, style)

    return {
        "passage_id": passage_id,
        "source": source_text,
        "plan": plan,
        "validation_errors": errors,
        "translations": translations,
        "n_segments": len(plan["segments"]),
        "n_nodes": len(plan["node_registry"]),
        "n_uncertainties": len(plan["uncertainties"]),
        "valid": len(errors) == 0,
    }


def main():
    print("Sprint 5: Graph-constrained rendering\n")
    conn = connect(DB)

    # Test on Bhairavastava verse 1
    row = conn.execute("""
        SELECT p.passage_id, pr.reading_id FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'abhinavagupta_bhairavastava'
        ORDER BY p.sequence_index LIMIT 1
    """).fetchone()

    if row:
        result = full_pipeline(row[0], row[1], conn)
        print(f"Verse: {result['passage_id']}")
        print(f"Segments: {result['n_segments']}, Nodes: {result['n_nodes']}, Uncertainties: {result['n_uncertainties']}")
        print(f"Valid: {result['valid']}")
        if result['validation_errors']:
            for e in result['validation_errors']:
                print(f"  ERROR: {e}")
        print(f"\nConstrual:    {result['translations']['construal']}")
        print(f"Philological: {result['translations']['philological']}")
        print(f"Interpretive: {result['translations']['interpretive']}")

        # Save
        out = BASE / "proof" / "constrained_render_bv1.json"
        with open(out, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nSaved: {out}")

    conn.close()
    print("\nSprint 5 complete.")


if __name__ == "__main__":
    main()
