# Sanskritree Development Plan

## Table of Contents
1. Phase G0 — Weighted Evidence Propagation in SQLite
2. Spandakārikā Ingestion
3. Testing Checkpoints
4. Mitrasamgraha Evaluation Harness
5. Sheaf Consistency Prototype (G2)
6. Lexical Sense Inventory
7. Lean Layer B and C
8. Constrained LLM Rendering (G4)
9. Risk Assessment
10. Timeline Estimate

---

## 1. Phase G0 — Weighted Evidence Propagation in SQLite

### 1.1 New Tables

```sql
CREATE TABLE graph_nodes (
    id            TEXT PRIMARY KEY,          -- 'node:type:uuid' 
    node_type     TEXT NOT NULL,             -- 'token_analysis' | 'lexical_sense' | 'semantic_frame' | 'translation_candidate' | 'compound_reading'
    payload_id    INTEGER,                   -- FK to the specific table row
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE graph_edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id     TEXT NOT NULL REFERENCES graph_nodes(id),
    target_id     TEXT NOT NULL REFERENCES graph_nodes(id),
    relation      TEXT NOT NULL,             -- 'SUPPORTS' | 'REQUIRES' | 'EXCLUDES' | 'CONTRADICTS' | 'ALIGNS_WITH'
    weight        REAL NOT NULL DEFAULT 1.0, -- edge strength 0..1
    signed        INTEGER NOT NULL DEFAULT 1, -- +1 support, -1 opposes
    evidence_ref  TEXT,                      -- 'mitrasamgraha:p123' | 'manual:bhairavastava:v1'
    created_at    TEXT DEFAULT (datetime('now')),
    UNIQUE(source_id, target_id, relation)
);

CREATE TABLE graph_propagation_state (
    node_id       TEXT PRIMARY KEY REFERENCES graph_nodes(id),
    belief        REAL NOT NULL DEFAULT 0.0, -- aggregated belief -1..1
    confidence    REAL NOT NULL DEFAULT 0.0, -- |belief| or separate 0..1
    round         INTEGER NOT NULL DEFAULT 0,
    updated_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE evidence_sources (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,      -- 'manual_adjudication' | 'mitrasamgraha' | 'vidyut' | 'heritage' | 'dcs'
    reliability   REAL NOT NULL DEFAULT 0.5, -- 0..1 prior reliability
    is_human      INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_graph_edges_source ON graph_edges(source_id);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_id);
CREATE INDEX idx_graph_edges_relation ON graph_edges(relation);
CREATE INDEX idx_propagation_round ON graph_propagation_state(round);
```

### 1.2 Integration with Existing Tables

The 401,936 `token_analyses` rows are the primary source of graph nodes. Each distinct `(token_id, engine, analysis_type)` becomes a graph node with node_type = 'token_analysis'. Relationship to `token`:

```sql
-- View to bridge token_analyses to graph
CREATE VIEW graph_token_analysis_bridge AS
SELECT 
    'node:token_analysis:' || ta.id AS node_id,
    ta.id AS token_analysis_id,
    ta.token_id,
    ta.engine,
    ta.analysis_type,
    ta.confidence,
    t.work_id,
    t.passage_id
FROM token_analyses ta
JOIN tokens t ON t.id = ta.token_id;
```

### 1.3 Propagation Algorithm

```
Algorithm: WeightedSignedPropagation

Input:
  - G = (V, E) where each edge e = (u, v, r, w, s)
    s = +1 for SUPPORTS/REQUIRES, -1 for EXCLUDES/CONTRADICTS
  - B^0 = initial beliefs from evidence_sources.reliability
  - α = decay factor (default 0.85)
  - θ = convergence threshold (default 0.001)
  - max_iterations = 20

Output:
  - B* = converged belief vector

For round t = 1..max_iterations:
  For each node v in V:
    incoming = { (u, w, s) | edge (u → v) exists }
    
    if incoming is empty:
      B^t[v] = B^0[v]          // prior
      continue
    
    // Weighted signed sum, normalized by degree
    raw = Σ_{(u,w,s) in incoming} w · s · B^{t-1}[u]
    deg = |incoming|
    
    // Tanh squashing to [-1, 1] with decay
    B_raw[v] = tanh(raw / deg) * α + B^0[v] * (1 - α)
    
    // Confidence: how much the neighborhood agrees
    agreement = 1 - |Σ_{(u,w,s)} w · s · B^{t-1}[u]| / Σ_{(u,w)} w
    C^t[v] = C^{t-1}[v] * 0.9 + agreement * 0.1
  
  // Check convergence
  Δ = max_v |B^t[v] - B^{t-1}[v]|
  if Δ < θ:
    break

Return B^t, C^t
```

### 1.4 SQL Implementation (single iteration)

```sql
-- Single propagation iteration in SQL
WITH incoming AS (
    SELECT 
        e.target_id AS node_id,
        SUM(e.weight * e.signed * ps.belief) AS raw_sum,
        COUNT(*) AS degree,
        SUM(e.weight) AS total_weight,
        SUM(e.weight * e.signed * ps.belief) / NULLIF(SUM(e.weight), 0) AS weighted_mean
    FROM graph_edges e
    JOIN graph_propagation_state ps ON ps.node_id = e.source_id
    WHERE ps.round = (SELECT MAX(round) FROM graph_propagation_state)
    GROUP BY e.target_id
),
new_beliefs AS (
    SELECT 
        i.node_id,
        TANH(i.weighted_mean) * 0.85 + COALESCE(ps.belief, 0.0) * 0.15 AS belief_new,
        1.0 - ABS(i.weighted_mean) AS agreement,
        ps.confidence * 0.9 + (1.0 - ABS(i.weighted_mean)) * 0.1 AS confidence_new
    FROM incoming i
    LEFT JOIN graph_propagation_state ps 
        ON ps.node_id = i.node_id 
        AND ps.round = (SELECT MAX(round) FROM graph_propagation_state)
)
INSERT INTO graph_propagation_state (node_id, belief, confidence, round)
SELECT 
    node_id, 
    belief_new, 
    confidence_new,
    (SELECT MAX(round) FROM graph_propagation_state) + 1
FROM new_beliefs;
```

### 1.5 Seed Strategy from Existing Data

Every `token_analyses` row with `confidence >= 0.8` from Vidyut engine becomes a SUPPORTS edge to its lemma. Ambiguous parses from different engines become CONTRADICTS edges between each other.

