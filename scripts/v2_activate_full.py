"""Full V2 activation: ingest all MBT verses, run Vidyut morphology, blind translation, lexicon."""
from __future__ import annotations

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
from sanskritree.corpus.ingestion import ingest_manifest
from sanskritree.philology.adapters import analyze
from sanskritree.philology.analysis_lattice import persist_lattice
from sanskritree.translation.candidates import start_blind_run

VERSES_FILE = BASE / "data" / "datasets" / "mbt_verses.jsonl"
ENGLISH_FILE = BASE / "data" / "datasets" / "mbt_page_aligned.jsonl"
MANIFEST_OUT = BASE / "data" / "manifests" / "mbt_v2_full.yaml"
DB_PATH = BASE / "data" / "sanskritree-v2.db"


def load_verses(max_verses: int | None = None) -> list[dict]:
    verses = []
    with open(VERSES_FILE) as f:
        for line in f:
            v = json.loads(line)
            if v.get("verse_number") is not None:
                verses.append(v)
    return verses[:max_verses] if max_verses else verses


def load_english_map() -> dict[int, str]:
    mapping = {}
    with open(ENGLISH_FILE) as f:
        for line in f:
            entry = json.loads(line)
            mapping[entry["sanskrit_page"]] = entry.get("english", "")
    return mapping


def clean(text: str) -> str:
    text = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', '', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_manifest(verses, english_map):
    passages = []
    for v in verses:
        pid = f"mbt.v{v['chapter']}.{v['verse_number']}.{uuid.uuid4().hex[:4]}"
        page = v.get("source_page", 0)
        sa_text = clean(v["sanskrit"])
        en_text = clean(english_map.get(page, ""))

        passage = {
            "id": pid,
            "chapter": str(v["chapter"]),
            "verse": str(v["verse_number"]),
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
            "metadata": {"pilot_role": "v2_full_activation", "ocr_engine": "google_vision"},
        },
        "edition": {
            "id": "dyczkowski.2009.ignca",
            "editor": "Mark S. G. Dyczkowski",
            "publication": "Indira Gandhi National Centre for the Arts",
            "year": 2009,
            "isbn": "9788124604984",
            "licence": "locally supplied; not for redistribution",
            "critical_method": "Google Vision OCR; unreviewed",
        },
        "passages": passages,
    }


def main():
    print("=" * 60)
    print("V2 FULL ACTIVATION — MBT Kumārikākhaṇḍa")
    print("=" * 60)

    print("\n[1] Building manifest...")
    verses = load_verses()
    print(f"  {len(verses)} numbered verses")
    english_map = load_english_map()
    manifest = build_manifest(verses, english_map)
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_OUT, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Manifest: {MANIFEST_OUT}")

    print("\n[2] Ingesting into V2 database...")
    conn = connect(DB_PATH)
    migrate(conn, BASE / "migrations")
    results = ingest_manifest(conn, manifest)
    print(f"  {len(results)} passages ingested")
    for table in ["works", "editions", "passages", "passage_readings", "translations"]:
        n = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n}")

    print("\n[3] Running morphology (Vidyut engine)...")
    readings = conn.execute(
        "SELECT reading_id, sanskrit_normalized FROM passage_readings WHERE sanskrit_normalized != '' ORDER BY reading_id"
    ).fetchall()
    print(f"  {len(readings)} readings to analyze")

    total_analyses = 0
    for i, (rid, text) in enumerate(readings):
        if not text or len(text) < 5:
            continue
        lattice = analyze(text, ["vidyut", "fallback"])
        n = persist_lattice(conn, rid, lattice)
        total_analyses += n
        if (i + 1) % 200 == 0:
            print(f"  [{i+1}/{len(readings)}] {total_analyses} analyses so far")

    stats = conn.execute("""
        SELECT engine, count(*) as cnt, count(DISTINCT lemma) as lemmas
        FROM token_analyses GROUP BY engine
    """).fetchall()
    for engine, cnt, lemmas in stats:
        print(f"  {engine}: {cnt} analyses, {lemmas} unique lemmas")

    print("\n[4] Blind translation runs...")
    sample = manifest["passages"][:20]
    for i, p in enumerate(sample):
        run_id = start_blind_run(
            conn, p["id"],
            profiles=["literal", "idiomatic"],
            retrieval_results=[{"source": "vision_ocr", "preview": p["sanskrit"][:60]}],
            prompt_version="v2-full",
        )
    n_runs = conn.execute("SELECT count(*) FROM translation_runs").fetchone()[0]
    print(f"  {n_runs} blind runs created")

    print("\n[5] Lexicon extraction...")
    top = conn.execute("""
        SELECT lemma, count(*) as cnt
        FROM token_analyses
        WHERE lemma IS NOT NULL AND lemma != ''
        GROUP BY lemma ORDER BY cnt DESC LIMIT 30
    """).fetchall()
    print(f"  Top lemmas:")
    for lemma, cnt in top:
        print(f"    {lemma}: {cnt}")

    unique_lemmas = conn.execute(
        "SELECT count(DISTINCT lemma) FROM token_analyses WHERE lemma IS NOT NULL AND lemma != ''"
    ).fetchone()[0]
    print(f"  Total unique lemmas: {unique_lemmas}")

    conn.close()
    print(f"\nV2 DB: {DB_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
