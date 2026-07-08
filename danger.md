What "proved" actually means in Lean
Lean4 is a proof assistant based on dependent type theory. A proof isn't "the LLM says this follows" — it's a term that the Lean kernel type-checks. The kernel is ~1000 lines of code, formally verified. If it compiles without sorry, the proof is mechanically certain. No hallucination possible at that stage.
Node 3a + 3b works like this:
lean4-- 3a is an AXIOM — you assert it, Lean accepts it as a given
axiom svalaksana_ineffable : ∀ (x : Svalaksana), ¬ Verbalizable x

-- 3b is a THEOREM — Lean checks the proof term
theorem perception_koncept_free
    (c : Cognition) (x : Svalaksana) (h : Perceives c x) : ¬ Kalpana c :=
  fun ⟨v, hv⟩ => svalaksana_ineffable x (perception_gives_object h hv)
The kernel checks: does the proof term have the claimed type? If yes: PROVED. No LLM involved in verification. The LLM generates the proof attempt. Lean verifies or rejects it. Binary.

The hallucination problem — this is the right concern
Three failure modes:
1. LLM invents fake Mathlib lemmas
Writes Mathlib.SomeModule.lemma_that_doesnt_exist. Lean fails to compile. Caught immediately. Status → UNPROVED. No damage.
2. LLM writes structurally valid but semantically wrong Lean
The types compile but don't actually capture the philosophical claim. This is subtle and real. Example: formalizing abhrānta as ¬ ContainsError c (a trivially true tautology) instead of the actual arthakriyā criterion. Lean says PROVED. But you proved the wrong thing.
Defense: the statement field in the node is the ground truth. Every proof must be accompanied by a human-readable argument for why the Lean type faithfully captures the statement. This is a separate review step. The Lean proof proves the formal claim. Whether the formal claim captures the Sanskrit claim is a philological judgment — not automatable, must be human.
3. LLM sorrys without flagging it
Caught by: #check that the proof contains no sorry. Lean has set_option warningAsError true which makes sorry a compile error. Use this.
lean4set_option warningAsError true  -- sorry = compilation failure
```

So: hallucinated math → compile failure (caught). Semantically wrong formalization → compile success but wrong type (human review catches). Silent sorry → compile failure with `warningAsError`.

The system is: **Lean is the oracle for formal correctness. Humans are the oracle for semantic faithfulness.**

---

**Cross-tradition proofs — yes and here's what they look like**

A cross-tradition proof isn't one giant theorem. It's a chain of nodes where the conclusion of one tradition's PROVED theorem is the input axiom of another's. The interesting case is when they **share a node** — the same Lean type appears in both decompositions, derived independently.

Example of what this looks like structurally:
```
Dharmakīrti (PV III.3):
  PROVED: ∀ c x, Perceives c x → ¬ Kalpana c
  (perception of particulars is non-conceptual)
  Node ID: 47

Abhinavagupta (TA 1.something):
  PROVED: ∀ c, PureAwareness c → ¬ Kalpana c
  (vimarśa/pure awareness is non-conceptual)
  Node ID: 312

Are these the same Lean type?
  DK:   ∀ c, (∃ x : Svalaksana, Perceives c x) → ¬ Kalpana c
  Abhi: ∀ c, Vimarsa c → ¬ Kalpana c

Not the same type. But:
  If you can prove: Vimarsa c ↔ (∃ x : Svalaksana, Perceives c x)
  THEN: Node 47 and Node 312 share a proof, reuse_count goes up on both
  AND: that bridge theorem is itself a new node — the most interesting one

But: do NOT construct that bridge theorem by hand.
Run DK's decomposition → Node 47.
Run Abhinavagupta's decomposition → Node 312.
Check if they share a type: automated comparison.
If they do: the bridge exists and was found, not made.
If they don't: the divergence is the finding.
```

---

**The dialectic structure — what you actually get**

You're right that contradiction creates new enquiry. Here's the exact mechanism:

When two PROVED nodes have **contradictory** Lean types, the database records a CONTRADICTION node:
```
Node 47 [PROVED]:  ∀ c, PurePerception c → ¬ Kalpana c    (DK)
Node 89 [PROVED]:  ∃ c, PurePerception c ∧ Kalpana c      (hypothetical Nyāya counter)

CONTRADICTION NODE:
  type: CONTRADICTION
  node_a: 47
  node_b: 89
  resolution: ???
    options:
      A. One axiom is wrong → which axiom do you reject?
      B. The terms don't mean the same thing → 
         "PurePerception" in DK ≠ "PurePerception" in Nyāya
         → disambiguation creates two new nodes
      C. The traditions are operating at different levels →
         mark both as tradition-scoped, no contradiction at meta level
