#!/usr/bin/env python3
"""
Export nodes from proof_engine.db to JSON for the frontend.
Run from sanskritree root: python frontend/export_nodes.py
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "proof_engine" / "proof_engine.db"


def layout_tree(nodes: list[dict]) -> list[dict]:
    """Simple tree layout: root center, children spread horizontally."""
    by_parent: dict[int | None, list] = {}
    for n in nodes:
        pid = n.get("parent_id")
        by_parent.setdefault(pid, []).append(n)

    def place(node: dict, x: float, y: float, dx: float):
        node["x"] = int(x)
        node["y"] = int(y)
        children = by_parent.get(node["id"]) or []
        n = len(children)
        for i, c in enumerate(children):
            cx = x + (i - (n - 1) / 2) * dx
            place(c, cx, y - 200, dx * 0.6)

    roots = by_parent.get(None) or []
    for i, r in enumerate(roots):
        place(r, 4800 + i * 800, 4800, 400)

    return nodes


def main():
    db_path = ROOT / "proof_engine.db" if (ROOT / "proof_engine.db").exists() else DB
    if not db_path.exists():
        print(json.dumps({"nodes": [], "edges": [], "bridges": []}), file=sys.stdout)
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, parent_id, statement, sanskrit, lean_type, status, provenance FROM nodes"
    ).fetchall()
    conn.close()

    nodes = [dict(r) for r in rows]
    if nodes:
        prov = nodes[0].get("provenance")
        if isinstance(prov, str):
            for n in nodes:
                if n.get("provenance"):
                    try:
                        n["tradition"] = json.loads(n["provenance"] or "{}").get("tradition", "")
                    except Exception:
                        n["tradition"] = ""
        else:
            for n in nodes:
                n["tradition"] = (n.get("provenance") or {}).get("tradition", "")
        nodes = layout_tree(nodes)

    edges = [{"from": n["id"], "to": n["parent_id"]} for n in nodes if n.get("parent_id")]

    out = {"nodes": nodes, "edges": edges, "bridges": []}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
