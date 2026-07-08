"""
Ground truth loader. Seeds the graph from Mathlib + PhysLean + primitives.
Three-tier structure: Tier 1 (Mathlib theorems), Tier 2 (functional primitives), Tier 3 (tradition axioms).
"""

import json
import uuid
from pathlib import Path
from . import db

GROUND_TRUTH_DIR = Path(__file__).resolve().parents[1] / "ground_truth"


def load_json(name: str) -> dict:
    path = GROUND_TRUTH_DIR / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_mathlib_catalog() -> dict:
    return load_json("mathlib_catalog.json")


def load_physlean_catalog() -> dict:
    return load_json("physlean_catalog.json")


def load_iit_formal_types() -> dict:
    return load_json("iit_formal_types.json")


def load_primitives_tier2() -> dict:
    return load_json("primitives_tier2.json")


def load_claims(tradition: str) -> dict:
    m = {"iit": "iit_claims.json", "gwt": "gwt_claims.json", "dharmakirti": "dharmakirti_claims.json", "nyaya": "nyaya_claims.json"}
    return load_json(m.get(tradition, f"{tradition}_claims.json"))


def load_negative_controls() -> dict:
    return load_json("negative_controls.json")


def seed_ground_truth(conn) -> dict:
    """Seed ground_truth table from catalogs. Specific theorems with signatures."""
    gt_count = 0

    # Mathlib — fixed_points, functions, relations, finset, topology, logic, sets, measure_theory, order, graph_theory
    mathlib = load_mathlib_catalog()
    for key in ("fixed_points", "functions", "relations", "finset", "topology", "logic", "sets", "measure_theory", "order", "graph_theory"):
        if key not in mathlib or not isinstance(mathlib[key], dict):
            continue
        section = mathlib[key]
        module = section.get("module", "")
        for item in section.get("items", []):
            conn.execute("""
                INSERT OR IGNORE INTO ground_truth (source, module_path, item_name, item_type, lean_signature, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, ("mathlib", module, item.get("name"), "theorem", item.get("signature", "")))
            gt_count += 1
    conn.commit()

    # PhysLean — causal_structure, information, quantum, pearl_causality
    physlean = load_physlean_catalog()
    for key in ("causal_structure", "information", "quantum", "pearl_causality"):
        if key not in physlean or not isinstance(physlean[key], dict):
            continue
        section = physlean[key]
        for item in section.get("items", []):
            conn.execute("""
                INSERT OR IGNORE INTO ground_truth (source, module_path, item_name, item_type, lean_signature, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, ("physlean", key, item.get("name"), "definition", item.get("signature", "")))
            gt_count += 1

    # IIT formal types (Kleiner & Tull 2020)
    iit = load_iit_formal_types()
    for key in ("system_class", "experience_space", "repertoire", "integration", "classical_iit"):
        if key not in iit or not isinstance(iit[key], dict):
            continue
        section = iit[key]
        for item in section.get("items", []):
            sig = item.get("signature", "")
            if item.get("def"):
                sig = f"{sig} [{item['def']}]"
            conn.execute("""
                INSERT OR IGNORE INTO ground_truth (source, module_path, item_name, item_type, lean_signature, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, ("kleiner_tull_2020", key, item.get("name"), "definition", sig))
            gt_count += 1
    conn.commit()

    return {"ground_truth_count": gt_count}


def seed_primitives_tier2(conn) -> int:
    """Seed primitives table with Tier 2 functional primitives only."""
    data = load_primitives_tier2()
    count = 0
    for p in data.get("primitives", []):
        conn.execute("""
            INSERT OR REPLACE INTO primitives (primitive_id, definition, lean_hint, source, status, created_at)
            VALUES (?, ?, ?, ?, 'tier2', datetime('now'))
        """, (p["id"], p.get("definition", ""), p.get("lean_hint", ""), "primitives_tier2"))
        count += 1
    conn.commit()
    return count


def seed_claims(conn) -> dict:
    """Seed claims table from iit, gwt, dharmakirti, nyaya + iit_integration_decomposed."""
    count = 0
    for trad, fname in [("iit", "iit_claims"), ("gwt", "gwt_claims"), ("dharmakirti", "dharmakirti_claims"), ("nyaya", "nyaya_claims")]:
        data = load_json(f"{fname}.json")
        for c in data.get("claims", []):
            cid = c.get("id", str(uuid.uuid4())[:8])
            full_id = f"{trad}_{cid}"
            conn.execute("""
                INSERT OR REPLACE INTO claims (id, tradition, statement, plain, primitive_hint, sanskrit, lean_type, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', datetime('now'))
            """, (full_id, trad, c.get("statement", ""), c.get("plain", ""), c.get("primitive_hint"), c.get("sanskrit"), c.get("lean_type")))
            count += 1

    # Fully decomposed worked example (IIT Integration)
    dec = load_json("iit_integration_decomposed.json")
    if dec.get("id"):
        conn.execute("""
            INSERT OR REPLACE INTO claims (id, tradition, statement, plain, primitive_hint, sanskrit, lean_type, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', datetime('now'))
        """, (dec["id"], dec.get("tradition", "iit"), dec.get("statement", ""), dec.get("statement", ""), "Integration", None, None))
        count += 1
    conn.commit()
    return {"claims_count": count}


def seed_negative_controls(conn) -> int:
    """Seed negative_controls — known non-bridges for testing (cross-tradition and within-tradition)."""
    conn.execute("DELETE FROM negative_controls")
    data = load_negative_controls()
    count = 0
    for pair in data.get("pairs", []):
        conn.execute("""
            INSERT OR IGNORE INTO negative_controls (a, b, reason, source, failure_type, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (pair.get("a", ""), pair.get("b", ""), pair.get("reason", ""), pair.get("source", ""), pair.get("failure_type")))
        count += 1
    conn.commit()
    return count


def seed_graph_nodes(conn) -> dict:
    """
    Create initial graph nodes. Three-tier structure.
    Root → Tier1 (Mathlib ~12) → Tier1 (PhysLean ~9) → Tier2 (primitives ~7) → Tier3/Sanskrit (4) → Negative controls (~8)
    """
    root = db.add_node(
        conn, None,
        "Consciousness theory map — ground truth",
        node_type="FORMAL", status="PROVED",
        source_module="ground_truth",
        notes="Three-tier: Tier1 (Mathlib+PhysLean), Tier2 (functional primitives), Tier3 (tradition axioms).",
        kanda=1,
    )

    # Tier 1: Mathlib
    mathlib_node = db.add_node(
        conn, root,
        "Tier1: Mathlib theorems (logic, sets, measure, order, graph)",
        node_type="DEFINITION", status="PROVED",
        source_module="mathlib",
        lean_proof="-- ground truth, already proved",
        notes="~12 items. modus_ponens, Set.partition, ProbabilityMeasure, PartialOrder, SimpleGraph.connected.",
        kanda=1,
    )
    db.add_edge(conn, root, mathlib_node, "decomposition")

    # Tier 1: PhysLean
    physlean_node = db.add_node(
        conn, root,
        "Tier1: PhysLean (causal, information, quantum)",
        node_type="DEFINITION", status="PROVED",
        source_module="physlean",
        lean_proof="-- ground truth, already proved",
        notes="~9 items. CausalOrder, ShannonEntropy, VonNeumannEntropy, Entanglement.",
        kanda=1,
    )
    db.add_edge(conn, root, physlean_node, "decomposition")

    # Tier 2: Functional primitives
    tier2_ids = ["CausalPower", "Integration", "Broadcast", "Selectivity", "SelfReference", "Threshold", "Exclusion"]
    primitives_node = db.add_node(
        conn, root,
        "Tier2: Functional primitives (cross-tradition, yes/no definitions)",
        node_type="DEFINITION", status="PROVED",
        source_module="primitives_tier2",
        lean_proof="-- formal definitions with conditions",
        notes="CausalPower, Integration, Broadcast, Selectivity, SelfReference, Threshold, Exclusion.",
        kanda=1,
        primitive_ids=tier2_ids,
    )
    db.add_edge(conn, root, primitives_node, "decomposition")

    # Tier 3: Sanskrit.lean
    sanskrit_node = db.add_node(
        conn, root,
        "Tier3/Sanskrit: Cognition, Svalaksana, Perceives, Kalpana",
        node_type="DEFINITION", status="PROVED",
        source_module="proof_engine_lean/Sanskrit.lean",
        lean_proof="-- axiomatic",
        notes="Dharmakīrti PV III. Tradition-anchored.",
        kanda=1,
        primitive_ids=["Cognition", "Svalaksana", "Perceives", "Kalpana"],
    )
    db.add_edge(conn, root, sanskrit_node, "decomposition")

    # Negative controls
    neg_node = db.add_node(
        conn, root,
        "Negative controls: known non-bridges for testing",
        node_type="DEFINITION", status="PROVED",
        source_module="negative_controls",
        lean_proof="-- test set",
        notes="~8 pairs. If system produces these as bridges, it's broken.",
        kanda=1,
    )
    db.add_edge(conn, root, neg_node, "decomposition")

    conn.commit()
    return {
        "root_id": root,
        "node_ids": {
            "mathlib": mathlib_node,
            "physlean": physlean_node,
            "primitives": primitives_node,
            "sanskrit": sanskrit_node,
            "negative_controls": neg_node,
        },
    }


def run_seed(conn, catalog_only: bool = False) -> dict:
    """
    Full seed. ~60 ground truth entries.
    catalog_only: only populate tables, no graph nodes.
    """
    result = seed_ground_truth(conn)
    prim_count = seed_primitives_tier2(conn)
    result["primitives_count"] = prim_count
    result["claims_count"] = seed_claims(conn).get("claims_count", 0)
    result["negative_controls_count"] = seed_negative_controls(conn)

    if not catalog_only:
        graph = seed_graph_nodes(conn)
        result["graph"] = graph

    return result
