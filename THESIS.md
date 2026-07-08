# Sanskrit Proof Engine: A Thesis

## Formal Derivation from Sanskrit Philosophical Texts to Machine-Verifiable Proofs

---

## 1. The Problem

Sanskrit philosophy—Nyāya, Buddhist epistemology, Kashmir Śaivism, Advaita Vedānta—contains some of the most precise formal reasoning ever written. Dharmakīrti’s *Pramāṇavārttika*, the Nyāya-Sūtras, Nāgārjuna’s *Mūlamadhyamakakārikā*: these texts make claims that are falsifiable, structured, and often close to modern logic. Yet they remain locked in natural language. We have no way to:

- **Verify** whether a claim follows from its premises
- **Compare** traditions at the level of formal structure, not translation
- **Locate** where formal content ends and empirical or unsayable content begins
- **Measure** translation quality by whether different renderings reach the same formal node

The usual approach—commentary, philology, hermeneutics—is irreplaceable. But it does not give us machine-checkable proofs. We want both: scholarly fidelity *and* formal verification.

---

## 2. What This Project Is

The **Sanskrit Proof Engine** is a **truth compressor**. It takes a Sanskrit philosophical claim and produces one of three outcomes:

1. **PROVED** — A Lean 4 type that compiles and is proved (or stipulated as axiom)
2. **OUTSIDE_FORMAL** — The claim is empirical; it needs evidence, not proof
3. **HOLLOW** — The claim is unfalsifiable; no well-typed formal expression exists for it

The goal is **honesty, not proofs**. When a claim does not support formalization, PARTIAL or OUTSIDE_FORMAL is the correct result. The boundary between what can and cannot be formalized is itself a finding.

The output is a **node graph**: each node is a claim with a status, a Lean type (when formalizable), and a traceable path to its justification. High-reuse nodes are formal primitives that appear across traditions. Divergence nodes are where traditions share structure but differ in axiom choice. The graph is the result.

---

## 3. Bhartṛhari and the Formal Structure Thesis

Bhartṛhari’s *Vākyapadīya* opens with *anādinidhanam brahma śabdatattvaṃ*—the word-principle (śabda-tattva) as beginningless, endless Brahman. For Bhartṛhari, śabda is not merely language about the world; it is the **primordial structuring principle**. The world is articulated through word; structure precedes and conditions what can be said and known. Abhinavagupta, in the Śaiva tradition, takes this further: *parāvāk* (the supreme word) is the first movement of Śiva-consciousness—the self-luminous awareness that articulates itself as world and language.

**Thesis:** Formalizing Sanskrit philosophical reasoning in type theory is not an arbitrary encoding. It is an attempt to **recover the formal structure** that the tradition takes to be built into reality. If śabda structures the knowable, then the formal invariants we extract—the centre nodes, the divergence points, the bridges—are candidates for that structure. The graph is a hypothesis about what that structure is.

---

## 4. Architecture

### 4.1 Hybrid Oracle System

We are not a complete formal system in the logician’s sense. We are a **hybrid oracle system**:

- **Lean 4** — Formal oracle: type-checks and proves. No `sorry`.
- **Human** — Semantic oracle: judges faithfulness to the source, resolves contradictions, promotes bridges.
- **LLM (Qwen 3.5)** — Decomposition oracle: sayability, template selection, decomposition. **Never** proof generation.

The LLM suggests structure; Lean verifies it. The human ensures we are not formalizing the wrong thing.

### 4.2 The Pipeline

```
Sanskrit (IAST) → Morphology (Heritage/ByT5) → NN Parse → Template TRS → Lean type → Prove or classify
```

For each claim:

1. **Sayability** — Can it be falsified? If not → HOLLOW.
2. **Library check** — Loogle, LeanSearch, local DB. Match → PROVED (reuse).
3. **Formalize** — Map to Lean type via templates (vyāpti, abheda, sambandha, etc.).
4. **Prove** — Pantograph / `lake build`. Success → PROVED. Sorry → UNPROVED (gap, not proved).
5. **Decompose** — If unproved, split into sub-claims. Recurse.
6. **Propagate** — Parent status from children (REFUTED → HOLLOW → PROVED → UNPROVED → PARTIAL).

### 4.3 Tradition-Scoped Terms

The same Sanskrit word in different traditions is a **different node**. *pramāṇa* in Nyāya (valid cognition as factive) ≠ *pramāṇa* in Dharmakīrti (defined via arthakriyā). A term registry stores `(iast, tradition) → tid`. Same IAST, different tradition → different formal type. This avoids false mergers and makes divergence explicit.

