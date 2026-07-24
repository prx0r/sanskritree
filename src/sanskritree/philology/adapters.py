"""Explicit analysis-engine adapters. Unavailable engines report gaps, not parses."""
from __future__ import annotations

import re
from dataclasses import dataclass
from .analysis_lattice import Analysis, whitespace_lattice


KNOWN_ENGINES = ("heritage", "dcs", "vidyut", "process_sanskrit", "ud", "fallback")

_VIDYUT_CACHED: dict = {}


def _init_vidyut() -> dict:
    if _VIDYUT_CACHED:
        return _VIDYUT_CACHED
    try:
        from vidyut.cheda import Chedaka
        from vidyut.kosha import Kosha, PadaEntry
        from vidyut.lipi import transliterate, Scheme
        chedaka = Chedaka("/root/vidyut-0.4.0")
        kosha = Kosha("/root/vidyut-0.4.0/kosha")
        _VIDYUT_CACHED.update(chedaka=chedaka, kosha=kosha, pada_entry=PadaEntry, scheme=Scheme, transliterate=transliterate)
    except Exception as e:
        _VIDYUT_CACHED["error"] = str(e)
    return _VIDYUT_CACHED


def _vidyut_analyze(text: str) -> list[list[Analysis]]:
    """Analyze text with Vidyut. Returns list of analysis lists, one per whitespace token."""
    v = _init_vidyut()
    if "error" in v:
        surfaces = re.findall(r"\S+", text)
        return [[Analysis("vidyut", None, {}, 0.0, {"error": v["error"]})] for _ in surfaces]
    def _make_analysis(tok) -> Analysis:
        features = {}
        detail = {"surface_slp1": tok.text}
        lemma = tok.lemma
        if tok.data is not None:
            detail["raw"] = str(tok.data)
            data_cls = type(tok.data).__name__
            detail["data_class"] = data_cls
            if "Subanta" in data_cls:
                features["vibhakti"] = str(getattr(tok.data, "vibhakti", ""))
                features["vacana"] = str(getattr(tok.data, "vacana", ""))
                features["linga"] = str(getattr(tok.data, "linga", ""))
            elif "Tinanta" in data_cls:
                features["lakara"] = str(getattr(tok.data, "lakara", ""))
                features["purusha"] = str(getattr(tok.data, "purusha", ""))
                features["vacana"] = str(getattr(tok.data, "vacana", ""))
                features["prayoga"] = str(getattr(tok.data, "prayoga", ""))
        if lemma is None:
            try:
                kosha_entries = v["kosha"].get(tok.text)
                if kosha_entries:
                    entry = kosha_entries[0]
                    entry_cls = type(entry).__name__
                    if "Subanta" in entry_cls:
                        lemma = entry.lemma
                        features["vibhakti"] = str(getattr(entry, "vibhakti", ""))
                        features["vacana"] = str(getattr(entry, "vacana", ""))
                        detail["kosha_fallback"] = True
                    elif "Tinanta" in entry_cls:
                        lemma = entry.lemma
                        features["lakara"] = str(getattr(entry, "lakara", ""))
                        features["purusha"] = str(getattr(entry, "purusha", ""))
                        detail["kosha_fallback"] = True
            except Exception:
                pass
        conf = 1.0 if lemma else 0.5
        return Analysis("vidyut", lemma, features, conf, detail)

    # Detect input scheme: Devanāgarī Unicode or IAST
    has_devanagari = any('\u0900' <= c <= '\u097F' for c in text)
    input_scheme = v["scheme"].Devanagari if has_devanagari else v["scheme"].Iast

    surfaces = re.findall(r"\S+", text)
    results = []
    for srf in surfaces:
        try:
            normalized = srf.replace("\u1e41", "\u1e43").replace("'", "").replace("\u2019", "")
            slp1 = v["transliterate"](normalized, input_scheme, v["scheme"].Slp1)
            cheda_tokens = list(v["chedaka"].run(slp1))
        except Exception as e:
            results.append([Analysis("vidyut", None, {}, 0.5, {"error": str(e), "surface": srf})])
            continue
        if not cheda_tokens:
            results.append([Analysis("vidyut", None, {}, 0.5, {"surface": srf})])
            continue
        group = [_make_analysis(t) for t in cheda_tokens]
        results.append(group)
    return results


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

    vidyut_analyses = None
    if "vidyut" in requested:
        vidyut_analyses = _vidyut_analyze(text)

    merged = []
    vi = 0
    for surface, start, end, fallback in base:
        candidates = list(fallback)
        for engine in requested:
            if engine == "vidyut" and vidyut_analyses is not None:
                group = vidyut_analyses[vi] if vi < len(vidyut_analyses) else [Analysis("vidyut", None, {}, 0.5, {"surface": surface})]
                candidates.extend(group)
                vi += 1
            else:
                candidates.append(Analysis(engine, None, {}, None, {"availability": "not_configured", "surface": surface}))
        merged.append((surface, start, end, candidates))
    return merged