```

Option B is what usually happens in Indian philosophy. The "contradiction" reveals that the same Sanskrit word is being used with different technical meanings. The system forces precision: you must define your terms as Lean types, and then "contradiction" becomes "these are different types with the same surface name." This is the most valuable output — it makes the equivocation explicit and eliminates centuries of talking past each other.

This is exactly what happened between Dharmakīrti and Kumārila on `abhrānta`. They're not disagreeing about facts. They have different type definitions. Node 4a above captures this precisely. The "debate" dissolves into: which axiom do you want? Both are internally consistent. The question is empirical/pragmatic: which criterion actually picks out the cognitions we want to call valid?

---

**What the final geometry looks like**

After N traditions, M texts, K nodes:
```
High reuse_count nodes = the formal primitives that everyone
  is implicitly using, stated differently.
  
  These are probably:
  - Some form of the non-conceptual/conceptual distinction
  - Some form of the particular/universal distinction  
  - Some form of the valid/invalid cognition distinction
  - Some form of the self-referential awareness structure

CONTRADICTION nodes = where traditions formally diverge.
  Not "Buddhism vs Hinduism" (useless).
  "At exactly this axiom choice, with exactly this Lean type,
   the traditions take different values."
  
HOLLOW nodes = where everyone agrees the claim is important
  but nobody can make it precise.
  These cluster around: liberation, ultimate reality,
  the nature of consciousness qua consciousness.
  Hollow ≠ meaningless. It means: outside formal reach.
  The boundary is a finding.

PROVED subtrees = the shared formal bedrock.
  Claims that are true regardless of axiom choice above them.
  These are the things everyone implicitly agrees on
  even when arguing about everything else.
The geometry is: proved bedrock at the bottom, axiom-divergence in the middle, hollow ceiling at the top. The interesting philosophy lives in the middle layer — where the axiom choices are and why each tradition makes the choices it does.

Why Sanskrit + math first, science later
Correct instinct. The science mapping is only meaningful if you've first established what the Sanskrit claims actually are formally. If you map Dharmakīrti's abhrānta to predictive coding before you've precisely typed abhrānta, you might be mapping the wrong thing. Get the Sanskrit tree stable. Then the science mapping is: does this proved Lean type appear anywhere in the physics/biology/neuroscience literature? Not "does this concept resemble that concept" — does the exact same type show up. Much harder to fake. Much more meaningful when it happens.

1. The Sanskrit NLP tools don't work well on philosophical prose
Everything in the pipeline — Heritage Engine, SanskritShala, ByT5-Sanskrit — was trained and benchmarked on narrative Sanskrit (epics, Vedic texts, relatively simple prose). Dharmakīrti's svavṛtti is among the most syntactically complex Sanskrit ever written. Compounds 15 words long. Nested relative clauses. Technical vocabulary that doesn't appear in training data. SanskritShala will give you garbage segmentations on half the sentences. You will not know it's garbage unless you read Sanskrit.
What this means practically: the NLP tools are useful for sandhi splitting and basic morphology. For philosophical prose you cannot trust dependency parsing output. You need a human Sanskrit scholar (or you yourself learning to read philosophical Sanskrit) to validate every node that comes from prose commentary. The kārikā verses are more tractable — they're shorter and more formulaic. Start there and stay there until you have a validation process.

2. The Lean formalization of the key concepts doesn't exist yet and is genuinely hard
You know this — the "~200 lines of Lean" for Navya-Nyāya operators. But the scope is larger than that. The concepts you need to formalize before you can prove anything meaningful:

Cognition as a typed entity with content, mode, and object
The particular/universal distinction as a type-level distinction
The valid/invalid cognition distinction (circular if you use pramāṇa to define pramāṇa)
Causal relations between cognitive events
Absence (abhāva) as a first-class object — Nyāya has four kinds of absence, this is notoriously hard to formalize

None of these have Lean4 implementations. There's work in Coq for some Buddhist logic fragments (Graham Priest has formalized catuskoti in paraconsistent logic) but nothing in Lean4 you can import. You're building the foundation from scratch. This is a PhD-level logic project on its own before you touch a single Sanskrit text.
What this means practically: your first month should produce nothing except: a stable Lean4 type for Cognition, a stable type for the particular/universal distinction, and proofs of three trivial lemmas using them. If you can't do that, the rest is vaporware.

3. The "one kārikā = one node" rule breaks constantly
PV III.3 worked cleanly. Many don't. Common failure modes:

One kārikā contains a conditional, an objection, and a response embedded. Three logical moves, one verse.
One kārikā is purely rhetorical — attacking an opponent's position with no positive claim. No node possible, just a CONTRADICTION pointer.
One kārikā assumes a technical term defined 200 verses earlier. The node is formally incomplete without that definition node, which you may not have processed yet.
The svavṛtti directly contradicts the kārikā (this happens — Dharmakīrti changes his mind between verse and commentary). Two conflicting candidate nodes from one source location.