### 4.4 Kāṇḍa System (from Pāṇini)

- **Kāṇḍa 1 (siddha)** — Axioms, definitions. Globally visible. No proof required.
- **Kāṇḍa 2 (vidhi)** — Derivations. Dependency-ordered. Must prove or decompose.
- **Kāṇḍa 3 (asiddha)** — FDE nodes, circular definitions, abhāva. Invisible to Kāṇḍa 1. Human promotion required for bridges.

---

## 5. What We Have Built

### 5.1 Core Pipeline

- **Algorithm** — Seven-step process: sayability → anuvrtti → library → formalize → prove (with retry) → decompose → propagate.
- **Database** — Nodes, edges, terms, contradictions, bridge index, traces. SQLite with migrations.
- **Lean integration** — Pantograph, `lake env lean`, inlined Sanskrit axioms (Cognition, Svalaksana, Perceives, Kalpana).
- **Library check** — Loogle (type search), LeanSearch (NL search), local DB reuse.
- **Term registry** — Tradition-scoped. Bootstrap for Dharmakīrti and Nyāya.
- **Validation set** — Canonical pairs (e.g. pratyakṣa → ∀ c x, Perceives c x → ¬ Kalpana c). Gate: pass_rate = 1.0 or DEV_MODE.
- **Trace emission** — On PROVED, write to traces table (anchor, tradition, layers, metadata).
- **Retry policy** — Up to 3 attempts on Lean failure; then human_review flag.

### 5.2 Phase 1: Dharmakīrti

- **Text** — Pramāṇavārttika III (pratyakṣa chapter).
- **Terms** — pratyakṣa, kalpanā, svalakṣaṇa, arthakriyā, pramāṇa.
- **Definitions** — pratyakṣa, kalpanā, svalakṣaṇa as DEFINITION (Kāṇḍa 1, PROVED by stipulation).
- **Run** — `python run_dharmakirti.py --full` or `python run_pv3.py` for a single kārikā.

### 5.3 Phase 1: Nyāya

- **Terms** — pramāṇa, saṃśaya, vyāpti, anumāna, nigrahasthāna.
- **Structure** — Same pipeline, Nyāya-specific templates.

### 5.4 LLM Integration

- **Qwen 3.5** (Chutes API) — Single call for sayability + formalization + decomposition.
- **Agent mode** — `python run_dharmakirti.py --agent` for autonomous runs.

### 5.5 BNF Grammar

- **NNExpr** — Parser for Navya-Nyāya expressions (TID_N[Trad], vyāpti(a,b), abheda, etc.). Gate for LLM output.

---

## 6. The Vision

### 6.1 The Graph as Finding

After many runs across traditions and texts:

- **Centre nodes** (high reuse_count) = formal primitives that appear across Nyāya, Buddhist, Śaiva, Vedānta. Not declared; discovered.
- **Boundary nodes** (OUTSIDE_FORMAL leaves) = precise map of where each tradition’s formal content ends.
- **Divergence nodes** (DEFINITION/AXIOM) = where traditions share structure but differ in commitment. Not “they disagree” but “they disagree at exactly this axiom, and here is its formal statement.”
- **Bridges** = same Lean type from independent decomposition. Found, not constructed.

### 5.2 Cross-Tradition Combat Map

The intellectual network is explicit: Dharmakīrti vs. Kumārila on intrinsic validity; Dharmakīrti vs. Uddyotakara on ātman; Utpaladeva using Dharmakīrti’s tools against him; Abhinavagupta engaging Bhartṛhari. Each polemical engagement is a divergence node. The graph records where and how traditions formally part ways.

### 6.3 Translation Quality

Steps to shared node = measurable translation fidelity. Two translations of the same Sanskrit that reach the same Lean type are semantically faithful. Divergence in the graph shows where translation introduces or loses formal content.

### 6.4 The Boundary Is the Result

We do not aim to prove everything. We aim to be precise about what can and cannot be proved. HOLLOW and OUTSIDE_FORMAL are correct when the text does not support formalization. The boundary between formal and non-formal is the finding.

### 6.5 Bootstrap: Tarkasaṃgraha and the Five-Stage Sequence

