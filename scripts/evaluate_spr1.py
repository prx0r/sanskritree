"""Sprint 1 evaluation: layer-specific metrics from adjudication decisions."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")


def apply_migration(conn):
    conn.executescript(Path(BASE / "migrations" / "0005_v2_adjudication.sql").read_text())
    conn.commit()


def candidate_recall(conn, work_id: str, layer: str = "morphology") -> dict:
    """Gold recall@K for candidate generation."""
    decisions = conn.execute("""
        SELECT status, reason_code FROM adjudication_decisions ad
        JOIN passages p ON p.passage_id = ad.passage_id
        WHERE p.work_id = ? AND ad.layer = ?
    """, (work_id, layer)).fetchall()

    total = len(decisions)
    accepted = sum(1 for d in decisions if d[0] == "accepted")
    acceptable = sum(1 for d in decisions if d[0] == "acceptable_alternative")
    rejected = sum(1 for d in decisions if d[0] == "rejected")

    return {
        "layer": layer,
        "total_decisions": total,
        "accepted": accepted,
        "acceptable_alternative": acceptable,
        "rejected": rejected,
        "recall": round((accepted + acceptable) / max(total, 1) * 100, 1),
    }


def engine_comparison(conn, work_id: str) -> dict:
    """Compare candidate recall by engine."""
    engines = conn.execute("""
        SELECT DISTINCT tah.engine FROM token_analysis_hypothesis tah
        JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
        JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
        JOIN passages p ON p.passage_id = pr.passage_id
        WHERE p.work_id = ?
    """, (work_id,)).fetchall()

    results = {}
    for (eng,) in engines:
        n = conn.execute("""
            SELECT count(*) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id = ? AND tah.engine = ?
        """, (work_id, eng)).fetchone()[0]
        results[eng] = n
    return results


def coverage_report(conn, work_id: str) -> dict:
    """Token coverage by source span."""
    total = conn.execute("""
        SELECT count(*) FROM token_occurrence tocc
        JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
        JOIN passages p ON p.passage_id = pr.passage_id
        WHERE p.work_id = ?
    """, (work_id,)).fetchone()[0]

    covered = conn.execute("""
        SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
        JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
        JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
        JOIN passages p ON p.passage_id = pr.passage_id
        WHERE p.work_id = ?
    """, (work_id,)).fetchone()[0]

    return {
        "total_tokens": total,
        "covered_tokens": covered,
        "coverage_pct": round(covered / max(total, 1) * 100, 1),
    }


def reason_code_distribution(conn, work_id: str) -> dict:
    """Distribution of reason codes in adjudications."""
    codes = conn.execute("""
        SELECT reason_code, count(*) as cnt FROM adjudication_decisions ad
        JOIN passages p ON p.passage_id = ad.passage_id
        WHERE p.work_id = ? AND reason_code IS NOT NULL
        GROUP BY reason_code ORDER BY cnt DESC
    """, (work_id,)).fetchall()
    return {r[0]: r[1] for r in codes}


def main():
    print("Sprint 1: Evaluation framework\n")
    conn = connect(DB)
    apply_migration(conn)

    # Report on all active works
    for wid in ["abhinavagupta_bhairavastava", "spandakarika", "vijnanabhairava"]:
        title = conn.execute("SELECT canonical_title FROM works WHERE work_id=?", (wid,)).fetchone()
        if not title:
            continue
        print(f"\n{'='*60}")
        print(f"  {title[0]}")
        print(f"{'='*60}")

        cov = coverage_report(conn, wid)
        print(f"  Coverage: {cov['coverage_pct']}% ({cov['covered_tokens']}/{cov['total_tokens']})")

        eng = engine_comparison(conn, wid)
        print(f"  Engines: {json.dumps(eng, indent=2)}")

        # Check if adjudications exist
        n_adj = conn.execute("""
            SELECT count(*) FROM adjudication_decisions ad
            JOIN passages p ON p.passage_id = ad.passage_id
            WHERE p.work_id = ?
        """, (wid,)).fetchone()[0]
        if n_adj > 0:
            rec = candidate_recall(conn, wid)
            print(f"  Adjudications: {n_adj}")
            print(f"  Recall: {rec['recall']}% ({rec['accepted']} accepted, {rec['acceptable_alternative']} alt, {rec['rejected']} rejected)")
            codes = reason_code_distribution(conn, wid)
            if codes:
                print(f"  Reason codes: {json.dumps(codes, indent=2)}")
        else:
            print(f"  Adjudications: 0 (needs annotation)")

    conn.close()
    print(f"\nDone. Migration 0005 applied.")


if __name__ == "__main__":
    main()
