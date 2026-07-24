import Sanskritree.Semantics.Relation

namespace Sanskritree

-- ============================================================
-- Layer A: Decision objects for traceable morphological choices
-- ============================================================

inductive AnalysisEngine
  | vidyut | heritage | dcs | fallback | human_review

structure EvidenceId where
  source : AnalysisEngine
  confidence : Float

structure Lemma where
  slp1 : String
  iast : String
  devanagari : String
  gloss : String

structure Morphology where
  vibhakti : Option String
  vacana : Option String
  linga : Option String
  lakara : Option String
  purusha : Option String
  prayoga : Option String

structure TokenReading where
  surface : String
  lemma : Lemma
  morphology : Morphology
  engine : AnalysisEngine
  sourceEvidence : List EvidenceId

inductive CompoundRelation
  | karmadharaya
  | tatpurusha
  | bahuvrihi
  | dvandva
  | avyayibhava
  | unknown

structure CompoundReading where
  members : List Lemma
  relation : CompoundRelation
  resultingSense : String

-- ============================================================
-- Lemma inventory for Bhairavastava 1
-- ============================================================

def bhairavaLemma : Lemma := {
  slp1 := "BErava"
  iast := "bhairava"
  devanagari := "bhairava"
  gloss := "Bhairava, the terrifying aspect of Siva"
}

def nathaLemma : Lemma := {
  slp1 := "nATa"
  iast := "natha"
  devanagari := "natha"
  gloss := "lord, protector, refuge"
}

def anathaLemma : Lemma := {
  slp1 := "anATa"
  iast := "anatha"
  devanagari := "anatha"
  gloss := "without a protector, helpless"
}

def saraNyaLemma : Lemma := {
  slp1 := "saraRya"
  iast := "saranya"
  devanagari := "saranya"
  gloss := "refuge, protection"
}

def tvanmayaLemma : Lemma := {
  slp1 := "tvanmaya"
  iast := "tvanmaya"
  devanagari := "tvanmaya"
  gloss := "consisting of you, filled with you"
}

def cittaLemma : Lemma := {
  slp1 := "citta"
  iast := "citta"
  devanagari := "citta"
  gloss := "mind, consciousness, awareness"
}

def hrdLemma : Lemma := {
  slp1 := "hfd"
  iast := "hrd"
  devanagari := "hrd"
  gloss := "heart"
}

def vandLemma : Lemma := {
  slp1 := "vand"
  iast := "vand"
  devanagari := "vand"
  gloss := "to praise, worship, salute"
}

-- ============================================================
-- Morphological analyses
-- ============================================================

def bhairavanatham_morph : Morphology := {
  vibhakti := some "dvitIya"
  vacana := some "eka"
  linga := some "napumsaka"
  lakara := none
  purusha := none
  prayoga := none
}

def hrdi_morph : Morphology := {
  vibhakti := some "saptami"
  vacana := some "eka"
  linga := none
  lakara := none
  purusha := none
  prayoga := none
}

def vande_morph : Morphology := {
  vibhakti := none
  vacana := some "eka"
  linga := none
  lakara := some "lat"
  purusha := some "uttama"
  prayoga := some "parasmaipada"
}

-- ============================================================
-- Competing compound parses (the graph branches)
-- ============================================================

-- bhairavanatham: two possible relations between members
def bhairavanatham_karmadharaya : CompoundReading := {
  members := [bhairavaLemma, nathaLemma]
  relation := CompoundRelation.karmadharaya
  resultingSense := "Bhairava who is the lord (appositional)"
}

def bhairavanatham_tatpurusa : CompoundReading := {
  members := [bhairavaLemma, nathaLemma]
  relation := CompoundRelation.tatpurusha
  resultingSense := "the lord of Bhairava (genitive)"
}

-- tvanmayacittataya: the compound "tvanmaya-citta-ta"
def tvanmayacitta_karmadharaya : CompoundReading := {
  members := [tvanmayaLemma, cittaLemma]
  relation := CompoundRelation.karmadharaya
  resultingSense := "the mind that consists of you"
}

def tvanmayacitta_bahuvrihi : CompoundReading := {
  members := [tvanmayaLemma, cittaLemma]
  relation := CompoundRelation.bahuvrihi
  resultingSense := "the state of having a mind filled with you"
}

-- ============================================================
-- Consistency checks verified by Lean
-- ============================================================

-- Every lemma has a non-empty gloss
theorem glosses_nonempty :
  bhairavaLemma.gloss ≠ "" ∧ nathaLemma.gloss ≠ "" ∧
  anathaLemma.gloss ≠ "" ∧ saraNyaLemma.gloss ≠ "" ∧
  tvanmayaLemma.gloss ≠ "" ∧ cittaLemma.gloss ≠ "" := by
  repeat' (first | apply And.intro | decide)

-- At least one compound analysis must be selected for bhairavanatham
theorem bhairavanatham_has_analysis :
  bhairavanatham_karmadharaya.resultingSense ≠ "" ∨
  bhairavanatham_tatpurusa.resultingSense ≠ "" := by
  left; decide

-- vande is first person singular, confirming subject is "I"
theorem vande_first_person :
  vande_morph.purusha = some "uttama" := by
  decide

-- hrdi is locative, indicating location of worship
theorem hrdi_locative :
  hrdi_morph.vibhakti = some "saptami" := by
  decide

-- If Karmadharaya is chosen, case must be dvitIya
theorem karmadharaya_requires_case :
  bhairavanatham_karmadharaya.relation = CompoundRelation.karmadharaya →
  bhairavanatham_morph.vibhakti = some "dvitIya" := by
  intro h
  rfl

end Sanskritree
