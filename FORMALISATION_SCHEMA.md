# Formalisation Schema

Aligned with Kleiner & Tull (arXiv:2002.07655), Kleiner (arXiv:1907.03223), PyPhi, IIT 4.0, and Dharmakīrti (SEP). This schema ensures consistency when building on their work.

---

## 1. Kleiner & Tull — Categorisation Approach

### 1.1 Two-Domain Structure

IIT is a **map** between two classes:

```
Sys ──E──> Exp
```

- **Sys** (system class): physical systems and their states
- **Exp** (experience class): spaces of conscious experience
- **E**: for each S ∈ Sys, E(S) = experience space; for each s ∈ St(S), E(S,s) = actual experience

### 1.2 System Class (Definition 1)

Each S ∈ Sys has:

| Component | Kleiner & Tull | Our mapping |
|-----------|----------------|-------------|
| States | St(S) | `Substrate → State` |
| Subsystems | Subs(S) ⊂ Sys, s\|M ∈ St(M) | `Composition`, `Hierarchy` |
| Decompositions | DS, trivial 1 ∈ DS | `Finset.partition`, `Set.partition` |
| Cuts | S^z, s^z for z ∈ DS | Cut system = system with modified dynamics |
| Empty system | I ∈ Sub(S) ∀S | Unit / trivial substrate |

