"""Extract Dyczkowski verse translations from SpandaVrtti + SpandaVivrti section."""
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

patcher = re.compile(r'^Stanza (' + '|'.join(stanza_map.keys()) + r')$')

# Find all stanza markers with their line positions
stanza_positions = []
for i, line in enumerate(lines):
    m = patcher.match(line.strip())
    if m and 6754 < i < 12800:
        stanza_positions.append((i, stanza_map[m.group(1)]))

print(f"Found {len(stanza_positions)} stanza markers in SpandaVrtti section")

# Extract verse text after each stanza marker
# The pattern is: "Stanza N" → intro text → ALL CAPS verse → section header
verses = {}
stanza_failures = []

for idx, (pos, num) in enumerate(stanza_positions):
    end = stanza_positions[idx + 1][0] if idx + 1 < len(stanza_positions) else min(pos + 300, len(lines))
    block = lines[pos:end]

    caps_lines = []
    in_caps = False
    in_paren = False
    seen_caps = False

    for j, line in enumerate(block[1:], 1):
        stripped = line.strip()
        if not stripped:
            if seen_caps and len(caps_lines) > 0:
                break
            if in_caps:
                continue
            continue

        is_all_caps = stripped.isupper() and len(stripped) > 10

        # Skip section headers
        if stripped in ("THE BRIEF EXPLANATION", "THE EXTENSIVE EXPLANATION", "THE BRIEF", "THE EXTENSIVE"):
            if caps_lines:
                break
            continue

        # Skip footnote markers like "50", "51"
        if is_all_caps and re.match(r'^\d+$', stripped):
            continue

        # Skip running headers
        if is_all_caps and any(h in stripped for h in ["SEARCHABLE", "CVISION", "STANZAS ON VIBRATION", "BRIEF EXPLANATION"]):
            if caps_lines:
                break
            continue

        if is_all_caps:
            caps_lines.append(stripped)
            seen_caps = True
            in_caps = True
        elif seen_caps:
            # After ALL CAPS, continue collecting parentheticals
            if stripped.startswith("(") or (in_paren and not stripped.startswith("(")):
                caps_lines.append(stripped)
                if stripped.startswith("("):
                    in_paren = True
                if stripped.endswith(")") and not stripped.startswith("("):
                    in_paren = False
                continue
            # Also skip the "THE BRIEF" / "THE EXTENSIVE" headers
            break

    if caps_lines:
        verse = " ".join(caps_lines)
        verse = re.sub(r'(?<=[A-Z]) (?=[A-Z])', '', verse)
        verse = verse.replace("N1MESA", "NIMESA")
        verse = re.sub(r'\s+', ' ', verse).strip()
        verses[num] = verse
    else:
        stanza_failures.append(num)

# Map to canonical verse IDs
def stanza_to_id(num):
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

print(f"Extracted: {len(verses)}/{len(stanza_positions)}")
if stanza_failures:
    print(f"Failed stanzas: {stanza_failures}")

result = {}
for num in sorted(verses.keys()):
    vid = stanza_to_id(num)
    result[vid] = {
        "dyczkowski_stanza": num,
        "verse_id": vid,
        "translation": verses[num]
    }

for vid in sorted(result.keys(), key=lambda x: [int(y) for y in x.split(".")[1:]]):
    v = result[vid]
    t = v["translation"]
    print(f"  {vid:12s} (stanza {v['dyczkowski_stanza']:2d}): {t[:80]}...")

out = Path("proof/checkpoint1/references/dyczkowski_full.json")
with open(out, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")

# Coverage report
split = json.load(open("proof/checkpoint1/split_manifest.json"))
dev = set(split["development"]["verses"])
holdout = set(split["internal_holdout"]["verses"])
chal = set(split["final_challenge"]["verses"])
dyck = set(result.keys())
print(f"\nCoverage: {len(dyck)}/53 total")
print(f"  Dev: {len(dev & dyck)}/{len(dev)}")
print(f"  Holdout: {len(holdout & dyck)}/{len(holdout)}")
print(f"  Challenge: {len(chal & dyck)}/{len(chal)}")
print(f"  Missing dev: {sorted(dev - dyck)}")
