"""Real candidate Recall@k against adjudicated gold.
Usage: PYTHONPATH=src python3 scripts/candidate_recall.py [--layer morphology]
"""
from __future__ import annotations
import json, sys
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.evaluation.candidate_recall import calculate_recall, report_to_dict


def main():
    layer = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--layer" else "morphology"
    conn = connect(str(BASE / "data" / "sanskritree-v2.db"))
    report = calculate_recall(conn, layer=layer)
    data = report_to_dict(report)

    print(f"Candidate Recall Report (layer: {layer})")
    print(f"{'='*60}")
    print(f"  Adjudicated items: {data['n_adjudicated']}")
    print(f"  Recall@1:          {data['recall_at_1']:.1%}")
    print(f"  Recall@3:          {data['recall_at_3']:.1%}")
    print(f"  Recall@5:          {data['recall_at_5']:.1%}")
    print(f"  Engine miss rate:  {data['engine_miss_rate']:.1%}")
    print(f"  Misses (>R@5):     {data['n_misses']}")
    print()

    print("  By engine:")
    for eng in sorted(data["by_engine"].keys()):
        v = data["by_engine"][eng]
        print(f"    {eng:30s} n={v['n']:4d}  R@1={v['recall_at_1']:.1%}  R@3={v['recall_at_3']:.1%}  R@5={v['recall_at_5']:.1%}")
    print()

    print("  By work:")
    for wid in sorted(data["by_work"].keys()):
        v = data["by_work"][wid]
        print(f"    {wid:35s} n={v['n']:4d}  R@1={v['recall_at_1']:.1%}  R@3={v['recall_at_3']:.1%}  R@5={v['recall_at_5']:.1%}")

    if data["misses"]:
        print(f"\n  Misses (first 10):")
        for m in data["misses"][:10]:
            pid = m.get("passage_id", "?")
            occ = m.get("occurrence_id", "?")[-40:]
            lemma = m.get("accepted_lemma", "?")
            rank = m.get("rank", "?")
            print(f"    {pid:30s} occ={occ:40s} lemma={str(lemma):10s} rank={str(rank)}")

    out = BASE / "proof" / "recall_ci_v04.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n  Saved: {out}")
    conn.close()


if __name__ == "__main__":
    main()
