"""Factor graph: passage-local inference over typed hypotheses."""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class VariableChoice:
    """One possible assignment for a variable."""
    hypothesis_id: str
    payload: dict[str, Any]
    prior_logit: float = 0.0


@dataclass
class Assignment:
    """A complete or partial assignment of variables."""
    choices: dict[str, VariableChoice] = field(default_factory=dict)
    energy: float = 0.0

    def get(self, var_name: str) -> VariableChoice | None:
        return self.choices.get(var_name)

    def copy(self) -> Assignment:
        return Assignment(choices=dict(self.choices), energy=self.energy)


@dataclass
class Factor:
    """A factor scores compatibility of a subset of variables."""
    name: str
    variable_names: list[str]
    energy_fn: Callable[[dict[str, VariableChoice]], float]
    is_hard: bool = False
    weight: float = 1.0

    def energy(self, assignment: dict[str, VariableChoice]) -> float:
        return self.weight * self.energy_fn(assignment)


class FactorGraph:
    """Passage-local factor graph for one inference run."""

    def __init__(self, passage_id: str):
        self.passage_id = passage_id
        self.variables: dict[str, list[VariableChoice]] = {}
        self.factors: list[Factor] = []

    def add_variable(self, name: str, choices: list[VariableChoice]):
        self.variables[name] = choices
    
    def set_detected_actions(self, actions: list[str]):
        """Set detected ritual actions for action_detection_factor."""
        payload = {"actions": actions}
        self.add_variable("_actions", [VariableChoice("_detected", payload, 0.0)])

    def add_factor(self, factor: Factor):
        self.factors.append(factor)

    def total_energy(self, assignment: Assignment) -> float:
        energy = 0.0
        for factor in self.factors:
            relevant = {}
            for vn in factor.variable_names:
                if vn in assignment.choices:
                    relevant[vn] = assignment.choices[vn]
            if factor.is_hard:
                e = factor.energy_fn(relevant)
                if e == float('inf'):
                    return float('inf')
                energy += e
            else:
                energy += factor.energy(relevant)
        return energy

    def beam_search(self, beam_width: int = 50) -> Assignment:
        """Beam search for minimum-energy assignment."""
        beam = [Assignment()]

        for var_name, choices in self.variables.items():
            candidates = []
            for assignment in beam:
                for choice in choices:
                    new_assignment = assignment.copy()
                    new_assignment.choices[var_name] = choice
                    energy = self.total_energy(new_assignment)
                    if energy == float('inf'):
                        continue
                    new_assignment.energy = energy
                    candidates.append(new_assignment)

            if not candidates:
                continue

            candidates.sort(key=lambda a: a.energy)
            beam = candidates[:beam_width]

        return beam[0] if beam else Assignment()

    def neighborhood(self, conn, passage_reading_id: str, depth: int = 1):
        """Pull hypotheses from DB for this passage reading."""
        # Tokens + hypotheses
        rows = conn.execute("""
            SELECT tocc.occurrence_id, tocc.token_index, tocc.surface,
                   tah.hypothesis_id, tah.analysis_type_id, tah.engine,
                   tah.confidence, tah.status,
                   mat.features_json, lex.lemma_slp1
            FROM token_occurrence tocc
            JOIN token_analysis_hypothesis tah ON tah.occurrence_id = tocc.occurrence_id
            LEFT JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
            LEFT JOIN lexeme lex ON lex.lexeme_id = mat.lexeme_id
            WHERE tocc.passage_reading_id = ?
              AND tah.status = 'proposed'
            ORDER BY tocc.token_index
        """, (passage_reading_id,)).fetchall()

        # Group by token index
        token_groups = {}
        for row in rows:
            idx = row[1]
            if idx not in token_groups:
                token_groups[idx] = []
            token_groups[idx].append(row)

        for idx, group in token_groups.items():
            var_name = f"token_{idx}"
            choices = []
            for row in group:
                occ_id, _, surface, hyp_id, atype_id, engine, conf, status, feat_json, lemma = row
                payload = {
                    "occurrence_id": occ_id,
                    "surface": surface,
                    "analysis_type_id": atype_id,
                    "engine": engine,
                    "lemma": lemma or "",
                    "features": {},
                }
                if feat_json:
                    try:
                        import json
                        payload["features"] = json.loads(feat_json)
                    except Exception:
                        pass
                prior = math.log(max(conf or 0.01, 0.001))
                choices.append(VariableChoice(
                    hypothesis_id=hyp_id,
                    payload=payload,
                    prior_logit=prior,
                ))
            if choices:
                self.add_variable(var_name, choices)

        return self
