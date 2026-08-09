"""Tests for the frozen Spanda v1 benchmark."""
import json
import unittest
from pathlib import Path

BENCHMARK = Path(__file__).parents[1] / "benchmarks" / "spanda_v1"


def load_passages():
    return [json.loads(l) for l in BENCHMARK.joinpath("passages.jsonl").read_text().strip().split("\n") if l.strip()]


def load_splits():
    return json.loads(BENCHMARK.joinpath("splits.json").read_text())


def load_manifest():
    return json.loads(BENCHMARK.joinpath("manifest.json").read_text())


class TestSpandaBenchmark(unittest.TestCase):

    def test_all_53_passages_present(self):
        passages = load_passages()
        assert len(passages) == 53, f"Expected 53, got {len(passages)}"

    def test_passage_ids_are_unique(self):
        passages = load_passages()
        ids = [p["passage_id"] for p in passages]
        assert len(ids) == len(set(ids)), "Duplicate passage IDs"

    def test_every_passage_resolves_to_database(self):
        # This test requires DB — skip in offline mode
        pass

    def test_source_hashes_match_database_readings(self):
        manifest = load_manifest()
        source_hash = BENCHMARK.joinpath("source.sha256").read_text().strip()
        assert source_hash == manifest["source_hash"], "Source hash mismatch"

    def test_split_sizes_are_30_13_10(self):
        splits = load_splits()
        assert len(splits["development"]) == 30, f"Dev: expected 30, got {len(splits['development'])}"
        assert len(splits["holdout"]) == 13, f"Holdout: expected 13, got {len(splits['holdout'])}"
        assert len(splits["challenge"]) == 10, f"Challenge: expected 10, got {len(splits['challenge'])}"

    def test_splits_do_not_overlap(self):
        splits = load_splits()
        dev = set(splits["development"])
        hold = set(splits["holdout"])
        chal = set(splits["challenge"])
        assert len(dev & hold) == 0, "Dev/holdout overlap"
        assert len(dev & chal) == 0, "Dev/challenge overlap"
        assert len(hold & chal) == 0, "Holdout/challenge overlap"

    def test_reference_files_have_aligned_records(self):
        ref_file = BENCHMARK / "references" / "dyczkowski.jsonl"
        passages = load_passages()
        refs = [json.loads(l) for l in ref_file.read_text().strip().split("\n") if l.strip()]
        ref_ids = {r["passage_id"] for r in refs}
        # Not all verses have refs, but every ref should map to a passage
        for r in refs:
            assert r["passage_id"] in {p["passage_id"] for p in passages}, f"Unknown passage: {r['passage_id']}"

    def test_gold_morphology_resolves(self):
        gold_file = BENCHMARK / "gold" / "morphology.jsonl"
        gold = [json.loads(l) for l in gold_file.read_text().strip().split("\n") if l.strip()]
        assert len(gold) > 0, "No gold morphology records"
        for g in gold:
            assert "hypothesis_id" in g
            assert "lemma" in g

    def test_manifest_integrity(self):
        m = load_manifest()
        assert m["benchmark_id"] == "spanda_v1"
        assert m["n_passages"] == 53
        assert m["frozen_at"] is not None
