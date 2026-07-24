"""Hard and soft factors for Sanskritree factor graphs."""
from __future__ import annotations
import json
from typing import Any
from .factor_graph import Factor, VariableChoice, FactorGraph


def surface_coverage_factor(source_length: int) -> Factor:
    """Hard constraint: token spans must tile exactly from 0 to source_length."""
    def fn(assignment: dict[str, VariableChoice]) -> float:
        spans = []
        for var_name, choice in assignment.items():
            if var_name.startswith("token_"):
                feat = choice.payload.get("features", {})
                # Features not available at assignment level — we stored occurrence bounds
                # This is checked at graph construction time instead
                pass
        return 0.0
    return Factor(
        name="surface_coverage",
        variable_names=[],
        energy_fn=fn,
        is_hard=True,
    )


def exclusivity_factor() -> Factor:
    """Hard constraint: exactly one hypothesis per token variable."""
    def fn(assignment: dict[str, VariableChoice]) -> float:
        # Beam search naturally enforces one choice per variable
        return 0.0
    return Factor(
        name="exclusivity",
        variable_names=[],
        energy_fn=fn,
        is_hard=False,  # Enforced by search structure, not energy
    )


def agreement_factor() -> Factor:
    """Soft constraint: adjacent tokens should agree in case/number/gender."""
    def fn(assignment: dict[str, VariableChoice]) -> float:
        energy = 0.0
        # Collect tokens in order
        token_vars = [(name, choice) for name, choice in assignment.items()
                      if name.startswith("token_")]
        token_vars.sort(key=lambda x: int(x[0].split("_")[1]))

        for i in range(len(token_vars) - 1):
            _, c1 = token_vars[i]
            _, c2 = token_vars[i + 1]
            f1 = c1.payload.get("features", {})
            f2 = c2.payload.get("features", {})

            # Adjective-noun: same case, number, gender
            v1 = f1.get("vibhakti", "")
            v2 = f2.get("vibhakti", "")
            if v1 and v2 and v1 != v2:
                energy += 1.0

            # Number agreement
            n1 = f1.get("vacana", "")
            n2 = f2.get("vacana", "")
            if n1 and n2 and n1 != n2:
                energy += 0.5

        return energy
    return Factor(
        name="agreement",
        variable_names=[],
        energy_fn=fn,
        weight=0.5,
    )


def compound_factor() -> Factor:
    """Soft constraint: karmadharaya requires same case; tatpurusa stem form."""
    def fn(assignment: dict[str, VariableChoice]) -> float:
        energy = 0.0
        compound = assignment.get("compound")
        if not compound:
            return 0.0
        rel = compound.payload.get("relation", "")
        members = compound.payload.get("member_tokens", [])

        member_analyses = []
        for m_token in members:
            for var_name, choice in assignment.items():
                if var_name == f"token_{m_token}":
                    member_analyses.append(choice)

        if rel == "karmadharaya" and len(member_analyses) >= 2:
            v1 = member_analyses[0].payload.get("features", {}).get("vibhakti", "")
            v2 = member_analyses[1].payload.get("features", {}).get("vibhakti", "")
            if v1 and v2 and v1 != v2:
                energy += 2.0

        if rel == "tatpurusa" and len(member_analyses) >= 1:
            v1 = member_analyses[0].payload.get("features", {}).get("vibhakti", "")
            if v1 and v1 not in ("", "genitive"):
                energy += 1.0

        return energy
    return Factor(
        name="compound",
        variable_names=[],
        energy_fn=fn,
        weight=1.0,
    )


def frame_factor() -> Factor:
    """Soft constraint: DevotionalAct needs praise verb; IdentityClaim needs copula."""
    def fn(assignment: dict[str, VariableChoice]) -> float:
        frame = assignment.get("frame")
        if not frame:
            return 0.0
        frame_type = frame.payload.get("frame_type", "")

        # Collect lemmas from selected token analyses
        lemmas = []
        for var_name, choice in assignment.items():
            if var_name.startswith("token_"):
                lemmas.append(choice.payload.get("lemma", ""))

        if frame_type == "DevotionalAct":
            has_praise = any(l in ("vand", "stu", "bhaj") for l in lemmas)
            if not has_praise:
                return 3.0

        if frame_type == "IdentityClaim":
            has_copula = any(l in ("as", "bhū") for l in lemmas)
            if not has_copula:
                return 2.0

        return 0.0
    return Factor(
        name="frame",
        variable_names=[],
        energy_fn=fn,
        weight=1.5,
    )


