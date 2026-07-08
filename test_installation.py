#!/usr/bin/env python3
"""
Comprehensive installation test for Sanskrit Proof Engine.
Runs all checks from proofenginge.md and instruction.md.
"""

import sys
import subprocess
import urllib.request
import json
import os

def ok(msg): print(f"  [OK] {msg}")
def fail(msg): print(f"  [FAIL] {msg}")
def warn(msg): print(f"  [WARN] {msg}")

results = {"ok": 0, "fail": 0, "warn": 0}

def test(name, fn):
    try:
        fn()
        results["ok"] += 1
        return True
    except AssertionError as e:
        fail(f"{name}: {e}")
        results["fail"] += 1
        return False
    except Exception as e:
        fail(f"{name}: {type(e).__name__} {e}")
        results["fail"] += 1
        return False

print("\n" + "=" * 60)
print("  SANSKRIT PROOF ENGINE - Installation Test")
print("=" * 60)

# Python packages
print("\n1. Python packages")
def _req(): assert __import__("requests")
test("requests", _req)
def _anth(): assert __import__("anthropic")
test("anthropic", _anth)
def _her(): assert __import__("heritage")
test("heritage", _her)
def _tf(): assert __import__("transformers")
test("transformers", _tf)
def _torch(): assert __import__("torch")
test("torch", _torch)
def _sql(): assert __import__("sqlite3")
test("sqlite3", _sql)

# Pantograph - note: PyPI pantograph is different from Lean4 PyPantograph
def _pan():
    import pantograph
    # Our proof_engine uses fallback when Pantograph Server not available
    assert pantograph
test("pantograph (pip)", _pan)

# Lean toolchain
print("\n2. Lean toolchain")
path = os.path.expanduser("~/.elan/bin")
path_sep = ";" if sys.platform == "win32" else ":"
env = os.environ.copy()
env["PATH"] = path + path_sep + env.get("PATH", "")

def _elan():
    r = subprocess.run(["elan", "--version"], capture_output=True, text=True, env=env, timeout=10)
    assert r.returncode == 0, r.stderr
test("elan", _elan)

def _lake():
    r = subprocess.run(["lake", "--version"], capture_output=True, text=True, env=env, timeout=30)
    assert r.returncode == 0
test("lake", _lake)

def _lean():
    r = subprocess.run(["lean", "--version"], capture_output=True, text=True, env=env, timeout=30)
    assert r.returncode == 0
test("lean", _lean)

# APIs
print("\n3. External APIs")
def _loogle():
    with urllib.request.urlopen("https://loogle.lean-lang.org/json?q=List", timeout=15) as r:
        d = json.loads(r.read().decode())
        assert "hits" in d or "count" in d
test("Loogle", _loogle)

def _leansearch():
    try:
        with urllib.request.urlopen("https://leansearch.net/api/search?query=List&num_results=3", timeout=15) as r:
            d = json.loads(r.read().decode())
            assert d is not None
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            warn("LeanSearch: HTTP " + str(e.code) + " (may be rate-limited)")
            results["warn"] += 1
            return
        raise
test("LeanSearch", _leansearch)

# Heritage (Sanskrit)
print("\n4. Heritage Engine")
def _heritage():
    from heritage.heritage import HeritagePlatform
    p = HeritagePlatform()
    assert p is not None
test("HeritagePlatform", _heritage)

# Proof engine
print("\n5. Proof engine")
def _proof_engine():
    from proof_engine.db import init_db
    from proof_engine.algorithm import process_claim
    path = os.path.join(os.path.dirname(__file__), "test_install_temp.db")
    try:
        conn = init_db(path)
        nid = process_claim(conn, "Test claim", max_depth=1)
        assert nid > 0
        conn.close()
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except OSError:
                pass
test("proof_engine run", _proof_engine)

# Lean build (if lean_test exists and lakefile has no BOM)
print("\n6. Lean build")
lean_test = os.path.join(os.path.dirname(__file__), "lean_test")
if os.path.isdir(lean_test):
    lf = os.path.join(lean_test, "lakefile.toml")
    if os.path.isfile(lf):
        # Remove BOM if present (Windows PowerShell adds it)
        with open(lf, "rb") as f:
            b = f.read()
        if b.startswith(b"\xef\xbb\xbf"):
            with open(lf, "wb") as f:
                f.write(b[3:])
        def _lean_build():
            r = subprocess.run(["lake", "build"], cwd=lean_test, capture_output=True, text=True, env=env, timeout=120)
            assert r.returncode == 0, r.stderr or r.stdout
        test("lake build", _lean_build)
    else:
        warn("lean_test/lakefile.toml not found")
else:
    warn("lean_test/ not found - run 'lake new lean_test' then 'lake build'")

# Summary
print("\n" + "=" * 60)
print(f"  Results: {results['ok']} OK, {results['fail']} FAIL, {results['warn']} WARN")
print("=" * 60 + "\n")

sys.exit(0 if results["fail"] == 0 else 1)
