#!/usr/bin/env python3
"""
Full pipeline: Decomposition Loop -> Bridge Probe -> (Auto-informalization runs inside decomposition).
Run on IIT Integration first, then all claims.
Usage: python run_pipeline.py [--db PATH] [--claim ID] [--all]
"""
import argparse
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proof_engine.db import (
    init_db, get_claim, get_decompositions, get_all_claims,
    get_claims_sharing_primitives,
)
from proof_engine import decomposition
from proof_engine import bridge_probe
from proof_engine import ground_truth

GROUND_TRUTH = Path(__file__).resolve().parent / "ground_truth"


def main():
    ap = argparse.ArgumentParser(description="Run full decomposition + bridge probe pipeline")
    ap.add_argument("--db", default="proof_engine.db", help="Database path")
    ap.add_argument("--claim", help="Run decomposition on single claim only")
    ap.add_argument("--all", action="store_true", help="Run decomposition on all claims, then bridge probe")
    ap.add_argument("--probe-only", action="store_true", help="Skip decomposition, run bridge probe only")
    args = ap.parse_args()

    conn = init_db(args.db)
    ground_truth.run_seed(conn, catalog_only=True)

    # Step 1: Decomposition loop
    if not args.probe_only:
        claim_id = args.claim or "iit_integration_001"
        pre_decomposed = None
        if claim_id == "iit_integration_001":
            dec_path = GROUND_TRUTH / "iit_integration_decomposed.json"
            if dec_path.exists():
                dec = json.loads(dec_path.read_text(encoding="utf-8"))
                pre_decomposed = dec.get("components", [])

        result = decomposition.decompose_claim(
            conn, claim_id,
            pre_decomposed=pre_decomposed,
            fast=True,
        )
        print(f"[Decomposition] {claim_id}: {result.value}")

        if args.all:
            claims = get_all_claims(conn)
            for c in claims:
                cid = c["id"]
                if cid != claim_id:
                    r = decomposition.decompose_claim(conn, cid, fast=True)
                    print(f"  {cid}: {r.value}")

    # Step 2: Bridge probe (only pairs with lean_type)
    pairs = get_claims_sharing_primitives(conn)
    placed = sum(1 for a, b in pairs if a.get("lean_type") and b.get("lean_type"))
    print(f"\n[Bridge Probe] {len(pairs)} pairs share primitives, {placed} have lean_type")
    results = bridge_probe.probe_all_bridges(conn, fast=True)
    print(f"  Relations stored: {len(results)}")
    for r in results[:5]:
        print(f"    {r['a']} --{r['relation_type']}-> {r['b']}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
