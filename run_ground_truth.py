#!/usr/bin/env python3
"""
Seed the graph from ground truth: Mathlib + PhysLean + primitives.
Run: python run_ground_truth.py [--db PATH] [--catalog-only]
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from proof_engine.db import init_db, get_node, get_children
from proof_engine import ground_truth


def print_tree(conn, nid: int, depth: int = 0):
    node = get_node(conn, nid)
    if not node:
        return
    sym = {"PROVED": "+", "UNPROVED": "?"}.get(node["status"], "?")
    indent = "  " * depth
    stmt = (node["statement"] or "")[:60]
    src = node.get("source_module") or ""
    print(f"{indent}[{node['id']}] {sym} {stmt}... ({src})")
    for c in get_children(conn, nid):
        print_tree(conn, c["id"], depth + 1)


def main():
    ap = argparse.ArgumentParser(description="Seed ground truth")
    ap.add_argument("--db", default="proof_engine.db", help="Database path")
    ap.add_argument("--catalog-only", action="store_true", help="Only populate catalogs, no graph nodes")
    args = ap.parse_args()

    conn = init_db(args.db)
    result = ground_truth.run_seed(conn, catalog_only=args.catalog_only)

    print("Ground truth seed complete.")
    print(f"  Ground truth entries: {result['ground_truth_count']}")
    print(f"  Primitives (Tier2): {result['primitives_count']}")
    print(f"  Claims: {result.get('claims_count', 0)}")
    print(f"  Negative controls: {result.get('negative_controls_count', 0)}")

    if "graph" in result:
        g = result["graph"]
        print(f"\n  Root: {g['root_id']}")
        print("  Graph:")
        print_tree(conn, g["root_id"])
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
