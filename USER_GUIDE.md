# SANSKRIT PROOF ENGINE — User Guide

*For yourself, cold. Everything you need to run the system and not break it.*

---

## 1. What This Is

A **truth compressor** for Sanskrit philosophical claims. Input: Sanskrit text. Output: a node graph where each node is either PROVED (Lean4), OUTSIDE_FORMAL (empirical), HOLLOW (unsayable), or PARTIAL (mixed).

**Goal:** Honesty, not proofs. PARTIAL and OUTSIDE_FORMAL are correct when the text doesn't support formalization. The boundary is the finding.

**Architecture:** Typed deductive DB with fixed-point status semantics. Lean = formal oracle. Human = semantic oracle. LLM = decomposition + template selection only (never proof).

---

## 2. The Algorithm (Memorize This)

```
process(C):
  if ¬sayable(C): return HOLLOW
  if match(Library): import; return
  lean_type ← formalize(C, template, SOI/DOI)
  if DEFINITION: return PROVED (axiom)
  if structural: prove(lean_type); return result
  if FDE: fde_eval(lean_type); return result
  children ← decompose(C)  // 4a commentary | 4b secondary | 4c llm
  for c in children: process(c)
  return propagate(C)
```

**Decomposition priority:** 4a commentary (svavṛtti etc.) → 4b secondary scholarship → 4c LLM (flag human_review).

**Propagation order:** REFUTED → HOLLOW → PARTIAL_HOLLOW → PROVED → UNPROVED → PARTIAL.

---

## 3. Schema Quick Ref

- **Node:** id, parent_id, source_text (IAST anchor), provenance, kāṇḍa, logic_foundation, status, lean_type, lean_template_id, formalization_rationale, decomposition_source, circular, absence_type
- **Term registry:** Required before ~50 nodes. iast canonical; definition_nodes[{tradition, node_id}]; same IAST diff tradition → diff nodes
- **CONTRADICTION:** node_a, node_b, defeat_argument, contradiction_scope (intra_author | intra_tradition | inter_tradition)
- **Bridge:** Same Lean type, independent decomposition; same kāṇḍa or human promotion from Kāṇḍa 3

---

## 4. Kāṇḍa System (Pāṇini)

- **Kāṇḍa 1 (siddha):** Axioms, DEFINITION nodes, anchors. Globally visible.
- **Kāṇḍa 2 (vidhi):** Operational derivations. Dependency-ordered.
- **Kāṇḍa 3 (asiddha):** FDE nodes, circular, abhāva. Invisible to Kāṇḍa 1. Bridges need human promotion.

---

## 5. Templates (§6)

All formalization via schema templates. No free-form Lean.

