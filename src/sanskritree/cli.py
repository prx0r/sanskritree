from __future__ import annotations
import argparse
from pathlib import Path
from .database import connect, migrate
from .corpus.ingestion import ingest_manifest, load_manifest
from .philology.analysis_lattice import persist_lattice, whitespace_lattice


def _db(args):
    conn = connect(args.database)
    migrate(conn, Path(__file__).parents[2] / "migrations")
    return conn


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sanskritree")
    parser.add_argument("--database", default="data/sanskritree-v2.db")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("ingest", "analyze", "align", "build-lexical-graph", "blind-translate", "reveal-reference", "extract-semantics", "formalize", "compare-translations"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--manifest")
        cmd.add_argument("--reading")
        cmd.add_argument("--work")
        cmd.add_argument("--passage")
        cmd.add_argument("--translator")
        cmd.add_argument("--level")
        cmd.add_argument("--engines")
        cmd.add_argument("--profiles")
        cmd.add_argument("--all-candidates", action="store_true")
    args = parser.parse_args(argv)
    conn = _db(args)
    if args.command == "ingest":
        if not args.manifest: parser.error("ingest requires --manifest")
        results = ingest_manifest(conn, load_manifest(args.manifest), Path(args.manifest).parent)
        print(f"ingested {len(results)} passages")
    elif args.command == "analyze":
        if not args.reading: parser.error("analyze requires --reading in the foundation slice")
        raw = conn.execute("SELECT sanskrit_normalized FROM passage_readings WHERE reading_id=?", (args.reading,)).fetchone()
        if raw is None: parser.error("unknown reading")
        print(f"persisted {persist_lattice(conn, args.reading, whitespace_lattice(raw[0]))} analysis candidates")
    else:
        print(f"{args.command}: scaffolded; requires reviewed records from the preceding stage")


if __name__ == "__main__":
    main()
