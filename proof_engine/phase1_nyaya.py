"""
Phase 1: Nyāya-Sūtras validation per proofenginge.md.
Terms in order: pramāṇa → saṃśaya → vyāpti → anumāna → nigrahasthāna.
NO bias toward Shannon/entropy. Decompose faithfully. PARTIAL/OUTSIDE_FORMAL are correct.
"""

from . import db
from . import algorithm
from . import fol_lean_bridge
from . import sanskrit_pipeline


PHASE1_TERMS = [
    {
        "sanskrit": "pramāṇa",
        "devanagari": "प्रमाण",
        "statement": "Pramāṇa: valid means of cognition produces true belief about its object",
        "provenance": {"tradition": "nyaya", "text": "nyaya_sutra", "ref": "1.1.3", "period": "~200CE", "author": "Gautama"},
        "expected_lean": "∀ (source : Type) (belief : Prop), ValidCognition source belief → belief",
    },
    {
        "sanskrit": "saṃśaya",
        "devanagari": "संशय",
        "statement": "Saṃśaya: doubt arises when cognition fails to uniquely determine its object",
        "provenance": {"tradition": "nyaya", "text": "nyaya_sutra", "ref": "1.1.23", "period": "~200CE"},
        "expected_lean": "∀ (obj : α), Doubt obj ↔ ¬(∃! (c : Cognition), Determines c obj)",
    },
    {
        "sanskrit": "vyāpti",
        "devanagari": "व्याप्ति",
        "statement": "Vyāpti: wherever hetu exists, sādhya exists — universal concomitance",
        "provenance": {"tradition": "navya_nyaya", "text": "tattvacintamani", "ref": "vyapti", "period": "14th_century_CE", "author": "Gaṅgeśa"},
        "expected_lean": "∀ (α : Type*) (Hetu Sadhya : α → Prop), (∀ x, Hetu x → Sadhya x)",
    },
    {
        "sanskrit": "anumāna",
        "devanagari": "अनुमान",
        "statement": "Anumāna: inference via five-membered syllogism (pratijñā, hetu, udāharaṇa, upanaya, nigamana)",
        "provenance": {"tradition": "nyaya", "text": "nyaya_sutra", "ref": "1.1.5", "period": "~200CE"},
    },
    {
        "sanskrit": "nigrahasthāna",
        "devanagari": "निग्रहस्थान",
        "statement": "Nigrahasthāna: grounds for defeat in debate — formal fallacy catalogue",
        "provenance": {"tradition": "nyaya", "text": "nyaya_sutra", "ref": "5.2", "period": "~200CE"},
    },
]


def run_phase1(conn, terms: list[dict] | None = None, *, fast_mode: bool = True) -> dict:
    """
    Run Phase 1 validation. Process each term through the algorithm.
    fast_mode=True: skip LeanSearch/Loogle/lake (default for quick runs).
    Returns {root_id, term_results, stats}.
    """
    terms = terms or PHASE1_TERMS
    root = db.add_node(
        conn, None,
        "Nyāya-Sūtras 1.1 — sixteen padārthas: formal validation",
        sanskrit="pramāṇa-prameya-saṃśaya-...",
        provenance={"tradition": "nyaya", "text": "nyaya_sutra", "ref": "1.1.1"},
        node_type="FORMAL", status="UNPROVED", notes="Phase 1 root"
    )

    term_results = []
    for t in terms:
        nid = algorithm.process_claim(
            conn,
            t["statement"],
            parent_id=root,
            sanskrit=t.get("sanskrit"),
            devanagari=t.get("devanagari"),
            provenance=t.get("provenance"),
            is_sanskrit=True,
            max_depth=5,
            fast_mode=fast_mode,
        )
        node = db.get_node(conn, nid)
        term_results.append({
            "term": t.get("sanskrit"),
            "node_id": nid,
            "status": node["status"],
            "lean_type": node.get("lean_type"),
        })

    # Propagate root
    root_status = algorithm.propagate(conn, root)
    db.update_status(conn, root, root_status)

    # Stats
    rows = conn.execute("SELECT status, COUNT(*) FROM nodes GROUP BY status").fetchall()
    stats = dict(rows)

    return {
        "root_id": root,
        "term_results": term_results,
        "stats": stats,
        "root_status": root_status,
    }


def run_ns_1_1_1_full(conn) -> dict:
    """
    Full NS 1.1.1 decomposition per proofenginge.
    Root: "By true knowledge of the sixteen categories, supreme good is attained"
    Splits: (a) soteriological [EMPIRICAL] (b) structural [FORMAL]
    """
    root = db.add_node(
        conn, None,
        "By true knowledge of the sixteen categories, supreme good (niḥśreyasa) is attained",
        sanskrit="pramāṇa-prameya-saṃśaya-...",
        devanagari="प्रमाण-प्रमेय-संशय...",
        provenance={"text": "nyaya_sutra", "book": 1, "chapter": 1, "sutra": 1, "tradition": "nyaya", "period": "~200CE", "author": "Gautama"},
        node_type="FORMAL", status="UNPROVED", notes="Root. Splits into soteriological + structural."
    )

    # Liberation branch — EMPIRICAL, OUTSIDE_FORMAL
    lib = db.add_node(
        conn, root,
        "True knowledge leads to liberation (niḥśreyasa)",
        sanskrit="tattvajñānān niḥśreyasādhigamaḥ",
        node_type="EMPIRICAL", status="OUTSIDE_FORMAL",
        notes="BOUNDARY. Liberation has no agreed formal definition."
    )

    # Structure branch — FORMAL
    struct = db.add_node(
        conn, root,
        "The sixteen padārthas form a complete system for valid cognition",
        sanskrit="ṣoḍaśa-padārtha-sākalyam",
        node_type="FORMAL", status="UNPROVED", notes="Completeness claim. Decomposes."
    )

    # Process pramāṇa, saṃśaya, vyāpti under structure
    for t in PHASE1_TERMS[:3]:
        algorithm.process_claim(
            conn, t["statement"],
            parent_id=struct,
            sanskrit=t.get("sanskrit"),
            devanagari=t.get("devanagari"),
            provenance=t.get("provenance"),
            is_sanskrit=True,
            max_depth=4,
        )

    root_status = algorithm.propagate(conn, root)
    db.update_status(conn, root, root_status)

    return {"root_id": root, "root_status": root_status}
