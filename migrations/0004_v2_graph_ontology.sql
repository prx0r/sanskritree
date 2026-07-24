-- V2 Graph Ontology: separate TOKEN_OCCURRENCE, MORPH_ANALYSIS_TYPE, LEXEME
-- Each surface occurrence is distinct from the reusable analysis type.

CREATE TABLE IF NOT EXISTS lexeme (
    lexeme_id TEXT PRIMARY KEY,
    lemma_slp1 TEXT NOT NULL,
    lemma_iast TEXT,
    lemma_devanagari TEXT,
    pos TEXT,
    -- opens | closes | saves | noun | verb | indeclinable | etc
    created_at TEXT NOT NULL,
    UNIQUE(lemma_slp1)
);

CREATE TABLE IF NOT EXISTS morph_analysis_type (
    analysis_type_id TEXT PRIMARY KEY,
    lexeme_id TEXT NOT NULL REFERENCES lexeme(lexeme_id),
    -- grammatical features as a canonical JSON blob
    features_json TEXT NOT NULL,
    -- hash for deduplication
    features_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(lexeme_id, features_hash)
);

CREATE TABLE IF NOT EXISTS token_occurrence (
    occurrence_id TEXT PRIMARY KEY,
    passage_reading_id TEXT NOT NULL REFERENCES passage_readings(reading_id),
    token_index INTEGER NOT NULL,
    surface TEXT NOT NULL,
    start_offset INTEGER NOT NULL,
    end_offset INTEGER NOT NULL,
    UNIQUE(passage_reading_id, token_index)
);

CREATE TABLE IF NOT EXISTS token_analysis_hypothesis (
    hypothesis_id TEXT PRIMARY KEY,
    occurrence_id TEXT NOT NULL REFERENCES token_occurrence(occurrence_id),
    analysis_type_id TEXT NOT NULL REFERENCES morph_analysis_type(analysis_type_id),
    engine TEXT NOT NULL,
    confidence REAL,
    status TEXT NOT NULL DEFAULT 'proposed',
    -- proposed | accepted | rejected | superseded
    created_at TEXT NOT NULL,
    UNIQUE(occurrence_id, analysis_type_id, engine)
);

-- Many-to-many passage relations for commentary anchoring
CREATE TABLE IF NOT EXISTS passage_relation (
    relation_id TEXT PRIMARY KEY,
    source_passage_id TEXT NOT NULL REFERENCES passages(passage_id),
    target_passage_id TEXT NOT NULL REFERENCES passages(passage_id),
    relation_type TEXT NOT NULL,
    -- COMMENTARY_ON | COMMENTS_ON_SPAN | INTRODUCES_SECTION
    -- QUOTES | PARAPHRASES | EXPLAINS_TERM | APPLIES_TO_RANGE
    source_span_start INTEGER,
    source_span_end INTEGER,
    target_span_start INTEGER,
    target_span_end INTEGER,
    confidence REAL,
    provenance TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(source_passage_id, target_passage_id, relation_type)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_token_occ_reading ON token_occurrence(passage_reading_id);
CREATE INDEX IF NOT EXISTS idx_token_hyp_occ ON token_analysis_hypothesis(occurrence_id);
CREATE INDEX IF NOT EXISTS idx_token_hyp_status ON token_analysis_hypothesis(status);
CREATE INDEX IF NOT EXISTS idx_morph_type_lexeme ON morph_analysis_type(lexeme_id);
CREATE INDEX IF NOT EXISTS idx_passage_rel_source ON passage_relation(source_passage_id);
CREATE INDEX IF NOT EXISTS idx_passage_rel_target ON passage_relation(target_passage_id);