abheda→a=b | vyapti→∀x,Hx→Sx | sambandha→Ra b | avacchedaka→∀{x:α},Px | pratiyogin→Counterpositive | anuyogin→Bearer | nirupaka→Definer | nirupya→Defined | samavaya→Inheres | anyonyabhava→a≠b | samsargabhava→¬(Ra b) | property→P:α→Prop | negation paryudasa→{x//¬Px} | negation prasajya→¬P | fde_val, fde_neg

**Template conflict:** SOI (same subexpression) → apavāda wins. DOI (different operands) → para (dependent) wins.

---

## 6. Critical Constraints

1. **No provability bias.** Decompose faithfully to source. If no proof emerges, PARTIAL/OUTSIDE_FORMAL is correct.
2. **Bridges found, not constructed.** Independent decomposition only. Never force a match.
3. **IAST canonical.** Comparison at IAST level. English is display only.
4. **Anchor immutable.** source_text never changes. Interpretation (statement, lean_type) is versioned.
5. **Term registry before 50 nodes.** Same word, diff tradition → diff nodes. definition_nodes: [{tradition, node_id}].
6. **validation_set_pass_rate = 1.0 ∨ DEV_MODE.** Hard gate. 20 gold claims before production.
7. **warningAsError true.** No sorry.
8. **formalization_rationale required.** Human judges semantic faithfulness; Lean judges formal correctness.

---

## 7. Dharmakīrti First (Recommended)

**Why:** Pramāṇavārttika has kārikā + svavṛtti. The structure is pre-given: kārikā = node, svavṛtti = decomposition. Easiest text. Most formalizable after Nyāya-Sūtras.

**Text:** Pramāṇavārttika (PV). GRETIL, SARIT. Steinkellner editions.

**logic_foundation:** classical (not FDE; that's Nāgārjuna).

**Key terms:** pramāṇa, pratyakṣa, kalpanā, svalakṣaṇa, arthakriyā, anumāna, apoha.

**Pitfalls:**
- svavṛtti is syntactically brutal. NLP tools (ByT5, SanskritShala) trained on narrative; expect garbage on half of prose. Validate with human/Sanskrit reader.
- One kārikā can contain conditional + objection + response → split to 3 nodes.
- svavṛtti sometimes contradicts kārikā → two nodes, CONTRADICTION.
- pramāṇa ↔ arthakriyā ↔ successful cognition is circular. Mark circular: coherentist; axiom + review.
- Dharmakīrti vs Kumārila on abhrānta: different type definitions, not factual disagreement. CONTRADICTION with term_disambiguation.

**Start:** PV III (pratyakṣa chapter). PV III.3 is a clean example (perception of particulars is non-conceptual). Create `phase1_dharmakirti.py` parallel to `phase1_nyaya.py` with PV III.3 kārikās as PHASE1_TERMS.

---

## 8. Granularity

| Text type | Unit |
|-----------|------|
| kārikā (PV, MMK) | one kārikā |
| sūtra (NS, SS) | one sūtra |
| prose (svavṛtti) | one sentence, one distinct claim |
| TA verse | one śloka |

---

## 9. Danger List (Don't Skip)

1. **NLP on philosophical prose:** Heritage/ByT5 trained on narrative. Dharmakīrti's svavṛtti = garbage on many sentences. Validate.
2. **Lean formalization doesn't exist:** Cognition, particular/universal, abhāva — no Lean4 impl. Build foundation first.
3. **Kārikā edge cases:** Conditional+objection+response in one verse → split. Purely rhetorical → CONTRADICTION only. Term defined 200 verses earlier → placeholder + dependency.
4. **Translation lag:** Compare at IAST. Same English, diff IAST → candidate false merge.
5. **LLM bias toward provability:** Decomposition will westernize. Mitigate: Sanskrit-first decomposition; faithfulness check; track decomposition_source.
6. **Abhāva:** Four types (prior, posterior, mutual, absolute). Dharmakīrti: absence by inference. Nyāya: by perception. Require absence_type; human decides.
7. **Term registry rot:** After 200 nodes: kalpanā, kalpana, vikalpa, conceptual construction — all same-ish, used interchangeably. Registry before 50.
8. **Validation set:** 20 claims (5 PROVED, 5 OUTSIDE_FORMAL, 5 HOLLOW, 5 PARTIAL). From secondary lit. Run first.
9. **Pantograph:** Research software. Fallback: lake build + parse output.

---

## 10. Tools

| Tool | Role |
|------|------|
| Heritage, ByT5, SanskritShala | Sandhi, morph, POS, dep |
| DCS, Sembank | Sense-disambiguated corpus; WordNet |
| GRETIL | PV, TA, Shiva Sūtras (IAST) |
| LeanSearch, Loogle | Library match |
| Pantograph | Python↔Lean4 REPL |
| panini-nlp | 3996 sūtras as graph; use, don't rebuild |

---

## 11. Pipeline

```
Sanskrit (GRETIL) → Heritage/ByT5 → NN parse → Template(SOI/DOI) → lean_type → process()
```

Prose: +human validation. Kārikā/sūtra: automated.

---

## 12. File Map

| File | Purpose |
|------|---------|
| SCHEMA.md | Formal schema. Source of truth. |
| proofenginge.md | Full instructions, phases, tool stack |
| danger.md | Pitfalls, what breaks |
| instruction.md | Meta-prompt, resources |
| standards.md | Node definition, granularity |
| first.md | Dharmakīrti-first, network map |
| panini.md | Kāṇḍa, anuvrtti, SOI/DOI |
| baguette.md | TRS, five layers, FDE |
| review.md | Peer review, prompts |
| math.md | Mandala geometry, dead ends |
| proof_engine/ | Python impl: db, algorithm, api, fol_lean_bridge, lean_checker, sanskrit_pipeline. *Note:* db.py is a minimal subset of SCHEMA.md; migrate to full schema (kāṇḍa, term_registry, CONTRADICTION, Bridge) before Dharmakīrti run. |
| frontend/ | 2D/3D viz, mandala |

---

## 13. First Run Checklist

- [ ] Term registry with pramāṇa, pratyakṣa, kalpanā, svalakṣaṇa, arthakriyā (Dharmakīrti scope)
- [ ] validation_set 20 claims OR DEV_MODE
- [ ] PV III.3 IAST + svavṛtti from GRETIL
- [ ] Run process() on PV III.3
- [ ] decomposition_source = commentary for svavṛtti-derived children
- [ ] formalization_rationale on every lean_type
- [ ] No sorry (warningAsError)

---

## 14. References

Briggs 1985, Priest 2010, Guhe 2017, Ganeri 2008, Rajpopat 2022, Scherf Advaita/Dao/Dzogchen, panini.md, math.md.
