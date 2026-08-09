"""B0 baseline: plain DeepSeek on 36 diagnostic passages."""
import json, os, sys, time
from pathlib import Path
from openai import OpenAI

api_key = "sk-SDjjQ8NtTdpM2OmWl3GXDrPlhcQiLvZln60mSVVcJQ3rkg7trYHQoLKshcKSeg0Y"
client = OpenAI(api_key=api_key, base_url="https://opencode.ai/zen/go/v1")

diag = json.load(open("proof/diagnostic_36.json"))
out_path = Path("proof/b0_diagnostic_36.json")

done = {}
if out_path.exists():
    for r in json.loads(out_path.read_text()):
        done[r["passage_id"]] = r

results = list(done.values())
for d in diag:
    if d["passage_id"] in done:
        continue
    
    for attempt in range(2):
        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "Sanskrit translation engine. Output ONLY the English translation."},
                    {"role": "user", "content": f"Translate:\n{d['source']}"}
                ],
                temperature=0.0,
                max_tokens=8192,
            )
            t = (resp.choices[0].message.content or "").strip()
            if isinstance(t, list): t = ""
            if t:
                results.append({"passage_id": d["passage_id"], "source": d["source"], "domain": d["domain"], "work": d["work"], "b0": t})
                sys.stdout.write(f"✅ {d['passage_id']}: {t[:60]}...\n")
                sys.stdout.flush()
                break
        except Exception as e:
            sys.stdout.write(f"⚠ {d['passage_id']}: {str(e)[:40]}\n")
            sys.stdout.flush()
        time.sleep(2 * attempt)
    else:
        results.append({"passage_id": d["passage_id"], "b0": ""})
        sys.stdout.write(f"❌ {d['passage_id']}: empty\n")
        sys.stdout.flush()
    
    out_path.write_text(json.dumps(results, indent=2))
    time.sleep(0.1)

ok = sum(1 for r in results if r.get("b0", "").strip())
sys.stdout.write(f"\nDone: {ok}/{len(results)} non-empty\n")
sys.stdout.flush()
