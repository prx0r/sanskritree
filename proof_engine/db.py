"""
Database schema per proofenginge.md + Schema v3.
Nodes, edges, terms, contradictions, bridge_index, traces.
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Optional

NODE_TYPES = ("FORMAL", "EMPIRICAL", "DEFINITION", "UNSAYABLE", "CLAIM", "INFERENCE", "PERCEPTION", "PĀṆINI")
STATUSES = ("PROVED", "UNPROVED", "PARTIAL", "HOLLOW", "OUTSIDE_FORMAL", "REFUTED", "PARTIAL_HOLLOW")


def _migrate(conn: sqlite3.Connection):
    """Add new columns/tables if missing."""
    cur = conn.execute("PRAGMA table_info(nodes)")
    cols = {r[1] for r in cur.fetchall()}
    if "kanda" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN kanda INTEGER DEFAULT 2")
    if "inherited_from" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN inherited_from INTEGER")
    if "delta_terms" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN delta_terms TEXT")
    if "logic_foundation" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN logic_foundation TEXT DEFAULT 'classical'")
    if "template_used" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN template_used TEXT")
    if "retry_count" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN retry_count INTEGER DEFAULT 0")
    if "human_review" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN human_review INTEGER DEFAULT 0")
    if "decomp_source" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN decomp_source TEXT")
    if "absence_type" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN absence_type TEXT")
    if "source_module" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN source_module TEXT")
    if "primitive_ids" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN primitive_ids TEXT")
    conn.commit()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER NOT NULL,
            child_id INTEGER NOT NULL,
            edge_type TEXT NOT NULL,
            relation TEXT,
            provenance TEXT,
            human_confirmed INTEGER DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES nodes(id),
            FOREIGN KEY (child_id) REFERENCES nodes(id),
            UNIQUE(parent_id, child_id, edge_type)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            tid INTEGER PRIMARY KEY AUTOINCREMENT,
            iast TEXT NOT NULL,
            tradition TEXT NOT NULL,
            lean_type_repr TEXT,
            sembank_synset TEXT,
            definition_node_id INTEGER,
            UNIQUE(iast, tradition),
            FOREIGN KEY (definition_node_id) REFERENCES nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contradictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_a INTEGER NOT NULL,
            node_b INTEGER NOT NULL,
            contradiction_scope TEXT,
            defeat_argument INTEGER,
            resolution TEXT,
            human_confirmed INTEGER DEFAULT 0,
            FOREIGN KEY (node_a) REFERENCES nodes(id),
            FOREIGN KEY (node_b) REFERENCES nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bridge_index (
            lean_type_hash TEXT NOT NULL,
            node_id INTEGER NOT NULL,
            tradition TEXT,
            PRIMARY KEY (lean_type_hash, node_id),
            FOREIGN KEY (node_id) REFERENCES nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            node_id INTEGER NOT NULL,
            anchor TEXT,
            tradition TEXT,
            source_text TEXT,
            layer0 TEXT,
            layer1 TEXT,
            layer3 TEXT,
            layer5 TEXT,
            metadata TEXT,
            created_at TEXT,
            FOREIGN KEY (node_id) REFERENCES nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS validation_set (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nn_expr TEXT,
            expected_lean_type TEXT,
            tradition TEXT,
            passed INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS primitives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            primitive_id TEXT NOT NULL UNIQUE,
            definition TEXT,
            lean_hint TEXT,
            source TEXT,
            mathlib_ref TEXT,
            status TEXT DEFAULT 'to_formalize',
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ground_truth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            module_path TEXT,
            item_name TEXT,
            item_type TEXT,
            lean_signature TEXT,
            relevance TEXT,
            notes TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY,
            tradition TEXT NOT NULL,
            statement TEXT NOT NULL,
            plain TEXT,
            primitive_hint TEXT,
            sanskrit TEXT,
            lean_type TEXT,
            node_id INTEGER,
            created_at TEXT,
            FOREIGN KEY (node_id) REFERENCES nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decompositions (
            id TEXT PRIMARY KEY,
            claim_id TEXT NOT NULL,
            component_text TEXT,
            primitive_id TEXT,
            maps_cleanly INTEGER,
            residue TEXT,
            created_at TEXT,
            FOREIGN KEY (claim_id) REFERENCES claims(id),
            FOREIGN KEY (primitive_id) REFERENCES primitives(primitive_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS negative_controls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            a TEXT NOT NULL,
            b TEXT NOT NULL,
            reason TEXT,
            source TEXT,
            failure_type TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS failure_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id TEXT,
            node_id INTEGER,
            failure_type TEXT NOT NULL,
            context TEXT,
            lean_output TEXT,
            primitive_candidate TEXT,
            created_at TEXT,
            FOREIGN KEY (claim_id) REFERENCES claims(id),
            FOREIGN KEY (node_id) REFERENCES nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS primitive_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT NOT NULL,
            definition TEXT,
            source_claim_id TEXT,
            source_residue TEXT,
            status TEXT DEFAULT 'candidate',
            created_at TEXT,
            FOREIGN KEY (source_claim_id) REFERENCES claims(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS claim_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            bridge_axioms TEXT,
            evidence TEXT,
            verified_by TEXT,
            created_at TEXT,
            FOREIGN KEY (source_id) REFERENCES claims(id),
            FOREIGN KEY (target_id) REFERENCES claims(id),
            UNIQUE(source_id, target_id)
        )
    """)
    conn.commit()

    # Edges: add relation_metadata for bridge_axioms (after edges table exists)
    cur = conn.execute("PRAGMA table_info(edges)")
    edge_cols = {r[1] for r in cur.fetchall()}
    if "relation_metadata" not in edge_cols:
        conn.execute("ALTER TABLE edges ADD COLUMN relation_metadata TEXT")
    conn.commit()

    # Claims: add status column
    cur = conn.execute("PRAGMA table_info(claims)")
    claim_cols = {r[1] for r in cur.fetchall()}
    if "status" not in claim_cols:
        conn.execute("ALTER TABLE claims ADD COLUMN status TEXT DEFAULT 'PENDING'")
    conn.commit()


