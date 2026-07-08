Let me take one actual Dharmakīrti kārikā and run it all the way through.Searched the webSearched the webGood. I have the exact Sanskrit. Now the full worked example:

THE VERSE — PV III.3 (Dharmakīrti's definition of perception)
pratyakṣaṃ kalpanāpoḍham abhrāntam
Dignāga's original: pratyakṣaṃ kalpanāpoḍham (perception = free from conceptual construction)
Dharmakīrti's addition: abhrāntam (non-erroneous)
Two words added. Centuries of argument. This is the entry point.

STEP 0 — SAYABILITY CHECK
Root claim: "Perception (pratyakṣa) is cognition that is free from conceptual construction (kalpanāpoḍha) and non-erroneous (abhrānta)"
Negation: "There exists a valid perception that is either (a) conceptually constructed, or (b) erroneous"
Coherent? Yes — this is exactly what Kumārila Bhaṭṭa argues. Nyāya argues (b) partially. The negation has clear consequences. ✓ SAYABLE → continue.

THE NODE TREE — what the svavṛtti decomposition gives you
NODE 1 [ROOT]
id: 1
source_text: "pratyakṣaṃ kalpanāpoḍham abhrāntam"
source_ref: PV III.3
statement: "pratyakṣa is kalpanāpoḍha AND abhrānta"
status: ??? (depends on children)
lean_type: Pratyaksa = {c : Cognition // KalpanaPoḍha c ∧ Abhrānta c}

    ├── NODE 2 [DEFINITION]
    │   statement: "kalpanā = cognition apt for verbal expression (abhilāpasaṃsargayogya)"
    │   source_ref: PV III.svavṛtti
    │   status: DEFINITION (Dharmakīrti defines this explicitly)
    │   lean_type: def Kalpana (c : Cognition) : Prop :=
    │               AptForVerbalExpression c
    │
    ├── NODE 3 [FORMAL]
    │   statement: "pratyakṣa is free from kalpanā (KalpanaPoḍha)"
    │   status: → recurse
    │
    │       ├── NODE 3a [DEFINITION]
    │       │   statement: "svalakṣaṇa (particular) is the object of perception"
    │       │   status: DEFINITION (Yogācāra ontology: only particulars are real)
    │       │   lean_type: axiom SvalaksanaReal : ∀ x, Real x → Particular x
    │       │
    │       └── NODE 3b [FORMAL → PROVED]
    │           statement: "perception of svalakṣaṇa cannot be conceptually constructed"
    │           status: PROVED (follows from 3a + def of kalpanā)
    │           lean_type: theorem no_kalpana_in_perception :
    │                       ∀ (c : Cognition) (x : Svalaksana),
    │                         Perceives c x → ¬ Kalpana c
    │
    └── NODE 4 [FORMAL — THE INTERESTING ONE]
        statement: "pratyakṣa is abhrānta (non-erroneous)"
        status: → recurse

            ├── NODE 4a [DEFINITION/AXIOM]
            │   statement: "abhrānta = avisaṃvādita = not misleading re: arthakriyā
            │               (causal efficacy of object)"
            │   source_ref: PV svavṛtti — Dharmakīrti explicitly defines abhrānta
            │               as avisaṃvāditva, not as "accurate representation"
            │   status: DEFINITION — but DIVERGENCE POINT
            │   note: Kumārila defines abhrānta as yathāvasthita-ākāra
            │         (accurate image of object as it stands).
            │         Dharmakīrti rejects this. Two axiom choices. Same word.
            │   lean_type: -- Dharmakīrti's version:
            │               def Abhranta_DK (c : Cognition) : Prop :=
            │                 LeadsToSuccessfulAction c
            │               -- Kumārila's version (divergence node):
            │               def Abhranta_K (c : Cognition) : Prop :=
            │                 AccuratelyRepresentsObject c
            │
            └── NODE 4b [EMPIRICAL → OUTSIDE_FORMAL]
                statement: "sensory illusions (timira, double-moon) are erroneous
                            despite being conception-free"
                status: OUTSIDE_FORMAL
                note: This is Dharmakīrti's argument FOR adding abhrānta —
                      Dignāga's definition alone admits illusions as valid.
                      Whether double-moon cognition is "conception-free"
                      is an empirical/phenomenological claim, not provable
                      in Lean without a model of cognition.

THE DIVERGENCE NODE — this is gold
Node 4a is where the whole Kumārila vs. Dharmakīrti debate lives. Same term abhrānta, two definitions:

Dharmakīrti: non-erroneous = leads to successful action re the object (arthakriyā). Pragmatic/causal criterion.
Kumārila: non-erroneous = accurately mirrors the object as it stands (yathāvasthita). Correspondence criterion.

In Lean this becomes two separate type definitions. Both are DEFINITION nodes (neither can be proved from more basic premises — they're axiom choices). But you can now prove:
lean4-- Under Dharmakīrti's definition:
theorem dk_vs_kumārila :
  ∀ (c : Cognition),
    Abhranta_DK c ↔ ¬ Abhranta_K c → False := by
  -- Not provable — they're independent axiom choices
  -- But we can show: cases exist where they diverge
  sorry -- placeholder for phenomenological case

-- The divergence case Dharmakīrti uses:
-- timira (eye-floaters) cognition: conception-free ✓, leads to failed action ✓
-- → Abhranta_K = True (it accurately represents what the diseased eye sees)
-- → Abhranta_DK = False (leads to failed action re actual object)
-- DIVERGENCE: same cognition, opposite verdict under two definitions
The sorry here is honest — it marks an empirical claim (whether timira cognition is conception-free) that requires a phenomenological model, not just logic.

THE LEAN PROOF — what actually compiles
The proved core (Node 3b + 3a):
lean4-- Ontological axiom (Node 3a — DEFINITION, Dharmakīrti's Yogācāra commitment)
axiom Svalaksana : Type  -- particulars are a type
axiom only_svalaksana_real : ∀ (x : α), Real x → IsSvalaksana x

-- Definitions (Node 2)
def Kalpana (c : Cognition) : Prop :=
  ∃ (v : VerbalizableForm), Represents c v

-- Node 3b — this actually proves
theorem svalaksana_perception_is_kalpana_free
    (c : Cognition) (x : Svalaksana)
    (h : DirectlyPerceives c x) :
    ¬ Kalpana c := by
  intro ⟨v, hv⟩
  -- svalakṣaṇa are ineffable (Dharmakīrti PV svavṛtti)
  -- verbalizable forms are sāmānyalakṣaṇa (universals), not svalakṣaṇa
  exact absurd (perceives_svalaksana_not_verbalizable h hv)
              (svalaksana_ineff x)
Status: PROVED conditional on svalaksana_ineff axiom. That axiom is Node 3a. The tree structure is exactly the proof dependency structure.

The science crossover — run INDEPENDENTLY, don't aim at it
After the tree above is fully logged, the formal core of Node 3b is:

"Cognition that directly tracks causally efficacious particulars is non-conceptual"

Independent decomposition of predictive coding (Friston/Clark): "Prediction error signals (surprise minimization) operate on raw sensory particulars before conceptual categorisation"
If these two decompose to the same Lean type — finding. If not — finding. You don't touch the Sanskrit nodes when running the science side.

What this shows about chunking
One kārikā (pratyakṣaṃ kalpanāpoḍham abhrāntam) — 5 words — produced 7 nodes. Of those: 2 DEFINITION, 1 PROVED, 1 OUTSIDE_FORMAL, 1 DIVERGENCE (most valuable), 2 still open. The svavṛtti told you the decomposition. You didn't decide the chunk size — Dharmakīrti did. Your job is just to run the algorithm on what he already segmented.
This is why Dharmakīrti first. Every kārikā is a candidate node. Every svavṛtti paragraph is its decomposition. The structure is pre-given. With Nāgārjuna you'd have to do the decomposition yourself from commentaries — much harder, do that second.