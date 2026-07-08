"""
API clients per proofenginge.md and instruction.md.
LeanSearch, Loogle, Heritage Engine, SanskritShala.
"""

import urllib.request
import urllib.parse
import json
from typing import Optional

# LeanSearch: NL → Lean declaration. May 404 if service down.
LEANSEARCH_URL = "https://leansearch.net/api/search"

# Loogle: type signature → theorem. JSON API.
LOOGLE_JSON_URL = "https://loogle.lean-lang.org/json"

# Heritage Engine: sanskrit.inria.fr — web-based, no direct REST API.
# Heritage.py provides Python interface. Fallback: document URL for manual use.
HERITAGE_BASE = "https://sanskrit.inria.fr"

# SanskritShala: sanskritshala.iitkgp.ac.in
# Alternative: cnerg.iitkgp.ac.in/sanskritshala. Web-based.
SANSKRITSHALA_BASE = "https://sanskritshala.iitkgp.ac.in"


def leansearch(query: str, num_results: int = 10) -> list[dict]:
    """
    Natural language search for Lean declarations.
    Returns: [{id, formal_name, formal_type}, ...]
    """
    try:
        url = f"{LEANSEARCH_URL}?{urllib.parse.urlencode({'query': query, 'num_results': num_results})}"
        with urllib.request.urlopen(url, timeout=15) as req:
            data = json.loads(req.read().decode())
            return data if isinstance(data, list) else data.get("results", [])
    except Exception:
        return []


def loogle(query: str, num_results: int = 20) -> list[dict]:
    """
    Type signature / pattern search. Loogle syntax: ?a for metavars, |- for conclusion.
    Returns: [{name, type, module, doc}, ...]
    """
    try:
        url = f"{LOOGLE_JSON_URL}?{urllib.parse.urlencode({'q': query})}"
        with urllib.request.urlopen(url, timeout=15) as req:
            data = json.loads(req.read().decode())
            hits = data.get("hits", [])
            return hits[:num_results]
    except Exception:
        return []


def library_check(conn, statement: str, lean_type: Optional[str], *, external: bool = True) -> Optional[dict]:
    """
    STEP 1 — LIBRARY CHECK.
    Query LeanSearch (NL) and Loogle (type). If match found in DB or external, return reuse info.
    external=False: DB only (fast mode, no network).
    """
    # 1. Check DB for existing proved node with same lean_type
    if lean_type:
        existing = conn.execute(
            "SELECT id, lean_proof, mathlib_deps FROM nodes WHERE lean_type=? AND status='PROVED' LIMIT 1",
            (lean_type,)
        ).fetchone()
        if existing:
            deps = json.loads(existing[2]) if existing[2] else []
            return {"source": "db", "node_id": existing[0], "proof": existing[1], "deps": deps}

    if not external:
        return None

    # 2. Loogle (type signature → Mathlib theorem) — use first for formal match
    if lean_type:
        lg_results = loogle(_lean_to_loogle(lean_type), num_results=5)
        for r in lg_results:
            ft = r.get("type", "")
            if ft and _type_similar(ft, lean_type):
                return {"source": "loogle", "name": r.get("name"), "proof": r.get("name", ""), "type": ft, "module": r.get("module")}

    # 3. LeanSearch NL
    ls_results = leansearch(statement[:500], num_results=5)
    for r in ls_results:
        ft = r.get("formal_type") or r.get("type", "")
        if ft and lean_type and _type_similar(ft, lean_type):
            return {"source": "leansearch", "formal_name": r.get("formal_name"), "proof": r.get("formal_name", ""), "formal_type": ft}

    return None


def _type_similar(a: str, b: str) -> bool:
    """Heuristic: same structure (forall, implies)."""
    a_norm = a.replace(" ", "").replace("→", "->").replace("∀", "forall")
    b_norm = b.replace(" ", "").replace("→", "->").replace("∀", "forall")
    return a_norm in b_norm or b_norm in a_norm


def _lean_to_loogle(lean_type: str) -> str:
    """Convert Lean type to Loogle pattern. Loogle uses ?a for metavars."""
    return lean_type.replace("∀", "∀").replace("→", "→")
