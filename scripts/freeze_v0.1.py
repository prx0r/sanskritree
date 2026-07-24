"""Freeze Research Kernel v0.1 — reproducible baseline.

Usage: PYTHONPATH=src python3 scripts/freeze_v0.1.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))
from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")

def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main():
    print("=" * 60)
    print("FREEZE: Research Kernel v0.1")
    print("=" * 60)
    
    conn = connect(DB)
    
    # 1. Corpus stats
    print("\n[1] Corpus:")
    for wid, title in conn.execute("SELECT work_id, canonical_title FROM works").fetchall():
        n_v = conn.execute("SELECT count(*) FROM passages WHERE work_id=? AND passage_type='verse'", (wid,)).fetchone()[0]
        n_p = conn.execute("SELECT count(*) FROM passages WHERE work_id=?", (wid,)).fetchone()[0]
        print(f"  {title[:50]:50s} {n_v} verses, {n_p} passages")
    
    # 2. Pipeline tests
    print("\n[2] Tests:")
    import unittest
    loader = unittest.TestLoader()
    suite = loader.discover(str(BASE / "tests"))
    runner = unittest.TextTestRunner(stream=open("/dev/null", "w"))
    result = runner.run(suite)
    n_pass = result.testsRun - len(result.failures) - len(result.errors)
    n_fail = len(result.failures) + len(result.errors)
    print(f"  {n_pass} passed, {n_fail} failed")
    
    # 3. Lean
    print("\n[3] Lean:")
    r2 = subprocess.run(
        ["lake", "build", "Sanskritree"],
        capture_output=True, text=True, cwd=BASE / "lean",
        env={"PATH": f"{Path.home()}/.elan/bin:{__import__('os').environ.get('PATH', '')}"}
    )
    lean_ok = r2.returncode == 0
    print(f"  Compiles: {lean_ok}")
    lean_modules = sorted(f.name for f in (BASE / "lean" / "Sanskritree").glob("*.lean"))
    for m in lean_modules:
        print(f"    {m}")
    
    # 4. Coverage
    print("\n[4] Coverage:")
    for wid, title in conn.execute("SELECT work_id, canonical_title FROM works").fetchall():
        total = conn.execute("""SELECT count(*) FROM token_occurrence tocc
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            WHERE pr.passage_id IN (SELECT passage_id FROM passages WHERE work_id=?)""", (wid,)).fetchone()[0]
        covered = conn.execute("""SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            LEFT JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
            WHERE tocc.passage_reading_id IN (SELECT reading_id FROM passage_readings WHERE passage_id IN
                (SELECT passage_id FROM passages WHERE work_id=?))
            AND mat.lexeme_id != 'lex_unknown'""", (wid,)).fetchone()[0]
        if total > 0:
            print(f"  {title[:50]:50s} {covered:4d}/{total:4d} ({covered/max(total,1)*100:.0f}%)")
    
    # 5. Adjudications
    n_adj = conn.execute("SELECT count(*) FROM adjudication_decisions").fetchone()[0]
    n_sessions = conn.execute("SELECT count(*) FROM adjudication_sessions").fetchone()[0]
    print(f"\n[5] Adjudications: {n_adj} decisions, {n_sessions} sessions")
    
    # 6. Engines
    print("\n[6] Engine distribution:")
    for r in conn.execute("""SELECT tah.engine, count(*) FROM token_analysis_hypothesis tah
        GROUP BY tah.engine ORDER BY count(*) DESC""").fetchall():
        print(f"  {r[0]:25s} {r[1]}")
    
    # 7. DB size
    db_size = Path(DB).stat().st_size
    print(f"\n[7] DB: {db_size / 1e6:.0f} MB")
    
    # 8. Source hashes
    print("\n[8] Key file hashes (SHA-256):")
    key_files = [
        "src/sanskritree/inference/factor_graph.py",
        "src/sanskritree/inference/factors.py",
        "src/sanskritree/inference/propagation.py",
        "src/sanskritree/inference/scoring.py",
        "src/sanskritree/translation/alignments.py",
        "src/sanskritree/translation/realization.py",
        "src/sanskritree/translation/evaluation.py",
        "migrations/0001_v2_foundation.sql",
        "migrations/0004_v2_graph_ontology.sql",
        "lean/Sanskritree/Decision.lean",
        "lean/Sanskritree/LayerB.lean",
        "tests/test_pipeline.py",
    ]
    for fp in key_files:
        p = BASE / fp
        if p.exists():
            h = hash_file(p)
            print(f"  {fp:45s} {h}")
    
    conn.close()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"RESEARCH KERNEL v0.1 — FREEZE REPORT")
    print(f"{'='*60}")
    print(f"Pass: {n_pass}/16 tests")
    print(f"Lean: {lean_ok} ({len(lean_modules)} modules)")
    print(f"Adjudications: {n_adj}")
    print(f"DB: {db_size / 1e6:.0f} MB")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
