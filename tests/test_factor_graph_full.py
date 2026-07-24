"""Full Bhairavastava factor graph test — all 9 verses."""
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score


def get_verses(conn):
    rows = conn.execute("""
        SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'abhinavagupta_bhairavastava'
        ORDER BY p.sequence_index
    """).fetchall()
    return rows


def add_compound_variable(g: FactorGraph, compounds: list[dict]):
    choices = [VariableChoice(c["id"], c, c.get("prior", 0.0)) for c in compounds]
    g.add_variable("compound", choices)


def add_frame_variable(g: FactorGraph, frames: list[dict]):
    choices = [VariableChoice(f["id"], f, f.get("prior", 0.0)) for f in frames]
    g.add_variable("frame", choices)


def verse_compounds(vn: int, rid: str) -> list[dict]:
    all_compounds = {
        1: [
            {"id": f"{rid}_karmadharaya_0", "relation": "karmadharaya", "member_tokens": [0], "prior": 0.3},
            {"id": f"{rid}_tatpurusa_0", "relation": "tatpurusa", "member_tokens": [0], "prior": -0.3},
            {"id": f"{rid}_karmadharaya_1", "relation": "karmadharaya", "member_tokens": [1], "prior": 0.2},
            {"id": f"{rid}_tatpurusa_1", "relation": "tatpurusa", "member_tokens": [1], "prior": 0.3},
            {"id": f"{rid}_karmadharaya_2", "relation": "karmadharaya", "member_tokens": [2], "prior": 0.2},
            {"id": f"{rid}_bahuvrihi_2", "relation": "bahuvrihi", "member_tokens": [2], "prior": 0.1},
        ],
        4: [
            {"id": f"{rid}_karmadharaya_0", "relation": "karmadharaya", "member_tokens": [0], "prior": 0.2},
            {"id": f"{rid}_karmadharaya_1", "relation": "karmadharaya", "member_tokens": [1], "prior": 0.2},
        ],
        5: [
            {"id": f"{rid}_dvandva_0", "relation": "dvandva", "member_tokens": [0], "prior": 0.2},
            {"id": f"{rid}_tatpurusa_0", "relation": "tatpurusa", "member_tokens": [0], "prior": 0.1},
        ],
        6: [
            {"id": f"{rid}_karmadharaya_0", "relation": "karmadharaya", "member_tokens": [0], "prior": 0.2},
        ],
        7: [
            {"id": f"{rid}_karmadharaya_2", "relation": "karmadharaya", "member_tokens": [2], "prior": 0.2},
        ],
        8: [
            {"id": f"{rid}_karmadharaya_0", "relation": "karmadharaya", "member_tokens": [0], "prior": 0.2},
            {"id": f"{rid}_karmadharaya_2", "relation": "karmadharaya", "member_tokens": [2], "prior": 0.2},
        ],
        9: [
            {"id": f"{rid}_karmadharaya_3", "relation": "karmadharaya", "member_tokens": [3], "prior": 0.2},
            {"id": f"{rid}_tatpurusa_7", "relation": "tatpurusa", "member_tokens": [7], "prior": 0.2},
        ],
    }
    return all_compounds.get(vn, [])


def test_all_verses():
    conn = connect(str(BASE / "data" / "sanskritree-v2.db"))
    verses = get_verses(conn)
    print(f"Running factor graph on {len(verses)} verses\n")

    results = []
    for pid, vs, rid, raw in verses:
        vn = int(vs) if vs else 0
        g = FactorGraph(pid)
        g.neighborhood(conn, rid)

        # Add compounds for this verse
        comps = verse_compounds(vn, rid)
        if comps:
            add_compound_variable(g, comps)

        # Add standard frame options
        add_frame_variable(g, [
            {"id": f"{rid}_devotional", "frame_type": "DevotionalAct", "prior": 0.3},
            {"id": f"{rid}_identity", "frame_type": "IdentityClaim", "prior": -0.3},
            {"id": f"{rid}_predication", "frame_type": "Predication", "prior": 0.0},
        ])

        register_graph(g)

        best, beliefs, energy = propagate_and_score(g, beam_width=30)

        # Collect key metrics
        selected = {}
        for vn2, c in best.choices.items():
            label = c.payload.get("lemma", c.payload.get("relation", c.payload.get("frame_type", "?")))
            selected[vn2] = (label, beliefs.get(c.hypothesis_id, 0.0))

        n_tokens = sum(1 for v in g.variables if v.startswith("token_"))
        n_hypotheses = sum(len(c) for c in g.variables.values())

        info = {
            "verse": vs,
            "tokens": n_tokens,
            "hypotheses": n_hypotheses,
            "energy": energy,
            "selected": selected,
        }
        results.append(info)

        tokens_str = ", ".join(f"{k}={v[0]}" for k, v in sorted(selected.items()) if k.startswith("token_"))
        extras = ", ".join(f"{k}={v[0]}({v[1]:.2f})" for k, v in sorted(selected.items()) if not k.startswith("token_"))
        print(f"  Verse {vs:2s}: {n_tokens} tokens/{n_hypotheses} hyps  energy={energy:.2f}")
        print(f"    tokens: {tokens_str[:80]}")
        print(f"    extras: {extras}")

    conn.close()

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    n_pass = sum(1 for r in results if r["energy"] < 10.0)
    print(f"  Verses with valid assignment: {n_pass}/{len(results)}")
    print(f"  Avg energy: {sum(r['energy'] for r in results)/len(results):.2f}")


if __name__ == "__main__":
    test_all_verses()
