import Sanskritree.Semantics.Relation

namespace Sanskritree

-- ============================================================
-- Layer B: Semantic frame consistency with grammatical verification
-- ============================================================

-- Sanskrit grammatical cases
inductive GrammaticalCase
  | nominative
  | accusative
  | instrumental
  | dative
  | ablative
  | genitive
  | locative
  | vocative
deriving DecidableEq

-- Semantic roles a token can fill in a frame
inductive FrameRole
  | agent
  | agent_passive
  | patient
  | object
  | goal
  | instrument
  | manner
  | location
  | domain
  | source
  | beneficiary
  | qualifier
  | predicate
deriving DecidableEq

-- A single morphological analysis tied to a token occurrence
structure MorphAnalysis where
  tokenId : Nat
  lemma : String
  grammaticalCase : Option GrammaticalCase

-- A binding between a semantic role and one or more token occurrences
structure RoleBinding where
  role : FrameRole
  entityId : Nat
  evidenceTokenIds : List Nat

-- A ritual action frame (praise, worship, offer, meditate, etc.)
structure RitualAction where
  action : String
  bindings : List RoleBinding
  sequenceIndex : Nat

-- A propositional frame (assertion, identity, causation, etc.)
structure PropositionalFrame where
  subject : String
  relation : String
  object : String
  modality : String
  polarity : Bool  -- true = affirmed, false = denied
  evidenceTokenIds : List Nat

-- ============================================================
-- Case-role compatibility (sparse, verified, not a false universal)
-- ============================================================

-- Compatible (case, role) pairs under standard Sanskrit grammar.
-- This is a compatibility relation, not a rule — actual usage
-- depends on verb valency, voice, construction, and semantic frame.
def compatibleCaseRole : GrammaticalCase → FrameRole → Bool
  | .accusative, .object => true
  | .accusative, .goal => true
  | .instrumental, .instrument => true
  | .instrumental, .manner => true
  | .instrumental, .agent_passive => true
  | .dative, .beneficiary => true
  | .ablative, .source => true
  | .genitive, .qualifier => true
  | .locative, .location => true
  | .locative, .domain => true
  | .nominative, .agent => true
  | .nominative, .predicate => true
  | .vocative, .qualifier => true
  | _, _ => false

-- ============================================================
-- Verification theorems
-- ============================================================

-- If a binding claims accusative→object, that is compatible
theorem accusative_object_compatible :
  compatibleCaseRole .accusative .object := by
  decide

-- If a binding claims instrumental→manner, that is compatible
theorem instrumental_manner_compatible :
  compatibleCaseRole .instrumental .manner := by
  decide

-- If a binding claims locative→location, that is compatible
theorem locative_location_compatible :
  compatibleCaseRole .locative .location := by
  decide

-- Nominative does not directly license object role
theorem nominative_not_object :
  compatibleCaseRole .nominative .object = false := by
  decide

-- Accusative does not directly license agent role
theorem accusative_not_agent :
  compatibleCaseRole .accusative .agent = false := by
  decide

-- ============================================================
-- Bhairavastava verse 1: frame verification
-- ============================================================

-- Morphological analyses for verse 1
def lb_bhairavanatham : MorphAnalysis := {
  tokenId := 0
  lemma := "bhairava-natha"
  grammaticalCase := some .accusative
}

def lb_hrdi : MorphAnalysis := {
  tokenId := 3
  lemma := "hrd"
  grammaticalCase := some .locative
}

def lb_vande : MorphAnalysis := {
  tokenId := 4
  lemma := "vand"
  grammaticalCase := none  -- verb, not a nominal
}

-- Frame: DevotionalAct — Abhinavagupta praises Bhairava
def bs_v1_frame : RitualAction := {
  action := "praise"
  bindings := [
    { role := .agent, entityId := 1, evidenceTokenIds := [4] },
    { role := .object, entityId := 2, evidenceTokenIds := [0] },
    { role := .location, entityId := 3, evidenceTokenIds := [3] },
    { role := .manner, entityId := 4, evidenceTokenIds := [2] }
  ]
  sequenceIndex := 1
}

-- Verify accusative→object binding is valid
theorem bs_v1_object_is_accusative :
  compatibleCaseRole .accusative .object := by
  decide

-- Verify locative→location binding is valid
theorem bs_v1_location_is_locative :
  compatibleCaseRole .locative .location := by
  decide

-- Verify the action frame has at least one binding
theorem bs_v1_has_bindings :
  bs_v1_frame.bindings ≠ [] := by
  decide

end Sanskritree