def init_db(path: str = "proof_engine.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id     INTEGER,
            statement     TEXT NOT NULL,
            sanskrit      TEXT,
            devanagari    TEXT,
            provenance    TEXT,
            node_type     TEXT NOT NULL,
            status        TEXT NOT NULL,
            lean_type     TEXT,
            lean_proof    TEXT,
            mathlib_deps  TEXT,
            reuse_count   INTEGER DEFAULT 0,
            notes         TEXT,
            created_at    TEXT
        )
    """)
    conn.commit()
    _migrate(conn)
    return conn


def lean_type_hash(lean_type: str) -> str:
    return hashlib.md5((lean_type or "").encode()).hexdigest()


def add_node(
    conn: sqlite3.Connection,
    parent_id: Optional[int],
    statement: str,
    *,
    sanskrit: Optional[str] = None,
    devanagari: Optional[str] = None,
    provenance: Optional[dict] = None,
    node_type: str = "FORMAL",
    status: str = "UNPROVED",
    lean_type: Optional[str] = None,
    lean_proof: Optional[str] = None,
    mathlib_deps: Optional[list] = None,
    notes: Optional[str] = None,
    kanda: int = 2,
    inherited_from: Optional[int] = None,
    delta_terms: Optional[list] = None,
    logic_foundation: str = "classical",
    decomp_source: Optional[str] = None,
    source_module: Optional[str] = None,
    primitive_ids: Optional[list] = None,
) -> int:
    cols = ["parent_id", "statement", "sanskrit", "devanagari", "provenance", "node_type", "status",
            "lean_type", "lean_proof", "mathlib_deps", "reuse_count", "notes", "created_at",
            "kanda", "inherited_from", "delta_terms", "logic_foundation", "decomp_source",
            "source_module", "primitive_ids"]
    vals = [
        parent_id, statement, sanskrit, devanagari,
        json.dumps(provenance) if provenance else None,
        node_type, status, lean_type, lean_proof,
        json.dumps(mathlib_deps) if mathlib_deps else None,
        0, notes, datetime.now().isoformat(),
        kanda, inherited_from, json.dumps(delta_terms) if delta_terms else None,
        logic_foundation, decomp_source,
        source_module, json.dumps(primitive_ids) if primitive_ids else None,
    ]
    ph = ",".join("?" * len(cols))
    conn.execute(f"INSERT INTO nodes ({','.join(cols)}) VALUES ({ph})", vals)
    conn.commit()
    nid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return nid


def add_edge(conn: sqlite3.Connection, parent_id: int, child_id: int, edge_type: str = "decomposition", **kw) -> int:
    conn.execute("""
        INSERT OR IGNORE INTO edges (parent_id, child_id, edge_type, relation, provenance, human_confirmed)
        VALUES (?,?,?,?,?,?)
    """, (parent_id, child_id, edge_type, kw.get("relation"), kw.get("provenance"), kw.get("human_confirmed", 0)))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def register_term(conn: sqlite3.Connection, iast: str, tradition: str, **kw) -> int:
    conn.execute("""
        INSERT OR IGNORE INTO terms (iast, tradition, lean_type_repr, sembank_synset, definition_node_id)
        VALUES (?,?,?,?,?)
    """, (iast, tradition, kw.get("lean_type_repr"), kw.get("sembank_synset"), kw.get("definition_node_id")))
    conn.commit()
    r = conn.execute("SELECT tid FROM terms WHERE iast=? AND tradition=?", (iast, tradition)).fetchone()
    return r[0] if r else 0


def get_term(conn: sqlite3.Connection, iast: str, tradition: str) -> Optional[dict]:
    r = conn.execute("SELECT * FROM terms WHERE iast=? AND tradition=?", (iast, tradition)).fetchone()
    if not r:
        return None
    cols = [d[1] for d in conn.execute("PRAGMA table_info(terms)").fetchall()]  # d[1]=name
    return dict(zip(cols, r))


def add_to_bridge_index(conn: sqlite3.Connection, node_id: int, lean_type: str, tradition: Optional[str] = None):
    h = lean_type_hash(lean_type)
    conn.execute("INSERT OR IGNORE INTO bridge_index (lean_type_hash, node_id, tradition) VALUES (?,?,?)",
                 (h, node_id, tradition))
    conn.commit()


def add_trace(conn: sqlite3.Connection, trace_id: str, node_id: int, **layers):
    conn.execute("""
        INSERT OR REPLACE INTO traces (trace_id, node_id, anchor, tradition, source_text, layer0, layer1, layer3, layer5, metadata, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        trace_id, node_id,
        layers.get("anchor"), layers.get("tradition"), layers.get("source_text"),
        json.dumps(layers.get("layer0")) if layers.get("layer0") else None,
        json.dumps(layers.get("layer1")) if layers.get("layer1") else None,
        json.dumps(layers.get("layer3")) if layers.get("layer3") else None,
        json.dumps(layers.get("layer5")) if layers.get("layer5") else None,
        json.dumps(layers.get("metadata")) if layers.get("metadata") else None,
        datetime.now().isoformat(),
    ))
    conn.commit()


