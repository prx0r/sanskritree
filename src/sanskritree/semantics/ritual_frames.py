"""M8: Ritual-frame ontology for Vijñānabhairava procedural instructions.

VB contains ~112 practice descriptions. Each is a procedural instruction
with agent, action, object/focus, bodily locus, and result.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ── Ritual frame types for Vijñānabhairava ──

INSTRUCTION_TYPES = {
    "FIX_AWARENESS": "stabilize awareness on a single point or object",
    "ATTEND_TO": "direct attention to a specific phenomenon",
    "RETAIN_BREATH": "hold or restrain the breath",
    "SUSPEND_BREATH": "stop breath entirely at a threshold",
    "ENTER_INTERVAL": "enter the space between two states (breath, thought, perception)",
    "VISUALIZE": "imagine a form, light, energy or deity",
    "DISSOLVE": "merge or dissolve one state into another",
    "EXPAND": "expand awareness from localized to universal",
    "CONTEMPLATE_VOID": "rest in emptiness or absence of mental constructs",
    "LOCATE_ENERGY": "fix awareness on a bodily energy center",
    "WITHDRAW_SENSES": "withdraw attention from sensory objects",
    "RECOGNIZE_IDENTITY": "recognize identity with Śiva/Bhairava/absolute",
    "CONTEMPLATE_CONTRADICTION": "hold two incompatible perceptions simultaneously",
    "FOLLOW_RHYTHM": "attend to a natural rhythm (breath, pulse, sensation)",
    "OBSERVE_END": "attend to the ending of a state or phenomenon",
    "REMAIN_IN_STATE": "abide without effort in a spontaneously arising state",
}

LOCI = {
    "heart": "hṛd, hṛdaya",
    "forehead": "lalāṭa, bhrūmadhya",
    "crown": "brahmarandhra, dvādaśānta",
    "palate": "tālu",
    "fontanel": "kapāla",
    "between_eyebrows": "bhrūmadhya",
    "top_of_head": "mūrdhan",
    "throat": "kaṇṭha",
    "navel": "nābhi",
    "perineum": "mūla, ādhāra",
    "entire_body": "sarvāṅga",
    "external_space": "bahirvyoman",
    "internal_space": "antarvyoman",
    "middle": "madhya",
}


@dataclass
class RitualStep:
    action: str
    focus: Optional[str] = None
    locus: Optional[str] = None
    manner: Optional[str] = None
    breath_state: Optional[str] = None
    duration: Optional[str] = None
    condition: Optional[str] = None
    sequence_index: int = 0

@dataclass
class RitualProcedure:
    passage_id: str
    steps: list[RitualStep] = field(default_factory=list)
    result: Optional[str] = None
    prohibition: Optional[str] = None


# ── Known VB procedures (first pass) ──

KNOWN_PROCEDURES = {
    # Verse 28: cintayet tāṃ dviṣaṭkānte śyāmyantīm bhairavodayaḥ
    "vb.28": RitualProcedure(
        passage_id="vb.28",
        steps=[RitualStep(
            action="VISUALIZE",
            focus="the goddess dissolving at the end of the twelve",
            locus="end of twelve (dviṣaṭkānte)",
            manner="contemplating dissolution",
        )],
        result="bhairavodayaḥ — the arising of Bhairava",
    ),
    # Verse 36: dṛṣṭe bindau kramāl līne tanmadhye paramā sthitiḥ
    "vb.36": RitualProcedure(
        passage_id="vb.36",
        steps=[RitualStep(
            action="ATTEND_TO",
            focus="the bindu (drop/point)",
            manner="observing its gradual dissolution",
        )],
        result="paramā sthitiḥ — supreme state in the middle of that",
    ),
    # Verse 55: praviśya hṛdaye dhyāyan muktaḥ svātantryam āpnuyāt
    "vb.55": RitualProcedure(
        passage_id="vb.55",
        steps=[RitualStep(
            action="ENTER_INTERVAL",
            focus="within the heart",
            locus="heart (hṛdaya)",
            manner="meditating after entering",
        )],
        result="muktaḥ svātantryam — liberated, attains freedom",
    ),
    # Verse 61: yugapac ca dvayaṃ tyaktvā madhye tattvam prakāśate
    "vb.61": RitualProcedure(
        passage_id="vb.61",
        steps=[RitualStep(
            action="CONTEMPLATE_CONTRADICTION",
            focus="both (dvaya) simultaneously (yugapat)",
            manner="releasing both, the middle reveals reality",
        )],
        result="tattvam prakāśate — reality is revealed",
    ),
    # Verse 79: kakṣavyomni manaḥ kurvan śamam āyāti tallayāt
    "vb.79": RitualProcedure(
        passage_id="vb.79",
        steps=[RitualStep(
            action="LOCATE_ENERGY",
            focus="mind at the armpit-space (kakṣavyoman)",
            manner="placing the mind there",
        )],
        result="śamam āyāti — attains peace through dissolution in that",
    ),
    # Verse 102: bhramad vā dhyāyataḥ sarvam paśyataś ca sukhodgamaḥ
    "vb.102": RitualProcedure(
        passage_id="vb.102",
        steps=[RitualStep(
            action="ATTEND_TO",
            focus="whirling or perceiving all",
            manner="meditating on the whirling, or perceiving everything",
        )],
        result="sukhodgamaḥ — the arising of bliss",
    ),
    # Verse 132: śabdān pratikṣaṇaṃ dhyāyan kṛtārtho 'rthānurūpataḥ
    "vb.132": RitualProcedure(
        passage_id="vb.132",
        steps=[RitualStep(
            action="ATTEND_TO",
            focus="sounds (śabdān) moment by moment",
            manner="meditating on each sound as it arises",
        )],
        result="kṛtārthaḥ — fulfilled, attaining the meaning",
    ),
}


def get_ritual_frame(verse_num: int) -> RitualProcedure | None:
    """Get the ritual frame for a VB verse by number."""
    pid = f"vb.{verse_num}"
    return KNOWN_PROCEDURES.get(pid)


def detect_action(sanskrit_text: str) -> list[str]:
    """Heuristically detect ritual actions from Sanskrit keywords."""
    keywords = {
    "FIX_AWARENESS": ["sthirīkṛtya", "sthirī", "niścala", "nirodha", "sthirīkftya", "sthirIkftya"],
    "ATTEND_TO": ["dhyā", "dhyāna", "cintay", "bhāvay", "manasā", "manas", "manaḥ",
                   "dhyāyan", "dhyāyato", "dhyātvā", "cintayet", "bhāvayet",
                   "dhyāta", "dhyātavyam", "cintā", "cintan"],
    "RETAIN_BREATH": ["prāṇa", "vāyu", "kumbhaka", "rodha", "prāṇa", "vāyu", "ucchvāsa"],
    "SUSPEND_BREATH": ["niruddha", "nirodha", "ucchvāsa", "niśvāsa", "nirudhya"],
    "ENTER_INTERVAL": ["madhye", "antar", "madhyam", "madhya", "antare", "madhya"],
    "VISUALIZE": ["bhāvay", "rūpa", "rūpam", "vibhāvay", "bhāvayan", "bhāvanā",
                   "vibhāvayet", "rūpī", "rūpiṇī"],
    "DISSOLVE": ["laya", "līna", "vilaya", "pra√lī", "līyate", "laya", "līna"],
    "LOCATE_ENERGY": ["sthāna", "cakra", "padma", "pīṭha", "ādhāra", "kakṣa",
                       "vyoman", "vyomni", "kakṣavyomni", "mūrdhan", "bhrūmadhya",
                       "nābhi", "hṛdaya", "hṛdi", "kaṇṭha", "tālu"],
    "WITHDRAW_SENSES": ["ni√vṛt", "pratyāhāra", "niṣkala", "nivartate", "pratyāhāra"],
    "RECOGNIZE_IDENTITY": ["śiva", "bhairava", "cidānanda", "aham", "aham", "asmī",
                            "śivaḥ", "bhairavaḥ", "śivarūpī"],
    "CONTEMPLATE_VOID": ["śūnya", "vyoman", "nirādhāra", "amala", "śūnye", "vyomni",
                          "nirādhāram"],
    }
    found = []
    for action, kws in keywords.items():
        if any(kw in sanskrit_text for kw in kws):
            found.append(action)
    return found
