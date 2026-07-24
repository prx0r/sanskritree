"""Pipeline test suite — corpus integrity, morphology, segmentation, factor graph, propagation, Lean."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")


class TestCorpusIntegrity(unittest.TestCase):
    """A. Corpus integrity tests."""

    @classmethod
    def setUpClass(cls):
        cls.conn = connect(DB)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_a1_bhairavastava_9_verses(self):
        n = self.conn.execute(
            "SELECT count(*) FROM passages WHERE work_id='abhinavagupta_bhairavastava' AND passage_type='verse'"
        ).fetchone()[0]
        self.assertEqual(n, 9)

    def test_a2_spandakarika_53_verses(self):
        n = self.conn.execute(
            "SELECT count(*) FROM passages WHERE work_id='spandakarika' AND passage_type='verse'"
        ).fetchone()[0]
        self.assertEqual(n, 53)

    def test_a3_no_orphan_readings(self):
        orphans = self.conn.execute("""
            SELECT count(*) FROM passage_readings pr
            WHERE NOT EXISTS (SELECT 1 FROM passages p WHERE p.passage_id = pr.passage_id)
        """).fetchone()[0]
        self.assertEqual(orphans, 0)

    def test_a4_no_empty_readings(self):
        empty = self.conn.execute(
            "SELECT count(*) FROM passage_readings WHERE sanskrit_raw IS NULL OR sanskrit_raw = ''"
        ).fetchone()[0]
        self.assertEqual(empty, 0)

    def test_a5_no_duplicate_ids(self):
        for table in ["passages", "passage_readings", "tokens", "lexeme", "token_occurrence"]:
            dups = self.conn.execute(
                f"SELECT id, count(*) FROM (SELECT rowid as id FROM {table}) GROUP BY id HAVING count(*) > 1"
            ).fetchall()
            self.assertEqual(len(dups), 0, f"{table} has duplicate IDs")


class TestMorphologyCoverage(unittest.TestCase):
    """B. Morphology candidate tests."""

    @classmethod
    def setUpClass(cls):
        cls.conn = connect(DB)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_b1_bhairavastava_tokens_have_hypotheses(self):
        n = self.conn.execute("""
            SELECT count(DISTINCT tocc.occurrence_id) FROM token_occurrence tocc
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id = 'abhinavagupta_bhairavastava'
        """).fetchone()[0]
        n_with = self.conn.execute("""
            SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id = 'abhinavagupta_bhairavastava'
        """).fetchone()[0]
        self.assertGreater(n_with, 0, "No hypotheses for Bhairavastava")
        print(f"\n  Tokens: {n}, With hypotheses: {n_with} ({n_with/max(n,1)*100:.0f}%)")

    def test_b2_vidyut_heritage_engines_recorded(self):
        engines = self.conn.execute("""
            SELECT DISTINCT tah.engine FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id = 'abhinavagupta_bhairavastava'
        """).fetchall()
        engine_names = {r[0] for r in engines}
        self.assertIn("vidyut", engine_names)
        self.assertIn("manual_compound", engine_names)

    def test_b3_no_duplicate_hypotheses(self):
        dups = self.conn.execute("""
            SELECT hypothesis_id, count(*) FROM token_analysis_hypothesis
            GROUP BY hypothesis_id HAVING count(*) > 1
        """).fetchall()
        self.assertEqual(len(dups), 0, f"Duplicate hypothesis IDs: {len(dups)}")


class TestFactorGraph(unittest.TestCase):
    """D. Factor graph determinism tests."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(BASE / "src"))
        from sanskritree.inference.factor_graph import FactorGraph
        from sanskritree.inference.factors import register_graph
        from sanskritree.inference.propagation import propagate_and_score
        cls.FactorGraph = FactorGraph
        cls.register_graph = register_graph
        cls.propagate_and_score = propagate_and_score
        cls.conn = connect(DB)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_d1_bhairavastava_v1_deterministic(self):
        from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
        from sanskritree.inference.factors import register_graph
        from sanskritree.inference.propagation import propagate_and_score

        rid = self.conn.execute("""
            SELECT pr.reading_id FROM passages p
            JOIN passage_readings pr ON pr.passage_id = p.passage_id
            WHERE p.work_id = 'abhinavagupta_bhairavastava' ORDER BY p.sequence_index LIMIT 1
        """).fetchone()[0]

        results = []
        for _ in range(3):
            g = FactorGraph("bhairavastava.1")
            g.neighborhood(self.conn, rid)
            g.add_variable("compound", [
                VariableChoice("k", {"relation": "karmadharaya"}, 0.3),
                VariableChoice("t", {"relation": "tatpurusa"}, -0.3),
            ])
            g.add_variable("frame", [
                VariableChoice("d", {"frame_type": "DevotionalAct"}, 0.3),
                VariableChoice("i", {"frame_type": "IdentityClaim"}, -0.3),
            ])
            register_graph(g)
            best, beliefs, energy = propagate_and_score(g)
            results.append((best.energy, tuple(sorted(beliefs.items()))))

        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i], "Factor graph not deterministic")


