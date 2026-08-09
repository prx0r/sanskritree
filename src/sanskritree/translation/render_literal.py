"""Literal renderer: constrained, deterministic English from a semantic plan.
Every output span is licensed by a semantic node or marked as uncertain.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Span:
    start: int
    end: int
    text: str
    semantic_node_ids: list[str] = field(default_factory=list)
    realization_type: str = "literal"  # literal | implicit | uncertain


@dataclass
class LicensedOutput:
    text: str
    spans: list[Span]
    uncertainties: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "spans": [
                {"start": s.start, "end": s.end, "text": s.text,
                 "semantic_node_ids": s.semantic_node_ids,
                 "realization_type": s.realization_type}
                for s in self.spans
            ],
            "uncertainties": self.uncertainties,
        }


LEMMA_ENGLISH = {
    "tad": "that", "Sakti": "power", "cakra": "wheel",
    "viBava": "manifestation", "prabhava": "source",
    "SaMkara": "Sankara", "vand": "I praise", "hfd": "in the heart",
    "nATa": "lord", "anATa": "helpless", "saraRya": "refuge",
    "tvanmaya": "consisting of you", "citta": "mind",
    "BErava": "Bhairava", "ca": "and", "na": "not",
    "api": "also", "eva": "indeed", "aham": "I",
    "nAtha": "lord", "Siva": "Siva",
    "deva": "god", "Atman": "self",
    "nitya": "eternal", "sarvatra": "everywhere",
    "paramam": "supreme", "pada": "state",
    "spand": "vibrates",
}


def literal_render(lemmas: list[str], frame: str | None = None,
                   polarity: str = "positive") -> LicensedOutput:
    """Render a literal English gloss from lemmas.

    Each lemma maps to a fixed gloss. No fluency heuristics.
    Output spans are individually licensed by their lemma.
    """
    spans = []
    words = []
    uncertainties = []
    pos = 0

    for lem in lemmas:
        gloss = LEMMA_ENGLISH.get(lem)
        if gloss is None:
            gloss = f"[{lem}]"
            uncertainties.append(f"Unrecognized lemma: {lem}")

        if words:
            words.append(" ")
            pos += 1

        words.append(gloss)
        span = Span(
            start=pos,
            end=pos + len(gloss),
            text=gloss,
            semantic_node_ids=[f"lemma:{lem}"],
            realization_type="literal",
        )
        spans.append(span)
        pos += len(gloss)

    # Handle negation
    if polarity == "negative":
        words.insert(0, "not ")
        span = Span(start=0, end=4, text="not ",
                    semantic_node_ids=["negation"],
                    realization_type="literal")
        spans.insert(0, span)

    text = "".join(words)

    if frame:
        text = text + f" [{frame}]"

    return LicensedOutput(text=text, spans=spans, uncertainties=uncertainties)


def validate_licence(output: LicensedOutput) -> list[str]:
    """Check that all content spans have semantic licences."""
    errors = []
    for span in output.spans:
        if not span.semantic_node_ids:
            errors.append(f"Span '{span.text}' has no semantic licence")
        if span.realization_type not in ("literal", "implicit", "uncertain"):
            errors.append(f"Span '{span.text}' has unknown type: {span.realization_type}")
    return errors
