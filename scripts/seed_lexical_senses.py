"""Seed the lexical_senses table with Spanda-domain sense entries.
Each sense has: lemma, tradition, gloss, definition, semantic_class.
After seeding, link senses to works via sense_attestation.
"""
from __future__ import annotations
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parents[1]
import sys
sys.path.insert(0, str(BASE / "src"))
from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")

# Sense entries: lemma, tradition, gloss, definition, semantic_class
SPANDA_SENSES = [
    # ── kalā ──
    ("kalA", "spanda", "principle of limitation",
     "One of the five kañcukas (limiting principles). Limited agency/power that obscures the bound soul's true omnipotence.",
     "TECHNICAL_TERM"),
    ("kalA", "general", "art, skill, craft",
     "A practical art or creative skill, e.g., music, dance, painting.",
     "COMMON_NOUN"),
    ("kalA", "general", "a small part, a portion",
     "A division, part, or digit of the moon.",
     "COMMON_NOUN"),
    
    # ── paśu / paSu ──
    ("paSu", "spanda", "bound soul, fettered being",
     "The individual soul under the three bonds (mala, karma, māyā). Not 'beast' in this context.",
     "TECHNICAL_TERM"),
    ("paSu", "general", "beast, animal, cattle",
     "A domesticated quadruped or wild animal.",
     "COMMON_NOUN"),
    
    # ── pada ──
    ("pada", "spanda", "state, condition, level of being",
     "A spiritual station or level of consciousness. In 'pada-dvaya', refers to the two states (waking and dreaming).",
     "TECHNICAL_TERM"),
    ("pada", "general", "foot",
     "The lower extremity of the leg.",
     "COMMON_NOUN"),
    ("pada", "general", "word, term",
     "A unit of language.",
     "COMMON_NOUN"),
    
    # ── unmeṣa / unmeza ──
    ("unmeza", "spanda", "opening/expansion of consciousness",
     "The outward-directed movement of consciousness that manifests the universe. Contrasted with nimeṣa (contraction/withdrawal).",
     "TECHNICAL_TERM"),
    ("unmeza", "general", "glance, look, flash of the eye",
     "A brief visual opening or look.",
     "COMMON_NOUN"),
    
    # ── pratyaya ──
    ("pratyaya", "spanda", "cognition, mental representation",
     "A unit of awareness or mental event. Not 'faith' or 'belief' in this context.",
     "TECHNICAL_TERM"),
    ("pratyaya", "general", "faith, trust, belief",
     "Confidence or reliance in someone or something.",
     "COMMON_NOUN"),
    ("pratyaya", "grammar", "affix, suffix",
     "A grammatical formative element.",
     "GRAMMATICAL"),
    
    # ── śakti / Sakti ──
    ("Sakti", "spanda", "conscious power, dynamic energy of Śiva",
     "The active aspect of Supreme Consciousness that creates, sustains, and withdraws the universe.",
     "TECHNICAL_TERM"),
    ("Sakti", "general", "power, capacity, ability",
     "The capability to produce an effect.",
     "COMMON_NOUN"),
    
    # ── spanda ──
    ("spanda", "spanda", "vibratory dynamism of consciousness",
     "The central doctrine of the Spanda school. The self-motive pulse of Śiva's consciousness that manifests as the universe.",
     "TECHNICAL_TERM"),
    ("spanda", "general", "vibration, trembling, throb",
     "A slight shaking or oscillatory movement.",
     "COMMON_NOUN"),
    
    # ── bandhayitrī / banDayitrI ──
    ("banDayitrI", "spanda", "She who binds (a form of Śakti)",
     "The power of Śiva's consciousness that binds the fettered soul. A feminine divinity or aspect of Śakti.",
     "TECHNICAL_TERM"),
    
    # ── śabdānuvedha / Sap1 ──
    ("Sap1", "spanda", "penetration/impregnation by speech",
     "The process by which linguistic cognition enters and structures awareness.",
     "TECHNICAL_TERM"),
    
    # ── dīkṣā / dIkzA ──
    ("dIkzA", "spanda", "spiritual initiation, consecration",
     "The transmission of spiritual power and knowledge from teacher to disciple.",
     "TECHNICAL_TERM"),
    ("dIkzA", "general", "initiation, consecration",
     "A ceremony admitting someone into a group or tradition.",
     "COMMON_NOUN"),
    
    # ── mūḍha / mUDa ──
    ("mUDa", "spanda", "deluded, spiritually ignorant one",
     "One who is confused about their true nature due to the veiling power of māyā.",
     "TECHNICAL_TERM"),
    ("mUDa", "general", "foolish, stupid, bewildered",
     "Lacking intelligence or common sense.",
     "COMMON_NOUN"),
    
    # ── nirvāṇa / nirvARa ──
    ("nirvARa", "spanda", "liberation, spiritual freedom",
     "The state of release from the cycle of rebirth, the highest goal.",
     "TECHNICAL_TERM"),
    ("nirvARa", "general", "extinction, blowing out",
     "The act of being extinguished, cooling.",
     "COMMON_NOUN"),
    
    # ── ātman / Atman ──
    ("Atman", "spanda", "the Self, pure consciousness",
     "One's true nature as identical with Śiva. The innermost reality.",
     "TECHNICAL_TERM"),
    ("Atman", "general", "self, soul, essence",
     "The essential nature of a person.",
     "COMMON_NOUN"),
    
    # ── siddhi ──
    ("siddhi", "spanda", "spiritual accomplishment, perfection",
     "The attainments gained through practice, including both mystical powers and liberation.",
     "TECHNICAL_TERM"),
    ("siddhi", "general", "success, accomplishment, fulfillment",
     "The achievement of a desired goal.",
     "COMMON_NOUN"),
    
    # ── smaryamāṇa / smaryamARatva ──
    ("smaryamARatvam", "spanda", "state of being remembered",
     "The condition of being an object of memory rather than directly perceived.",
     "TECHNICAL_TERM"),
    
    # ── adhikāra / aDikAra ──
    ("aDikAra", "spanda", "spiritual qualification, authority",
     "The eligibility or competence for a particular spiritual path or practice.",
     "TECHNICAL_TERM"),
    ("aDikAra", "general", "authority, right, title",
     "The power or right to do something.",
     "COMMON_NOUN"),
    
    # ── tattva ──
    ("tattva", "spanda", "reality, principle, category of existence",
     "A fundamental category of reality. In Śaiva systems, there are 36 tattvas.",
     "TECHNICAL_TERM"),
    ("tattva", "general", "truth, reality, essence",
     "The true nature of something.",
     "COMMON_NOUN"),
    
    # ── kṣobha / kzoBa ──
    ("kzoBa", "spanda", "agitation, disruption of the sense of separate self",
     "The spiritual turmoil that arises from ego-identification and dissolves upon awakening.",
     "TECHNICAL_TERM"),
    ("kzoBa", "general", "agitation, disturbance, shaking",
     "A state of nervous or emotional disturbance.",
     "COMMON_NOUN"),
    
    # ── śiva / Siva ──
    ("Siva", "spanda", "Śiva, Supreme Consciousness",
     "The ultimate reality in Kashmir Shaivism. Pure consciousness, the ground of all existence.",
     "TECHNICAL_TERM"),
    ("Siva", "general", "auspicious, benign, gracious",
     "The quality of being propitious or benevolent.",
     "COMMON_NOUN"),
    
    # ── cakra ──
    ("cakra", "spanda", "wheel of energies, circle of śaktis",
     "The dynamic complex of powers surrounding and emanating from Śiva.",
     "TECHNICAL_TERM"),
    ("cakra", "general", "wheel, disc, circle",
     "A circular object or formation.",
     "COMMON_NOUN"),
    
    # ── saṃsāra / saMsAra ──
    ("saMsAra", "spanda", "cycle of rebirth, conditioned existence",
     "The realm of birth, death, and rebirth from which liberation is sought.",
     "TECHNICAL_TERM"),
    ("saMsAra", "general", "world, worldly existence",
     "The cycle of transmigration.",
     "COMMON_NOUN"),
    
    # ── māyā / mAya ──
    ("mAya", "spanda", "principle of manifestation/limitation",
     "In nondual Śaivism, the power through which the one appears as many. NOT 'illusion.'",
     "TECHNICAL_TERM"),
    ("mAya", "general", "illusion, magic, deception",
     "Something that deceives by producing a false impression.",
     "COMMON_NOUN"),
    
    # ── jīvanmukta / jIvanmukta ──
    ("jIvanmukta", "spanda", "liberated while living",
     "One who has attained liberation while still embodied.",
     "TECHNICAL_TERM"),
    
    # ── kañcuka ──
    ("kaYcuka", "spanda", "limiting sheath, vesture",
     "One of the five principles (kalā, vidyā, rāga, niyati, kāla) that limit the bound soul.",
     "TECHNICAL_TERM"),
    
    # ── dānu / dAnu ──
    ("dAnu", "general", "giving, donation",
     "The act of giving (from dā 'to give').",
     "COMMON_NOUN"),
    
    # ── vedha / veDa ──
    ("veDa", "general", "piercing, penetration",
     "The act of piercing through.",
     "COMMON_NOUN"),
    ("veDa", "spanda", "penetration (by speech/sound)",
     "The process by which linguistic cognition enters awareness.",
     "TECHNICAL_TERM"),
    
    # ── laukika / lOkika ──
    ("lOkika", "general", "worldly, ordinary, mundane",
     "Pertaining to everyday worldly life as distinct from spiritual practice.",
     "COMMON_NOUN"),
]

