#!/usr/bin/env python3
"""
Simulation: What would the proof engine produce on Shiva Sūtras?
Runs actual algorithm on representative claims. No LLM by default (shows baseline).
"""
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proof_engine.db import init_db, get_node, get_children
from proof_engine import algorithm

# Shiva Sūtras (Vasugupta, ~9th c.) — first 6 + a few more. IAST + English.
# Source: standard translations (Singh, Lakshman Joo)
SHIVA_SUTRAS = [
    {
        "sanskrit": "caitanyam ātmā",
        "statement": "Consciousness (caitanya) is the self (ātman)",
        "ref": "1.1",
    },
    {
        "sanskrit": "jñānam bandhaḥ",
        "statement": "Knowledge (jñāna) is bondage",
        "ref": "1.2",
    },
    {
        "sanskrit": "yonivargaḥ kalāśarīram",
        "statement": "The yoni divisions are the body of time (kalā)",
        "ref": "1.3",
    },
    {
        "sanskrit": "mātṛkāśaktisaṃpuṭāt",
        "statement": "The mātṛkās (phonemic powers) are the seat of knowledge",
        "ref": "1.4",
    },
    {
        "sanskrit": "udyamo bhairavaḥ",
        "statement": "Endeavour (udyama) is Bhairava",
        "ref": "1.5",
    },
    {
        "sanskrit": "śaktisandhāne viśvasaṃhāraḥ",
        "statement": "In the union of the circle of Śaktis is the dissolution of the universe",
        "ref": "1.6",
    },
    {
        "sanskrit": "jñānaṃ jāgrat",
        "statement": "Knowledge in the waking state",
        "ref": "2.1",
    },
    {
        "sanskrit": "svapnaḥ saṃkalpaḥ",
        "statement": "Dream is conceptual construction",
        "ref": "2.2",
    },
    {
        "sanskrit": "vikalpaḥ māyā",
        "statement": "Conceptual diversity is māyā",
        "ref": "2.3",
    },
]


def run_simulation(use_llm: bool = False, fast_mode: bool = True):
    conn = init_db(":memory:")
    provenance = {"tradition": "shaiva", "text": "shiva_sutra", "period": "~9th c. CE", "author": "Vasugupta"}

    root = conn.execute(
        "INSERT INTO nodes (parent_id, statement, sanskrit, provenance, node_type, status, created_at) "
        "VALUES (?,?,?,?,?,?,datetime('now'))",
        (None, "Shiva Sūtras — Kashmir Shaivism foundation", "caitanyam ātmā ...", 
         '{"tradition":"shaiva","text":"shiva_sutra"}', "FORMAL", "UNPROVED")
    ).fetchall()
    conn.commit()
    root_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    llm_fn = None
    if use_llm:
        try:
            from proof_engine import llm_client
            def _llm(c, s, p):
                return llm_client.process_claim(c, s, p or provenance)
            llm_fn = _llm
        except Exception as e:
            print(f"  [LLM unavailable: {e}]")

    results = []
    for s in SHIVA_SUTRAS:
        prov = {**provenance, "ref": s["ref"]}
        nid = algorithm.process_claim(
            conn, s["statement"],
            parent_id=root_id,
            sanskrit=s["sanskrit"],
            provenance=prov,
            is_sanskrit=True,
            llm_fn=llm_fn,
            max_depth=5,
            fast_mode=fast_mode,
            dev_mode=True,
        )
        conn.execute("INSERT OR IGNORE INTO edges (parent_id, child_id, edge_type) VALUES (?,?,?)",
                     (root_id, nid, "decomposition"))
        conn.commit()
        node = get_node(conn, nid)
        results.append({
            "ref": s["ref"],
            "sanskrit": s["sanskrit"][:40],
            "status": node["status"],
            "node_type": node["node_type"],
            "lean_type": (node.get("lean_type") or "")[:60],
            "notes": (node.get("notes") or "")[:50],
        })

    root_status = algorithm.propagate(conn, root_id)
    conn.execute("UPDATE nodes SET status=? WHERE id=?", (root_status, root_id))
    conn.commit()

    return {"root_id": root_id, "root_status": root_status, "results": results, "conn": conn}


def print_tree(conn, nid: int, depth: int = 0):
    node = get_node(conn, nid)
    if not node:
        return
    sym = {"PROVED": "+", "UNPROVED": "?", "OUTSIDE_FORMAL": "E", "HOLLOW": "o", "PARTIAL": "p", "REFUTED": "x"}.get(node["status"], "?")
    indent = "  " * depth
    stmt = (node["statement"] or "")[:55]
    print(f"{indent}[{node['id']}] {sym} {node['node_type'][:3]} {stmt}...")
    if node.get("lean_type"):
        print(f"{indent}    Lean: {node['lean_type'][:50]}...")
    if node.get("notes"):
        print(f"{indent}    Note: {node['notes'][:45]}...")
    for c in get_children(conn, nid):
        print_tree(conn, c["id"], depth + 1)


