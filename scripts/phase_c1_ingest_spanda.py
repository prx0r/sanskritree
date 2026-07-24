"""Phase C1: Ingest Spandakārikā from GRETIL with verse/commentary separation.

Structure:
  verse_text // vspk_X.Y //  (verse marker)
  * [commentary || vspkc_X.Y:Z * ... ]  (Kṣemarāja commentary)

Output: passages (verse), passages (commentary), passage_relations,
        Vidyut morphology, factor graph inference.
"""
from __future__ import annotations

import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect, migrate
from sanskritree.corpus.ingestion import ingest_manifest
from sanskritree.philology.adapters import analyze
from sanskritree.philology.analysis_lattice import persist_lattice
from sanskritree.inference.factor_graph import FactorGraph, VariableChoice
from sanskritree.inference.factors import register_graph
from sanskritree.inference.propagation import propagate_and_score

import yaml

SOURCE_FILE = "/tmp/sp.txt"
WORK_ID = "spandakarika"
MANIFEST_PATH = BASE / "data" / "manifests" / "spandakarika_gretil.yaml"
DB_PATH = BASE / "data" / "sanskritree-v2.db"


def parse_spanda(text: str) -> dict:
    """Parse GRETIL Spandakārikā into verses and commentary blocks."""
    # Strip header
    lines = text.split("\n")
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "# Text":
            start = i + 1
            break
    body = "\n".join(lines[start:])

    verses = []
    commentaries = []
    current_commentary = []
    current_commentary_refs = []
    in_commentary = False

    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # Verse line: text // vspk_X.Y //
        vm = re.search(r'//\s*vspk_(\d+)\.(\d+)\s*//', stripped)
        if vm and not stripped.startswith("*"):
            ch, vs = int(vm.group(1)), int(vm.group(2))
            verse_text = re.sub(r'//\s*vspk_\d+\.\d+\s*//', '', stripped).strip()
            verses.append({
                "chapter": ch,
                "verse": vs,
                "text": verse_text,
            })
            continue

        # Commentary line: starts with *
        if stripped.startswith("*"):
            in_commentary = True
            # Extract references: vspkc_X.Y:Z
            refs = re.findall(r'vspkc_(\d+)\.(\d+)(?::(\d+))?', stripped)
            for ref in refs:
                ch, vs = int(ref[0]), int(ref[1])
                seg = int(ref[2]) if ref[2] else 0
                current_commentary_refs.append((ch, vs, seg))
            # Extract commentary text (between * delimiters or after *)
            ct = re.sub(r'\*\s*\[?<?\s*spandakārikānirṇaya>?\s*\*?\s*', '', stripped)
            ct = re.sub(r'\s*\|\|\s*vspkc_[\d\.:]+', '', ct)
            ct = ct.strip().strip("*").strip()
            if ct:
                current_commentary.append(ct)
        else:
            if in_commentary and current_commentary:
                commentaries.append({
                    "text": " ".join(current_commentary),
                    "refs": list(set(current_commentary_refs)),
                })
                current_commentary = []
                current_commentary_refs = []
            in_commentary = False

    # Flush last commentary
    if in_commentary and current_commentary:
        commentaries.append({
            "text": " ".join(current_commentary),
            "refs": list(set(current_commentary_refs)),
        })

    return {"verses": verses, "commentaries": commentaries}


