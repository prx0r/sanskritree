# SANSKRIT PROOF ENGINE
## Formal Instructions for an LLM Agent

---

## WHAT THIS IS

A **truth compressor**. Takes claims from Sanskrit philosophical texts,
decomposes them recursively until reaching either:
- A proved Lean4 theorem (formal content confirmed)
- An empirical claim (outside formal, needs evidence)
- An undefined term (unsayable, needs axiom)

The output is a **node graph** where every node has an integer ID,
a status, and a traceable path to its justification.

Proofs are the reward signal. Boundaries are equally valuable findings.
The system does not aim at proofs. It aims at honesty.

**DO NOT** bias decomposition toward existing formal results.
Decompose faithfully to the source text. If no proof emerges, PARTIAL
or OUTSIDE_FORMAL is the correct and informative result.

---

## DATABASE SCHEMA

```sql
CREATE TABLE nodes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id     INTEGER,
    statement     TEXT NOT NULL,
    sanskrit      TEXT,              -- IAST transliteration
    devanagari    TEXT,              -- display only
    provenance    TEXT,              -- JSON: {text, tradition, period, author, ref}
    node_type     TEXT NOT NULL,     -- FORMAL | EMPIRICAL | DEFINITION | UNSAYABLE
    status        TEXT NOT NULL,     -- PROVED | UNPROVED | PARTIAL | HOLLOW
                                     -- OUTSIDE_FORMAL | PLACEHOLDER | REFUTED
    lean_type     TEXT,              -- Lean4 type signature
    lean_proof    TEXT,              -- Lean4 proof term
    mathlib_deps  TEXT,              -- JSON array
    reuse_count   INTEGER DEFAULT 0, -- imports by other nodes
    notes         TEXT,
    created_at    TEXT
);
```

**reuse_count** is the centrality measure. High reuse = centre node.
Not declared. Emerges from the graph.

---

## THE ALGORITHM

```
INPUT: claim C

STEP 0 — SAYABILITY
  Can C be falsified? Can you state what would make it false?
  NO  → node_type=UNSAYABLE, status=HOLLOW. Stop. Return to human.
  YES → create node, continue.

STEP 1 — LIBRARY CHECK
  Query LeanSearch (leansearch.net): natural language match for C
  Query Loogle (loogle.lean-lang.org): type signature match
  Match found and reuse warranted → import node, increment reuse_count. Done.
  No match → continue.

STEP 2 — FORMALIZE
  Express C as a candidate Lean4 type signature.
  Be conservative. If unsure, decompose instead.

STEP 3 — PROVE ATTEMPT
  Submit to Pantograph (Lean4 REPL, machine-to-machine).
  Run ReProver (LeanDojo retrieval-augmented prover) as second attempt.

  Compiles, no sorry  → status=PROVED. Store proof. Done.
  sorry remaining     → status=PLACEHOLDER. Human needed.
  Type error          → formalization wrong → go to STEP 4.
  Fails               → go to STEP 4.

STEP 4 — DECOMPOSE
  Ask: "For C to be true, what must be true?"
  Produce children C1...Cn such that (C1 ∧ C2 ∧ ... Cn) → C.
  Classify each child:

  DEFINITION  → add to axiom base, record philosophical commitment
  EMPIRICAL   → status=OUTSIDE_FORMAL, stop branch, note evidence needed
  UNSAYABLE   → status=HOLLOW, stop branch, return to human
  FORMAL      → create node, recurse from STEP 0

STEP 5 — PROPAGATE (after subtree completes)
  PROVED   = all children PROVED or DEFINITION
  PARTIAL  = some PROVED, some EMPIRICAL  ← normal for philosophy
  UNPROVED = any child UNPROVED or PLACEHOLDER
  HOLLOW   = any child UNSAYABLE
  REFUTED  = any child REFUTED
```

---

## TOOL STACK

