"""Phase C3a: Seed critical compound members + Tantra vocabulary.

Adds known word parts from active works (Bhairavastava, Spandakārikā)
and common Tantric terminology to the lexeme table so the compound
splitter can generate valid split hypotheses.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect


def slp1(word: str) -> str:
    """IAST → SLP1 conversion."""
    m = {
        'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṝ': 'F', 'ḹ': 'X',
        'ṛ': 'f', 'ḷ': 'x',
        'ṃ': 'M', 'ḥ': 'H',
        'ñ': 'Y', 'ṭ': 'T', 'ḍ': 'D', 'ṇ': 'N',
        'ś': 'S', 'ṣ': 'z',
    }
    return ''.join(m.get(c, c) for c in word)


# Vocabulary to seed: (iast, pos, english_gloss)
VOCABULARY = [
    # ── Bhairavastava compounds ──
    ("bhairava", "noun", "Bhairava, the terrifying aspect of Siva"),
    ("nātha", "noun", "lord, protector, refuge"),
    ("anātha", "adj", "without a protector, helpless"),
    ("śaraṇa", "noun", "refuge, protection"),
    ("śaraṇya", "adj", "affording protection, a refuge"),
    ("tvanmaya", "adj", "consisting of you, filled with you"),
    ("tvad", "pron", "you (stem form)"),
    ("citta", "noun", "mind, consciousness"),
    ("cittatā", "noun", "the state of mind"),
    ("maya", "suffix", "made of, consisting of"),
    ("tā", "suffix", "abstract noun suffix (-ness, -ity)"),
    ("śaṅkara", "noun", "Sankara, Siva"),
    ("sevana", "noun", "service, devotion"),
    ("cintana", "noun", "thought, contemplation"),
    ("dhīra", "adj", "steadfast, firm, wise"),
    ("bhīṣaṇa", "adj", "terrible, fearsome"),
    ("śakti", "noun", "power, energy, Sakti"),
    ("śaktimaya", "adj", "consisting of power, filled with power"),
    ("maya", "suffix", "made of"),
    ("mṛtyu", "noun", "death"),
    ("yama", "noun", "Yama (god of death), restraint"),
    ("antaka", "noun", "the end-maker, death"),
    ("piśāca", "noun", "demon, goblin"),
    ("bhāva", "noun", "being, state, true condition"),
    ("parāmṛta", "noun", "supreme nectar, ambrosia"),
    ("nirbhara", "adj", "full, filled with, abundant"),
    ("pūrṇa", "adj", "full, complete"),
    ("abheda", "noun", "non-difference, unity, oneness"),
    ("stotra", "noun", "hymn, praise"),
    ("vṛṣṭi", "noun", "rain, shower"),
    ("tāvaka", "adj", "your, belonging to you"),
    ("śāstra", "noun", "teaching, scripture"),
    ("cintā", "noun", "thought, reflection"),
    ("sudarśana", "adj", "beautiful, lovely to behold"),
    ("durlabha", "adj", "hard to obtain, rare"),
    ("samayajña", "adj", "knower of the right time/moment"),
    ("anyajana", "noun", "other people"),
    ("māyā", "noun", "illusion, Maya"),

    # ── Spandakārikā compounds ──
    ("śakti", "noun", "power, energy"),
    ("cakra", "noun", "wheel, cycle, collection"),
    ("vibhava", "noun", "power, might, manifestation"),
    ("prabhava", "noun", "source, origin, manifestation"),
    ("unmeṣa", "noun", "opening, expansion, manifestation"),
    ("nimeṣa", "noun", "closing, contraction, withdrawal"),
    ("jagat", "noun", "world, universe"),
    ("pralaya", "noun", "dissolution, destruction"),
    ("udaya", "noun", "rising, coming forth, emergence"),
    ("nirodha", "noun", "cessation, restraint, obstruction"),
    ("karaṇa", "noun", "cause, instrument, sense organ"),
    ("varga", "noun", "group, class, collection"),
    ("jñāna", "noun", "knowledge, wisdom"),
    ("kriyā", "noun", "action, activity"),
    ("icchā", "noun", "will, desire"),
    ("sphura", "verb", "to throb, shine forth, manifest"),
    ("spanda", "noun", "vibration, throb, dynamic impulse"),
    ("madhya", "noun", "middle, center, between"),
    ("prāṇa", "noun", "vital breath, life force"),
    ("bhairava", "noun", "Bhairava"),
    ("sva", "adj", "one's own, self"),
    ("bhāva", "noun", "state, nature, feeling"),
    ("tattva", "noun", "truth, reality, principle"),
    ("artha", "noun", "meaning, object, purpose"),
    ("ātman", "noun", "self, soul"),
    ("paramātman", "noun", "supreme self"),
    ("śiva", "noun", "Siva, auspicious one"),
    ("śakti", "noun", "power, energy"),
    ("bīja", "noun", "seed, seed-mantra"),
    ("mantra", "noun", "mantra, sacred utterance"),
    ("deva", "noun", "god, deity"),
    ("devī", "noun", "goddess"),
    ("yogin", "noun", "yogi, practitioner"),
    ("yoginī", "noun", "yogini, female practitioner"),
    ("kula", "noun", "family, lineage, totality"),
    ("akula", "noun", "beyond Kula, absolute"),
    ("kaula", "adj", "belonging to the Kula tradition"),

    # ── Common grammatical words needed for compound splitting ──
    ("su", "prefix", "good, well, beautiful"),
    ("ati", "prefix", "excess, beyond"),
    ("sam", "prefix", "together, complete"),
    ("vi", "prefix", "apart, distinct"),
    ("ni", "prefix", "down, into"),
    ("pra", "prefix", "forth, forward"),
    ("ā", "prefix", "towards, near"),
    ("ud", "prefix", "up, upward"),
    ("amṛta", "adj", "immortal, nectar"),
    ("praśna", "noun", "question, inquiry"),
    ("uttara", "noun", "answer, reply, superior"),
    ("sūtra", "noun", "thread, aphorism, rule"),
    ("bhāṣya", "noun", "commentary, explanation"),
    ("vārttika", "noun", "critical commentary, gloss"),
    ("kārikā", "noun", "explanatory verse"),
    ("śāstra", "noun", "treatise, scripture"),
    ("tantra", "noun", "tantra, treatise, system"),
    ("āgama", "noun", "scripture, traditional doctrine"),
    ("nigama", "noun", "veda, scripture"),
    ("āmnāya", "noun", "tradition, transmission, scripture"),
    ("darśana", "noun", "vision, philosophy, system"),

    # ── Case endings (for better compound recognition) ──
    ("am", "suffix", "accusative singular ending"),
    ("am", "suffix", "accusative singular"),
    ("āya", "suffix", "dative singular"),
    ("āt", "suffix", "ablative singular"),
    ("asya", "suffix", "genitive singular"),
    ("e", "suffix", "locative singular / dative singular"),
    ("ena", "suffix", "instrumental singular"),
    ("aiḥ", "suffix", "instrumental plural"),
    ("ānām", "suffix", "genitive plural"),

    # ── Additional verbs appearing in the texts ──
    ("vand", "verb", "to praise, worship, salute"),
    ("stu", "verb", "to praise, extol"),
    ("bhaj", "verb", "to worship, adore, share"),
    ("dā", "verb", "to give"),
    ("kṛ", "verb", "to do, make"),
    ("bhū", "verb", "to be, become"),
    ("as", "verb", "to be"),
    ("i", "verb", "to go"),
    ("gam", "verb", "to go"),
    ("vid", "verb", "to know"),
    ("jñā", "verb", "to know"),
    ("dṛś", "verb", "to see"),
    ("śru", "verb", "to hear"),
    ("vad", "verb", "to speak"),
    ("vac", "verb", "to speak"),
    ("āp", "verb", "to obtain, reach"),
    ("syand", "verb", "to flow, glide"),
    ("nī", "verb", "to lead"),
    ("pā", "verb", "to drink, protect"),
    ("hrī", "verb", "to be ashamed"),

    # ── Common indeclinables ──
    ("ca", "indeclinable", "and"),
    ("na", "indeclinable", "not"),
    ("api", "indeclinable", "also, even, though"),
    ("eva", "indeclinable", "indeed, exactly, just"),
    ("hi", "indeclinable", "for, because, indeed"),
    ("tu", "indeclinable", "but, now, then"),
    ("cet", "indeclinable", "if"),
    ("vā", "indeclinable", "or"),
    ("iti", "indeclinable", "thus, end quote"),
    ("yad", "indeclinable", "since, because, that"),
    ("tad", "pron", "that, this, it"),
    ("etad", "pron", "this, this here"),
    ("kim", "pron", "what, who, which"),
    ("aham", "pron", "I"),
    ("tvam", "pron", "you"),
    ("sa", "pron", "he, that"),
    ("sā", "pron", "she, that"),
    ("mad", "pron", "I (stem), my"),
    ("tvad", "pron", "you (stem), your"),
    ("asmad", "pron", "we (stem)"),
    ("yuṣmad", "pron", "you (pl, stem)"),
    ("dva", "num", "two"),
    ("tri", "num", "three"),
    ("bahu", "adj", "many, much"),
    ("sarva", "adj", "all, every, whole"),
    ("eka", "adj", "one, alone, single"),
    ("para", "adj", "other, supreme, highest"),
    ("nitya", "adj", "constant, eternal, regular"),
    ("satya", "adj", "true, real, genuine"),
    ("param", "adv", "supremely, ultimately"),
    ("sadā", "adv", "always, constantly"),
    ("sarvadā", "adv", "always, at all times"),
    ("tathā", "adv", "thus, so, in that way"),
    ("yathā", "adv", "as, just as, according to"),
    ("katham", "adv", "how, why, in what way"),
    ("atra", "adv", "here, in this matter"),
    ("tatra", "adv", "there, in that matter"),
]


def iast_to_slp1(word: str) -> str:
    mapping = {
        'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṝ': 'F', 'ḹ': 'X',
        'ṛ': 'f', 'ḷ': 'x',
        'ṃ': 'M', 'ḥ': 'H',
        'ñ': 'Y', 'ṭ': 'T', 'ḍ': 'D', 'ṇ': 'N',
        'ś': 'S', 'ṣ': 'z',
    }
    return ''.join(mapping.get(c, c) for c in word)


def seed_tantra_vocabulary(conn):
    """Seed the vocabulary list into the lexeme table."""
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    errors = 0

    for iast, pos, gloss in VOCABULARY:
        slp1_form = iast_to_slp1(iast)
        lid = f"lex_vocab_{slp1_form}"

        try:
            conn.execute("""INSERT OR IGNORE INTO lexeme
                (lexeme_id, lemma_slp1, lemma_iast, pos, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (lid, slp1_form, iast, pos, now))
            if conn.total_changes:
                count += 1
        except Exception:
            errors += 1

    conn.commit()
    print(f"  {count} vocabulary items seeded ({errors} errors)")


