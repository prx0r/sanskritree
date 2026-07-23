-- Sanskritree V2. Raw sources are immutable; derived values live separately.
CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS works (
  work_id TEXT PRIMARY KEY, canonical_title TEXT NOT NULL, title_iast TEXT,
  title_devanagari TEXT, author TEXT, tradition TEXT, subtradition TEXT,
  estimated_date_start INTEGER, estimated_date_end INTEGER, genre TEXT,
  parent_work_id TEXT, metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS editions (
  edition_id TEXT PRIMARY KEY, work_id TEXT NOT NULL REFERENCES works(work_id), editor TEXT,
  publication TEXT, year INTEGER, source_url TEXT, licence TEXT, base_witnesses_json TEXT,
  critical_method TEXT, source_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS translators (
  translator_id TEXT PRIMARY KEY, name TEXT NOT NULL, profile_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS publications (
  publication_id TEXT PRIMARY KEY, citation TEXT NOT NULL, source_url TEXT, licence TEXT
);
CREATE TABLE IF NOT EXISTS passages (
  passage_id TEXT PRIMARY KEY, work_id TEXT NOT NULL REFERENCES works(work_id),
  edition_id TEXT REFERENCES editions(edition_id), parent_passage_id TEXT,
  chapter TEXT, section TEXT, verse_start TEXT, verse_end TEXT, sequence_index INTEGER NOT NULL,
  passage_type TEXT NOT NULL DEFAULT 'verse'
);
CREATE TABLE IF NOT EXISTS passage_readings (
  reading_id TEXT PRIMARY KEY, passage_id TEXT NOT NULL REFERENCES passages(passage_id),
  witness_or_edition_id TEXT NOT NULL, sanskrit_raw TEXT NOT NULL,
  sanskrit_normalized TEXT NOT NULL, transliteration_scheme TEXT NOT NULL,
  critical_status TEXT, source_page TEXT, source_hash TEXT NOT NULL,
  UNIQUE(passage_id, witness_or_edition_id, source_hash)
);
CREATE TABLE IF NOT EXISTS translations (
  translation_id TEXT PRIMARY KEY, reading_id TEXT NOT NULL REFERENCES passage_readings(reading_id),
  translator_id TEXT REFERENCES translators(translator_id), publication_id TEXT REFERENCES publications(publication_id),
  translation_type TEXT NOT NULL, language TEXT NOT NULL, text TEXT NOT NULL,
  source_page TEXT, review_status TEXT NOT NULL DEFAULT 'unreviewed'
);
CREATE TABLE IF NOT EXISTS tokens (
  token_id TEXT PRIMARY KEY, reading_id TEXT NOT NULL REFERENCES passage_readings(reading_id),
  token_index INTEGER NOT NULL, surface TEXT NOT NULL, start_offset INTEGER NOT NULL, end_offset INTEGER NOT NULL,
  UNIQUE(reading_id, token_index)
);
CREATE TABLE IF NOT EXISTS token_analyses (
  analysis_id TEXT PRIMARY KEY, token_id TEXT NOT NULL REFERENCES tokens(token_id), engine TEXT NOT NULL,
  lemma TEXT, features_json TEXT NOT NULL DEFAULT '{}', analysis_json TEXT NOT NULL DEFAULT '{}',
  confidence REAL, review_status TEXT NOT NULL DEFAULT 'unreviewed', rejected_reason TEXT
);
CREATE TABLE IF NOT EXISTS alignments (
  alignment_id TEXT PRIMARY KEY, translation_id TEXT NOT NULL REFERENCES translations(translation_id),
  source_span_start INTEGER NOT NULL, source_span_end INTEGER NOT NULL,
  target_span_start INTEGER NOT NULL, target_span_end INTEGER NOT NULL,
  relation_type TEXT NOT NULL, confidence REAL, evidence_json TEXT NOT NULL DEFAULT '{}',
  review_status TEXT NOT NULL DEFAULT 'unreviewed'
);
CREATE TABLE IF NOT EXISTS lexical_senses (
  sense_id TEXT PRIMARY KEY, lemma TEXT NOT NULL, tradition TEXT, historical_layer TEXT,
  short_gloss TEXT NOT NULL, definition TEXT, semantic_class TEXT
);
CREATE TABLE IF NOT EXISTS sense_evidence (
  evidence_id TEXT PRIMARY KEY, sense_id TEXT NOT NULL REFERENCES lexical_senses(sense_id),
  passage_id TEXT NOT NULL REFERENCES passages(passage_id), translation_id TEXT REFERENCES translations(translation_id),
  source_span TEXT NOT NULL, target_span TEXT, evidence_type TEXT NOT NULL, weight REAL,
  review_status TEXT NOT NULL DEFAULT 'unreviewed'
);
CREATE TABLE IF NOT EXISTS translation_runs (
  run_id TEXT PRIMARY KEY, passage_id TEXT NOT NULL REFERENCES passages(passage_id), mode TEXT NOT NULL,
  model TEXT, prompt_version TEXT NOT NULL, retrieval_results_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL, reference_revealed_at TEXT
);
CREATE TABLE IF NOT EXISTS translation_candidates (
  candidate_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES translation_runs(run_id),
  profile TEXT NOT NULL, text TEXT NOT NULL, sense_choices_json TEXT NOT NULL DEFAULT '[]',
  parse_choices_json TEXT NOT NULL DEFAULT '[]', ranking_json TEXT NOT NULL DEFAULT '{}',
  immutable INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS semantic_frames (
  frame_id TEXT PRIMARY KEY, source_passage_id TEXT NOT NULL REFERENCES passages(passage_id),
  source_span TEXT NOT NULL, discourse_mode TEXT NOT NULL, subject_json TEXT NOT NULL,
  relation TEXT NOT NULL, object_json TEXT NOT NULL, explicitness TEXT NOT NULL,
  confidence REAL NOT NULL, alternatives_json TEXT NOT NULL DEFAULT '[]', review_status TEXT NOT NULL DEFAULT 'unreviewed'
);
CREATE TABLE IF NOT EXISTS formalizations (
  formalization_id TEXT PRIMARY KEY, frame_id TEXT NOT NULL REFERENCES semantic_frames(frame_id),
  lean_code TEXT NOT NULL, template_id TEXT NOT NULL, formal_role TEXT NOT NULL,
  lean_status TEXT NOT NULL, assumptions_json TEXT NOT NULL DEFAULT '[]', compiler_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS review_events (
  event_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, actor TEXT NOT NULL,
  old_value_json TEXT, new_value_json TEXT NOT NULL, reason TEXT NOT NULL, evidence_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
);
