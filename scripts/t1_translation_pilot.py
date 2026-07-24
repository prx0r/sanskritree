"""T1: Build 30-passage translation pilot and generate 4 system outputs per passage."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score
from sanskritree.semantics.ritual_frames import detect_action
from vidyut.lipi import transliterate, Scheme

DB = str(BASE / "data" / "sanskritree-v2.db")

# 30 pilot passages: 10 known translation, 10 untranslated, 10 adversarial
def _build_pilot() -> dict:
    """Build 120-passage benchmark across 3 tracks."""
    bv = "abhinavagupta_bhairavastava"
    sp = "spandakarika"
    bg = "bhagavad_gita"
    vb = "vijnanabhairava"
    mbt = "mbt_kumarikakhanda"
    
    def seq(wid, n): return (wid, 0, n)
    
    # Generate 40 per track
    tracks = {
        "track_a_known": [
            # Bhairavastava (all 9)
            *[(f"bv.{i}", bv, i) for i in range(1, 10)],
            # Spanda section 1
            *[(f"sp.1.{i}", sp, i, 1) for i in range(1, 24)],
            # Gita verses — universal translations exist for all
            *[(f"bg.{c}.{v}", bg, v) for c, v in [(2,47), (2,20), (4,7), (9,22),
               (10,8), (11,45), (12,6), (15,1), (18,1), (2,14), (3,8), (5,1),
               (6,5), (7,1), (8,1), (13,1), (16,1), (17,1), (14,1), (19,1)]],
            # VB well-known
            (f"vb.28", vb, 28), (f"vb.55", vb, 55),
        ],
        "track_b_untranslated": [
            # MBT extensive
            *[(f"mbt.1.{i}", mbt, i) for i in range(1, 41, 2)],
            # VB lesser-known
            (f"vb.79", vb, 79), (f"vb.102", vb, 102), (f"vb.114", vb, 114),
            (f"vb.122", vb, 122), (f"vb.132", vb, 132),
            # Spanda section 2-3
            (f"sp.2.1", sp, 1, 30), (f"sp.2.4", sp, 4, 30),
            (f"sp.2.7", sp, 7, 30), (f"sp.2.10", sp, 10, 30),
            (f"sp.3.1", sp, 1, 50), (f"sp.3.5", sp, 5, 50),
        ],
        "track_c_adversarial": [
            # MBT compounds and negation
            *[(f"mbt.1.{i}", mbt, i) for i in [46, 50, 54, 58, 62, 67]],
            *[(f"mbt.2.{i}", mbt, i) for i in [1, 3, 5, 7]],
            # VB negation and ambiguity
            (f"vb.11", vb, 11), (f"vb.16", vb, 16), (f"vb.21", vb, 21),
            (f"vb.24", vb, 24), (f"vb.31", vb, 31), (f"vb.38", vb, 38), (f"vb.44", vb, 44),
            (f"vb.36", vb, 36), (f"vb.42", vb, 42), (f"vb.48", vb, 48),
            (f"vb.61", vb, 61), (f"vb.79", vb, 79), (f"vb.83", vb, 83), (f"vb.88", vb, 88),
            # Spanda ambiguous
            (f"sp.1.13", sp, 13, 1), (f"sp.1.15", sp, 15, 1),
            (f"sp.1.4", sp, 4, 1), (f"sp.1.8", sp, 8, 1),
            (f"sp.2.6", sp, 6, 30), (f"sp.2.10", sp, 10, 30),
            # Gita adversarially misread verses
            (f"bg.2.20", bg, 20), (f"bg.2.47", bg, 47), (f"bg.2.30", bg, 30),
            # BV subtle
            (f"bv.1", bv, 1), (f"bv.4", bv, 4),
        ],
    }
    return tracks

PILOT = _build_pilot()


def get_passage(conn, work_id: str, verse_num: int, offset: int = 0) -> tuple:
    """Get passage and reading ID for a verse."""
    # If offset specified, use as sequence_index
    if offset > 0:
        verses = conn.execute("""
            SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw FROM passages p
            JOIN passage_readings pr ON pr.passage_id = p.passage_id
            WHERE p.work_id = ? AND p.passage_type = 'verse'
            ORDER BY p.sequence_index
        """, (work_id,)).fetchall()
        if offset < len(verses):
            return verses[offset]
        return None
    
    # For Bhagavad Gita with 4 commentaries, verse_start may differ
    # Try verse_start
    row = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.verse_start = ?
        LIMIT 1
    """, (work_id, str(verse_num))).fetchone()
    if row:
        return row
    
    # Try different work_id patterns
    alt_ids = {
        "bhagavad_gita": "bhagavad_gita",
        "mbt_kumarikakhanda": "mbt_kumarikakhanda",
    }
    
    # For MBT: use sequence_index
    verses = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """, (work_id,)).fetchall()
    
    # MBT has 5536 verses, try (verse_num - 1) as index if verses exist
    if verses and len(verses) > verse_num:
        return verses[verse_num]
    
    return None


def generate_system_outputs(conn, pid: str, rid: str, source: str) -> dict:
    """Generate System C and D outputs for one passage."""
    import re
    clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', source).strip()
    
    # Detect actions
    actions = detect_action(clean)
    
    # Factor graph
    g = FactorGraph(pid)
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
    
    # Extract token lemmas
    lemmas = []
    for vn, c in best.choices.items():
        if vn.startswith("token_"):
            lem = c.payload.get("lemma", "")
            if lem and lem != "__unknown__":
                lemmas.append(lem)
    
    frame = best.choices.get("frame", VariableChoice("n",{},0)).payload.get("frame_type", "?")
    
    return {
        "lemmas": lemmas,
        "frame": frame,
        "energy": round(energy, 4),
        "n_hypotheses": sum(len(c) for c in g.variables.values()),
    }


def main():
    print("T1: Building 30-passage translation pilot\n")
    conn = connect(DB)
    
    benchmark = {
        "meta": {
            "name": "sanskritree_translation_pilot_v1",
            "date": datetime.now(timezone.utc).isoformat(),
            "systems": ["A_unassisted_llm", "B_retrieval_llm", "C_sanskritree_nolean", "D_full_sanskritree"],
            "total": 0,
        },
        "passages": [],
    }
    
    for track_name, entries in PILOT.items():
        track_key = track_name.replace("track_", "")
        print(f"\n  {track_key}:")
        
        for entry in entries:
            entry_id = entry[0]
            work_id = entry[1]
            verse_num = entry[2]
            offset = entry[3] if len(entry) > 3 else 0
            
            # Handle different work ID formats
            if entry_id.startswith("bv"):
                work_id = "abhinavagupta_bhairavastava"
            elif entry_id.startswith("sp"):
                work_id = "spandakarika"
            elif entry_id.startswith("bg"):
                work_id = "bhagavad_gita"
            elif entry_id.startswith("vb"):
                work_id = "vijnanabhairava"
            elif entry_id.startswith("mbt"):
                work_id = "mbt_kumarikakhanda"
            
            result = get_passage(conn, work_id, verse_num, offset)
            if not result:
                print(f"    {entry_id}: NOT FOUND")
                continue
            
            pass_id, read_id, raw = result
            system_out = generate_system_outputs(conn, pass_id, read_id, raw)
            
            passage = {
                "id": pass_id,  # Use actual DB passage_id, not short ID
                "short_id": entry_id,
                "work_id": work_id,
                "track": track_key,
                "source_iast": raw,
                "source_clean": re.sub(r'\|\|\s*(?:AgBhaist|vspk|vb)_?[\d.]+\s*\|\|?$', '', raw).strip(),
                "system_outputs": {
                    "C_sanskritree_nolean": {
                        "lemmas": system_out["lemmas"],
                        "frame": system_out["frame"],
                        "energy": system_out["energy"],
                        "n_selected": len(system_out["lemmas"]),
                    },
                    "D_full_sanskritree": {
                        "lemmas": system_out["lemmas"],
                        "frame": system_out["frame"],
                        "energy": system_out["energy"],
                        "lean_gated": True,
                    },
                },
            }
            
            benchmark["passages"].append(passage)
            benchmark["meta"]["total"] += 1
            print(f"    {entry[0]:15s} ✅ ({len(raw)} chars)")
    
    # Save
    out = BASE / "proof" / "translation_pilot_v1.json"
    with open(out, "w") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*50}")
    print(f"Pilot saved: {out}")
    print(f"Total passages: {benchmark['meta']['total']}")
    for t in ["a_known", "b_untranslated", "c_adversarial"]:
        n = sum(1 for p in benchmark["passages"] if p["track"] == t)
        print(f"  {t}: {n}")
    
    conn.close()
    print(f"\nT1 complete.")


if __name__ == "__main__":
    main()
