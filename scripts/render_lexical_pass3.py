"""PR 8C: Re-render lexical-error verses with technical-context ranker.
Uses src/sanskritree/evidence/ranker.py for structured evidence.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

BASE = Path(__file__).parents[1]
import sys
sys.path.insert(0, str(BASE / "src"))

from sanskritree.evidence.ranker import build_evidence_text, is_technical_context
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url="https://opencode.ai/zen/go/v1")

records = [json.loads(l) for l in Path("proof/checkpoint1/runs/pass_1/blind_pass_1.jsonl").read_text().strip().split("\n") if l.strip()]
adj = json.loads(Path("proof/checkpoint1/evaluation/dev_adjudications_pass_1.json").read_text())

def seq_to_vid(seq):
    if seq <= 24: return f"spk.1.{seq + 1}"
    elif seq <= 31: return f"spk.2.{seq - 24}"
    elif seq <= 50: return f"spk.3.{seq - 31}"
    else: return f"spk.4.{seq - 50}"

# Find verses with unresolved lexical errors (not FIXED)
lexical_targets = [a for a in adj if a["cause"] == "LEXICAL_SENSE" and a.get("fixed_in_pass2") != True]

print(f"Re-rendering {len(lexical_targets)} LEXICAL_SENSE verses with technical-context evidence\n")

for a in lexical_targets:
    vid = a["verse_id"]
    note = a.get("note", "")
    
    # Find record
    rec = None
    for r in records:
        if seq_to_vid(r["sequence_index"]) == vid:
            rec = r
            break
    if not rec:
        continue
    
    seq = rec["sequence_index"]
    source = rec["source_clean"]
    lemmas = rec["pipeline"]["factor_graph"]["lemmas"]
    frame = rec["pipeline"]["factor_graph"]["frame"]
    old = rec["pipeline"]["llm_rendering"].get("translation_pass2", "") or rec["pipeline"]["llm_rendering"].get("translation", "")
    
    # Build improved evidence
    evidence = build_evidence_text(lemmas, source=source)
    is_tech = is_technical_context(lemmas)
    
    # Prompt with context
    domain_hint = "This is a verse from the Spandakārikā (Kashmir Shaivism)." if is_tech else ""
    prompt = f"""{domain_hint}
Translate this Sanskrit verse to English.

SANSKRIT: {source}

LEXICAL EVIDENCE:
{evidence}

FRAME: {frame}"""
    
    print(f"[{seq:2d}] {vid}")
    print(f"  Source: {source}")
    print(f"  Lemmas: {lemmas}")
    print(f"  Evidence:\n{evidence[:200]}\n")
    
    for attempt in range(2):
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "You are a Sanskrit translation engine specialized in Kashmir Shaivism. Output ONLY the English translation."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0, max_tokens=8192 if attempt == 1 else 4096,
            )
            content = (resp.choices[0].message.content or "").strip()
            if isinstance(content, list): content = ""
            if content:
                print(f"  OLD: {old[:80]}...")
                print(f"  NEW: {content[:80]}...")
                rec["pipeline"]["llm_rendering"]["translation_pass3"] = content
                rec["pipeline"]["llm_rendering"]["ranker_version"] = "pr8c_ranker_v1"
                break
        except Exception as e:
            print(f"  ERROR: {str(e)[:60]}")
            time.sleep(1)
    
    # Save after each
    Path("proof/checkpoint1/runs/pass_1/blind_pass_1.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records))
    print()

print("Done.")
PYEOF