class TestPropagation(unittest.TestCase):
    """E. Propagation tests using Bhairavastava factor graph."""

    @classmethod
    def setUpClass(cls):
        from sanskritree.inference.factor_graph import FactorGraph, VariableChoice, Assignment
        from sanskritree.inference.factors import register_graph
        from sanskritree.inference.propagation import compute_beliefs
        cls.FactorGraph = FactorGraph
        cls.VariableChoice = VariableChoice
        cls.Assignment = Assignment
        cls.register_graph = register_graph
        cls.compute_beliefs = compute_beliefs
        cls.conn = connect(DB)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def _make_bv1_graph(self):
        from sanskritree.inference.factors import register_graph
        rid = self.conn.execute("""
            SELECT pr.reading_id FROM passages p
            JOIN passage_readings pr ON pr.passage_id = p.passage_id
            WHERE p.work_id = 'abhinavagupta_bhairavastava' ORDER BY p.sequence_index LIMIT 1
        """).fetchone()[0]
        g = self.FactorGraph("bhairavastava.1")
        g.neighborhood(self.conn, rid)
        g.add_variable("compound", [
            self.VariableChoice("k", {"relation": "karmadharaya"}, 0.3),
            self.VariableChoice("t", {"relation": "tatpurusa"}, -0.3),
        ])
        g.add_variable("frame", [
            self.VariableChoice("d", {"frame_type": "DevotionalAct"}, 0.3),
            self.VariableChoice("i", {"frame_type": "IdentityClaim"}, -0.3),
        ])
        register_graph(g)
        return g, rid

    def test_e1_deterministic(self):
        g1, _ = self._make_bv1_graph()
        g2, _ = self._make_bv1_graph()
        b1 = g1.beam_search(beam_width=20)
        b2 = g2.beam_search(beam_width=20)
        self.assertEqual(b1.energy, b2.energy)
        self.assertEqual(set(b1.choices.keys()), set(b2.choices.keys()))

    def test_e2_convergence(self):
        from sanskritree.inference.propagation import compute_beliefs
        g, rid = self._make_bv1_graph()
        best = g.beam_search(beam_width=20)
        b1 = compute_beliefs(g, best, max_iter=50)
        b2 = compute_beliefs(g, best, max_iter=200)
        for n in b1:
            self.assertAlmostEqual(b1[n], b2[n], places=3, msg=f"{n} did not converge")

    def test_e3_no_nan_inf(self):
        from sanskritree.inference.propagation import compute_beliefs
        g, rid = self._make_bv1_graph()
        best = g.beam_search(beam_width=20)
        beliefs = compute_beliefs(g, best, max_iter=100)
        import math
        for n, v in beliefs.items():
            self.assertFalse(math.isnan(v), f"{n} is NaN")
            self.assertFalse(math.isinf(v), f"{n} is Inf")

    def test_e4_best_assignment_has_no_inf_energy(self):
        g, rid = self._make_bv1_graph()
        best = g.beam_search(beam_width=20)
        self.assertNotEqual(best.energy, float('inf'), "Best assignment has infinite energy")

    def test_e5_karmadharaya_preferred(self):
        g, rid = self._make_bv1_graph()
        from sanskritree.inference.propagation import propagate_and_score
        best, beliefs, energy = propagate_and_score(g)
        kb = beliefs.get("k", 0.0)
        tb = beliefs.get("t", 0.0)
        self.assertGreater(kb, tb, f"karmadharaya ({kb}) should beat tatpurusa ({tb})")


class TestLeanInterface(unittest.TestCase):
    """F. Lean interface tests."""

    def test_f1_lean_compiles(self):
        import subprocess
        result = subprocess.run(
            ["lake", "build", "Sanskritree"],
            cwd=str(BASE / "lean"),
            capture_output=True, text=True,
            env={"PATH": f"{Path.home()}/.elan/bin:{__import__('os').environ.get('PATH', '')}"},
        )
        self.assertEqual(result.returncode, 0, f"Lean build failed:\n{result.stderr}")

    def test_f2_decision_module_exists(self):
        self.assertTrue((BASE / "lean" / "Sanskritree" / "Decision.lean").exists())
        self.assertTrue((BASE / "lean" / "Sanskritree" / "LayerB.lean").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
