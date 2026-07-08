"""
Phase 1: Dharmakīrti — Pramāṇavārttika III (pratyakṣa chapter).
Per USER_GUIDE.md: kārikā = node, svavṛtti = decomposition.
logic_foundation: classical. NO bias toward provability.
"""

from . import db
from . import algorithm
from . import fol_lean_bridge
from . import registry


# PV III.3: pratyakṣaṃ kalpanāpoḍham — perception is free from conceptual construction
# DEFINITION terms = axiom, PROVED by stipulation (schema §0.8). No PLACEHOLDER.
PHASE1_TERMS = [
    {
        "sanskrit": "pratyakṣa",
        "definition": True,  # Dharmakīrti's definition of perception
        "devanagari": "प्रत्यक्ष",
        "statement": "Pratyakṣa (perception) of particulars (svalakṣaṇa) is free from conceptual construction (kalpanāpoḍha)",
        "source_text": "pratyakṣaṃ kalpanāpoḍham",
        "provenance": {
            "tradition": "dharmakirti",
            "text": "pramāṇavārttika",
            "ref": "III.3",
            "period": "~600-660CE",
            "author": "Dharmakīrti",
        },
        "expected_lean": "∀ (c : Cognition) (x : Svalaksana), Perceives c x → ¬ Kalpana c",
    },
    {
        "sanskrit": "kalpanā",
        "definition": True,
        "devanagari": "कल्पना",
        "statement": "Kalpanā: conceptual construction — cognition that associates with names, etc.",
        "provenance": {
            "tradition": "dharmakirti",
            "text": "pramāṇavārttika",
            "ref": "III.123",
            "period": "~600-660CE",
        },
        "expected_lean": "Kalpana : Cognition → Prop",
    },
    {
        "sanskrit": "svalakṣaṇa",
        "definition": True,
        "devanagari": "स्वलक्षण",
        "statement": "Svalakṣaṇa: the particular — inexpressible, object of perception only",
        "provenance": {
            "tradition": "dharmakirti",
            "text": "pramāṇavārttika",
            "ref": "III.1-3",
            "period": "~600-660CE",
        },
        "expected_lean": "Svalaksana : Type",
    },
    {
        "sanskrit": "arthakriyā",
        "devanagari": "अर्थक्रिया",
        "statement": "Arthakriyā: causal efficacy — what something does defines what it is",
        "provenance": {
            "tradition": "dharmakirti",
            "text": "pramāṇavārttika",
            "ref": "II",
            "period": "~600-660CE",
        },
        "expected_lean": "∀ (x : α), Arthakriya x → SuccessfulCognition x",
    },
    {
        "sanskrit": "pramāṇa",
        "devanagari": "प्रमाण",
        "statement": "Pramāṇa (Dharmakīrti): valid cognition defined by arthakriyā of its object",
        "provenance": {
            "tradition": "dharmakirti",
            "text": "pramāṇavārttika",
            "ref": "II.1",
            "period": "~600-660CE",
        },
        "expected_lean": "∀ (c : Cognition), Pramana c ↔ Arthakriya (object_of c)",
        "notes": "circular: pramāṇa ↔ arthakriyā ↔ successful cognition; mark coherentist",
    },
]


def _formalize_dharmakirti(claim: str, sanskrit: str | None, provenance: dict | None) -> str | None:
    """Use Dharmakīrti term mappings when tradition is dharmakirti."""
    if provenance and provenance.get("tradition") == "dharmakirti" and sanskrit:
        return fol_lean_bridge.DHARMAKIRTI_LEAN_TYPES.get(sanskrit.strip().lower())
    return None


def run_phase1(conn, terms: list[dict] | None = None, *, fast_mode: bool = True, agent_mode: bool = False) -> dict:
    """
    Run Phase 1 Dharmakīrti validation. Process each term through the algorithm.
    fast_mode=True: skip LeanSearch/Loogle/lake (default for quick runs).
    agent_mode=True: Qwen3.5/Chutes API for sayability, decomposition, formalization (autonomous).
    Returns {root_id, term_results, stats}.
    """
    terms = terms or PHASE1_TERMS

    llm_fn = None
    formalize_fn = _formalize_dharmakirti
    if agent_mode:
        from . import llm_client
        def _llm(claim, sanskrit, provenance):
            r = llm_client.process_claim(claim, sanskrit, provenance)
            if not r.get("lean_type") and sanskrit and provenance and provenance.get("tradition") == "dharmakirti":
                r["lean_type"] = _formalize_dharmakirti(claim, sanskrit, provenance)
            return r
        llm_fn = _llm

    # Bootstrap term registry
    registry.register_dharmakirti_terms(conn)

    root = db.add_node(
        conn,
        None,
        "Pramāṇavārttika III — pratyakṣa (perception): formal validation",
        sanskrit="pratyakṣaṃ kalpanāpoḍham",
        provenance={
            "tradition": "dharmakirti",
            "text": "pramāṇavārttika",
            "ref": "III.1",
            "period": "~600-660CE",
            "author": "Dharmakīrti",
        },
        node_type="FORMAL",
        status="UNPROVED",
        notes="Phase 1 Dharmakīrti root",
        kanda=2,
    )

    term_results = []
    for t in terms:
        if t.get("definition"):
            # DEFINITION = axiom, PROVED by stipulation. Kāṇḍa 1.
            lean_type = fol_lean_bridge.DHARMAKIRTI_LEAN_TYPES.get((t.get("sanskrit") or "").strip().lower())
            nid = db.add_node(conn, root, t["statement"],
                sanskrit=t.get("sanskrit"), devanagari=t.get("devanagari"),
                provenance=t.get("provenance"), node_type="DEFINITION", status="PROVED",
                lean_type=lean_type, lean_proof="-- axiomatic", notes="Dharmakīrti definition",
                kanda=1)
            db.add_edge(conn, root, nid, "decomposition")
            if lean_type:
                db.add_to_bridge_index(conn, nid, lean_type, "dharmakirti")
        else:
            nid = algorithm.process_claim(
                conn, t["statement"],
                parent_id=root,
                sanskrit=t.get("sanskrit"),
                devanagari=t.get("devanagari"),
                provenance=t.get("provenance"),
                is_sanskrit=True,
                formalize_fn=formalize_fn,
                llm_fn=llm_fn,
                max_depth=5,
                fast_mode=fast_mode,
                dev_mode=True,
            )
        node = db.get_node(conn, nid)
        term_results.append({
            "term": t.get("sanskrit"),
            "node_id": nid,
            "status": node["status"],
            "lean_type": node.get("lean_type"),
        })

    root_status = algorithm.propagate(conn, root)
    db.update_status(conn, root, root_status)

    rows = conn.execute("SELECT status, COUNT(*) FROM nodes GROUP BY status").fetchall()
    stats = dict(rows)

    return {
        "root_id": root,
        "term_results": term_results,
        "stats": stats,
        "root_status": root_status,
    }
