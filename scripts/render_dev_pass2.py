"""Re-render dev verses with improved lexical evidence (PR 7).
Uses the expanded KS glossary for technical terms.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

BASE = Path(__file__).parents[1]
import sys
sys.path.insert(0, str(BASE / "src"))

from sanskritree.evidence.lexical import build_evidence_text
from sanskritree.database import connect
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url="https://opencode.ai/zen/go/v1")
conn = connect(str(BASE / "data" / "sanskritree-v2.db"))

DB = Path("data/sanskritree-v2.db")

def re_render_verse(seq: int, source: str, lemmas: list[str], frame: str) -> str:
    evidence = build_evidence_text(lemmas, work_id="spandakarika", conn=conn)
    prompt = f"Translate this Sanskrit verse to English using the lexical evidence.\n\nSANSKRIT: {source}\n\nLEXICAL EVIDENCE:\n{evidence}\n\nFRAME: {frame}"
    
    for attempt in range(2):
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "You are a Sanskrit translation engine specialized in Kashmir Shaivism. Output ONLY the English translation."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0, max_tokens=4096 if attempt == 0 else 8192,
            )
            content = (resp.choices[0].message.content or "").strip()
            if isinstance(content, list): content = ""
            if content:
                return content
        except Exception:
            time.sleep(1)
    return ""

# Load dev verses with lexical errors to fix
target_verses = {
    18: "spk.1.18",   # "pada" → "foot" error
    44: "spk.3.13",   # "kalā" → "arts" error  
    45: "spk.3.15",   # "pratyaya" → "faith" error
    # Also the omission/candidate failures
    24: "spk.3.3",    # Only 1 lemma
    47: "spk.3.16",   # Only 2 lemmas
    4: "spk.1.4",     # Negation omission
}

records = [json.loads(l) for l in Path("proof/checkpoint1/runs/pass_1/blind_pass_1.jsonl").read_text().strip().split("\n") if l.strip()]

print("Re-rendering target verses with improved lexical evidence\n")
for seq, vid in sorted(target_verses.items()):
    rec = records[seq]
    source = rec["source_clean"]
    lemmas = rec["pipeline"]["factor_graph"]["lemmas"]
    frame = rec["pipeline"]["factor_graph"]["frame"]
    
    old = rec["pipeline"]["llm_rendering"]["translation"]
    new = re_render_verse(seq, source, lemmas, frame)
    
    print(f"[{seq:2d}] {vid}")
    print(f"  OLD: {old[:80]}...")
    print(f"  NEW: {new[:80]}...")
    print()
    
    rec["pipeline"]["llm_rendering"]["translation_pass2"] = new
    rec["pipeline"]["llm_rendering"]["lexicon_version"] = "pr7_ks_glossary_v1"
    Path("proof/checkpoint1/runs/pass_1/blind_pass_1.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records))

conn.close()
print("Done.")
