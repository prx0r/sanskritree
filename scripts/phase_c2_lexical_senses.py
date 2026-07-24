"""Phase C2: Lazy lexical-sense inventory for active works.

For each lemma in Bhairavastava + Spandakārikā:
  1. Extract glosses from Mitrasamgraha training set
  2. Record commentary evidence from passage_relations
  3. Create lexical_senses + sense_evidence rows
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parents[1]
import sys
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect


def get_active_lemmas(conn) -> set[str]:
    """Get all lemmas appearing in active works (Bhairavastava + Spandakārikā)."""
    rows = conn.execute("""
        SELECT DISTINCT lex.lemma_slp1
        FROM token_analysis_hypothesis tah
        JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
        JOIN lexeme lex ON lex.lexeme_id = mat.lexeme_id
        JOIN token_occurrence tocc ON tocc.occurrence_id = tah.occurrence_id
        JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
        JOIN passages p ON p.passage_id = pr.passage_id
        WHERE p.work_id IN ('abhinavagupta_bhairavastava', 'spandakarika')
          AND lex.lemma_slp1 NOT LIKE '__%'
    """).fetchall()
    return {r[0] for r in rows}


def load_mitrasamgraha_glosses(path: str) -> dict[str, list[str]]:
    """Build lemma→gloss map from Mitrasamgraha training set."""
    lemma_glosses = defaultdict(list)
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        return {}

    # SLP1→IAST mapping for rough matching
    slp1_to_iast = {
        'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ',
        'x': 'ḷ', 'X': 'ḹ', 'M': 'ṃ', 'H': 'ḥ',
        'Y': 'ñ', 'T': 'ṭ', 'D': 'ḍ', 'N': 'ṇ',
        'S': 'ś', 'z': 'ṣ', 'L': 'ḻ',
    }

    def slp1_to_iast_rough(slp1: str) -> str:
        result = []
        for c in slp1:
            if c in slp1_to_iast:
                result.append(slp1_to_iast[c])
            else:
                result.append(c)
        return ''.join(result)

    for item in data[:5000]:  # Sample from training
        sk = item.get("sanskrit", "")
        en = item.get("english", "")
        # Extract key terms: look for short words that match our lemmas
        words = sk.split()
        for w in words[:3]:  # First few words most likely to contain key terms
            w_clean = re.sub(r'[^\w]', '', w)
            if 3 <= len(w_clean) <= 15:
                lemma_glosses[w_clean].append(en[:80])

    return lemma_glosses


def seed_senses(conn, lemmas: set[str], gloss_data: dict[str, list[str]]):
    """Create lexical_senses for each active lemma."""
    count = 0
    for lemma in sorted(lemmas):
        # Find IAST form from lexeme table
        iast = conn.execute(
            "SELECT lemma_iast FROM lexeme WHERE lemma_slp1 = ?",
            (lemma,)
        ).fetchone()
        iast_form = iast[0] if iast and iast[0] else lemma

        # Gather glosses
        glosses = gloss_data.get(iast_form, [])
        # Also try SLP1 form
        glosses.extend(gloss_data.get(lemma, []))
        gloss = glosses[0][:100] if glosses else ""

        sense_id = f"sense_{lemma}"
        conn.execute("""INSERT OR IGNORE INTO lexical_senses
            (sense_id, lemma, tradition, short_gloss, semantic_class)
            VALUES (?, ?, 'trika', ?, 'unknown')""",
            (sense_id, lemma, gloss or lemma))

        # Sense evidence from Mitrasamgraha
        for g in glosses[:3]:
            conn.execute("""INSERT OR IGNORE INTO sense_evidence
                (evidence_id, sense_id, passage_id, evidence_type, weight, review_status)
                VALUES (?, ?, 'mitrasamgraha', 'parallel_corpus', 0.3, 'unreviewed')""",
                (f"sev_{lemma}_{hash(g) % 10000}", sense_id))

        count += 1
        if count % 50 == 0:
            conn.commit()

    conn.commit()
    return count


def main():
    print("=" * 60)
    print("PHASE C2 — Lazy lexical-sense inventory")
    print("=" * 60)

    db_path = BASE / "data" / "sanskritree-v2.db"
    conn = connect(str(db_path))

    print("\n[1] Finding active lemmas...")
    lemmas = get_active_lemmas(conn)
    print(f"  {len(lemmas)} lemmas in active works")

    print("\n[2] Loading Mitrasamgraha glosses...")
    mitra_path = BASE / "data" / "datasets" / "mitrasamgraha_train.json"
    gloss_data = load_mitrasamgraha_glosses(str(mitra_path))
    total_entries = sum(len(v) for v in gloss_data.values())
    print(f"  {len(gloss_data)} lemma types, {total_entries} gloss entries")

    print("\n[3] Seeding lexical senses...")
    n = seed_senses(conn, lemmas, gloss_data)
    senses = conn.execute("SELECT count(*) FROM lexical_senses").fetchone()[0]
    evidence = conn.execute("SELECT count(*) FROM sense_evidence").fetchone()[0]
    print(f"  {senses} lexical senses, {evidence} sense evidence records")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
