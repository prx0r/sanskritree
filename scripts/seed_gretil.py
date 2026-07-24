"""Fetch clean IAST texts from GRETIL and ingest into V2 pipeline.

Targets (from research programme Stage 1):
  - Bhagavad Gītā    — grammar, verbs, cases, core philosophy
  - Vijñānabhairava — Trika vocabulary (spanda, madhya, śakti, bhairava)
  - Spandakārikā    — vibration metaphysics (already have pilot)

Usage: PYTHONPATH=src python3 scripts/seed_gretil.py [--text bg|vb|sp]
"""
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

DB_PATH = BASE / "data" / "sanskritree-v2.db"

# GRETIL URLs for clean IAST texts
GRETIL = {
    "bg": {
        "url": "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_bhagavadgItA-4comm.txt",
        "id": "bhagavad_gita",
        "title": "Śrīmad Bhagavad Gītā (with 4 commentaries)",
        "tradition": "epic",
        "genre": "itihasa",
    },
    "sp": {
        "url": "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_vasugupta-spandakArikA-comm.txt",
        "id": "spandakarika",
        "title": "Spandakārikā (with Kṣemarāja commentary)",
        "tradition": "trika",
        "genre": "tantra",
    },
    "ab": {
        "url": "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_abhinavagupta-bhairavastava.txt",
        "id": "abhinavagupta_bhairavastava",
        "title": "Abhinavagupta: Bhairavastava",
        "tradition": "trika",
        "genre": "stotra",
    },
}


