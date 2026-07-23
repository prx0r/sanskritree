"""Explicit analysis-engine adapters. Unavailable engines report gaps, not parses."""
from __future__ import annotations

from dataclasses import dataclass
from .analysis_lattice import Analysis, whitespace_lattice


KNOWN_ENGINES = ("heritage", "dcs", "vidyut", "process_sanskrit", "ud", "fallback")


def analyze(text: str, engines: list[str]) -> list[tuple[str, int, int, list[Analysis]]]:
    """Merge candidates by token position while retaining each engine's provenance.

    Production adapters will replace the unavailable records once their data or
    executable has been installed and source-audited. This never fabricates a
    morphology result merely because an engine was requested.
    """
    unknown = set(engines) - set(KNOWN_ENGINES)
    if unknown:
        raise ValueError(f"unknown analysis engines: {', '.join(sorted(unknown))}")
    base = whitespace_lattice(text)
    requested = [engine for engine in engines if engine != "fallback"]
    if not requested:
        return base
    merged = []
    for surface, start, end, fallback in base:
        candidates = list(fallback)
        for engine in requested:
            candidates.append(Analysis(engine, None, {}, None, {"availability": "not_configured", "surface": surface}))
        merged.append((surface, start, end, candidates))
    return merged
