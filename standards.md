These are the right questions to ask before building anything. Let me think through them precisely.
The core problem you've identified
A "statement" in natural language doesn't map cleanly to a node. One sentence can contain three claimable propositions. One paragraph can be one claim with supporting evidence. And Dharmakīrti writes in compressed verse (kārikā) where a single line has been debated for 1000 years. Chunking by sentence/verse is wrong. Chunking by paragraph is wrong. You need a semantic unit, not a syntactic one.
What a node actually is
The cleanest definition: a node is the smallest unit that can independently have a truth value. Not "Dharmakīrti says X" — that's a historical claim. Not "perception is valid" — that's too vague to prove or falsify. The right unit:
A node = a proposition P such that:
  1. P makes a falsifiable claim
  2. P has identifiable truth conditions
  3. P cannot be split into two independent falsifiable sub-claims
     without losing meaning
Test: can you write a Lean type for it? If yes, it's a node. If the Lean type requires two → that don't depend on each other, it's two nodes.
For Dharmakīrti specifically
His Pramāṇavārttika is structured as: root kārikā (verse) + auto-commentary (svavṛtti) + later commentaries (Dharmottara etc.). The kārikās are the claims. The commentaries are the decomposition he already did. You don't need to decide the chunking — he already chunked it. Each kārikā = one candidate node. The svavṛtti = his own decomposition of it into sub-claims.
So the pipeline for Dharmakīrti is actually:
kārikā verse → candidate node (his claim)
svavṛtti → his decomposition (child nodes, already done)
your engine → formalize + prove/classify each
This is not true for all texts. Nāgārjuna's MMK has no auto-commentary. Abhinavagupta's TA is continuous prose mixed with verse. Dharmakīrti is the easiest precisely because the structure is pre-given.
The epistemological framework question
You don't need a universal theory of "what counts as a statement." You need a rejection criterion. Run the sayability check:
Can I write this as "it is not the case that P" such that
the negation is coherent and has identifiable consequences?

YES → P is a node candidate
NO  → P is not a node (UNSAYABLE, return to human)
The grey areas you're worried about mostly resolve under this. "Consciousness is self-luminous" — can I say "consciousness is NOT self-luminous"? Yes, and it has consequences (different theory of cognition). Node. "Śiva is the ground of being" — can I say "Śiva is NOT the ground of being"? In Abhinavagupta's system this is incoherent because Śiva is defined as the ground. Not falsifiable within the system. HOLLOW (definitional, not empirical).
The editing/versioning problem
This is the most important practical issue. Your worry: you run 500 nodes, then want to edit the decomposition logic or the Lean formalization scheme, and now everything is inconsistent.
Solution: separate the immutable from the mutable in the schema.
pythonNode:
  # IMMUTABLE — never change after creation
  id: int (permanent)
  source_text: str (exact original Sanskrit/IAST)
  source_ref: str (PV 1.3, exact)
  created_at: datetime
  
  # VERSIONED — can change, tracked
  version: int
  statement: str (your English formulation)
  node_type: ...
  status: ...
  lean_type: str
  lean_proof: str
  updated_at: datetime
  
  # AUDIT — what changed and why
  edit_history: json [{version, field, old, new, reason, timestamp}]
```

The source_text never changes — it's the anchor. Your interpretation of it (statement, lean_type, status) is versioned. When you want to change the formalization of vimarśa across 50 nodes, you write a migration: `UPDATE nodes SET version = version+1, lean_type = ... WHERE lean_type LIKE '%vimarsa%'`, logged in edit_history.

**The standardisation question — what you actually need to define up front**

Before running any text, you need exactly three decisions locked in:

**1. Granularity convention per text type**
```
kārikā text (PV, MMK): one kārikā = one candidate node
sūtra text (NS, SS): one sūtra = one candidate node  
prose commentary: one sentence making a distinct claim = one candidate node
TA verse: one śloka = one candidate node
```

Not perfect but consistent. Decomposition handles cases where one kārikā contains multiple claims — they become children, the kārikā node becomes PARTIAL or a container.

**2. Statement normalisation format**

Every node's `statement` field follows the same template:
```
"{Subject} {copula/relation} {predicate}"
with subject and predicate drawn from the text's own vocabulary (IAST)
translated to English only when necessary

Examples:
"pratyakṣa (perception) yields particulars (svalakṣaṇa) not universals"
"Valid cognition (pramāṇa) is defined by causal efficacy (arthakriyā)"
"śūnyatā applies to śūnyatā itself"
3. Tradition register
Every node gets a tradition field that scopes the axioms. What counts as DEFINITION vs EMPIRICAL differs by tradition. "ātman exists" is DEFINITION in Nyāya, UNPROVED in Buddhist, HOLLOW in Madhyamaka. The tradition field makes this explicit rather than hiding it.