def generate_compound_hypotheses(conn, work_id: str):
    """Re-run compound splitting with enriched vocabulary using Vidyut transliteration."""
    import json
    import re
    from datetime import datetime, timezone

    now2 = datetime.now(timezone.utc).isoformat()

    # Load Vidyut transliterator
    try:
        from vidyut.lipi import transliterate, Scheme
        has_vidyut = True
    except ImportError:
        has_vidyut = False

    # Load all lexeme SLP1 forms
    lemmas = {r[0] for r in conn.execute("SELECT lemma_slp1 FROM lexeme").fetchall()}

    # Scan passages in the work
    passages = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """, (work_id,)).fetchall()

    total = 0
    for pid, rid, raw in passages:
        clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', raw).strip()
        tokens = clean.split()
        for idx, token in enumerate(tokens):
            # Check if token already has a lemma analysis
            has_lemma = conn.execute("""
                SELECT 1 FROM token_analysis_hypothesis tah
                JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
                JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
                WHERE tocc.passage_reading_id = ? AND tocc.token_index = ?
                  AND mat.lexeme_id != 'lex_unknown' LIMIT 1
            """, (rid, idx)).fetchone()
            if has_lemma:
                continue

            # Try to split: convert IAST to SLP1 using Vidyut
            if has_vidyut:
                try:
                    slp1_form = transliterate(token, Scheme.Iast, Scheme.Slp1)
                except Exception:
                    slp1_form = token.lower()
            else:
                slp1_form = token.lower()

            # Generate all possible splits at any position
            n = len(slp1_form)
            splits_found = []
            for split_pos in range(2, n - 1):
                left = slp1_form[:split_pos]
                right = slp1_form[split_pos:]
                if left in lemmas and right in lemmas:
                    splits_found.append((left, right))

            if splits_found:
                for left, right in splits_found:
                    # Find actual lexeme_id for each member
                    lid = conn.execute(
                        "SELECT lexeme_id FROM lexeme WHERE lemma_slp1 = ? LIMIT 1",
                        (left,)
                    ).fetchone()
                    if not lid:
                        continue
                    lid = lid[0]

                    atype_id = f"cmp_{rid}_{idx}_{left}+{right}"
                    features = json.dumps({
                        "compound_members": [left, right],
                        "compound_relation": "unknown",
                    })
                    try:
                        conn.execute("""INSERT INTO morph_analysis_type
                            (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                            VALUES (?, ?, ?, ?, ?)""",
                            (atype_id, lid, features, f"cmp_{left}+{right}"[:16], now2))
                    except Exception:
                        continue  # FK or duplicate, skip

                    occs = conn.execute("""
                        SELECT occurrence_id FROM token_occurrence
                        WHERE passage_reading_id = ? AND token_index = ?
                    """, (rid, idx)).fetchall()
                    for (occ_id,) in occs:
                        hyp_id = f"hyp_compound_{rid}_{idx}_{left}+{right}"
                        try:
                            conn.execute("""INSERT INTO token_analysis_hypothesis
                                (hypothesis_id, occurrence_id, analysis_type_id, engine,
                                 confidence, status, created_at)
                                VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
                                (hyp_id, occ_id, atype_id, "compound_splitter_v2",
                                 0.4, now2))
                            total += 1
                        except Exception:
                            continue
            conn.commit()

    print(f"  {total} compound split hypotheses generated")


