
PEER REVIEW — SANSKRIT PROOF ENGINE v1.0
What's solid
The schema is clean. The Pāṇini structure (paribhāṣā → saṃjñā → vidhi → niyama) is not just aesthetic — it correctly separates meta-rules from object-level rules, which matters when the system reasons about itself. The immutable/versioned/audit split is correct. The role boundaries in §5 are the most important thing in the document and they're right. warningAsError is right. The propagation rules in §3.5 are correct.

Critical gaps found
G1. Logic foundation is unspecified — this is fatal for Nāgārjuna
The schema assumes classical two-valued logic throughout. This works for Dharmakīrti. It breaks for Nāgārjuna. The catuskoti posits four possibilities for any state of affairs: that it holds, that it does not, both, or neither — making perfectly good sense in the semantics of paraconsistent logics such as First Degree Entailment. San Jose State University You need a declared logic foundation per tradition-scope or the CONTRADICTION node resolution is undefined for Buddhist texts. Without this, Nāgārjuna nodes will either be misclassified as HOLLOW (wrong) or cause the Lean kernel to reject paradoxical-but-meaningful claims (also wrong).
Fix required in §2: add axiom 2.11: logic_foundation ∈ {classical, FDE, intuitionistic} as a required field on Node, defaulting to classical. Nāgārjuna nodes: FDE. Dharmakīrti: classical. Abhinavagupta: likely classical with modal extension.
G2. Absence (abhāva) policy is too blunt
§2.9 says abhāva → OUTSIDE_FORMAL. In Navya-Nyāya, absence is doubly categorized into mutual absence and relational absence, both crucial for inferential processes, and the framework must accommodate non-well-foundedness. Academia.edu Blanket OUTSIDE_FORMAL loses the entire Nyāya/Dharmakīrti debate about whether absence is perceived or inferred — which is one of the most formally tractable debates in the corpus. The policy should be: abhāva claims → flag, require explicit absence_type annotation, then human decides OUTSIDE_FORMAL or custom type. Not blanket exclusion.
G3. The template set in §6 is insufficient
Six templates. Navya-Nyāya alone requires: avacchedaka (limitor), pratiyogin (counterpositive of absence), anuyogin (relatum of absence), nirupaka/nirupya (definer/defined), samavāya (inherence). The property-theoretic framework for Navya-Nyāya requires operations on properties and relations including their negations, and an account of pervasion (vyāpti) definition, all of which go beyond standard FOL patterns. Springer The template set needs ~12 entries minimum before you touch NN texts. Dharmakīrti can run on current templates. Add NN templates before phase 1 of §12 (which is Nyāya-Sūtras).
G4. No handling of two-negation types in Sanskrit
Nāgārjuna uses two different negations: paryudāsa (nominal/implicative negation) and prasajya-pratiṣedha (verbal/non-implicative negation), with importantly different scope. ResearchGate Your negation template is a single ¬ P. This maps both to the same Lean type, which makes structurally distinct claims look identical. In Lean4: paryudāsa → complement type {x // ¬ P x}, prasajya → propositional negation ¬ P. Different types. Conflating them produces false shared nodes. Add negation_type: paryudasa | prasajya to the negation template entry.
G5. Term registry has no version scope for semantic drift
Dharmakīrti's kalpanā and Abhinavagupta's kalpanā have different technical meanings. Your registry has tradition_scope but no mechanism for one term to have different definition_node_id values in different traditions. Schema fix: definition_node_id → definition_nodes: [{tradition, node_id}]. Without this, the registry becomes a source of false bridges between traditions using the same word with different meanings.
G6. No mechanism for tracking defeated arguments
REFUTED propagates up, but there's no record of what defeated the node or what argument was used. The Indian tradition is explicitly adversarial — Dharmakīrti doesn't just assert, he defeats Kumārila's position with a specific argument. The defeat matters as much as the defeat's outcome. Add to CONTRADICTION schema: defeat_argument: node_id | NULL — pointing to the node that constitutes the defeating argument. This is not metadata, it's the dialectic structure.
G7. Validation set (§4.7) has no timing constraint
You wrote "required before production" with no enforcement mechanism. In practice this will be skipped when you're excited and 50 nodes in. Add to §3.4 algorithm: PRECONDITION: validation_set_pass_rate = 1.0 OR status = DEV_MODE. Hard gate.

What's missing entirely
M1. The existing formalization literature is not cited
You are not the first. This work exists:

Computational aspects of the Technical Language of Navya-Nyāya have been described, including syntax of expressions, graphical rendering via Conceptual Graphs, and a semi-automatic computational algorithm Springer — Springer Handbook of Logical Thought in India, chapter by Guhe (2017). This is exactly your §6 templates but already done for NN. Read before implementing.
A property-theoretic framework for formal reconstruction of Navya-Nyāya logic exists Springer, Guhe (2017), same handbook. Your template set should derive from this, not be invented from scratch.
Graham Priest's FDE formalization of catuskoti (2010, Comparative Philosophy) — your FDE logic foundation for Nāgārjuna nodes should be this system or a declared variant of it.
Rick Briggs (1985), "Knowledge Representation in Sanskrit and AI" — AI Magazine. First computational NN formalization. Historical baseline.

Not citing these means you might rebuild what exists or contradict it without knowing. Both waste time.
M2. No policy on circular definitions
Dharmakīrti defines pramāṇa using arthakriyā. Arthakriyā is defined using successful cognition. Successful cognition uses pramāṇa-derived belief. This circularity is in the source texts — it's not a mistake, it's a structural feature. Your system has no handling. Options: (a) accept circularity, mark circular definition chains with a circular: bool flag, (b) require all DEFINITION nodes to have non-circular grounding. Decide now; it affects ~30% of nodes in any Indian epistemology text.
M3. No handling of tradition-internal contradiction
Your CONTRADICTION schema covers inter-tradition conflict. But Dharmakīrti contradicts himself between PV chapters (he's more idealist in some places, more realist in others). Dharmakīrti is the sort of author who sometimes modifies his thoughts radically across works Encyclopedia of Buddhism. These are intra-tradition contradictions requiring a different resolution path — not axiom choice between traditions, but text-critical judgment about which version is canonical or chronologically later. Add contradiction_scope: intra_author | intra_tradition | inter_tradition to the CONTRADICTION table.

The one structural problem
§3.4 step 4 says: "LLM: 'For C to be true, what must be true?'" This is fine for decomposition. But it cannot generate the child list from nothing — it needs the source text's own decomposition (svavṛtti, commentary) as the primary input, with LLM inference only as fallback when commentary is absent. The current algorithm doesn't distinguish these two sources. Add to step 4:
4. DECOMPOSE:
   4a. IF commentary exists for C: extract children from commentary
       decomposition_source = "commentary"
   4b. ELSE IF secondary scholarship exists: extract from scholarship  
       decomposition_source = "secondary"
   4c. ELSE: LLM inference
       decomposition_source = "llm"
       flag for human review
This is already in §4.1 as decomposition_source field but not enforced in the algorithm.

LLM continuation prompts
Give these cold to any capable model to continue the research:

PROMPT 1 — Logic foundation specification
You are formalizing Indian philosophical texts in Lean4. 
The system uses classical logic by default but requires 
paraconsistent logic (First Degree Entailment) for 
Madhyamaka texts and intuitionistic logic for certain 
Advaita claims.

Task: Specify exactly how to encode FDE as a Lean4 type 
system. Specifically:
1. How does a truth value set {T, F, B (both), N (neither)} 
   map to Lean4 types?
2. How do the FDE connectives (∧, ∨, ¬) differ from 
   classical Lean4 connectives?
3. Can FDE be encoded as a type class that classical nodes 
   import from, so the same Lean4 file can contain nodes 
   from both logics without conflict?
4. What is the minimal Lean4 boilerplate for a FDE-scoped 
   node versus a classical-scoped node?

Reference: Priest (2010) "The Logic of the Catuskoti", 
First Degree Entailment semantics.

PROMPT 2 — Navya-Nyāya template completion
The Sanskrit Proof Engine uses a template system to 
constrain LLM formalization of Sanskrit claims into 
Lean4 types. Current templates (abheda, vyapti, sambandha, 
avacchedaka, property, negation) are insufficient for 
Navya-Nyāya texts.

Task: Using Guhe (2017) "The Logic of Late Nyāya: 
A Property-Theoretic Framework" and Ganeri (2008) 
"Towards a formal regimentation of the Navya-Nyāya 
technical language", specify Lean4 type patterns for:
1. pratiyogin (counterpositive of absence)
2. anuyogin (relatum of absence)
3. nirupaka/nirupya (definer/defined relation)
4. samavāya (inherence)
5. The two absence types (anyonyābhāva, samsargābhāva)
6. avacchedaka in its limitor-of-cognition sense 
   (distinct from the quantifier sense)

For each: give the Lean4 type pattern with typed holes 
for arguments, one example from Tattvacintāmaṇi, and 
one example from Dharmakīrti's Pramāṇavārttika where 
the same operator appears under different terminology.

PROMPT 3 — Validation set construction
The Sanskrit Proof Engine requires a validation set of 
20 claims with known correct classifications before 
production use. Classifications: PROVED, OUTSIDE_FORMAL, 
HOLLOW, PARTIAL, with optional expected_divergence flag.

Task: Construct this validation set using only claims 
that have been formally analyzed in the secondary 
literature (Matilal, Ganeri, Tillemans, Dreyfus, Ratié). 
Do not invent classifications.

For each claim provide:
- source_text (IAST)
- source_ref (text.chapter.verse)
- expected_status
- expected_divergence (bool)
- justification citing the secondary source that 
  establishes the expected classification

Distribution required: 5 PROVED, 5 OUTSIDE_FORMAL, 
5 HOLLOW, 5 PARTIAL. Traditions: minimum 2 Buddhist, 
2 Nyāya, 1 Kashmir Shaivism.

PROMPT 4 — Circular definition policy
Indian epistemology texts contain circular definitions 
that are structural features, not errors. Example: 
Dharmakīrti's pramāṇa is defined via arthakriyā, which 
is defined via successful action, which presupposes 
pramāṇa-derived belief.

Task: Design a formal policy for the Sanskrit Proof 
Engine's handling of circular definition chains. 
Specifically:
1. Detection: algorithm for identifying circular 
   dependency chains in the node graph
2. Classification: when is circularity (a) a well-founded 
   recursive definition, (b) a vicious circle requiring 
   HOLLOW classification, (c) a coherentist structure 
   accepted as DEFINITION?
3. Lean4 encoding: how do well-founded circular 
   definitions map to Lean4's inductive types or 
   well-founded recursion? How does this differ from 
   the encoding of non-circular definitions?
4. Precedent: cite at least two examples from Indian 
   philosophy literature where scholars have explicitly 
   addressed this circularity issue.

PROMPT 5 — Cross-tradition proof chain specification
The Sanskrit Proof Engine aims to discover "bridges" — 
cases where independent decomposition of claims from 
different traditions yields the same Lean4 type. The 
system must distinguish genuine bridges (independent 
convergence) from constructed bridges (bias).

Task: Specify the exact algorithm for bridge detection.
1. What constitutes "same Lean4 type"? Definitional 
   equality? Alpha equivalence? Up to isomorphism?
2. At what granularity is comparison performed — 
   leaf nodes only, or entire proved subtrees?
3. When two nodes share a Lean type but their 
   formalization_rationale fields cite different 
   Sanskrit terms, what is the protocol?
4. Specify the data structure for a confirmed bridge: 
   what fields beyond node_a and node_b are required 
   to make it auditable and falsifiable?
5. Give one worked example of a genuine bridge and 
   one of a false bridge (where surface similarity 
   conceals a difference in the underlying Sanskrit).

---

## IN-DEPTH REVIEW & RESEARCH FINDINGS

### Research methodology

Web searches, academic sources, and MCP fetches were used to address G1–G7, M1–M3, and PROMPTs 1–5. Findings below.

---

### PROMPT 1 — FDE in Lean4 (Logic foundation for Nāgārjuna)

**Sources:** Priest (2010) "The Logic of the Catuskoti" (Comparative Philosophy 1.2); Dunn/Belnap FDE; lean4-logic, logic4, Formalized Formal Logic.

**Findings:**

1. **Truth values {T, F, B, N} → Lean4 types**

   Priest uses Dunn’s four-valued lattice: t (true), f (false), b (both), n (neither). In Lean4 this maps to:

   - `inductive FDEVal : Type | t | f | b | n`
   - Or `structure FDEProp where val : FDEVal` with `Prop`-level semantics via a valuation function.

   No existing Lean4 FDE implementation was found. `iehality/lean4-logic` covers classical, intuitionistic, modal; `fgdorais/logic4` is general; neither has FDE. Implementation must be added.

2. **FDE connectives vs classical**

   - Conjunction: meet (glb) in Dunn lattice; b ∧ f = f, t ∧ n = n.
   - Disjunction: join (lub); b ∨ n = t.
   - Negation: ¬t = f, ¬f = t, ¬b = b, ¬n = n (fixed points for b, n).

   These differ from classical `And`, `Or`, `Not`; they must be defined as lattice operations on `FDEVal`.

3. **Type class for classical vs FDE**

   Use a type class to switch logic:

   ```lean
   class LogicFoundation (α : Type) where
     logic : LogicKind  -- classical | FDE | intuitionistic
   ```

   Nodes with `logic_foundation = FDE` use `FDEProp` and FDE connectives; classical nodes use `Prop`. Same file can mix both by scoping to different namespaces or modules.

4. **Minimal boilerplate**

   - FDE module: `FDEVal`, `FDEProp`, `fdeAnd`, `fdeOr`, `fdeNot`, valuation `⟦·⟧ : FDEProp → FDEVal`.
   - Node annotation: `logic_foundation : LogicKind` on Node (schema axiom 2.11).
   - Nāgārjuna nodes: `logic_foundation = FDE`; Dharmakīrti: `classical`.

**Action:** Add axiom 2.11 to SCHEMA.md; implement FDE module in proof_engine; document in proofenginge.md.

---

### PROMPT 2 — Navya-Nyāya template completion

**Sources:** Guhe (2017) Springer Handbook; Ganeri (2008) "Towards a formal regimentation…"; advaita.org.uk navya-nyāya; wisdomlib.org abhāva types.

**Findings:**

| Template | Lean pattern | NN role | Example (Tattvacintāmaṇi) |
|----------|--------------|---------|---------------------------|
| pratiyogin | `Counterpositive P x := ¬(P x)` — counterpositive of absence | What is absent | absence-of-pot-on-floor: pot = pratiyogin |
| anuyogin | `Bearer P x := locus of absence` | Where absence holds | floor = anuyogin |
| nirupaka/nirupya | `Definer P Q := ∀ x, Q x ↔ DefOf P x` | Definer/defined | vyāpti defined by co-location |
| samavāya | `Inheres a b := InherenceRel a b` — substance–quality, whole–part | Inherence relation | color inheres in pot |
| anyonyābhāva | `A ≠ B` (mutual absence) | Mutual exclusion | pot ≠ cloth |
| saṃsargābhāva | `¬(R a b)` (relational absence) | Prior/posterior/constant absence | prāgabhāva, pradhvaṃsābhāva, atyantābhāva |
| avacchedaka (limitor) | `∀ {x : α}, Limitor P x` — cognition limitor | Restricts cognition scope | avacchedaka as qualifier of cognition |

**Four absence types (Nyāya):**

1. **Prāgabhāva** — prior absence (before creation)
2. **Pradhvaṃsābhāva** — posterior absence (after destruction)
3. **Atyantābhāva** — constant absence (never present)
4. **Anyonyābhāva** — mutual absence (A ≠ B)

First three = relational absence; fourth = mutual exclusion. G2 fix: require `absence_type` annotation instead of blanket OUTSIDE_FORMAL.

**Action:** Extend §6 templates to ~12 entries; add pratiyogin, anuyogin, nirupaka, nirupya, samavāya, anyonyābhāva, saṃsargābhāva, avacchedaka_limitor. Derive from Guhe/Ganeri, not ad hoc.

---

### PROMPT 3 — Validation set construction

**Requirement:** 20 claims, 5 each of PROVED, OUTSIDE_FORMAL, HOLLOW, PARTIAL. Min 2 Buddhist, 2 Nyāya, 1 Kashmir Shaivism. Secondary literature only (Matilal, Ganeri, Tillemans, Dreyfus, Ratié).

**Proposed structure (to be filled from secondary sources):**

| # | Tradition | Source | Claim (IAST) | Expected | Justification |
|---|------------|--------|--------------|----------|---------------|
| 1–5 | Mixed | NS, PV, TA | TBD | PROVED | Formalizable vyāpti, identity, inference structure |
| 6–10 | Mixed | MMK, NS | TBD | OUTSIDE_FORMAL | Empirical, absence, catuskoti (pre-FDE) |
| 11–15 | Mixed | Rhetorical, poetic | TBD | HOLLOW | Unfalsifiable, purely rhetorical |
| 16–20 | Mixed | Cross-domain | TBD | PARTIAL | Part formal, part empirical |

**Action:** Create `validation_set.md`; populate from Matilal (1985, 1998), Ganeri (2001, 2008), Tillemans (1999), Dreyfus (1997), Ratié (2011). Do not invent; cite each classification.

---

### PROMPT 4 — Circular definition policy

**Sources:** Dharmakīrti pramāṇa–arthakriyā; Wikipedia Pramāṇavārttika; Foundations of Dharmakīrti's Philosophy.

**Findings:**

1. **Detection**

   Build dependency graph: DEFINITION nodes with `definition_of` edges. Run cycle detection (DFS). Cycles = circular chains.

2. **Classification**

   - **(a) Well-founded recursive:** Base case exists; recursion terminates (e.g. inductive types). → Allow, encode as Lean `inductive`.
   - **(b) Vicious circle:** No base case; no independent grounding. → HOLLOW or flag `circular: vicious`.
   - **(c) Coherentist:** Mutually supporting but not vicious; accepted in tradition. → `circular: coherentist`, human review, possible DEFINITION with caveat.

3. **Lean4 encoding**

   - Well-founded: `inductive` or `well_founded` recursion.
   - Vicious: Do not encode as DEFINITION; mark HOLLOW.
   - Coherentist: Encode as axiom block with explicit `axiom`; document circularity in `formalization_rationale`.

4. **Precedent**

   - Dharmakīrti: pramāṇa ↔ arthakriyā ↔ successful cognition. Discussed in Dreyfus (1997), Tillemans.
   - Nyāya: pramāṇa defined via pramā (valid cognition); circularity debated in later Nyāya.

**Action:** Add `circular: bool | vicious | coherentist | null` to DEFINITION nodes; document policy in §2 or new §2.10a.

---

### PROMPT 5 — Bridge detection algorithm

**Findings:**

1. **"Same Lean4 type"**

   Use **definitional equality** (`Eq`) for proved terms. Alpha-equivalence for unproved types. Avoid "up to isomorphism" unless explicitly defined—too loose for falsifiability.

2. **Granularity**

   Compare **proved leaf nodes** first. If two roots have identical proved subtrees (same `lean_type` + `lean_proof`), treat as bridge. Do not compare UNPROVED or PLACEHOLDER subtrees.

3. **formalization_rationale differs**

   If `lean_type` matches but `formalization_rationale` cites different Sanskrit terms:

   - Flag for human review.
   - Do not auto-confirm bridge.
   - Possible genuine convergence (same structure, different terms) or false bridge (bias). Human decides.

4. **Bridge data structure**

   ```json
   {
     "id": 1,
     "node_a": 42,
     "node_b": 87,
     "lean_type_hash": "sha256...",
     "comparison_granularity": "leaf" | "subtree",
     "formalization_rationale_match": true | false,
     "human_confirmed": bool,
     "discovery_method": "automated" | "human"
   }
   ```

   Required: `node_a`, `node_b`, `lean_type_hash`, `human_confirmed`. Optional: `formalization_rationale_match`, `discovery_method`.

5. **Worked examples**

   - **Genuine bridge:** Nyāya "vyāpti = co-location of hetu and sādhya" and Dharmakīrti "vyāpti = invariable concomitance" → both `∀ x, H x → S x` when properly formalized. Independent traditions, same structure.
   - **False bridge:** "śūnyatā" (Madhyamaka emptiness) vs "brahman" (Advaita) both sometimes rendered as "absence of intrinsic nature." Surface similarity; different negation types (prasajya vs paryudāsa) and different logic (FDE vs classical). Do not bridge.

---

### G4 — Two negation types (paryudāsa vs prasajya-pratiṣedha)

**Sources:** Buddha-Nature glossary; Tsadra; Harvard-Yenching; Nāgārjuna's Negation (Springer).

| Type | Sanskrit | Meaning | Lean encoding |
|------|----------|---------|---------------|
| Paryudāsa | पर्युदासप्रतिषेध | Implicative/qualified negation; implies alternative | `{x // ¬ P x}` (subtype/complement) |
| Prasajya-pratiṣedha | प्रसज्यप्रतिषेध | Non-implicative; pure denial | `¬ P` (propositional negation) |

**Example:** "Brahmins should not drink" (prasajya) = pure denial. "Non-Brahmin" (paryudāsa) = implies some other class.

**Action:** Add `negation_type: paryudasa | prasajya` to negation template; use distinct Lean patterns.

---

### M1 — Formalization literature (citations)

| Author | Year | Title | Relevance |
|--------|------|-------|------------|
| Briggs | 1985 | "Knowledge Representation in Sanskrit and AI" (AI Magazine 6.1) | First computational Sanskrit–AI link; semantic nets vs Pāṇini |
| Priest | 2010 | "The Logic of the Catuskoti" (Comparative Philosophy 1.2) | FDE formalization of tetralemma |
| Guhe | 2017 | "The Logic of Late Nyāya: A Property-Theoretic Framework" (Springer Handbook) | NN templates, Conceptual Graphs, semi-automatic algorithm |
| Ganeri | 2008 | "Towards a formal regimentation of the Navya-Nyāya technical language" (College Publications) | Formal regimentation of NN technical language |

**Action:** Add REFERENCES section to SCHEMA.md or proofenginge.md citing these.

---

### Summary: schema changes required

| Gap | Fix |
|-----|-----|
| G1 | Add axiom 2.11: `logic_foundation ∈ {classical, FDE, intuitionistic}` |
| G2 | Replace blanket abhāva→OUTSIDE_FORMAL with `absence_type` annotation + human decision |
| G3 | Extend §6 to ~12 templates (pratiyogin, anuyogin, nirupaka, nirupya, samavāya, absence types, avacchedaka_limitor) |
| G4 | Add `negation_type: paryudasa | prasajya` to negation template |
| G5 | `definition_node_id` → `definition_nodes: [{tradition, node_id}]` |
| G6 | Add `defeat_argument: node_id | NULL` to CONTRADICTION |
| G7 | PRECONDITION: `validation_set_pass_rate = 1.0 OR status = DEV_MODE` in §3.4 |
| M1 | Add REFERENCES section |
| M2 | Add circular definition policy (detection, classification, encoding) |
| M3 | Add `contradiction_scope: intra_author | intra_tradition | inter_tradition` to CONTRADICTION |
| Structural | Enforce 4a→4b→4c in DECOMPOSE step |