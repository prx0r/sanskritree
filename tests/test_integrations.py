from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from sanskritree.integrations.sanskrit_library import analyse
from sanskritree.integrations.tei import read_tei

class IntegrationTests(unittest.TestCase):
    def test_sanskrit_library_adapter_never_fabricates_unconfigured_results(self):
        result = analyse("kubjikA")
        self.assertEqual(result[0].engine, "sanskrit_library")
        self.assertEqual(result[0].detail["availability"], "transport_not_configured")
        configured = analyse("kubjikA", lambda _: [{"lemma": "kubjikA", "gender": "f", "case": "nom", "number": "sg", "confidence": .8}])
        self.assertEqual(configured[0].lemma, "kubjikA")

    def test_tei_reader_hashes_raw_source_and_extracts_units(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.xml"
            path.write_text('<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><titleStmt><title>Pilot</title></titleStmt></fileDesc></teiHeader><text><body><l xml:id="v1">kubjikā śaktiḥ</l></body></text></TEI>', encoding="utf-8")
            document = read_tei(path)
        self.assertEqual(document.title, "Pilot")
        self.assertEqual(document.units[0].xml_id, "v1")
        self.assertEqual(document.units[0].text, "kubjikā śaktiḥ")
        self.assertEqual(len(document.raw_hash), 64)
