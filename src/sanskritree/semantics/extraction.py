from __future__ import annotations
import json
from .schema import SemanticFrame


def persist_frame(conn, frame: SemanticFrame, review_status: str = "unreviewed") -> None:
    conn.execute("INSERT INTO semantic_frames VALUES (?,?,?,?,?,?,?,?,?,?,?)", (frame.frame_id, frame.source_passage_id, frame.source_span, frame.discourse_mode, json.dumps(frame.subject.asdict() if hasattr(frame.subject, 'asdict') else {"label": frame.subject.label, "class_name": frame.subject.class_name}), frame.relation, json.dumps({"label": frame.object.label, "class_name": frame.object.class_name}), frame.explicitness, frame.confidence, json.dumps(frame.alternatives), review_status))
    conn.commit()