def build_manifest(parsed: dict) -> dict:
    """Build V2 manifest from parsed verses."""
    passages = []
    for v in parsed["verses"]:
        pid = f"spk.{v['chapter']}.{v['verse']}"
        passages.append({
            "id": pid,
            "chapter": str(v["chapter"]),
            "verse": str(v["verse"]),
            "type": "verse",
            "transliteration": "IAST",
            "critical_status": "gretil_import",
            "sanskrit": v["text"],
        })

    # Also add commentary blocks as separate passages
    for i, c in enumerate(parsed["commentaries"]):
        cid = f"spk.comm.{i}"
        if c["refs"]:
            ch, vs, *_ = c["refs"][0]
            cid = f"spk.comm.{ch}.{vs}.{i}"
        passages.append({
            "id": cid,
            "chapter": str(c["refs"][0][0]) if c["refs"] else "",
            "type": "commentary",
            "transliteration": "IAST",
            "critical_status": "gretil_import_commentary",
            "sanskrit": c["text"],
            "commentary_on": [f"spk.{r[0]}.{r[1]}" for r in c["refs"]],
        })

    return {
        "work": {
            "id": WORK_ID,
            "title": "Spandakārikā with Kṣemarāja commentary",
            "title_iast": "Spandakārikā",
            "author": "Vasugupta (attr.)",
            "tradition": "trika",
            "genre": "tantra",
            "metadata": {"source": "GRETIL", "commentator": "Kṣemarāja"},
        },
        "edition": {
            "id": "spandakarika.gretil",
            "editor": "Oliver Hellwig",
            "publication": "GRETIL",
            "licence": "CC-BY-NC-SA 4.0",
            "critical_method": "GRETIL IAST e-text; Kṣemarāja commentary preserved separately",
        },
        "passages": passages,
    }


def link_commentaries(conn, manifest: dict, parsed: dict):
    """Create passage_relation entries for commentary→verse links."""
    now = datetime.now(timezone.utc).isoformat()
    count = 0

    # Get all commentary passages from manifest
    comm_passages = [p for p in manifest["passages"] if p.get("type") == "commentary"]
    for cp in comm_passages:
        source_id = cp["id"]
        targets = cp.get("commentary_on", [])
        for target_id in targets:
            # Verify target exists
            exists = conn.execute(
                "SELECT 1 FROM passages WHERE passage_id = ?", (target_id,)
            ).fetchone()
            if not exists:
                continue
            rid = str(uuid.uuid4())
            conn.execute("""INSERT OR IGNORE INTO passage_relation
                (relation_id, source_passage_id, target_passage_id, relation_type,
                 confidence, provenance, created_at)
                VALUES (?, ?, ?, 'COMMENTARY_ON', 0.9, 'gretil_structure', ?)""",
                (rid, source_id, target_id, now))
            count += 1

    conn.commit()
    return count


def run_factor_graph(conn, work_id: str):
    """Run factor graph inference on all verses."""
    verses = conn.execute("""
        SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """, (work_id,)).fetchall()

    results = []
    for pid, vs, rid, raw in verses:
        g = FactorGraph(pid)
        g.neighborhood(conn, rid)
        add_standard_vars(g)
        register_graph(g)

        best, beliefs, energy = propagate_and_score(g, beam_width=30)
        n_tokens = sum(1 for v in g.variables if v.startswith("token_"))
        n_hyp = sum(len(c) for c in g.variables.values())
        results.append((vs, n_tokens, n_hyp, energy))

    return results


def add_standard_vars(g: FactorGraph):
    """Add standard frame options."""
    g.add_variable("frame", [
        VariableChoice("frame_devotional", {"frame_type": "DevotionalAct"}, 0.2),
        VariableChoice("frame_identity", {"frame_type": "IdentityClaim"}, -0.2),
        VariableChoice("frame_predication", {"frame_type": "Predication"}, 0.0),
    ])


