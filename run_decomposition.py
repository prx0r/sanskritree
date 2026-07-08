#!/usr/bin/env python3
"""
Run the decomposition loop. First on IIT Integration (fully decomposed example), then on all claims.
Usage: python run_decomposition.py [--claim ID] [--all] [--db PATH]
"""
import argparse
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proof_engine.db import init_db, get_claim, get_decompositions
from proof_engine import decomposition
from proof_engine import ground_truth

GROUND_TRUTH = Path(__file__).resolve().parent / "ground_truth"


def main():
    ap = argparse.ArgumentParser(description="Run decomposition loop")
    ap.add_argument("--db", default="proof_engine.db", help="Database path")
    ap.add_argument("--claim", help="Run on single claim ID (default: iit_integration_001)")
    ap.add_argument("--all", action="store_true", help="Run on all claims after first")
    ap.add_argument("--fast", action="store_true", default=True, help="Use fast mode (no Lean subprocess)")
    args = ap.parse_args()

    conn = init_db(args.db)
    ground_truth.run_seed(conn, catalog_only=True)

    claim_id = args.claim or "iit_integration_001"

    # Pre-decomposed components for IIT Integration (worked example)
    pre_decomposed = None
    if claim_id == "iit_integration_001":
        dec_path = GROUND_TRUTH / "iit_integration_decomposed.json"
        if dec_path.exists():
            dec = json.loads(dec_path.read_text(encoding="utf-8"))
            pre_decomposed = dec.get("components", [])

    result = decomposition.decompose_claim(
        conn, claim_id,
        pre_decomposed=pre_decomposed,
        fast=args.fast,
    )

    print(f"Claim: {claim_id}")
    print(f"Result: {result.value}")
    decs = get_decompositions(conn, claim_id)
    print(f"Decompositions: {len(decs)}")
    for d in decs:
        print(f"  - {d.get('component_text', '')[:50]}... -> {d.get('primitive_id') or 'CANDIDATE'} (maps_cleanly={d.get('maps_cleanly')})")
    claim = get_claim(conn, claim_id)
    if claim:
        lt = claim.get('lean_type') or ''
        print(f"Status: {claim.get('status', '?')} | lean_type: {lt[:60] if lt else 'None'}...")

    if args.all and result == decomposition.DecompositionResult.PLACED:
        iit = ground_truth.load_json("iit_claims.json")
        all_claims = [c["id"] for c in iit.get("claims", [])]
        for cid in all_claims:
            full_id = f"iit_{cid}"
            if full_id != claim_id:
                r = decomposition.decompose_claim(conn, full_id, fast=args.fast)
                print(f"  {full_id}: {r.value}")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