def verify_coverage(conn, work_id: str):
    """Check how many tokens now have hypotheses."""
    passages = conn.execute("""
        SELECT p.verse_start, pr.reading_id
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """, (work_id,)).fetchall()

    total_tokens = 0
    total_with_lemma = 0
    for vs, rid in passages:
        tokens = conn.execute("""
            SELECT count(*) FROM token_occurrence
            WHERE passage_reading_id = ?
        """, (rid,)).fetchone()[0]

        with_lemma = conn.execute("""
            SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
            WHERE tocc.passage_reading_id = ? AND mat.lexeme_id != 'lex_unknown'
        """, (rid,)).fetchone()[0]

        total_tokens += tokens
        total_with_lemma += with_lemma

    print(f"\n  Coverage for {work_id}:")
    print(f"    Tokens: {total_tokens}")
    print(f"    With lemma: {total_with_lemma}")
    print(f"    Coverage: {total_with_lemma/max(total_tokens,1)*100:.1f}%")


def main():
    print("=" * 60)
    print("PHASE C3a — Seed Tantra vocabulary")
    print("=" * 60)

    db_path = BASE / "data" / "sanskritree-v2.db"
    conn = connect(str(db_path))

    # Ensure unknown placeholder
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""INSERT OR IGNORE INTO lexeme
        (lexeme_id, lemma_slp1, lemma_iast, pos, created_at)
        VALUES ('lex_unknown', '__unknown__', '__unknown__', 'unknown', ?)""", (now,))
    conn.commit()

    print("\n[1] Seeding vocabulary...")
    seed_tantra_vocabulary(conn)

    print("\n[2] Re-running compound generation for active works...")
    for wid in ["abhinavagupta_bhairavastava", "spandakarika"]:
        print(f"\n  --- {wid} ---")
        generate_compound_hypotheses(conn, wid)

    print("\n[3] Coverage verification...")
    for wid in ["abhinavagupta_bhairavastava", "spandakarika"]:
        verify_coverage(conn, wid)

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
