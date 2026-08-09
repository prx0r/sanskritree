"""Real candidate Recall@k against adjudicated gold.
For each adjudicated token, finds the rank of the accepted hypothesis
among all available pre-adjudication candidates.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CandidateEquivalence:
    lemma_id: str | None = None
    part_of_speech: str | None = None
    case: str | None = None
    number: str | None = None
    gender: str | None = None
    person: str | None = None
    tense_mood: str | None = None
    voice: str | None = None

    @classmethod
    def from_analysis_features(cls, lemma_id: str, features: dict) -> CandidateEquivalence:
        pos = features.get("heritage_pos") or features.get("pos")
        return cls(
            lemma_id=lemma_id,
            part_of_speech=pos,
            case=features.get("heritage_case") or features.get("vibhakti"),
            number=features.get("heritage_number") or features.get("vacana"),
            gender=features.get("heritage_gender") or features.get("linga"),
            person=features.get("heritage_person") or features.get("purusha"),
            tense_mood=features.get("heritage_tense") or features.get("lakara"),
            voice=features.get("heritage_voice") or features.get("prayoga"),
        )


LEMMA_EQUIVALENCE = {
    "tad": ["tad", "syad", "etad", "idam", "ada"],
    "Sakti": ["Sakti", "Sakti1", "Sakti2"],
    "viBava": ["viBava", "viBava1"],
    "i": ["i", "iN"],
}

def lemma_matches(gold_lemma: str | None, candidate_lemma: str | None) -> bool:
    if not gold_lemma or not candidate_lemma:
        return False
    if gold_lemma == candidate_lemma:
        return True
    gold_norm = gold_lemma.replace("1", "").replace("2", "").replace("3", "")
    cand_norm = candidate_lemma.replace("1", "").replace("2", "").replace("3", "")
    if gold_norm == cand_norm:
        return True
    for base, variants in LEMMA_EQUIVALENCE.items():
        if gold_lemma in variants and candidate_lemma in variants:
            return True
    return False


def features_match(gold: CandidateEquivalence, cand: CandidateEquivalence) -> bool:
    if not lemma_matches(gold.lemma_id, cand.lemma_id):
        return False
    if gold.part_of_speech and cand.part_of_speech and gold.part_of_speech != cand.part_of_speech:
        return False
    return True


def extract_features(analysis_type_id: str, conn) -> dict:
    row = conn.execute(
        "SELECT features_json FROM morph_analysis_type WHERE analysis_type_id = ?",
        (analysis_type_id,),
    ).fetchone()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


@dataclass
class RecallReport:
    n_adjudicated: int = 0
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    engine_miss_rate: float = 0.0
    by_engine: dict[str, dict] = field(default_factory=dict)
    by_work: dict[str, dict] = field(default_factory=dict)
    misses: list[dict] = field(default_factory=list)


def calculate_recall(conn, layer: str = "morphology", min_rank: int = 5) -> RecallReport:
    """Calculate Recall@k for an adjudication layer.

    For each adjudicated decision with status='accepted':
    1. Get the accepted hypothesis
    2. Get the occurrence_id it belongs to
    3. Get all candidate hypotheses for that occurrence (pre-adjudication)
    4. Score candidates by engine confidence (baseline)
    5. Determine rank of the accepted hypothesis
    6. Calculate recall at k=1,3,5

    Only morphology-layer decisions are used by default.
    """
    report = RecallReport()

    accepted = conn.execute(
        """
        SELECT a.decision_id, a.passage_id, a.candidate_hypothesis_id, a.candidate_text,
               h.occurrence_id, h.analysis_type_id, h.engine, h.confidence,
               m.lexeme_id, m.features_json
        FROM adjudication_decisions a
        JOIN token_analysis_hypothesis h ON h.hypothesis_id = a.candidate_hypothesis_id
        LEFT JOIN morph_analysis_type m ON m.analysis_type_id = h.analysis_type_id
        WHERE a.status = 'accepted' AND a.layer = ?
        """,
        (layer,),
    ).fetchall()

    report.n_adjudicated = len(accepted)

    hits = {1: 0, 3: 0, 5: 0}
    engine_counts: dict[str, dict] = defaultdict(lambda: {"n": 0, "hit_1": 0, "hit_3": 0, "hit_5": 0})
    work_counts: dict[str, dict] = defaultdict(lambda: {"n": 0, "hit_1": 0, "hit_3": 0, "hit_5": 0})
    misses_list = []
    engine_miss_count = 0

    for row in accepted:
        decision_id, passage_id, hyp_id, text, occ_id, atype_id, engine, conf, lexeme_id, feat_json = row

        # Get work_id from passage
        work_row = conn.execute(
            "SELECT work_id FROM passages WHERE passage_id = ?", (passage_id,)
        ).fetchone()
        work_id = work_row[0] if work_row else "unknown"

        # Build equivalence key for accepted candidate
        features = {}
        if feat_json:
            try:
                features = json.loads(feat_json)
            except Exception:
                pass
        gold_key = CandidateEquivalence.from_analysis_features(lexeme_id or "", features)

        # Get ALL candidate hypotheses for the same occurrence (pre-adjudication)
        candidates = conn.execute(
            """
            SELECT h.hypothesis_id, h.analysis_type_id, h.engine, h.confidence,
                   m.lexeme_id, m.features_json
            FROM token_analysis_hypothesis h
            LEFT JOIN morph_analysis_type m ON m.analysis_type_id = h.analysis_type_id
            WHERE h.occurrence_id = ?
            ORDER BY h.confidence DESC
            """,
            (occ_id,),
        ).fetchall()

        if not candidates:
            engine_miss_count += 1
            misses_list.append({
                "passage_id": passage_id,
                "occurrence_id": occ_id,
                "accepted_hypothesis": hyp_id,
                "reason": "No candidates available for occurrence",
            })
            continue

        # Rank candidates: find where accepted hypothesis appears
        # Use engine confidence as baseline ranking score
        scored = []
        for c in candidates:
            c_hyp_id, c_atype_id, c_engine, c_conf, c_lexeme_id, c_feat_json = c
            feat_c = {}
            if c_feat_json:
                try:
                    feat_c = json.loads(c_feat_json)
                except Exception:
                    pass
            c_key = CandidateEquivalence.from_analysis_features(c_lexeme_id or "", feat_c)
            score = c_conf if c_conf else 0.01

            # Compute equivalence match
            is_match = features_match(gold_key, c_key)

            scored.append({
                "hypothesis_id": c_hyp_id,
                "analysis_type_id": c_atype_id,
                "engine": c_engine,
                "score": score,
                "is_gold": is_match,
                "lexeme_id": c_lexeme_id,
            })

        # Sort by score descending
        scored.sort(key=lambda x: -x["score"])

        # Find rank of gold
        rank = None
        for i, s in enumerate(scored):
            if s["is_gold"]:
                rank = i + 1
                break

        if rank is None:
            # Gold not found among candidates
            engine_miss_count += 1
            misses_list.append({
                "passage_id": passage_id,
                "occurrence_id": occ_id,
                "accepted_hypothesis": hyp_id,
                "accepted_lemma": text,
                "n_candidates": len(candidates),
                "reason": "Accepted hypothesis not among candidates",
            })
            continue

        if rank == 1:
            hits[1] += 1
            hits[3] += 1
            hits[5] += 1
        elif rank <= 3:
            hits[3] += 1
            hits[5] += 1
        elif rank <= 5:
            hits[5] += 1

        # Track by engine
        for s in scored:
            if s["is_gold"]:
                eng = s["engine"] or "unknown"
                engine_counts[eng]["n"] += 1
                if rank == 1:
                    engine_counts[eng]["hit_1"] += 1
                if rank <= 3:
                    engine_counts[eng]["hit_3"] += 1
                if rank <= 5:
                    engine_counts[eng]["hit_5"] += 1
                break

        # Track by work
        work_counts[work_id]["n"] += 1
        if rank == 1:
            work_counts[work_id]["hit_1"] += 1
        if rank <= 3:
            work_counts[work_id]["hit_3"] += 1
        if rank <= 5:
            work_counts[work_id]["hit_5"] += 1

        if rank > min_rank:
            misses_list.append({
                "passage_id": passage_id,
                "occurrence_id": occ_id,
                "accepted_hypothesis": hyp_id,
                "accepted_lemma": text,
                "rank": rank,
                "n_candidates": len(candidates),
                "engines": list(set(s["engine"] for s in scored)),
            })

    n = max(report.n_adjudicated, 1)
    report.recall_at_1 = hits[1] / n
    report.recall_at_3 = hits[3] / n
    report.recall_at_5 = hits[5] / n
    report.engine_miss_rate = engine_miss_count / n
    report.misses = misses_list[:100]

    report.by_engine = {}
    for eng, counts in engine_counts.items():
        en = max(counts["n"], 1)
        report.by_engine[eng] = {
            "n": counts["n"],
            "recall_at_1": counts["hit_1"] / en,
            "recall_at_3": counts["hit_3"] / en,
            "recall_at_5": counts["hit_5"] / en,
        }

    report.by_work = {}
    for wid, counts in work_counts.items():
        wn = max(counts["n"], 1)
        report.by_work[wid] = {
            "n": counts["n"],
            "recall_at_1": counts["hit_1"] / wn,
            "recall_at_3": counts["hit_3"] / wn,
            "recall_at_5": counts["hit_5"] / wn,
        }

    return report


def report_to_dict(report: RecallReport) -> dict:
    return {
        "n_adjudicated": report.n_adjudicated,
        "recall_at_1": round(report.recall_at_1, 4),
        "recall_at_3": round(report.recall_at_3, 4),
        "recall_at_5": round(report.recall_at_5, 4),
        "engine_miss_rate": round(report.engine_miss_rate, 4),
        "by_engine": report.by_engine,
        "by_work": report.by_work,
        "n_misses": len(report.misses),
        "misses": report.misses[:20],
    }
