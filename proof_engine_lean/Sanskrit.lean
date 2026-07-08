/-
  Minimal axioms for Dharmakīrti (PV III). Per proofenginge.md.
  Cognition, Svalaksana, Perceives, Kalpana — opaque types.
-/

axiom Cognition : Type
axiom Svalaksana : Type
axiom Perceives : Cognition → Svalaksana → Prop
axiom Kalpana : Cognition → Prop
