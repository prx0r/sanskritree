"""
Failure taxonomy. AxiomMath-style: failed proofs as signals.
When the decomposition loop or bridge probe fails, classify and log.
"""

from enum import Enum
from typing import Optional
from . import db


class FailureType(Enum):
    """Failure types from proof attempts. Each implies a different recovery action."""
    COMPILE_ERROR = "compile_error"
    # Type doesn't check — formalization is wrong. Go back, re-decompose the claim.

    UNPROVABLE = "unprovable"
    # Well-typed but no proof exists. Either genuinely independent, or missing axioms.
    # Log what axioms WOULD make it provable.

    TIMEOUT = "timeout"
    # Search space too large. Claim may be too complex, needs sub-lemmas.
    # Split into smaller claims, retry.

    MISSING_PRIMITIVE = "missing_primitive"
    # Proof attempt reveals a needed type that doesn't exist.
    # Candidate new primitive — add to primitive_candidates, retry.


def log_failure(
    conn,
    failure_type: FailureType,
    *,
    claim_id: Optional[str] = None,
    node_id: Optional[int] = None,
    context: Optional[str] = None,
    lean_output: Optional[str] = None,
    primitive_candidate: Optional[str] = None,
) -> int:
    """Log a failure. Returns failure_log id."""
    conn.execute("""
        INSERT INTO failure_log (claim_id, node_id, failure_type, context, lean_output, primitive_candidate, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (claim_id, node_id, failure_type.value, context, lean_output, primitive_candidate))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def add_primitive_candidate(
    conn,
    candidate_id: str,
    definition: str,
    *,
    source_claim_id: Optional[str] = None,
    source_residue: Optional[str] = None,
) -> int:
    """When MISSING_PRIMITIVE: add to primitive_candidates for human review."""
    conn.execute("""
        INSERT OR IGNORE INTO primitive_candidates (candidate_id, definition, source_claim_id, source_residue, status, created_at)
        VALUES (?, ?, ?, ?, 'candidate', datetime('now'))
    """, (candidate_id, definition, source_claim_id, source_residue))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_recovery_action(failure_type: FailureType) -> str:
    """Return the implied recovery action for this failure type."""
    actions = {
        FailureType.COMPILE_ERROR: "Go back to decomposition. Re-formalize the claim.",
        FailureType.UNPROVABLE: "Log what axioms would make it provable. Check for CONTRADICTS.",
        FailureType.TIMEOUT: "Split into smaller claims. Retry with sub-lemmas.",
        FailureType.MISSING_PRIMITIVE: "Add to primitive_candidates. Retry after review.",
    }
    return actions.get(failure_type, "Unknown failure type.")
