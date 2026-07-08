/-
  Foundation proofs for consciousness theory formalization.
  Proved lemmas from Mathlib that claims bottom out in.
  Per mathlib_catalog.json, FORMALISATION_SCHEMA.md.
-/

import Mathlib.Logic.Basic
import Mathlib.Data.Set.Basic
import Mathlib.Data.Real.Basic

-- =============================================================================
-- Logic (Mathlib.Logic.Basic)
-- =============================================================================

/-- Modus ponens: P and (P → Q) implies Q -/
theorem modus_ponens (P Q : Prop) (hP : P) (hPQ : P → Q) : Q := hPQ hP

/-- Forall-implication: ∀ x, H x → S x is provable by intro -/
theorem forall_imp (α : Type*) (Hetu Sadhya : α → Prop) (h : ∀ x, Hetu x → Sadhya x) :
    ∀ x, Hetu x → Sadhya x := h

/-- Contrapositive -/
theorem contrapositive (P Q : Prop) (h : P → Q) : ¬Q → ¬P := fun hnq hp => hnq (h hp)

-- =============================================================================
-- Sets and partitions (for IIT decompositions)
-- =============================================================================

namespace Set

/-- A partition of a type is a set of disjoint sets whose union is univ -/
def IsPartition {α : Type*} (parts : Set (Set α)) : Prop :=
  (∀ a b, a ∈ parts → b ∈ parts → a ≠ b → Disjoint a b) ∧
  ⋃₀ parts = Set.univ

end Set

-- =============================================================================
-- Non-negative reals (for experience space intensity, φ)
-- =============================================================================

/-- Zero is non-negative -/
theorem nnreal_zero : 0 ≤ (0 : ℝ) := le_refl 0
