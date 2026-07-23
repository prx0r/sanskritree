"""Conservative classification of formalized translation commitments."""
from __future__ import annotations


def classify(proposition_a: str, proposition_b: str) -> tuple[str, list[str]]:
    """Only claim equivalence when canonical propositions match exactly.

    Non-identical propositions require actual entailment probes and bridge
    assumptions; they are intentionally reported as underdetermined here.
    """
    norm = lambda value: "".join(value.split())
    if norm(proposition_a) == norm(proposition_b):
        return "equivalent", []
    return "underdetermined", ["No Lean entailment probe has established either direction."]
