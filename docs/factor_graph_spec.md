# Factor Graph Specification

## What we're building

An energy-based factor graph over the existing V2 database. Each passage produces a set of variables (choices to make) and factors (compatibility constraints between choices). Inference selects the lowest-energy consistent interpretation.

This is the Krishna et al. (2020) arc-factored model, extended upward from morphosyntax into compound semantics, lexical senses, semantic frames, and translation alignment.

---

## 1. Variable types

Each variable represents a choice point in the interpretation of a passage.

| Variable | Domain | Source |
|----------|--------|--------|
| `S_i` | Segmentation hypotheses for span i | Vidyut chedaka / Heritage |
| `M_i` | Morphological analyses of token i | `token_analyses` rows |
| `C_i` | Compound parses of compound span i | Vidyut + manual |
| `L_i` | Lexical senses of lemma i | `lexical_senses` table |
| `D_ij` | Dependency relation between token i and j | Parse candidates |
| `F` | Semantic frame for the passage | Frame type enum |
| `T_j` | Translation alignment for English span j | Alignment candidates |
| `R` | Discourse mode / register | Mode enum |

### Variable encoding

Each variable choice is a hypothesis node in the DB:

```sql
-- Existing table, currently empty
INSERT INTO analysis_hypothesis (hypothesis_id, passage_reading_id, hypothesis_type, engine, payload_json, confidence, status)
VALUES (?, ?, 'morphology', 'vidyut', '{ "lemma": "vand", "vibhakti": null, "lakara": "lat", "purusha": "uttama" }', 0.95, 'proposed')
```

---

## 2. Factor types

Each factor scores the compatibility of a set of variable assignments.

### 2a. Surface factor `φ_surface(S)`

Does this segmentation cover the source string without overlap?

```python
def surface_factor(segmentation):
    spans = sorted(segmentation.values(), key=lambda s: s.start)
    for i in range(len(spans) - 1):
        if spans[i].end != spans[i+1].start:
            return INF  # gap or overlap
    if spans[0].start != 0 or spans[-1].end != source_length:
        return INF
    return 0.0  # valid
```

**Hard constraint:** INF energy if segments don't tile the source exactly.

### 2b. Morphology factor `φ_morph(S, M)`

Does this morphological analysis correspond to a valid segmentation?

```python
def morphology_factor(segmentation, morphology):
    # Each token's morphology must be valid for its surface form
    for token, morph in zip(segmentation.tokens, morphology):
        if not vidyut.valid_analysis(token.surface, morph.lemma, morph.features):
            return 5.0  # penalty, not INF (Vidyut may have gaps)
    return -sum(m.confidence for m in morphology) / len(morphology)
```

**Score:** Negative log confidence of the Vidyut analysis. Lower energy = higher confidence.

### 2c. Agreement factor `φ_agreement(M_i, M_j)`

Do two co-occurring tokens agree in case, number, gender?

```python
def agreement_factor(m1, m2, relation):
    if relation == "adjective_noun":
        if m1.vibhakti != m2.vibhakti: return 3.0
        if m1.vacana != m2.vacana: return 2.0
        if m1.linga != m2.linga and m1.linga and m2.linga: return 2.0
        return 0.0
    if relation == "subject_verb":
        if m1.vacana != m2.vacana: return 3.0
        if m1.purusha != m2.purusha: return 2.0
        return 0.0
    return 0.0
```

**Three relations implemented:** `adjective_noun`, `subject_verb`, `apposition`.

### 2d. Compound factor `φ_compound(C, M, context)`

Is this compound parse compatible with the morphology of its members?

```python
def compound_factor(compound_parse, member_morphologies, context):
    energy = 0.0
    # A karmadharaya requires same case for both members
    if compound_parse.relation == "karmadharaya":
        if member_morphologies[0].vibhakti != member_morphologies[1].vibhakti:
            energy += 2.0
    # A tatpurusa requires genitive or stem form for first member
    if compound_parse.relation == "tatpurusa":
        if member_morphologies[0].vibhakti not in (None, "genitive", "stem"):
            energy += 2.0
    # Add context prior: karmadharaya is ~3x more common in epithets
    if compound_parse.relation == "karmadharaya":
        energy -= 0.5
    return energy
```

