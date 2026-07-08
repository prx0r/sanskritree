#!/usr/bin/env python3
"""Run validation set. PRECONDITION for production."""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from proof_engine.db import init_db
from proof_engine import validation

conn = init_db(":memory:")
r = validation.run_validation(conn)
print(f"passed: {r['passed']}/{r['total']}")
print(f"pass_rate: {r['pass_rate']:.2f}")
if r["failed"]:
    for f in r["failed"]:
        print(f"  FAIL: {f['sanskrit']} ({f['tradition']})")
print("OK" if r["pass_rate"] >= 1.0 else "FAIL")
