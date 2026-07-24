import fitz, glob, re, sys, yaml
from pathlib import Path

BASE = Path(__file__).parents[1]
VOL1 = glob.glob(str(BASE / "sources/TANTRALOKA*VOLUME*ONE*"))[0]
OUT = BASE / "data/manifests/tantraloka_ch1_pilot.yaml"

IAST_MARKERS = set("āīūṣṇṃḥṛśñṭḍḷṅ")
LATIN_UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LATIN_LOWER = set("abcdefghijklmnopqrstuvwxyz")

def latin_ratio(s):
    if not s: return 0
    latin = sum(1 for c in s if c in LATIN_UPPER or c in LATIN_LOWER)
    return latin / len(s)

def is_iast_line(line):
    if len(line) < 15:
        return False
    lr = latin_ratio(line)
    if lr < 0.7:
        return False
    if line[0].isupper() and not line.startswith("||"):
        return False
    stop_words = {"the", "and", "that", "this", "which", "with", "from",
                  "their", "thus", "such", "these", "those", "what", "when",
                  "have", "has", "had", "not", "but", "for", "its", "his",
                  "her", "all", "will", "would", "can", "shall", "should",
                  "one", "two", "into", "upon", "than", "then", "also",
                  "some", "very", "each", "every", "both", "own", "same",
                  "more", "much", "many", "after", "before", "here", "there",
                  "note", "see", "above", "below", "cf.", "i.e.", "e.g.",
                  "who", "whom", "whose", "however", "therefore", "indeed",
                  "although", "because", "through", "according", "without",
                  "within", "between"}
    first_word = line.split()[0].lower().strip("('\"")
    if first_word in stop_words:
        return False
    markers = sum(1 for c in line if c in IAST_MARKERS)
    if markers >= 2:
        return True
    if "||" in line and markers >= 1:
        return True
    return False

def extract_verses_from_page(page):
    blocks = page.get_text("dict")["blocks"]
    verses = []
    current_lines = []
    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(s.get("text", "") for s in line.get("spans", [])).strip()
            if not text:
                continue
            if is_iast_line(text):
                current_lines.append(text)
            else:
                if current_lines:
                    joined = " ".join(current_lines)
                    joined = re.sub(r'\s+', ' ', joined).strip()
                    joined = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', '', joined)
                    verses.append(joined)
                    current_lines = []
    if current_lines:
        joined = " ".join(current_lines)
        joined = re.sub(r'\s+', ' ', joined).strip()
        joined = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', '', joined)
        verses.append(joined)
    return verses

def extract_verse_number(text):
    m = re.search(r'\|\|\s*(\d+)\s*\|?\w?\s*\|\|?\s*$', text)
    if m:
        return int(m.group(1))
    return None

def main():
    doc = fitz.open(VOL1)
    # Chapter 1 is pages 15-442 (0-indexed 14-441)
    ch1_pages = list(range(14, 442))
    
    all_texts = []
    for pn in ch1_pages:
        if pn % 2 == 0:  # 0-indexed even = odd 1-indexed
            page = doc[pn]
            verses = extract_verses_from_page(page)
            for v in verses:
                if v and len(v) > 15:
                    all_texts.append((pn, v))
    doc.close()
    
    # Deduplicate and sort by verse number
    seen_texts = set()
    deduped = []
    for pn, text in all_texts:
        # Normalize for dedup
        key = re.sub(r'\s+', ' ', text).strip()
        if key not in seen_texts and len(key) > 15:
            seen_texts.add(key)
            deduped.append((pn, key))
    
    # Build passages
    passages = []
    verse_nums_seen = set()
    for pn, text in deduped:
        vnum = extract_verse_number(text)
        if vnum and vnum not in verse_nums_seen:
            verse_nums_seen.add(vnum)
            passage = {
                "id": f"ta.ch1.{vnum:03d}",
                "reading_id": f"ta.ch1.{vnum:03d}.dyczkowski.2023",
                "chapter": "1",
                "verse": str(vnum),
                "type": "verse",
                "transliteration": "IAST",
                "critical_status": "edition_derived_transliteration_unreviewed",
                "sanskrit": text,
                "source_page": str(pn + 1)
            }
            passages.append(passage)
    
    passages.sort(key=lambda p: int(p["verse"]))
    
    print(f"Found {len(passages)} verses from Chapter 1")
    for p in passages[:10]:
        print(f"  Verse {p['verse']}: {p['sanskrit'][:80]}...")
    if len(passages) > 10:
        print(f"  ... and {len(passages)-10} more")
    
    manifest = {
        "work": {
            "id": "tantraloka",
            "title": "Tantrāloka",
            "title_iast": "Tantrāloka",
            "author": "Abhinavagupta",
            "tradition": "trika",
            "genre": "tantra",
            "commentary": "Viveka by Jayaratha",
            "metadata": {
                "pilot_role": "calibration_source",
                "translator": "Mark S. G. Dyczkowski",
                "source_access": "locally_supplied_commercial_scan",
                "volume": "1",
                "chapter": "1",
                "chapter_title": "Vijñānabhid — The Types of Liberating Knowledge"
            }
        },
        "edition": {
            "id": "dyczkowski.2023.vol1",
            "editor": "Mark S. G. Dyczkowski",
            "publication": "Independently published",
            "year": 2023,
            "licence": "locally supplied commercial scan; not for redistribution",
            "critical_method": "IAST transliteration extracted from PDF; unreviewed import"
        },
        "passages": passages
    }
    
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"\nSaved to {OUT}")

if __name__ == "__main__":
    main()
