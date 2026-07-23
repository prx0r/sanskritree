from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sanskritree.corpus.ingestion import ingest_manifest, load_manifest
from sanskritree.database import connect, migrate
from sanskritree.philology.adapters import analyze


ROOT = Path(__file__).parents[1]


class SpandakarikaPilotTests(unittest.TestCase):
    def test_ten_verse_source_slice_retains_raw_transliteration(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(Path(tmp) / "spk.db")
            migrate(conn, ROOT / "migrations")
            results = ingest_manifest(conn, load_manifest(ROOT / "data/manifests/spandakārika_pilot.yaml"))
            self.assertEqual(len(results), 10)
            rows = conn.execute("SELECT sanskrit_raw, transliteration_scheme, critical_status FROM passage_readings ORDER BY passage_id").fetchall()
            self.assertEqual(rows[0][0], "Yasyonmesanimesabhyam jagatah pralayodayau / Tam Sakticakravibhavaprabhavam Sankaram stumah // 1")
            self.assertTrue(all(row[1] == "Roman ASCII transliteration" for row in rows))
            self.assertTrue(all(row[2] == "edition_derived_transliteration_unreviewed" for row in rows))
            lattice = analyze(rows[0][0], ["dcs", "vidyut"])
            self.assertTrue(all(candidate.engine != "dcs_vidyut_verified" for _, _, _, candidates in lattice for candidate in candidates))
            conn.close()


if __name__ == "__main__":
    unittest.main()
