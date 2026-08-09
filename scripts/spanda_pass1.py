"""Spandakārikā blind Pass 1: generate factor graph outputs for all 53 verses.
Runs the frozen v0.4 pipeline WITHOUT accessing any reference translation.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score
from sanskritree.semantics.ritual_frames import detect_action
from sanskritree.translation.realization import semantic_plan_from_assignment, render_english, validate_plan

DB = str(BASE / "data" / "sanskritree-v2.db")
OUT = BASE / "proof" / "checkpoint1" / "runs" / "pass_1"

LEMMA_GLOSS = {
    "vand": "to praise", "hfd": "heart", "nATa": "lord",
    "anATa": "helpless", "saraRya": "refuge", "tvanmaya": "consisting of you",
    "citta": "mind", "BErava": "Bhairava", "tad": "that",
    "Sakti": "Sakti/power", "cakra": "wheel", "viBava": "manifestation",
    "prabhava": "source", "SaMkara": "Sankara/Siva", "stu": "to praise",
    "ca": "and", "na": "not", "api": "also/even",
    "paramArtha": "ultimate reality", "mA": "not/my",
    "phala": "fruit/result", "karma": "action", "eva": "indeed",
    "aham": "I", "Atman": "self", "yoga": "union",
    "deva": "god/lord", "Siva": "Siva", "bhairava": "Bhairava",
    "nAtha": "lord", "SrInATa": "glorious lord",
    "guru": "teacher", "putra": "son",
    "kula": "family", "kram": "step/sequence",
    "BU": "to become", "as": "to be", "kf": "to do",
    "gam": "to go", "zru": "to hear", "vac": "to speak",
    "dRS": "to see", "jYA": "to know", "i": "to go",
    "SyAm": "to dissolve", "cint": "to think", "dhyAI": "to meditate",
    "praviS": "to enter", "muc": "to liberate", "Ap": "to obtain",
    "spand": "to vibrate/spand", "Sakta": "capable",
    "samasta": "entire", "sva": "self/own",
    "para": "other/supreme", "sat": "being/true",
    "abheda": "non-difference", "bheda": "difference",
    "nitya": "eternal", "sarvatra": "everywhere",
    "sphuT": "to manifest", "udaya": "arising",
    "pralaya": "dissolution", "sthiti": "subsistence",
    "pravftti": "activity", "saMhf": "withdrawal",
    "svatantra": "independent", "akftrima": "natural",
    "paramam": "supreme", "pada": "state/step",
    "kSobha": "agitation", "praI": "to dissolve",
    "abhiyoga": "effort/application", "saMsparSa": "contact",
    "niScaya": "certainty", "smaryamANatva": "being remembered",
    "tattva": "reality", "pratipad": "to attain",
    "kAryatA": "causality", "kSayin": "perishable",
    "kartftva": "agency", "akSaya": "imperishable",
    "lupta": "destroyed", "vilupta": "lost",
    "abudha": "ignorant", "upalambhana": "perception",
    "suprabuddha": "fully awakened", "Adyanta": "beginning and end",
    "vibhu": "omnipresent", "cinmaya": "consisting of consciousness",
    "labdha": "obtained", "AtmalAbha": "self-realization",
    "aparipanthin": "unobstructed", "pAtayanti": "cause to fall",
    "duruttara": "hard to cross", "ghora": "terrible",
    "saMsAra": "cycle of existence", "vartman": "path",
    "jAgrat": "waking", "nija": "own",
    "bhAva": "state/nature", "acireRa": "quickly",
    "adhigam": "to attain", "dhAv": "to run",
    "pratiSThita": "established", "avaSyam": "necessarily",
    "saMkalp": "to resolve", "sauSuMna": "sushumna",
    "adhvan": "path", "astaG": "to set/disappear",
    "brahmANDa": "cosmos", "gocara": "sphere/scope",
    "sauSupta": "deep sleep", "mUDha": "deluded",
    "prabuddha": "awakened", "anAvfta": "uncovered",
    "adhikAra": "qualification/authority", "karaRa": "organ",
    "dehin": "embodied one", "ArAdhaka": "worshipper",
    "Sivadharmin": "having Siva's nature", "saMvedana": "awareness",
    "rUpa": "form", "tAdAtmya": "identity",
    "pratipatti": "realization", "bhoktf": "enjoyer",
    "bhogya": "object of enjoyment", "saMsthita": "abiding",
    "yukta": "united/attentive", "jIvanmukta": "liberated while living",
    "saMpatti": "attainment", "icchat": "desiring",
    "sAdhaka": "practitioner", "nirvARa": "liberation",
    "dIkSA": "initiation", "SadbhAva": "true nature",
    "dAyin": "bestowing", "soma": "soma/moon",
    "sUrya": "sun", "udaya": "rising",
    "sampad": "to accomplish", "sphuTa": "manifest",
    "madhya": "middle", "avasthita": "situated",
    "prakAS": "to shine", "laukika": "worldly",
    "svapna": "dream", "bala": "strength",
    "udyoga": "exertion", "bhavita": "fostered",
    "Akram": "to overcome", "AcChAd": "to cover",
    "bubhukSA": "desire to eat/hunger", "atibubhukSita": "very hungry",
    "adhiSThAna": "foundation/standing upon",
    "unmeSa": "opening/manifestation", "vijYA": "to be known",
    "upalakSay": "to observe", "kSobhakatva": "causing agitation",
    "bahunA": "much", "ukta": "said",
    "avabhotsyate": "will be understood", "Aropayet": "should place",
    "pID": "to oppress", "gata": "gone",
    "paSu": "bound soul", "ahetuka": "causeless",
    "ahetu": "without cause", "anuvandha": "connection",
    "pratyaya": "cognition", "udbhava": "arising",
    "bandhayitf": "binding (fem.)", "svamArga": "own path",
    "siddhi": "perfection", "upapAdikA": "conducive",
    "puryaSThaka": "subtle body (city of eight)",
    "saMruddha": "enclosed", "uttha": "arising from",
    "saMsftp": "cycle of rebirth", "pracakS": "to declare",
    "niyam": "to control/restrain", "bhoktf": "enjoyer",
    "cakreSvara": "lord of the wheel", "vicitra": "varied/colorful",
    "artha": "meaning/object", "padA": "having words",
    "citra": "wonderful", "gurubhAratI": "speech of the teacher",
    "Sivas": "for Siva", "sarvaloka": "all the world",
}


def get_verse_by_index(conn, seq_idx: int):
    row = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = 'spandakarika' AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
        LIMIT 1 OFFSET ?
    """, (seq_idx,)).fetchone()
    if not row:
        return None
    return {"passage_id": row[0], "reading_id": row[1], "sanskrit_raw": row[2]}


