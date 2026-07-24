"""Test factor graph on Bhairavastava verse 1."""
from __future__ import annotations

import sys
import json
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice, Assignment
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score


def get_bhairavastava_reading_id(conn) -> str:
    row = conn.execute("""
        SELECT pr.reading_id FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'abhinavagupta_bhairavastava'
        ORDER BY p.sequence_index LIMIT 1
    """).fetchone()
    return row[0] if row else None


def add_compound_variable(g: FactorGraph, compounds: list[dict]):
    """Add compound analysis choices."""
    choices = []
    for c in compounds:
        choices.append(VariableChoice(
            hypothesis_id=c["id"],
            payload=c,
            prior_logit=c.get("prior", 0.0),
        ))
    g.add_variable("compound", choices)


def add_frame_variable(g: FactorGraph, frames: list[dict]):
    """Add semantic frame choices."""
    choices = []
    for f in frames:
        choices.append(VariableChoice(
            hypothesis_id=f["id"],
            payload=f,
            prior_logit=f.get("prior", 0.0),
        ))
    g.add_variable("frame", choices)


def test_bhairavastava_v1():
    """Factor graph should rank karmadharaya > tatpurusa for verse 1."""
    conn = connect(str(BASE / "data" / "sanskritree-v2.db"))
    rid = get_bhairavastava_reading_id(conn)
    assert rid is not None, "Bhairavastava reading not found"

    g = FactorGraph("bhairavastava.1")
    g.neighborhood(conn, rid)

    # Add compound alternatives
    add_compound_variable(g, [
        {
            "id": "compound_karmadharaya",
            "relation": "karmadharaya",
            "member_tokens": [0],
            "gloss": "Bhairava who is the Lord (appositional)",
            "prior": 0.5,
        },
        {
            "id": "compound_tatpurusa",
            "relation": "tatpurusa",
            "member_tokens": [0],
            "gloss": "the lord of Bhairava (genitive relation)",
            "prior": -0.5,
        },
    ])

    # Add frame alternatives
    add_frame_variable(g, [
        {
            "id": "frame_devotional",
            "frame_type": "DevotionalAct",
            "prior": 0.3,
        },
        {
            "id": "frame_identity",
            "frame_type": "IdentityClaim",
            "prior": -0.3,
        },
    ])

    register_graph(g)

    # Run inference
    best, beliefs, energy = propagate_and_score(g, beam_width=20)

    print(f"\nBhairavastava v1 — Factor graph result")
    print(f"  Energy: {energy:.4f}")
    print(f"  Best assignment:")
    for var_name, choice in best.choices.items():
        print(f"    {var_name}: {choice.payload.get('lemma', choice.payload.get('relation', choice.payload.get('frame_type', '?')))}[{choice.hypothesis_id[:20]}...]")

    print(f"\n  Beliefs (all):")
    sorted_beliefs = sorted(beliefs.items(), key=lambda x: -x[1])
    for hid, bel in sorted_beliefs:
        for vn, choices in g.variables.items():
            for c in choices:
                if c.hypothesis_id == hid:
                    label = c.payload.get("lemma", c.payload.get("relation", c.payload.get("frame_type", "?")))
                    print(f"    {vn:15s} {label:25s} belief={bel:.4f}")
                    break

    # Check: karmadharaya belief > tatpurusa belief
    compound_choices = {c.hypothesis_id: c for c in g.variables.get("compound", [])}
    kid = [k for k in compound_choices if "karmadharaya" in k]
    tid = [k for k in compound_choices if "tatpurusa" in k]

    if kid and tid:
        kb = beliefs.get(kid[0], 0.0)
        tb = beliefs.get(tid[0], 0.0)
        print(f"\n  Compound ranking: karmadharaya={kb:.4f}  tatpurusa={tb:.4f}  margin={kb - tb:.4f}")
        assert kb > tb, f"karmadharaya should rank higher than tatpurusa (got {kb} vs {tb})"
        print("  ✅ PASS: karmadharaya > tatpurusa")
    else:
        print("  ⚠️  Compound variables not found — check naming")

    # Check: DevotionalAct belief > IdentityClaim
    frame_choices = {c.hypothesis_id: c for c in g.variables.get("frame", [])}
    fid = [k for k in frame_choices if "devotional" in k]
    iid = [k for k in frame_choices if "identity" in k]

    if fid and iid:
        fb = beliefs.get(fid[0], 0.0)
        ib = beliefs.get(iid[0], 0.0)
        print(f"  Frame ranking: DevotionalAct={fb:.4f}  IdentityClaim={ib:.4f}  margin={fb - ib:.4f}")
        assert fb > ib, f"DevotionalAct should rank higher than IdentityClaim"
        print("  ✅ PASS: DevotionalAct > IdentityClaim")
    else:
        print("  ⚠️  Frame variables not found")

    conn.close()
    return beliefs


if __name__ == "__main__":
    test_bhairavastava_v1()
