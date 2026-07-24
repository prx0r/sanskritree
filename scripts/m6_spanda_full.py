"""M6: Full Spandakārikā processing — factor graph + proof bundle for all 53 verses."""
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

DB = str(BASE / "data" / "sanskritree-v2.db")
OUT = BASE / "proof"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    print("M6: Processing Spandakārikā (53 verses)\n")
    conn = connect(DB)

    verses = conn.execute("""
        SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'spandakarika' AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """).fetchall()

    results = []
    for pid, vs, rid, raw in verses:
        import re
        clean = re.sub(r'\|\|\s*vspk_\d+\.\d+\s*\|\|?$', '', raw).strip()

        g = FactorGraph(pid)
        g.neighborhood(conn, rid)
        g.add_variable("frame", [
            VariableChoice("fr_d", {"frame_type": "DevotionalAct"}, 0.2),
            VariableChoice("fr_i", {"frame_type": "IdentityClaim"}, 0.0),
            VariableChoice("fr_p", {"frame_type": "Predication"}, 0.1),
        ])
        register_graph(g)
        best, beliefs, energy = propagate_and_score(g, beam_width=30)

        n_tokens = sum(1 for v in g.variables if v.startswith("token_"))
        n_hyp = sum(len(c) for c in g.variables.values())

        results.append({
            "verse": vs,
            "source": clean,
            "tokens": n_tokens,
            "hypotheses": n_hyp,
            "energy": round(energy, 4),
        })

    # Save
    out = {
        "pipeline": "M6 — Spandakārikā full processing",
        "verses": len(results),
        "avg_tokens": sum(r["tokens"] for r in results) / len(results),
        "avg_hypotheses": sum(r["hypotheses"] for r in results) / len(results),
        "results": results,
    }
    path = OUT / "spandakarika_all.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    ok = sum(1 for r in results if r["energy"] < 10.0)
    print(f"  {ok}/{len(results)} verses with valid assignments")
    print(f"  Avg tokens/verse: {out['avg_tokens']:.1f}")
    print(f"  Avg hypotheses/verse: {out['avg_hypotheses']:.1f}")
    print(f"  Saved: {path}")
    conn.close()


if __name__ == "__main__":
    main()
