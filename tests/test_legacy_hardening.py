from __future__ import annotations

import os
import tempfile
import unittest

from proof_engine import algorithm, db
from proof_engine.sanskrit_pipeline import process_sanskrit


class LegacyHardeningTests(unittest.TestCase):
    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.file.close()
        self.conn = db.init_db(self.file.name)

    def tearDown(self):
        self.conn.close()
        os.unlink(self.file.name)

    def test_two_tokens_do_not_create_identity_or_lean_candidate(self):
        result = process_sanskrit("kubjikā śaktiḥ")
        self.assertIsNone(result["nn_expr"])
        self.assertIsNone(result["lean_type_candidate"])

    def test_llm_lean_type_is_ignored(self):
        node = algorithm.process_claim(self.conn, "claim", llm_fn=lambda *_: {"sayable": True, "lean_type": "False", "children": []}, fast_mode=True)
        self.assertIsNone(db.get_node(self.conn, node)["lean_type"])

    def test_definition_is_an_axiom_not_a_proof(self):
        parent = db.add_node(self.conn, None, "parent")
        child = db.add_node(self.conn, parent, "definition", node_type="DEFINITION", status="UNPROVED", formal_role="textual_axiom")
        self.assertEqual(db.get_node(self.conn, child)["formal_role"], "textual_axiom")
        self.assertNotEqual(algorithm.propagate(self.conn, parent), "PROVED")

    def test_retries_run_to_limit(self):
        original = algorithm.lean_checker.pantograph_check
        calls = []
        algorithm.lean_checker.pantograph_check = lambda *_args, **_kwargs: calls.append(1) or {"status": "UNPROVED", "proof": None, "mathlib_deps": []}
        try:
            algorithm.process_claim(self.conn, "claim", formalize_fn=lambda *_: "P", fast_mode=True)
        finally:
            algorithm.lean_checker.pantograph_check = original
        self.assertEqual(len(calls), algorithm.MAX_RETRIES)


if __name__ == "__main__":
    unittest.main()
