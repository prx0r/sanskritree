"""Render Nyāyasūtra with full sense registry (C2).
Launches in background. Saves to proof/checkpoint3/runs/ns_c2.jsonl
"""
from __future__ import annotations
import json, os, re, sys, time
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score
from sanskritree.semantics.ritual_frames import detect_action
from sanskritree.evidence.ranker import set_db_connection, set_allowed_scopes, build_evidence_text
from openai import OpenAI

DB = str(BASE / "data" / "sanskritree-v2.db")
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key: print("FATAL: no API key"); sys.exit(1)

client = OpenAI(api_key=api_key, base_url="https://opencode.ai/zen/go/v1")
conn = connect(DB)
set_db_connection(conn)
set_allowed_scopes(None)  # C2: all senses

verses = conn.execute("""
    SELECT p.sequence_index, p.passage_id, pr.reading_id, pr.sanskrit_raw
    FROM passages p JOIN passage_readings pr ON pr.passage_id = p.passage_id
    WHERE p.work_id = 'nyayasutra' AND p.passage_type = 'sutra'
    ORDER BY p.sequence_index
""").fetchall()

out_dir = BASE / "proof" / "checkpoint3" / "runs"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "ns_c2.jsonl"

done_ids = set()
if out_path.exists():
    for line in out_path.read_text().strip().split("\n"):
        if line.strip():
            try: done_ids.add(json.loads(line)["passage_id"])
            except: pass

records = []
for seq, pid, rid, source in verses:
    if pid in done_ids: continue

    clean = re.sub(r'\|\|\s*(?:\w+)_?[\d.]+\s*\|\|?$', '', source).strip()
    actions = detect_action(clean)
    g = FactorGraph(pid)
    g.neighborhood(conn, rid)
    if actions: g.set_detected_actions(actions)
    g.add_variable("compound", [
        VariableChoice("k", {"relation": "karmadharaya"}, 0.3),
        VariableChoice("t", {"relation": "tatpurusa"}, -0.3),
    ])
    g.add_variable("frame", [
        VariableChoice("d", {"frame_type": "DevotionalAct"}, 0.2),
        VariableChoice("i", {"frame_type": "Instruction"}, 0.2),
        VariableChoice("id", {"frame_type": "IdentityClaim"}, 0.0),
    ])
    register_graph(g)
    best, _, energy = propagate_and_score(g)

    lemmas = []
    for vn, c in best.choices.items():
        if vn.startswith("token_"):
            lem = c.payload.get("lemma", "")
            if lem and lem != "__unknown__":
                lemmas.append(lem)
    frame = best.choices.get("frame", VariableChoice("n",{},0)).payload.get("frame_type", "?")

    evidence = build_evidence_text(lemmas, work_id="nyayasutra")
    prompt = f"Translate this Sanskrit sutra to English.\n\nSANSKRIT: {clean}\n\nLEXICAL EVIDENCE:\n{evidence}\n\nFRAME: {frame}"

    translation, status = "", "ERROR"
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "system", "content": "Sanskrit translation engine. Output ONLY the English translation."},
                          {"role": "user", "content": prompt}],
                temperature=0.0, max_tokens=8192 if attempt > 0 else 4096,
            )
            content = (resp.choices[0].message.content or "").strip()
            if isinstance(content, list): content = ""
            if content:
                translation, status = content, "SUCCESS"
                break
            time.sleep(4 * (2 ** attempt))
        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "429" in err:
                time.sleep(8 * (2 ** attempt))
            else:
                time.sleep(2 * (2 ** attempt))

    rec = {
        "passage_id": pid, "sequence_index": seq, "system": "c2",
        "source": clean, "lemmas": lemmas, "frame": frame,
        "translation": translation, "render_status": status,
        "time_s": 0, "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    records.append(rec)
    out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records))
    sys.stdout.write(f"[NS] {seq:2d} {pid}: {status} {len(lemmas)} lemmas — {translation[:60]}...\n")
    sys.stdout.flush()

conn.close()
sys.stdout.write(f"\nDone: {len(records)} sutras → {out_path}\n")
