"""Technical-sense ranker: selects the correct sense for a lemma based on context.
Queries lexical_senses DB table first, falls back to built-in glossary.
Combines: domain context, same-work attestation, tradition proximity, cross-verse consistency.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RankedSense:
    lemma: str
    gloss: str
    score: float
    source: str  # db | glossary | same_work | commentary | dictionary
    is_technical: bool = False
    tradition: str = ""


# Track last-used DB connection for background queries
_conn = None
_allowed_scopes: set[str] | None = None  # None = all scopes allowed

def set_db_connection(conn):
    global _conn
    _conn = conn

def set_allowed_scopes(scopes: list[str] | None):
    """Restrict sense retrieval to specific scope tiers.
    None = all scopes. Used for C0/C1/C2 ablation in Phase 2.
    """
    global _allowed_scopes
    _allowed_scopes = set(scopes) if scopes else None

def get_allowed_scopes() -> set[str] | None:
    return _allowed_scopes


def query_db_senses(lemma: str) -> list[dict]:
    """Query lexical_senses table for a lemma, filtering by allowed scopes."""
    if not _conn:
        return []
    try:
        if _allowed_scopes is not None:
            placeholders = ",".join("?" for _ in _allowed_scopes)
            rows = _conn.execute(
                f"SELECT lemma, tradition, short_gloss, definition, semantic_class FROM lexical_senses WHERE lemma = ? AND scope IN ({placeholders})",
                (lemma, *list(_allowed_scopes)),
            ).fetchall()
        else:
            rows = _conn.execute(
                "SELECT lemma, tradition, short_gloss, definition, semantic_class FROM lexical_senses WHERE lemma = ?",
                (lemma,),
            ).fetchall()
        return [
            {"lemma": r[0], "tradition": r[1], "gloss": r[2], "definition": r[3], "semantic_class": r[4]}
            for r in rows
        ]
    except Exception:
        return []


def query_work_tradition(work_id: str) -> str:
    """Determine tradition for a work."""
    if not _conn:
        return ""
    try:
        row = _conn.execute(
            "SELECT DISTINCT tradition FROM lexical_senses ls JOIN sense_attestation sa ON sa.sense_id = ls.sense_id WHERE sa.work_id = ? LIMIT 1",
            (work_id,),
        ).fetchone()
        if row:
            return row[0]
    except Exception:
        pass
    # Fallback: guess from work_id
    if "spanda" in work_id.lower():
        return "spanda"
    if "bhairava" in work_id.lower():
        return "trika"
    if "gita" in work_id.lower():
        return "vedanta"
    return ""


# Tradition proximity tiers (0 = exact match, higher = more distant)
TRADITION_PROXIMITY = {
    ("spanda", "spanda"): 0,
    ("spanda", "trika"): 1,
    ("spanda", "saiva"): 2,
    ("spanda", "vedanta"): 3,
    ("spanda", "general"): 4,
    ("trika", "spanda"): 1,
    ("trika", "trika"): 0,
    ("trika", "saiva"): 1,
    ("trika", "general"): 3,
    ("general", "general"): 0,
    ("general", "spanda"): 3,
    ("general", "trika"): 3,
}


TECHNICAL_TERMS_KS = {
    # Spanda-specific
    "spanda": ("vibration/pulsation of consciousness", 0.9),
    "unmeza": ("unmeSa — opening/expansion of consciousness (manifestation of the universe)", 0.9),
    "unmeSa": ("unmeSa — opening/expansion of consciousness", 0.9),
    "nimeza": ("nimeSa — closing/contraction of consciousness (withdrawal of manifestation)", 0.9),
    "nimeSa": ("nimeSa — closing/contraction of consciousness", 0.9),
    "kzoBa": ("kSobha — agitation/disruption of the sense of separate self", 0.85),
    "kSobha": ("kSobha — agitation/disruption of ego", 0.85),
    
    # 36 tattvas
    "Siva": ("Siva — Supreme Consciousness, the ultimate reality", 0.85),
    "Sakti": ("Sakti — the dynamic power/energy of consciousness", 0.85),
    "sakti": ("sakti — power/energy of consciousness", 0.85),
    "kalA": ("kalA — the principle of limitation/obscuration (one of 5 kanchukas)", 0.95),
    "kalā": ("kalā — principle of limitation (kanchuka), NOT 'arts' or 'time'", 0.95),
    "niyati": ("niyati — causal necessity/fate (one of 5 kanchukas)", 0.9),
    "rAga": ("rAga — attachment/passion (one of 5 kanchukas)", 0.8),
    "vidyA": ("vidyA — limited knowledge (one of 5 kanchukas)", 0.85),
    "kAla": ("kAla — time (one of 5 kanchukas)", 0.8),
    "mAyA": ("mAyA — principle of manifestation/limitation, NOT 'illusion'", 0.85),
    "prakfti": ("prakfti — primordial nature", 0.8),
    "puruza": ("puruSa — individual soul/consciousness principle", 0.85),
    "buddhi": ("buddhi — intellect/determinative faculty", 0.8),
    
    # Trika-specific
    "paSu": ("paSu — the bound soul/fettered being", 0.9),
    "paśu": ("paśu — the bound soul, NOT 'beast/animal'", 0.95),
    "pati": ("pati — the Lord/Siva", 0.85),
    "pASa": ("pASa — bond/fetter that binds the soul", 0.85),
    "pāśa": ("pāśa — bond that binds the soul", 0.85),
    "grantha": ("grantha — spiritual knot/blockage", 0.8),
    "dIkzA": ("dIkSA — initiation/spiritual transmission", 0.85),
    "nirvARa": ("nirvANa — liberation/spiritual freedom", 0.85),
    
    # Key philosophical terms
    "pratyaya": ("pratyaya — cognition/mental representation, NOT 'faith' or 'belief'", 0.9),
    "tattva": ("tattva — reality/principle/category of existence", 0.85),
    "pada": ("pada — state/condition/level of being, NOT 'foot' in philosophical context", 0.9),
    "dharma": ("dharma — essential nature/quality, also virtue", 0.8),
    "abheda": ("abheda — non-difference/non-duality", 0.85),
    "bheda": ("bheda — difference/duality", 0.85),
    "svatantrya": ("svatantrya — sovereign freedom/independence (Siva's key attribute)", 0.9),
    "akftrima": ("akftrima — natural/uncontrived (not artificial)", 0.8),
    "adhiSThAna": ("adhiSThAna — foundation/basis/standing upon", 0.8),
    "sauSupta": ("sauSupta — the state of deep sleep", 0.85),
    "sauZupta": ("sauZupta — deep sleep state", 0.85),
    "mUDa": ("mUDha — deluded/confused one", 0.8),
    "prabudDa": ("prabuddha — awakened/enlightened one", 0.85),
    "anAvfta": ("anAvfta — uncovered/unveiled/revealed", 0.8),
    
    # Powers and their functions
    "bandhayitrI": ("bandhayitrI — She who binds (a form of Śakti's power of limitation)", 0.9),
    "banDayitrI": ("bandhayitrI — She who binds (a Śakti)", 0.9),
    "svamArga": ("sva-mārga — one's own path (the soul's path back to Siva)", 0.85),
    "siddhi": ("siddhi — spiritual accomplishment/extraordinary power", 0.85),
    "upapAdikA": ("upapAdikA — she who bestows/brings about", 0.8),
    
    # Compound terms common in Spanda
    "padadvaya": ("pada-dvaya — the two states (waking and dreaming, or the dual condition)", 0.9),
    "jIvanmukta": ("jIvanmukta — liberated while still living", 0.9),
    "jIvanmukti": ("jIvanmukti — liberation while alive", 0.9),
    "paramapada": ("parama-pada — the supreme state", 0.85),
    "cakreSvara": ("cakreSvara — lord of the wheel (master of the energy-wheels)", 0.85),
    "zabdAnuveDa": ("zabdAnuveDha — penetration/impregnation by speech/sound", 0.9),
    "Sap1": ("śabdānuvedha — penetration by speech/sound", 0.8),
    "Sap": ("śabda — word/sound", 0.8),
    "dAnu": ("dānu — giving/dona (may be from dā 'to give')", 0.6),
    "veDa": ("vedha — piercing/penetrating", 0.8),
}


def is_technical_context(lemmas: list[str]) -> bool:
    """Check if a set of lemmas suggests a technical/doctrinal context."""
    technical_hits = 0
    for lemma in lemmas:
        norm = lemma.lower().replace("1", "").replace("2", "")
        if norm in TECHNICAL_TERMS_KS:
            technical_hits += 1
    return technical_hits >= 2 or (len(lemmas) > 0 and technical_hits / len(lemmas) >= 0.3)


def _normalize_slp1(lemma: str) -> str:
    """Normalize SLP1 to a canonical form for glossary lookup."""
    s = lemma.lower().replace("1", "").replace("2", "").replace("3", "")
    # SLP1 to IAST/devanagari mapping
    mapping = {
        "a": "a", "A": "ā", "i": "i", "I": "ī", "u": "u", "U": "ū",
        "f": "ṛ", "F": "ṝ", "x": "ṣ", "X": "kṣ",
        "G": "ṅ", "J": "ñ", "N": "ṇ", "T": "ṭ", "D": "ḍ",
        "S": "ś", "z": "ṣ", "h": "h", "M": "ṃ", "H": "ḥ",
        "e": "e", "o": "o", "k": "k", "K": "kh", "g": "g", "G": "gh",
        "c": "c", "C": "ch", "j": "j", "J": "jh",
        "t": "t", "d": "d", "n": "n", "p": "p", "P": "ph",
        "b": "b", "B": "bh", "m": "m", "y": "y", "r": "r",
        "l": "l", "v": "v", "w": "v",
    }
    # Generate IAST approximation
    iast = ""
    for ch in s:
        iast += mapping.get(ch, ch)
    # Also try the SLP1-like key (Sap1 → Sap → śap → śabda)
    # Remove trailing digits
    base = lemma.rstrip("123")
    return s, iast, base.lower()


def rank_senses(lemma: str, context_lemmas: list[str], work_id: str | None = None) -> list[RankedSense]:
    """Rank candidate senses for a lemma given its context.
    Priority: DB lexical_senses (with tradition proximity) → glossary → generic fallback.
    """
    norm_slp1, norm_iast, norm_base = _normalize_slp1(lemma)
    candidates = []

    tech_context = is_technical_context(context_lemmas)
    work_tradition = query_work_tradition(work_id) if work_id else ""

    # Build candidate lemma forms for matching
    import re
    candidate_forms = set()
    for f in [lemma, lemma.lower(), norm_slp1, norm_iast, norm_base,
              lemma.rstrip("123"), lemma.lower().rstrip("123"), norm_slp1.rstrip("123")]:
        f_clean = re.sub(r'[^a-zA-Zāīūṛṝḷḹēōṃḥṅñṭḍṇśṣ0-9]', '', f)
        if f_clean:
            candidate_forms.add(f_clean)

    # TIER 1: DB lexical_senses table
    db_senses = query_db_senses(lemma)
    if not db_senses and norm_slp1 != lemma:
        db_senses = query_db_senses(norm_slp1)
    if not db_senses and norm_base != lemma and norm_base != norm_slp1:
        db_senses = query_db_senses(norm_base)

    if db_senses:
        for s in db_senses:
            tradition = s["tradition"]
            proximity = TRADITION_PROXIMITY.get((work_tradition, tradition), 3) if work_tradition else 2
            base_score = 0.9 if s["semantic_class"] == "TECHNICAL_TERM" else 0.6
            score = base_score - (proximity * 0.1)
            if tech_context and s["semantic_class"] == "TECHNICAL_TERM":
                score += 0.15
            candidates.append(RankedSense(
                lemma=lemma, gloss=s["gloss"], score=min(score, 0.99),
                source="db", is_technical=(s["semantic_class"] == "TECHNICAL_TERM"),
                tradition=tradition,
            ))

    # TIER 2: Glossary fallback (if DB didn't have entries)
    if not candidates:
        matched = False
        for form in sorted(candidate_forms, key=len, reverse=True):
            if form in TECHNICAL_TERMS_KS:
                gloss, score = TECHNICAL_TERMS_KS[form]
                if tech_context:
                    score = min(score + 0.15, 0.99)
                candidates.append(RankedSense(lemma=lemma, gloss=gloss, score=score,
                                              source="glossary", is_technical=True))
                matched = True
                break

        # Partial match — requires strong overlap and same start/end boundary
        if not matched:
            for form in sorted(candidate_forms, key=len, reverse=True):
                for key, (gloss, score) in TECHNICAL_TERMS_KS.items():
                    if len(form) < 4 or len(key) < 4:
                        continue
                    shorter, longer = (form, key) if len(form) <= len(key) else (key, form)
                    ratio = len(shorter) / len(longer)
                    if ratio < 0.65:
                        continue
                    if longer.startswith(shorter) or longer.endswith(shorter):
                        if tech_context:
                            score = min(score + 0.15, 0.99)
                        candidates.append(RankedSense(lemma=lemma, gloss=gloss, score=score * 0.9,
                                                      source="glossary", is_technical=True))
                        matched = True
                        break
                if matched:
                    break

    # TIER 3: Generic fallback
    if not candidates:
        candidates.append(RankedSense(lemma=lemma, gloss=f"[{lemma}]", score=0.3,
                                      source="dictionary", is_technical=False))

    candidates.sort(key=lambda c: -c.score)

    # Deduplicate by gloss
    seen = set()
    deduped = []
    for c in candidates:
        key = (c.lemma, c.gloss[:30])
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    return deduped[:3]


def build_evidence_text(lemmas: list[str], source: str = "", work_id: str | None = None) -> str:
    """Build structured evidence text for LLM prompt with technical context marking.
    Uses DB-backed lexical_senses for tradition-aware sense selection.
    """
    is_tech = is_technical_context(lemmas)
    work_tradition = query_work_tradition(work_id) if work_id else ""

    lines = []
    if is_tech or work_tradition:
        tradition_note = work_tradition.capitalize() if work_tradition else "Kashmir Shaiva"
        lines.append(f"[CONTEXT: This text belongs to the {tradition_note} tradition. Technical terms should be understood in their {tradition_note} philosophical sense.]")
        lines.append("")

    for lemma in lemmas[:12]:
        ranked = rank_senses(lemma, lemmas, work_id)
        if ranked:
            best = ranked[0]
            if best.is_technical and best.score >= 0.85:
                marker = " (TECHNICAL TERM)" if best.score >= 0.9 else ""
                note = best.gloss.split("—")[0].strip() if "—" in best.gloss else best.gloss
                lines.append(f"  {lemma}: {note}{marker}")
            else:
                lines.append(f"  {lemma}: {best.gloss}")
            # Show alternatives if they're high-confidence
            if len(ranked) > 1 and ranked[1].score > 0.5 and best.score - ranked[1].score < 0.3:
                alt = ranked[1]
                lines.append(f"    (also: {alt.gloss} — {alt.source})")
        else:
            lines.append(f"  {lemma}: [unrecognized]")

    return "\n".join(lines)
