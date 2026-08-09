"""Phase 2: Blind rendering of VB dev verses with C0/C1/C2 sense ablation.
Usage: PYTHONPATH=src python3 scripts/phase2_render.py --system c2 [--limit 80]
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
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

SCOPE_MAP = {
    "c0": ["GENERAL_SANSKRIT"],
    "c1": ["GENERAL_SANSKRIT", "PAN_SAIVA"],
    "c2": None,  # all scopes
}


def render_verse(client, pid, source, lemmas, frame, system, conn):
    set_allowed_scopes(SCOPE_MAP[system])
    evidence = build_evidence_text(lemmas, work_id="vijnanabhairava")
    prompt = f"Translate this Sanskrit verse to English.\n\nSANSKRIT: {source}\n\nLEXICAL EVIDENCE:\n{evidence}\n\nFRAME: {frame}"

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
                return content, "SUCCESS"
            # Empty content: likely rate limit or reasoning overflow
            if attempt < 2:
                time.sleep(4 * (2 ** attempt))  # exponential backoff
        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "limit" in err or "429" in err or "too many" in err:
                wait = 8 * (2 ** attempt)
                print(f"  Rate limited, backing off {wait}s...")
                time.sleep(wait)
            elif attempt < 2:
                time.sleep(4 * (2 ** attempt))
    return "", "ERROR"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", choices=["c0", "c1", "c2"], required=True)
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("FATAL: OPENAI_API_KEY not set"); return

    conn = connect(DB)
    set_db_connection(conn)
    client = OpenAI(api_key=api_key, base_url="https://opencode.ai/zen/go/v1")

    # Get VB verses (all 162, we'll filter dev later)
    verses = conn.execute("""
        SELECT p.sequence_index, p.passage_id, pr.reading_id, pr.sanskrit_raw
        FROM passages p JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'vijnanabhairava' AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """).fetchall()

    out_dir = BASE / "proof" / "checkpoint2" / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"vb_{args.system}.jsonl"

    # Load existing progress
    done_ids = set()
    if out_path.exists():
        for line in out_path.read_text().strip().split("\n"):
            if line.strip():
                try:
                    done_ids.add(json.loads(line)["passage_id"])
                except: pass

    records = []
    count = 0
    for seq, pid, rid, source in verses:
        if pid in done_ids:
            continue
        if count >= args.limit:
            break
        if count < args.offset:
            count += 1
            continue

        clean = re.sub(r'\|\|\s*(?:vb)_?[\d.]+\s*\|\|?$', '', source).strip()
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
        ])
        register_graph(g)
        best, _, energy = propagate_and_score(g)

        lemmas = []
        for vn, c in best.choices.items():
            if vn.startswith("token_"):
                lem = c.payload.get("lemma", "")
                if lem and lem != "__unknown__":
                    lemmas.append(lem)
        frame = best.choices.get("frame", VariableChoice("n", {}, 0)).payload.get("frame_type", "?")

        t0 = time.time()
        translation, status = render_verse(client, pid, clean, lemmas, frame, args.system, conn)
        elapsed = time.time() - t0

        rec = {
            "passage_id": pid,
            "sequence_index": seq,
            "system": args.system,
            "source": clean,
            "lemmas": lemmas,
            "frame": frame,
            "n_hypotheses": sum(len(c) for c in g.variables.values()),
            "translation": translation,
            "render_status": status,
            "time_s": round(elapsed, 1),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        records.append(rec)
        out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records))

        count += 1
        print(f"[{args.system.upper()}] {seq:3d} {pid}: {status} {len(lemmas)} lemmas ({elapsed:.0f}s) — {translation[:50]}...")

    print(f"\n{args.system.upper()} done: {len(records)} verses → {out_path}")
    conn.close()


if __name__ == "__main__":
    main()
