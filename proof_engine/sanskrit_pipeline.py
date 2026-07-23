"""
Sanskrit processing pipeline per proofenginge.md + instruction.md.
Heritage Engine → ByT5-Sanskrit → Navya-Nyāya parse → Lean4 type candidate.
Resources: SanskritShala (pre-Heritage, faster), DCS Sembank, panini-nlp.
"""

import urllib.request
import urllib.parse
import json
from typing import Optional
from . import fol_lean_bridge


def process_sanskrit(raw: str) -> dict:
    """
    Full pipeline for Sanskrit-sourced claims.
    Returns analysis candidates only. Formalisation is deferred to reviewed V2
    Semantic IR; this legacy adapter never emits Lean authority.
    """
    # 1. SanskritShala (faster) or Heritage Engine for sandhi + morphology
    parsed = _sanskritshala_or_heritage(raw)
    if not parsed:
        parsed = {"raw": raw, "words": [raw], "morphology": []}

    # 2. Extract Navya-Nyāya structure (LLM-assisted in full system)
    nn_expr = _extract_nn_structure(parsed)

    return {
        "sanskrit": raw,
        "devanagari": _iast_to_devanagari(raw),
        "parsed": parsed,
        "lean_type_candidate": None,
        "nn_expr": nn_expr,
    }


def _sanskritshala_or_heritage(text: str) -> Optional[dict]:
    """
    SanskritShala: cnerg.iitkgp.ac.in/sanskritshala or sanskritshala.iitkgp.ac.in
    Heritage: sanskrit.inria.fr — no public REST API; use Heritage.py if installed.
    """
    # SanskritShala may have an API — structure unknown. Return None for now.
    # Heritage Engine: Huet's site is web-based. heritage package: pip install from github.
    try:
        import heritage
        # Heritage API if available
        return {"words": [text], "morphology": []}
    except ImportError:
        pass
    return {"words": [text], "morphology": []}


def _extract_nn_structure(parsed: dict) -> Optional[fol_lean_bridge.NNExpr]:
    """Extract abheda, vyāpti, sambandha from parse."""
    # Token count alone is never evidence of identity.
    if "vyāpti" in str(parsed).lower() or "vyapti" in str(parsed).lower():
        return fol_lean_bridge.NNExpr("vyapti", ["Hetu", "Sadhya"])
    return None


def _iast_to_devanagari(iast: str) -> str:
    """Minimal IAST → Devanagari. Full impl would use indic-transliteration or similar."""
    # Placeholder: return IAST for display when no transliteration available
    return iast


# Provenance format per proofenginge
def provenance(tradition: str, text: str, ref: str, period: str = "", author: str = "", register: str = "") -> dict:
    return {
        "tradition": tradition,
        "text": text,
        "ref": ref,
        "period": period,
        "author": author,
        "register": register,
    }
