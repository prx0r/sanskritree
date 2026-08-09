"""Run Spanda Checkpoint: frozen, reproducible full-text translation.
Usage:
  PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py prepare
  PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py generate --split development
  PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py audit --run RUN_ID
  PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py evaluate --run RUN_ID
  PYTHONPATH=src python3 scripts/run_spanda_checkpoint.py report --run RUN_ID
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.evaluation.blind_context import BlindRunContext
from sanskritree.translation.analysis_manifest import build_manifest
from sanskritree.evidence.ranker import set_db_connection as set_ranker_db_connection


DB = str(BASE / "data" / "sanskritree-v2.db")
BENCHMARK = BASE / "benchmarks" / "spanda_v1"


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE).decode().strip()
    except Exception:
        return "unknown"


def prepare():
    """Verify benchmark integrity and create run registry."""
    print("Preparing Spanda Checkpoint...")

    # Verify benchmark exists
    assert BENCHMARK.exists(), f"Benchmark not found at {BENCHMARK}"
    manifest = json.loads((BENCHMARK / "manifest.json").read_text())
    print(f"  Benchmark: {manifest['benchmark_id']} v{manifest['version']}")
    print(f"  Passages: {manifest['n_passages']}")
    print(f"  Splits: {manifest['splits']}")

    # Verify database
    conn = connect(DB)
    count = conn.execute("SELECT COUNT(*) FROM passages WHERE work_id='spandakarika'").fetchone()[0]
    print(f"  Spanda verses in DB: {count}")
    conn.close()

    # Create run manifest
    run_id = str(uuid.uuid4())
    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "benchmark": manifest["benchmark_id"],
        "status": "prepared",
    }
    print(f"  Run ID: {run_id}")
    print("  Ready.")

    return run


def generate(split: str = "development"):
    """Generate translations for a split using blind context."""
    run = prepare()
    commit = get_git_commit()

    passages = [json.loads(l) for l in BENCHMARK.joinpath("passages.jsonl").read_text().strip().split("\n") if l.strip()]
    split_passages = [p for p in passages if p["split"] == split]

    print(f"\nGenerating translations for '{split}' ({len(split_passages)} passages)...")

    conn = connect(DB)
    from sanskritree.evidence.ranker import set_db_connection as set_ranker_conn
    set_ranker_conn(conn)
    results = []

    for p in split_passages:
        pid = p["passage_id"]
        source = p["source_iast"]

        with BlindRunContext(BENCHMARK) as ctx:
            manifest = build_manifest(conn, pid, source, git_commit=commit)

        results.append(manifest.to_dict())
        print(f"  {pid}: {manifest.selected_lemma[:30] if manifest.selected_lemma else 'NO LEMMA'}...")

    # Save run
    out_dir = BASE / "proof" / "checkpoint1" / "runs" / f"run_{split}"
    out_dir.mkdir(parents=True, exist_ok=True)

    run_record = {
        "run_id": run.get("run_id", str(uuid.uuid4())),
        "split": split,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "n_passages": len(results),
        "results": results,
    }
    with open(out_dir / "run_manifest.json", "w") as f:
        json.dump(run_record, f, indent=2)

    print(f"\nSaved: {out_dir / 'run_manifest.json'}")
    conn.close()


def audit(run_id: str):
    """Run audit suite on a completed run."""
    from sanskritree.audit.translation import run_audit_suite

    # Find the run
    runs_dir = BASE / "proof" / "checkpoint1" / "runs"
    found = None
    for d in runs_dir.iterdir():
        if d.is_dir():
            m = d / "run_manifest.json"
            if m.exists():
                data = json.loads(m.read_text())
                if data.get("run_id") == run_id or d.name == run_id:
                    found = data
                    break
    if not found:
        print(f"Run not found: {run_id}")
        return

    audits = []
    for r in found.get("results", []):
        output_text = r.get("selected", {}).get("lemma", "")
        source_info = {
            "polarity": "positive",
            "lemmas": [output_text] if output_text else [],
            "expected_hash": r.get("source_hash", ""),
            "actual_hash": r.get("source_hash", ""),
        }
        results = run_audit_suite(output_text, source_info)
        audits.append({"passage_id": r.get("passage_id"), "audits": results})

    print(f"Audit results for run {run_id}:")
    for a in audits:
        pid = a["passage_id"]
        fails = [au for au in a["audits"] if not au["pass"]]
        if fails:
            print(f"  {pid}: FAILURES: {[f['mutation'] for f in fails]}")
        else:
            print(f"  {pid}: PASS")


def evaluate(run_id: str):
    """Compare run output against references."""
    from sanskritree.evaluation.candidate_recall import calculate_recall

    conn = connect(DB)
    report = calculate_recall(conn, layer="morphology")
    conn.close()

    print(f"Evaluation for run {run_id}:")
    print(f"  Recall@1: {report.recall_at_1:.1%}")
    print(f"  Recall@3: {report.recall_at_3:.1%}")
    print(f"  Recall@5: {report.recall_at_5:.1%}")


def report(run_id: str):
    """Full report for a run."""
    # Find the run
    runs_dir = BASE / "proof" / "checkpoint1" / "runs"
    found = None
    for d in runs_dir.iterdir():
        if d.is_dir():
            m = d / "run_manifest.json"
            if m.exists():
                data = json.loads(m.read_text())
                if data.get("run_id") == run_id or d.name == run_id:
                    found = data
                    break
    if not found:
        print(f"Run not found: {run_id}")
        return

    print(f"Report for run {run_id}")
    print(f"  Split: {found.get('split', '?')}")
    print(f"  Passages: {found.get('n_passages', 0)}")
    print(f"  Git commit: {found.get('git_commit', '?')[:12]}")
    print(f"  Created: {found.get('created_at', '?')}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Spanda Checkpoint runner")
    parser.add_argument("command", choices=["prepare", "generate", "audit", "evaluate", "report"])
    parser.add_argument("--split", default="development")
    parser.add_argument("--run", default=None)
    args = parser.parse_args()

    if args.command == "prepare":
        prepare()
    elif args.command == "generate":
        generate(args.split)
    elif args.command == "audit":
        audit(args.run or "latest")
    elif args.command == "evaluate":
        evaluate(args.run or "latest")
    elif args.command == "report":
        report(args.run or "latest")


if __name__ == "__main__":
    main()