| Tool | Role | Call |
|------|------|------|
| **Mathlib4** | Foundation (~2M lines) | Import in Lean files |
| **LeanSearch** | NL → Lean declaration | HTTP GET leansearch.net |
| **Loogle** | Type signature → theorem | HTTP GET loogle.lean-lang.org |
| **Pantograph** | Python↔Lean4 REPL | subprocess |
| **ReProver** | Retrieval-augmented prover | LeanDojo API |
| **Heritage Engine** | Sanskrit morphology + sandhi | HTTP sanskrit.inria.fr |
| **ByT5-Sanskrit** | Tokenization, POS, dependency | HuggingFace: bowphs/ByT5-Sanskrit |
| **GRETIL** | Sanskrit corpus (machine-readable) | gretil.sub.uni-goettingen.de |
| **pramana-nlp** | Pre-processed Sanskrit philosophy corpus | github.com/tylergneill/pramana-nlp |
| **SQLite** | Node database | local |
| **LLM (Claude Sonnet)** | Decomposition + formalization | Anthropic API |

---

## SANSKRIT PROCESSING PIPELINE

For Sanskrit-sourced claims only. Skip for English claims.

```
Raw Sanskrit text (GRETIL)
        ↓
Heritage Engine — sandhi split, morphological analysis, Pāṇinian derivation
        ↓
ByT5-Sanskrit — tokenization, POS tagging, dependency parse
        ↓
Navya-Nyāya parse — extract cognitive structure (LLM-assisted)
  Key relations: abheda (identity), vyāpti (concomitance),
                 sambandha (relation), avacchedaka (limitor)
        ↓
Lean4 type candidate — conservative formalization
        ↓
Enter main algorithm at STEP 1
```

**Provenance labelling** — every Sanskrit node gets:
```json
{
  "tradition": "kashmir_shaivism | nyaya | advaita | buddhist",
  "period": "~200CE | 10th_century_CE | 14th_century_CE",
  "text": "nyaya_sutra | tantraloka | shiva_sutra | tattvacintamani",
  "register": "sutra | navya_nyaya | tantric_shaiva | vedantic",
  "ref": "book.chapter.verse or ahnika.verse"
}
```

Same Sanskrit word in different traditions → different nodes (different meaning).
Same Lean type from different nodes → shared proof, reuse_count incremented.

---

## TEXTS: PHASE 1 — NYĀYA (validation corpus)

**Purpose**: validate the pipeline. Nyāya was designed as a formal inference
system. Claims decompose cleanly. Multiple English translations available
for benchmarking. Expected outcome: most formal content proves, soteriological
claims terminate OUTSIDE_FORMAL.

**Primary text**: Nyāya-Sūtras Book 1, Chapter 1 (Gautama, ~200 CE)
Translations: Ganganatha Jha (1912), Matilal (1985), Ganeri (2001)

**Key terms to decompose in order**:

1. **pramāṇa** — valid means of cognition
   Expected Lean type: `∀ s p, ValidCognition s p → p`
   Interest: factivity axiom is where Nyāya and Buddhist epistemology
   formally diverge. Same structure, different axiom. Divergence node.

2. **saṃśaya** — doubt
   Expected Lean type: `∀ obj, Doubt obj ↔ ¬(∃! c, Determines c obj)`
   Interest: maps to non-unique determination. Possibly bridges to
   conditional entropy but DO NOT aim for this. Let decomposition decide.

3. **vyāpti** — universal concomitance
   Expected Lean type: `∀ x, Hetu x → Sadhya x`
   Interest: core inference principle. Proves cleanly as universal implication.
   Sanskrit direct parse reaches this in 1 step vs 2-3 for English translations.
   Measure the difference. Record it.

4. **anumāna** — inference (five-membered syllogism)
   Interest: the complete inference structure. pratijñā (thesis), hetu (reason),
   udāharaṇa (example), upanaya (application), nigamana (conclusion).
   This is a proof structure. May formalize as an inference rule in Lean.

5. **nigrahasthāna** — grounds for defeat in debate
   Interest: formal fallacy catalogue. Maps to type errors in Lean.
   A hetvābhāsa (pseudo-reason) is a malformed proof term.

**Translation benchmark protocol**:
For each key term, run:
- Sanskrit source via Heritage Engine pipeline
- Each available English translation independently
Record: steps to shared node, node ID reached, divergence points.
Divergence = the translation introduced or lost semantic content.

---

## TEXTS: PHASE 2 — SHIVA SUTRAS (the interesting part)

**Purpose**: test on maximally compressed ontological claims.
Shiva Sutras are 77 aphorisms. 3 sections. Terse to the point of
being almost purely nominal. The grammar does almost all the work.