def main():
    print("=" * 60)
    print("PHASE C1 — Spandakārikā ingestion")
    print("=" * 60)

    # Parse
    print("\n[1] Parsing GRETIL file...")
    raw = Path(SOURCE_FILE).read_text(encoding="utf-8")
    parsed = parse_spanda(raw)
    print(f"  {len(parsed['verses'])} verses")
    print(f"  {len(parsed['commentaries'])} commentary blocks")

    # Build manifest
    print("\n[2] Building manifest...")
    manifest = build_manifest(parsed)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Manifest: {MANIFEST_PATH}")

    # Ingest
    print("\n[3] Ingesting into V2 DB...")
    conn = connect(str(DB_PATH))
    migrate(conn, BASE / "migrations")
    results = ingest_manifest(conn, manifest)
    print(f"  {len(results)} passages ingested")

    # Link commentaries
    print("\n[4] Linking commentaries to verses...")
    n = link_commentaries(conn, manifest, parsed)
    print(f"  {n} passage_relation links created")

    # Run Vidyut morphology
    print("\n[5] Running Vidyut morphology...")
    readings = conn.execute("""
        SELECT pr.reading_id, pr.sanskrit_normalized FROM passage_readings pr
        JOIN passages p ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.passage_type = 'verse'
    """, (WORK_ID,)).fetchall()

    total = 0
    for rid, text in readings:
        if not text or len(text) < 5:
            continue
        lattice = analyze(text, ["vidyut", "fallback"])
        n = persist_lattice(conn, rid, lattice)
        total += n
    print(f"  {total} token analyses created")
    print(f"  Verse readings: {len(readings)}")

    # Run graph ontology seed
    print("\n[6] Seeding graph ontology...")
    # Inline seed: extract lexemes, analysis types, occurrences from new data
    import hashlib
    def fhash(f): return hashlib.sha256(json.dumps(f, sort_keys=True).encode()).hexdigest()[:16]
    now = datetime.now(timezone.utc).isoformat()
    rows = conn.execute("""
        SELECT DISTINCT ta.lemma FROM token_analyses ta
        WHERE ta.lemma IS NOT NULL AND ta.lemma != ''
          AND ta.lemma NOT IN (SELECT lemma_slp1 FROM lexeme)
    """).fetchall()
    for (lemma,) in rows:
        conn.execute("INSERT OR IGNORE INTO lexeme (lexeme_id, lemma_slp1, pos, created_at) VALUES (?,?,?,?)",
                     (f"lex_{lemma}", lemma, "unknown", now))
    print(f"  Lexemes added: {len(rows)}")
    rows2 = conn.execute("""
        SELECT DISTINCT ta.lemma, ta.features_json FROM token_analyses ta
        WHERE ta.lemma IS NOT NULL AND ta.lemma != ''
    """).fetchall()
    atypes = 0
    for lemma, feat_json in rows2:
        features = json.loads(feat_json) if feat_json else {}
        fh = fhash(features)
        conn.execute("INSERT OR IGNORE INTO morph_analysis_type (analysis_type_id, lexeme_id, features_json, features_hash, created_at) VALUES (?,?,?,?,?)",
                     (f"mat_{lemma}_{fh}", f"lex_{lemma}", json.dumps(features, sort_keys=True), fh, now))
        atypes += 1
    print(f"  Analysis types added: {atypes}")
    rows3 = conn.execute("""
        SELECT t.token_id, t.reading_id, t.token_index, t.surface, t.start_offset, t.end_offset
        FROM tokens t WHERE t.reading_id NOT IN (SELECT passage_reading_id FROM token_occurrence)
    """).fetchall()
    occs = 0
    for tid, rid, idx, surface, start, end in rows3:
        conn.execute("INSERT OR IGNORE INTO token_occurrence (occurrence_id, passage_reading_id, token_index, surface, start_offset, end_offset) VALUES (?,?,?,?,?,?)",
                     (f"occ_{rid}_{idx}", rid, idx, surface, start, end))
        occs += 1
    print(f"  Occurrences added: {occs}")
    conn.commit()

    # Factor graph
    print("\n[7] Running factor graph inference...")
    fg_results = run_factor_graph(conn, WORK_ID)
    n_ok = sum(1 for _, _, _, e in fg_results if e < 10.0)
    for vs, nt, nh, energy in fg_results[:5]:
        print(f"  Verse {vs}: {nt} tokens / {nh} hyps  energy={energy:.2f}")
    if len(fg_results) > 5:
        print(f"  ... and {len(fg_results) - 5} more")
    print(f"\n  Valid assignments: {n_ok}/{len(fg_results)}")

    # Stats
    for table in ["lexeme", "morph_analysis_type", "token_occurrence",
                   "token_analysis_hypothesis", "passage_relation"]:
        n = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n}")

    conn.close()
    print(f"\nDone.")


if __name__ == "__main__":
    main()
