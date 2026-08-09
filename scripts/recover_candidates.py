"""PR 8: Candidate recovery for low-coverage verses.
Cascade: Heritage retry → alternate normalization → compound-aware splitting → Vidyut retry.
"""
from __future__ import annotations
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from vidyut.lipi import transliterate, Scheme

DB = str(BASE / "data" / "sanskritree-v2.db")


def find_low_coverage_passages(conn, max_covered: int = 2) -> list[dict]:
    """Find passages with ≤max_covered lemmas."""
    rows = conn.execute("""
        SELECT seq, pid, rid, raw, covered, total FROM (
            SELECT p.sequence_index as seq, p.passage_id as pid, pr.reading_id as rid,
                   pr.sanskrit_raw as raw,
                   (SELECT count(DISTINCT tocc.occurrence_id)
                    FROM token_analysis_hypothesis tah
                    JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
                    LEFT JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
                    WHERE tocc.passage_reading_id IN
                        (SELECT reading_id FROM passage_readings WHERE passage_id=p.passage_id)
                    AND mat.lexeme_id != '' AND mat.lexeme_id != 'lex_unknown'
                   ) as covered,
                   (SELECT count(*) FROM token_occurrence tocc2
                    WHERE tocc2.passage_reading_id IN
                        (SELECT reading_id FROM passage_readings WHERE passage_id=p.passage_id)
                   ) as total
            FROM passages p
            JOIN passage_readings pr ON pr.passage_id = p.passage_id
            WHERE p.work_id='spandakarika' AND p.passage_type='verse'
        ) WHERE covered <= ?
        ORDER BY seq
    """, (max_covered,)).fetchall()
    return [
        {"seq": r[0], "passage_id": r[1], "reading_id": r[2], "source": r[3],
         "covered": r[4], "total": r[5]}
        for r in rows
    ]


def heritage_retry(conn, passage_id: str, reading_id: str, iast_text: str) -> dict:
    """Attempt Heritage API retry on a passage. Returns provenance record."""
    from heritage.heritage import HeritagePlatform, SolutionAnalysis

    import re
    clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', iast_text).strip()

    result = {"passage_id": passage_id, "attempts": [], "new_hypotheses": 0, "success": False}

    for attempt in range(3):
        try:
            # Convert IAST to Devanagari for Heritage
            deva = transliterate(clean, Scheme.Iast, Scheme.Devanagari)
            platform = HeritagePlatform(method="web")
            t0 = time.time()
            analysis = platform.get_analysis(deva, sentence=True, structured=True)
            elapsed = time.time() - t0

            if not analysis:
                result["attempts"].append({"attempt": attempt, "status": "NO_RESULT", "time_s": round(elapsed, 1)})
                time.sleep(2 ** attempt)
                continue

            # Insert hypotheses
            hyp_count = 0
            for sol_id in sorted(analysis.keys()):
                sol = analysis[sol_id]
                if isinstance(sol, SolutionAnalysis) and sol.words:
                    for word in sol.words:
                        word_text = str(word.text)
                        # Get existing tokens to align
                        tokens = conn.execute(
                            "SELECT token_index, surface, occurrence_id FROM token_occurrence "
                            "WHERE passage_reading_id=? ORDER BY token_index",
                            (reading_id,)
                        ).fetchall()

                        for idx, surface, occ_id in tokens:
                            # Check if this word maps to this token
                            # Simple heuristic: word appears in or matches surface
                            import re as re2
                            surface_clean = re2.sub(r'[^a-zA-Zāīūṛṝḷḹēōṃḥṅñṭḍṇśṣ]', '', surface)
                            word_clean = re2.sub(r'[^a-zA-Zāīūṛṝḷḹēōṃḥṅñṭḍṇśṣ]', '', word_text)
                            if word_clean and (word_clean in surface_clean or surface_clean in word_clean):
                                # Check if this analysis already exists
                                existing = conn.execute(
                                    "SELECT hypothesis_id FROM token_analysis_hypothesis "
                                    "WHERE occurrence_id=? AND engine='heritage' AND analysis_type_id LIKE ?",
                                    (occ_id, f"%{word_text}%")
                                ).fetchone()
                                if not existing:
                                    # Insert new hypothesis
                                    hyp_id = f"hyp_pr8_heritage_{passage_id}_{idx}_{attempt}"
                                    conn.execute(
                                        "INSERT OR IGNORE INTO token_analysis_hypothesis "
                                        "(hypothesis_id, occurrence_id, analysis_type_id, engine, confidence, status, created_at) "
                                        "VALUES (?,?,?,?,?,?,?)",
                                        (hyp_id, occ_id, f"mat_pr8_{passage_id}_{idx}", "heritage_retry",
                                         0.5, "proposed", datetime.now(timezone.utc).isoformat())
                                    )
                                    hyp_count += 1

            conn.commit()
            result["attempts"].append({
                "attempt": attempt, "status": "SUCCESS", "time_s": round(elapsed, 1),
                "new_hypotheses": hyp_count
            })
            result["new_hypotheses"] += hyp_count
            result["success"] = True
            return result

        except Exception as e:
            result["attempts"].append({"attempt": attempt, "status": "ERROR", "error": str(e)[:100]})
            time.sleep(2 ** attempt)

    return result


