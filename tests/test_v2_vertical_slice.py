from __future__ import annotations
import sqlite3
import tempfile
import unittest
from pathlib import Path

from sanskritree.alignment.spans import add_alignment
from sanskritree.corpus.ingestion import ingest_manifest, load_manifest
from sanskritree.database import connect, migrate
from sanskritree.formal.compiler import compile_frame, persist_formalization
from sanskritree.formal.checker import check_persisted
from sanskritree.philology.analysis_lattice import persist_lattice, whitespace_lattice
from sanskritree.semantics.extraction import persist_frame
from sanskritree.semantics.schema import Entity, SemanticFrame
from sanskritree.translation.candidates import record_candidate, reveal_reference, start_blind_run


ROOT = Path(__file__).parents[1]


class VerticalSliceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = connect(Path(self.tmp.name) / "v2.db")
        migrate(self.conn, ROOT / "migrations")
        result = ingest_manifest(self.conn, load_manifest(ROOT / "data/manifests/mbt_kumarika_pilot.yaml"))[0]
        self.reading_id, self.passage_id = result.reading_id, result.passage_id

    def tearDown(self):
        self.conn.close(); self.tmp.cleanup()

    def test_raw_reading_is_preserved_and_normalised_separately(self):
        row = self.conn.execute("SELECT sanskrit_raw, sanskrit_normalized, source_hash FROM passage_readings").fetchone()
        self.assertEqual(row[0], "kubjikā śaktiḥ")
        self.assertEqual(row[0], row[1])
        self.assertEqual(len(row[2]), 64)

    def test_vertical_slice_is_auditable(self):
        self.assertEqual(persist_lattice(self.conn, self.reading_id, whitespace_lattice("kubjikā śaktiḥ")), 2)
        translation = self.conn.execute("SELECT translation_id FROM translations").fetchone()[0]
        add_alignment(self.conn, translation, 0, 7, 0, 7, "one_to_one", .9, {"kind": "fixture"})
        run = start_blind_run(self.conn, self.passage_id, ["literal"], [{"source": "fixture"}])
        candidate = record_candidate(self.conn, run, "literal", "Kubjika, power.", senses=[], parses=[], ranking={"evidence": [{"source": "fixture"}], "grammar": 1})
        reveal_reference(self.conn, run)
        frame = SemanticFrame("mbt.kum.pilot.001.frame.1", self.passage_id, "0:15", "assertion", Entity("Kubjika", "Deity"), "QUALIFICATION", Entity("Power", "Property"), "grammatically_explicit", .75)
        persist_frame(self.conn, frame)
        code, template, assumptions = compile_frame(frame)
        self.assertEqual(template, "qualification.v1")
        self.assertNotIn("sorry", code)
        self.assertIn("{α : Type}", code)
        self.assertIn('Sanskritree.Relation "QUALIFICATION"', code)
        formalization = persist_formalization(self.conn, frame)
        stored = self.conn.execute("SELECT formal_role, lean_status FROM formalizations WHERE formalization_id=?", (formalization,)).fetchone()
        self.assertEqual(tuple(stored), ("textual_axiom", "uncompiled"))
        ok, output = check_persisted(self.conn, formalization, ROOT / "lean")
        self.assertTrue(ok, output)
        self.assertEqual(self.conn.execute("SELECT lean_status FROM formalizations WHERE formalization_id=?", (formalization,)).fetchone()[0], "typechecked")
        self.assertEqual(self.conn.execute("SELECT immutable FROM translation_candidates WHERE candidate_id=?", (candidate,)).fetchone()[0], 1)

    def test_invalid_ir_and_unsupported_alignment_fail(self):
        with self.assertRaises(ValueError):
            Entity("x", "MadeUp")
        with self.assertRaises(ValueError):
            add_alignment(self.conn, "nope", 2, 1, 0, 1, "one_to_one", 1, {})

    def test_lean_templates_contain_no_placeholders(self):
        for path in (ROOT / "lean").rglob("*.lean"):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("sorry", source)
            self.assertNotIn("admit", source)
            self.assertNotIn("unsafe", source)


if __name__ == "__main__":
    unittest.main()
