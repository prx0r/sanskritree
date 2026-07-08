/-
  IIT scaffolding. Kleiner & Tull (arXiv:2002.07655) structures.
  Defines System class, Experience space, Cause-effect repertoire, Integration.
  Per FORMALISATION_SCHEMA.md, ground_truth/iit_formal_types.json.
-/

import Foundation

-- =============================================================================
-- System class (Kleiner & Tull Def 1)
-- =============================================================================

/-- A physical system in the IIT sense. -/
structure System (Sys : Type*) where
  /-- States of the system -/
  stateSpace : Type*
  /-- Subsystems (may depend on state) -/
  subsystems : stateSpace → Type*  -- indices or refs to subsystems
  /-- Decompositions: partitions of the system -/
  decompositions : Type*
  /-- Trivial decomposition -/
  trivialDecomp : decompositions
  /-- Cut system for a decomposition -/
  cutSystem : decompositions → Sys
  /-- Cut state for a decomposition and state -/
  cutState : decompositions → stateSpace → stateSpace

/-- The empty/trivial system -/
axiom EmptySystem : Type*

-- =============================================================================
-- Experience space (Kleiner & Tull Def 2)
-- =============================================================================

/-- An experience space E with intensity, distance, scalar multiplication. -/
structure ExperienceSpace where
  carrier : Type*
  intensity : carrier → ℝ
  distance : carrier → carrier → ℝ
  scale : ℝ → carrier → carrier
  intensity_scale : ∀ r e, intensity (scale r e) = r * intensity e
  scale_one : ∀ e, scale 1 e = e

-- =============================================================================
-- Decomposition of experience (Kleiner & Tull Def 5)
-- =============================================================================

/-- A decomposition of e over D is a map ē : D → E with ē(1) = e -/
def DecompositionOver {E : Type*} {D : Type*} (one : D) (e : E) (decomp : D → E) : Prop :=
  decomp one = e

-- =============================================================================
-- Integration level (Kleiner & Tull Def 8)
-- =============================================================================

/-- φ(e) = min over z≠1 of d(e, ē(z)). Placeholder: full def needs finite D. -/
def integrationLevel {E D : Type*} (d : E → E → ℝ) (e : E) (one : D) (decomp : D → E)
    (h_one : decomp one = e) : ℝ :=
  0

/-- Integration scaling ι(e) = φ(e) · ê. Placeholder. -/
def integrationScaling {E : Type*} (φ : ℝ) (e : E) (norm : E → E) : E :=
  norm e

-- =============================================================================
-- Cause-effect repertoire (Kleiner & Tull Def 6)
-- =============================================================================

/-- Proto-experience space for system S -/
axiom ProtoExperience (Sys : Type*) : Sys → Type*

/-- Cause repertoire: caus_s(M,P) ∈ PE(S) -/
axiom causeRepertoire {Sys : Type*} (S : Sys) (s : Unit) (M P : Type*) : ProtoExperience Sys S

/-- Effect repertoire: eff_s(M,P) ∈ PE(S) -/
axiom effectRepertoire {Sys : Type*} (S : Sys) (s : Unit) (M P : Type*) : ProtoExperience Sys S

-- =============================================================================
-- Concept and Q-shape (Kleiner & Tull §6, §7)
-- =============================================================================

/-- Concept of mechanism M: core integration scaling of (caus(M), eff(M)) -/
axiom Concept {Sys : Type*} (S : Sys) (s : Unit) (M : Type*) : Type*

/-- Q-shape: collection of concepts over all mechanisms -/
axiom QShape {Sys : Type*} (S : Sys) (s : Unit) : Type*

/-- Actual experience E(S,s) = core integration scaling of Q(S,s) -/
axiom actualExperience {Sys : Type*} (S : Sys) (s : Unit) : Type*

/-- Φ(S,s) = ||E(S,s)|| — quantity of experience -/
axiom Phi {Sys : Type*} (S : Sys) (s : Unit) : ℝ

-- =============================================================================
-- Classical IIT: TPM, conditional independence (Kleiner & Tull §9)
-- =============================================================================

/-- Transition probability matrix: T : P(S) → P(S) -/
axiom TPM (StateSpace : Type*) : Type*

/-- Conditional independence: T(p) = ∏ᵢ Tᵢ(p) -/
axiom ConditionalIndependence {α : Type*} (T : α → α) (T_component : ℕ → α → α) : Prop

-- =============================================================================
-- Our primitives as IIT-facing types
-- =============================================================================

/-- Substrate: the physical base. IIT existence, Dharmakīrti, everything. -/
axiom Substrate : Type

/-- CausalPower: x affects y's probability distribution -/
def CausalPower (x y : Substrate) : Prop := True  -- placeholder

/-- Integration: system cannot be partitioned without information loss -/
def Integration (s : Substrate) : Prop := True  -- placeholder

/-- Composition: system has distinguishable parts -/
def Composition (s : Substrate) : Prop := True  -- placeholder

/-- Exclusion: only one description level applies at a time -/
def Exclusion (s : Substrate) : Prop := True  -- placeholder
