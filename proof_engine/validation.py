"""
Validation set per Schema v3 §5.
PRECONDITION: validation_set_pass_rate = 1.0 ∨ DEV_MODE before production.
"""

from . import db
from . import fol_lean_bridge

# Canonical NNExpr → Lean type pairs for Dharmakīrti + Nyāya
VALIDATION_PAIRS = [
    {"sanskrit": "pratyakṣa", "tradition": "dharmakirti", "expected": "∀ (c : Cognition) (x : Svalaksana), Perceives c x → ¬ Kalpana c"},
    {"sanskrit": "vyāpti", "tradition": "nyaya", "expected": "∀ (α : Type*) (Hetu Sadhya : α → Prop), (∀ x, Hetu x → Sadhya x)"},
    {"sanskrit": "pramāṇa", "tradition": "nyaya", "expected": "∀ (source : Type) (belief : Prop), ValidCognition source belief → belief"},
]


def run_validation(conn) -> dict:
    """Run validation set. Return {passed, total, failed}."""
    passed = 0
    total = len(VALIDATION_PAIRS)
    failed = []
    for p in VALIDATION_PAIRS:
        trad = p["tradition"]
        sk = p["sanskrit"]
        expected = p["expected"]
        if trad == "dharmakirti":
            actual = fol_lean_bridge.DHARMAKIRTI_LEAN_TYPES.get(sk.strip().lower())
        else:
            actual = fol_lean_bridge.NYAYA_LEAN_TYPES.get(sk.strip().lower())
        if actual and _normalize(actual) == _normalize(expected):
            passed += 1
        else:
            failed.append({"sanskrit": sk, "tradition": trad, "expected": expected[:60], "actual": (actual or "")[:60]})
    return {"passed": passed, "total": total, "failed": failed, "pass_rate": passed / total if total else 1.0}


def _normalize(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in "→∀() ").replace(" ", "")


def validation_ok(conn, dev_mode: bool = False) -> bool:
    """True if pass_rate >= 1.0 or DEV_MODE."""
    if dev_mode:
        return True
    r = run_validation(conn)
    return r["pass_rate"] >= 1.0