# If we had done the scholarly work: Shiva terms as axioms (like Dharmakīrti definitions)
# These are STIPULATED — we're not claiming they're proved, just formalizable
SHIVA_LEAN_TYPES = {
    "caitanyam": "Consciousness : Type",  # cit/caitanya as type
    "jñānam": "Knowledge : Type",
    "bandhaḥ": "Bondage : Type",
    "saṃkalpaḥ": "ConceptualConstruction : Type",  # saṃkalpa ≈ kalpanā
    "vikalpaḥ": "ConceptualDiversity : Type",
    "māyā": "Illusion : Type",
}


def run_with_formalization():
    """Simulate: we added Shiva terms to fol_lean_bridge. What then?"""
    from proof_engine.db import init_db, get_node, get_children
    from proof_engine import algorithm

    conn = init_db(":memory:")
    provenance = {"tradition": "shaiva", "text": "shiva_sutra", "period": "~9th c. CE"}

    def formalize_shaiva(claim, sanskrit, prov):
        if not sanskrit:
            return None
        # Try first word (sūtras often put key term first)
        first = sanskrit.split()[0].strip().lower() if sanskrit else ""
        return SHIVA_LEAN_TYPES.get(first)

    root_id = conn.execute(
        "INSERT INTO nodes (parent_id, statement, sanskrit, provenance, node_type, status, created_at) "
        "VALUES (?,?,?,?,?,?,datetime('now'))",
        (None, "Shiva Sūtras (with formalization)", "caitanyam ātmā ...",
         '{"tradition":"shaiva"}', "FORMAL", "UNPROVED")
    )
    conn.commit()
    root_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    results = []
    for s in SHIVA_SUTRAS[:6]:  # First 6 only
        prov = {**provenance, "ref": s["ref"]}
        nid = algorithm.process_claim(
            conn, s["statement"],
            parent_id=root_id,
            sanskrit=s["sanskrit"],
            provenance=prov,
            is_sanskrit=True,
            formalize_fn=formalize_shaiva,
            max_depth=5,
            fast_mode=True,
            dev_mode=True,
        )
        conn.execute("INSERT OR IGNORE INTO edges (parent_id, child_id, edge_type) VALUES (?,?,?)",
                     (root_id, nid, "decomposition"))
        conn.commit()
        node = get_node(conn, nid)
        results.append({"ref": s["ref"], "sanskrit": s["sanskrit"][:35], "status": node["status"],
                        "lean_type": (node.get("lean_type") or "(none)")[:50]})
    return results


def main():
    print("=" * 70)
    print("  SHIVA SŪTRAS SIMULATION — What would the proof engine produce?")
    print("=" * 70)

    # SCENARIO 1: Baseline (no LLM, no Shiva terms)
    print("\n  SCENARIO 1: Baseline — no formalization for unknown terms")
    print("  (Current system has only Nyāya + Dharmakīrti term mappings)\n")
    r = run_simulation(use_llm=False, fast_mode=True)
    print("  ROOT STATUS:", r["root_status"])
    for x in r["results"][:4]:
        print(f"    {x['ref']}: {x['status']} | Lean: {x['lean_type'] or '(none)'}")
    print("    ...")
    rows = r["conn"].execute("SELECT status, COUNT(*) FROM nodes GROUP BY status").fetchall()
    print("  →", dict(rows), "| PROVED:", sum(c for s, c in rows if s == "PROVED"), "/", sum(c for _, c in rows))

    # SCENARIO 2: With pre-mapped Shiva terms (best-case: we did the scholarly work)
    print("\n  SCENARIO 2: With formalization — we added Shiva terms as axiom types")
    print("  (Still no Lean proof — types are novel, Loogle won't match)\n")
    r2 = run_with_formalization()
    for x in r2:
        print(f"    {x['ref']}: {x['status']} | Lean: {x['lean_type']}")
    print("  → We get lean_type for some, but prove step fails → UNPROVED")

    # SCENARIO 3: LLM (if available) — skip by default (90s timeout)
    print("\n  SCENARIO 3: With LLM — run with: python simulate_shiva_sutras.py --llm")
    if "--llm" in sys.argv:
        try:
            r3 = run_simulation(use_llm=True, fast_mode=True)
            print("  ROOT STATUS:", r3["root_status"])
            for x in r3["results"][:4]:
                print(f"    {x['ref']}: {x['status']} | Lean: {x['lean_type'] or '(none)'[:45]}")
            rows3 = r3["conn"].execute("SELECT status, COUNT(*) FROM nodes GROUP BY status").fetchall()
            print("  →", dict(rows3))
        except Exception as e:
            print("  [LLM failed:", e, "]")

    print("\n" + "=" * 70)
    print("  VERDICT: Shiva Sūtras are definitional/metaphysical. Without")
    print("  (a) pre-built axiom layer (cit, māyā, śakti...) and")
    print("  (b) actual Lean proofs (not just type-check), we get flat UNPROVED.")
    print("  The tree stays shallow; decomposition rarely triggers.")
    print("=" * 70)


if __name__ == "__main__":
    main()
