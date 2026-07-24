-- Sprint 1: Adjudication schema for gold annotation

CREATE TABLE IF NOT EXISTS adjudication_decisions (
    decision_id TEXT PRIMARY KEY,
    passage_id TEXT NOT NULL REFERENCES passages(passage_id),
    annotator TEXT NOT NULL DEFAULT 'system',
    layer TEXT NOT NULL,
    -- segmentation | morphology | compound | syntax | lexical_sense | frame | alignment | translation
    candidate_hypothesis_id TEXT,
    candidate_text TEXT,
    status TEXT NOT NULL,
    -- accepted | acceptable_alternative | rejected | unresolved
    reason_code TEXT,
    -- MORPHOLOGY_INCOMPATIBLE | SANDHI_INVALID | WRONG_COMPOUND_RELATION
    -- FRAME_ROLE_INCOMPATIBLE | COMMENTARY_SUPPORT | PARALLEL_SUPPORT
    -- TRADITION_SENSE | UNSUPPORTED_ADDITION | ACCEPTABLE_VARIANT
    -- INSUFFICIENT_EVIDENCE | CORRECT | OOV
    reason_note TEXT,
    evidence_family_id TEXT,
    created_at TEXT NOT NULL,
    graph_version TEXT
);

CREATE INDEX IF NOT EXISTS idx_adjudication_passage ON adjudication_decisions(passage_id);
CREATE INDEX IF NOT EXISTS idx_adjudication_layer ON adjudication_decisions(layer);
CREATE INDEX IF NOT EXISTS idx_adjudication_status ON adjudication_decisions(status);

CREATE TABLE IF NOT EXISTS adjudication_sessions (
    session_id TEXT PRIMARY KEY,
    passage_id TEXT NOT NULL REFERENCES passages(passage_id),
    annotator TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    candidates_shown INTEGER,
    decisions_made INTEGER,
    notes TEXT
);
