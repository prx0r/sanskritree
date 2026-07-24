"""M6.5: Heritage occurrence mapping — DP aligner, dedup, exclusion groups."""
from __future__ import annotations

import json
import re
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from vidyut.lipi import transliterate, Scheme
from heritage.heritage import HeritagePlatform, SolutionAnalysis

from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")


# ── IAST ↔ Devanagari utilities ──

def iast_to_deva(text: str) -> str:
    return transliterate(text, Scheme.Iast, Scheme.Devanagari)

def deva_to_iast(text: str) -> str:
    return transliterate(text, Scheme.Devanagari, Scheme.Iast)

# ── DP aligner: source characters → Heritage reconstructed segments ──

def dp_align(source_iast: str, heritage_segments: list[str]) -> list[dict]:
    """Dynamic programming aligner between IAST source and Heritage Devanagari segments.

    Returns list of alignment records mapping each segment to source character offsets.
    """
    # Normalize: strip metadata markers from source
    source_clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', source_iast).strip()

    # Convert source to Devanagari for comparison
    try:
        source_deva = iast_to_deva(source_clean)
    except Exception:
        source_deva = source_clean

    # Remove trailing 'a' that Heritage adds in Velthuis conversion
    segs = [s.rstrip('a') for s in heritage_segments]

    # DP: align segments to source
    # We work in Devanagari since that's what Heritage returns
    source_chars = list(source_deva)
    n = len(source_chars)
    m = len(segs)

    # Score matrix: best alignment of first i source chars to first j segments
    INF = 10**9
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    choice = [[-1] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        for j in range(m + 1):
            if dp[i][j] >= INF:
                continue
            if j < m:
                seg_chars = list(segs[j])
                for k in range(i + 1, min(n + 1, i + len(seg_chars) * 3 + 1)):
                    match = ''.join(source_chars[i:k])
                    cost = abs(len(match) - len(seg_chars))
                    if match == seg_chars[:len(match)] or seg_chars[:len(match)] == match:
                        pass  # good match
                    else:
                        cost += 2  # character mismatch penalty
                    if dp[k][j + 1] > dp[i][j] + cost:
                        dp[k][j + 1] = dp[i][j] + cost
                        choice[k][j + 1] = i

    # Backtrack
    alignments = []
    i, j = n, m
    while j > 0 and i > 0:
        prev_i = choice[i][j]
        if prev_i < 0:
            break
        alignments.append({
            "source_start": prev_i,
            "source_end": i,
            "segment_text_deva": segs[j - 1],
            "segment_text_iast": deva_to_iast(segs[j - 1]) if segs[j - 1] else segs[j - 1],
            "segment_index": j - 1,
        })
        i = prev_i
        j -= 1

    alignments.reverse()
    return alignments


# ── Hypothesis support table ──

def ensure_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hypothesis_solution_support (
            hypothesis_id TEXT NOT NULL,
            heritage_solution_id TEXT NOT NULL,
            local_segment_index INTEGER NOT NULL,
            PRIMARY KEY (hypothesis_id, heritage_solution_id, local_segment_index)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS segmentation_choice_group (
            group_id TEXT PRIMARY KEY,
            passage_id TEXT NOT NULL,
            exactly_one INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS segmentation_choice_member (
            group_id TEXT NOT NULL,
            segmentation_hypothesis_id TEXT NOT NULL,
            PRIMARY KEY (group_id, segmentation_hypothesis_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS token_analysis_choice_group (
            group_id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            at_most_one INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()


# ── Main mapping pipeline ──

def process_verse(conn, passage_id: str, reading_id: str, source_iast: str):
    """Full Heritage → graph mapping for one verse."""
    now = datetime.now(timezone.utc).isoformat()

    # Call Heritage
    try:
        deva = iast_to_deva(source_iast)
    except Exception:
        return {"status": "error", "reason": "IAST→Devanagari failed"}

    platform = HeritagePlatform(method="web")
    result = platform.get_analysis(deva, sentence=True, structured=True)
    if not result:
        return {"status": "error", "reason": "Heritage returned no solutions"}

    total_solutions = 0
    total_hyps = 0
    dedup_saved = 0
    seen_analyses = set()

    # Create segmentation choice group
    group_id = f"seg_group_{reading_id}"
    conn.execute("""INSERT OR IGNORE INTO segmentation_choice_group
        (group_id, passage_id, exactly_one) VALUES (?, ?, 1)""",
        (group_id, passage_id))

    for sol_id in sorted(result.keys()):
        sol = result[sol_id]
        if not isinstance(sol, SolutionAnalysis) or not sol.words:
            continue

        sol_str = str(sol_id)
        words = [str(w.text) for w in sol.words if str(w.text).strip()]
        if len(words) < 2:
            continue

        total_solutions += 1

        # DP align
        alignments = dp_align(source_iast, words)
        if not alignments:
            continue

        seg_hyp_id = f"seg_{reading_id}_{sol_str}"
        conn.execute("""INSERT OR IGNORE INTO segmentation_choice_member
            (group_id, segmentation_hypothesis_id) VALUES (?, ?)""",
            (group_id, seg_hyp_id))

        # Process each aligned segment
        for al in alignments:
            seg_text = al["segment_text_deva"]
            seg_iast = al["segment_text_iast"]

            # Check if this segment has a matching token_occurrence
            # by approximate position
            tok_idx = al["segment_index"]
            occ = conn.execute("""
                SELECT occurrence_id FROM token_occurrence
                WHERE passage_reading_id = ? AND token_index = ?
                LIMIT 1
            """, (reading_id, tok_idx)).fetchone()

            if not occ:
                continue
            occ_id = occ[0]

            # Extract analysis data from Heritage word object
            word_obj = sol.words[tok_idx] if tok_idx < len(sol.words) else None
            root = ""
            analyses = []
            if word_obj and hasattr(word_obj, 'candidates') and word_obj.candidates:
                cands = list(word_obj.candidates)
                if cands:
                    root = str(cands[0].root) if hasattr(cands[0], 'root') else ""
                    if hasattr(cands[0], 'analyses'):
                        for a in list(cands[0].analyses)[:1]:
                            analyses = [str(x) for x in a]

            # Build canonical analysis key for dedup
            canon_key = f"{root}|{'|'.join(analyses)}"
            canon_dup = canon_key in seen_analyses
            seen_analyses.add(canon_key)

            if canon_dup and len(analyses) >= 3:
                # Skip duplicate canonical analysis
                dedup_saved += 1
                continue

            if not root:
                continue

            # Convert root to IAST for lexeme lookup
            try:
                root_iast = deva_to_iast(root) if any(ord(c) > 127 for c in root) else root
            except Exception:
                root_iast = root

            # Create or find lexeme
            root_slp1 = transliterate(root, Scheme.Devanagari, Scheme.Slp1) if any(ord(c) > 127 for c in root) else root
            lid = f"lex_her_{root_slp1}"
            conn.execute("""INSERT OR IGNORE INTO lexeme
                (lexeme_id, lemma_slp1, lemma_iast, lemma_devanagari, pos, created_at)
                VALUES (?, ?, ?, ?, 'heritage', ?)""",
                (lid, root_slp1, root_iast, root, now))

            # Create morph analysis type — ensure lexeme FK first
            features = {}
            if len(analyses) >= 3:
                features["heritage_gender"] = analyses[0]
                features["heritage_case"] = analyses[1]
                features["heritage_number"] = analyses[2]
            elif len(analyses) == 1:
                features["heritage_pos"] = analyses[0]

            feat_json = json.dumps(features, sort_keys=True)
            atype_id = f"mat_her_{root_slp1}_{analyses[1] if len(analyses) > 1 else 'x'}"

            # Find actual lexeme_id — it might already exist under a different ID
            existing = conn.execute(
                "SELECT lexeme_id FROM lexeme WHERE lemma_slp1 = ? LIMIT 1",
                (root_slp1,)
            ).fetchone()
            actual_lid = existing[0] if existing else lid

            # Ensure it exists
            if not existing:
                conn.execute("""INSERT OR IGNORE INTO lexeme
                    (lexeme_id, lemma_slp1, lemma_iast, lemma_devanagari, pos, created_at)
                    VALUES (?, ?, ?, ?, 'heritage', ?)""",
                    (lid, root_slp1, root_iast, root, now))
                actual_lid = lid

            try:
                conn.execute("""INSERT INTO morph_analysis_type
                    (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)""",
                    (atype_id, actual_lid, feat_json, root_slp1[:16], now))
            except Exception:
                continue  # FK failure, skip this analysis

            # Create hypothesis
            hyp_id = f"hyp_her_{reading_id}_{tok_idx}_{sol_str}"
            conf = 0.5 + (0.3 / (1 + int(sol_str)))
            conn.execute("""INSERT OR IGNORE INTO token_analysis_hypothesis
                (hypothesis_id, occurrence_id, analysis_type_id, engine,
                 confidence, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
                (hyp_id, occ_id, atype_id, "heritage", min(conf, 0.9), now))
            total_hyps += 1

            # Record solution support
            conn.execute("""INSERT OR IGNORE INTO hypothesis_solution_support
                (hypothesis_id, heritage_solution_id, local_segment_index)
                VALUES (?, ?, ?)""",
                (hyp_id, sol_str, tok_idx))

    conn.commit()
    return {
        "status": "ok",
        "solutions": total_solutions,
        "hypotheses": total_hyps,
        "dedup_saved": dedup_saved,
    }


# ── Fixture tests ──

def test_fixtures(conn):
    """Test known compound fixtures."""
    fixtures = {
        "bhairavanātham": ["bhairava", "nātha"],
        "anāthaśaraṇyam": ["anātha", "śaraṇya"],
        "tvanmayacittatayā": ["tvad", "maya", "citta", "tayā"],
    }

    platform = HeritagePlatform(method="web")
    results = {}
    for iast, expected in fixtures.items():
        try:
            deva = iast_to_deva(iast)
            result = platform.get_analysis(deva, sentence=True, structured=True)
            found = False
            if result:
                for sol_id in sorted(result.keys()):
                    sol = result[sol_id]
                    if isinstance(sol, SolutionAnalysis) and sol.words:
                        words = [str(w.text).rstrip('a') for w in sol.words]
                        # Check if expected members appear as substrings of Heritage words
                        found_count = 0
                        for e in expected:
                            e_deva = iast_to_deva(e).rstrip('a')
                            if any(e_deva in w for w in words):
                                found_count += 1
                        if found_count >= max(2, len(expected) - 1):
                            found = True
                            results[iast] = {"status": "pass", "words": words[:6]}
                            break
            if not found:
                results[iast] = {"status": "fail", "expected": expected, "heritage_words": words[:6] if result and any(isinstance(sol, SolutionAnalysis) and sol.words for sol in result.values()) else []}
        except Exception as e:
            results[iast] = {"status": "error", "error": str(e)}
    return results


def main():
    print("M6.5: Heritage occurrence mapping\n")
    conn = connect(DB)
    ensure_schema(conn)

    # Test fixtures first
    print("[1] Running fixture tests...")
    fixtures = test_fixtures(conn)
    for iast, result in fixtures.items():
        status = result["status"]
        if status == "pass":
            print(f"  ✅ {iast:25s} → {result['words']}")
        else:
            print(f"  ❌ {iast:25s} → {result}")

    # Process Bhairavastava first (small, fast)
    print("\n[2] Processing Bhairavastava verses...")
    verses = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'abhinavagupta_bhairavastava' AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """).fetchall()

    for pid, rid, raw in verses:
        clean = re.sub(r'\|\|\s*AgBhaist_\d+\s*\|\|?$', '', raw).strip()
        r = process_verse(conn, pid, rid, clean)
        if r["status"] == "ok":
            print(f"  {pid:20s} {r['solutions']:3d} solutions, {r['hypotheses']:3d} hyps, {r['dedup_saved']} dedup")

    # Process Spandakārikā (batch of 20)
    print("\n[3] Processing Spandakārikā (first 20 verses)...")
    verses2 = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'spandakarika' AND p.passage_type = 'verse'
        ORDER BY p.sequence_index LIMIT 20
    """).fetchall()

    for pid, rid, raw in verses2:
        clean = re.sub(r'\|\|\s*vspk_\d+\.\d+\s*\|\|?$', '', raw).strip()
        r = process_verse(conn, pid, rid, clean)
        if r["status"] == "ok":
            print(f"  {pid:20s} {r['solutions']:3d} solutions, {r['hypotheses']:3d} hyps, {r['dedup_saved']} dedup")

    # Coverage report
    print("\n[4] Coverage report:")
    for wid in ["abhinavagupta_bhairavastava", "spandakarika"]:
        with_hyp = conn.execute("""
            SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id=?
        """, (wid,)).fetchone()[0]
        total = conn.execute("""
            SELECT count(*) FROM token_occurrence tocc
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id=?
        """, (wid,)).fetchone()[0]
        engines = conn.execute("""
            SELECT tah.engine, count(*) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id=?
            GROUP BY tah.engine ORDER BY count(*) DESC
        """, (wid,)).fetchall()
        print(f"  {wid}: {with_hyp}/{total} tokens covered ({with_hyp/max(total,1)*100:.0f}%)")
        for eng, cnt in engines:
            print(f"    {eng}: {cnt}")

    conn.close()
    print("\nM6.5 complete.")


if __name__ == "__main__":
    main()
