"""Anti-overfitting tests: ensure no verse-ID-specific rules or hard-coded translations."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

import inspect
import importlib


class TestAntiOverfitting(unittest.TestCase):

    def test_no_translation_rule_mentions_spanda_passage_id(self):
        """Check source code for passage-ID-specific patterns."""
        src_dir = Path(__file__).parents[1] / "src"
        offending = []
        for f in sorted(src_dir.rglob("*.py")):
            rel = f.relative_to(src_dir.parent)
            content = f.read_text()
            # Look for patterns like 'spk.1.1' or 'spk_1_1' in string literals
            if "spk." in content or "spk_" in content:
                # Exclude test files and seed data
                if "test_" not in f.name and "seed_" not in f.name:
                    for i, line in enumerate(content.split("\n"), 1):
                        if "spk." in line or "spk_" in line:
                            if "#" not in line.strip()[:2]:  # not a comment
                                offending.append(f"{rel}:{i}: {line.strip()[:80]}")
        if offending:
            for o in offending[:10]:
                print(f"  {o}")
        self.assertEqual(len(offending), 0, f"Found {len(offending)} passage-ID references in source code")

    def test_no_renderer_override_uses_exact_source_string(self):
        """Check that no rule matches exact Sanskrit source strings."""
        src_dir = Path(__file__).parents[1] / "src"
        for f in src_dir.rglob("*.py"):
            content = f.read_text()
            # Check for long Sanskrit strings (>30 chars) that might be verse-specific
            import re
            sanskrit_patterns = re.findall(r'["\']([\w\sāīūṛṝḷḹēōṃḥṅñṭḍṇśṣ\-\.]+)["\']', content)
            for p in sanskrit_patterns:
                if len(p) > 40 and any(c in p for c in 'āīūṛṝ'):
                    print(f"  POTENTIAL VERSE STRING in {f.name}: {p[:60]}")
                    self.fail(f"Hard-coded source string in {f.name}")

    def test_lexical_glossary_is_not_verse_specific(self):
        """Verify glossary entries don't reference specific verses."""
        from sanskritree.evidence.ranker import TECHNICAL_TERMS_KS
        from sanskritree.evidence.lexical import KS_GUY_GLOSSARY
        
        for name, glossary in [("TECHNICAL_TERMS_KS", TECHNICAL_TERMS_KS),
                                ("KS_GUY_GLOSSARY", KS_GUY_GLOSSARY)]:
            for key, value in glossary.items():
                if isinstance(value, tuple):
                    val = value[0]
                else:
                    val = value
                if "spk" in val.lower() or "sp." in val.lower():
                    self.fail(f"{name}[{key}] = {val[:60]} — verse-specific reference")

    def test_heritage_candidates_record_provenance(self):
        """Verify Heritage retry candidates are labelled."""
        from sanskritree.database import connect
        conn = connect(str(Path(__file__).parents[1] / "data" / "sanskritree-v2.db"))
        retry = conn.execute(
            "SELECT count(*) FROM token_analysis_hypothesis WHERE engine='heritage_retry'"
        ).fetchone()[0]
        self.assertGreater(retry, 0, "No heritage_retry candidates found")
        conn.close()

    def test_sense_table_has_tradition_entries(self):
        """Verify lexical_senses table has tradition-scoped entries."""
        from sanskritree.database import connect
        conn = connect(str(Path(__file__).parents[1] / "data" / "sanskritree-v2.db"))
        spanda = conn.execute(
            "SELECT count(*) FROM lexical_senses WHERE tradition='spanda'"
        ).fetchone()[0]
        general = conn.execute(
            "SELECT count(*) FROM lexical_senses WHERE tradition='general'"
        ).fetchone()[0]
        self.assertGreater(spanda, 0, "No Spanda-tradition senses")
        self.assertGreater(general, 0, "No general-tradition senses")
        conn.close()

    def test_heritage_retry_improves_coverage(self):
        """Verify that spk.3.3 now has better coverage."""
        from sanskritree.database import connect
        conn = connect(str(Path(__file__).parents[1] / "data" / "sanskritree-v2.db"))
        lemmas = conn.execute("""
            SELECT COUNT(DISTINCT lex.lemma_slp1)
            FROM lexeme lex
            JOIN morph_analysis_type mat ON mat.lexeme_id = lex.lexeme_id
            JOIN token_analysis_hypothesis tah ON tah.analysis_type_id = mat.analysis_type_id
            JOIN token_occurrence tocc ON tocc.occurrence_id = tah.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            WHERE pr.passage_id = 'spk.3.3'
        """).fetchone()[0]
        self.assertGreater(lemmas, 3, f"spk.3.3 only has {lemmas} lemmas — Heritage retry may not have applied")
        conn.close()


if __name__ == "__main__":
    unittest.main()
