"""Ingest Nyāya texts from downloaded GRETIL files into the DB.
Usage: PYTHONPATH=src python3 scripts/ingest_nyaya.py
"""
from __future__ import annotations
import json, re, yaml, uuid
from pathlib import Path

BASE = Path(__file__).parents[1]
import sys
sys.path.insert(0, str(BASE / "src"))
from sanskritree.database import connect
from sanskritree.corpus.ingestion import ingest_manifest

DB = str(BASE / "data" / "sanskritree-v2.db")


def parse_nyayasutra(text: str) -> list[dict]:
    """Parse Nyāyasūtra GRETIL text (format: 1.1.1: sutra text)."""
    passages = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Match: book.Chapter.sutraNumber: text
        m = re.match(r'^(\d+)\.(\d+)\.(\d+)[:;]\s*(.*)', line)
        if m:
            book, chapter, sutra, content = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
            pid = f"ns.{book}.{chapter}.{sutra}"
            passages.append({
                "id": pid,
                "chapter": str(chapter),
                "section": str(book),
                "verse": str(sutra),
                "type": "sutra",
                "transliteration": "IAST",
                "critical_status": "gretil_import",
                "sanskrit": content,
            })
    return passages


def parse_nyayabindu(text: str) -> list[dict]:
    """Parse Nyāyabindu GRETIL text."""
    passages = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(\d+)\.(\d+)[:;]\s*(.*)', line)
        if m:
            chapter, verse, content = int(m.group(1)), int(m.group(2)), m.group(3)
            pid = f"nb.{chapter}.{verse}"
            passages.append({
                "id": pid,
                "chapter": str(chapter),
                "verse": str(verse),
                "type": "sutra",
                "transliteration": "IAST",
                "critical_status": "gretil_import",
                "sanskrit": content,
            })
    return passages


def build_manifest(work_id, title, tradition, genre, passages, url):
    return {
        "work": {
            "id": work_id,
            "title": title,
            "tradition": tradition,
            "genre": genre,
            "metadata": {"source": "GRETIL", "url": url},
        },
        "edition": {
            "id": f"{work_id}.gretil",
            "editor": "GRETIL e-text",
            "publication": "Göttingen Register of Electronic Texts",
            "licence": "CC-BY-SA (GRETIL)",
            "critical_method": "GRETIL IAST e-text; unreviewed import",
        },
        "passages": passages,
    }


def main():
    sources = [
        ("sources/gretil_nyayasutra.txt", "nyayasutra", "Nyāyasūtra (Gautama)", "nyaya", "sutra",
         "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_gautama-nyAyasUtra.txt",
         parse_nyayasutra),
        ("sources/gretil_nyayabindu.txt", "nyayabindu", "Nyāyabindu (Dharmakīrti)", "buddhist", "sastra",
         "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_dharmakIrti-nyAyabindu.txt",
         parse_nyayabindu),
    ]

    conn = connect(DB)

    for filepath, wid, title, tradition, genre, url, parser in sources:
        path = BASE / filepath
        if not path.exists():
            print(f"❌ {filepath} not found — download first")
            continue

        text = path.read_text(encoding="utf-8")
        # Strip GRETIL header (everything before first sutra match)
        body = text.split("1.1.1:")[0] if "1.1.1:" in text else text
        # Better: find first sutra line
        lines = text.split("\n")
        content_start = 0
        for i, line in enumerate(lines):
            if re.match(r'^\d+\.\d+\.\d+:', line) or re.match(r'^\d+\.\d+:', line):
                content_start = i
                break
        body = "\n".join(lines[content_start:])

        passages = parser(body)
        print(f"{wid}: {len(passages)} passages parsed")

        if not passages:
            print(f"  No passages parsed! First content lines:")
            for l in body.split("\n")[:5]:
                print(f"    {l[:80]}")
            continue

        manifest = build_manifest(wid, title, tradition, genre, passages, url)
        results = ingest_manifest(conn, manifest)
        print(f"  ✅ {len(results)} passages ingested")

        # Save manifest
        manifest_path = BASE / "data" / "manifests" / f"{wid}_gretil.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest, f, allow_unicode=True)
        print(f"  ✅ Manifest saved")

    conn.close()
    print("\nDone. Nyāya texts ingested.")


if __name__ == "__main__":
    main()
