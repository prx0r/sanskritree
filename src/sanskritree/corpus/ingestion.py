from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .normalization import normalize_sanskrit
from ..database import source_hash


@dataclass(frozen=True)
class IngestResult:
    work_id: str
    edition_id: str
    passage_id: str
    reading_id: str


def load_manifest(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith(".json"):
        return json.loads(text)
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("YAML manifests require PyYAML; install requirements-v2.txt") from exc
    return yaml.safe_load(text)


def ingest_manifest(conn, manifest: dict[str, Any], base_dir: str | Path = ".") -> list[IngestResult]:
    """Ingest a deliberately small, explicit manifest. Source text remains byte-identical."""
    work = manifest["work"]
    edition = manifest["edition"]
    conn.execute("INSERT OR IGNORE INTO works (work_id, canonical_title, title_iast, tradition, genre, metadata_json) VALUES (?,?,?,?,?,?)",
                 (work["id"], work["title"], work.get("title_iast"), work.get("tradition"), work.get("genre"), json.dumps(work.get("metadata", {}), sort_keys=True)))
    conn.execute("INSERT OR IGNORE INTO editions (edition_id, work_id, editor, publication, year, source_url, licence, critical_method, source_hash) VALUES (?,?,?,?,?,?,?,?,?)",
                 (edition["id"], work["id"], edition.get("editor"), edition.get("publication"), edition.get("year"), edition.get("source_url"), edition.get("licence"), edition.get("critical_method"), source_hash(json.dumps(edition, sort_keys=True))))
    results = []
    for index, item in enumerate(manifest["passages"]):
        passage_id = item["id"]
        conn.execute("INSERT OR IGNORE INTO passages (passage_id, work_id, edition_id, chapter, section, verse_start, verse_end, sequence_index, passage_type) VALUES (?,?,?,?,?,?,?,?,?)",
                     (passage_id, work["id"], edition["id"], item.get("chapter"), item.get("section"), item.get("verse"), item.get("verse_end", item.get("verse")), index, item.get("type", "verse")))
        raw = item["sanskrit"]
        reading_id = item.get("reading_id", f"{passage_id}.reading.{edition['id']}")
        conn.execute("INSERT OR IGNORE INTO passage_readings VALUES (?,?,?,?,?,?,?,?,?)",
                     (reading_id, passage_id, edition["id"], raw, normalize_sanskrit(raw), item.get("transliteration", "IAST"), item.get("critical_status"), item.get("source_page"), source_hash(raw)))
        for translation in item.get("translations", []):
            translator_id = translation["translator_id"]
            conn.execute("INSERT OR IGNORE INTO translators VALUES (?,?,?)", (translator_id, translation.get("translator", translator_id), "{}"))
            conn.execute("INSERT OR IGNORE INTO translations VALUES (?,?,?,?,?,?,?,?,?)",
                         (translation.get("id", str(uuid.uuid4())), reading_id, translator_id, None, translation.get("type", "published_translation"), translation.get("language", "en"), translation["text"], translation.get("source_page"), "imported"))
        results.append(IngestResult(work["id"], edition["id"], passage_id, reading_id))
    conn.commit()
    return results


def audit_event(conn, entity_type: str, entity_id: str, actor: str, old_value: Any, new_value: Any, reason: str, evidence: Any) -> str:
    event_id = str(uuid.uuid4())
    conn.execute("INSERT INTO review_events VALUES (?,?,?,?,?,?,?,?,?)", (event_id, entity_type, entity_id, actor, json.dumps(old_value), json.dumps(new_value), reason, json.dumps(evidence), datetime.now(timezone.utc).isoformat()))
    conn.commit()
    return event_id
