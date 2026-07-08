#!/usr/bin/env python3
"""
Run Phase 1 Dharmakīrti validation.
Usage: python run_dharmakirti.py [--full] [--agent] [--db PATH]
  --full: use external LeanSearch/Loogle/lake (slower)
  --agent: Qwen3.5 via Chutes API for sayability, decomposition, formalization (autonomous)
  --db: database path (default: pv_phase1.db)

Set CHUTES_API_TOKEN or use models.md for dev.
"""

import argparse
import sys

# UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    p = argparse.ArgumentParser(description="Run Phase 1 Dharmakīrti")
    p.add_argument("--full", action="store_true", help="Use LeanSearch/Loogle/lake (slower)")
    p.add_argument("--agent", action="store_true", help="Qwen3.5 for autonomous sayability/decompose/formalize")
    p.add_argument("--db", default="pv_phase1.db", help="Database path")
    args = p.parse_args()

    from proof_engine.db import init_db
    from proof_engine import phase1_dharmakirti

    conn = init_db(args.db)
    result = phase1_dharmakirti.run_phase1(conn, fast_mode=not args.full, agent_mode=args.agent)

    print("root_id:", result["root_id"])
    print("root_status:", result["root_status"])
    print("stats:", result["stats"])
    print()
    for tr in result["term_results"]:
        print(f"  {tr['term']}: {tr['status']}")
    print()
    print("OK")


if __name__ == "__main__":
    main()
