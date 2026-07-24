-- V2 Decision Graph: trace competing interpretations through the pipeline.
-- Each hypothesis is one proposed analysis of a source span.
-- Dependencies record which decisions enable or exclude others.

CREATE TABLE IF NOT EXISTS analysis_hypothesis (
    hypothesis_id TEXT PRIMARY KEY,
    passage_reading_id TEXT NOT NULL REFERENCES passage_readings(reading_id),
    hypothesis_type TEXT NOT NULL,
    -- segmentation | morphology | compound_split | syntax | semantic_frame
    engine TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    confidence REAL,
    status TEXT NOT NULL DEFAULT 'proposed',
    -- proposed | accepted | rejected | superseded
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hypothesis_dependency (
    hypothesis_id TEXT NOT NULL REFERENCES analysis_hypothesis(hypothesis_id),
    depends_on_id TEXT NOT NULL REFERENCES analysis_hypothesis(hypothesis_id),
    relation TEXT NOT NULL,
    -- enables | excludes | refines | contradicts | same_evidence
    PRIMARY KEY (hypothesis_id, depends_on_id, relation)
);

CREATE TABLE IF NOT EXISTS translation_alignment (
    alignment_id TEXT PRIMARY KEY,
    translation_id TEXT NOT NULL REFERENCES translations(translation_id),
    source_token_id TEXT REFERENCES tokens(token_id),
    source_span_start INTEGER NOT NULL,
    source_span_end INTEGER NOT NULL,
    english_span TEXT NOT NULL,
    lexical_sense_id TEXT REFERENCES lexical_senses(sense_id),
    relation TEXT NOT NULL,
    -- direct | implicit | paraphrase | omitted | added
    confidence REAL,
    review_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE TABLE IF NOT EXISTS formalization_candidate (
    candidate_id TEXT PRIMARY KEY,
    formalization_id TEXT REFERENCES formalizations(formalization_id),
    semantic_frame_id TEXT REFERENCES semantic_frames(frame_id),
    layer TEXT NOT NULL,
    -- A = decision_object | B = frame_consistency | C = philosophical_proposition
    lean_code TEXT NOT NULL,
    assumptions_json TEXT NOT NULL DEFAULT '[]',
    compilation_status TEXT NOT NULL DEFAULT 'uncompiled',
    -- uncompiled | compiled | proven | refuted
    compiler_output TEXT,
    human_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE INDEX IF NOT EXISTS idx_hypothesis_reading ON analysis_hypothesis(passage_reading_id);
CREATE INDEX IF NOT EXISTS idx_hypothesis_dep ON hypothesis_dependency(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_alignment_translation ON translation_alignment(translation_id);
