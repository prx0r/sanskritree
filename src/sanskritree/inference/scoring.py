"""FactorGraphV2: explicit factor scoring with decomposition and explanation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .factor_graph import Assignment, Factor, FactorGraph, VariableChoice


@dataclass
class FactorContribution:
    """One factor's contribution to a candidate score."""
    factor_name: str
    raw_score: float
    weight_applied: float
    weighted_contribution: float
    is_hard: bool
    explanation: str = ""


@dataclass
class ScoredCandidate:
    """A candidate with decomposed score."""
    assignment: Assignment
    total_score: float
    contributions: list[FactorContribution]
    energy: float


def score_candidate(graph: FactorGraph, assignment: Assignment) -> ScoredCandidate:
    """Score one assignment with full decomposition."""
    contributions = []
    total_weighted = 0.0

    for factor in graph.factors:
        # Collect relevant variable assignments
        relevant = {}
        for vn in factor.variable_names:
            if vn in assignment.choices:
                relevant[vn] = assignment.choices[vn]

        raw = factor.energy_fn(relevant)
        weighted = factor.weight * raw
        total_weighted += weighted

        # Generate explanation
        if factor.is_hard:
            explanation = f"Hard constraint: {factor.name}"
            if raw == float('inf'):
                explanation += " — VIOLATED"
        else:
            explanation = f"Factor: {factor.name} (raw={raw:.3f}, weight={factor.weight})"

        contributions.append(FactorContribution(
            factor_name=factor.name,
            raw_score=raw,
            weight_applied=factor.weight,
            weighted_contribution=weighted,
            is_hard=factor.is_hard,
            explanation=explanation,
        ))

    return ScoredCandidate(
        assignment=assignment,
        total_score=total_weighted,
        contributions=contributions,
        energy=total_weighted,
    )


def decompose_best(graph: FactorGraph, beam_width: int = 30) -> ScoredCandidate:
    """Find best assignment and decompose its score."""
    best = graph.beam_search(beam_width=beam_width)
    return score_candidate(graph, best)


def format_decomposition(scored: ScoredCandidate) -> str:
    """Format score decomposition as readable string."""
    lines = [f"Total score: {scored.total_score:.4f}"]
    for c in scored.contributions:
        if c.is_hard:
            prefix = "  ⛓ HARD"
        elif c.weighted_contribution >= 0:
            prefix = "  +"
        else:
            prefix = "  −"
        lines.append(f"{prefix} {c.weighted_contribution:+.4f}  {c.explanation}")
    return "\n".join(lines)