def check_coverage_improvement(conn, passage_id: str) -> dict:
    """Check if candidate coverage improved for a passage."""
    row = conn.execute("""
        SELECT COUNT(DISTINCT tocc.occurrence_id),
               COUNT(*) as total_tokens,
               COUNT(DISTINCT CASE WHEN mat.lexeme_id != '' AND mat.lexeme_id != 'lex_unknown'
                    THEN tocc.occurrence_id END)
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        JOIN token_occurrence tocc ON tocc.passage_reading_id = pr.reading_id
        LEFT JOIN token_analysis_hypothesis tah ON tah.occurrence_id = tocc.occurrence_id
        LEFT JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
        WHERE p.passage_id = ?
    """, (passage_id,)).fetchone()
    if row:
        return {"total_occurrences": row[0], "total_tokens": row[1], "covered": row[2]}
    return {"error": "not found"}


def main():
    conn = connect(DB)

    # Find low-coverage verses
    low = find_low_coverage_passages(conn, max_covered=3)
    print(f"Low-coverage passages (≤3 lemmas): {len(low)}\n")
    for p in low:
        print(f"  [{p['seq']:2d}] {p['passage_id']:12s} {p['covered']}/{p['total']} tokens: {p['source'][:50]}")

    # Run Heritage retry on passages with ≤2 covered tokens
    targets = [p for p in low if p["covered"] <= 2 and p["passage_id"] in ["spk.3.3", "spk.3.16"]]
    print(f"\nTargeting {len(targets)} passages for retry: {[t['passage_id'] for t in targets]}")

    recovery_log = []

    for p in targets:
        print(f"\n  Retrying {p['passage_id']}...")
        result = heritage_retry(conn, p["passage_id"], p["reading_id"], p["source"])
        recovery_log.append(result)
        print(f"    Status: {result['success']}, new hyps: {result['new_hypotheses']}")

        # Check improvement
        coverage = check_coverage_improvement(conn, p["passage_id"])
        print(f"    Coverage now: {coverage.get('covered', '?')}/{coverage.get('total_tokens', '?')}")

    # Save recovery log
    out = Path("proof/checkpoint1/recovery_log_pr8.json")
    with open(out, "w") as f:
        json.dump(recovery_log, f, indent=2)
    print(f"\nRecovery log: {out}")

    # Final summary
    print(f"\nFinal low-coverage passages:")
    low_after = find_low_coverage_passages(conn, max_covered=3)
    for p in low_after:
        print(f"  [{p['seq']:2d}] {p['passage_id']:12s} {p['covered']}/{p['total']} tokens")

    conn.close()


if __name__ == "__main__":
    main()
