#!/usr/bin/env python3
"""Concordance over the RAW tantric corpus.

Searches the raw Sanskrit e-texts (Muktabodha + local GRETIL) only.
It NEVER indexes our own translation files -- that is the anti-echo guard:
the corpus layer is primary evidence (the source language), separate from
the interpretation layer (our T1/T2/T3/C1 markdown).

Usage:
  python3 scripts/concordance.py khecarī
  python3 scripts/concordance.py khecarī krama kula   (multi-term)
  python3 scripts/concordance.py khecarī --context 3   (lines around)
  python3 scripts/concordance.py khecarī --texts kubjik  (filter by filename substring)
  python3 scripts/concordance.py khecarī --max 200      (cap hits per text)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIRS = [
    ROOT / "sources" / "muktabodha-lib",
    ROOT / "sources" / "gretil2",
    ROOT / "sources",
]
# Only .txt files; skip any file that is a translation (English anchors).
TRANSLATION_MARKERS = ("eng", "translation", "vision", "dipika", "ghosh",
                       "khemraj", "root.txt", "aphorisms", "rajatarangini")
# The Muktabodha header block is ~28 lines of description; skip it.
HEADER_SKIP = 28

# Transliteration normalization: collapse diacritics so 'khecarī' matches 'khecari'.
_DIACRITIC_MAP = {
    "ā": "a", "ī": "i", "ū": "u", "ṝ": "r", "ṛ": "r", "ṟ": "r",
    "e": "e", "o": "o", "ai": "ai", "au": "au",
    "kh": "kh", "gh": "gh", "ch": "ch", "jh": "jh", "ṭh": "th",
    "ḍh": "dh", "th": "th", "dh": "dh", "ph": "ph", "bh": "bh",
    "ṅ": "n", "ñ": "n", "ṇ": "n", "ṭ": "t", "ḍ": "d", "ṃ": "m",
    "ḥ": "h", "ś": "s", "ṣ": "s", "ṝ": "r", "ḷ": "l", "ḹ": "l",
    "ṣ": "s", "ś": "s", "ā": "a", "ī": "i", "ū": "u",
}


def normalize(token: str) -> str:
    """Strip diacritics + punctuation for matching. 'khecarī' == 'khecari'.

    Anusvāra (ṃ) before a consonant is normalized to the homorganic nasal,
    so 'gaṃgā' == 'gaṅgā' == 'ganga' (orthographic variants of one sound).
    """
    out = []
    i = 0
    while i < len(token):
        two = token[i:i + 2]
        if two in ("ai", "au", "kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh", "ṅ", "ñ", "ṇ", "ṭ", "ḍ", "ḥ", "ś", "ṣ"):
            out.append(_DIACRITIC_MAP.get(two, two))
            i += 2
            continue
        ch = token[i]
        if ch == "ṃ" and i + 1 < len(token):
            nxt = token[i + 1]
            # homorganic nasal of the following consonant
            if nxt in "kkgghṅ":
                ch = "ṅ"
            elif nxt in "ccjjhñ":
                ch = "ñ"
            elif nxt in "ṭṭḍḍhṇ":
                ch = "ṇ"
            elif nxt in "ttddhn":
                ch = "n"
            elif nxt in "ppbbhm":
                ch = "m"
        # final/standalone anusvāra == m (editions write cittaṃ ~ cittam)
        out.append("m" if ch == "ṃ" else _DIACRITIC_MAP.get(ch, ch))
        i += 1
    return "".join(out).lower()


INDEX_CACHE = ROOT / ".concordance_index.json"
INDEX_VERSION = 2


def iter_corpus() -> list[Path]:
    files: list[Path] = []
    for d in CORPUS_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.txt")):
            name = p.name.lower()
            if any(m in name for m in TRANSLATION_MARKERS):
                continue
            files.append(p)
    return files


def read_lines(path: Path) -> list[str]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    lines = raw.splitlines()
    if "MUKTABODHA" in raw.upper() or "CATALOG NUMBER" in raw.upper():
        lines = lines[HEADER_SKIP:]
    return [ln.rstrip() for ln in lines if ln.strip()]


def build_index() -> dict[str, dict[str, list[int]]]:
    """Cache normalized lines per file. format: {file: {norm_token: [line_no,...]}}"""
    files = iter_corpus()
    index: dict[str, dict[str, list[int]]] = {}
    for path in files:
        lines = read_lines(path)
        if not lines:
            continue
        tokens: dict[str, list[int]] = {}
        for idx, line in enumerate(lines):
            norm = normalize(line)
            if not norm:
                continue
            # Store the whole normalized line -> we search substrings of it.
            tokens.setdefault(norm, []).append(idx)
        index[path.name] = tokens
    return index


def load_index() -> dict[str, dict[str, list[int]]]:
    if INDEX_CACHE.exists():
        try:
            data = json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
            if data.get("version") == INDEX_VERSION:
                return data["index"]
        except Exception:
            pass
    index = build_index()
    INDEX_CACHE.write_text(
        json.dumps({"version": INDEX_VERSION, "index": index}, ensure_ascii=False),
        encoding="utf-8",
    )
    return index


def find_hits(index: dict[str, dict[str, list[int]]], norm_terms: list[str]) -> dict[str, list[int]]:
    """Return {file: [line_no, ...]} for lines containing any term."""
    per_file: dict[str, list[int]] = {}
    for fname, norm_lines in index.items():
        hits: set[int] = set()
        for norm_line, linenos in norm_lines.items():
            for t in norm_terms:
                if t in norm_line:
                    hits.update(linenos)
                    break
        if hits:
            per_file[fname] = sorted(hits)
    return per_file


def read_file_by_name(name: str) -> list[str]:
    for d in CORPUS_DIRS:
        p = d / name
        if p.exists():
            return read_lines(p)
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Raw-corpus concordance (never our translations).")
    ap.add_argument("terms", nargs="+", help="Sanskrit terms (IAST); diacritics optional")
    ap.add_argument("--context", type=int, default=1, help="context lines around each hit")
    ap.add_argument("--texts", default=None, help="only files whose name contains this substring")
    ap.add_argument("--max", type=int, default=100, help="cap hits shown per text (0 = all)")
    args = ap.parse_args()

    norm_terms = [normalize(t) for t in args.terms]
    index = load_index()

    # If --texts is given, restrict the index to matching files.
    if args.texts:
        index = {fname: v for fname, v in index.items() if args.texts.lower() in fname.lower()}

    print(f"# Concordance: {', '.join(args.terms)}")
    print(f"# Corpus: {len(index)} raw e-texts (Muktabodha + local GRETIL) — translations excluded\n")

    per_file = find_hits(index, norm_terms)
    grand_total = sum(len(v) for v in per_file.values())

    if not per_file:
        print("(no hits in the raw corpus)")
        return 1

    for fname, hits in sorted(per_file.items(), key=lambda x: -len(x[1])):
        lines = read_file_by_name(fname)
        shown = hits if args.max == 0 else hits[:args.max]
        print(f"## {fname}  —  {len(hits)} occurrence{'s' if len(hits) != 1 else ''}")
        for h in shown:
            lo = max(0, h - args.context)
            hi = min(len(lines), h + args.context + 1)
            hit_idx = h - lo
            for offset, ln in enumerate(lines[lo:hi]):
                marker = "→" if offset == hit_idx else " "
                print(f"   {fname}:{lo + offset + 1}  {marker} {ln.strip()}")
            print()
        if len(hits) > len(shown):
            print(f"   (... {len(hits) - len(shown)} more)\n")

    print(f"## TOTAL: {grand_total} occurrences across {len(per_file)} texts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