### 2e. Sense factor `φ_sense(L, tradition, context)`

Is this lexical sense appropriate for the tradition and context?

```python
def sense_factor(lemma, sense, tradition, passage_terms):
    energy = 0.0
    # Sense has attested support in this tradition
    if tradition in sense.attested_traditions:
        energy -= 0.3
    # Sense has commentary evidence
    if sense.commentary_evidence:
        energy -= 1.0
    # Domain mismatch penalty
    if sense.domain == "ordinary" and tradition == "trika":
        energy += 1.0  # prefer technical sense in Tantric text
    return energy
```

### 2f. Frame factor `φ_frame(F, D, L)`

Is this semantic frame compatible with the dependency structure and lexical senses?

```python
def frame_factor(frame, dependencies, lexical_senses):
    energy = 0.0
    # A DevotionalAct frame requires a verb of praise/worship
    if frame.type == "DevotionalAct":
        has_praise_verb = any(s.lemma == "vand" or s.lemma == "stu" for s in lexical_senses)
        if not has_praise_verb:
            energy += 5.0
    # An IdentityClaim requires a copula or equational syntax
    if frame.type == "IdentityClaim":
        has_equational = any(d.rel == "copula" for d in dependencies)
        if not has_equational:
            energy += 3.0
    return energy
```

### 2g. Translation factor `φ_translation(T, F, L)`

Does this translation span align with the semantic frame and lexical choices?

```python
def translation_factor(alignment, frame, senses):
    energy = 0.0
    # Every semantically required role should have a translation span
    for role in frame.required_roles:
        if role not in [a.frame_role for a in alignment]:
            energy += 2.0  # omission penalty
    # Unsupported additions increase energy
    for span in alignment:
        if span.relation == "ADDS_FROM_CONTEXT" and not span.context_evidence:
            energy += 3.0  # DOCTRINAL_ADDITION
    return energy
```

---

## 3. Total energy function

```
E(y) =  α·Σ φ_surface(S_i)
      + β·Σ φ_morph(S_i, M_i)
      + γ·Σ φ_agreement(M_i, M_j, rel)
      + δ·Σ φ_compound(C_i, M_i, ctx)
      + ε·Σ φ_sense(L_i, tradition, ctx)
      + ζ·φ_frame(F, D, L)
      + η·Σ φ_translation(T_j, F, L)
```

Where α, β, γ, δ, ε, ζ, η are hyperparameters (start with all 1.0, tune later).

**Valid interpretations only:** Any configuration that violates a hard constraint receives E(y) = +∞ and is pruned before search.

---

## 4. Inference algorithm

### 4a. Search space construction

For each passage:

```python
def build_search_space(passage_id):
    # 1. Get all token_analyses from DB
    analyses = db.query("""
        SELECT t.token_index, t.surface, ta.lemma, ta.features_json, ta.confidence
        FROM tokens t
        JOIN token_analyses ta ON ta.token_id = t.token_id
        WHERE t.reading_id = ?
        ORDER BY t.token_index
    """, reading_id)

    # 2. Group by token index → each token is a variable with multiple candidates
    variables = defaultdict(list)
    for analysis in analyses:
        variables[analysis.token_index].append(AnalysisCandidate(
            lemma=analysis.lemma,
            features=json.loads(analysis.features_json),
            confidence=analysis.confidence,
            source="vidyut"
        ))

    # 3. Add compound candidates where words could merge
    compounds = generate_compound_candidates(variables)
    variables["compound"] = compounds

    # 4. Add lexical sense candidates from sense inventory
    for token_idx, candidates in variables.items():
        for c in candidates:
            c.senses = lexical_senses_for_lemma(c.lemma, tradition)

    # 5. Add frame candidates
    variables["frame"] = GENERIC_FRAMES  # DevotionalAct, IdentityClaim, etc.

    return FactorGraph(variables)
```

### 4b. Minimum energy search

For Bhairavastava-scale passages (5-15 tokens, 2-5 candidates each):

