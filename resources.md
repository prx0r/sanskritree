# Resources for Consciousness Theory Formalization

Curated by type. Priority reading order at bottom.

**Formalisation schema**: See `FORMALISATION_SCHEMA.md` for categorisation approach, formalisation methods, and cross-reference table aligned with these sources.

---

## Formal Formalizations (directly usable)

### Kleiner & Tull (2020) — "The Mathematical Structure of IIT"
- **Use:** Cleanest axiomatic decomposition of IIT primitives → Lean types
- **Content:** IIT as map from system class `Sys` into experience spaces `Exp`; IIT 3.0 and Quantum IIT as special cases
- **Links:** Frontiers; LMU Munich (category-theoretic causation + integration); **arXiv: 2002.07655**

### Kleiner (2019/2020) — "Mathematical Models of Consciousness"
- **Use:** Framework paper — what mathematical objects are appropriate for phenomenal experience → primitive library design
- **Content:** General framework for models of consciousness with epistemic context
- **Links:** arXiv: 1907.03223

### Kleiner PhD thesis (2024) — "Topics in Mathematical Consciousness Science"
- **Use:** Claim seeds; no-go theorems → OUTSIDE_FORMAL / HOLLOW candidates
- **Content:** Formal treatment of theories, experimental paradigms, methodology, artificial consciousness; no-go: if computational functionalism holds, consciousness cannot be a Turing computation
- **Links:** PhilArchive; edoc.ub.uni-muenchen.de

### IIT 4.0 (Tononi et al., 2023)
- **Use:** Authoritative claims source for IIT axioms/postulates
- **Content:** Substrate via transition probability; maximal cause-effect state; maximal substrate; integrated information
- **Links:** PubMed Central PMC10581496 (open access)

---

## Executable Implementations

### PyPhi — github.com/wmayner/pyphi
- **Use:** Ground truth oracle for IIT claim validation
- **Content:** Computes Φ, cause-effect structure for discrete dynamical systems
- **Critical:** Feed transition matrix → verify Lean primitive `Integration` matches PyPhi output

### PhysLean — github.com/HEPLean/PhysLean
- **Use:** Physics in Lean 4 (classical, relativity, QFT, string theory)
- **Check:** CausalOrder, MutualInformation, etc. before building from scratch

---

## Key Formalizable Structures

### GWT/GNW (Dehaene et al.)
- **Use:** Most computationally specified after IIT
- **Content:** Global workspace + specialist processors; explicit neural network implementations
- **Primitives:** Broadcast, Competition, Threshold, Accessibility → Tier 2
- **Links:** PNAS

### Free Energy Principle
- **Use:** FEP primitive extraction
- **Content:** Brain as statistical model; brain–world synchrony
- **Best math treatment:** Buckley et al. (2017) "The free energy principle for action and perception: A mathematical review" — *Journal of Mathematical Psychology*
- **Links:** Open Encyclopedia of Cognitive Science

### Dharmakīrti — formal logic resources
- **Use:** Sanskrit tradition claim seeds; no Lean library yet — your contribution
- **Content:** Nominalism; universals as fictions; arthakriyā → CausalPower
- **Sources:** SEP (plato.stanford.edu/entries/dharmakiirti/); Dunne "Foundations of Dharmakīrti's Philosophy" (PhilPapers)

---

## What Doesn't Exist (your gap)

- No Lean/Coq/Agda formalization of any consciousness theory
- No cross-tradition primitive library
- No machine-checkable placement of IIT/GWT/Dharmakīrti claims relative to each other

Kleiner & Tull (2020) is closest — category theory, not proof assistants. You take those structures into Lean.

---

## Priority Reading Order

1. **Kleiner & Tull 2020** (arXiv 2002.07655) — IIT in category theory → Lean types
2. **IIT 4.0** (PMC10581496) — authoritative postulates → claims DB
3. **Kleiner "Mathematical Models of Consciousness"** (arXiv 1907.03223) — valid structures for phenomenal experience
4. **PyPhi** source + docs — oracle for IIT primitive validation
5. **Buckley et al. 2017** — FEP primitive extraction
6. **SEP Dharmakīrti + Dunne** — Sanskrit claim seeds
