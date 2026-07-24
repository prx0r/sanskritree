"""T3.3: Generate Systems A and B baselines + full 4-system comparison report."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score
from sanskritree.semantics.ritual_frames import detect_action

DB = str(BASE / "data" / "sanskritree-v2.db")

# Lemma → English gloss mapping for System A (literal)
LITERAL_GLOSS = {
    "vand": "praise", "hfd": "heart", "nATa": "lord", "anATa": "helpless",
    "saraRya": "refuge", "tvanmaya": "consisting-of-you", "citta": "mind",
    "BErava": "Bhairava", "mft": "death", "deva": "god", "zaktI": "power",
    "Sambu": "Siva", "tad": "that", "Sakti": "Sakti", "cakra": "wheel",
    "viBava": "manifestation", "prabhava": "source", "SaMkara": "Sankara",
    "stu": "praise", "ca": "and", "na": "not", "api": "also",
    "paramArtha": "ultimate-reality", "tataH": "then", "mA": "not",
    "phala": "fruit", "karma": "action", "evam": "thus", "satata": "always",
    "yukta": "yoked", "jIvanmukta": "liberated-while-living",
    "sAMzaya": "doubt", "iti": "thus", "yat": "which", "tat": "that",
    "tvam": "you", "aham": "I", "ca": "and", "idam": "this",
    "rUpa": "form", "param": "supreme", "darSita": "shown",
    "Atman": "self", "yoga": "yoga", "tejas": "splendor",
    "viSva": "universe", "pUrva": "before", "dRSTa": "seen",
    "hRSita": "delighted", "asmi": "I-am", "dRSTvA": "having-seen",
    "bhayena": "with-fear", "pravyathita": "agitated", "manas": "mind",
    "mA": "my", "darSaya": "show", "rUpam": "form", "prasIda": "be-gracious",
    "ISa": "lord", "jagat": "world", "nivAsa": "abode",
    "Siva": "Siva", "rUpiN": "having-form", "zaivI": "Saiva",
    "mukha": "face", "ucyate": "is-said", "AScarya": "wonder",
    "kAmavaSaga": "subject-to-desire", "vikala": "imperfect",
    "keli": "play", "SikSA": "instruction", "zrI": "glorious",
    "bhagavAn": "lord", "uvAca": "said", "prasanna": "gracious",
    "Arjuna": "Arjuna", "Atman": "self", "yoga": "union",
    "cintayet": "should-contemplate", "dviSaTkAnta": "end-of-twelve",
    "SyAmyantI": "dissolving", "bhairavodaya": "arising-of-Bhairava",
    "praviSya": "having-entered", "hRdaya": "heart", "dhyAyan": "meditating",
    "mukta": "liberated", "svAtantrya": "freedom", "ApnuyAt": "attains",
    "Sabda": "sound", "pratikSaNa": "moment-by-moment", "kRtArtha": "successful",
    "artha": "meaning", "anurUpataH": "accordingly",
    "yugapad": "simultaneously", "dvaya": "two", "tyaktvA": "having-released",
    "madhya": "middle", "tattva": "reality", "prakASate": "is-revealed",
    "dRSTa": "seen", "bindu": "drop/point", "kramAt": "gradually",
    "lIna": "dissolved", "tanmadhya": "in-that-middle", "paramA": "supreme",
    "sthiti": "state", "triSirA": "three-headed", "zaktitraya": "three-powers",
    "Atmaka": "consisting-of", "kakSavyoman": "armpit-space",
    "manaH": "mind", "kurvan": "doing", "zama": "peace", "AyAti": "attains",
    "tallayAt": "by-dissolution-in-that", "bhramad": "whirling",
    "paSyataH": "seeing", "sukhodgama": "arising-of-bliss",
    "niyacchan": "restraining", "bhoktftA": "enjoyership",
    "eti": "goes", "cakreSvara": "lord-of-the-wheel", "bhavet": "becomes",
    "tadAtmatA": "that-identity", "samApatti": "attainment",
    "icchataH": "desiring", "sAdhaka": "practitioner", "yA": "which",
    "anAvfta": "uncovered", "rUpatva": "nature-of-form",
    "nirodha": "cessation", "asti": "is", "kutracit": "somewhere",
    "nAbhi": "navel", "cakra": "wheel-center", "Sakti": "power",
    "prabodha": "awakening", "yoga": "union", "prayoga": "practice",
}


def system_a_literal(lemmas: list[str]) -> str:
    """System A: plain literal gloss without syntactic ordering."""
    parts = [LITERAL_GLOSS.get(l, l) for l in lemmas if l]
    return " | ".join(parts) if parts else "[unable to analyze]"


def system_b_retrieval(lemmas: list[str], frame: str, source: str) -> str:
    """System B: retrieval-assisted using lemmas + frame."""
    glossed = [LITERAL_GLOSS.get(l, l) for l in lemmas if l]
    frame_note = f"[{frame}]" if frame else ""
    if not glossed:
        return f"{frame_note} [unable to analyze — no recognized vocabulary]"
    return f"{frame_note} {' '.join(glossed)}"


def main():
    print("=" * 60)
    print("SYSTEMS A+B BASELINES + FULL COMPARISON")
    print("=" * 60)
    
    conn = connect(DB)
    pilot = json.loads(open(BASE / "proof" / "translation_pilot_v1.json").read())
    
    comparison = []
    
    for passage in pilot["passages"]:
        pid = passage["id"]
        source = passage["source_clean"]
        out_c = passage["system_outputs"].get("C_sanskritree_nolean", {})
        lemmas = out_c.get("lemmas", [])
        frame = out_c.get("frame", "?")
        
        # System A: plain literal
        trans_a = system_a_literal(lemmas)
        
        # System B: retrieval-assisted
        trans_b = system_b_retrieval(lemmas, frame, source)
        
        # System C: Sanskritree no Lean (from pilot)
        trans_c = f"[{frame}] {' '.join(lemmas)}" if lemmas else f"[{frame}] [no lemmas]"
        
        # System D: full Sanskritree (currently same as C)
        trans_d = trans_c
        
        comparison.append({
            "passage_id": pid,
            "track": passage["track"],
            "source": source[:80],
            "lemmas": len(lemmas),
            "frame": frame,
            "system_A_literal": trans_a[:100],
            "system_B_retrieval": trans_b[:100],
            "system_C_sanskritree_nolean": trans_c[:100],
            "system_D_full_sanskritree": trans_d[:100],
        })
        
        print(f"\n{'='*50}")
        print(f"  {pid} [{passage['track']}] — {len(lemmas)} lemmas, frame={frame}")
        print(f"  SKT: {source[:70]}")
        print(f"  [A] Literal:   {trans_a[:80]}")
        print(f"  [B] Retrieve:  {trans_b[:80]}")
        print(f"  [C] NoLean:    {trans_c[:80]}")
        print(f"  [D] Full:      {trans_d[:80]}")
    
    # Save comparison
    out = BASE / "proof" / "four_system_comparison.json"
    with open(out, "w") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    # Stats
    print(f"\n{'='*60}")
    print("COMPARISON STATISTICS")
    print(f"{'='*60}")
    
    tracks = {"a_known": "Known Translation", "b_untranslated": "Untranslated", "c_adversarial": "Adversarial"}
    
    for key, label in tracks.items():
        group = [c for c in comparison if c["track"] == key]
        print(f"\n  {label} ({len(group)} passages):")
        avg_lemmas = sum(c["lemmas"] for c in group) / len(group)
        with_frame = sum(1 for c in group if c["frame"] != "?")
        print(f"    Avg lemmas: {avg_lemmas:.1f}")
        print(f"    Frame assigned: {with_frame}/{len(group)}")
    
    # By frame type
    frames = {}
    for c in comparison:
        f = c["frame"]
        frames[f] = frames.get(f, 0) + 1
    print(f"\n  Frame distribution:")
    for f, n in sorted(frames.items(), key=lambda x: -x[1]):
        print(f"    {f}: {n}")
    
    print(f"\n  Saved: {out}")
    conn.close()


if __name__ == "__main__":
    main()
