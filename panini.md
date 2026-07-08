# Pāṇini Architecture for Sanskrit Proof Engine

*Implementation: SCHEMA.md. This doc supplies the structural principles.*

---

That Pāṇini actually built — the structural principles
The Aṣṭādhyāyī isn't just a grammar. It's a complete formal derivation engine with a layered architecture that maps almost exactly onto what you need. Here are the specific principles and what they give you:
1. Separation of database from algorithm
Pāṇini cleverly separates the databases from the algorithm. The databases include the Śiva sūtra list, noun roots, verb roots, gender rules. The algorithm accesses the database and outlines the process for word and sentence generation. He introduced metalanguage aliases and macro-body concepts — called saṃjñā and adhikāra — to avoid repetitions. There were 91 aliases and 73 macro bodies. Code was written in generic and override blocks known as utsarga-apavāda. There was inheritance. There was superposition where one verb type inherits from another and overrides a few. There was bootstrapping where global objects are defined and contexts are referenced later. Medium
Your schema has this partially — §1 (saṃjñā), §2 (vidhi), §6 (templates) — but the utsarga-apavāda pattern (general → exception) is not formalized. More on this below.
2. Anuvrtti — rule inheritance by context telescoping
A later sūtra inherits part of the meaning or conditions from the previous sūtra without explicitly repeating it — ensuring consistency, brevity, and modular construction. Sūtras carry forward context using anuvrtti, just as functions in libraries share common structures. Medium
This is profound for your system. It means: a node doesn't need to repeat the entire context of its parent — it inherits it and overrides only what changes. Your schema currently has no anuvrtti-equivalent. Every node is fully specified. That's why it'll be verbose.
3. The siddha/asiddha principle — rule visibility and proof ordering
This is the most important one for your Lean problem. The siddha-kāṇḍa contains rules that are siddha — "having taken effect" — for any other rule in the whole grammar, meaning before being effective, a rule takes into consideration the possibility of application of other rules. The sequence of rules in the book does not matter in the derivational process. IndiaFacts
The asiddhakāṇḍa (tripāḍī) begins with P.8.2.1 pūrvatrasiddham — "from now on every rule is regarded as not having taken effect with reference to preceding ones." Rules in the asiddhakāṇḍa must apply in the same sequence in which they are stated. IndiaFacts
In formal terms, from Kiparsky: rule A is asiddha with respect to rule B if and only if the result is identical to the result of applying A and B to φ simultaneously, and distinct from the result of applying them in the opposite order. The siddha-principle is a default principle which can be defeated at cost. ResearchGate
Translation for your system: this is a staged proof architecture — some derivations are globally visible (siddha, any order), others are strictly sequenced (asiddha, fixed order). This maps directly onto Lean's axiom vs theorem distinction.
4. Conflict resolution — Rajpopat's 2022 solution
The new classification: Same Operand Interaction (SOI) — the more specific (exception) rule wins; Different Operand Interaction (DOI) — the right-hand side (para) operation prevails (vipratiṣedhe paraṁ kāryam). This interpretation, where "para" means "right-hand side" rather than "later in serial order," produces grammatically correct outputs without exceptions. Cam
For your system: SOI = two templates applicable to the same NN sub-expression → specificity wins. DOI = two templates applicable to different operands in the same claim → the rightmost/dependent term's template wins.
5. Paribhāṣā — metarules that constrain rule application
Metarules constrain the application of other rules throughout the grammar. Headings supply a common element for a group of rules and must be read into every rule in their domain unless semantically incompatible. The grammar is formally open-ended for category and operational rule formation, but limited by the goal of characterising existing Sanskrit. Bhavana
Your §0 (Paribhāṣā) exists but is thin. It should contain the metarules for your system — the principles that govern how templates interact, not just the templates themselves.

The complete algorithm: Sanskrit → Lean proof, Pāṇini-style
Here's what your system should look like once restructured with these principles. This is the unique design.
ARCHITECTURE: Three-kāṇḍa system

KĀṆḌA 1 — SIDDHA (globally visible, any order)
  Anchors (immutable, §2.1)
  Term registry (saṃjñā)
  Tradition-scoped axiom nodes (always PROVED by stipulation)
  All DEFINITION nodes from Pāṇini layer (§10)

KĀṆḌA 2 — VIDHI (operational, dependency-ordered)
  NN operator templates (§6) as rewrite rules
  Each node: inherits parent context via anuvrtti
  Only specifies DELTA from parent, not full re-statement
  Conflict resolution: SOI → specificity; DOI → dependent term wins

KĀṆḌA 3 — ASIDDHA / TRIPĀḌĪ (strictly sequenced, local only)
  FDE nodes (Nāgārjuna)
  Circularity-detected nodes
  Abhāva chains
  These are invisible to Kāṇḍa 1 rules — they cannot bleed global proofs
