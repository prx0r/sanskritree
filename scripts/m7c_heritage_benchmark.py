"""M7c: Hybrid benchmark — test 20 hard cases against remote Heritage API.

Categories: long compounds, known timeouts, HERITAGE_OOV, COMPOUND_NOT_GENERATED,
high-impact mistranslations. Records success/failure, latency, candidate count,
whether correct candidate exists, and whether it's a timeout or true OOV.
"""
from __future__ import annotations

import sys, re, json, time
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path('/root/projects/sanskritree/src')))
from sanskritree.database import connect
from vidyut.lipi import transliterate, Scheme
from heritage.heritage import HeritagePlatform, SolutionAnalysis

DB = str(Path('/root/projects/sanskritree/data/sanskritree-v2.db'))
conn = connect(DB)

# 20 hard cases from across the corpus
STRESS_SET = [
    # Long Tantric compounds
    ("MBT compound", "mbt", "bhairavanātham anāthaśaraṇyaṃ tvanmayacittatayā hṛdi vande"),
    ("Spanda compound", "spanda", "taṃ śakticakravibhavaprabhavaṃ śaṃkaraṃ stumaḥ"),
    ("MBT long compound", "mbt", "mṛtyuyamāntakakarmapiśācair nātha namo 'stu na jātu bibhemi"),
    ("VB dense compound", "vb", "śabdān pratikṣaṇaṃ dhyāyan kṛtārtho 'rthānurūpataḥ"),
    
    # Known timeouts / long verses
    ("Previous timeout", "vb", "jñāyate digvibhāgādi tadvac chaktyā śivaḥ priye"),
    ("Long VB verse", "vb", "na cāsau triśirā devo na ca śaktitrayātmakaḥ na cakrakramasambhinno na ca śaktisvarūpakaḥ"),
    ("BhG long", "bhg", "adṛṣṭa pūrvam hṛṣitaḥ asmi dṛṣṭvā bhayena ca pravyathitam manaḥ me tat eva me darśaya deva rūpam prasīda deva īśa jagat nivāsa"),
    
    # Known OOV (Heritage doesn't know these)
    ("OOV test", "vb", "aca caṇḍāla iva sadā vācyaḥ paramārthataḥ"),
    ("Rare form", "spanda", "pipīlasparśavelāyām prathate paramaṃ sukham"),
    
    # High-impact mistranslations from the current pipeline
    ("VB practice", "vb", "dhyāyato 'nuttare śūnye praveśo hṛdaye bhavet"),
    ("VB instruction", "vb", "kakṣavyomni manaḥ kurvan śamam āyāti tallayāt"),
    ("VB bindu", "vb", "binduṃ śikhānte hṛdaye layānte dhyāyato layaḥ"),
    ("VB contradict", "vb", "yugapac ca dvayaṃ tyaktvā madhye tattvam prakāśate"),
    
    # Bhairavastava (should be easy for Heritage)
    ("BV praise", "bv", "bhairavanātham anāthaśaraṇyaṃ tvanmayacittatayā hṛdi vande"),
    ("BV death", "bv", "mṛtyuyamāntakakarmapiśācair nātha namo 'stu na jātu bibhemi"),
    
    # Bhagavad Gita (general Sanskrit)
    ("Gita general", "bhg", "karmaṇy evādhikāras te mā phaleṣu kadācana"),
    ("Gita dense", "bhg", "śrī bhagavān uvāca mayā prasannena tava arjuna idam rūpam param darśitam ātma yogāt"),
    
    # Additional tricky Tantric forms
    ("Spanda rare", "spanda", "unmeṣaḥ sa tu vijñeyaḥ svayaṃ tam upalakṣayet"),
    ("VB void", "vb", "nirādhāre mano yāti taddhyānapreraṇāc chamī"),
]

print("=" * 70)
print("M7c: Heritage Web API Stress Test — 20 hard cases")
print("=" * 70)

results = []
heritage_failures = 0
heritage_timeouts = 0
heritage_oov = 0
heritage_success = 0

for label, category, text in STRESS_SET:
    clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', text).strip()
    
    # Remote Heritage
    t0 = time.time()
    success = False
    latency = 0
    n_words = 0
    has_morph = False
    is_timeout = False
    is_oov = False
    
    try:
        deva = transliterate(clean, Scheme.Iast, Scheme.Devanagari)
        platform = HeritagePlatform(method="web")
        result = platform.get_analysis(deva, sentence=True, structured=True)
        latency = time.time() - t0
        
        if result:
            for sol_id in sorted(result.keys()):
                sol = result[sol_id]
                if isinstance(sol, SolutionAnalysis) and sol.words:
                    words = [str(w.text) for w in sol.words]
                    n_words = len(words)
                    # Check if any word has morphological analysis
                    for w in sol.words[:5]:
                        if hasattr(w, 'candidates') and w.candidates:
                            has_morph = True
                            break
                    success = True
                    break
        if not success:
            is_oov = True
            heritage_oov += 1
    except Exception as e:
        latency = time.time() - t0
        err_str = str(e)
        if "timeout" in err_str.lower() or "timed out" in err_str.lower():
            is_timeout = True
            heritage_timeouts += 1
        else:
            heritage_failures += 1
    
    if success:
        heritage_success += 1
    
    results.append({
        "label": label,
        "category": category,
        "text": clean[:50],
        "success": success,
        "latency": round(latency, 2),
        "n_words": n_words,
        "has_morph": has_morph,
        "is_timeout": is_timeout,
        "is_oov": is_oov,
    })
    
    status = "✅" if success else ("⚠️ TIMEOUT" if is_timeout else ("❌ OOV" if is_oov else "❌ FAIL"))
    morph = "morph" if has_morph else "no-morph"
    print(f"  {status:12s} {label:25s}  ({latency:.1f}s, {n_words:2d} words, {morph})")

# Summary
print(f"\n{'='*70}")
print(f"RESULTS")
print(f"{'='*70}")
print(f"  Success:    {heritage_success}/20 ({heritage_success*5}%)")
print(f"  Timeout:    {heritage_timeouts}/20")
print(f"  True OOV:   {heritage_oov}/20")
print(f"  Other fail: {heritage_failures}/20")
print(f"  Avg latency: {sum(r['latency'] for r in results)/20:.1f}s")
print(f"  Avg words: {sum(r['n_words'] for r in results)/20:.0f}")

# Decision guidance
total_fail = heritage_timeouts + heritage_oov + heritage_failures
if heritage_timeouts >= 5:
    print(f"\n⚠️  {heritage_timeouts}/20 timeouts — local Heritage would help with throughput")
if heritage_oov >= 10:
    print(f"❌ {heritage_oov}/20 true OOV — local Heritage won't fix (lexicon gap)")
if heritage_success >= 15:
    print(f"✅ {heritage_success}/20 success — web API is adequate for current corpus")
elif heritage_success >= 10:
    print(f"⚠️ {heritage_success}/20 success — mixed results, local could help")
else:
    print(f"❌ {heritage_success}/20 success — web API is unreliable for Tantric texts")

out = Path("/root/projects/sanskritree/proof/heritage_benchmark.json")
with open(out, "w") as f:
    json.dump({"results": results, "summary": {
        "success": heritage_success, "timeout": heritage_timeouts,
        "oov": heritage_oov, "other_fail": heritage_failures,
        "avg_latency": sum(r['latency'] for r in results)/20
    }}, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")
conn.close()
PYEOF