**Constraint**: Subs(S) ≃ Subs(S') for all states; Subs(S) ≃ Subs(S^z) for all cuts.

### 1.3 Experience Space (Definition 2)

E has:

| Component | Signature | Notes |
|-----------|-----------|-------|
| Intensity | \|\|·\|\| : E → ℝ⁺ | Φ = \|\|E(S,s)\|\| |
| Distance | d : E × E → ℝ⁺ | For integration level |
| Scalar multiplication | ℝ⁺ × E → E | r·e, \|\|r·e\|\| = r·\|\|e\|\| |

**Product** (Definition 4): E × F with d((e,f),(e',f')) = d(e,e') + d(f,f').

### 1.4 Decomposition (Definition 5)

A **decomposition of e over D** is a map ē : D → E with ē(1) = e.

### 1.5 Cause-Effect Repertoire (Definition 6)

For S, s, M, P ∈ Subs(S):

- **Proto-experience space** PE(S)
- **caus_s(M,P)**, **eff_s(M,P)** ∈ PE(S)
- Each has decomposition over D_M,P = D_M × D_P

**Cause-effect structure** (Definition 7): specification for every S, with PE(S) = PE(S^z).

### 1.6 Integration (Definition 8)

- **Integration level**: φ(e) = min_{z≠1} d(e, ē(z))
- **Integration scaling**: ι(e) = φ(e) · ê (normalised e)
- **Core**: subsystem C where φ(e_C) is maximal
- **Concept** (mechanism level): CS,s(M) = core integration scaling of (caus(M), eff(M))
- **Q-shape**: Qs(S) = (CS,s(M))_{M ∈ Subs(S)}
- **Actual experience**: E(S,s) = core integration scaling of Q(S,s)
- **Φ(S,s)** = \|\|E(S,s)\|\| (quantity)
- **Quality** = ê(S,s)

### 1.7 Classical IIT (Section 9)

- **States**: St(S) = St(S1) × ... × St(Sn), T : P(S) → P(S)
- **Conditional independence**: T(p) = ∏ᵢ Tᵢ(p)
- **Subsystems**: subset M of elements, T_M = ⟨M⊥|T|s_M⊥⟩
- **Decompositions**: partitions z = (M, M⊥)
- **Cut**: T^(M,M⊥) replaces edges M⊥→M with uniform noise
- **Proto-experiences**: PE(S) = P(S) with Wasserstein metric
- **Cause repertoire**: (27), (28), (29) — conditioning, product, unconstrained extension
- **Effect repertoire**: (25), (26), (29) — marginalization, product, extension

---

## 2. PyPhi — Executable Structure

### 2.1 Core Objects

| PyPhi | Our primitive | Notes |
|-------|---------------|-------|
| `Network(tpm, cm)` | TPM + connectivity | Transition probability matrix |
| `Subsystem(network, state, node_indices)` | Substrate + state | Mechanism/purview |
| `phi(subsystem)` | Φ value | Integration level |
| `sia(subsystem)` | SystemIrreducibilityAnalysis | Full cause-effect structure |
| `Concept` | Concept (mechanism level) | cause + effect at core purview |

### 2.2 Conventions

- **TPM**: state-by-node form, shape (2^n, n) for n nodes
- **Connectivity matrix**: cm[i,j]=1 iff edge i→j
- **State**: n-tuple of node states

### 2.3 Validation

**Oracle**: Feed PyPhi a TPM → get Φ, concepts, cause-effect repertoires. Our Lean `Integration` primitive must match the *structure* PyPhi computes (partition-based irreducibility), not the numerical value.

---

## 3. Dharmakīrti — Conceptual Structure (SEP)

### 3.1 Existence Criterion

| Term | Definition | Our primitive |
|------|------------|---------------|
| **arthakriyā** | Causal efficacy | CausalPower |
| **arthakriyāsamartha** | Having causal powers | CausalPower |
| **paramārthasat** | Really exists | CausalPower → Real |
| **saṃvṛtisat** | Customarily existent | Fictional / conceptual |

**Axiom**: x exists iff x has causal efficacy (arthakriyā).

### 3.2 Epistemic Structure

| Term | Definition | Our primitive |
|------|------------|---------------|
| **svalakṣaṇa** | Particular, ineffable | Particularity |
| **sāmānyalakṣaṇa** | Universal, fictional | — (excluded) |
| **pramāṇa** | Reliable cognition | Normativity |
| **pratyakṣa** | Perception | Direct, non-conceptual |
| **anumāna** | Inference | Conceptual, via vyāpti |

### 3.3 Causal Theory of Properties

- **svabhāvapratibandha**: connection by essential natures
- **avinābhāvaniyama**: nexus where effect cannot be without cause
- **anvaya** (co-presence), **vyatireka** (co-absence): inductive method

### 3.4 Formalisation Hooks

- `CausalPower` ↔ arthakriyā
- `Particularity` ↔ svalakṣaṇa
- `Normativity` ↔ pramāṇa (avisaṃvādin)  
- `∀ x, Real x → Particular x` (only particulars are real)
- `∀ x, Real x → CausalPower x` (real = causally efficacious)

---

## 4. GWT / Dehaene et al.

| PyPhi/IIT | GWT | Our primitive |
|-----------|-----|----------------|
| Mechanism | Representation | — |
| Purview | Specialist modules | — |
| Broadcast | Global availability | Broadcast |
| Competition | Selection for access | — |
| Threshold | Activation | Threshold |
| Accessibility | Readable by | Accessibility |

**Formal**: Long-distance connectivity = graph reachability; broadcast = reachability from winner to all modules.

---

## 5. Free Energy Principle (Buckley et al. 2017)

- **Statistical model**: brain as model of world
- **Synchronization**: perception (world→agent), action (agent→world)
- **Primitives**: Prediction error, variational inference, free energy

---

## 6. Cross-Reference Table

| Our primitive | Kleiner & Tull | PyPhi | Dharmakīrti | IIT 4.0 |
|---------------|----------------|-------|-------------|---------|
| Substrate | S ∈ Sys | Network | — | Substrate |
| CausalPower | caus, eff repertoires | Causal structure | arthakriyā | Cause-effect |
| Integration | φ(e), ι(e) | phi | — | Φ (postulate 2) |
| Composition | Subs(S) | Subsystem | — | Composition |
| Exclusion | Core, major complex | Maximal | — | Exclusion |
| Particularity | — | — | svalakṣaṇa | Intrinsicality |
| Broadcast | — | — | — | GWT |
| Threshold | — | — | — | GWT |
| Normativity | — | — | pramāṇa | — |

---

## 7. Consistency Rules

1. **IIT claims** must decompose to Kleiner & Tull structures: Sys, St, Subs, DS, cause-effect repertoire, φ, integration scaling, core.
2. **Dharmakīrti claims** must use arthakriyā → CausalPower, svalakṣaṇa → Particularity.
3. **Primitive definitions** must match source: e.g. Integration = "no partition preserves cause-effect structure" (Kleiner & Tull Def 8).
4. **PyPhi** is the oracle for IIT: numerical validation of Integration/Φ structure.
5. **PhysLean** checked before building: CausalOrder, ShannonEntropy, etc.

---

## 8. Lean Type Mappings (from schema)

```lean
-- Kleiner & Tull: System
structure System where
  stateSpace : Type
  subsystems : stateSpace → Set System
  decompositions : Set (Partition stateSpace)

-- Experience space (Def 2)
structure ExperienceSpace where
  carrier : Type
  intensity : carrier → ℝ
  distance : carrier → carrier → ℝ
  scale : ℝ → carrier → carrier

-- Integration (Def 8)
def integrationLevel (e : E) (decomp : D → E) : ℝ :=
  min (d e (decomp z)) over z ≠ 1

-- Dharmakīrti
def Arthakriya (x : Type) : Prop := CausalPower x
def Real (x : Type) : Prop := Particular x ∧ CausalPower x
```

---

## 9. Source References

- Kleiner & Tull 2020: arXiv:2002.07655
- Kleiner 2019: arXiv:1907.03223  
- IIT 4.0: PLoS Comput Biol 19(10) e1011465, PMC
- PyPhi: github.com/wmayner/pyphi, PLOS Comput Biol 14(7) e1006343
- Dharmakīrti: plato.stanford.edu/entries/dharmakiirti/
- PhysLean: github.com/HEPLean/PhysLean