```python
# pseudocode for seeding
def seed_graph_from_analyses(db):
    # 1. Create graph nodes for all token_analyses
    for ta in db.query("SELECT * FROM token_analyses"):
        node_id = f"node:token_analysis:{ta.id}"
        db.execute("INSERT OR IGNORE INTO graph_nodes VALUES (?, 'token_analysis', ?, datetime('now'))",
                   (node_id, ta.id))
    
    # 2. For high-confidence parses, create SUPPORTS edges to lemma
    for ta in db.query("SELECT * FROM token_analyses WHERE confidence >= 0.8"):
        lemma_node = f"node:lemma:{ta.lemma_hash}"  # from lexical_senses
        db.execute("""INSERT OR IGNORE INTO graph_edges 
            (source_id, target_id, relation, weight, signed)
            VALUES (?, ?, 'SUPPORTS', ?, 1)""",
            (f"node:token_analysis:{ta.id}", lemma_node, ta.confidence))
    
    # 3. For conflicting parses of same token, create CONTRADICTS
    rows = db.query("""
        SELECT a.id AS aid, b.id AS bid, a.token_id 
        FROM token_analyses a 
        JOIN token_analyses b ON a.token_id = b.token_id AND a.id < b.id
        WHERE a.engine != b.engine AND a.analysis_type = b.analysis_type
    """)
    for r in rows:
        db.execute("""INSERT OR IGNORE INTO graph_edges 
            (source_id, target_id, relation, weight, signed)
            VALUES (?, ?, 'CONTRADICTS', 0.5, -1)""",
            (f"node:token_analysis:{r.aid}", f"node:token_analysis:{r.bid}"))
    
    # 4. Initialize propagation state with priors
    db.execute("""INSERT INTO graph_propagation_state (node_id, belief, confidence, round)
        SELECT id, 0.0, 0.5, 0 FROM graph_nodes""")
```

### 1.6 Manual Seed for Bhairavastava (9 verses)

For the structural gold corpus, manually create nodes and edges for the known compound splits:

```sql
-- Bhairavastava v1: karmadharaya vs tatpurusa test
-- Token "śivaśaktyoḥ" — expected karmadharaya (śiva + śakti, both equal)
-- Wrong parse: tatpurusa (śivasya śaktiḥ — genitive relation)

-- Manual nodes
INSERT INTO graph_nodes VALUES 
  ('node:compound_reading:bhairava_v1_kd', 'compound_reading', NULL, datetime('now')),
  ('node:compound_reading:bhairava_v1_tp', 'compound_reading', NULL, datetime('now'));

-- Edges from evidence
INSERT INTO graph_edges (source_id, target_id, relation, weight, signed, evidence_ref) VALUES
  ('node:compound_reading:bhairava_v1_kd', 'node:semantic_frame:bhairava_v1_śivaśakti', 'ALIGNS_WITH', 0.9, 1, 'manual_adjudication'),
  ('node:compound_reading:bhairava_v1_tp', 'node:semantic_frame:bhairava_v1_śivaśakti', 'CONTRADICTS', 0.7, -1, 'vidyut_ambiguous');

-- After propagation: karmadharaya should have belief > 0.6, tatpurusa < -0.3
```

---

## 2. Spandakārikā Ingestion

### 2.1 Source Format

GRETIL plaintext URL: `https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_vasugupta-spandakArikA-comm.txt`

Format analysis (expected): Devanagari verses + Kṣemarāja's commentary interspersed. Each verse is numbered. Commentary follows each verse or group of verses.

### 2.2 Ingestion Pipeline

```python
# src/sanskritree/corpus/spanda_ingestion.py

class SpandaIngestionPipeline:
    """Handle the peculiar structure: 52 verses + commentary interleaving."""
    
    COMMENTARY_INDICATORS = ["iti", "ityarthaḥ", "ityādi", "iti kṣemarājaḥ"]
    
    def parse_gretil_text(self, raw: str) -> list[dict]:
        """
        1. Strip GRETIL headers/footers (between --- lines)
        2. Split on verse markers like '॥ १ ॥' or '|| 1 ||'
        3. For each verse block:
           - Extract verse number
           - Separate verse text from commentary
           - Commentary: text following verse that contains COMMENTARY_INDICATORS
           - Or: use structural clue (commentary is prose, verse is metrical)
        
        Returns: list of {
            'verse_number': int,
            'verse_text': str (devanagari),
            'commentary_text': str | None,
            'commentary_author': 'kṣemarāja' | None
        }
        """
        
    def detect_verse_boundaries(self, lines: list[str]) -> list[tuple[int, int]]:
        """Find verse start/end line indices using śloka meter heuristics
        and known Spandakārikā structure."""
        
    def separate_commentary(self, block: str) -> tuple[str, str | None]:
        """
        Use multiple strategies:
        1. Structural: if block has two paragraphs, second is commentary
        2. Lexical: contains 'ityarthaḥ' or explanatory phrases
        3. Length: commentary is typically 3-10x longer than verse
        4. Prose detection: commentary lacks metrical regularity
        """
```

### 2.3 Commentary Storage Strategy

Two options — choose based on complexity:

**Option A (Recommended for G0): Single passage, tagged lines**
```sql
-- Extend passages table with commentary column
ALTER TABLE passages ADD COLUMN commentary_text TEXT;
ALTER TABLE passages ADD COLUMN commentary_source TEXT;  -- 'kṣemarāja'

-- Each verse = 1 passage with commentary_text populated
INSERT INTO passages (work_id, edition_id, passage_number, text, commentary_text, text_format)
VALUES (
    (SELECT id FROM works WHERE slug = 'spandakarika'),
    (SELECT id FROM editions WHERE slug = 'gretil'),
    1,
    'atha yaḥ ...',
    'Kṣemarāja's commentary text here...',
    'devanagari'
);
```

**Option B (Future G1+): Separate passage_with_commentary rows**
```sql
-- Each verse generates 2 passage rows:
-- passage_number = N   (verse only)
-- passage_number = -N  (commentary only, negative = structural marker)
```

### 2.4 Tokenization + Analysis

After ingestion, run the standard pipeline:
```bash
python -m sanskritree.cli analyze spandakarika --engine vidyut
python -m sanskritree.cli analyze spandakarika --engine heritage
```

This generates tokens + token_analyses for ~52 verses × ~15 tokens/verse = ~780 tokens, ~1,560 analyses.

### 2.5 Translation Seed

