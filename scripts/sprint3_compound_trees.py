"""Sprint 3: Nested compound trees — extend from flat labels to nested structure."""
from __future__ import annotations

import json
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")


def create_compound_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS compound_tree_hypothesis (
            tree_id TEXT PRIMARY KEY,
            passage_id TEXT NOT NULL REFERENCES passages(passage_id),
            token_index INTEGER NOT NULL,
            surface TEXT NOT NULL,
            structure_json TEXT NOT NULL,
            -- nested JSON: {"type": "karmadharaya", "left": {"lemma": "..."}, "right": {"type": "tatpurusa", ...}}
            root_relation TEXT NOT NULL,
            depth INTEGER NOT NULL,
            covers_source_span INTEGER NOT NULL DEFAULT 1,
            engine TEXT NOT NULL,
            confidence REAL,
            status TEXT NOT NULL DEFAULT 'proposed',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS compound_component (
            component_id TEXT PRIMARY KEY,
            tree_id TEXT NOT NULL REFERENCES compound_tree_hypothesis(tree_id),
            node_path TEXT NOT NULL,
            -- e.g. "left" or "right.left" for nesting
            lemma_slp1 TEXT,
            lemma_iast TEXT,
            surface_form TEXT,
            component_type TEXT NOT NULL,
            -- leaf | internal
            relation TEXT,
            -- karmadharaya | tatpurusa | bahuvrihi | dvandva | etc
            confidence REAL
        );

        CREATE INDEX IF NOT EXISTS idx_compound_tree_passage ON compound_tree_hypothesis(passage_id);
    """)
    conn.commit()


def build_compound_tree(surface: str, members: list[str], relations: list[str]) -> dict:
    """Build a nested compound tree from members and relations.

    Example:
        surface = "tvanmayacittatayā"
        members = ["tvad", "maya", "citta", "tā"]
        relations = ["tatpurusa", "karmadharaya", "karmadharaya"]

    Returns nested dict structure.
    """
    def make_node(member_or_subtree, relation=None):
        if isinstance(member_or_subtree, str):
            return {"type": "leaf", "lemma": member_or_subtree}
        return {
            "type": "internal",
            "relation": relation,
            "left": member_or_subtree[0],
            "right": member_or_subtree[1],
        }

    if len(members) == 2:
        return {
            "type": "internal",
            "relation": relations[0] if relations else "unknown",
            "left": make_node(members[0]),
            "right": make_node(members[1]),
        }

    # For 3+ members, build left-associative tree
    # [[[A B] C] D] ...
    current = make_node(members[0])
    for i in range(1, len(members)):
        rel = relations[i - 1] if i - 1 < len(relations) else "unknown"
        current = {
            "type": "internal",
            "relation": rel,
            "left": current,
            "right": make_node(members[i]),
        }
    return current


def seed_trees_for_verse(conn, passage_id: str, token_index: int, surface: str,
                          members: list[str], relations: list[str], engine: str = "manual"):
    """Seed one compound tree hypothesis."""
    now = datetime.now(timezone.utc).isoformat()
    tree = build_compound_tree(surface, members, relations)
    tree_id = f"ct_{passage_id}_{token_index}_{uuid.uuid4().hex[:8]}"

    conn.execute("""INSERT INTO compound_tree_hypothesis
        (tree_id, passage_id, token_index, surface, structure_json,
         root_relation, depth, engine, confidence, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?)""",
        (tree_id, passage_id, token_index, surface, json.dumps(tree),
         tree.get("relation", "unknown"),
         len(members) - 1,
         engine, 0.7, now))

    # Flatten tree into components
    def flatten(node, path=""):
        if node["type"] == "leaf":
            cid = f"cc_{tree_id}_{path or 'root'}"
            conn.execute("""INSERT INTO compound_component
                (component_id, tree_id, node_path, lemma_slp1, component_type, confidence)
                VALUES (?, ?, ?, ?, 'leaf', 0.8)""",
                (cid, tree_id, path, node.get("lemma", "")))
        else:
            cid = f"cc_{tree_id}_{path or 'root'}"
            conn.execute("""INSERT INTO compound_component
                (component_id, tree_id, node_path, component_type, relation, confidence)
                VALUES (?, ?, ?, 'internal', ?, 0.7)""",
                (cid, tree_id, path, node.get("relation", "unknown")))
            flatten(node.get("left", {}), f"{path}.left" if path else "left")
            flatten(node.get("right", {}), f"{path}.right" if path else "right")

    flatten(tree)
    conn.commit()
    return tree_id


def seed_known_compounds(conn):
    """Seed known compound trees for Bhairavastava and Spanda."""
    compounds = [
        # Bhairavastava v1
        ("bhairavastava.1", 0, "bhairavanātham",
         ["bhairava", "nātha"], ["karmadharaya"]),
        ("bhairavastava.1", 1, "anāthaśaraṇyam",
         ["anātha", "śaraṇya"], ["tatpurusa"]),
        # tvanmayacittatayā = [[[tvad + maya] + citta] + tā] + yā? Complex
        # For now, simplified: [tvad-maya] + [citta-tā]
        ("bhairavastava.1", 2, "tvanmayacittatayā",
         ["tvad", "maya", "citta", "tā"], ["karmadharaya", "tatpurusa", "karmadharaya"]),
        # Verse 4
        ("bhairavastava.4", 0, "śaṅkarasevanacintanadhīra",
         ["śaṅkara", "sevana", "cintana", "dhīra"], ["tatpurusa", "karmadharaya", "karmadharaya"]),
        ("bhairavastava.4", 1, "bhīṣaṇabhairavaśaktimaya",
         ["bhīṣaṇa", "bhairava", "śakti", "maya"], ["karmadharaya", "tatpurusa", "karmadharaya"]),
        # Spanda v1
        ("spk.1.1", 0, "śakticakravibhavaprabhava",
         ["śakti", "cakra", "vibhava", "prabhava"], ["tatpurusa", "tatpurusa", "karmadharaya"]),
    ]

    count = 0
    for pid, idx, surface, members, relations in compounds:
        try:
            seed_trees_for_verse(conn, pid, idx, surface, members, relations)
            count += 1
        except Exception as e:
            print(f"  Error seeding {surface}: {e}")
    return count


def report_trees(conn):
    """Report compound tree coverage."""
    n_trees = conn.execute("SELECT count(*) FROM compound_tree_hypothesis").fetchone()[0]
    n_components = conn.execute("SELECT count(*) FROM compound_component").fetchone()[0]
    print(f"\n  Trees: {n_trees}")
    print(f"  Components: {n_components}")
    
    trees = conn.execute("""
        SELECT surface, root_relation, depth FROM compound_tree_hypothesis
        ORDER BY created_at
    """).fetchall()
    for surface, rel, depth in trees:
        print(f"    {surface:30s} rel={rel:15s} depth={depth}")


def main():
    print("Sprint 3: Nested compound trees\n")
    conn = connect(DB)
    create_compound_tables(conn)

    print("[1] Seeding known compounds...")
    n = seed_known_compounds(conn)
    print(f"  {n} trees seeded")

    print("\n[2] Report:")
    report_trees(conn)

    # Show one tree structure
    tree = conn.execute("""
        SELECT surface, structure_json FROM compound_tree_hypothesis LIMIT 1
    """).fetchone()
    if tree:
        print(f"\n[3] Sample tree: {tree[0]}")
        print(json.dumps(json.loads(tree[1]), indent=2))

    conn.close()
    print("\nSprint 3 complete.")


if __name__ == "__main__":
    main()
