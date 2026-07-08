#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sanskrit Proof Engine - main entry point.
Per proofenginge.md + instruction.md.

Usage:
  python run_proof_engine.py              # Phase 1 Nyaya validation
  python run_proof_engine.py --term vyapti # Single term
  python run_proof_engine.py --db proof.db # Custom DB path
"""

import argparse
import io
import sys

# Fix Windows console encoding for Sanskrit/Unicode output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proof_engine.db import init_db, get_node, get_children
from proof_engine.phase1_nyaya import run_phase1, run_ns_1_1_1_full, PHASE1_TERMS


def print_tree(conn, node_id: int, depth: int = 0):
    """Pretty-print decomposition tree."""
    node = get_node(conn, node_id)
    if not node:
        return
    symbols = {
        "PROVED": "+", "PLACEHOLDER": "~", "UNPROVED": "?",
        "OUTSIDE_FORMAL": "E", "HOLLOW": "o", "PARTIAL": "p", "REFUTED": "x"
    }
    sym = symbols.get(node["status"], "?")
    indent = "  " * depth
    stmt = (node["statement"] or "")[:60]
    print(f"{indent}[{node['id']:2d}] {sym} {node['node_type'][:3]} {stmt}...")
    if node.get("lean_type"):
        print(f"{indent}     [L] {node['lean_type'][:55]}...")
    if node.get("sanskrit"):
        print(f"{indent}     [S] {node['sanskrit'][:40]}")
    for child in get_children(conn, node_id):
        print_tree(conn, child["id"], depth + 1)


def main():
    ap = argparse.ArgumentParser(description="Sanskrit Proof Engine")
    ap.add_argument("--db", default="proof_engine.db", help="SQLite DB path")
    ap.add_argument("--term", help="Process single term (e.g. vyāpti)")
    ap.add_argument("--full", action="store_true", help="Run full NS 1.1.1 decomposition")
    args = ap.parse_args()

    conn = init_db(args.db)

    if args.term:
        term = next((t for t in PHASE1_TERMS if t["sanskrit"] == args.term), None)
        if not term:
            print(f"Unknown term: {args.term}. Known: {[t['sanskrit'] for t in PHASE1_TERMS]}")
            sys.exit(1)
        from proof_engine.algorithm import process_claim
        nid = process_claim(conn, term["statement"], sanskrit=term["sanskrit"],
                            devanagari=term.get("devanagari"), provenance=term.get("provenance"),
                            is_sanskrit=True)
        node = get_node(conn, nid)
        print(f"\n[{nid}] {term['sanskrit']} -> {node['status']}")
        print(f"  Lean: {node.get('lean_type', '—')}")
        conn.close()
        return

    if args.full:
        result = run_ns_1_1_1_full(conn)
        root = result["root_id"]
    else:
        result = run_phase1(conn)
        root = result["root_id"]

    sep = "=" * 62
    print("\n" + sep)
    print("  SANSKRIT PROOF ENGINE - Phase 1 Nyaya")
    print(sep)
    print(f"\n  Root [{root}] status: {result.get('root_status', '—')}")
    print(f"  Stats: {result.get('stats', {})}")
    if "term_results" in result:
        print("\n  Term results:")
        for tr in result["term_results"]:
            print(f"    {tr['term']}: node {tr['node_id']} -> {tr['status']}")

    print(f"\n{sep}\n  DECOMPOSITION TREE\n{sep}")
    print_tree(conn, root)
    print("\n  Symbols: + PROVED  ~ PLACEHOLDER  ? UNPROVED  E OUTSIDE_FORMAL  o HOLLOW  p PARTIAL")

    conn.close()
    print("\n  Done. DB:", args.db)


if __name__ == "__main__":
    main()
