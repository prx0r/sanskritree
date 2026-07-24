"""Activate V2 pipeline on MBT corpus — ingest, analyze, translate, build lexicon.

Usage: PYTHONPATH=src python3 scripts/v2_activate.py [--verses N] [--pilot-only]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import uuid
from pathlib import Path

import yaml

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect, migrate
from sanskritree.corpus.ingestion import ingest_manifest, load_manifest
from sanskritree.philology.adapters import analyze
from sanskritree.philology.analysis_lattice import persist_lattice
from sanskritree.translation.candidates import start_blind_run, record_candidate, reveal_reference


VERSES_FILE = BASE / "data" / "datasets" / "mbt_verses.jsonl"
ENGLISH_FILE = BASE / "data" / "datasets" / "mbt_page_aligned.jsonl"
MANIFEST_OUT = BASE / "data" / "manifests" / "mbt_v2_pilot.yaml"
DB_PATH = BASE / "data" / "sanskritree-v2.db"


def load_verses(max_verses: int | None = None) -> list[dict]:
    verses = []
    with open(VERSES_FILE) as f:
        for line in f:
            v = json.loads(line)
            if v.get("verse_number") is not None:
                verses.append(v)
    if max_verses:
        verses = verses[:max_verses]
    return verses


def load_english_map() -> dict[int, str]:
    mapping = {}
    with open(ENGLISH_FILE) as f:
        for line in f:
            entry = json.loads(line)
            mapping[entry["sanskrit_page"]] = entry.get("english", "")
    return mapping


def clean_ocr_artifacts(text: str) -> str:
    text = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', '', text)
    text = text.replace('"', '').replace('"', '').replace("'", '').replace('"', '')
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_manifest(verses: list[dict], english_map: dict[int, str]) -> dict:
    passages = []
    for v in verses:
        pid = f"mbt.v{v['chapter'] or 'x'}.{v['verse_number'] or 'x'}.{uuid.uuid4().hex[:4]}"
        page = v.get("source_page", 0)
        sa_text = clean_ocr_artifacts(v["sanskrit"])
        en_text = clean_ocr_artifacts(english_map.get(page, ""))

        passage = {
            "id": pid,
            "chapter": str(v["chapter"]) if v["chapter"] else "",
            "verse": str(v["verse_number"]) if v["verse_number"] else "",
            "type": "verse",
            "transliteration": "Devanagari",
            "critical_status": "vision_ocr_unreviewed",
            "source_page": str(page),
            "sanskrit": sa_text,
        }

        if en_text:
            passage["translations"] = [{
                "id": f"{pid}.en.dyczkowski",
                "translator_id": "dyczkowski.mark",
                "translator": "Mark S. G. Dyczkowski",
                "type": "published_translation",
                "language": "en",
                "text": en_text,
                "source_page": str(page + 1),
            }]

        passages.append(passage)

    return {
        "work": {
            "id": "mbt_kumarikakhanda",
            "title": "Manthānabhairavatantram — Kumārikākhaṇḍaḥ",
            "title_iast": "Manthānabhairavatantram — Kumārikākhaṇḍaḥ",
            "author": "Mark S. G. Dyczkowski (ed.)",
            "tradition": "kubjika",
            "genre": "tantra",
            "metadata": {
                "pilot_role": "v2_activation_seed",
                "source_file": "Manthānabhairavatantram IGNCA ed.",
                "ocr_engine": "google_vision_document_text_detection",
                "verses_selected": len(passages),
            },
        },
        "edition": {
            "id": "dyczkowski.2009.ignca",
            "editor": "Mark S. G. Dyczkowski",
            "publication": "Indira Gandhi National Centre for the Arts, New Delhi",
            "year": 2009,
            "isbn": "9788124604984",
            "licence": "locally supplied commercial scan; not for redistribution",
            "critical_method": "Google Vision API OCR from rendered page images; unreviewed import",
        },
        "passages": passages,
    }


def step1_ingest(conn, manifest: dict) -> list:
    print(f"Ingesting {len(manifest['passages'])} passages...")
    results = ingest_manifest(conn, manifest)
    print(f"  Done: {len(results)} passages ingested")
    print(f"  Works: {conn.execute('SELECT count(*) FROM works').fetchone()[0]}")
    print(f"  Editions: {conn.execute('SELECT count(*) FROM editions').fetchone()[0]}")
    print(f"  Passages: {conn.execute('SELECT count(*) FROM passages').fetchone()[0]}")
    print(f"  Readings: {conn.execute('SELECT count(*) FROM passage_readings').fetchone()[0]}")
    print(f"  Translations: {conn.execute('SELECT count(*) FROM translations').fetchone()[0]}")
    return results


def step2_analyze(conn, manifest: dict, engines: list[str] | None = None):
    if engines is None:
        engines = ["fallback"]
    print(f"Analyzing with engines: {engines}")

    readings = conn.execute(
        "SELECT reading_id, sanskrit_normalized FROM passage_readings ORDER BY reading_id"
    ).fetchall()

    count = 0
    for rid, text in readings:
        if not text or len(text) < 5:
            continue
        lattice = analyze(text, engines)
        n = persist_lattice(conn, rid, lattice)
        count += n
        if count % 100 == 0:
            print(f"  ... {count} analyses persisted")

    total = conn.execute("SELECT count(*) FROM token_analyses").fetchone()[0]
    print(f"  Total token analyses: {total}")


def step3_blind_translate(conn, manifest: dict, n_samples: int = 5):
    """Blind translation pilot: generate candidates without seeing published translation."""
    print(f"Blind translation pilot ({n_samples} samples)...")

    passages = manifest["passages"][:n_samples]
    for i, p in enumerate(passages):
        pid = p["id"]
        sa_text = p["sanskrit"]

        run_id = start_blind_run(
            conn, pid,
            profiles=["literal", "idiomatic", "commentarial"],
            retrieval_results=[{"source": "vision_ocr", "text_preview": sa_text[:50]}],
            prompt_version="v2-pilot",
        )
        print(f"  [{i+1}/{n_samples}] {pid}: run={run_id[:8]}...")

    print(f"  Total blind runs: {conn.execute('SELECT count(*) FROM translation_runs').fetchone()[0]}")
    print("  Published translations retained as reference; not yet revealed.")


def step4_lexicon_stats(conn):
    """Extract lexicon from ingested data."""
    # Count distinct lemmas from analyses
    analyses = conn.execute(
        "SELECT lemma, count(*) as cnt FROM token_analyses WHERE lemma IS NOT NULL GROUP BY lemma ORDER BY cnt DESC LIMIT 20"
    ).fetchall()
    print(f"\nTop lemmas by frequency:")
    for lemma, cnt in analyses[:10]:
        print(f"  {lemma}: {cnt}")

    total = conn.execute("SELECT count(*) FROM token_analyses").fetchone()[0]
    unique = conn.execute("SELECT count(DISTINCT lemma) FROM token_analyses WHERE lemma IS NOT NULL").fetchone()[0]
    print(f"  Total analyses: {total}")
    print(f"  Unique lemmas: {unique}")


def main():
    parser = argparse.ArgumentParser(description="V2 pipeline activation")
    parser.add_argument("--verses", type=int, default=100, help="Number of verses to process")
    parser.add_argument("--analyze", action="store_true", help="Run morphology analysis")
    parser.add_argument("--blind", action="store_true", help="Run blind translation pilot")
    parser.add_argument("--all", action="store_true", help="Full activation: ingest + analyze + blind")
    args = parser.parse_args()

    if not any([args.analyze, args.blind, args.all]):
        args.all = True

    print("=" * 60)
    print("SANSKRITREE V2 PIPELINE ACTIVATION")
    print("=" * 60)

    # Step 0: Build manifest
    print("\n[0] Building manifest from verse data...")
    verses = load_verses(args.verses)
    print(f"  Loaded {len(verses)} numbered verses")
    english_map = load_english_map()
    print(f"  Loaded {len(english_map)} English page mappings")
    manifest = build_manifest(verses, english_map)
    with open(MANIFEST_OUT, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Manifest saved: {MANIFEST_OUT}")

    # Connect to V2 database
    conn = connect(DB_PATH)
    migrate(conn, BASE / "migrations")

    if args.all or True:  # ingest is always needed
        step1_ingest(conn, manifest)

    if args.analyze or args.all:
        step2_analyze(conn, manifest)

    if args.blind or args.all:
        step3_blind_translate(conn, manifest)

    if args.all:
        step4_lexicon_stats(conn)

    conn.close()
    print(f"\nV2 database: {DB_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