**Primary text**: Shiva Sūtras (Vasugupta, ~9th century CE)
Commentary: Kṣemarāja's Vimarśinī (use for decomposition guidance)
Tradition: Kashmir Shaivism (Trika)
Register: tantric_shaiva

**Section 1: Śāmbhavopāya** (the divine means)

**SS 1.1**: *citiḥ śaktiḥ* — consciousness-power
  Sanskrit parse: two nominals, abheda (identity) relation
  DO NOT translate as "consciousness is power" — Heritage Engine gives
  you identity, not predication. Lean type: `Citi = Sakti` (type identity)
  or `∃ f : Citi ≃ Sakti, ...` (isomorphism)
  Interest: if this shares a node with anything in Levin bioelectric cognition
  or FEP, it's a genuine finding. If not, PARTIAL is correct.

**SS 1.2**: *jñānaṃ bandhaḥ* — knowledge is bondage
  Interest: paradox. Pramāṇa (valid knowledge) is liberation in Nyāya.
  Here knowledge is bondage. Same term (jñāna), opposite valence.
  Will decompose to reveal: what KIND of knowledge? Differentiated vs
  undifferentiated? This is a real philosophical distinction that may
  formalize as a type distinction.

**SS 1.3**: *yoniḥ vargāṇāṃ kalaśarīram* — the womb of groups is
  the body of kala (limited time/action)
  Interest: highly esoteric. Expected result: mostly OUTSIDE_FORMAL
  or HOLLOW. The system correctly identifies this. That is the finding.

**SS 1.5**: *udyamo bhairavaḥ* — effort/upsurge IS Bhairava
  Interest: another identity claim (abheda). Bhairava = absolute
  consciousness. Effort = dynamic aspect. If Citi=Sakti (SS 1.1) proved,
  does udyamo=bhairavaḥ share that node? If yes: same formal structure,
  different mythic framing. Reuse_count goes up on the identity node.

**Section 2: Śāktopāya** (the power means)
Focus: SS 2.1-2.7 (theory of mantras as cognitive operators)
Interest: mantras described as operators that transform cognitive states.
This is an action semantics. May formalize as state transition functions.

**Section 3: Āṇavopāya** (the individual means)
Mostly practice instructions. Expected: mostly OUTSIDE_FORMAL.
Confirms the system correctly identifies propositional vs performative claims.

---

## TEXTS: PHASE 3 — TANTRĀLOKA CROSSOVER (the research hypothesis phase)

**Purpose**: Abhinavagupta's full ontological system. Longer arguments.
Use as research hypothesis generator.

**Primary text**: Tantrāloka (Abhinavagupta, ~1000 CE)
Focus āhnikas: 1 (consciousness), 3 (śakti theory), 6 (ābhāsa/manifestation),
               9 (spanda/vibration)

**The agent protocol for crossover**:

When a PARTIAL node is found — formal content proved, empirical/metaphysical
content outside formal — the agent may:

1. Extract the proved formal component as a research hypothesis
2. Search scientific literature for claims with the same formal structure
3. If found: run the scientific claim through the algorithm independently
4. Compare node IDs

If independent decompositions share a node: record as convergence finding.
If not: record as non-convergence. Both are valid results.

Example:
- SS 1.1 *citiḥ śaktiḥ* proves: `Citi ≃ Sakti` (identity of two aspects)
- Hypothesis: is there a scientific claim formalizing to a similar type identity?
- Candidate: Levin's claim that bioelectric pattern = cognitive identity
- Run Levin claim independently
- Check for node sharing
- DO NOT force the match. Record honestly.

**Interesting candidate crossovers** (run independently, compare):

| Sanskrit claim | Scientific candidate | Why interesting |
|---------------|---------------------|-----------------|
| *spanda* — vibration as nature of consciousness (TA 9) | Oscillatory dynamics in neural binding (Engel 2001) | Both claim oscillation is constitutive, not epiphenomenal |
| *ābhāsa* — appearance/manifestation as information (TA 6) | FEP generative model (Friston 2010) | Both describe reality as the structure of appearances |
| *vimarśa* — self-reflexive awareness (TA 1) | Higher-order theories of consciousness (Rosenthal) | Both require self-reference as constitutive |
| *saṃvit* — pure awareness as ground state | Integrated Information Theory Φ (Tononi) | Both claim consciousness is fundamental, not derived |
| *krama* — sequential cognition (Krama school) | Temporal binding / predictive coding | Sequential structure of cognition as formal object |

