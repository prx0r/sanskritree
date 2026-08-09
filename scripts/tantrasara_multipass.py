"""Tantrasāra multipass: 3 passes, full text, background."""
import json, os, sys, time
from pathlib import Path
from openai import OpenAI

api_key = "sk-SDjjQ8NtTdpM2OmWl3GXDrPlhcQiLvZln60mSVVcJQ3rkg7trYHQoLKshcKSeg0Y"
client = OpenAI(api_key=api_key, base_url="https://opencode.ai/zen/go/v1")

# Load text
import sys; sys.path.insert(0, "src"); from sanskritree.database import connect
conn = connect("data/sanskritree-v2.db")
rows = conn.execute("SELECT pr.sanskrit_raw FROM passages p JOIN passage_readings pr ON pr.passage_id=p.passage_id WHERE p.work_id='tantrasara' ORDER BY p.sequence_index").fetchall()
conn.close()

full_text = "\n\n".join(f"[{i+1}] {r[0]}" for i, r in enumerate(rows))
out = Path("/root/projects/sanskritree/proof/tantrasara_multipass.jsonl")

def call(messages, label=""):
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash", messages=messages,
                temperature=0.0, max_tokens=16384,
            )
            t = (resp.choices[0].message.content or "").strip()
            if t:
                sys.stdout.write(f"[{label}] OK ({len(t)} chars)\n")
                sys.stdout.flush()
                return t
            time.sleep(4 * attempt)
        except Exception as e:
            sys.stdout.write(f"[{label}] retry {attempt}: {str(e)[:40]}\n")
            sys.stdout.flush()
            time.sleep(4 * attempt)
    return "[ERROR]"

# Pass 1
sys.stdout.write("=== PASS 1: Full translation ===\n")
sys.stdout.flush()
p1 = call([
    {"role": "system", "content": "Translate Abhinavagupta's Tantrasāra into accurate English. This is a dense Trika Kashmir Shaiva philosophical text."},
    {"role": "user", "content": f"Translate the entire Tantrasāra into English:\n\n{full_text}\n\nTRANSLATION:"}
], "P1")
open("/tmp/ts_p1.txt","w").write(p1)

# Save checkpoint
json.dump({"pass": 1, "text": p1}, open("/tmp/ts_checkpoint.json","w"))

# Pass 2
sys.stdout.write("\n=== PASS 2: Concept map + critique ===\n")
sys.stdout.flush()
p2 = call([
    {"role": "system", "content": "You are reviewing your own translation. Identify specific errors, doctrinal misinterpretations, or omissions."},
    {"role": "user", "content": f"Review this translation of Tantrasāra. Identify specific problems:\n\n{p1[:8000]}\n\nCRITIQUE:"}
], "P2")
open("/tmp/ts_p2.txt","w").write(p2)
json.dump({"pass": 2, "text": p2}, open("/tmp/ts_checkpoint.json","w"))

# Pass 3
sys.stdout.write("\n=== PASS 3: Revised translation ===\n")
sys.stdout.flush()
p3 = call([
    {"role": "system", "content": "You are revising your translation after peer review."},
    {"role": "user", "content": f"Below is your translation and a critique. Produce a revised version.\n\nTRANSLATION:\n{p1[:8000]}\n\nCRITIQUE:\n{p2[:4000]}\n\nREVISED TRANSLATION:"}
], "P3")
open("/tmp/ts_p3.txt","w").write(p3)

# Save all
result = [{"pass": 1, "text": p1}, {"pass": 2, "text": p2}, {"pass": 3, "text": p3}]
out.write_text(json.dumps(result, indent=2))
sys.stdout.write(f"\n✅ All 3 passes complete → {out}\n")
sys.stdout.flush()
