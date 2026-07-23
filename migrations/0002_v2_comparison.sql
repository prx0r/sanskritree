CREATE TABLE IF NOT EXISTS formal_relations (
  formal_relation_id TEXT PRIMARY KEY,
  formalization_a_id TEXT NOT NULL REFERENCES formalizations(formalization_id),
  formalization_b_id TEXT NOT NULL REFERENCES formalizations(formalization_id),
  classification TEXT NOT NULL,
  bridge_assumptions_json TEXT NOT NULL DEFAULT '[]',
  evidence_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_passage_readings_passage ON passage_readings(passage_id);
CREATE INDEX IF NOT EXISTS idx_token_analyses_token ON token_analyses(token_id);
CREATE INDEX IF NOT EXISTS idx_semantic_frames_passage ON semantic_frames(source_passage_id);