**None of these are declared bridges. They are hypotheses.**
Run each pair independently. The algorithm decides.

---

## PĀṆINI LAYER (phase 2+)

Every Sanskrit morphological parse via Heritage Engine traces through
Pāṇinian rules (Aṣṭādhyāyī). Make this explicit:

```
vyāptiḥ
→ root: vyāp (to pervade) — dhātu
→ suffix: -ti (kṛt, action noun) — kṛdanta
→ case: nominative singular feminine — vibhakti
→ Pāṇinian rule chain: [3.3.18] [7.2.116] ...

Each rule application is a sub-node:
  node: "vyāp takes -ti suffix by rule 3.3.18"
  node_type: DEFINITION
  status: PROVED (rule application is deterministic)
  lean_type: -- grammatical derivation, not propositional
```

Value: the grammatical derivation is a proof that the Sanskrit term
means what the parse says it means. No translation assumption.
The meaning is in the grammar.

Over many terms: which Pāṇinian rule patterns correlate with
clean formalization? Which with OUTSIDE_FORMAL? This is a finding
about Sanskrit's internal formal structure.

---

## WHAT THE SYSTEM IS NOT

- Not a translation tool. Heritage Engine handles translation.
  The system maps formal content, not meaning.

- Not a bridge-finder. Bridges are discovered by independent
  convergence. Never constructed.

- Not a Sanskrit teacher. Though the output is the most precise
  analysis of Sanskrit philosophical claims ever produced.
  That's a side effect, not a goal.

- Not aiming at proofs. PARTIAL and OUTSIDE_FORMAL are correct
  outputs when the text doesn't support formalization.
  The boundary IS the result.

---

## THE ACTUAL GOAL

A **node graph** where:

- Centre nodes (high reuse_count) = formal primitives that appear
  across traditions, texts, sciences. Not declared. Found.

- Boundary nodes (OUTSIDE_FORMAL leaves) = precise map of where
  each tradition's formal content ends.

- Divergence nodes (DEFINITION/AXIOM) = where traditions share
  structure but differ in commitment.
  These are the philosophically interesting nodes.
  Not "these traditions disagree" — but "they disagree at exactly
  this axiom, and here is the formal statement of the disagreement."

- Translation quality = measurable. Steps to shared node.
  Not subjective. Formal.

After enough runs: the graph is the best Sanskrit philosophy teacher
ever built. Every claim traced to its formal content. Every boundary
precisely located. Every cross-tradition connection either proved
or honestly absent.

---

## INITIAL RUN INSTRUCTIONS

```python
# 1. Install
pip install sqlite3 requests anthropic

# 2. Install Lean4 + Mathlib
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh
lake new proof_engine
cd proof_engine && echo 'require mathlib from ...' >> lakefile.lean
lake exe cache get

# 3. Install Pantograph
pip install pantograph

# 4. Run Phase 1
# Start with Nyāya-Sūtra 1.1.1, terms in order:
# pramāṇa → saṃśaya → vyāpti → anumāna
# Get pipeline working before touching Shiva Sutras.

# 5. Validate translation benchmark
# Each term: run Sanskrit route and all available English translations.
# Confirm they reach the same node.
# If they don't: the divergence is your first finding.

# 6. First interesting node to prove (not simulate):
# vyāpti: ∀ x, Hetu x → Sadhya x
# This is just forall_imp in Mathlib. Should compile.
# If it does: you have your first real proved node from a Sanskrit source.
```

---

## NODE 9 CLARIFICATION

The vyāpti ↔ Shannon bridge claimed in earlier exploration was
**methodologically unsound**. The sorry was not a technical gap —
it was hiding the fact that vyāpti was interpreted selectively
to match Shannon. That is bias, not discovery.

The correct approach:
- Decompose vyāpti faithfully per Navya-Nyāya commentary
- Let it reach whatever Lean type honest decomposition produces
- Separately decompose Shannon conditional entropy
- If they share a node: that is a finding
- If they don't: that is equally a finding

The system's value is not in finding bridges.
It is in making the question formally answerable.