# Works by tradition proximity
SPANDA_WORKS = {
    "spandakarika": "spanda",
    "abhinavagupta_bhairavastava": "spanda",
    "vijnanabhairava": "trika",
    "bhagavad_gita": "vedanta",
}


def seed_senses(conn):
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    for lemma, tradition, gloss, definition, sem_class in SPANDA_SENSES:
        sense_id = f"sense_{lemma}_{tradition}_{gloss[:16]}"
        conn.execute(
            "INSERT OR IGNORE INTO lexical_senses (sense_id, lemma, tradition, historical_layer, short_gloss, definition, semantic_class) VALUES (?,?,?,?,?,?,?)",
            (sense_id, lemma, tradition, "contemporary", gloss, definition, sem_class),
        )
        count += conn.total_changes
    conn.commit()
    print(f"Seeded {count} senses")


def attest_senses(conn):
    """Link senses to works via existing occurrences."""
    now = datetime.now(timezone.utc).isoformat()
    
    # Create sense_attestation table if needed
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sense_attestation (
            attestation_id TEXT PRIMARY KEY,
            sense_id TEXT NOT NULL REFERENCES lexical_senses(sense_id),
            work_id TEXT NOT NULL,
            passage_id TEXT,
            occurrence_id TEXT,
            evidence_type TEXT NOT NULL,
            proximity_tier INTEGER,
            source TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(sense_id, work_id, passage_id, evidence_type)
        )
    """)
    
    # Get all works
    works = conn.execute("SELECT work_id, count FROM (SELECT p.work_id, COUNT(*) as count FROM passages p GROUP BY p.work_id) ORDER BY count DESC").fetchall()
    work_list = [w[0] for w in works]
    
    attest_count = 0
    
    # For each Spanda sense, find occurrences in works
    senses = conn.execute("SELECT sense_id, lemma, tradition FROM lexical_senses WHERE tradition='spanda'").fetchall()
    for sense_id, lemma, tradition in senses:
        # Find this lemma in works of the same tradition
        for work_id in work_list:
            trail = SPANDA_WORKS.get(work_id, "unknown")
            proximity = 2 if trail == tradition else 4 if trail in ("trika", "saiva") else 8
            
            # Find passages where this lemma appears as accepted
            passages = conn.execute("""
                SELECT DISTINCT p.passage_id
                FROM passages p
                JOIN passage_readings pr ON pr.passage_id = p.passage_id
                JOIN token_occurrence tocc ON tocc.passage_reading_id = pr.reading_id
                JOIN token_analysis_hypothesis tah ON tah.occurrence_id = tocc.occurrence_id
                JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
                JOIN lexeme lex ON lex.lexeme_id = mat.lexeme_id
                WHERE p.work_id = ? AND lex.lemma_slp1 = ?
                LIMIT 3
            """, (work_id, lemma)).fetchall()
            
            for passage in passages:
                att_id = f"att_{sense_id}_{work_id}_{passage[0][:16]}"
                conn.execute(
                    "INSERT OR IGNORE INTO sense_attestation (attestation_id, sense_id, work_id, passage_id, evidence_type, proximity_tier, source, created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (att_id, sense_id, work_id, passage[0], "SAME_WORK_OCCURRENCE", proximity, "automatic_seeding", now),
                )
                attest_count += 1
    
    conn.commit()
    print(f"Attested {attest_count} sense occurrences")


def main():
    conn = connect(DB)
    seed_senses(conn)
    attest_senses(conn)
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM lexical_senses").fetchone()[0]
    att_count = conn.execute("SELECT COUNT(*) FROM sense_attestation").fetchone()[0]
    print(f"\nlexical_senses: {count} rows")
    print(f"sense_attestation: {att_count} rows")
    
    # Show sample
    print("\nSample senses:")
    for r in conn.execute("SELECT sense_id, lemma, tradition, short_gloss FROM lexical_senses WHERE tradition='spanda' LIMIT 10").fetchall():
        print(f"  {r[0]}: {r[1]} [{r[2]}] = {r[3]}")
    
    conn.close()


if __name__ == "__main__":
    main()
