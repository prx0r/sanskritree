#!/usr/bin/env python3
"""audit_t1.py — FoJin-style claim guard over our T1 translation files.

For every Sanskrit token in a T1 file's SOURCE lines (the raw text before the
`>` translation arrows), look it up in the raw-corpus concordance index and
report a trust state:

  verified    - token occurs in the raw corpus
  not-found   - token occurs in ZERO raw-corpus texts
                (transcription suspect, our emendation, or an over-claim)
  [X]-flagged - token appears inside a bracketed [X] marker (known doubt)

The audit is a whitelist guard: a translation may only *use* a token that the
corpus actually contains. It never reads our own translations as evidence
(anti-echo); the corpus is the referee.

Usage:
  python3 scripts/audit_t1.py translations/01_t1_working/jnanakarika_patalas2-3_completion_pass1.md
  python3 scripts/audit_t1.py translations/01_t1_working/*.md      (all files)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_CACHE = ROOT / ".concordance_index.json"
INDEX_VERSION = 2

# Tokens that are scaffolding, not Sanskrit; never flagged.
STOP = {
    "om", "svaha", "iti", "atha", "nama", "ca", "tu", "na", "yad", "tat",
    "evam", "atha", "tatha", "sad", "parama", "sarva", "vai", "evam",
    "hi", "kim", "idam", "yatra", "tatra", "asyam", "ity", "yad", "tad",
    "bhavet", "syat", "katham", "yena", "yatraiva",
}

_READER = __import__("importlib").import_module("concordance") if False else None


def normalize(token: str) -> str:
    # Mirror concordance.normalize without importing (avoid .pyc coupling).
    _DM = {
        "ā": "a", "ī": "i", "ū": "u", "ṛ": "r", "ṝ": "r", "ṟ": "r",
        "e": "e", "o": "o", "ai": "ai", "au": "au",
        "ṅ": "n", "ñ": "n", "ṇ": "n", "ṭ": "t", "ḍ": "d", "ḥ": "h",
        "ś": "s", "ṣ": "s", "ḷ": "l", "ḹ": "l",
    }
    out = []
    i = 0
    while i < len(token):
        two = token[i:i + 2]
        if two in ("ai", "au", "kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh", "ṅ", "ñ", "ṇ", "ṭ", "ḍ", "ḥ", "ś", "ṣ"):
            out.append(_DM.get(two, two))
            i += 2
            continue
        ch = token[i]
        if ch == "ṃ" and i + 1 < len(token):
            nxt = token[i + 1]
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
        out.append("m" if ch == "ṃ" else _DM.get(ch, ch))
        i += 1
    return "".join(out).lower()


def load_index() -> dict[str, dict[str, list[int]]]:
    if not INDEX_CACHE.exists():
        print("(no index — run concordance.py once to build it)")
        sys.exit(1)
    data = json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
    if data.get("version") != INDEX_VERSION:
        print("(stale index — delete .concordance_index.json and rebuild)")
        sys.exit(1)
    return data["index"]


def extract_tokens(path: Path) -> tuple[dict[str, int], dict[str, int], set[str]]:
    """Return {token: count} for SOURCE-line tokens, {token: count} for [X]-tokens,
    and the set of raw tokens seen."""
    src_tokens: dict[str, int] = {}
    x_tokens: dict[str, int] = {}
    raw_seen: set[str] = set()
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        # A SOURCE line: the line immediately before a '>' translation arrow.
        if i + 1 < len(lines) and lines[i + 1].lstrip().startswith(">"):
            for tok in re.findall(r"[a-zA-Zāīūṛṝṅñṇṭḍśṣṃḥḷ]+", line):
                raw_seen.add(tok)
                if tok.lower() in STOP:
                    continue
                src_tokens.setdefault(tok, 0)
                src_tokens[tok] += 1
        # [X: ...] markers on any line
        for xm in re.findall(r"\[X:\s*([^\]]+)\]", line):
            for tok in re.findall(r"[a-zA-Zāīūṛṝṅñṇṭḍśṣṃḥḷ]+", xm):
                if tok.lower() in STOP:
                    continue
                x_tokens.setdefault(tok, 0)
                x_tokens[tok] += 1
    return src_tokens, x_tokens, raw_seen


def corpus_span(index: dict[str, dict[str, list[int]]], norm: str) -> int:
    """Number of corpus texts containing the normalized token."""
    count = 0
    for fname, lines in index.items():
        for norm_line in lines:
            if norm in norm_line:
                count += 1
                break
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="FoJin-style claim guard over T1 files.")
    ap.add_argument("files", nargs="+", help="T1 markdown files to audit")
    ap.add_argument("--min-freq", type=int, default=2, help="only report tokens seen N+ times")
    args = ap.parse_args()

    index = load_index()

    for path in sorted({Path(f) for f in args.files}):
        if not path.exists():
            print(f"[MISSING] {path}")
            continue
        src_tokens, x_tokens, raw_seen = extract_tokens(path)

        # Resolve each raw token to its normalized form (with anusvara homorganic fix)
        results: list[tuple[str, str, int, int]] = []  # raw, norm, src_count, corpus_texts
        for raw, count in src_tokens.items():
            norm = normalize(raw)
            texts = corpus_span(index, norm)
            results.append((raw, norm, count, texts))

        not_found = [r for r in results if r[3] == 0]
        verified = [r for r in results if r[3] > 0]

        print(f"# {path.name}")
        print(f"  source tokens: {len(results)} | verified: {len(verified)} | "
              f"not-found: {len(not_found)} | [X]-tokens: {len(x_tokens)}")
        if not_found:
            print("\n  NOT-FOUND in raw corpus (check these):")
            for raw, norm, count, texts in sorted(not_found, key=lambda r: -r[2]):
                flag = " [X]" if raw in x_tokens or any(raw in t for t in x_tokens) else ""
                print(f"    {raw}  (x{count}){flag}")
        if verified:
            print(f"\n  verified (top 15 by source frequency):")
            for raw, norm, count, texts in sorted(verified, key=lambda r: -r[2])[:15]:
                print(f"    {raw}  (x{count}, in {texts} corpus texts)")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
