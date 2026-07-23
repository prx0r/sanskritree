"""Conservative Sanskrit Library morphology integration boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from ..philology.analysis_lattice import Analysis

@dataclass(frozen=True)
class SanskritLibraryAnalysis:
    lemma: str | None
    gender: str | None
    case: str | None
    number: str | None
    confidence: float | None
    raw: dict
    def as_candidate(self) -> Analysis:
        return Analysis("sanskrit_library", self.lemma, {"gender": self.gender, "case": self.case, "number": self.number}, self.confidence, self.raw)

def analyse(surface_form_slp1: str, transport: Callable[[str], list[dict]] | None = None) -> list[Analysis]:
    """Call only a configured transport; never scrape an undocumented web UI."""
    if not surface_form_slp1.strip():
        raise ValueError("Sanskrit Library analysis requires a non-empty SLP1 surface form")
    if transport is None:
        return [Analysis("sanskrit_library", None, {}, None, {"availability": "transport_not_configured", "input_scheme": "SLP1", "source_url": "https://www.sanskritlibrary.org/morphologicalAnalyzerSHF.html"})]
    return [SanskritLibraryAnalysis(item.get("lemma"), item.get("gender"), item.get("case"), item.get("number"), item.get("confidence"), item).as_candidate() for item in transport(surface_form_slp1)]
