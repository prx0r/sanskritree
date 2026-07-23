"""Auditable recovery of legacy-font PDF text streams.

Legacy decoding is a candidate-generation process. A decoder is not accepted
for corpus ingestion until it reproduces independently known controls.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Control:
    raw: str
    expected: str
    label: str

@dataclass(frozen=True)
class DecoderValidation:
    decoder_id: str
    passed: bool
    results: list[dict]

def validate_decoder(decoder_id: str, decoder: Callable[[str], str], controls: list[Control]) -> DecoderValidation:
    results = [{"label": control.label, "raw": control.raw, "expected": control.expected, "actual": decoder(control.raw)} for control in controls]
    return DecoderValidation(decoder_id, all(row["expected"] == row["actual"] for row in results), results)

def decode_candidate(raw: str, decoder_id: str, decoder: Callable[[str], str], validation: DecoderValidation) -> dict:
    return {"raw_glyph_stream": raw, "decoded_candidate": decoder(raw), "decoder_id": decoder_id, "decoder_validation_passed": validation.passed, "review_status": "candidate_only" if validation.passed else "blocked"}
