"""M3: Adjudicate all 9 Bhairavastava verses — factor graph + decisions + proof bundles."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score
from sanskritree.translation.realization import semantic_plan_from_assignment, validate_plan, render_english

DB = str(BASE / "data" / "sanskritree-v2.db")
OUT = BASE / "proof"
OUT.mkdir(parents=True, exist_ok=True)

# Compound patterns for all 9 verses
COMPOUNDS = {
    1: [("compound_k1", "karmadharaya", 0.3), ("compound_t1", "tatpurusa", -0.3),
        ("compound_k2", "karmadharaya", 0.2), ("compound_t2", "tatpurusa", 0.3),
        ("compound_k3", "karmadharaya", 0.2), ("compound_b3", "bahuvrihi", 0.1)],
    4: [("compound_k4a", "karmadharaya", 0.3), ("compound_k4b", "karmadharaya", 0.3)],
    5: [("compound_d5", "dvandva", 0.3), ("compound_t5", "tatpurusa", 0.2)],
    6: [("compound_k6", "karmadharaya", 0.3)],
    7: [("compound_k7", "karmadharaya", 0.3)],
    8: [("compound_k8a", "karmadharaya", 0.3), ("compound_k8b", "karmadharaya", 0.3)],
    9: [("compound_k9", "karmadharaya", 0.3), ("compound_t9", "tatpurusa", 0.3)],
}


def get_verses(conn):
    return conn.execute("""
        SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'abhinavagupta_bhairavastava'
        ORDER BY p.sequence_index
    """).fetchall()


def adjudicate_verse(conn, pid, vs, rid, raw) -> dict:
    vn = int(vs) if vs else 0
    g = FactorGraph(pid)
    g.neighborhood(conn, rid)

    # Add compounds for this verse
    for hid, rel, prior in COMPOUNDS.get(vn, []):
        g.add_variable("compound", [VariableChoice(hid, {"relation": rel}, prior)])

    # Add frame options
    g.add_variable("frame", [
        VariableChoice("fr_dev", {"frame_type": "DevotionalAct"}, 0.3),
        VariableChoice("fr_id", {"frame_type": "IdentityClaim"}, -0.3),
        VariableChoice("fr_pred", {"frame_type": "Predication"}, 0.0),
    ])

    register_graph(g)
    best, beliefs, energy = propagate_and_score(g, beam_width=30)

    n_tokens = sum(1 for v in g.variables if v.startswith("token_"))
    n_hyp = sum(len(c) for c in g.variables.values())

    # Build interpretation
    interp = {}
    for vn2, c in best.choices.items():
        if vn2.startswith("token_"):
            lem = c.payload.get("lemma", "?")
            hyp = c.hypothesis_id[:30]
            bel = round(beliefs.get(c.hypothesis_id, 0), 4)
            interp[vn2] = f"{lem}({bel})"
        elif vn2 == "compound":
            interp["compound"] = f"{c.payload.get('relation','?')}({round(beliefs.get(c.hypothesis_id,0), 4)})"
        elif vn2 == "frame":
            interp["frame"] = f"{c.payload.get('frame_type','?')}({round(beliefs.get(c.hypothesis_id,0), 4)})"

    return {
        "passage_id": pid,
        "verse": vs,
        "source": raw,
        "tokens": n_tokens,
        "hypotheses": n_hyp,
        "energy": round(energy, 4),
        "interpretation": interp,
        "beliefs": {k[:30]: round(v, 4) for k, v in beliefs.items()},
    }


def main():
    print("M3: Adjudicating all 9 Bhairavastava verses\n")
    conn = connect(DB)
    verses = get_verses(conn)
    results = []
    errors = []

    for pid, vs, rid, raw in verses:
        try:
            r = adjudicate_verse(conn, pid, vs, rid, raw)
            results.append(r)
            comp = r["interpretation"].get("compound", "-")
            fram = r["interpretation"].get("frame", "-")
            print(f"  Verse {vs:2s}: {r['tokens']} tokens/{r['hypotheses']} hyps  energy={r['energy']:.4f}")
            print(f"           compound={comp}  frame={fram}")
        except Exception as e:
            errors.append({"verse": vs, "error": str(e)})
            print(f"  Verse {vs:2s}: ERROR — {e}")

    # Save
    out = {
        "pipeline": "M3 — Bhairavastava adjudication",
        "date": "2026-07-24",
        "verses_total": len(verses),
        "verses_ok": len(results),
        "verses_error": len(errors),
        "results": results,
        "errors": errors,
    }
    path = OUT / "bhairavastava_all.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n  ✅ {len(results)}/{len(verses)} verses adjudicated")
    if errors:
        print(f"  ❌ {len(errors)} errors: {errors}")
    print(f"  📄 Saved to {path}")
    conn.close()


if __name__ == "__main__":
    main()