Use available public-domain translations (Kṣemarāja's commentary may have PD translations). If none are CC-BY, flag as private:

```python
translation_sources = {
    "jaideva_singh": "1995 SUNY Press — NOT CC, internal only",
    "mark_dyczkowski": "1992 — NOT CC, internal only" 
}
```

---

## 3. Testing Checkpoints

### 3.1 G0 Checkpoints

```
G0-C1: Database tables exist
  Test: SELECT COUNT(*) FROM graph_nodes > 0
  Test: SELECT COUNT(*) FROM graph_edges > 0  
  Test: SELECT COUNT(*) FROM graph_propagation_state > 0
  Criterion: All migrations run without error

G0-C2: Token analysis seeding works
  Test: Number of graph_nodes == number of token_analyses
  Test: Each distinct (token_id, engine) pair has exactly one node
  Criterion: 401,936 nodes created from existing data

G0-C3: Edge generation from conflicts
  Test: For token T with analyses from engines A and B:
    SELECT COUNT(*) FROM graph_edges 
    WHERE relation = 'CONTRADICTS' 
    AND source_id IN (node for A, node for B)
  Criterion: ≥1 CONTRADICTS edge per conflicting pair

G0-C4: Propagation converges
  Test: Run 20 iterations; max delta < 0.001
  Criterion: Convergence in ≤20 iterations

G0-C5: Bhairavastava ranking (MANDATORY GATE)
  Test: 
    -- Inject known karmadharaya split with weight 0.9
    -- Inject known tatpurusa split with weight 0.5  
    -- After propagation:
    SELECT belief FROM graph_propagation_state 
    WHERE node_id = 'node:compound_reading:bhairava_v1_kd'
    -- Must be > 0.5
    SELECT belief FROM graph_propagation_state 
    WHERE node_id = 'node:compound_reading:bhairava_v1_tp'
    -- Must be < -0.2
  Criterion: Correct ranking (karmadharaya > tatpurusa)

G0-C6: Graph query API works
  Test: GET /graph/node/:id returns node + beliefs + incoming edges
  Test: GET /graph/subgraph/:passage_id returns all nodes for a passage
  Criterion: Both endpoints return 200 with valid JSON
```

### 3.2 G1 Checkpoints

```
G1-C1: PyTorch Geometric Data object constructed
  Test: data.x.shape == (num_nodes, feature_dim)
  Test: data.edge_index.shape == (2, num_edges)
  Criterion: Feature dim = 16 (8 node type one-hot + 4 metadata + 4 embeddings)

G1-C2: Relational GCN converges
  Test: Train loss decreases monotonically for 50 epochs
  Test: Validation belief MAE < 0.1
  Criterion: Model can predict held-out edge beliefs

G1-C3: G1 > G0 on Bhairavastava
  Test: G1 belief for karmadharaya > G0 belief
  Criterion: Relational message passing improves over naive weighted sum
```

### 3.3 G2 Checkpoints

```
G2-C1: Restriction maps defined for 9 verses
  Test: len(restriction_maps) == 3 × 9 = 27 maps
  Criterion: Each map has valid domain/codomain

G2-C2: Consistency energy computed
  Test: consistency_energy(verse_1) is a finite float
  Test: consistency_energy(wrong_parse) > consistency_energy(correct_parse)
  Criterion: Energy functional orders hypotheses correctly

G2-C3: G2 > G1 on Bhairavastava
  Test: G2 belief separation (kd - tp) > G1 separation
  Criterion: Sheaf constraint tightens belief distribution
```

### 3.4 G3 Checkpoints

```
G3-C1: Human adjudication imported
  Test: SELECT COUNT(*) FROM review_events WHERE decision IS NOT NULL > 0
  Criterion: ≥50 adjudication events from blind translation review

G3-C2: Pathway reliability learned
  Test: evidence_sources.reliability updated after training
  Test: Vidyut reliability > Heritage reliability for morphology (or vice versa)
  Criterion: Reliability weights change from initial 0.5

G3-C3: Human agreement correlation
  Test: Graph belief for adjudicated items correlates with human decision
  Criterion: Spearman ρ > 0.7 on held-out adjudications
```

### 3.5 G4 Checkpoints

```
G4-C1: Graph-to-prompt format works
  Test: generate_rendering_prompt(passage_id) returns valid string
  Criterion: Prompt contains: source text, candidate readings with beliefs, constraints

G4-C2: LLM output aligns to graph
  Test: alignment_backlink_count(graph_node, llm_output) > 0
  Criterion: Each claim in output maps to ≥1 graph node

G4-C3: Constrained rendering > unconstrained
  Test: Blind review: constrained output has fewer errors than free translation
  Criterion: Error rate reduction ≥30%
```

---

## 4. Mitrasamgraha Evaluation Harness

### 4.1 Source Coverage Reporter

```python
# src/sanskritree/evaluation/coverage.py

class SourceCoverageReporter:
    """
    For each Sanskrit word in Mitrasamgraha, does the graph have 
    a corresponding lexical_sense node with evidence?
    
    Metrics:
      - Lemma coverage: unique lemmas in graph / unique lemmas in Mitrasamgraha
      - Sense coverage: sense disambiguations / total occurrences
      - Edge coverage: % of Mitrasamgraha pairs that have graph SUPPORTS edges
    """
    
    def lemma_coverage(self) -> dict:
        """Per-part-of-speech coverage stats."""
        return self.db.query("""
            SELECT 
                pos, 
                COUNT(DISTINCT ms.lemma) AS total,
                COUNT(DISTINCT ls.lemma) AS covered,
                ROUND(COUNT(DISTINCT ls.lemma) * 100.0 / COUNT(DISTINCT ms.lemma), 1) AS pct
            FROM mitrasamgraha.ms_entries ms
            LEFT JOIN lexical_senses ls ON ls.lemma = ms.lemma
            GROUP BY pos
        """)
    
    def coverage_gap_report(self, threshold: float = 0.3) -> list[dict]:
        """Lemmas below threshold coverage with Mitrasamgraha evidence."""
```

### 4.2 Multi-Dimensional Metric Stack

```python
# src/sanskritree/evaluation/metrics.py

from sacrebleu import sentence_chrf
from typing import Callable

class MetricStack:
    """
    Composite evaluation metric that returns a dict of scores.
    """
    
    def __init__(self, reference_pairs: list[tuple[str, str]]):
        """
        reference_pairs: list of (sanskrit, english) from Mitrasamgraha
        """
        self.references = reference_pairs
    
    def evaluate(self, hypothesis: str, source: str) -> dict:
        return {
            "chrf_plus_plus": self._chrf_plus_plus(hypothesis),
            "morph_coverage": self._morph_coverage(hypothesis, source),
            "term_preservation": self._term_preservation(hypothesis, source),
            "doctrinal_addition": self._detect_doctrinal_addition(hypothesis, source),
            "source_alignment": self._source_alignment_density(hypothesis, source),
        }
    
    def _chrf_plus_plus(self, hypothesis: str) -> float:
        """Character n-gram F-score with word n-grams."""
        return sentence_chrf(hypothesis, [self.reference_for(hypothesis)]).score
    
    def _morph_coverage(self, hypothesis: str, source: str) -> float:
        """
        What fraction of source morphemes have a corresponding 
        English token in the hypothesis?
        
        Uses token_analyses to decompose source into morphemes,
        then checks if each has a lexical_sense → translation span.
        """
        source_morphemes = self._decompose_morphemes(source)
        covered = sum(
            1 for m in source_morphemes 
            if self._lemma_in_hypothesis(m.lemma, hypothesis)
        )
        return covered / len(source_morphemes) if source_morphemes else 1.0
    
    def _term_preservation(self, hypothesis: str, source: str) -> float:
        """
        For technical terms identified in source (via semantic_frames),
        are they preserved or dropped in the translation?
        """
        terms = self._extract_technical_terms(source)
        preserved = sum(
            1 for t in terms 
            if self._term_in_hypothesis(t, hypothesis) 
            or self._acceptable_synonym(t, hypothesis)
        )
        return preserved / len(terms) if terms else 1.0
    
    def _detect_doctrinal_addition(self, hypothesis: str, source: str) -> float:
        """
        Score 0..1 where 1 = no doctrinal addition, 0 = pure doctrinal invention.
        
        Uses existing error taxonomy from Bhairavastava blind review.
        Checks for:
        - Added theological terms not in source (śakti, śiva, etc.)
        - Doctrinal gloss inserted as translation
        """
        doctrinal_terms = self._load_doctrinal_lexicon()
        source_terms = set(self._tokenize(source))
        hypothesis_terms = set(self._tokenize(hypothesis.lower()))
        
        additions = hypothesis_terms - doctrinal_terms  # non-doctrinal additions
        doctrinal_additions = hypothesis_terms & doctrinal_terms - source_terms
        
        if doctrinal_additions and len(additions.union(doctrinal_additions)) > 0:
            return 1.0 - (len(doctrinal_additions) / len(additions.union(doctrinal_additions)))
        return 1.0
    
    def _source_alignment_density(self, hypothesis: str, source: str) -> float:
        """
        What fraction of the hypothesis tokens are aligned back to 
        specific source tokens via translation_alignment table?
        """
        alignments = self.db.query("""
            SELECT COUNT(*) FROM translation_alignment ta
            JOIN tokens t ON t.id = ta.source_token_id
            WHERE t.text = ? AND ta.target_text IN ?
        """, (source, tuple(self._tokenize(hypothesis))))
        return alignments / len(self._tokenize(hypothesis))
```

### 4.3 Integration with Graph

```python
# src/sanskritree/evaluation/harness.py

from mitrasamgraha import MitrasamgrahaDataset
from metrics import MetricStack
from coverage import SourceCoverageReporter

class EvaluationHarness:
    """
    Runs the full Mitrasamgraha eval and reports to the graph.
    """
    
    def __init__(self, db, graph_propagator):
        self.db = db
        self.graph = graph_propagator
    
    def evaluate_all(self, split: str = "validation"):
        """
        For each entry in Mitrasamgraha:
        1. Check if graph has a semantic_frame for the source
        2. If yes, use graph belief to weight translation candidates
        3. Pick highest-belief candidate as hypothesis
        4. Compare to Mitrasamgraha reference
        5. Record results
        
        Returns: aggregate metrics dict
        """
        dataset = MitrasamgrahaDataset(split=split)
        metric_stack = MetricStack(dataset.references)
        
        results = []
        for source, reference in dataset:
            hypothesis = self._graph_weighted_translation(source)
            metrics = metric_stack.evaluate(hypothesis, source)
            results.append(metrics)
        
        return self._aggregate(results)
    
    def _graph_weighted_translation(self, source: str) -> str:
        """
        Query graph for the highest-belief translation candidate for source.
        Falls back to lexical lookup if graph has no candidate.
        
        Pseudocode:
        1. Tokenize source
        2. For each token, find token_analysis nodes
        3. For each analysis, follow SUPPORTS edges to lexical_sense
        4. For each sense, follow ALIGNS_WITH edges to translation_candidate
        5. Weight candidates by propagation belief + edge weight
        6. Return highest-weighted candidate chain
        """
```

### 4.4 Reporting

```bash
# CLI usage
python -m sanskritree.cli evaluate \
  --harness mitrasamgraha \
  --split validation \
  --output reports/eval_g0_$(date +%Y%m%d).json

# Example report output
{
  "timestamp": "2026-07-24T12:00:00Z",
  "phase": "G0",
  "chrf_plus_plus": { "mean": 68.2, "std": 12.4 },
  "morph_coverage": { "mean": 0.74, "std": 0.18 },
  "term_preservation": { "mean": 0.81, "std": 0.15 },
  "doctrinal_addition": { "mean": 0.92, "std": 0.08 },
  "source_alignment": { "mean": 0.67, "std": 0.21 },
  "coverage_gaps": ["lemma:ātman (0.12)", "lemma:yoga (0.23)"]
}
```

---

## 5. Sheaf Consistency Prototype (G2)

### 5.1 Theory

A sheaf on a graph assigns to each node a **stalk** (a vector space) and to each edge a **restriction map** (a linear transformation). A **global section** is an assignment to each node from its stalk that agrees across all restriction maps. The **consistency energy** measures how far a given assignment is from being a global section.

### 5.2 Stalks for Bhairavastava (9 verses)

Three relationship types with three stalk dimensions:

```python
# src/sanskritree/graph/sheaf.py

import torch
import torch.nn.functional as F

class BhairavastavaSheaf:
    """
    Sheaf for 9-verse structural gold corpus.
    
    Stalks:
      TokenAnalysis:  R⁴  [syntactic_role(2), confidence(1), engine_reliability(1)]
      CompoundReading: R³  [split_type(2), entity_count(1)]  
      SemanticFrame:  R⁶  [frame_type(3), arg_count(1), domain(2)]
      EnglishAlignment: R² [span_start(1), span_end(1)]
    
    Restriction maps:
      ρ_token→frame:  R⁴ → R⁶ (4×6 matrix)
      ρ_compound→entity: R³ → R² (3×2 matrix)
      ρ_frame→alignment: R⁶ → R² (6×2 matrix)
    """
    
    def __init__(self):
        # Manually defined restriction maps for 9 verses
        # These encode philological knowledge:
        #   - A nominative token (syntactic_role=[1,0]) restricts possible frames
        #   - A karmadharaya compound restricts entity count to 1 (same entity)
        #   - A locative frame restricts alignment to temporal/spatial spans
        
        # ρ_token→frame: syntactic_role → frame type
        # Nom(1,0) → Action frames: high weight to col 0
        # Acc(0,1) → Patient frames: high weight to col 1
        self.restriction_token_to_frame = torch.tensor([
            [0.9, 0.1, 0.1, 0.1, 0.1, 0.1],  # nominative → action
            [0.1, 0.9, 0.1, 0.1, 0.1, 0.1],  # accusative → patient
            [0.1, 0.1, 0.9, 0.1, 0.1, 0.1],  # confidence boost
            [0.1, 0.1, 0.1, 0.9, 0.1, 0.1],  # reliability boost
        ])  # 4×6
        
        # ρ_compound→entity: split_type → entity interpretation
        # karmadharaya(1,0) → single entity: [1, 0]
        # tatpurusa(0,1) → two entities: [0, 1]
        self.restriction_compound_to_entity = torch.tensor([
            [0.9, 0.1],   # karmadharaya → same entity
            [0.1, 0.9],   # tatpurusa → different entities
            [0.5, 0.5],   # entity_count bypass
        ])  # 3×2
        
        # ρ_frame→alignment: frame → english span
        # Frame type affects alignment structure
        self.restriction_frame_to_alignment = torch.tensor([
            [0.8, 0.2],   # action frame → tight alignment
            [0.2, 0.8],   # state frame → loose alignment  
            [0.5, 0.5],   # relation frame → medium
            [0.7, 0.3],   # arg_count >2 → wider spans
            [0.6, 0.4],   # tantric domain = looser
            [0.4, 0.6],   # mundane domain = tighter
        ])  # 6×2
```

### 5.3 Consistency Energy Formula

```python
def consistency_energy(self, assignments: dict[str, torch.Tensor]) -> float:
    """
    assignments: {node_id: stalk_vector}
    
    Energy = Σ_{(u,v) in E} ||ρ_{u→v}(x_u) - x_v||²
    
    Lower energy = more consistent assignment.
    """
    total = 0.0
    for u, v, rel in self.edges:
        x_u = assignments[u]
        x_v = assignments[v]
        
        if rel == 'ALIGNS_WITH' and self._is_token_analysis(u) and self._is_semantic_frame(v):
            rho = self.restriction_token_to_frame
        elif rel == 'ALIGNS_WITH' and self._is_compound_reading(u) and self._is_semantic_frame(v):
            rho = self.restriction_compound_to_entity  
        elif rel == 'ALIGNS_WITH' and self._is_semantic_frame(u) and self._is_english_alignment(v):
            rho = self.restriction_frame_to_alignment
        else:
            continue  # no restriction map, skip
        
        predicted = rho.T @ x_u  # or rho @ x_u depending on convention
        total += F.mse_loss(predicted, x_v)
    
    return total.item()


def verify_global_section(self, assignments, threshold=0.01) -> bool:
    """
    A true global section has energy ≈ 0.
    Tests if assignment satisfies all restriction constraints.
    """
    energy = self.consistency_energy(assignments)
    return energy < threshold
```

### 5.4 Manual Construction for 9 Verses

For each of the 9 Bhairavastava verses, manually annotate:

```python
# src/sanskritree/philology/bhairavastava_sheaf_data.py

VERSE_1_STALKS = {
    "node:token_analysis:śiva_1": torch.tensor([1.0, 0.0, 0.9, 0.8]),  # nom, high conf, vidyut
    "node:token_analysis:śakti_1": torch.tensor([1.0, 0.0, 0.8, 0.8]), # nom, high conf, vidyut
    "node:token_analysis:śivaśaktyoḥ_1": torch.tensor([0.0, 1.0, 0.7, 0.6]), # gen, med conf
    "node:compound_reading:śivaśaktyoḥ_kd": torch.tensor([1.0, 0.0, 1.0]), # kd, one entity
    "node:compound_reading:śivaśaktyoḥ_tp": torch.tensor([0.0, 1.0, 2.0]), # tp, two entities
    "node:semantic_frame:verse1_abheda": torch.tensor([1.0, 0.0, 0.0, 2.0, 1.0, 0.0]), # action, 2args, tantric
    "node:english_alignment:verse1": torch.tensor([0.0, 1.0]), # entire verse translated
}

# Sheaf consistency check:
# karmadharaya assignment:
#   ρ_compound_to_entity @ kd_stalk = [0.9, 0.1] ≈ frame entity_interpretation
#   Energy = small ✅
# tatpurusa assignment:
#   ρ_compound_to_entity @ tp_stalk = [0.1, 0.9] ≠ frame entity_interpretation  
#   Energy = large ❌
```

### 5.5 Integration with G0 Propagation

```python
def sheaf_weighted_propagation(self, assignments, alpha=0.5):
    """
    Augment G0 propagation with sheaf consistency.
    The sheaf energy becomes a regularization term.
    
    B_new[v] = α * G0_propagated_belief[v] + (1-α) * (1 - sheaf_energy(v))
    """
    base_belief = self.g0_propagate()
    energy = self.consistency_energy(assignments)
    
    corrected = {}
    for v in base_belief:
        node_energy = self._node_contribution_to_energy(v, assignments)
        corrected[v] = alpha * base_belief[v] + (1-alpha) * (1 - node_energy)
    
    return corrected
```

---

## 6. Lexical Sense Inventory

### 6.1 Schema

```sql
CREATE TABLE lexical_senses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma           TEXT NOT NULL,            -- from token_analyses.lemma
    pos             TEXT,                     -- noun, verb, etc
    sense_number    INTEGER NOT NULL DEFAULT 1, -- 1 = primary, 2 = secondary...
    gloss           TEXT NOT NULL,            -- English gloss
    domain          TEXT,                     -- 'tantric' | 'philosophical' | 'general'
    source          TEXT,                     -- 'mitrasamgraha' | 'mw' | 'vidyut' | 'manual'
    frequency       INTEGER DEFAULT 0,       -- occurrences in corpus
    graph_node_id   TEXT REFERENCES graph_nodes(id),
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(lemma, sense_number)
);

CREATE TABLE sense_evidence (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sense_id        INTEGER NOT NULL REFERENCES lexical_senses(id),
    source_entry    TEXT NOT NULL,            -- 'mitrasamgraha:12345' | 'token_analysis:6789'
    source_text     TEXT,                     -- the actual Sanskrit string
    translation     TEXT,                     -- the actual English translation
    confidence      REAL DEFAULT 0.5,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_senses_lemma ON lexical_senses(lemma);
CREATE INDEX idx_senses_domain ON lexical_senses(domain);
```

### 6.2 Population Process

```python
# src/sanskritree/semantics/sense_inventory.py

class LexicalSenseInventory:
    """
    Populate lexical_senses from:
    1. Mitrasamgraha parallel pairs (primary source)
    2. Vidyut dictionary output (fallback)
    3. Manual adjudication (for tantric terms)
    """
    
    def populate_from_mitrasamgraha(self):
        """
        For each lemma in Mitrasamgraha:
        1. Collect all English translations for that lemma
        2. Cluster translations by meaning (via embedding similarity)
        3. Each cluster = one sense
        4. Most frequent cluster = sense_number 1
        """
        lemmas = self.db.query("""
            SELECT DISTINCT ms.sanskrit_word, ms.english_translation, ms.lemma
            FROM mitrasamgraha_entries ms
            WHERE ms.lemma IS NOT NULL
        """)
        
        from collections import defaultdict
        lemma_translations = defaultdict(list)
        for row in lemmas:
            lemma_translations[row.lemma].append(row.english_translation)
        
        for lemma, translations in lemma_translations.items():
            clusters = self._cluster_by_similarity(translations)
            for i, cluster in enumerate(clusters):
                gloss = cluster.most_representative()
                self.db.execute("""
                    INSERT OR IGNORE INTO lexical_senses 
                    (lemma, pos, sense_number, gloss, domain, source, frequency)
                    VALUES (?, ?, ?, ?, 'general', 'mitrasamgraha', ?)
                """, (lemma, self._guess_pos(lemma), i+1, gloss, len(cluster.members)))
    
    def _cluster_by_similarity(self, translations: list[str]) -> list[Cluster]:
        """Use sentence embeddings to cluster synonymous translations.
        
        1. Encode all translations with sentence-transformer
        2. Agglomerative clustering with threshold 0.7
        3. Return clusters with representative member
        """
    
    def populate_tantric_terms(self, manual_entries: list[dict]):
        """
        For tantric terms (śakti, śiva, bhairava, etc.):
        Manually define multiple senses with domain = 'tantric'
        
        Example:
        śakti:
          sense 1: 'power, energy' (general)
          sense 2: 'the Goddess, active principle of the divine' (tantric)
          sense 3: 'capability, faculty' (philosophical)
        """
        for entry in manual_entries:
            self.db.execute("""
                INSERT INTO lexical_senses 
                (lemma, pos, sense_number, gloss, domain, source)
                VALUES (?, ?, ?, ?, 'tantric', 'manual')
            """, (entry['lemma'], entry['pos'], entry['sense_number'], entry['gloss']))
```

### 6.3 Linking to Token Analyses

```python
def link_analyses_to_senses(self):
    """
    For each token_analysis row with a lemma:
    If the lemma has senses, create a SUPPORTS edge 
    from token_analysis → lexical_sense for the most likely sense.
    
    Sense disambiguation heuristic:
    - Use domain match: tantric text → prefer tantric sense
    - Use frequency: if no domain info, pick highest-frequency sense
    - Consider neighboring tokens for context
    """
    self.db.execute("""
        INSERT INTO graph_edges (source_id, target_id, relation, weight, signed)
        SELECT 
            'node:token_analysis:' || ta.id,
            'node:lexical_sense:' || ls.id,
            'SUPPORTS',
            CASE 
                WHEN ls.domain = 'tantric' AND w.is_tantric = 1 THEN 0.9
                ELSE 0.7
            END,
            1
        FROM token_analyses ta
        JOIN tokens t ON t.id = ta.token_id
        JOIN works w ON w.id = t.work_id
        JOIN lexical_senses ls ON ls.lemma = ta.lemma
        WHERE ls.sense_number = (
            -- Prefer tantric sense for tantric works
            SELECT MIN(sense_number) FROM lexical_senses ls2
            WHERE ls2.lemma = ta.lemma
            ORDER BY CASE WHEN ls2.domain = 'tantric' AND w.is_tantric = 1 THEN 0 ELSE 1 END,
                     ls2.frequency DESC
            LIMIT 1
        )
    """)
```

### 6.4 Validation Gate

```python
def validate_sense_inventory(self) -> dict:
    """Check health of sense inventory."""
    stats = {
        "total_lemmas": self.db.query("SELECT COUNT(DISTINCT lemma) FROM lexical_senses")[0][0],
        "lemmas_with_multiple_senses": self.db.query("""
            SELECT COUNT(*) FROM (
                SELECT lemma FROM lexical_senses GROUP BY lemma HAVING COUNT(*) > 1
            )
        """),
        "unlinked_token_analyses": self.db.query("""
            SELECT COUNT(*) FROM token_analyses ta
            WHERE NOT EXISTS (
                SELECT 1 FROM graph_edges e
                WHERE e.source_id = 'node:token_analysis:' || ta.id
                AND e.relation = 'SUPPORTS'
                AND e.target_id LIKE 'node:lexical_sense:%'
            )
        """),
    }
    return stats
```

---

## 7. Lean Layer B and C

### 7.1 Layer B — Frame Consistency Checking

Frame = ritual action structure with typed participants.

```lean
-- lean/Sanskritree/Frame.lean
namespace Sanskritree.Frame

/--
  A ritual-action frame has:
  - agent: the performer (typically śiva or sādhaka)
  - instrument: the means (mantra, mudra, etc.)
  - object: the recipient (devatā, śiṣya)
  - procedure: sequence (dhyāna → pūjā → homa)
  - result: phalaśruti
-/
structure RitualFrame where
  agent : EntityRef
  instrument : EntityRef
  object : EntityRef
  procedure : List ActionStep
  result : Expression

inductive ActionType where
  | meditation    -- dhyāna
  | worship       -- pūjā, arcanā  
  | offering      -- homa, bali
  | recitation    -- japa, pāṭha
  | instruction   -- upadeśa

structure ActionStep where
  sequence : Nat
  action : ActionType
  actor : EntityRef
  target : EntityRef
  instrument : Option EntityRef

/--
  Frame consistency theorem:
  If a token is analyzed as accusative, and its governing verb 
  is in a ritual-action frame, then the accusative must be the 
  object of that frame.
-/
theorem frame_case_consistency 
  (frame : RitualFrame) 
  (tok : TokenRef) 
  (hCase : tok.analysis.case = .accusative)
  (hGov : tok.governedBy = some frame.agent.verbToken)
  : tok.semanticRole = frame.object := by
  -- The case agreement forces accusative = object in ritual frames
  match frame.action with
  | .worship => 
    -- In pūjā, the object is the devatā being worshipped
    -- Accusative marker on the devatā name confirms this
    have hDevatā : tok = frame.object := by
      -- Uses the philological rule: ritual worship always has accusative object
      apply ritual_accusative_rule tok frame.object hCase
    exact hDevatā
  | _ => 
    -- Default: case role assignment from frame
    apply default_role_assignment tok frame hCase

/--
  Procedure ordering theorem:
  In a ritual procedure, offerings (homa) must follow 
  worship (pūjā), not precede it.
-/
theorem procedure_ordering 
  (steps : List ActionStep) 
  (hWorship : steps.contains (λ s => s.action = .worship))
  (hOffering : steps.contains (λ s => s.action = .offering))
  : (steps.find (λ s => s.action = .worship)).map (·.sequence) < 
    (steps.find (λ s => s.action = .offering)).map (·.sequence) := by
  -- Convention: Śaiva ritual manuals always order pūjā before homa
  apply ritual_ordering_convention steps hWorship hOffering

end Sanskritree.Frame
```

### 7.2 Layer C — Philosophical Proposition Formalization

```lean
-- lean/Sanskritree/Philosophy.lean
namespace Sanskritree.Philosophy

/--
  A philosophical proposition in the Spandakārikā tradition.

  Examples:
  - "śiva is both transcendent and immanent" (viśvottīrṇa + viśvamaya)
  - "the universe is a manifestation of śiva's spanda (vibration)"
  - "liberation (mokṣa) is recognition (pratyabhijñā) of one's true nature"
-/
structure Proposition where
  subject : Term
  predicate : Predicate
  modality : Modality    -- necessary, possible, actual
  school : SchoolTradition

inductive Modality where
  | necessary    -- nitya, avaśyaṃbhāvī
  | actual       -- vartamāna, vyavahārika
  | possible     -- aikāntika, sambhava

inductive Relation between
  | identity     -- "X is Y" (tādātmya)
  | causation    -- "X causes Y" (satkārya, asatkārya)
  | inherence    -- "X inheres in Y" (samavāya)
  | qualification -- "X qualifies Y" (viśeṣaṇa-viśeṣya)

structure PropositionRelation where
  premise : Proposition
  conclusion : Proposition
  relation : Relation
  justification : String   -- textual reference

/--
  Non-contradiction theorem:
  No school can simultaneously assert and deny a proposition 
  in the same modality.
-/
theorem non_contradiction 
  (p : Proposition) 
  (hAssert : Asserted p) 
  (hDeny : Denied p)
  : False := by
  apply school_consistency p hAssert hDeny

/--
  Pratyabhijñā theorem (Recognition):
  If the subject is "jīva" (individual self), and the predicate 
  is "śiva" (ultimate reality), and the modality is "identity",
  then this is the pratyabhijñā position.
-/
theorem pratyabhijna_identification
  (p : Proposition)
  (hSubject : p.subject = "jīva")
  (hPredicate : p.predicate = "śiva")  
  (hModality : p.modality = .identity)
  : p.school = .pratyabhijna := by
  apply identify_pratyabhijna_claim p hSubject hPredicate hModality

/--
  Spanda theorem (vibration):
  If an action is predicated of śiva, and the modality is "necessary",
  then śiva's nature as spanda (self-aware vibration) is entailed.
-/
theorem spanda_entailment
  (action : Predicate)
  (hSubject : action.subject = "śiva")
  (hNecessary : action.modality = .necessary)
  : SpandaNature action := by
  -- Spanda = cit (consciousness) + vimarśa (reflexive awareness) + spanda (vibration)
  -- All necessary actions of śiva entail spanda
  apply derive_spanda_from_necessary_action action hSubject

end Sanskritree.Philosophy
```

### 7.3 Layer B+C Integration with Graph

```lean
-- Connecting Lean theorems to graph beliefs
namespace Sanskritree.Decision

/--
  When a frame consistency check fails, the graph belief on 
  the offending analysis should be downgraded.
  
  The compiler generates a Lean theorem whose proof either 
  succeeds (consistent) or fails (inconsistent). Failure is 
  reported to the graph as a CONTRADICTS edge.
-/
theorem frame_consistency_affects_belief
  (frameAnalysis : TokenAnalysis)
  (hFrameCheck : Lean.Except.ok (checkRitualFrame frameAnalysis))
  : graphBelief frameAnalysis.node ≥ 0.5 := by
  -- A successfully verified frame gives belief floor of 0.5
  apply belief_floor_from_verification frameAnalysis hFrameCheck

theorem frame_inconsistency_downgrades
  (frameAnalysis : TokenAnalysis)
  (hFrameCheck : Lean.Except.error (checkRitualFrame frameAnalysis))
  : graphBelief frameAnalysis.node ≤ 0.2 := by
  -- A failed frame check caps belief at 0.2
  apply belief_ceiling_from_failure frameAnalysis hFrameCheck

end Sanskritree.Decision
```

---

## 8. Constrained LLM Rendering (G4)

### 8.1 Graph-to-Prompt Format

```python
# src/sanskritree/rendering/prompt_builder.py

class ConstrainedRenderingPrompt:
    """
    Builds a prompt that constrains the LLM to graph-supported readings.
    
    The prompt structure:
    1. System instruction: "You are a constrained translator..."
    2. Source text with markup
    3. Graph readings with beliefs
    4. Hard constraints (from Lean)
    5. Soft preferences (from graph)
    6. Output format specification
    """
    
    def build(self, passage_id: int) -> str:
        passage = self._get_passage(passage_id)
        readings = self._get_graph_readings(passage_id)
        constraints = self._get_lean_constraints(passage_id)
        
        return f"""
SYSTEM: You are a constrained Sanskrit-to-English translator for Tantric texts.
You must follow the graph-supported readings below. Do not introduce 
interpretations not backed by graph evidence.

SOURCE TEXT:
{passage.text}

GRAPH-SUPPORTED READINGS (with belief scores):

{self._format_readings(readings)}

For each token, three candidates are provided:
  CONSTRIAL (literal): grammatical default
  PHILOLOGICAL (natural): contextually fluent
  INTERPRETIVE (tradition-specific): sectarian reading

HARD CONSTRAINTS (verified by Lean formal proof):
{self._format_constraints(constraints)}

INSTRUCTIONS:
1. For each token, select the reading with highest BELIEF.
2. Never select a reading marked DISALLOWED.
3. If two readings have similar belief, prefer PHILOLOGICAL > CONSTRIAL > INTERPRETIVE
4. The output MUST maintain the ordering: each English span corresponds 
   to exactly one source token or compound.
5. Mark each English span with its source node ID in the format [NODE:...].

OUTPUT FORMAT:
```json
{{
  "translation": "English translation with [NODE:xxx] markers",
  "alignment": [
    {{"source_node": "node:token_analysis:uuid", "span": "English word(s)"}},
    ...
  ],
  "confidence": 0.85,
  "disclaimer": "Any interpretive additions beyond graph evidence"
}}
```
"""
    
    def _format_readings(self, readings: list) -> str:
        """Format readings as a structured table for the prompt."""
        lines = []
        for r in readings:
            status = "✓" if r.belief > 0.3 else "✗" if r.belief < -0.2 else "?"
            lines.append(
                f"  {r.token_text}: [{r.reading_type}]\n"
                f"    Reading: \"{r.gloss}\" (lemma: {r.lemma})\n"
                f"    Belief: {r.belief:.2f}, Confidence: {r.confidence:.2f}\n"
                f"    Status: {status}"
            )
        return "\n".join(lines)
    
    def _format_constraints(self, constraints: list) -> str:
        """Format Lean-verified constraints."""
        if not constraints:
            return "  (none)"
        return "\n".join(f"  - {c.description} (from {c.lean_theorem})" for c in constraints)
```

### 8.2 Output Alignment

```python
class AlignmentPostprocessor:
    """
    After LLM returns JSON, validate alignment:
    1. Every [NODE:xxx] marker corresponds to an existing graph node
    2. The alignment list covers all source tokens (no gaps)
    3. No token is assigned multiple incompatible readings
    """
    
    def validate_alignment(self, llm_output: dict, passage_id: int) -> dict:
        tokens = self._get_tokens(passage_id)
        errors = []
        
        # Check 1: All node references exist
        for marker in self._extract_markers(llm_output['translation']):
            node_id = marker.replace('[NODE:', '').replace(']', '')
            if not self._node_exists(node_id):
                errors.append(f"Invalid node: {node_id}")
        
        # Check 2: Coverage
        aligned_tokens = {a['source_node'] for a in llm_output['alignment']}
        missing = set(t.node_id for t in tokens) - aligned_tokens
        if missing:
            errors.append(f"Missing tokens: {missing}")
        
        # Check 3: No conflicts
        llm_output['validation'] = {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'coverage': len(aligned_tokens) / len(tokens),
        }
        return llm_output
```

### 8.3 API Contract

```json
// POST /api/v1/render
// Request:
{
  "passage_id": 1234,
  "mode": "constrained",
  "options": {
    "temperature": 0.3,
    "max_tokens": 2000
  }
}

// Response:
{
  "translation": "Śiva [NODE:ta:abc] and Śakti [NODE:ta:def] are one [NODE:fr:ghi]...",
  "alignment": [
    {"source_node": "node:token_analysis:abc", "span": "Śiva"},
    {"source_node": "node:token_analysis:def", "span": "Śakti"},
    {"source_node": "node:semantic_frame:ghi", "span": "are one"}
  ],
  "graph_belief": 0.82,
  "lean_verified": true,
  "candidates_used": {
    "construal": 0.7,
    "philological": 0.8,
    "interpretive": 0.3
  },
  "validation": {
    "is_valid": true,
    "coverage": 1.0,
    "errors": []
  }
}
```

### 8.4 Fallback Strategy

```python
def render_with_fallback(passage_id: int, llm_client) -> dict:
    """
    Three-tier fallback:
    1. Try constrained rendering (graph-guided)
    2. If graph has low belief (<0.3), fall back to philogical-only
    3. If LLM unavailable, return template with highest-belief spans
    """
    graph_belief = get_graph_belief(passage_id)
    
    if graph_belief >= 0.5:
        return constrained_render(passage_id, llm_client)
    elif graph_belief >= 0.3:
        return philological_render(passage_id, llm_client)  # relaxed constraints
    else:
        return template_render(passage_id)  # no LLM, just concat highest-belief glosses
```

---

## 9. Risk Assessment

| # | Risk | Phase | Likelihood | Impact | Mitigation |
|---|------|-------|------------|--------|------------|
| R1 | SQLite can't handle 400K+ hybrid graph queries | G0 | Medium | High | Index all join columns; batch propagation in chunks of 10K; add WAL mode; pre-aggregate degree counts in trigger-maintained table |
| R2 | Propagation doesn't converge | G0 | Low | Medium | Add damping factor α adjustable per iteration; detect oscillation (sign flip >3 rounds) and force reset to prior; cap iterations at 20 |
| R3 | G1 model (PyTorch Geometric) exceeds 11GB disk | G1 | Medium | High | Train on CPU with reduced hidden dim (64 → 32); save checkpoints to temp; upgrade container before training |
| R4 | Mitrasamgraha evaluation shows G0 performs worse than random baseline | G0 | Medium | High | Fix: inject manual SUPPORTS edges from Bhairavastava adjudication; verify edge weights are positive; add baseline random edge test |
| R5 | Spandakārikā commentary separation fails | Ingest | Low | Medium | Manual pass for 52 verses is feasible (2 hours); commentary may lack consistent structural markers, but prose detection works for Sanskrit |
| R6 | Lean compilation times blow up | B/C | Medium | Medium | Keep each theorem small; use `#eval` for timing; split files; avoid heavy `simp` on large inductive types |
| R7 | LLM ignores graph constraints | G4 | High | Medium | Post-processing validation rejects outputs violating constraints; use temperature=0.2; retry with increasingly strict prompts on failure; maintain alignment blacklist |
| R8 | Sheaf energy is always high (no global section) | G2 | Medium | High | Sheaf is descriptive, not prescriptive — high energy means "hypothesis is unlikely." Accept that some verses have no consistent interpretation; report energy as uncertainty |
| R9 | Dyczkowski copyright contamination in evaluation | All | Low | Critical | Never include Dyczkowski in training/eval data; Mitrasamgraha-only public eval; use Dyczkowski only for internal reference; add `private=true` flag to data sources |
| R10 | Vidyut engine unavailable or API changes | G0 | Low | Medium | Cache Vidyut output in token_analyses (already done — 401K rows). Freeze engine version in requirements.txt. |

---

## 10. Timeline Estimate

| Phase | Tasks | Est. Hours | Calendar (solo) | Key Deliverable |
|-------|-------|------------|-----------------|-----------------|
| **G0 Setup** | DB schema, migration, seeding from token_analyses | 16h | 2 days | graph_nodes + graph_edges populated |
| **G0 Propagation** | Algorithm, SQL, convergence testing | 12h | 1.5 days | Propagation converges on test data |
| **G0 Validation** | Bhairavastava test, belief ranking check | 8h | 1 day | G0-C5 passes |
| **G0 Evaluation** | Mitrasamgraha harness, metrics, coverage | 16h | 2 days | Metric stack works on validation split |
| **Spanda Ingestion** | Parser, commentary separation, tokenization | 8h | 1 day | 52 verses ingested |
| **Sense Inventory** | Extract lemmas, cluster from Mitrasamgraha, manual tantric senses | 16h | 2 days | 5,465 lemmas with ≥1 sense each |
| **G1 Setup** | PyTorch Geometric data builder, RGCN model | 20h | 2.5 days | G1 model trains |
| **G1 Tuning** | Hyperparameter search, eval on Mitrasamgraha | 12h | 1.5 days | G1 > G0 on metrics |
| **G2 Sheaf** | Restriction maps, energy formula, 9-verse annotation | 24h | 3 days | Sheaf energy separates kd/tp |
| **G2 Integration** | Sheaf-weighted propagation, comparison vs G1 | 8h | 1 day | G2 > G1 on Bhairavastava |
| **Lean Layer B** | Frame types, ritual action theorems | 16h | 2 days | Lean verifies Bhairavastava frames |
| **Lean Layer C** | Proposition types, philosophical theorems | 16h | 2 days | Lean verifies Spanda proposition |
| **G3 Human Eval** | Import review_events, learn pathway reliability | 16h | 2 days | Evidence source weights diverge |
| **G4 Rendering** | Prompt builder, alignment validator, API | 16h | 2 days | Constrained > unconstrained rendering |
| **G4 Integration** | End-to-end pipeline: graph → Lean → LLM → validation | 12h | 1.5 days | E2E demo on 9 verses |
| **Documentation** | API docs, graph schema docs, README | 8h | 1 day | Docs complete |

### Total: 224 hours (~28 days full-time, ~8 weeks part-time)

### Critical path:
```
G0 Setup (16h) → G0 Propagation (12h) → G0 Validation (8h) → G1 Setup (20h) → G1 Tuning (12h) → G2 Sheaf (24h) → G2 Integration (8h) → G4 (44h)
                                                                                         ↑
Spanda Ingest (8h) ─────────────────────────────────────────────────────────────────────┘
Sense Inventory (16h) ──────────────────────────────────────────────────────────────────┘
Lean B+C (32h) ─────────────────────────────────────────────────────────────────────────┘
```

### Parallelizable:
- Spanda ingestion + Sense inventory can run alongside G0-G1
- Lean Layer B+C can run after G0 (theorems depend on graph API, not G1/G2)
- G3 Human eval can start as soon as G0 has belief predictions for adjudication
