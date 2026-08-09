"""Semantic plan: structured representation of a verse's meaning.
Captures predicate, roles, polarity, modality, and uncertainties.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticNode:
    node_id: str
    label: str
    node_type: str = "entity"  # entity | predicate | modifier | implicit
    source_hypothesis_id: str | None = None
    commentary: bool = False


@dataclass
class SemanticPlan:
    verse_id: str
    predicate: SemanticNode | None = None
    roles: dict[str, list[str]] = field(default_factory=lambda: {
        "agent": [],
        "patient": [],
        "instrument": [],
        "locus": [],
        "beneficiary": [],
    })
    modifiers: list[str] = field(default_factory=list)
    polarity: str = "positive"  # positive | negative
    modality: str | None = None
    tense_aspect: str | None = None
    technical_terms: list[str] = field(default_factory=list)
    coreference: list[dict] = field(default_factory=list)
    implicit_nodes: list[SemanticNode] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        def node_dict(n: SemanticNode | None):
            if n is None:
                return None
            return {"node_id": n.node_id, "label": n.label, "type": n.node_type, "commentary": n.commentary}

        return {
            "verse_id": self.verse_id,
            "predicate": node_dict(self.predicate),
            "roles": {k: list(v) for k, v in self.roles.items()},
            "modifiers": self.modifiers,
            "polarity": self.polarity,
            "modality": self.modality,
            "tense_aspect": self.tense_aspect,
            "technical_terms": self.technical_terms,
            "coreference": self.coreference,
            "implicit_nodes": [node_dict(n) for n in self.implicit_nodes],
            "unresolved": self.unresolved,
        }


def build_semantic_plan(verse_id: str, lemmas: list[str], source: str) -> SemanticPlan:
    """Build a minimal semantic plan from lemmas and source text.
    Detects negation, identifies potential predicate, classifies technical terms.
    """
    plan = SemanticPlan(verse_id=verse_id)

    # Detect negation
    negation_markers = {"na", "mA", "no", "noc", "nahi", "nA", "na ca", "mā", "ma"}
    for lem in lemmas:
        if lem.lower() in negation_markers:
            plan.polarity = "negative"

    # Detect technical terms
    tech_terms = {"spanda", "Sakti", "Atman", "brahman", "yoga", "tattva",
                  "mantra", "cakra", "bhairava", "Siva", "nirvARa", "mokSa",
                  "dharma", "karma", "pramARa", "jYAna", "prakfti", "purusa",
                  "ISvara", "mAyA", "para", "apara", "nirodha", "samAdhi",
                  "prANa", "kundalinI", "nARa", "bindu", "nAda", "devatA"}
    for lem in lemmas:
        if lem in tech_terms:
            plan.technical_terms.append(lem)

    # Detect common verbs as predicates
    verb_markers = {"vand": "to praise/worship", "stu": "to praise",
                    "kf": "to do/make", "gam": "to go", "as": "to be",
                    "BU": "to become", "dRS": "to see", "zru": "to hear",
                    "jYA": "to know", "i": "to go", "vad": "to speak",
                    "spand": "to vibrate", "muc": "to liberate", "Ap": "to obtain",
                    "prakAS": "to shine", "bhU": "to be/become"}

    for lem in lemmas:
        if lem in verb_markers:
            plan.predicate = SemanticNode(
                node_id=f"pred_{lem}",
                label=lem,
                node_type="predicate",
            )
            break

    # Detect unresolved items
    for lem in lemmas:
        if lem.startswith("__unknown__") or lem == "?":
            plan.unresolved.append(lem)

    return plan
