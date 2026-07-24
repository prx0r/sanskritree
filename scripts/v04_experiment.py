"""v0.4: Decisive B2-vs-C experiment — framework + evidence bundles + evaluation.

Usage:
  python3 v04_experiment.py --generate     # Generate evidence bundles for all 30 passages
  python3 v04_experiment.py --evaluate     # Blind evaluation interface
  python3 v04_experiment.py --report       # Generate comparison report
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))
from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")

# ── Frozen prompt definitions ──

A2_PROMPT = """You are a Sanskrit translation assistant. Translate the following Sanskrit verse into accurate English. Do not add commentary or explanation. If the text is unclear or contains vocabulary you do not recognize, state "Uncertain: [your best attempt]" rather than inventing a meaning.

SANSKRIT: {source}"""

B2_PROMPT = """You are a Sanskrit translation assistant. You have been given lexical and grammatical evidence to support your translation. Use the evidence provided below, but produce a natural English translation. If the evidence is insufficient for any part of the verse, state "Uncertain: [your best attempt]" rather than inventing a meaning.

SANSKRIT: {source}

LEXICAL EVIDENCE:
{evidence}

FRAME: {frame}

Translate the verse using the provided evidence. Do not add unsupported content."""

FROZEN_CONFIG = {
    "model": "to_be_set",  # Set when running
    "provider": "to_be_set",
    "temperature": 0.0,
    "max_tokens": 256,
    "version": "v0.4",
}


def build_evidence_bundle(lemmas: list[str], lemma_glosses: dict) -> str:
    """Build structured lexical evidence from lemmas."""
    if not lemmas:
        return "[No lexical evidence available]"
    lines = []
    for l in lemmas[:10]:
        gloss = lemma_glosses.get(l, f"[unrecognized: {l}]")
        lines.append(f"  {l}: {gloss}")
    return "\n".join(lines)


def generate_evidence_bundles() -> dict:
    """Generate evidence bundles for all 30 passages."""
    conn = connect(DB)
    pilot = json.loads(open(BASE / "proof" / "translation_pilot_v1.json").read())
    
    # Lemma gloss dictionary
    lemma_gloss = {
        "vand": "to praise", "hfd": "heart", "nATa": "lord",
        "anATa": "helpless", "saraRya": "refuge", "tvanmaya": "consisting of you",
        "citta": "mind", "BErava": "Bhairava", "tad": "that",
        "Sakti": "Sakti/power", "cakra": "wheel", "viBava": "manifestation",
        "prabhava": "source", "SaMkara": "Sankara/Siva", "stu": "to praise",
        "ca": "and", "na": "not", "api": "also/even",
        "paramArtha": "ultimate reality", "mA": "not/my",
        "phala": "fruit/result", "karma": "action", "eva": "indeed",
        "aham": "I", "Atman": "self", "yoga": "union",
        "deva": "god/lord", "Siva": "Siva", "bhairava": "Bhairava",
        "nAtha": "lord", "SrInATa": "glorious lord", "maRqala": "mandala",
        "mudra": "gesture", "guru": "teacher", "putra": "son",
        "kula": "family", "kram": "step/sequence",
        "BU": "to become", "as": "to be", "kf": "to do",
        "gam": "to go", "zru": "to hear", "vac": "to speak",
        "dRS": "to see", "jYA": "to know", "i": "to go",
        "SyAm": "to dissolve", "cint": "to think", "dhyAI": "to meditate",
        "praviS": "to enter", "muc": "to liberate", "Ap": "to obtain",
    }
    
    bundles = []
    for passage in pilot["passages"]:
        pid = passage["id"]
        source = passage["source_clean"]
        out_c = passage["system_outputs"].get("C_sanskritree_nolean", {})
        lemmas = out_c.get("lemmas", [])
        frame = out_c.get("frame", "?")
        
        evidence = build_evidence_bundle(lemmas, lemma_gloss)
        
        bundles.append({
            "passage_id": pid,
            "track": passage["track"],
            "source": source,
            "lemmas": lemmas,
            "frame": frame,
            "a2_prompt": A2_PROMPT.format(source=source),
            "b2_prompt": B2_PROMPT.format(source=source, evidence=evidence, frame=frame),
            "frozen_config": FROZEN_CONFIG,
            "evidence_bundle": evidence,
            "llm_output_a2": None,  # To be filled when LLM is called
            "llm_output_b2": None,
            "llm_cost": None,
            "llm_tokens": None,
            "llm_timestamp": None,
        })
    
    conn.close()
    return bundles


def create_evaluation_sheet(bundles: list[dict]) -> list[dict]:
    """Create a blind evaluation sheet with randomized labels."""
    evaluations = []
    random.seed(42)  # deterministic shuffle
    
    for bundle in bundles:
        order = ["B2", "C"]
        random.shuffle(order)
        
        out_c = {"lemmas": bundle["lemmas"], "frame": bundle["frame"]}
        out_c_text = f"[{out_c['frame']}] {' '.join(out_c['lemmas'])}" if out_c['lemmas'] else f"[{out_c['frame']}] [no lemmas]"
        
        # Get B2 output (approximation until real LLM)
        b2_text = bundle.get("llm_output_b2") or bundle.get("b2_prompt", "")[:80] + "..."
        c_text = out_c_text
        
        ev = {
            "passage_id": bundle["passage_id"],
            "track": bundle["track"],
            "source": bundle["source"],
            "labels": {"A": order[0], "B": order[1]},
            "outputs": {
                order[0]: b2_text if order[0] == "B2" else c_text,
                order[1]: b2_text if order[1] == "B2" else c_text,
            },
        }
        evaluations.append(ev)
    
    return evaluations


def report(bundles: list[dict]) -> dict:
    """Generate comparison report by track."""
    by_track = defaultdict(list)
    for b in bundles:
        by_track[b["track"]].append(b)
    
    report_data = {}
    for track, items in by_track.items():
        n_lemmas = [len(i["lemmas"]) for i in items]
        n_zero = sum(1 for i in items if len(i["lemmas"]) == 0)
        n_low = sum(1 for i in items if len(i["lemmas"]) <= 1)
        frames = defaultdict(int)
        for i in items:
            frames[i["frame"]] += 1
        
        report_data[track] = {
            "count": len(items),
            "avg_lemmas": round(sum(n_lemmas) / len(items), 1),
            "zero_lemmas": n_zero,
            "low_coverage": n_low,
            "frame_distribution": dict(frames),
            "b2_llm_ready": sum(1 for i in items if i.get("llm_output_b2")),
            "a2_llm_ready": sum(1 for i in items if i.get("llm_output_a2")),
        }
    
    return {
        "total": len(bundles),
        "by_track": report_data,
        "llm_baseline_ready": all(b.get("llm_output_b2") for b in bundles),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="Generate evidence bundles")
    parser.add_argument("--evaluate", action="store_true", help="Generate blind evaluation sheet")
    parser.add_argument("--report", action="store_true", help="Generate comparison report")
    args = parser.parse_args()
    
    if args.generate:
        bundles = generate_evidence_bundles()
        out = BASE / "proof" / "v04_evidence_bundles.json"
        with open(out, "w") as f:
            json.dump(bundles, f, indent=2, ensure_ascii=False)
        print(f"Generated {len(bundles)} evidence bundles → {out}")
        
        # Also save separate prompt files for LLM batch processing
        prompts_dir = BASE / "proof" / "v04_prompts"
        prompts_dir.mkdir(exist_ok=True)
        for b in bundles:
            pid = b["passage_id"].replace(".", "_")
            (prompts_dir / f"a2_{pid}.txt").write_text(b["a2_prompt"])
            (prompts_dir / f"b2_{pid}.txt").write_text(b["b2_prompt"])
        print(f"Prompts saved → {prompts_dir}/")
    
    if args.evaluate:
        bundles = json.loads(open(BASE / "proof" / "v04_evidence_bundles.json").read())
        evals = create_evaluation_sheet(bundles)
        out = BASE / "proof" / "v04_blind_evaluation.json"
        with open(out, "w") as f:
            json.dump(evals, f, indent=2, ensure_ascii=False)
        print(f"Blind evaluation sheet → {out}")
        
        # Print summary for human evaluator
        print(f"\n  Evaluation instructions:")
        print(f"  For each of {len(evals)} passages, two outputs labeled A and B are shown.")
        print(f"  Record which is more accurate, and note critical errors.")
    
    if args.report:
        bundles = json.loads(open(BASE / "proof" / "v04_evidence_bundles.json").read())
        r = report(bundles)
        print(f"\n  Total passages: {r['total']}")
        for track, data in r["by_track"].items():
            print(f"\n  {track}:")
            print(f"    Passages: {data['count']}")
            print(f"    Avg lemmas: {data['avg_lemmas']}")
            print(f"    Zero lemmas: {data['zero_lemmas']}")
            print(f"    Low coverage: {data['low_coverage']}")
            print(f"    Frames: {data['frame_distribution']}")
            print(f"    B2 ready: {data['b2_llm_ready']}/{data['count']}")
        
        print(f"\n  Decision rule:")
        print(f"  C succeeds if: fewer critical errors than B2,")
        print(f"                  lower or equal post-edit time,")
        print(f"                  lower unsupported-addition rate,")
        print(f"                  no major regression on readability.")
        
        out = BASE / "proof" / "v04_report.json"
        with open(out, "w") as f:
            json.dump(r, f, indent=2)
        print(f"\n  Report → {out}")


if __name__ == "__main__":
    main()