def build_evidence_bundle(lemmas, frame, english_hypothesis):
    lines = []
    for lemma in lemmas[:10]:
        gloss = LEMMA_GLOSS.get(lemma, f"[unrecognized: {lemma}]")
        lines.append(f"  {lemma}: {gloss}")
    evidence = "\n".join(lines) if lines else "[No lexical evidence available]"
    bundle = {
        "lemmas": lemmas,
        "frame": frame,
        "evidence": evidence,
        "sanskritree_rendering": english_hypothesis,
    }
    return bundle


def process_verse(conn, seq_idx: int):
    verse = get_verse_by_index(conn, seq_idx)
    if not verse:
        return None

    pid = verse["passage_id"]
    rid = verse["reading_id"]
    source = verse["sanskrit_raw"]

    clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', source).strip()

    actions = detect_action(clean)
    g = FactorGraph(pid)
    g.neighborhood(conn, rid)
    if actions:
        g.set_detected_actions(actions)
    g.add_variable("compound", [
        VariableChoice("k", {"relation": "karmadharaya"}, 0.3),
        VariableChoice("t", {"relation": "tatpurusa"}, -0.3),
    ])
    g.add_variable("frame", [
        VariableChoice("d", {"frame_type": "DevotionalAct"}, 0.2),
        VariableChoice("i", {"frame_type": "Instruction"}, 0.2),
        VariableChoice("id", {"frame_type": "IdentityClaim"}, 0.0),
    ])
    register_graph(g)

    t0 = time.time()
    best, beliefs, energy = propagate_and_score(g)
    elapsed = time.time() - t0

    lemmas = []
    token_count = 0
    for vn, c in best.choices.items():
        if vn.startswith("token_"):
            token_count += 1
            lem = c.payload.get("lemma", "")
            if lem and lem != "__unknown__":
                lemmas.append(lem)

    frame = best.choices.get("frame", VariableChoice("n", {}, 0)).payload.get("frame_type", "?")

    plan = semantic_plan_from_assignment(best.choices, source)
    plan_errors = validate_plan(plan)
    english = render_english(plan)

    n_hypotheses = sum(len(c) for c in g.variables.values())

    record = {
        "sequence_index": seq_idx,
        "passage_id": pid,
        "reading_id": rid,
        "source_raw": source,
        "source_clean": clean,
        "pipeline": {
            "factor_graph": {
                "n_variables": len(g.variables),
                "n_hypotheses": n_hypotheses,
                "selected_tokens": token_count,
                "lemmas": lemmas,
                "frame": frame,
                "best_energy": round(energy, 4),
                "propagation_time_s": round(elapsed, 3),
            },
            "semantic_plan": plan,
            "plan_errors": plan_errors,
            "rendered_english": english,
            "actions_detected": actions,
        },
        "evidence_bundle": build_evidence_bundle(lemmas, frame, english),
        "n_token_vars": token_count,
        "n_lemma_tokens": len(lemmas),
        "run_version": "v0.4",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reference_blind": True,
    }

    return record


