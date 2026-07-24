from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sanskritree.corpus.ingestion import ingest_manifest, load_manifest
from sanskritree.database import connect, migrate
from sanskritree.review.importer import apply_annotations


ROOT = Path(__file__).parents[1]


class ReviewImporterTests(unittest.TestCase):
    def test_annotations_add_auditable_records_without_changing_source_reading(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(Path(tmp) / "review.db")
            migrate(conn, ROOT / "migrations")
            ingest_manifest(conn, load_manifest(ROOT / "data/manifests/spandakārika_pilot.yaml"))
            counts = apply_annotations(conn, load_manifest(ROOT / "data/manifests/spandakārika_stanza_1_annotations.yaml"))
            self.assertEqual(counts, {"alignments": 1, "candidates": 1, "frames": 2})
            self.assertEqual(conn.execute("SELECT count(*) FROM alignments").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT count(*) FROM translation_candidates").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT count(*) FROM semantic_frames").fetchone()[0], 2)
            self.assertEqual(conn.execute("SELECT sanskrit_raw FROM passage_readings WHERE reading_id='spk.001.reading.dyczkowski.1992.local'").fetchone()[0], "Yasyonmesanimesabhyam jagatah pralayodayau / Tam Sakticakravibhavaprabhavam Sankaram stumah // 1")
            conn.close()


if __name__ == "__main__":
    unittest.main()
