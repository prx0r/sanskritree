"""Translation audit: structural and semantic checks on translation outputs.
Performs mutation testing, licence validation, and consistency checks.
"""
from __future__ import annotations
import hashlib
from typing import Any

AUDIT_POLES = {
    "REQUIRED_POLARITY_NOT_REALIZED": "Negation required by source but missing in output",
    "FRAME_ROLE_MISMATCH": "Agent/patient roles swapped",
    "UNSUPPORTED_ADDITION": "Content not licensed by any semantic node",
    "UNLABELLED_COMMENTARY_IMPORT": "Commentary-derived content without label",
    "REJECTED_CANDIDATE_LEAKAGE": "Output references a rejected candidate",
    "SOURCE_HASH_MISMATCH": "Source hash doesn't match frozen reference",
    "TERM_POLICY_DRIFT": "Technical term translated differently than established",
    "REQUIRED_NODE_MISSING": "Required semantic node not realized",
}


def audit_mutation(output_text: str, mutation_type: str, source: dict | None = None) -> dict:
    """Run a single mutation audit check."""
    result = {"mutation": mutation_type, "pass": True, "details": ""}

    if mutation_type == "negation":
        # Check if negation is preserved
        if "not" not in output_text.lower() and source and source.get("polarity") == "negative":
            result["pass"] = False
            result["details"] = "Source negative but output lacks 'not'"

    elif mutation_type == "unsupported_addition":
        # Check for doctrinal terms not in source lemmas
        doctrinal_terms = ["Siva", "Sakti", "Brahman", "Atman", "consciousness",
                          "universal", "absolute", "transcendental"]
        if source and source.get("lemmas"):
            for term in doctrinal_terms:
                if term.lower() in output_text.lower():
                    # Check if licensed by a lemma
                    licensed = any(term.lower() in l.lower() for l in source["lemmas"])
                    if not licensed:
                        result["pass"] = False
                        result["details"] = f"Unlicensed doctrinal term: {term}"
                        break

    elif mutation_type == "source_hash":
        expected = (source or {}).get("expected_hash", "")
        actual = (source or {}).get("actual_hash", "")
        if expected and actual and expected != actual:
            result["pass"] = False
            result["details"] = f"Hash mismatch: expected {expected[:16]}..., got {actual[:16]}..."

    return result


def run_audit_suite(output_text: str, source_info: dict) -> list[dict]:
    """Run all mutation audits."""
    results = []
    for mutation in ["negation", "unsupported_addition", "source_hash"]:
        result = audit_mutation(output_text, mutation, source_info)
        results.append(result)
    return results