```python
def infer(graph: FactorGraph) -> Assignment:
    # Beam search through variable assignments
    beam = [Assignment()]  # start with empty
    for var_name, candidates in graph.variables.items():
        new_beam = []
        for assignment in beam:
            for candidate in candidates:
                new_assignment = assignment + {var_name: candidate}
                energy = graph.total_energy(new_assignment)
                new_beam.append((new_assignment, energy))
        # Keep top K
        new_beam.sort(key=lambda x: x[1])
        beam = [a for a, e in new_beam[:BEAM_WIDTH]]

    best = beam[0]
    return best
```

**For larger search spaces** (Heritage can produce 60K candidates), switch to:
- **ILP** using `pulp` or `ortools` — exact for linear energies with hard constraints
- **Belief propagation** — approximate for loopy graphs
- **Chu-Liu/Edmonds** — exact for dependency parsing subproblems

### 4c. Bhairavastava-specific beam width

```
Beam width K = 50
Variables per verse = 5-15 (tokens + compound + frame)
Candidates per variable = 2-5 (morph alternatives + sense choices)
Total search space: 2^5 to 5^15 ≈ 32 to 30 billion (naive)
With beam search at K=50: ~50 × 15 × 5 = 3,750 evaluations
Runtime: milliseconds
```

---

## 5. Integration with existing DB

### New module: `src/sanskritree/inference/factor_graph.py`

```python
class FactorGraph:
    def __init__(self, passage_reading_id: str):
        self.reading_id = passage_reading_id
        self.variables: dict[str, list[VariableChoice]] = {}
        self.factors: list[Factor] = []
    
    def add_variable(self, name: str, choices: list[VariableChoice]):
        self.variables[name] = choices
    
    def add_factor(self, factor: Factor):
        self.factors.append(factor)
    
    def total_energy(self, assignment: Assignment) -> float:
        return sum(f.energy(assignment) for f in self.factors)

class Assignment:
    def __init__(self, choices: dict = None):
        self.choices = choices or {}
    
    def get(self, var_name: str) -> VariableChoice:
        return self.choices.get(var_name)
```

### New module: `src/sanskritree/inference/exact.py`

```python
def beam_search(graph: FactorGraph, beam_width: int = 50) -> Assignment:
    """Beam search: keep top K partial assignments at each step."""
    ...

def ilp_solve(graph: FactorGraph) -> Assignment:
    """ILP formulation for exact inference on linear energies."""
    ...
```

### New module: `src/sanskritree/graph/builder.py`

```python
def build_from_passage(passage_id: str) -> FactorGraph:
    """Build factor graph from existing DB data."""
    g = FactorGraph()
    g.add_morphology_variables(passage_id)   # from token_analyses
    g.add_compound_variables(passage_id)     # from compound candidates
    g.add_sense_variables(passage_id)        # from lexical_senses
    g.add_frame_variables(passage_id)        # from semantic frame enum
    g.add_surface_factor()                   # hard constraint
    g.add_morphology_factors()               # per analysis
    g.add_agreement_factors()                # pairs
    g.add_compound_factors()                 # per compound
    g.add_sense_factors()                    # per lemma
    g.add_frame_factor()                     # per passage
    return g
```

### Query pattern to populate `analysis_hypothesis`:

```python
def seed_hypotheses(passage_id: str):
    """Populate analysis_hypothesis from existing token_analyses."""
    db.execute("""
        INSERT INTO analysis_hypothesis (hypothesis_id, passage_reading_id, 
            hypothesis_type, engine, payload_json, confidence, status)
        SELECT 
            'hyp_' || ta.analysis_id,
            pr.reading_id,
            'morphology',
            ta.engine,
            json_object('lemma', ta.lemma, 'features', ta.features_json),
            ta.confidence,
            'proposed'
        FROM token_analyses ta
        JOIN tokens t ON ta.token_id = t.token_id
        JOIN passage_readings pr ON t.reading_id = pr.reading_id
        JOIN passages p ON pr.passage_id = p.passage_id
        WHERE p.passage_id = ?
    """, passage_id)
```

### Query pattern to add hypothesis dependencies:

