from __future__ import annotations
import os
import unittest
from pathlib import Path
from sanskritree.integrations.morpho_sequences import lookup

class MorphoDatasetTests(unittest.TestCase):
    def test_staged_dataset_lookup_preserves_source_metadata(self):
        directory = Path("data/raw/sanskrit-morpho-sequences")
        if not directory.exists():
            self.skipTest("audited morphology dataset not staged")
        results = lookup("prayacCati", directory, limit=1)
        self.assertTrue(results)
        self.assertEqual(results[0].engine, "dcs_vidyut_verified")
        self.assertIn("verification", results[0].detail)