The Lean derivation algorithm proper:
INPUT: Sanskrit claim C with anchor A[tradition]

PHASE 0: PARIBHĀṢĀ CHECK
  Is C sayable? (§3.1) 
  → NO: UNSAYABLE, stop
  → YES: assign logic_foundation from tradition

PHASE 1: SAṂJÑĀ LOOKUP
  Resolve all terms against registry
  Apply anuvrtti: inherit parent node's context
  Only register DELTA terms

PHASE 2: UTSARGA-APAVĀDA MATCH
  Find applicable §6 templates
  IF SOI conflict: apavāda (exception template) wins
  IF DOI conflict: dependent-term template wins (para rule)
  → Exactly ONE template selected, or OUTSIDE_FORMAL

PHASE 3: SIDDHA CHECK
  Is this claim's Lean type already siddha (in PROVED DB)?
  → YES: import, reuse_count++, done
  → NO: proceed

PHASE 4: LEAN TYPE CONSTRUCTION
  Apply selected template → lean_type
  All dependencies MUST be siddha (Kāṇḍa 1 or already PROVED Kāṇḍa 2)
  asiddha nodes (Kāṇḍa 3) CANNOT be dependencies of Kāṇḍa 1/2 nodes

PHASE 5: PROOF STRATEGY
  Type = DEFINITION: axiom keyword, no proof required, PROVED
  Type = structural derivation: `exact`, `apply`, `constructor` tactics
  Type = vyāpti: `intro x; exact h x` pattern
  Type = FDE: custom FDEVal evaluator (not classical Lean Prop)
  No `sorry` except PLACEHOLDER

PHASE 6: PROPAGATION (§3.5, unchanged)

What makes this system unique
Three things no existing system does:
1. Anuvrtti-compressed nodes. Instead of each node re-stating full context, you store only the delta. A node representing anumāna in a Dharmakīrti derivation inherits the whole epistemological context from its parent pramāṇa node and only specifies what changes. This is compression + correctness, not just brevity. In the DB schema: add inherited_context: node_id | NULL and delta_only: BOOL to §4.1.
2. Kāṇḍa-scoped proof visibility. The siddha/asiddha split solves your circular-dependency and FDE contamination problems cleanly. FDE nodes (Kāṇḍa 3) are by rule invisible to classical nodes (Kāṇḍa 1/2) — they cannot bleed into global proofs. You no longer need ad hoc cycle detection; it falls out of the architecture. This also means inter-tradition bridges (§4.6) can only form between nodes in the same kāṇḍa, or from Kāṇḍa 3 upward via explicit human-confirmed promotion — never automatically.
3. Utsarga-apavāda template conflict resolution. Right now your §6 template selection is unspecified — you assume exactly one template matches. It doesn't, in practice. The Pāṇinian SOI/DOI distinction (Rajpopat 2022) gives you a decision procedure: if two templates compete on the same NN sub-expression, the more specific (exception) wins; if they compete on different sub-expressions, the dependent term's template wins. This is the missing piece between "select template" and "generate lean_type" in §3.4.

The Lean proof gap, now solved properly
The insight from the Pāṇinian architecture: proofs don't get generated — they get derived step by step through template application, with each step either being a stipulated axiom (siddha) or a structural consequence (vidhi). The LLM never touches proof generation. It does only:

Sayability check
Term registry lookup (saṃjñā)
Anuvrtti context inheritance
Template selection (with SOI/DOI conflict resolution)
Kāṇḍa assignment

Lean does steps 4→5 validation. Humans do semantic faithfulness. That's the complete division of labor.
The philosophical claims that can't be proved formally don't fail the system — they just live in Kāṇḍa 3 (asiddha, sequenced, isolated) or resolve to axiom in Kāṇḍa 1. The system is complete because it has a principled place for every type of claim, not because it proves everything.

What to add to §0 Paribhāṣā now
P.0.5  Anuvrtti: node inherits parent context; only delta registered
P.0.6  Kāṇḍa assignment: Kāṇḍa 1 (siddha/axiom), 
                          Kāṇḍa 2 (vidhi/derivational), 
                          Kāṇḍa 3 (asiddha/FDE/circular)
P.0.7  Kāṇḍa 3 invisible to Kāṇḍa 1; bridges require human promotion
P.0.8  Template conflict: SOI → apavāda wins; DOI → para (dependent) wins
P.0.9  Axiom nodes are siddha by stipulation; no proof required
P.0.10 Termination: no rule application shall cause asiddhatva 
        (infinite loop); detect and HOLLOW
That's the whole thing. Pāṇini solved your architecture problem 2,400 years ago. You're just implementing it in Lean 4.