def get_node(conn: sqlite3.Connection, nid: int) -> Optional[dict]:
    cur = conn.execute("SELECT * FROM nodes WHERE id=?", (nid,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [d[0] for d in cur.description]
    d = dict(zip(cols, row))
    if d.get("provenance"):
        try:
            d["provenance"] = json.loads(d["provenance"])
        except Exception:
            pass
    if d.get("mathlib_deps"):
        try:
            d["mathlib_deps"] = json.loads(d["mathlib_deps"])
        except Exception:
            pass
    if d.get("delta_terms"):
        try:
            d["delta_terms"] = json.loads(d["delta_terms"])
        except Exception:
            pass
    return d


def get_children(conn: sqlite3.Connection, nid: int) -> list[dict]:
    cur = conn.execute("SELECT * FROM nodes WHERE parent_id=?", (nid,))
    cols = [d[0] for d in cur.description]
    out = []
    for r in cur.fetchall():
        d = dict(zip(cols, r))
        if d.get("provenance"):
            try:
                d["provenance"] = json.loads(d["provenance"])
            except Exception:
                pass
        if d.get("mathlib_deps"):
            try:
                d["mathlib_deps"] = json.loads(d["mathlib_deps"])
            except Exception:
                pass
        out.append(d)
    return out


def update_status(
    conn: sqlite3.Connection,
    nid: int,
    status: str,
    lean_proof: Optional[str] = None,
    mathlib_deps: Optional[list] = None,
    lean_type: Optional[str] = None,
    human_review: Optional[bool] = None,
):
    conn.execute("""
        UPDATE nodes SET status=?, lean_proof=?, mathlib_deps=? WHERE id=?
    """, (status, lean_proof, json.dumps(mathlib_deps) if mathlib_deps else None, nid))
    if lean_type is not None:
        conn.execute("UPDATE nodes SET lean_type=? WHERE id=?", (lean_type, nid))
    if human_review is not None:
        conn.execute("UPDATE nodes SET human_review=? WHERE id=?", (1 if human_review else 0, nid))
    conn.commit()


def increment_reuse(conn: sqlite3.Connection, nid: int):
    conn.execute("UPDATE nodes SET reuse_count = reuse_count + 1 WHERE id=?", (nid,))
    conn.commit()


def find_by_lean_type(conn: sqlite3.Connection, lean_type: str) -> Optional[dict]:
    cur = conn.execute("SELECT * FROM nodes WHERE lean_type=? AND status='PROVED' LIMIT 1", (lean_type,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def add_decomposition(conn: sqlite3.Connection, claim_id: str, component_text: str, primitive_id: Optional[str] = None,
                      maps_cleanly: Optional[bool] = None, residue: Optional[str] = None) -> str:
    """Add a decomposition component. Returns decomposition id."""
    import uuid
    did = f"dec_{claim_id}_{uuid.uuid4().hex[:8]}"
    conn.execute("""
        INSERT OR REPLACE INTO decompositions (id, claim_id, component_text, primitive_id, maps_cleanly, residue, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (did, claim_id, component_text, primitive_id, 1 if maps_cleanly else 0 if maps_cleanly is False else None, residue))
    conn.commit()
    return did


def get_decompositions(conn: sqlite3.Connection, claim_id: str) -> list[dict]:
    """Get all decomposition components for a claim."""
    cur = conn.execute("SELECT * FROM decompositions WHERE claim_id=? ORDER BY id", (claim_id,))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_claim(conn: sqlite3.Connection, claim_id: str) -> Optional[dict]:
    """Get claim by id."""
    cur = conn.execute("SELECT * FROM claims WHERE id=?", (claim_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def get_all_claims(conn: sqlite3.Connection) -> list[dict]:
    """Get all claims."""
    cur = conn.execute("SELECT * FROM claims ORDER BY tradition, id")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def find_primitive(conn: sqlite3.Connection, primitive_id: str) -> Optional[dict]:
    """Find primitive by primitive_id."""
    cur = conn.execute("SELECT * FROM primitives WHERE primitive_id=?", (primitive_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def get_primitives(conn: sqlite3.Connection) -> list[dict]:
    """Get all primitives for LLM injection."""
    cur = conn.execute("SELECT primitive_id, definition, lean_hint FROM primitives WHERE status='tier2' ORDER BY primitive_id")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def is_negative_control(conn: sqlite3.Connection, a_id: str, b_id: str) -> bool:
    """Check if (a,b) or (b,a) is a known non-bridge."""
    cur = conn.execute(
        "SELECT 1 FROM negative_controls WHERE (a=? AND b=?) OR (a=? AND b=?) LIMIT 1",
        (a_id, b_id, b_id, a_id),
    )
    return cur.fetchone() is not None


def add_claim_relation(
    conn: sqlite3.Connection,
    source_id: str,
    target_id: str,
    relation_type: str,
    *,
    bridge_axioms: Optional[str] = None,
    evidence: Optional[str] = None,
    verified_by: Optional[str] = None,
) -> int:
    """Add or update claim-to-claim relation from bridge probe."""
    conn.execute("""
        INSERT OR REPLACE INTO claim_relations (source_id, target_id, relation_type, bridge_axioms, evidence, verified_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (source_id, target_id, relation_type, bridge_axioms, evidence, verified_by))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def update_claim_status(conn: sqlite3.Connection, claim_id: str, status: str, lean_type: Optional[str] = None):
    """Update claim status and optionally lean_type."""
    if lean_type is not None:
        conn.execute("UPDATE claims SET lean_type=?, status=? WHERE id=?", (lean_type, status, claim_id))
    else:
        conn.execute("UPDATE claims SET status=? WHERE id=?", (status, claim_id))
    conn.commit()


def get_claims_sharing_primitives(conn: sqlite3.Connection) -> list[tuple[dict, dict]]:
    """Get pairs of claims that share at least one primitive. For bridge probe."""
    def prims(c: dict) -> set:
        dec = get_decompositions(conn, c["id"])
        s = {d["primitive_id"] for d in dec if d.get("primitive_id")}
        if c.get("primitive_hint"):
            s.add(c["primitive_hint"])
        return s

    claims = get_all_claims(conn)
    pairs = []
    for i, a in enumerate(claims):
        pa = prims(a)
        for b in claims[i + 1:]:
            if pa & prims(b):
                pairs.append((a, b))
    return pairs
