"""Lexical evidence service: ranked word senses from database + domain glossary.
Queries DB for accepted senses, same-work attestations, then falls back to glossary.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Sense:
    lemma: str
    gloss: str
    source_type: str  # same_work | same_author | commentary | dictionary | glossary
    source_ids: list[str] = field(default_factory=list)
    confidence: float = 0.5

    def to_dict(self) -> dict:
        return {"lemma": self.lemma, "gloss": self.gloss, "source": self.source_type,
                "confidence": self.confidence, "sources": self.source_ids}


KS_GUY_GLOSSARY = {
    # 36 tattvas (categories of reality) — Kashmir Shaivism
    "Siva": "Siva (the Supreme Consciousness, ultimate reality in Kashmir Shaivism)",
    "Sakti": "Sakti (the dynamic power/energy of consciousness)",
    "sakti": "sakti (power/energy)",
    "nara": "nara (the limited individual soul)",
    "bIja": "bIja (seed/point of origin, also the phoneme seed in mantra)",
    "bindu": "bindu (point, the condensed source of manifestation)",
    "nAda": "nAda (vibration/sound, the first stirring of manifestation)",
    "unmeza": "unmeSa (opening/expansion of consciousness, manifestation)",
    "nimeza": "nimeSa (closing/contraction of consciousness, withdrawal)",
    "spanda": "spanda (the vibratory dynamism of consciousness, the central doctrine of this text)",
    "prANa": "prANa (vital energy/life-force)",
    "kalA": "kalA (limiting factor/principle of limitation, one of the 5 kanchukas that obscure the bound soul)",
    "kAla": "kAla (time, one of the 5 kanchukas/limiting principles)",
    "niyati": "niyati (causal necessity/fate, one of the 5 kanchukas)",
    "rAga": "rAga (attachment/passion, one of the 5 kanchukas)",
    "vidyA": "vidyA (limited knowledge, one of the 5 kanchukas)",
    "mAyA": "mAyA (the principle of manifestation/limitation, not illusion in Shaiva Siddhanta)",
    "moha": "moha (delusion/confusion)",
    "prakfti": "prakfti (primordial nature)",
    "puruza": "puruSa (individual soul/consciousness principle)",
    "buddhi": "buddhi (intellect/determinative faculty)",
    "ahaGkAra": "ahaGkAra (ego/self-sense)",
    "manas": "manas (mind/the internal organ)",
    "karma": "karma (action/deed)",
    "jYAna": "jYAna (knowledge/gnosis)",
    "icCA": "icCA (will/volition)",
    "kriyA": "kriyA (action/activity)",
    "mAyA1": "mAyA (the principle of limitation/condensation of consciousness)",
    
    # Technical terms from Spandakārikā
    "pada": "pada (state/condition/level of being, not 'foot' in this context)",
    "padadvaya": "pada-dvaya (the two states, referring to waking and dreaming or the dual condition)",
    "tattva": "tattva (reality/principle/category of existence)",
    "pratyaya": "pratyaya (cognition/mental representation/awareness, not 'faith')",
    "zabdAnuveDa": "zabdAnuveDha (penetration/impregnation by speech/sound)",
    "upalabDf": "upalabdhf (perceiver/subject of awareness)",
    "cakra": "cakra (wheel/circle/energy-center, in Spanda context: the wheel of energies/Saktis)",
    "kzoBa": "kSobha (agitation/turmoil/disruption of the sense of separate self)",
    "dharma": "dharma (nature/essential quality, also: virtue/right conduct)",
    "abheda": "abheda (non-difference/non-duality)",
    "bheda": "bheda (difference/duality)",
    "nirvARa": "nirvANa (liberation/extinction of suffering)",
    "mokza": "mokSa (liberation/release)",
    "mukti": "mukti (liberation)",
    "jIvanmukti": "jIvanmukti (liberation while still living)",
    "upAya": "upAya (means/method to realization)",
    "anupAya": "anupAya (no-means, the effortless path)",
    "samAveza": "samAveza (penetration/absorption into Siva)",
    "samAdhi": "samAdhi (contemplative absorption/meditative union)",
    "dIkzA": "dIkSA (initiation/spiritual transmission)",
    "guru": "guru (spiritual teacher/master)",
    "mantra": "mantra (sacred sound formula)",
    "yoga": "yoga (union/spiritual discipline)",
    "yogin": "yogin (practitioner of yoga)",
    "sAdhaka": "sAdhaka (spiritual practitioner)",
    "siddhi": "siddhi (spiritual accomplishment/perfection)",
    "paSu": "paSu (bound soul/fettered being, one of the three categories: pati, paSa, paSu)",
    "pati": "pati (Lord/Siva)",
    "pASa": "pASa (bond/fetter)",
    "bandha": "bandha (bondage)",
    "grantha": "grantha (knot/psychic blockage)",
    "kartftva": "kartftva (agency/the quality of being a doer)",
    "kAryatA": "kAryatA (causality/the state of being an effect)",
    "svatantrya": "svatantrya (freedom/independence/autonomy, Siva's sovereign freedom)",
    "akftrima": "akftrima (natural/uncontrived, not artificial)",
    "bala": "bala (strength/power, often inner spiritual strength)",
    "nirodha": "nirodha (cessation/restriction/obstruction)",
    "svarUpa": "sva-rUpa (one's own nature/essential form)",
    "parama": "parama (supreme/highest/transcendent)",
    "aparA": "aparA (lower/inferior/immanent aspect)",
    "parA": "parA (supreme/transcendent aspect)",
    
    # Common verbs in Spanda
    "vand": "to praise/worship/revere",
    "stu": "to praise/extol",
    "kf": "to do/make/perform",
    "bhU": "to be/become",
    "as": "to be",
    "gam": "to go/attain",
    "zru": "to hear",
    "vad": "to speak/say",
    "dRS": "to see/perceive",
    "jYA": "to know/recognize",
    "i": "to go/attain",
    "spand": "to vibrate/pulsate/throb",
    "muc": "to liberate/release",
    "Ap": "to obtain/attain",
    "prakAS": "to shine/manifest/illumine",
    "praviS": "to enter",
    "Bud": "to awaken/know",
    "cint": "to think/reflect",
    "dhyAI": "to meditate on",
    "smf": "to remember",
    "vft": "to be/exist/turn",
    "ni-vft": "to cease/turn back/return",
    "pra-vft": "to proceed/begin/be active",
    "saM-vft": "to become/turn into",
    "ava-gam": "to understand/realize",
    "prati-pad": "to attain/understand/reach",
    "upa-labh": "to perceive/obtain",
    "ut-pad": "to arise/emerge",
    "pra-lI": "to dissolve/merge",
    "ava-sthA": "to abide/stand/remain",
    "A-ramb": "to begin",
    "sam-A-ramb": "to undertake",
    "nAza": "to destroy/perish",
    
    # Negation
    "na": "not (negation marker)",
    "mA": "not/prohibition (negative particle)",
    "no": "not",
    "noc": "and not, nor",
    
    # Conjunctions and particles
    "ca": "and",
    "api": "also/even/though",
    "eva": "indeed/just/only (emphatic particle)",
    "tu": "but/however/and",
    "ced": "if",
    "hi": "for/indeed/because",
    "kuta": "how?/whence?/why?",
    "sadA": "always/constantly",
    "nityam": "always/constantly/eternally",
    "anutpanna": "unborn/unproduced",
    "samasta": "complete/entire/all",
    "viSvam": "all/everything/the universe",
    "ekam": "one/alone/unique",
    "advaya": "non-dual/without a second",
    "amfta": "immortal/nectar of immortality",
    "bRh": "great/vast",
    "etat": "this (neuter pronoun)",
    "idam": "this (demonstrative)",
    "tat": "that (demonstrative, often referring to the Absolute)",
    "ayam": "this (masculine)",
    "asya": "of this (genitive)",
    "yathA": "as/just as/in accordance",
    "tathA": "so/thus/in that way",
    "saha": "with/together",
}

# Additional glosses transliterated in SLP1
def normalize_lemma(lemma: str) -> str:
    """Convert SLP1 to approximate Devanagari-readable key for lookup."""
    # Map common SLP1 variants
    replacements = {
        "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ",
        "x": "ṣ", "X": "kṣ", "G": "ṅ", "J": "ñ", "N": "ṇ",
        "t": "t", "T": "ṭ", "d": "d", "D": "ḍ", "n": "n",
        "S": "ś", "z": "ṣ", "h": "h", "M": "ṃ", "H": "ḥ",
    }
    return lemma  # Keep as-is for lookup, we handle variants in _resolve


def get_senses(lemma: str, work_id: str | None = None, conn=None) -> list[Sense]:
    """Get ranked senses for a lemma from DB first, then glossary."""
    senses = []

    # 1. Check DB for same-work accepted senses
    if conn and work_id:
        rows = conn.execute("""
            SELECT DISTINCT lex.lemma_slp1
            FROM lexeme lex
            JOIN morph_analysis_type mat ON mat.lexeme_id = lex.lexeme_id
            JOIN token_analysis_hypothesis tah ON tah.analysis_type_id = mat.analysis_type_id
            JOIN token_occurrence tocc ON tocc.occurrence_id = tah.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id = ? AND lex.lemma_slp1 = ?
            LIMIT 3
        """, (work_id, lemma)).fetchall()
        for row in rows:
            senses.append(Sense(lemma=lemma, gloss="[attested in this work]",
                                source_type="same_work", confidence=0.7))

    # 2. Glossary fallback
    # Try exact match
    key = lemma
    if key in KS_GUY_GLOSSARY:
        senses.append(Sense(lemma=lemma, gloss=KS_GUY_GLOSSARY[key],
                            source_type="glossary", confidence=0.6))

    # 3. Try normalized variants
    norm = lemma.lower().replace("1", "").replace("2", "").replace("3", "")
    if norm in KS_GUY_GLOSSARY:
        senses.append(Sense(lemma=lemma, gloss=KS_GUY_GLOSSARY[norm],
                            source_type="glossary", confidence=0.55))
    elif norm not in (lemma, lemma.lower()):
        norm2 = lemma.lower()
        if norm2 in KS_GUY_GLOSSARY:
            senses.append(Sense(lemma=lemma, gloss=KS_GUY_GLOSSARY[norm2],
                                source_type="glossary", confidence=0.55))

    return senses


def build_evidence_text(lemmas: list[str], work_id: str | None = None, conn=None,
                        max_lemmas: int = 15) -> str:
    """Build structured lexical evidence text for LLM prompt."""
    lines = []
    for lemma in lemmas[:max_lemmas]:
        senses = get_senses(lemma, work_id, conn)
        if senses:
            best = senses[0]
            lines.append(f"  {lemma}: {best.gloss} [{best.source_type}]")
        else:
            lines.append(f"  {lemma}: [unrecognized — may be a proper noun or rare term]")
    return "\n".join(lines) if lines else "[No lexical evidence available]"