def unsupported_addition_factor() -> Factor:
    """Soft constraint: penalize English content without source evidence.

    Higher penalty for spans marked ADDS_FROM_CONTEXT without commentary support.
    """
    def fn(assignment: dict[str, VariableChoice]) -> float:
        alignments_data = assignment.get("_alignments")
        if not alignments_data:
            return 0.0
        payload = alignments_data.payload
        additions = payload.get("additions", [])
        energy = 0.0
        for add in additions:
            if add.get("evidence") == "none":
                energy += 3.0
            elif add.get("evidence") == "commentarial":
                energy += 0.5
            else:
                energy += 2.0
        omissions = payload.get("omissions", [])
        energy += len(omissions) * 1.5
        return energy
    return Factor(
        name="unsupported_addition",
        variable_names=["_alignments"],
        energy_fn=fn,
        weight=2.0,
    )


# ── Action detection compatibility ──
# Maps detected action types → frame type → support score
ACTION_FRAME_COMPAT = {
    "FIX_AWARENESS": {"Instruction": 0.8, "DevotionalAct": 0.1, "IdentityClaim": 0.1},
    "ATTEND_TO": {"Instruction": 0.7, "DevotionalAct": 0.2, "Predication": 0.1},
    "RETAIN_BREATH": {"Instruction": 0.9, "DevotionalAct": 0.0, "IdentityClaim": 0.0},
    "SUSPEND_BREATH": {"Instruction": 0.9, "DevotionalAct": 0.0, "IdentityClaim": 0.0},
    "ENTER_INTERVAL": {"Instruction": 0.8, "IdentityClaim": 0.1, "DevotionalAct": 0.1},
    "VISUALIZE": {"Instruction": 0.7, "DevotionalAct": 0.2, "Predication": 0.1},
    "DISSOLVE": {"Instruction": 0.6, "IdentityClaim": 0.2, "DevotionalAct": 0.1},
    "EXPAND": {"Instruction": 0.6, "IdentityClaim": 0.2, "DevotionalAct": 0.1},
    "CONTEMPLATE_VOID": {"Instruction": 0.7, "IdentityClaim": 0.2, "DevotionalAct": 0.1},
    "LOCATE_ENERGY": {"Instruction": 0.8, "DevotionalAct": 0.1, "Predication": 0.1},
    "WITHDRAW_SENSES": {"Instruction": 0.7, "DevotionalAct": 0.1, "IdentityClaim": 0.1},
    "RECOGNIZE_IDENTITY": {"IdentityClaim": 0.7, "Instruction": 0.2, "DevotionalAct": 0.1},
    "CONTEMPLATE_CONTRADICTION": {"Instruction": 0.7, "IdentityClaim": 0.2, "DevotionalAct": 0.1},
    "FOLLOW_RHYTHM": {"Instruction": 0.7, "DevotionalAct": 0.1, "Predication": 0.1},
    "OBSERVE_END": {"Instruction": 0.7, "DevotionalAct": 0.1, "IdentityClaim": 0.1},
    "REMAIN_IN_STATE": {"Instruction": 0.6, "IdentityClaim": 0.2, "DevotionalAct": 0.1},
}

ACTION_DETECTION_WEIGHT = 0.5


def action_detection_factor() -> Factor:
    """Soft constraint: detected ritual actions support specific frame types.
    
    Reads _detected_actions from the passage to score frame candidates.
    This is additive — other evidence can overrule it.
    """
    def fn(assignment: dict[str, VariableChoice]) -> float:
        actions_data = assignment.get("_actions")
        if not actions_data:
            return 0.0
        actions = actions_data.payload.get("actions", [])
        frame_choice = assignment.get("frame")
        if not frame_choice or not actions:
            return 0.0
        
        frame_type = frame_choice.payload.get("frame_type", "")
        if not frame_type:
            return 0.0
        
        # Compute support from all detected actions
        total_support = 0.0
        for action in actions:
            compat = ACTION_FRAME_COMPAT.get(action, {})
            support = compat.get(frame_type, 0.0)
            total_support += support
        
        # Normalize by number of actions
        if actions:
            total_support /= len(actions)
        
        # Energy contribution = negative support (lower energy = better)
        return -total_support * ACTION_DETECTION_WEIGHT
    
    return Factor(
        name="action_detection",
        variable_names=["frame", "_actions"],
        energy_fn=fn,
        weight=1.0,
    )


def register_graph(g: FactorGraph):
    """Register all standard factors onto a graph."""
    g.add_factor(agreement_factor())
    g.add_factor(compound_factor())
    g.add_factor(frame_factor())
    g.add_factor(unsupported_addition_factor())
    g.add_factor(action_detection_factor())