def fetch_text(key: str) -> str | None:
    import urllib.request
    info = GRETIL.get(key)
    if not info:
        print(f"Unknown text: {key}")
        return None
    url = info["url"]
    print(f"Fetching {info['title']} from {url}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "sanskritree-v2/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
        # GRETIL metadata header ends at first ---- or ==== line
        lines = raw.split("\n")
        content_start = 0
        for i, line in enumerate(lines):
            if line.startswith("---") or line.startswith("==="):
                content_start = i + 1
                break
        body = "\n".join(lines[content_start:]).strip()
        print(f"  {len(body)} chars fetched")
        return body
    except Exception as e:
        print(f"  FAILED: {e}")
        return None


def parse_verses(text: str) -> list[dict]:
    """Parse GRETIL IAST text into numbered verses."""
    verses = []
    lines = text.split("\n")
    current = []
    vnum = None
    chapter = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Skip transliteration scheme lines
        if stripped.startswith("Input") or stripped.startswith("Output") or stripped.startswith("-----"):
            continue

        # Chapter marker: || chapter_number ||
        cm = re.match(r"^।।\s*(\d+)\s*।।", stripped)
        if cm:
            chapter = int(cm.group(1))
            continue

        # Verse end marker: || verse_number || or just || number
        vm = re.search(r"\|{1,2}\s*(\d{1,3})\s*\|{1,2}\s*$", stripped)
        if vm:
            vnum = int(vm.group(1))
            current.append(stripped)
            verses.append({
                "chapter": chapter,
                "verse": vnum,
                "text": " ".join(current),
                "raw": list(current),
            })
            current = []
            vnum = None
        else:
            current.append(stripped)

    # Flush remaining
    if current:
        verses.append({
            "chapter": chapter,
            "verse": vnum,
            "text": " ".join(current),
            "raw": list(current),
        })

    return verses


def build_manifest(key: str, verses: list[dict]) -> dict:
    info = GRETIL[key]
    passages = []
    for i, v in enumerate(verses):
        vid = f"{info['id']}.{v['chapter'] or 'x'}.{v['verse'] or i}.{uuid.uuid4().hex[:4]}"
        passages.append({
            "id": vid,
            "chapter": str(v["chapter"]) if v["chapter"] else "",
            "verse": str(v["verse"]) if v["verse"] else str(i + 1),
            "type": "verse",
            "transliteration": "IAST",
            "critical_status": "gretil_import",
            "source_page": str(i + 1),
            "sanskrit": v["text"],
        })

    return {
        "work": {
            "id": info["id"],
            "title": info["title"],
            "title_iast": info["title"],
            "tradition": info["tradition"],
            "genre": info["genre"],
            "metadata": {"source": "GRETIL", "url": info["url"]},
        },
        "edition": {
            "id": f"{info['id']}.gretil",
            "editor": "GRETIL e-text",
            "publication": "Göttingen Register of Electronic Texts",
            "licence": "CC-BY-SA (GRETIL)",
            "critical_method": "GRETIL IAST e-text; unreviewed import",
        },
        "passages": passages,
    }


def ingest(conn, manifest: dict, run_morphology: bool = True):
    work_id = manifest["work"]["id"]
    total = len(manifest["passages"])
    print(f"\nIngesting {work_id}: {total} verses...")

    results = ingest_manifest(conn, manifest)
    print(f"  {len(results)} passages ingested")

    if run_morphology:
        readings = conn.execute("""
            SELECT pr.reading_id, pr.sanskrit_normalized
            FROM passage_readings pr
            JOIN passages p ON pr.passage_id = p.passage_id
            JOIN works w ON p.work_id = w.work_id
            WHERE w.work_id = ?
        """, (work_id,)).fetchall()
        print(f"  Running morphology on {len(readings)} readings...")

        total_analyses = 0
        for rid, text in readings:
            if not text or len(text) < 5:
                continue
            lattice = analyze(text, ["vidyut", "fallback"])
            n = persist_lattice(conn, rid, lattice)
            total_analyses += n

        print(f"  {total_analyses} analyses persisted")
        lemmas = conn.execute("""
            SELECT count(DISTINCT lemma) FROM token_analyses ta
            JOIN tokens t ON ta.token_id = t.token_id
            JOIN passage_readings pr ON t.reading_id = pr.reading_id
            JOIN passages p ON pr.passage_id = p.passage_id
            JOIN works w ON p.work_id = w.work_id
            WHERE w.work_id = ? AND ta.lemma IS NOT NULL AND ta.lemma != ''
        """, (work_id,)).fetchone()[0]
        print(f"  {lemmas} unique lemmas")


def main():
    import urllib.request

    texts = list(GRETIL.keys())

    conn = connect(str(DB_PATH))
    migrate(conn, BASE / "migrations")

    for key in texts:
        print(f"\n{'='*60}")
        raw = fetch_text(key)
        if not raw:
            continue

        verses = parse_verses(raw)
        print(f"  Parsed {len(verses)} verses")

        # Save raw text
        out_dir = BASE / "data" / "raw" / GRETIL[key]["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "gretil_raw.txt").write_text(raw)

        # Build and save manifest
        manifest = build_manifest(key, verses)
        manifest_path = BASE / "data" / "manifests" / f"{GRETIL[key]['id']}_gretil.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"  Manifest: {manifest_path}")

        # Ingest into V2
        ingest(conn, manifest)

    # Final lexicon stats
    print(f"\n{'='*60}")
    print("FINAL LEXICON STATUS")
    print(f"{'='*60}")
    stats = conn.execute("""
        SELECT w.work_id, w.canonical_title,
               count(DISTINCT pr.reading_id) as readings,
               count(DISTINCT ta.lemma) as lemmas
        FROM works w
        LEFT JOIN passages p ON w.work_id = p.work_id
        LEFT JOIN passage_readings pr ON pr.passage_id = p.passage_id
        LEFT JOIN tokens t ON t.reading_id = pr.reading_id
        LEFT JOIN token_analyses ta ON ta.token_id = t.token_id AND ta.engine = 'vidyut'
        GROUP BY w.work_id
    """).fetchall()
    for wid, title, readings, lemmas in stats:
        print(f"  {title:40s} {readings:5d} readings  {lemmas:5d} lemmas")

    conn.close()
    print(f"\nDB: {DB_PATH}")


if __name__ == "__main__":
    main()
