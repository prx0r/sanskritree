"""Build a Sanskrit-English aligned dataset from MBT OCR results.

Sanskrit pages (even, Khalnayak font) were OCR'd via Vision API.
English pages (odd, SanskritTimes font) extract from text layer.

Produces:
  - data/datasets/mbt_page_aligned.jsonl    — page-level pairs
  - data/datasets/mbt_verses.jsonl           — verse-level Sanskrit with metadata
  - data/datasets/mbt_parallel.jsonl         — verse-level Sanskrit-English (where alignable)
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from collections import OrderedDict

import fitz
import yaml

BASE = Path(__file__).parents[1]
SOURCES = BASE / "sources"
OCR_STATE = BASE / "data" / "ocr" / "mbt_ocr_full_state.json"
DATASET_DIR = BASE / "data" / "datasets"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

MBT_FILE = list(SOURCES.glob("Manthānabhairavatantram _*"))[0]


def load_ocr_results() -> dict:
    data = json.loads(OCR_STATE.read_text())
    return data.get("results", {})


def get_english_pages(pdf_path: str) -> dict[int, str]:
    """Extract English text from non-Khalnayak pages via text layer."""
    doc = fitz.open(pdf_path)
    pages = {}
    for pn in range(len(doc)):
        fonts = doc[pn].get_fonts()
        has_khal = any("Khalnayak" in f[3] for f in fonts)
        if not has_khal:
            text = doc[pn].get_text("text").strip()
            if len(text) > 50:
                pages[pn + 1] = text
    doc.close()
    return pages


def extract_verses(sanskrit_text: str) -> list[dict]:
    """Extract individual verses from Devanāgarī OCR text.

    True verse markers are:  ॥ NUMBER ॥  (with double danda around the number).
    Standalone numbers (footnotes) are ignored.
    """
    verses = []
    lines = sanskrit_text.split("\n")
    current_verse = []
    verse_started = False

    # True verse marker: danda, optional space, digits, optional space, danda
    verse_end_re = re.compile(r"[॥।]\s*(\d{1,3})\s*[॥।]")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Skip lines that are ONLY numbers (footnote markers)
        if re.match(r"^[\d\s•··°\-\–—]+$", stripped):
            continue

        # Check for true verse-ending marker
        end_match = verse_end_re.search(stripped)
        if end_match:
            current_verse.append(stripped)
            vnum = int(end_match.group(1))
            # Only accept reasonable verse numbers (1-999)
            if 1 <= vnum <= 999:
                verses.append({
                    "verse_number": vnum,
                    "text": " ".join(current_verse),
                    "raw_lines": list(current_verse),
                })
                current_verse = []
                verse_started = False
                continue

        # Check if this line looks like verse content
        has_deva = any('\u0900' <= c <= '\u097F' for c in stripped)
        if has_deva:
            current_verse.append(stripped)
            verse_started = True
        elif verse_started and len(stripped) > 10:
            current_verse.append(stripped)

    # Flush remaining
    if current_verse and verse_started:
        verses.append({
            "verse_number": None,
            "text": " ".join(current_verse),
            "raw_lines": list(current_verse),
        })

    return verses


def clean_devanagari(text: str) -> str:
    """Clean common OCR artifacts from Devanāgarī text."""
    text = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', '', text)
    text = text.replace('"', '').replace('*', '').replace('_', '')
    text = text.replace('"', '').replace("'", '')
    # Remove footnote number lines embedded in verses
    text = re.sub(r'\b\d{2,3}\b', '', text)
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def detect_chapter(text: str) -> int | None:
    """Detect chapter number from Sanskrit text."""
    m = re.search(r"[ऽ॰ॐ]?\s*([क-ह])[व्य]?[तन]?[मय]?[०-९]+\s*[अआ]?[नन]?[दध]?[:ः]?", text[:100])
    # Look for patterns like प्रथमानन्दः, द्वितीयानन्दः
    chapter_map = {
        r"प्रथम": 1, r"द्वितीय": 2, r"तृतीय": 3, r"चतुर्थ": 4,
        r"पञ्चम": 5, r"षष्ठ": 6, r"सप्तम": 7, r"अष्टम": 8,
        r"नवम": 9, r"दशम": 10,
    }
    for pat, num in chapter_map.items():
        if re.search(pat, text[:200]):
            return num
    return None


def clean_devanagari(text: str) -> str:
    """Clean common OCR artifacts from Devanāgarī text."""
    # Remove superscript footnote numbers (HTML-style)
    text = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', '', text)
    # Remove stray HTML/XML artifacts
    text = text.replace('"', '').replace('*', '').replace('_', '')
    # Normalize unicode
    text = unicodedata.normalize('NFC', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def clean_english(text: str) -> str:
    """Clean English text extracted from PDF."""
    # Fix common PDF extraction artifacts
    text = text.replace('\u00ce', 'r')  # Î → r (vṛtta)
    text = text.replace('\u00d1', 'n')  # Ñ → n (maṇḍala)
    text = text.replace('\u00de', 'th')  # Þ → th
    text = text.replace('æ', 'ae')
    text = text.replace('\u0160', 'S')  # Š → S
    text = text.replace('\u00d0', 'D')  # Ð → D
    text = text.replace('\u00f0', 'd')
    text = text.replace('\u00fe', 't')
    text = text.replace('\u00e6', 'ae')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def main():
    print("Loading OCR results...")
    sanskrit_results = load_ocr_results()
    sanskrit_pages = {int(k): v for k, v in sanskrit_results.items()}
    print(f"  Sanskrit pages: {len(sanskrit_pages)}")

    print("Extracting English pages from PDF text layer...")
    english_pages = get_english_pages(str(MBT_FILE))
    print(f"  English pages: {len(english_pages)}")

    # ── 1. Page-level aligned dataset ──
    print("\nBuilding page-aligned dataset...")
    page_pairs = []
    for sp in sorted(sanskrit_pages.keys()):
        # English is on the next page (Sanskrit even, English odd)
        en_page = sp + 1 if (sp + 1) in english_pages else sp - 1
        en_page = en_page if en_page in english_pages else None
        entry = {
            "id": f"mbt.page.{sp:04d}",
            "sanskrit_page": sp,
            "english_page": en_page,
            "sanskrit": clean_devanagari(sanskrit_pages[sp]),
            "english": clean_english(english_pages.get(en_page or 0, "")) if en_page else "",
            "source": "Manthānabhairavatantra — Kumārikākhaṇḍa",
        }
        page_pairs.append(entry)

    out_file = DATASET_DIR / "mbt_page_aligned.jsonl"
    with open(out_file, "w") as f:
        for entry in page_pairs:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  {len(page_pairs)} aligned pairs → {out_file}")

    # ── 2. Verse-level Sanskrit dataset ──
    print("\nExtracting verses from Sanskrit OCR...")
    all_verses = []
    current_chapter = None
    for sp in sorted(sanskrit_pages.keys()):
        text = sanskrit_pages[sp]
        ch = detect_chapter(text)
        if ch:
            current_chapter = ch
        verses = extract_verses(text)
        for v in verses:
            all_verses.append({
                "id": f"mbt.ch{current_chapter or '?'}.v{v['verse_number'] or '?'}",
                "chapter": current_chapter,
                "verse_number": v["verse_number"],
                "sanskrit": clean_devanagari(v["text"]),
                "source_page": sp,
                "source": "Manthānabhairavatantra — Kumārikākhaṇḍa",
            })

    out_file2 = DATASET_DIR / "mbt_verses.jsonl"
    with open(out_file2, "w") as f:
        for v in all_verses:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    print(f"  {len(all_verses)} verses extracted → {out_file2}")

    # ── 3. Stats ──
    ch_counts = {}
    for v in all_verses:
        c = v["chapter"] or 0
        ch_counts[c] = ch_counts.get(c, 0) + 1
    print(f"\n  Verses per chapter: {dict(sorted(ch_counts.items()))}")
    print(f"  Total sanskrit chars: {sum(len(v['sanskrit']) for v in all_verses)}")

    # Print sample
    print(f"\n  Sample verse entries:")
    for v in all_verses[:3]:
        print(f"    {v['id']}: {v['sanskrit'][:80]}...")

    print("\nDataset build complete!")


if __name__ == "__main__":
    main()
