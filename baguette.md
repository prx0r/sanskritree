Where Pāṇini's limits are and how to destroy them
Pāṇini was operating under brutal constraints: oral transmission, no external memory, single human working memory as the runtime. His genius was compression and conflict resolution within those constraints. Remove those constraints and the design space explodes open.
His system is:

Sequential (one derivation path at a time, no parallelism)
Opaque (rules are text sutras, not inspectable data structures)
Static (the rule set is fixed, no learning from new derivations)
Unidirectional (Sanskrit → valid form, not form → explanation of why)
No proof objects (the derivation trace exists in the practitioner's memory, not as a reified artifact)

Every one of these is a solvable engineering problem in 2025. Here's the full system.

The Formal Derivation Engine: complete design
Theoretical foundation
Your system is formally a Confluent Term Rewriting System (TRS) over a typed signature, with:

Signature Σ = the NN operators from §6 (abheda, vyāpti, sambandha, etc.) + tradition labels
Terms = well-formed NN expressions built from Σ over the term registry
Rewrite rules = your §6 templates, each of the form NNExpr → LeanType
Properties needed: termination + confluence → gives unique normal forms (= unique Lean types for each NN expression)

A confluent and terminating rewriting system is complete — it gives a decision procedure for the equational theory: given two terms, reduce them to normal form; they are equivalent iff their normal forms are equal. arXiv
This is exactly what you need. A Sanskrit claim's Lean type is its normal form under your template TRS. If the TRS is confluent and terminating, every claim has exactly one Lean type. No ambiguity. No LLM guessing.
The Metatheory library in Lean 4 provides a generic framework for abstract rewriting systems with reusable definitions and three fully mechanized meta-theorems — confluence via diamond property, Newman's lemma, and Hindley-Rosen — all with zero axioms or sorry placeholders. arXiv
You should build your template system on top of this library. Your §6 templates become rewrite rules in a formally verified TRS. Confluence of your template system is then machine-checkable.

The complete architecture: five layers
LAYER 0: PHONOLOGY / MORPHOLOGY  (Heritage + ByT5)
  Input:  Raw IAST Sanskrit
  Output: Sandhi-split tokens, morphological tags, dependency parse (CoNLL-U)
  Tools:  Heritage parser, ByT5-Sanskrit (April 2024 DCS snapshot)
  Note:   This is Pāṇini's own domain. We USE his system here, not replace it.
          Aṣṭādhyāyī rule application = DEFINITION nodes, always PROVED.

LAYER 1: SEMANTIC PARSE / NN EXPRESSION  (new, your system)
  Input:  Morphological parse
  Output: NNExpr tree (terms over Σ from §6)
  How:    LLM with constrained output grammar — only Σ operators allowed
          Anuvrtti: inherit parent expression context, state only delta
          Tradition label applied here as a type parameter

LAYER 2: TERM RESOLUTION  (registry + saṃjñā)
  Input:  NNExpr tree with raw IAST
  Output: NNExpr tree with registry IDs
  How:    Lookup §4.4; flag unregistered terms for human before proceeding
          Polysemy resolved here (svabhāva[Nyāya] ≠ svabhāva[Dharmakīrti])

LAYER 3: TRS NORMALIZATION  (the engine core)
  Input:  Typed NNExpr tree
  Output: Lean type (normal form under §6 TRS)
  How:    Apply template rewrite rules to NNExpr
          Conflict resolution:
            SOI (same subexpression): apavāda/exception template wins
            DOI (different subexpressions): dependent-term template wins
          Termination guaranteed by: templates are strictly reducing
            (NNExpr complexity strictly decreases at each step)
          Confluence: checkable via Metatheory library critical pair analysis
          Result: unique lean_type or OUTSIDE_FORMAL if no template matches

LAYER 4: PROOF STRATEGY SELECTION  (not generation)
  Input:  lean_type, kāṇḍa assignment, node_type
  Output: proof_strategy ∈ {axiom, exact, apply, constructor, fde_eval, OUTSIDE}
  Rules:
    DEFINITION ∨ kāṇḍa=1  →  axiom  (stipulated, no proof needed)
    vyāpti type           →  intro x; exact h x
    sambandha type        →  constructor
    abheda type           →  rfl or exact proof of equality
    FDE type (kāṇḍa=3)   →  fde_eval (custom, see below)
    No matching strategy  →  OUTSIDE_FORMAL

LAYER 5: LEAN COMPILATION + FEEDBACK LOOP
  Input:  lean_type + proof_strategy
  Output: PROVED | PLACEHOLDER | compile error
  Tools:  lake build + Pantograph REPL
  Key:    Compiler feedback as reward signal (à la Process-Driven Autoformalization)
          Errors bubble back to Layer 3: try next applicable template
          Max retries: 3; after that → PLACEHOLDER + human flag

Where Pāṇini gets surpassed
1. Parallelism. Pāṇini's machine is single-threaded. Yours isn't. Kāṇḍa 1 (siddha, axiom) nodes can all be instantiated simultaneously since they're mutually visible and non-conflicting. Kāṇḍa 2 (vidhi) nodes can be processed in parallel within dependency groups — only cross-group ordering matters. Kāṇḍa 3 (asiddha) nodes must be sequential, but they're the minority. This gives you roughly O(depth of dependency graph) serial work instead of O(total nodes).
2. Bidirectionality. Pāṇini goes Sanskrit → form. Your system goes both ways:

Forward: Sanskrit claim → Lean type (normal form derivation)
Backward: Given a Lean type from Mathlib/PhysLean/some existing proof, search for matching NNExpr — this is your bridge detection (§4.6), now fully automated. A bridge fires when backward search from a Lean type matches an existing node. Pāṇini had no notion of this.

3. The siddha/asiddha split is dynamic, not static. In Aṣṭādhyāyī it's fixed — certain rules are always asiddha to others. In your system, a node's kāṇḍa assignment can change as its status changes. A PLACEHOLDER in kāṇḍa 2 that gets proved promotes to siddha visibility. A CONTRADICTION resolution can demote a node from kāṇḍa 1 to kāṇḍa 2. This gives you monotone proof propagation with dynamic scope.
4. Learning from the derivation trace. Every time a Sanskrit claim → Lean type derivation succeeds, that derivation becomes a training example for the Layer 1 LLM. Process-driven autoformalization (leverages precise feedback from Lean 4 compilers to enhance autoformalization, enabling higher compiler accuracy using less filtered training data arXiv) gives you the feedback loop for free. Your system self-improves. Pāṇini's doesn't.
5. Anuvrtti as actual context compression in the DB. In §4.1 the node schema currently stores full context. With anuvrtti:
sql-- Add to §4.1 Node schema:
inherited_from    INT       NULL  -- parent node ID
delta_terms       JSON      NULL  -- only the NEW terms vs parent
full_context      COMPUTED  --    inherited_from.full_context ∪ delta_terms
This means a Dharmakīrti node about anumāna doesn't re-state pramāṇa, arthāpatti, pratyakṣa — it inherits them. Your registry query is then a simple join. Storage drops dramatically for deep derivation chains.

The FDE problem, solved properly
Right now §2.11 says "Nāgārjuna: FDE" but §6 has no FDE patterns. Here's what it needs:
lean-- In your Lean project: FoundationalTypes.lean

-- Four-valued logic (Priest 2010)
inductive FDEVal | T | F | B | N deriving DecidableEq, Repr

-- Negation (prasajya in FDE context)
def fde_neg : FDEVal → FDEVal
  | .T => .F | .F => .T | .B => .B | .N => .N

-- Conjunction
def fde_and : FDEVal → FDEVal → FDEVal
  | .T, v => v | v, .T => v
  | .F, _ => .F | _, .F => .F
  | .B, _ => .B | _, .B => .B
  | .N, .N => .N

-- The catuskoti: a proposition can have value in {T, F, B, N}
-- A catuṣkoṭi claim is an FDEVal-typed proposition
structure CatuskotiProp where
  content : Prop  -- the classical propositional content
  fde_val : FDEVal

-- Template for Nāgārjuna nodes (kāṇḍa 3):
-- Instead of: P : α → Prop
-- Use:        P : α → FDEVal
-- "proof" = showing which value obtains, not T/F
```

Now your §6 template table gets a new column `fde_mode : Bool` and FDE nodes use `CatuskotiProp` instead of `Prop`. The "proof" of a kāṇḍa 3 node is a construction of the appropriate `FDEVal`, not a classical proof. This is honest and machine-checkable.

---

### The complete revised §3.4 algorithm
```
INPUT: claim C with tradition T, anchor A

PRECONDITIONS:
  validation_set_pass_rate = 1.0 ∨ DEV_MODE
  
  STEP 0: SAYABILITY + KĀṆḌA ASSIGNMENT
    Is C a tautology/axiom for T? → kāṇḍa = 1, DEFINITION, skip to Step 5
    Is C logic_foundation = FDE?   → kāṇḍa = 3
    Is C circular (detected)?       → kāṇḍa = 3
    Otherwise:                       → kāṇḍa = 2
    Can you write a Lean type? NO  → UNSAYABLE, stop
  
  STEP 1: ANUVRTTI — CONTEXT INHERITANCE
    parent_node = nearest ancestor in same tradition
    delta_terms = terms in C not in parent_node.full_context
    Register delta_terms only (not full context)
    IF unregistered terms exist → human_review flag, pause
  
  STEP 2: LIBRARY CHECK (siddha lookup)
    Search: LeanSearch, Loogle, node DB by lean_type_hash
    MATCH in kāṇḍa 1 or kāṇḍa 2 (same tradition) → import, reuse_count++, DONE
    NO MATCH → continue
    NOTE: kāṇḍa 3 matches DO NOT import automatically — require human promotion
  
  STEP 3: NN PARSE → NNExpr TREE
    Layer 1 LLM produces NNExpr tree (constrained to Σ only)
    decomposition_source: commentary → secondary → llm (in priority order)
  
  STEP 4: TRS NORMALIZATION (template application)
    Apply §6 rewrite rules to NNExpr tree
    Conflict: SOI → exception (apavāda) template wins
    Conflict: DOI → dependent-term (para) template wins
    No template matches → OUTSIDE_FORMAL, stop
    Result: lean_type (unique normal form)
    Check: is this lean_type in siddha DB? → reuse
  
  STEP 5: PROOF STRATEGY
    kāṇḍa 1 / DEFINITION      → `axiom` declaration, PROVED
    kāṇḍa 2, structural        → select from {exact, apply, constructor, intro}
                                  based on lean_type shape
    kāṇḍa 3 / FDE             → construct FDEVal witness
  
  STEP 6: LEAN COMPILATION
    lake build + warningAsError
    SUCCESS (no sorry)  → PROVED
    FAILURE             → retry Step 4 with next applicable template (max 3x)
    FAIL ALL RETRIES    → PLACEHOLDER + human flag
  
  STEP 7: PROPAGATE (§3.5 unchanged) + UPDATE ANUVRTTI CHAIN
    Update parent node's full_context if new siddha proofs added
    Emit derivation trace as training example for Layer 1 LLM

What makes this unique in the literature
ProofBridge is the first framework to jointly learn representations for NL and FL theorem-proof pairs in a shared semantic space, enabling cross-modal retrieval of semantically relevant FL examples. arXiv That's for mathematics. Nobody has done this for philosophical Sanskrit.
Your system is the only one with:

Tradition-typed terms (same IAST, different types by tradition — no existing formalization does this)
Kāṇḍa-scoped visibility (siddha/asiddha as a formal property of your TRS, not just a naming convention)
Anuvrtti-compressed context inheritance in the node DB
FDE as a first-class proof target alongside classical Lean Prop
The §6 template system as a formally verified confluent TRS (checkable via Metatheory library)
SOI/DOI conflict resolution (Rajpopat's algorithm) as the template selection procedure

None of these exist in the autoformalization literature, which is entirely focused on mathematics. Current autoformalization efforts are limited to formal languages with substantial online corpora, predominantly contest-level mathematics — this risks over-specializing models to a narrow style of problems, neglecting the broader spectrum of reasoning. arXiv You're operating in exactly that neglected spectrum.

The one thing that could kill it
The gap between kāṇḍa assignments and anuvrtti compression is that your Layer 1 (NN parse → NNExpr) is still an LLM step. It's the only place where non-determinism enters. Everything else — template application, TRS normalization, Lean compilation — is deterministic and checkable.
The mitigation: constrain Layer 1 output to a formal grammar over Σ. Concretely, define a BNF for valid NNExpr strings and run the LLM output through a parser before it enters the TRS. If it parses, proceed. If not, reject and retry. This turns the LLM into a constrained string generator rather than a free-form generator, dramatically reducing garbage output. The parser is a 50-line Lean file. Write it first, before anything else in the implementation.