def hash_record(record: dict) -> str:
    canonical = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    conn = connect(DB)

    verses = conn.execute("""
        SELECT sequence_index FROM passages
        WHERE work_id = 'spandakarika' AND passage_type = 'verse'
        ORDER BY sequence_index
    """).fetchall()

    verse_indices = [r[0] for r in verses]
    print(f"Spandakārikā blind Pass 1 — {len(verse_indices)} verses\n")

    all_records = []
    verse_hashes = []

    for idx in verse_indices:
        record = process_verse(conn, idx)
        if record is None:
            print(f"  [{idx:2d}] SKIP — verse not found")
            continue

        record_hash = hash_record(record)
        record["record_hash"] = record_hash
        all_records.append(record)
        verse_hashes.append({"sequence_index": idx, "record_hash": record_hash})

        lemmas = record["pipeline"]["factor_graph"]["lemmas"]
        n_hyp = record["pipeline"]["factor_graph"]["n_hypotheses"]
        english = record["pipeline"]["rendered_english"]
        plan_errors = record["pipeline"]["plan_errors"]
        print(f"  [{idx:2d}] {len(lemmas)} lemmas, {n_hyp} hyps, {len(plan_errors)} plan errors")
        if plan_errors:
            for e in plan_errors[:3]:
                print(f"         plan: {e}")
        if (idx + 1) % 10 == 0:
            print()

    print(f"\n{'='*50}")
    print(f"Processed {len(all_records)}/{len(verse_indices)} verses")

    run_manifest = {
        "run_id": "spanda_pass_1",
        "pipeline_version": "v0.4",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit": "c36c980",
        "n_verses": len(all_records),
        "n_unique_lemmas": len(set(
            l for r in all_records
            for l in r["pipeline"]["factor_graph"]["lemmas"]
        )),
        "verse_hashes": verse_hashes,
        "semantic_root_hash": hashlib.sha256(
            json.dumps(verse_hashes, sort_keys=True).encode()
        ).hexdigest(),
        "byte_archive_hash": hashlib.sha256(
            json.dumps(all_records, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest(),
        "hash_algorithm": "sha256",
    }

    # Save individual records as JSONL
    jsonl_path = OUT / "blind_pass_1.jsonl"
    with open(jsonl_path, "w") as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"\nRecords saved: {jsonl_path}")

    # Save manifest
    manifest_path = OUT / "blind_pass_1_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(run_manifest, f, indent=2)
    print(f"Manifest saved: {manifest_path}")

    # Summary
    total_lemmas = sum(len(r["pipeline"]["factor_graph"]["lemmas"]) for r in all_records)
    verses_without_lemmas = sum(1 for r in all_records if len(r["pipeline"]["factor_graph"]["lemmas"]) == 0)
    verses_low_coverage = sum(1 for r in all_records if len(r["pipeline"]["factor_graph"]["lemmas"]) <= 1)
    print(f"\nSummary:")
    print(f"  Total verses: {len(all_records)}")
    print(f"  Total unique lemmas: {run_manifest['n_unique_lemmas']}")
    print(f"  Avg lemmas/verse: {total_lemmas / max(len(all_records), 1):.1f}")
    print(f"  Verses with 0 lemmas: {verses_without_lemmas}")
    print(f"  Verses with ≤1 lemma: {verses_low_coverage}")
    print(f"  Semantic root hash: {run_manifest['semantic_root_hash']}")
    print(f"  Byte archive hash: {run_manifest['byte_archive_hash']}")

    conn.close()


if __name__ == "__main__":
    main()
