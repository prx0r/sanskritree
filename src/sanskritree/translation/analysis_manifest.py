"""Deterministic, auditable analysis manifest for a translation passage.
Records every decision: which candidate was selected, which were rejected,
and the decomposed score components.
"""
from __future__ import annotations
import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class ScoreComponents:
    engine_prior: float = 0.0
    morphological_compatibility: float = 0.0
    agreement: float = 0.0
    frame_compatibility: float = 0.0
    corpus_evidence: float = 0.0
    compound_coherence: float = 0.0

    def total(self) -> float:
        return sum([
            self.engine_prior,
            self.morphological_compatibility,
            self.agreement,
            self.frame_compatibility,
            self.corpus_evidence,
            self.compound_coherence,
        ])


@dataclass
class CandidateEntry:
    candidate_id: str
    rank: int
    score: float
    score_components: ScoreComponents
    hypothesis_id: str
    engine: str
    lemma: str
    analysis_type_id: str | None = None
    features: dict = field(default_factory=dict)
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass
class AnalysisManifest:
    passage_id: str
    run_id: str
    source_hash: str
    source_text: str
    selected_hypotheses: list[str]
    selected_lemma: str
    selected_engine: str
    compound_relation: str | None = None
    frame_type: str | None = None
    alternatives: list[CandidateEntry] = field(default_factory=list)
    uncertainties: list[dict] = field(default_factory=list)
    git_commit: str = ""
    pipeline_version: str = "v0.4"
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "passage_id": self.passage_id,
            "run_id": self.run_id,
            "source_hash": self.source_hash,
            "source_text": self.source_text[:100],
            "selected": {
                "hypothesis_ids": self.selected_hypotheses,
                "lemma": self.selected_lemma,
                "engine": self.selected_engine,
                "compound_relation": self.compound_relation,
                "frame_type": self.frame_type,
            },
            "alternatives": [asdict(a) for a in self.alternatives],
            "uncertainties": self.uncertainties,
            "git_commit": self.git_commit,
            "pipeline_version": self.pipeline_version,
            "created_at": self.created_at or datetime.now(timezone.utc).isoformat(),
        }


def build_manifest(
    conn,
    passage_id: str,
    source_text: str,
    git_commit: str = "",
    pipeline_version: str = "v0.4",
) -> AnalysisManifest:
    """Build an analysis manifest from factor graph output."""
    from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
    from sanskritree.inference.factors import register_graph
    from sanskritree.inference.propagation import propagate_and_score
    from sanskritree.semantics.ritual_frames import detect_action

    import re
    clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', source_text).strip()

    # Get reading_id
    row = conn.execute(
        "SELECT reading_id FROM passage_readings WHERE passage_id=? LIMIT 1",
        (passage_id,),
    ).fetchone()
    if not row:
        return AnalysisManifest(
            passage_id=passage_id,
            run_id=str(uuid.uuid4()),
            source_hash=hashlib.sha256(source_text.encode()).hexdigest(),
            source_text=source_text,
            selected_hypotheses=[],
            selected_lemma="",
            selected_engine="",
            uncertainties=[{"error": "No reading found for passage"}],
        )

    rid = row[0]
    source_hash = hashlib.sha256(clean.encode()).hexdigest()

    actions = detect_action(clean)
    g = FactorGraph(passage_id)
    g.neighborhood(conn, rid)
    if actions:
        g.set_detected_actions(actions)
    g.add_variable("compound", [
        VariableChoice("k", {"relation": "karmadharaya"}, 0.3),
        VariableChoice("t", {"relation": "tatpurusa"}, -0.3),
    ])
    g.add_variable("frame", [
        VariableChoice("d", {"frame_type": "DevotionalAct"}, 0.2),
        VariableChoice("i", {"frame_type": "Instruction"}, 0.2),
        VariableChoice("id", {"frame_type": "IdentityClaim"}, 0.0),
    ])
    register_graph(g)

    best, beliefs, energy = propagate_and_score(g)

    selected_ids = []
    selected_lemma = ""
    selected_engine = ""
    alternatives = []
    uncertainties = []

    for vn, choice in best.choices.items():
        if vn.startswith("token_"):
            hyp_id = choice.hypothesis_id
            lemma = choice.payload.get("lemma", "")
            engine = choice.payload.get("engine", "")
            selected_ids.append(hyp_id)
            if lemma and lemma != "__unknown__":
                selected_lemma = lemma
                selected_engine = engine

            # Collect alternatives for this variable
            if vn in g.variables:
                all_choices = g.variables[vn]
                for rank, alt in enumerate(all_choices):
                    alt_hyp_id = alt.hypothesis_id
                    alt_lemma = alt.payload.get("lemma", "")
                    alt_engine = alt.payload.get("engine", "")
                    if alt_hyp_id == hyp_id:
                        alternatives.append(CandidateEntry(
                            candidate_id=alt_hyp_id,
                            rank=rank,
                            score=alt.prior_logit,
                            score_components=ScoreComponents(engine_prior=alt.prior_logit),
                            hypothesis_id=alt_hyp_id,
                            engine=alt_engine or "?",
                            lemma=alt_lemma or "?",
                            analysis_type_id=alt.payload.get("analysis_type_id"),
                            features=alt.payload.get("features", {}),
                        ))
                        break

        elif vn == "compound":
            compound_rel = choice.payload.get("relation", "")

        elif vn == "frame":
            frame_type = choice.payload.get("frame_type", "")

    manifest = AnalysisManifest(
        passage_id=passage_id,
        run_id=str(uuid.uuid4()),
        source_hash=source_hash,
        source_text=source_text,
        selected_hypotheses=selected_ids,
        selected_lemma=selected_lemma,
        selected_engine=selected_engine,
        compound_relation=locals().get("compound_rel"),
        frame_type=locals().get("frame_type"),
        alternatives=alternatives,
        uncertainties=uncertainties,
        git_commit=git_commit,
        pipeline_version=pipeline_version,
    )

    return manifest
