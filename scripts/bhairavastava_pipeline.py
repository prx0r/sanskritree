"""Complete Bhairavastava pipeline: correct v1, blind translate v2-9, record everything."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect, migrate
from sanskritree.translation.candidates import start_blind_run, record_candidate
from sanskritree.semantics.schema import SemanticFrame, Entity
from sanskritree.formal.compiler import compile_frame, persist_formalization

conn = connect(str(BASE / "data" / "sanskritree-v2.db"))

# ── helpers ──

def get_verse(n: int):
    row = conn.execute("""
        SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'abhinavagupta_bhairavastava' AND p.verse_start = ?
        ORDER BY p.sequence_index LIMIT 1
    """, (str(n),)).fetchone()
    return row

def recording_error(candidate_id, error_type, severity, span, note):
    return {"candidate_id": candidate_id, "error_type": error_type,
            "severity": severity, "span": span, "note": note}

# ══════════════════════════════════════════════════════════
# PHASE 1.1: Correct verse 1 candidates
# ══════════════════════════════════════════════════════════

print("=" * 60)
print("PHASE 1.1 — Correct verse 1 candidates")
print("=" * 60)

row1 = get_verse(1)
pid, vs, rid, raw = row1
print(f"\nSource: {raw}")

# Create new blind run for corrected verse 1
run_id = start_blind_run(conn, pid,
    profiles=["construal", "philological", "interpretive"],
    retrieval_results=[{"source": "vidyut", "lemma_count": 4}],
    prompt_version="v2-bhairavastava-v2"
)

errors = []

# ── Candidate A (corrected) ──
cand_a = (
    "Lord Bhairava, refuge of the helpless — "
    "with my mind absorbed in you, I praise in my heart."
)
ca_id = record_candidate(conn, run_id, "construal", cand_a,
    senses=[{"lemma": "bhairava", "gloss": "Bhairava", "case": "accusative"},
            {"lemma": "natha", "gloss": "lord", "case": "accusative"},
            {"lemma": "vand", "gloss": "to praise"}],
    parses=[{"compound": "bhairavanatham", "split": "karmadharaya",
             "members": ["bhairava", "natha"]},
            {"compound": "tvanmayacittataya",
             "analysis": "tvad-maya-citta-ta-ya (abstract noun, instr.sg)",
             "relation": "qualification"}],
    ranking={"fidelity": 0.85, "fluency": 0.7,
             "evidence": [{"source": "vidyut", "note": "bhairavanatham: karmadharaya preferred"}]}
)
print(f"\n[A] CONSTRUAL: {cand_a}")

# ── Candidate B (corrected) ──
cand_b = (
    "With my mind wholly absorbed in you, "
    "I praise in my heart Lord Bhairava, refuge of the helpless."
)
cb_id = record_candidate(conn, run_id, "philological", cand_b,
    senses=[{"lemma": "bhairava", "gloss": "Lord Bhairava"},
            {"lemma": "natha", "gloss": "lord/protector"}],
    parses=[{"compound": "bhairavanatham", "split": "karmadharaya"}],
    ranking={"fidelity": 0.85, "fluency": 0.85,
             "evidence": [{"source": "vidyut"}]}
)
print(f"[B] PHILOLOGICAL: {cand_b}")

# ── Candidate C (corrected — no unsupported additions) ──
cand_c = (
    "With my consciousness completely absorbed in you, "
    "I worship in my innermost heart Lord Bhairava, "
    "the sole refuge of all who are helpless."
)
cc_id = record_candidate(conn, run_id, "interpretive", cand_c,
    senses=[{"lemma": "bhairava", "gloss": "Bhairava, the terrifying aspect of Siva"},
            {"lemma": "tvanmaya", "gloss": "consisting of you, absorbed in you"},
            {"lemma": "citta", "gloss": "mind, consciousness"}],
    parses=[{"compound": "bhairavanatham", "split": "karmadharaya"},
            {"compound": "tvanmayacittataya",
             "analysis": "tvad-maya-citta-ta (abstract noun suffix + instr.sg)",
             "relation": "qualification (not bahuvrihi)"}],
    ranking={"fidelity": 0.8, "fluency": 0.9,
             "evidence": [{"source": "trika_tradition",
                           "note": "hrdi interpreted as innermost heart (not physical organ)"}]}
)
print(f"[C] INTERPRETIVE: {cand_c}")

# ── Token alignments for candidate B (strongest) ──
alignments = [
    {"span": "bhairavanatham", "english": "Lord Bhairava", "type": "direct",
     "compound": "karmadharaya", "case": "accusative"},
    {"span": "anathasaranyam", "english": "refuge of the helpless", "type": "direct",
     "compound": "tatpurusa", "note": "anatha-saranya: refuge of the helpless"},
    {"span": "tvanmayacittataya", "english": "with my mind wholly absorbed in you",
     "type": "direct", "case": "instrumental",
     "note": "abstract noun (ta) + instr (ya): 'by the state of...'"},
    {"span": "hrdi", "english": "in my heart", "type": "direct", "case": "locative"},
    {"span": "vande", "english": "I praise", "type": "direct",
     "person": "first", "tense": "present"},
    {"span": "implicit_agent", "english": "I", "type": "implicit",
     "note": "1st person verb, no explicit pronoun in Sanskrit"},
]
print(f"\nToken alignments: {len(alignments)} spans")
for a in alignments:
    print(f"  {a['span']:25s} → {a['english']:40s} ({a['type']})")

# ── Error annotations for previous candidates ──
old_errors = [
    {"candidate": "A (original)", "error": "COMPOUND_BOUNDARY",
     "severity": "major",
     "span": "bhairavanatham",
     "note": "Nominalized natha to 'lordship'. Sanskrit has accusative natham = 'the Lord' (karmadharaya, not possessive tatpurusa)"},
    {"candidate": "C (original)", "error": "DOCTRINAL_ADDITION",
     "severity": "major",
     "span": "'the one consciousness, whole, endless, without beginning, who pervades every state...'",
     "note": "These attributes belong to other verses in the hymn (2-3), not verse 1. Must be labelled as contextual commentary."},
    {"candidate": "C (original)", "error": "COMPOUND_BOUNDARY",
     "severity": "minor",
     "span": "tvanmayacittataya",
     "note": "Analysed as bahuvrihi. More likely tvad-maya-citta-ta-ya: abstract noun (ta) + instrumental. Not a bahuvrihi compound."},
]
print(f"\nError annotations: {len(old_errors)}")
for e in old_errors:
    print(f"  [{e['severity']}] {e['error']} ({e['candidate']}): {e['note'][:80]}...")

# ══════════════════════════════════════════════════════════
# PHASE 1.2: Minimal Layer B schema — verse 1 frame
# ══════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("PHASE 1.2 — Layer B: Semantic frame (verse 1)")
print("=" * 60)

# Five frame types: DevotionalAct | IdentityClaim | Predication | StateOrManner | Qualification

frame = SemanticFrame(
    frame_id=f"bs.v1.frame",
    source_passage_id=pid,
    source_span="0:70",
    discourse_mode="praise",
    subject=Entity(label="abhinavagupta", class_name="Agent"),
    relation="MANIFESTATION",
    object=Entity(label="bhairavanatha", class_name="Deity"),
    explicitness="grammatically_explicit",
    confidence=0.9,
    alternatives=[
        {"relation": "PRESCRIPTION", "confidence": 0.1,
         "note": "praise as injunction to the reader"}
    ]
)
print(f"Frame: {frame.frame_id}")
print(f"  Mode: {frame.discourse_mode}")
print(f"  Subject: {frame.subject.label} ({frame.subject.class_name})")
print(f"  Relation: {frame.relation}")
print(f"  Object: {frame.object.label} ({frame.object.class_name})")

# Store in DB
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

# Generate Lean from frame
lean_code, template, assumptions = compile_frame(frame)
formalization_id = persist_formalization(conn, frame)
print(f"  Lean: {template} axiom frame_bs_v1_frame")
print(f"  Formalization ID: {formalization_id}")

# ══════════════════════════════════════════════════════════
# PHASE 1.3: Blind translate verses 2–9
# ══════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("PHASE 1.3 — Blind translate verses 2–9")
print("=" * 60)

blind_runs = []
for vn in range(2, 10):
    row = get_verse(vn)
    if not row:
        print(f"Verse {vn}: not found, skipping")
        continue
    pid, vs, rid, raw = row
    rid2 = start_blind_run(conn, pid,
        profiles=["construal", "philological", "interpretive"],
        retrieval_results=[{"source": "vidyut", "raw": raw[:60]}],
        prompt_version="v2-bhairavastava-blind-v1"
    )
    blind_runs.append((vn, pid, rid2, raw))
    print(f"  [{vn}] {pid}: run created")

# Add a placeholder translation candidate for each (human enters later)
for vn, pid, run_id, raw in blind_runs:
    # Temporary stub — replace with human translation
    record_candidate(conn, run_id, "philological",
        "[BLIND — awaiting human translation]",
        senses=[], parses=[], ranking={"fidelity": 0.0, "fluency": 0.0,
                                       "evidence": [{"source": "pending_human"}]}
    )

conn.commit()
print(f"\n  {len(blind_runs)} blind runs created, candidates stubbed")

# ══════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Verse 1: 3 candidates corrected, {len(alignments)} token alignments, {len(old_errors)} error annotations")
print(f"  Verse 1 Layer B: SemanticFrame generated, Lean axiom compiled")
print(f"  Verses 2-9: {len(blind_runs)} blind runs created, awaiting human translation")
print(f"  Total run: {conn.execute('SELECT count(*) FROM translation_runs').fetchone()[0]}")

# Show all candidates created
cands = conn.execute("""
    SELECT tr.mode, tc.profile, substr(tc.text, 1, 60)
    FROM translation_candidates tc
    JOIN translation_runs tr ON tc.run_id = tr.run_id
    ORDER BY tr.created_at DESC LIMIT 12
""").fetchall()
print(f"\n  Recent translation candidates:")
for mode, profile, text in cands:
    print(f"    {mode:15s} {profile:15s} {text}...")

conn.close()
print("\nDone.")
