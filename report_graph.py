#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report the knowledge tree: nodes, claims, decompositions, relations, failures.
Prints to stdout and optionally exports JSON for the frontend graph.
Usage: python report_graph.py [--db PATH] [--json PATH] [--no-seed]
"""
import argparse
import io
import json
import sqlite3
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proof_engine.db import (
    init_db, get_node, get_children,
    get_all_claims, get_decompositions, get_primitives,
)
from proof_engine import ground_truth


def print_node_tree(conn, nid: int, depth: int = 0) -> None:
    """Print hierarchical node tree (ground truth structure)."""
    node = get_node(conn, nid)
    if not node:
        return
    sym = {"PROVED": "+", "UNPROVED": "?"}.get(node.get("status", ""), "?")
    indent = "  " * depth
    stmt = (node.get("statement") or "")[:55]
    src = node.get("source_module") or ""
    print(f"{indent}[{node['id']}] {sym} {stmt}... ({src})")
    for c in get_children(conn, nid):
        print_node_tree(conn, c["id"], depth + 1)


def print_claims_tree(conn) -> None:
    """Print claims with decompositions as children."""
    claims = get_all_claims(conn)
    if not claims:
        print("  (no claims)")
        return
    for c in claims:
        status = c.get("status", "PENDING")
        lt = (c.get("lean_type") or "")[:50]
        print(f"\n  [{c['id']}] {status} | {c.get('tradition', '')}")
        print(f"      {c.get('statement', '')[:70]}...")
        if lt:
            print(f"      lean: {lt[:55]}...")
        decs = get_decompositions(conn, c["id"])
        for d in decs:
            maps = "ok" if d.get("maps_cleanly") else "CANDIDATE"
            prim = d.get("primitive_id") or "?"
            print(f"        - {d.get('component_text', '')[:45]}... -> {prim} ({maps})")


def print_relations(conn) -> None:
    """Print claim_relations (bridge probe results)."""
    rows = conn.execute(
        "SELECT source_id, target_id, relation_type, bridge_axioms FROM claim_relations"
    ).fetchall()
    if not rows:
        print("  (no relations yet)")
        return
    for r in rows:
        print(f"  {r[0]} --{r[2]}-> {r[1]}")


def print_failures(conn) -> None:
    """Print failure_log entries."""
    rows = conn.execute(
        "SELECT claim_id, failure_type, context, lean_output FROM failure_log ORDER BY id DESC LIMIT 20"
    ).fetchall()
    if not rows:
        print("  (none)")
        return
    for r in rows:
        ctx = (r[2] or "")[:50]
        print(f"  {r[0]} | {r[1]} | {ctx}...")


def print_primitive_candidates(conn) -> None:
    """Print primitive_candidates."""
    rows = conn.execute(
        "SELECT candidate_id, definition, source_claim_id FROM primitive_candidates"
    ).fetchall()
    if not rows:
        print("  (none)")
        return
    for r in rows:
        print(f"  {r[0]}: {r[1][:50]}... (from {r[2]})")


def export_for_frontend(conn, out_path: Path) -> None:
    """Export nodes + claims + relations to JSON for frontend graph."""
    nodes = []
    edges = []
    bridges = []
    node_id = 1

    # 1. Nodes from nodes table (ground truth hierarchy)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, parent_id, statement, sanskrit, lean_type, status, source_module FROM nodes"
    ).fetchall()
    for r in rows:
        d = dict(r)
        d["tradition"] = d.get("source_module", "")
        d["x"] = (len(nodes) % 10) * 120
        d["y"] = (len(nodes) // 10) * 200
        nodes.append(d)
        if d.get("parent_id"):
            edges.append({"from": d["id"], "to": d["parent_id"]})

    # 2. Claims as nodes (id = 1000 + index)
    claims = get_all_claims(conn)
    claim_to_nid = {}
    for i, c in enumerate(claims):
        nid = 1000 + i
        claim_to_nid[c["id"]] = nid
        nodes.append({
            "id": nid,
            "parent_id": None,
            "statement": c.get("statement", "")[:80],
            "sanskrit": c.get("sanskrit"),
            "lean_type": (c.get("lean_type") or "")[:80],
            "status": c.get("status", "PENDING"),
            "tradition": c.get("tradition", ""),
            "claim_id": c["id"],
            "x": 400 + (i % 8) * 180,
            "y": 600 + (i // 8) * 220,
        })

    # 3. Decomposition edges: claim -> primitive (dummy child nodes for layout)
    dec_count = 0
    for c in claims:
        decs = get_decompositions(conn, c["id"])
        pnid = claim_to_nid.get(c["id"])
        for j, d in enumerate(decs):
            cnid = 2000 + dec_count
            dec_count += 1
            nodes.append({
                "id": cnid,
                "parent_id": pnid,
                "statement": (d.get("component_text", "")[:40] or "?") + " -> " + (d.get("primitive_id") or "candidate"),
                "status": "PROVED" if d.get("maps_cleanly") else "PLACEHOLDER",
                "tradition": c.get("tradition", ""),
                "x": 0, "y": 0,
            })
            edges.append({"from": cnid, "to": pnid})

    # 4. claim_relations as bridges
    rels = conn.execute("SELECT source_id, target_id, relation_type FROM claim_relations").fetchall()
    for r in rels:
        a, b = claim_to_nid.get(r[0]), claim_to_nid.get(r[1])
        if a and b:
            bridges.append({"node_a": a, "node_b": b, "relation_type": r[2]})

    # Fallback: if no nodes from DB, add root
    if not nodes:
        nodes = [{"id": 1, "parent_id": None, "statement": "Empty graph", "status": "HOLLOW", "x": 4800, "y": 4800}]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"nodes": nodes, "edges": edges, "bridges": bridges}, indent=2), encoding="utf-8")
    print(f"\nExported to {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Report knowledge tree and graph")
    ap.add_argument("--db", default="proof_engine.db", help="Database path")
    ap.add_argument("--json", metavar="PATH", help="Export JSON for frontend to PATH")
    ap.add_argument("--no-seed", action="store_true", help="Skip seeding (use existing DB only)")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = Path(__file__).resolve().parent / args.db
    conn = init_db(str(db_path))

    result = ground_truth.run_seed(conn, catalog_only=False) if not args.no_seed else {}

    print("=" * 60)
    print("KNOWLEDGE TREE")
    print("=" * 60)
    if "graph" in result:
        g = result["graph"]
        print("\n[Ground truth nodes]")
        print_node_tree(conn, g["root_id"])
    else:
        # Try to find root
        r = conn.execute("SELECT id FROM nodes WHERE parent_id IS NULL LIMIT 1").fetchone()
        if r:
            print("\n[Ground truth nodes]")
            print_node_tree(conn, r[0])

    print("\n" + "-" * 60)
    print("[Claims + decompositions]")
    print_claims_tree(conn)

    print("\n" + "-" * 60)
    print("[Claim relations (bridge probe)]")
    print_relations(conn)

    print("\n" + "-" * 60)
    print("[Failure log (last 20)]")
    print_failures(conn)

    print("\n" + "-" * 60)
    print("[Primitive candidates]")
    print_primitive_candidates(conn)

    if args.json:
        out = Path(args.json)
        export_for_frontend(conn, out)

    conn.close()
    print("\n" + "=" * 60)


def _safe_print(s: str) -> None:
    """Print with ASCII fallback for Windows console."""
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    # Use UTF-8 for stdout on Windows
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
