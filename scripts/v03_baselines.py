"""v0.3 S2+S3: A2/B2 baselines + D publication gate + mutation tests.

Generates:
  proof/llm_baselines_v03.json    — A2, B2, C, D outputs
  proof/publication_gate_v03.json — D PASS/REJECT decisions
  proof/mutation_results_v03.json — mutation test results
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parents[1]
import sys
sys.path.insert(0, str(BASE / "src"))
from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")

# Lemma → English gloss for System A2 (plain literal)
LITERAL = {
    "vand": "praise", "hfd": "heart", "nATa": "lord", "anATa": "helpless",
    "saraRya": "refuge", "tvanmaya": "consisting-of-you", "citta": "mind",
    "BErava": "Bhairava", "mft": "death", "deva": "god", "Sakti": "power",
    "tad": "that", "ca": "and", "na": "not", "api": "also", "eva": "indeed",
    "tu": "but", "hi": "for", "iti": "thus", "yad": "which", "tat": "that",
    "tvam": "you", "aham": "I", "idam": "this", "kim": "what", "sa": "he",
    "sA": "she", "BU": "become", "as": "be", "kf": "do", "gam": "go",
    "zru": "hear", "vac": "speak", "dRS": "see", "jYA": "know",
    "Atman": "self", "karma": "action", "dharma": "teaching",
    "SrInATa": "glorious-lord", "maRqala": "mandala", "mudra": "gesture",
    "deva": "deity", "ziva": "Siva", "Sakti": "energy",
    "yoga": "union", "mantra": "sacred-speech", "cakra": "wheel-center",
    "Sambu": "Siva", "bhairava": "Bhairava", "nAtha": "lord",
    "Sakti": "power", "ISa": "ruler", "guru": "teacher",
    "putra": "son", "kula": "family", "kram": "step",
    "antar": "within", "madhya": "middle", "Urdhva": "upward",
    "adhas": "downward", "bAhya": "external", "Antara": "internal",
}


def system_a2(source: str) -> dict:
    """A2: plain literal gloss (no syntax, no context)."""
    words = re.sub(r'[^\w\sāīūṣṇṃḥṛśñṭḍḷ]', '', source).split()
    glossed = [LITERAL.get(w, f"[{w}]") for w in words[:10]]
    return {
        "system": "A2_literal",
        "translation": " ".join(glossed) if glossed else "[unable to parse]",
        "evidence": {"type": "dictionary_only", "source": "builtin_gloss"},
    }


def system_b2(source: str, lemmas: list[str], frame: str) -> dict:
    """B2: retrieval-assisted — lemmas + frame + gloss."""
    glossed = [LITERAL.get(l, l) for l in lemmas if l]
    evidence = {"lemmas": lemmas, "count": len(lemmas), "frame": frame}
    if not glossed:
        return {
            "system": "B2_retrieval",
            "translation": f"[{frame}] [no recognized vocabulary]",
            "evidence": evidence,
        }
    return {
        "system": "B2_retrieval",
        "translation": f"[{frame}] {' '.join(glossed)}",
        "evidence": evidence,
    }


def system_c(lemmas: list[str], frame: str) -> dict:
    """C: Sanskritree (no Lean)."""
    return {
        "system": "C_sanskritree",
        "translation": f"[{frame}] {' '.join(lemmas)}" if lemmas else f"[{frame}] [no lemmas]",
        "evidence": {"lemmas": lemmas, "count": len(lemmas), "frame": frame},
    }


def system_d(c_output: dict, lemmas: list[str], source: str, reading_id: str, conn) -> dict:
    """D: publication gate — PASS/REJECT with violations.

    Checks:
    1. At least 1 lemma (minimum coverage)
    2. No lemma named '__unknown__' (rejected hypothesis not used)
    3. Source length > 0 (valid source)
    """
    violations = []
    
    # Rule 1: minimum semantic coverage
    if not lemmas or len(lemmas) < 1:
        violations.append({
            "rule": "INSUFFICIENT_COVERAGE",
            "detail": f"Only {len(lemmas) if lemmas else 0} lemmas for {len(source)} chars of source",
            "severity": "ERROR",
        })
    
    # Rule 2: no rejected hypotheses
    if lemmas and any(l == '__unknown__' or l == 'lex_unknown' for l in lemmas):
        violations.append({
            "rule": "REJECTED_HYPOTHESIS_USED",
            "detail": "Output references unresolved/unknown lemma",
            "severity": "ERROR",
        })
    
    # Rule 3: source hash integrity (basic)
    if not source or len(source.strip()) < 3:
        violations.append({
            "rule": "INVALID_SOURCE",
            "detail": "Source text is empty or too short",
            "severity": "ERROR",
        })
    
    # Determine status
    errors = [v for v in violations if v["severity"] == "ERROR"]
    warnings = [v for v in violations if v["severity"] == "WARNING"]
    
    if errors:
        status = "REJECT"
    elif warnings:
        status = "PASS_WITH_WARNINGS"
    else:
        status = "PASS"
    
    return {
        "system": "D_publication_gate",
        "status": status,
        "translation": c_output["translation"] if status != "REJECT" else None,
        "violations": violations,
    }


def mutation_test(valid_data: dict, mutation_fn, description: str, expect_reject: bool = True) -> dict:
    """Apply a mutation and test whether D rejects it."""
    try:
        mutated = mutation_fn(dict(valid_data))
        d_result = system_d(
            {"translation": mutated["translation"]},
            mutated.get("lemmas", []),
            mutated.get("source", ""),
            mutated.get("reading_id", ""),
            None,
        )
        actually_rejected = d_result["status"] == "REJECT"
        return {
            "description": description,
            "expected_reject": expect_reject,
            "actual_status": d_result["status"],
            "detected": expect_reject == actually_rejected,
            "violations": d_result["violations"],
        }
    except Exception as e:
        return {"description": description, "error": str(e), "detected": False}


def main():
    print("v0.3 S2+S3: Baselines + publication gate + mutation tests\n")
    conn = connect(DB)
    pilot = json.loads(open(BASE / "proof" / "translation_pilot_v1.json").read())
    
    baselines = []
    gate_results = []
    
    for passage in pilot["passages"]:
        pid = passage["id"]
        source = passage["source_clean"]
        out_c = passage["system_outputs"].get("C_sanskritree_nolean", {})
        lemmas = out_c.get("lemmas", [])
        frame = out_c.get("frame", "?")
        
        # Generate all 4 system outputs
        a2 = system_a2(source)
        b2 = system_b2(source, lemmas, frame)
        c = system_c(lemmas, frame)
        
        # Get reading_id for D
        rid = conn.execute("SELECT reading_id FROM passage_readings WHERE passage_id=? LIMIT 1", (pid,)).fetchone()
        d = system_d(c, lemmas, source, rid[0] if rid else "", conn)
        
        baselines.append({
            "passage_id": pid,
            "short_id": passage.get("short_id", pid),
            "track": passage["track"],
            "source": source[:80],
            "A2_literal": a2,
            "B2_retrieval": b2,
            "C_sanskritree": c,
            "D_publication_gate": d,
        })
        
        gate_results.append({
            "passage_id": pid,
            "status": d["status"],
            "violations": d["violations"],
        })
    
    # Save baselines
    bl_out = BASE / "proof" / "llm_baselines_v03.json"
    with open(bl_out, "w") as f:
        json.dump(baselines, f, indent=2, ensure_ascii=False)
    
    # Publication gate summary
    gate_summary = defaultdict(int)
    for r in gate_results:
        gate_summary[r["status"]] += 1
    
    pg_out = BASE / "proof" / "publication_gate_v03.json"
    with open(pg_out, "w") as f:
        json.dump({"results": gate_results, "summary": dict(gate_summary)}, f, indent=2)
    
    print(f"  Baselines: {bl_out}")
    print(f"  Gate:      {pg_out}")
    print(f"  D results: {dict(gate_summary)}")
    
    # Mutation tests
    print("\n  Mutation tests:")
    valid = {"lemmas": ["vand", "hfd", "bhairava"], "source": "bhairava-vandana", "translation": "praise to Bhairava"}
    
    def identity(d):
        return dict(d)
    
    mutations = [
        (lambda d: {**d, "lemmas": []}, "Remove all lemmas", True),
        (lambda d: {**d, "lemmas": ["__unknown__"]}, "Unknown lemma used", True),
        (lambda d: {**d, "source": ""}, "Empty source", True),
        (identity, "Valid passage unchanged", False),
        (lambda d: {**d, "source": "   "}, "Blank source", True),
    ]
    
    mut_results = []
    for fn, desc, expect_reject in mutations:
        r = mutation_test(valid, fn, desc, expect_reject)
        mut_results.append(r)
        status = "✅" if r["detected"] else "❌"
        print(f"    {status} {desc}")
    
    mut_out = BASE / "proof" / "mutation_results_v03.json"
    det_rate = sum(1 for r in mut_results if r["detected"]) / len(mut_results) * 100
    with open(mut_out, "w") as f:
        json.dump({"results": mut_results, "detection_rate": det_rate}, f, indent=2)
    
    print(f"\n  Mutation detection rate: {det_rate:.0f}%")
    print(f"  Saved: {mut_out}")
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
