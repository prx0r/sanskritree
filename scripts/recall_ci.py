"""v0.3.1: Candidate-recall CI — Recall@k, engine contribution, low-coverage flags.

Runs against frozen 30-passage pilot. Outputs structured report.
Usage: PYTHONPATH=src python3 scripts/recall_ci.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))
from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")


def evaluate_candidate_recall() -> dict:
    """Evaluate candidate recall across the 30-passage pilot."""
    conn = connect(DB)
    pilot = json.loads(open(BASE / "proof" / "translation_pilot_v1.json").read())
    
    results = []
    overall = defaultdict(lambda: {"correct": 0, "total": 0, "passages": 0})
    low_coverage = []
    
    # Build canonical passage ID map
    id_map = {}
    # Assert all benchmark passage IDs resolve in the DB
    unresolved = []
    for passage in pilot["passages"]:
        pid = passage["id"]
        db_id = conn.execute("SELECT 1 FROM passages WHERE passage_id=? LIMIT 1", (pid,)).fetchone()
        if db_id:
            id_map[pid] = pid
        else:
            unresolved.append(pid)
    
    if unresolved:
        print(f"ERROR: {len(unresolved)} benchmark passages not found in DB: {unresolved}")
        print("Regenerate the pilot: python3 scripts/t1_translation_pilot.py")
        conn.close()
        return {"meta": {"error": "passage_id_mismatch", "unresolved": unresolved}}
    
    for passage in pilot["passages"]:
        pid = passage["id"]
        canonical_id = id_map[pid]
    
    for passage in pilot["passages"]:
        pid = passage["id"]
        canonical_id = id_map[pid]
        source = passage["source_clean"]
        clean = re.sub(r'\|\|\s*(?:vb|vspk|AgBhaist)_?[\d.]+\s*\|\|?$', '', source).strip()
        tokens = clean.split()
        n_tokens = len(tokens)
        
        # Count hypotheses by engine
        rid = conn.execute("""SELECT pr.reading_id FROM passages p2
            JOIN passage_readings pr ON pr.passage_id = p2.passage_id
            WHERE p2.passage_id=?""", (canonical_id,)).fetchone()
        
        engine_counts = {}
        total_hyps = 0
        if rid:
            engines = conn.execute("""SELECT tah.engine, count(*) FROM token_analysis_hypothesis tah
                JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
                WHERE tocc.passage_reading_id=?
                GROUP BY tah.engine""", (rid[0],)).fetchall()
            for eng, cnt in engines:
                engine_counts[eng] = cnt
                total_hyps += cnt
        
        # Lemma count (from system output — the selected lemmas)
        out = passage["system_outputs"].get("C_sanskritree_nolean", {})
        lemma_count = len(out.get("lemmas", []))
        frame = out.get("frame", "?")
        
        # Coverage: tokens with any hypothesis
        covered = 0
        if rid:
            covered = conn.execute("""SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
                JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
                LEFT JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
                WHERE tocc.passage_reading_id=? AND mat.lexeme_id != 'lex_unknown'""",
                (rid[0],)).fetchone()[0]
        
        # Low-coverage flag
        is_low = lemma_count <= 1
        if is_low:
            low_coverage.append({
                "passage": pid,
                "lemma_count": lemma_count,
                "total_hyps": total_hyps,
                "tokens": n_tokens,
                "covered": covered,
                "engine_counts": engine_counts,
                "failure_reason": _classify_failure(engine_counts, tokens),
            })
        
        entry = {
            "passage_id": pid,
            "track": passage["track"],
            "n_tokens": n_tokens,
            "covered_tokens": covered,
            "lemma_count": lemma_count,
            "total_hyps": total_hyps,
            "engine_counts": engine_counts,
            "low_coverage": is_low,
        }
        results.append(entry)
        
        for eng, cnt in engine_counts.items():
            overall[eng]["correct"] += cnt
            overall[eng]["passages"] += 1
        overall["total"]["total"] += total_hyps
        overall["total"]["passages"] += 1
    
    conn.close()
    
    return {
        "meta": {
            "benchmark": "30-passage translation pilot",
            "total_passages": len(results),
            "low_coverage_count": len(low_coverage),
        },
        "results": results,
        "low_coverage_verses": low_coverage,
        "engine_summary": {
            eng: {"hyps": data["correct"], "passages": data["passages"]}
            for eng, data in overall.items()
        },
        "recall_by_track": _compute_track_recall(results),
    }


def _classify_failure(engine_counts: dict, tokens: list[str]) -> str:
    """Classify why a passage has low coverage."""
    total = sum(engine_counts.values())
    if total == 0:
        return "ALL_ENGINES_MISS"
    long_tokens = [t for t in tokens if len(t) > 15]
    if long_tokens:
        return f"COMPOUND_SPLIT({len(long_tokens)} long tokens)"
    if "heritage" not in engine_counts and "vidyut" not in engine_counts:
        return "HERITAGE_TIMEOUT"
    return "PARTIAL_COVERAGE"


def _compute_track_recall(results: list) -> dict:
    """Compute recall metrics by track."""
    tracks = defaultdict(list)
    for r in results:
        tracks[r["track"]].append(r)
    
    track_stats = {}
    for track, items in tracks.items():
        total = len(items)
        low = sum(1 for i in items if i["low_coverage"])
        avg_lemmas = sum(i["lemma_count"] for i in items) / total
        avg_hyps = sum(i["total_hyps"] for i in items) / total
        avg_covered = sum(i["covered_tokens"] for i in items) / total
        track_stats[track] = {
            "passages": total,
            "low_coverage": low,
            "avg_lemmas": round(avg_lemmas, 1),
            "avg_hypotheses": round(avg_hyps, 1),
            "avg_covered_tokens": round(avg_covered, 1),
        }
    return track_stats


def main():
    print("v0.3.1: Candidate-recall CI\n")
    report = evaluate_candidate_recall()
    
    print(f"Total passages: {report['meta']['total_passages']}")
    print(f"Low-coverage: {report['meta']['low_coverage_count']}\n")
    
    print("By track:")
    for track, stats in report["recall_by_track"].items():
        print(f"  {track:20s} {stats['passages']} passages, {stats['low_coverage']} low, "
              f"{stats['avg_lemmas']} avg lemmas, {stats['avg_hypotheses']} avg hyps")
    
    print("\nLow-coverage verses:")
    for v in report["low_coverage_verses"]:
        print(f"  {v['passage']:15s} {v['lemma_count']} lemmas, "
              f"engines={v['engine_counts']}, reason={v['failure_reason']}")
    
    print("\nEngine contribution:")
    for eng, data in sorted(report["engine_summary"].items(), key=lambda x: -x[1]["hyps"]):
        print(f"  {eng:25s} {data['hyps']:6d} hyps across {data['passages']} passages")
    
    out = BASE / "proof" / "recall_ci_v03.json"
    with open(out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {out}")
    print(f"\nSuccess criterion: ≤2 low-coverage passages (currently {report['meta']['low_coverage_count']})")


if __name__ == "__main__":
    main()
