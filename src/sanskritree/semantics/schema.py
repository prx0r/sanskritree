from __future__ import annotations
from dataclasses import asdict, dataclass, field

ENTITY_CLASSES = {"Agent", "Consciousness", "Power", "State", "Process", "Deity", "Mantra", "Phoneme", "Body", "Faculty", "Level", "Place", "RitualAction", "Practice", "Substance", "Property", "Result", "TextualObject"}
RELATIONS = {"IDENTITY", "QUALIFICATION", "POSSESSION", "MANIFESTATION", "DEPENDENCE", "CAUSATION", "SEQUENCE", "TRANSFORMATION", "LOCATION", "PART_WHOLE", "CORRESPONDENCE", "INHERENCE", "PRESCRIPTION", "PROHIBITION", "ELIGIBILITY", "RESULT", "KNOWLEDGE", "PERCEPTION", "RECOGNITION"}
MODES = {"assertion", "definition", "injunction", "prohibition", "praise", "metaphor", "etymology", "ritual_identification", "visualisation", "narrative", "commentarial_interpretation"}
EXPLICITNESS = {"grammatically_explicit", "immediate_context", "same_text_supported", "same_corpus_supported", "commentarial", "translator_inference", "speculative"}


@dataclass(frozen=True)
class Entity:
    label: str
    class_name: str
    def __post_init__(self):
        if self.class_name not in ENTITY_CLASSES:
            raise ValueError(f"unsupported entity class: {self.class_name}")


@dataclass(frozen=True)
class SemanticFrame:
    frame_id: str
    source_passage_id: str
    source_span: str
    discourse_mode: str
    subject: Entity
    relation: str
    object: Entity
    explicitness: str
    confidence: float
    alternatives: list[dict] = field(default_factory=list)
    def __post_init__(self):
        if self.discourse_mode not in MODES or self.relation not in RELATIONS or self.explicitness not in EXPLICITNESS:
            raise ValueError("semantic frame contains an unregistered mode, relation, or explicitness value")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
    def asdict(self) -> dict:
        return asdict(self)
