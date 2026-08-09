"""Extract Dyczkowski Spandakārikā verse translations from PDF text."""
import json, re
from pathlib import Path

text = Path("/tmp/spanda_dyczkowski.txt").read_text()
lines = text.split("\n")

stanza_map = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
    "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10,
    "Eleven": 11, "Twelve": 12, "Thirteen": 13, "Fourteen": 14, "Fifteen": 15,
    "Sixteen": 16, "Seventeen": 17, "Eighteen": 18, "Nineteen": 19, "Twenty": 20,
    "Twenty-One": 21, "Twenty-Two": 22, "Twenty-Three": 23, "Twenty-Four": 24,
    "Twenty-Five": 25, "Twenty-Six": 26, "Twenty-Seven": 27, "Twenty-Eight": 28,
    "Twenty-Nine": 29, "Thirty": 30, "Thirty-One": 31, "Thirty-Two": 32,
    "Thirty-Three": 33, "Thirty-Four": 34, "Thirty-Five": 35, "Thirty-Six": 36,
    "Thirty-Seven": 37, "Thirty-Eight": 38, "Thirty-Nine": 39,
    "Forty": 40, "Forty-One": 41, "Forty-Two": 42, "Forty-Three": 43,
    "Forty-Four": 44, "Forty-Five": 45, "Forty-Six": 46, "Forty-Seven": 47,
    "Forty-Eight": 48, "Forty-Nine": 49, "Fifty": 50,
    "Fifty-One": 51, "Fifty-Two": 52, "Fifty-Three": 53,
}

pat = re.compile(r'^Stanza (' + '|'.join(stanza_map.keys()) + r')$')

stanza_positions = []
for i, line in enumerate(lines):
    m = pat.match(line.strip())
    if m and 12500 < i < 15900:
        stanza_positions.append((i, stanza_map[m.group(1)]))

print(f"Found {len(stanza_positions)} stanza markers in SpandaPradipika")

# Extract ALL CAPS verse text after each stanza marker
verses = {}
for idx, (pos, num) in enumerate(stanza_positions):
    end = stanza_positions[idx + 1][0] if idx + 1 < len(stanza_positions) else min(pos + 300, len(lines))
    block = lines[pos:end]

    caps_lines = []
    in_caps = False
    in_bracket = False

    for line in block[1:]:
        stripped = line.strip()
        if not stripped:
            if in_caps:
                continue
            continue

        is_all_caps = stripped.isupper() and len(stripped) > 8

        if is_all_caps:
            caps_lines.append(stripped)
            in_caps = True
        elif in_caps:
            if stripped.startswith("(") and stripped.endswith(")"):
                caps_lines.append(stripped)
                continue
            elif stripped.startswith("("):
            # Multi-line parenthetical
                caps_lines.append(stripped)
                in_bracket = True
                continue
            elif in_bracket and stripped.endswith(")"):
                caps_lines.append(stripped)
                in_bracket = False
                continue
            elif in_bracket:
                caps_lines.append(stripped)
                continue
            break

    if caps_lines:
        verse = " ".join(caps_lines)
        verse = re.sub(r'(?<=[A-Z]) (?=[A-Z])', '', verse)
        verse = verse.replace("N1MESA", "NIMESA")
        verse = re.sub(r'\s+', ' ', verse).strip()
        verses[num] = verse

# Map to canonical verse IDs (spk.section.verse_num within section)
# SpandaPradipika uses continuous numbering 1-53 across all sections
# Section 1: stanzas 1-25, Section 2: 26-32, Section 3: 33-51, Section 4: 52-53
def stanza_to_id(num):
    # Some stanzas cover multiple verses (e.g., "Six and Seven")
    # The Dyczkowski numbering is 1-53 sequential
    section = 0
    offset = 0
    if num <= 25:
        section = 1; offset = num
    elif num <= 32:
        section = 2; offset = num - 25
    elif num <= 51:
        section = 3; offset = num - 32
    else:
        section = 4; offset = num - 51
    return f"spk.{section}.{offset}"

result = {}
for num in sorted(verses.keys()):
    vid = stanza_to_id(num)
    result[vid] = {
        "dyczkowski_stanza": num,
        "verse_id": vid,
        "translation": verses[num]
    }

print(f"\nExtracted {len(result)} verse translations")
for vid in sorted(result.keys(), key=lambda x: [int(y) for y in x.split(".")[1:]]):
    v = result[vid]
    t = v["translation"]
    print(f"  {vid:12s} (stanza {v['dyczkowski_stanza']:2d}): {t[:80]}...")

out = Path("proof/checkpoint1/references/dyczkowski_extracted.json")
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")
