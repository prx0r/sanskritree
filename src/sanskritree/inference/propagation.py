"""Stable synchronous belief propagation over a factor graph assignment."""
from __future__ import annotations
from math import exp
from collections import defaultdict
from typing import Iterable
from collections.abc import Iterable
from .factor_graph import Assignment, FactorGraph


def sigmoid(x: float) -> float:
    if x < -20:
        return 0.0
    if x > 20:
        return 1.0
    return 1.0 / (1.0 + exp(-x))


def propagate(
    nodes: Iterable[str],
    edges: Iterable[Edge],
    priors: dict[str, float],
    *,
    max_iter: int = 50,
    tolerance: float = 1e-6,
    damping: float = 0.35,
    clamp: float = 8.0,
) -> dict[str, float]:
    """Simple propagation over an edge list (for testing)."""
    from .factor_graph import Assignment as _A
    from .factor_graph import FactorGraph as _FG
    g = _FG("test")
    g.add_variable("_all", [type("VC", (), {"hypothesis_id": n, "payload": {}, "prior_logit": priors.get(n, 0.0)})() for n in nodes])
    a = _A()
    for n in nodes:
        for c in g.variables["_all"]:
            if c.hypothesis_id == n:
                a.choices[n] = c
                break
    for e in edges:
        g.add_factor(type("F", (), {
            "name": f"edge_{e.source}_{e.target}",
            "variable_names": ["_all"],
            "energy_fn": lambda _: 0.0,
            "is_hard": False,
            "weight": 1.0,
        })())
    return compute_beliefs(g, a, max_iter=max_iter, tolerance=tolerance, damping=damping, clamp=clamp)


def compute_beliefs(
    graph: FactorGraph,
    assignment: Assignment,
    *,
    max_iter: int = 50,
    tolerance: float = 1e-6,
    damping: float = 0.35,
    clamp: float = 8.0,
) -> dict[str, float]:
    """Compute propagated beliefs from priors + factor consistency.

    Uses damped synchronous logit updates. Returns belief per hypothesis ID.
    """
    # Gather all hypotheses involved
    all_hypotheses = {}
    for var_name, choices in graph.variables.items():
        for choice in choices:
            all_hypotheses[choice.hypothesis_id] = choice

    # Initial logits from priors
    logits = {}
    for hid, choice in all_hypotheses.items():
        logits[hid] = choice.prior_logit

    # Build edge structure: which hypotheses co-occur in variables
    var_hyp_map = {}  # var_name → list of hypothesis_ids
    for var_name, choices in graph.variables.items():
        var_hyp_map[var_name] = [c.hypothesis_id for c in choices]

    for iteration in range(max_iter):
        # Compute messages: support from factor consistency
        incoming = defaultdict(float)

        for factor in graph.factors:
            var_names = [vn for vn in factor.variable_names
                         if vn in assignment.choices]
            if not var_names:
                continue

            # Energy of this factor given current assignment
            relevant = {vn: assignment.choices[vn] for vn in var_names}
            energy = factor.energy(relevant)

            # Each variable in this factor gets a consistency signal
            # Lower energy → positive signal
            consistency_signal = -energy * factor.weight
            for vn in var_names:
                if vn in assignment.choices:
                    hid = assignment.choices[vn].hypothesis_id
                    incoming[hid] += consistency_signal

        # Per-variable competition: selected hypothesis vs alternatives
        for var_name, hyp_ids in var_hyp_map.items():
            selected = assignment.choices.get(var_name)
            if selected:
                # Boost selected, suppress alternatives
                incoming[selected.hypothesis_id] += 0.5
                for hid in hyp_ids:
                    if hid != selected.hypothesis_id:
                        incoming[hid] -= 0.3

        # Synchronous update with damping + clamping
        proposed = {}
        for hid in all_hypotheses:
            raw = all_hypotheses[hid].prior_logit + incoming.get(hid, 0.0)
            proposed[hid] = max(-clamp, min(clamp, raw))

        updated = {}
        max_delta = 0.0
        for hid in all_hypotheses:
            val = (1.0 - damping) * logits.get(hid, 0.0) + damping * proposed.get(hid, 0.0)
            updated[hid] = val
            delta = abs(val - logits.get(hid, 0.0))
            if delta > max_delta:
                max_delta = delta

        logits = updated

        if max_delta < tolerance:
            break

    return {hid: sigmoid(logits.get(hid, 0.0)) for hid in all_hypotheses}


def propagate_and_score(
    graph: FactorGraph,
    beam_width: int = 50,
) -> tuple[Assignment, dict[str, float], float]:
    """Run beam search then propagate beliefs. Returns best assignment, beliefs, energy."""
    best = graph.beam_search(beam_width=beam_width)
    beliefs = compute_beliefs(graph, best)
    return best, beliefs, best.energy
