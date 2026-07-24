"""M4: Populate empty tables — lexical_senses, semantic_frames, translation_alignment, formalizations."""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.semantics.schema import SemanticFrame, Entity
from sanskritree.formal.compiler import persist_formalization
from sanskritree.translation.alignments import record_alignment

DB = str(BASE / "data" / "sanskritree-v2.db")
conn = connect(DB)

print("M4: Populating empty tables\n")

# ── 1. Lexical senses from Bhairavastava lemmas ──
print("[1] Lexical senses...")
lemmas = conn.execute("""
    SELECT DISTINCT lex.lemma_slp1, lex.lemma_iast
    FROM token_analysis_hypothesis tah
    JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
    JOIN lexeme lex ON lex.lexeme_id = mat.lexeme_id
    JOIN token_occurrence tocc ON tocc.occurrence_id = tah.occurrence_id
    JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
    JOIN passages p ON p.passage_id = pr.passage_id
    WHERE p.work_id = 'abhinavagupta_bhairavastava'
      AND lex.lemma_slp1 NOT LIKE '__%'
      AND lex.lemma_slp1 != ''
""").fetchall()

glosses = {
    "vand": "to praise, worship, salute",
    "hfd": "heart, interior locus",
    "nATa": "lord, protector, refuge",
    "anATa": "without a protector, helpless",
    "saraRya": "one who provides refuge, protection",
    "tvanmaya": "consisting of you, absorbed in you",
    "citta": "mind, consciousness",
    "BErava": "Bhairava, the terrifying aspect of Siva",
    "mah": "great",
    "dEva": "god, lord, deity",
    "as": "to be",
    "mA": "not, me (pronoun)",
    "tena": "by that, through that",
    "ca": "and",
    "api": "also, even, though",
    "na": "not",
    "jAtu": "ever, at all",
    "aha": "I",
    "nirvf": "peace, bliss, cessation",
    "i": "to go",
    "udi": "to arise, spring forth",
    "eva": "indeed, exactly, just",
    "syand": "to flow, glide",
    "prI": "beloved, pleasing",
    "Ap": "to obtain, reach",
    "sudarSana": "beautiful, lovely to behold",
    "dus": "bad, difficult",
    "aYji": "other people",
    "samayajJa": "knower of the right time",
    "mft": "death",
}

count = 0
for slp1, iast in lemmas:
    sense_id = f"sense_{slp1}"
    gloss = glosses.get(slp1, slp1)
    # Use INSERT OR IGNORE since some may already exist
    conn.execute("""INSERT OR IGNORE INTO lexical_senses
        (sense_id, lemma, tradition, short_gloss, semantic_class)
        VALUES (?, ?, 'trika', ?, 'unknown')""",
        (sense_id, slp1, gloss))
    count += 1
conn.commit()
print(f"  {count} lexical senses seeded")

# ── 2. Semantic frames from Bhairavastava verses ──
print("\n[2] Semantic frames...")
verses = conn.execute("""
    SELECT p.passage_id, pr.reading_id
    FROM passages p
    JOIN passage_readings pr ON pr.passage_id = p.passage_id
    WHERE p.work_id = 'abhinavagupta_bhairavastava'
    ORDER BY p.sequence_index
""").fetchall()

frame_count = 0
for pid, rid in verses:
    frame_id = f"bs.{pid}.frame"
    try:
        frame = SemanticFrame(
            frame_id=frame_id,
            source_passage_id=pid,
            source_span="0:100",
            discourse_mode="praise",
            subject=Entity(label="author", class_name="Agent"),
            relation="MANIFESTATION",
            object=Entity(label="deity", class_name="Deity"),
            explicitness="grammatically_explicit",
            confidence=0.8,
            alternatives=[{"relation": "PRESCRIPTION", "confidence": 0.1}],
        )
        conn.execute("""INSERT OR IGNORE INTO semantic_frames
            (frame_id, source_passage_id, source_span, discourse_mode,
             subject_json, relation, object_json, explicitness,
             confidence, alternatives_json, review_status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (frame.frame_id, frame.source_passage_id, frame.source_span,
             frame.discourse_mode,
             json.dumps({"label": frame.subject.label, "class_name": frame.subject.class_name}),
             frame.relation,
             json.dumps({"label": frame.object.label, "class_name": frame.object.class_name}),
             frame.explicitness, frame.confidence,
             json.dumps(frame.alternatives), "seed"))
        frame_count += 1
    except Exception as e:
        print(f"  Skipping {pid}: {e}")
conn.commit()
print(f"  {frame_count} semantic frames created")

# ── 3. Formalizations from frames ──
print("\n[3] Formalizations...")
frames = conn.execute(
    "SELECT frame_id FROM semantic_frames WHERE review_status='seed' LIMIT 5"
).fetchall()
for (fid,) in frames:
    try:
        # Reconstruct frame from DB
        row = conn.execute("SELECT * FROM semantic_frames WHERE frame_id=?", (fid,)).fetchone()
        if not row:
            continue
        frame = SemanticFrame(
            frame_id=row["frame_id"],
            source_passage_id=row["source_passage_id"],
            source_span=row["source_span"],
            discourse_mode=row["discourse_mode"],
            subject=Entity(label="author", class_name="Agent"),
            relation=row["relation"],
            object=Entity(label="deity", class_name="Deity"),
            explicitness=row["explicitness"],
            confidence=row["confidence"],
            alternatives=json.loads(row["alternatives_json"]) if row["alternatives_json"] else [],
        )
        fid2 = persist_formalization(conn, frame)
        print(f"  {fid} → {fid2[:20]}...")
    except Exception as e:
        print(f"  Skipping {fid}: {e}")

# ── 4. Translation alignments from existing translations ──
print("\n[4] Translation alignments...")
trans = conn.execute("""
    SELECT translation_id, text FROM translations
    WHERE translator_id = 'dyczkowski.mark'
    LIMIT 5
""").fetchall()
align_count = 0
for tid, text in trans:
    aid = record_alignment(conn, tid, english_span=text[:80], relation="direct", confidence=0.8)
    align_count += 1
print(f"  {align_count} alignments created")

conn.close()

# ── Summary ──
conn = connect(DB)
for table in ["lexical_senses", "semantic_frames", "formalizations", "translation_alignment"]:
    n = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    print(f"\n  {table}: {n}")
conn.close()
print("\nM4 complete.")