Our **bootstrap text** is Annambhaṭṭa’s *Tarkasaṃgraha*—not the Nyāya-Sūtras or Dharmakīrti directly. The Tarkasaṃgraha compresses Nyāya-Vaiśeṣika into a compact primer. Formalizing it first gives us a stable padārtha layer that epistemology and consciousness claims can build on.

**Stage 1: Padārtha** — The seven Vaiśeṣika categories (dravya, guṇa, karma, sāmānya, viśeṣa, samavāya, abhāva). Kāṇḍa 1 axioms. The ontology that all later claims presuppose.

**Stage 2: Sambandha, samavāya** — Relations and inherence. Śrīharṣa’s circularity objection (samavāya defined via sambandha, sambandha via samavāya) is a **formal question**: can we break the cycle in type theory, or does it force a Kāṇḍa 3 node?

**Stage 3: Pramāṇa** — Epistemology. Nyāya (valid cognition as factive) vs. Dharmakīrti (arthakriyā, svalakṣaṇa). Divergence nodes here.

**Stage 4: Utpaladeva’s bridge** — *Ajadapramātṛsiddhi* and related arguments. Utpaladeva uses Dharmakīrti’s tools (inference, pratyakṣa) to argue for a conscious knower. Bridges and divergences with Buddhist epistemology.

**Stage 5: Śaiva consciousness** — cit, svaprakāśa, spanda. Defined **relative to the graph**: these terms get formal types only insofar as they connect to the padārtha and pramāṇa layers. The graph records where Śaiva claims extend, diverge, or bridge.

### 6.6 The Empirical Question

Does the formal structure of Sanskrit reasoning about consciousness match the formal structure of physical theories of consciousness? Phase 3 (scientific crossover) is the experiment: take PROVED formal components as hypotheses, search scientific literature for isomorphic structure, compare node IDs. Convergence and non-convergence are both findings.

---

## 7. What We Do Not Do

- **We do not bias toward provability.** Decomposition follows the source. If no proof emerges, that is the answer.
- **We do not construct bridges.** We find them when independent decompositions share a type.
- **We do not translate.** We map formal content. Heritage/ByT5 handle morphology.
- **We do not let the LLM prove.** The LLM decomposes and selects templates; Lean proves.
- **We do not hide gaps.** No PLACEHOLDER. Sorry in Lean → UNPROVED. Gaps are explicit.

---

## 8. Roadmap

The intended **foundational phase** is Tarkasaṃgraha (padārtha). Current implementation targets Dharmakīrti and Nyāya first for pipeline validation; Tarkasaṃgraha is the planned bootstrap.

1. **Tarkasaṃgraha (padārtha)** — Bootstrap. Seven Vaiśeṣika categories, sambandha, samavāya. Kāṇḍa 1 axioms. Foundation for all later stages.
2. **Nyāya-Sūtras / Dharmakīrti (epistemology)** — Pramāṇa, pratyakṣa, anumāna. Current focus: Dharmakīrti PV III. Definitions PROVED; structural claims UNPROVED until Lean foundation expands. Nyāya-Sūtras as validation corpus.
3. **Utpaladeva (bridge)** — Ajadapramātṛsiddhi. Uses Dharmakīrti’s tools to argue for conscious knower. Bridges and divergences with Buddhist epistemology.
4. **Śaiva consciousness** — Shiva Sūtras, Tantrāloka, Abhinavagupta. cit, svaprakāśa, spanda. Defined relative to the graph.
5. **Nāgārjuna (MMK)** — FDE layer for catuskoṭi. Kāṇḍa 3.
6. **Cross-tradition bridges** — When Dharmakīrti and Abhinavagupta (or Nyāya and Buddhist) reach the same Lean type independently, record the bridge.
7. **Scientific crossover (Phase 3)** — Take PROVED formal components as hypotheses; search scientific literature for same structure; compare node IDs. **Empirical question:** Does the formal structure of Sanskrit reasoning about consciousness match the formal structure of physical theories of consciousness? Convergence and non-convergence are both findings.

---

## 9. Conclusion

The Sanskrit Proof Engine is a machine-verifiable pipeline from Sanskrit philosophical claims to Lean 4 types and proofs. It is honest about boundaries, tradition-scoped in its terms, and designed to surface formal primitives and divergence points across a 1500-year intellectual network. The graph that results—with its centre nodes, boundaries, and bridges—is the output. It is the most precise analysis of Sanskrit philosophical claims yet produced, and the structure of the graph is the finding.

---

*Sanskritree Project. Schema v3. 2025.*
