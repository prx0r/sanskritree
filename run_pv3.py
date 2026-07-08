#!/usr/bin/env python3
"""
Run 1 Dharmakīrti kārikā: PV III.3 pratyakṣaṃ kalpanāpoḍham.
Uses Pantograph, LeanSearch, Loogle, proof_engine_lean.
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from proof_engine.db import init_db, add_node, get_node, update_status, add_edge
from proof_engine import algorithm
from proof_engine import fol_lean_bridge
from proof_engine import registry
from proof_engine.sanskrit_pipeline import process_sanskrit

# PV III.3 — one kārikā
PV3 = {
    "sanskrit": "pratyakṣa",
    "devanagari": "प्रत्यक्ष",
    "statement": "Pratyakṣa (perception) of particulars (svalakṣaṇa) is free from conceptual construction (kalpanāpoḍha)",
    "source_text": "pratyakṣaṃ kalpanāpoḍham",
    "provenance": {"tradition": "dharmakirti", "text": "pramāṇavārttika", "ref": "III.3", "period": "~600-660CE", "author": "Dharmakīrti"},
}

def main():
    conn = init_db("pv3.db")
    registry.register_dharmakirti_terms(conn)
    # Sanskrit pipeline (Heritage/SanskritShala) for IAST
    parsed = process_sanskrit(PV3["source_text"])
    lean_candidate = parsed.get("lean_type_candidate")

    root = add_node(conn, None, "PV III.3 pratyakṣaṃ kalpanāpoḍham",
        sanskrit="pratyakṣaṃ kalpanāpoḍham",
        provenance=PV3["provenance"],
        notes="Single kārikā run")

    def formalize(c, s, p):
        return (lean_candidate or fol_lean_bridge.DHARMAKIRTI_LEAN_TYPES.get((s or "").strip().lower())) if s else None
    nid = algorithm.process_claim(
        conn, PV3["statement"],
        parent_id=root,
        sanskrit=PV3["sanskrit"],
        devanagari=PV3["devanagari"],
        provenance=PV3["provenance"],
        is_sanskrit=True,
        formalize_fn=formalize,
        max_depth=3,
        fast_mode=False,  # full: Pantograph, LeanSearch, Loogle
        dev_mode=True,
    )
    add_edge(conn, root, nid, "decomposition")
    root_status = algorithm.propagate(conn, root)
    update_status(conn, root, root_status)

    node = get_node(conn, nid)
    print("PV III.3 pratyakṣaṃ kalpanāpoḍham")
    print("status:", node["status"])
    print("lean_type:", (node.get("lean_type") or "")[:80])
    print("lean_proof:", (node.get("lean_proof") or "")[:60])
    print("OK")

if __name__ == "__main__":
    main()
