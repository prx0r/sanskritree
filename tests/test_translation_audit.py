"""Tests for translation audit: mutation detection, licence validation."""
import hashlib
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from sanskritree.translation.render_literal import literal_render, validate_licence, LicensedOutput, Span
from sanskritree.audit.translation import audit_mutation, run_audit_suite


class TestLiteralRender(unittest.TestCase):

    def test_render_simple_verse(self):
        output = literal_render(["vand", "tad", "SaMkara"], "DevotionalAct")
        self.assertIn("I praise", output.text)
        self.assertIn("[DevotionalAct]", output.text)

    def test_every_content_span_has_semantic_licence(self):
        output = literal_render(["tad", "Sakti", "cakra"])
        errors = validate_licence(output)
        self.assertEqual(len(errors), 0)

    def test_negation_node_must_be_realized(self):
        output = literal_render(["na", "asti"], polarity="negative")
        self.assertIn("not", output.text)

    def test_unknown_lemma_marked_uncertain(self):
        output = literal_render(["xyzzy_unknown"])
        self.assertTrue(len(output.uncertainties) > 0)

    def test_literal_renderer_is_deterministic(self):
        r1 = literal_render(["tad", "Sakti", "cakra"])
        r2 = literal_render(["tad", "Sakti", "cakra"])
        self.assertEqual(r1.text, r2.text)
        self.assertEqual(len(r1.spans), len(r2.spans))


class TestTranslationAudit(unittest.TestCase):

    def test_negation_mutation_detected(self):
        result = audit_mutation("He is happy", "negation", {"polarity": "negative"})
        self.assertFalse(result["pass"])

    def test_negation_ok_when_present(self):
        result = audit_mutation("He is not happy", "negation", {"polarity": "negative"})
        self.assertTrue(result["pass"])

    def test_unsupported_addition_detected(self):
        result = audit_mutation("Siva is supreme", "unsupported_addition",
                                {"lemmas": ["tad", "asti"]})
        self.assertFalse(result["pass"])

    def test_supported_doctrine_ok(self):
        result = audit_mutation("Siva is supreme", "unsupported_addition",
                                {"lemmas": ["Siva", "asti"]})
        self.assertTrue(result["pass"])

    def test_source_hash_mismatch_detected(self):
        result = audit_mutation("text", "source_hash",
                                {"expected_hash": "abc", "actual_hash": "xyz"})
        self.assertFalse(result["pass"])

    def test_source_hash_match_ok(self):
        h = hashlib.sha256(b"test").hexdigest()
        result = audit_mutation("text", "source_hash",
                                {"expected_hash": h, "actual_hash": h})
        self.assertTrue(result["pass"])

    def test_empty_audit_suite(self):
        results = run_audit_suite("Some text", {"polarity": "positive", "lemmas": ["some"]})
        self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