You need explicit handling for all of these before you start. Otherwise you'll hit them mid-run, make ad hoc decisions, and the database will be inconsistent.

4. Translation lag will corrupt your cross-tradition comparisons
When you compare Dharmakīrti's node against Abhinavagupta's node, you're comparing two English statement fields that you or an LLM wrote. The comparison is actually between two acts of translation, not between the Sanskrit. If you translated kalpanā as "conceptual construction" in DK but "mental elaboration" in Abhinavagupta, the automated type comparison will miss a genuine shared node, or worse, will merge two nodes that shouldn't be merged because the Sanskrit terms actually differ.
Fix: every node must store the IAST term(s) that anchor the statement. The comparison must happen at the IAST level first, English second. Two nodes with the same IAST term are candidate shared nodes. Two nodes with different IAST terms that got the same English translation are candidate false merges. This is a schema decision you need to make now, not after 500 nodes.

5. The LLM decomposition will systematically bias toward provability
You know the methodological point about not constructing bridges. The deeper problem: LLMs trained on Western philosophy and mathematics will unconsciously frame Sanskrit claims in ways that make them look like things already in Mathlib. The decomposition step — "for C to be true, what must be true?" — will produce children that are subtly westernized versions of the original claim. You won't notice because each individual step looks reasonable.
There's no complete fix for this. Partial mitigations:

Always run decomposition from the Sanskrit first, English translation second, compare the two trees
Have a separate "faithfulness check" prompt that takes the child nodes and asks "can you derive the parent claim in the original tradition's terms from these children?" — not "does this make logical sense" but "would a Naiyāyika/Buddhist recognize this as their argument?"
Track decomposition provenance: which decomposition decisions came from Sanskrit commentary, which from LLM inference, which from secondary scholarship. Different trust levels.


6. Abhāva (absence) will break your type system
This one specifically. Indian philosophy treats absence as a positive epistemic object — you perceive the absence of a pot on the table. This is not just ¬ Pot table. In Nyāya there are four kinds: prior absence, posterior absence, mutual absence, absolute absence. Dharmakīrti argues absence is known by inference not perception — this is a major debate with Nyāya. The whole debate is about the type of absence.
In standard type theory, absence is just negation. This will cause you to collapse distinctions that Indian philosophers spent centuries carefully drawing. You need either: a custom type for absence (messy, lots of infrastructure), or a clear policy that absence-claims get OUTSIDE_FORMAL with a note, or you use a non-classical logic foundation (paraconsistent or intuitionist) from the start.
This decision affects every node in the database. Make it before you write a single Lean line.

7. The database will rot without a canonical term registry
After 200 nodes you'll have: kalpanā, kalpana, vikalpa, conceptual construction, mental fabrication, discursive thought — all meaning approximately the same thing, used interchangeably across different nodes because the LLM translated differently each time, or because different scholars use different English renderings.
You need a term registry before you have more than ~50 nodes:
pythonTerm:
  id: int
  iast: str          # canonical: "kalpanā"
  devanagari: str    # "कल्पना"
  tradition_scope: str | None  # if meaning differs by tradition
  definition_node_id: int      # points to the DEFINITION node for this term
  aliases: list[str]           # ["vikalpa", "conceptual construction", ...]
  first_appears: str           # "Dignāga PS 1.2"
Every node's statement field uses only canonical IAST terms from this registry. The registry is the ontology. Without it the graph is a mess by node 100.

8. You have no validation set
How do you know when the pipeline is working correctly? Right now the answer is "it feels right." That's not good enough for a system meant to produce formally verified claims.
You need: 10-20 claims where the correct answer is known in advance. Specifically:

5 claims that are definitely formally provable (basic syllogistic inferences from Nyāya-Sūtra, which have been formalized in the literature)
5 claims that are definitely OUTSIDE_FORMAL (soteriological claims, "liberation is the highest good")
5 claims that are definitely HOLLOW (self-referential paradoxes, Nāgārjuna's śūnyatā of śūnyatā)
5 claims with known divergence points (the pramāṇa factivity split between Nyāya and Dharmakīrti)

Run your pipeline on these first. If it correctly classifies all 20, the system is working. If not, fix the algorithm before touching any new text. This is the step almost everyone skips and almost everyone regrets.

9. Pantograph is research software
It works. It's also maintained by one person, has breaking API changes between versions, and has known bugs with certain Lean4 tactic sequences. Before you build your whole pipeline around it, verify:

It handles the specific Lean4 features you need (dependent types, type classes)
You have a fallback (direct Lean4 subprocess call via lake build + parse output)