```python
def add_exclusion_edges(passage_id: str):
    """Same token index → mutually exclusive morphology hypotheses."""
    db.execute("""
        INSERT INTO hypothesis_dependency (hypothesis_id, depends_on_id, relation)
        SELECT a.hypothesis_id, b.hypothesis_id, 'excludes'
        FROM analysis_hypothesis a
        JOIN analysis_hypothesis b ON a.passage_reading_id = b.passage_reading_id
        JOIN tokens ta ON ta.reading_id = a.passage_reading_id
        JOIN tokens tb ON tb.reading_id = b.passage_reading_id
        WHERE a.hypothesis_type = 'morphology'
          AND b.hypothesis_type = 'morphology'
          AND a.hypothesis_id < b.hypothesis_id
          AND ta.token_index = tb.token_index
          AND ta.token_id != tb.token_id
    """, passage_id)
```

---

## 6. First experiment: Bhairavastava verse 1

### Setup

```python
passage_id = "bhairavastava.1"
g = build_from_passage(passage_id)
```

### Variables created

| Variable | Candidates |
|----------|------------|
| `token_0` | `bhairavanatham: [acc.sg, nom.sg, stem]` |
| `token_1` | `anathasaranyam: [acc.sg, nom.sg]` |
| `token_2` | `tvanmayacittataya: [instr.sg]` |
| `token_3` | `hrdi: [loc.sg]` |
| `token_4` | `vande: [1sg.pres, 3sg.pres, imperative]` |
| `compound` | `[karmadharaya, tatpurusa, bahuvrihi, unknown]` |
| `frame` | `[DevotionalAct, IdentityClaim, Predication]` |

### Factors activated

| Factor | Penalizes |
|--------|-----------|
| Surface | Overlapping/gapped segmentation |
| Morphology | Low-confidence Vidyut analysis |
| Agreement | Case mismatch between bhairavanatham and anathasaranyam |
| Agreement | Person mismatch between vande and implicit subject |
| Compound | Tatpurusa with accusative members (karmadharaya preferred) |
| Sense | Ordinary sense for bhairava in Trika text |
| Frame | DevotionalAct without praise verb |

### Expected output

```python
best = infer(g)
best.energy  # expected: ~2.3 (low)
best.choices:
  token_0 → bhairavanatham: acc.sg (karmadharaya analysis)
  token_1 → anathasaranyam: acc.sg
  token_2 → tvanmayacittataya: instr.sg
  token_3 → hrdi: loc.sg
  token_4 → vande: 1sg.pres
  compound → karmadharaya
  frame → DevotionalAct
```

The rejected tatpurusa compound should have energy ≈ 1.5 higher.

### Checkpoint criteria

```
1. Beam search runs without errors on Bhairavastava v1
2. Correct compound (karmadharaya) has lower energy than incorrect (tatpurusa)
3. Correct frame (DevotionalAct) has lower energy than alternatives
4. Agreement penalty fires when case is mismatched
5. Runtime < 100ms for a 9-verse batch
```

---

## 7. Implementation order

### Step 1: Factor graph core (2h)
- `src/sanskritree/inference/__init__.py`
- `src/sanskritree/inference/factor_graph.py` — FactorGraph, VariableChoice, Assignment, Factor base class

### Step 2: Individual factor implementations (4h)
- `src/sanskritree/inference/factors.py` — SurfaceFactor, MorphologyFactor, AgreementFactor, CompoundFactor, SenseFactor, FrameFactor, TranslationFactor

### Step 3: Search algorithm (3h)
- `src/sanskritree/inference/search.py` — beam_search, ilp_solve (stub)

### Step 4: Graph builder (3h)
- `src/sanskritree/graph/builder.py` — build_from_passage, seed_hypotheses, add_exclusion_edges

### Step 5: Bhairavastava test (2h)
- `tests/test_factor_graph.py` — test on all 9 verses, verify energy ordering

### Total: ~14 hours

---

## 8. What this connects to

After the factor graph works, the later phases plug in:

```
G1 (PyG):  Replace hand-coded factor energies with learned neural scorers
G2 (Sheaf): Add restriction maps that transform between variable types
G3 (Learn): Train pathway reliability weights from human adjudications
G4 (LLM):  Render lowest-energy assignment as constrained English
```

But first: 14 hours to a working factor graph on Bhairavastava.
