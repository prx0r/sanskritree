"""Blind evaluation tool for Checkpoint 1.
Presents blinded Sanskritree output vs Dyczkowski reference for each dev verse.
Records outcome, cause, severity using the frozen taxonomy.
Output: proof/checkpoint1/evaluation/dev_adjudications_pass_1.json
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parents[1]
OUT = BASE / "proof" / "checkpoint1" / "evaluation"

TAXONOMY = {
    "outcomes": ["SANSKRITREE_ERROR", "REFERENCE_ERROR_OR_WEAKNESS", "REFERENCE_INTERPRETIVE_EXPANSION", "BOTH_DEFENSIBLE", "TEXTUAL_VARIANT", "COMMENTARY_DEPENDENT", "UNRESOLVED"],
    "causes": ["NORMALIZATION", "SEGMENTATION", "MORPHOLOGY", "COMPOUND", "SYNTAX", "COREFERENCE", "LEXICAL_SENSE", "TECHNICAL_TERM", "FRAME_SELECTION", "FRAME_ROLE", "SEMANTIC_PLAN", "RENDERER", "DISCOURSE_CONTEXT", "UNSUPPORTED_ADDITION", "OMISSION"],
    "severity": ["MINOR", "MAJOR", "CRITICAL"],
}


def load_evaluation_sheet():
    """Load the dev comparison and assign blinded labels."""
    comp = json.loads((OUT / "dev_disagreements_pass_1.json").read_text())
    split = json.loads((BASE / "proof" / "checkpoint1" / "split_manifest.json").read_text())

    eval_sheet = []
    rng = random.Random(42)  # deterministic shuffle for reproducibility

    for d in comp["disagreements"]:
        if not d.get("reference_available"):
            continue

        order = ["sanskritree", "dyczkowski"]
        rng.shuffle(order)

        eval_sheet.append({
            "verse_id": d["verse_id"],
            "source": d["source"],
            "labels": {"A": order[0], "B": order[1]},
            "outputs": {
                "A": d["sanskritree"]["rendered_english"],
                "B": d["reference_dyczkowski"],
            },
            "sanskritree_output": d["sanskritree"]["rendered_english"],
            "reference_output": d["reference_dyczkowski"],
            "lemmas": d["sanskritree"]["lemmas"],
            "frame": d["sanskritree"]["frame"],
            "adjudication": None,
        })

    return eval_sheet


def show_verse(entry: dict) -> str:
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"VERSE: {entry['verse_id']}")
    lines.append(f"{'='*60}")
    lines.append(f"SOURCE: {entry['source']}")
    lines.append(f"")
    lines.append(f"TRANSLATION A: {entry['outputs']['A']}")
    lines.append(f"")
    lines.append(f"TRANSLATION B: {entry['outputs']['B']}")
    lines.append(f"")
    lines.append(f"A = {entry['labels']['A'].upper()}, B = {entry['labels']['B'].upper()}")
    lines.append(f"{'='*60}")
    return "\n".join(lines)


def interactive_eval():
    """Interactive CLI evaluation."""
    sheet = load_evaluation_sheet()
    results = []
    existing = OUT / "dev_adjudications_pass_1.json"
    if existing.exists():
        results = json.loads(existing.read_text())
        done_ids = {r["verse_id"] for r in results}
        sheet = [s for s in sheet if s["verse_id"] not in done_ids]
        print(f"Resuming: {len(done_ids)} already done, {len(sheet)} remaining")

    print(f"\nBlind Evaluation — {len(sheet)} verses")
    print(f"Taxonomy: outcomes={TAXONOMY['outcomes']}")
    print(f"          causes={TAXONOMY['causes']}")
    print(f"          severity={TAXONOMY['severity']}")
    input("Press Enter to begin...")

    for entry in sheet:
        print(show_verse(entry))
        print(f"\nWhich translation is more accurate? (A/B/same)")
        pref = input("> ").strip().upper()

        outcome = input(f"Outcome {TAXONOMY['outcomes']}: ").strip().upper()
        cause = input(f"Cause {TAXONOMY['causes']}: ").strip().upper()
        severity = input(f"Severity {TAXONOMY['severity']}: ").strip().upper()
        note = input("Rationale (optional): ").strip()

        entry["adjudication"] = {
            "preference": pref,
            "outcome": outcome if outcome in TAXONOMY["outcomes"] else None,
            "cause": cause if cause in TAXONOMY["causes"] else None,
            "severity": severity if severity in TAXONOMY["severity"] else None,
            "note": note,
        }
        results.append(entry)

        # Save after each verse
        with open(OUT / "dev_adjudications_pass_1.json", "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print(f"EVALUATION COMPLETE")
    print(f"{'='*60}")
    outcomes = {}
    causes = {}
    severities = {}
    for r in results:
        a = r.get("adjudication", {})
        o = a.get("outcome")
        c = a.get("cause")
        s = a.get("severity")
        if o: outcomes[o] = outcomes.get(o, 0) + 1
        if c: causes[c] = causes.get(c, 0) + 1
        if s: severities[s] = severities.get(s, 0) + 1

    print(f"Outcomes: {json.dumps(outcomes, indent=2)}")
    print(f"Causes: {json.dumps(causes, indent=2)}")
    print(f"Severity: {json.dumps(severities, indent=2)}")


def batch_report():
    """Generate report from existing adjudications."""
    path = OUT / "dev_adjudications_pass_1.json"
    if not path.exists():
        print("No adjudications found. Run interactive_eval first.")
        return

    results = json.loads(path.read_text())
    sheet = load_evaluation_sheet()

    print(f"{'='*60}")
    print(f"PASSAGE-LEVEL COMPARISON TABLE")
    print(f"{'='*60}")
    print(f"{'Verse':12s} {'Outcome':30s} {'Cause':20s} {'Sev':6s} {'Preference':10s}")
    print(f"{'-'*12} {'-'*30} {'-'*20} {'-'*6} {'-'*10}")

    outcomes = {}
    causes = {}
    severities = {}

    for r in results:
        a = r.get("adjudication", {})
        vid = r["verse_id"]
        out = a.get("outcome", "?")
        cause = a.get("cause", "?")
        sev = a.get("severity", "?")
        pref = a.get("preference", "?")

        print(f"{vid:12s} {out:30s} {cause:20s} {sev:6s} {pref:10s}")

        outcomes[out] = outcomes.get(out, 0) + 1
        causes[cause] = causes.get(cause, 0) + 1
        severities[sev] = severities.get(sev, 0) + 1

    print(f"{'='*60}")
    print(f"ERROR DISTRIBUTION")
    print(f"{'='*60}")
    print(f"Outcomes: {json.dumps(outcomes, indent=2)}")
    print(f"Causes: {json.dumps(causes, indent=2)}")
    print(f"Severity: {json.dumps(severities, indent=2)}")

    total = len(results)
    if severities.get("CRITICAL", 0) > 0:
        print(f"\n⚠ RELEASE BLOCKED: {severities.get('CRITICAL', 0)} critical errors")
    if severities.get("MAJOR", 0) > 2:
        print(f"⚠ RELEASE BLOCKED: {severities.get('MAJOR', 0)} major errors (max 2)")
    defensible = outcomes.get("BOTH_DEFENSIBLE", 0) + outcomes.get("REFERENCE_ERROR_OR_WEAKNESS", 0)
    print(f"Defensible reading rate: {defensible}/{total} ({defensible/max(total,1)*100:.0f}%)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        batch_report()
    elif len(sys.argv) > 1 and sys.argv[1] == "--export":
        sheet = load_evaluation_sheet()
        out = OUT / "dev_evaluation_sheet.json"
        with open(out, "w") as f:
            json.dump(sheet, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(sheet)} evaluation items to {out}")
        print(f"\nRun: python3 scripts/blind_evaluate.py --review")
    elif len(sys.argv) > 1 and sys.argv[1] == "--review":
        sheet = json.loads((OUT / "dev_evaluation_sheet.json").read_text())
        existing = OUT / "dev_adjudications_pass_1.json"
        done = {}
        if existing.exists():
            for r in json.loads(existing.read_text()):
                done[r["verse_id"]] = r.get("adjudication")
        for entry in sheet:
            vid = entry["verse_id"]
            if vid in done:
                print(f"\n[{vid}] ✅ Already adjudicated: {done[vid].get('outcome', '?')}")
                continue
            print("\n" + "=" * 60)
            print(f"VERSE: {vid}")
            print("=" * 60)
            print(f"SOURCE: {entry['source']}")
            print(f"\n--- SANSKRITREE ---")
            print(entry['sanskritree_output'][:200])
            print(f"\n--- DYCZKOWSKI ---")
            print(entry['reference_output'][:200])
            print(f"\n--- LEMMAS: {entry['lemmas']}")
            print(f"--- FRAME: {entry['frame']}")
            print()
    else:
        interactive_eval()
