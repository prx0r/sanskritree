from __future__ import annotations
import unittest
from sanskritree.integrations.legacy_font import Control, decode_candidate, validate_decoder

class LegacyFontTests(unittest.TestCase):
    def test_failed_control_blocks_candidate_promotion(self):
        controls = [Control("encoded-title", "मन्थानभैरवतन्त्रे", "MBT heading")]
        validation = validate_decoder("test", lambda _: "मन्थानभैतवतन्त्रे", controls)
        self.assertFalse(validation.passed)
        self.assertEqual(decode_candidate("encoded-verse", "test", lambda _: "candidate", validation)["review_status"], "blocked")

    def test_passing_controls_leave_result_as_review_candidate(self):
        controls = [Control("x", "y", "control")]
        validation = validate_decoder("test", lambda value: "y" if value == "x" else value, controls)
        self.assertTrue(validation.passed)
        self.assertEqual(decode_candidate("z", "test", lambda _: "decoded", validation)["review_status"], "candidate_only")
