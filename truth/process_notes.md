# Translation Process Notes — from Sambandhasiddhi

## 1. Finding Source Texts

### What worked:
- **Sanskrit Wikisource** (sa.wikisource.org) — found Sambandhasiddhi in Devanagari with variant readings
- **GRETIL** — directory listing blocked (403), specific file paths dead (404). Old URL patterns (siddhitr.htm, utpsiddh.htm) no longer work
- **Muktabodha** — new site requires JavaScript; old etexts site (etexts.muktabodha.org) unreachable
- **Archive.org** — no Sambandhasiddhi found via search

### Best source discovery path:
1. Try Sanskrit Wikisource first (sa.wikisource.org/wiki/{title})
2. Then GRETIL (but need to know exact filenames — try common patterns)
3. Then Muktabodha digital library
4. Then Archive.org KSTS editions
5. If all fail, check the truth files — they often contain references to where texts were found

### For future texts:
- Devanagari title on Wikisource: सम्बन्धसिद्धिः
- File was at: https://sa.wikisource.org/wiki/सम्बन्धसिद्धिः
- HTML contained embedded Devanagari — need to extract clean text from the page

## 2. Text Preparation

### Raw text extraction
- Wikisource HTML has mixed content (navigation, formatting, metadata)
- Need to extract just the Sanskrit text
- Variant readings marked in brackets: [ख. पु. ...] and [क. पु. ...]
- Page breaks marked as (प्. २), (प्. ३), etc.
- Verses are indented with tabs
- Prose sections are the auto-commentary (Vṛtti)

### IAST transliteration
- Devanagari needs to be transliterated to IAST for analysis
- Can use Python libraries (indic-transliteration) or manual conversion
- Key: preserve variant readings
- For this translation, I worked from the IAST directly (generated mentally)

## 3. Translation Protocol (from truthagent §4)

### Step A — Establish the text
- Record: edition, source, variant readings, commentary used, references
- No secondary paraphrases when Sanskrit is available

### Step B — Parse before interpreting
- Sandhi resolution (break compounds)
- Identify compounds and their types
- Case relations (who does what to whom)
- Verb and subject
- Ambiguous syntax
- Technical vocabulary (sambandha, prakāśa, vimarśa, etc.)

### Step C — Three translations (keep separate)
1. **Literal** — as close to syntax as possible. Purpose: show exactly what the Sanskrit says
2. **Philosophical** — readable while preserving inferential structure. Purpose: show the argument
3. **Doctrinal** — interpretation favoured by the school. Purpose: show how the tradition reads it

### Step D — Record translation risk
- Terms whose translation the argument depends on
- No fixed English equivalent across contexts
- For Sambandhasiddhi: sambandha (relation/connection), prakāśa (light/manifestation), vimarśa (reflexive awareness/apprehension), parāmarśa (reflexive grasp), svasaṃvedana (self-awareness), ābhāsa (appearance/manifestation), aikātmya (identity/oneness)

### Step E — Argument reconstruction (per passage)
1. Identify the explanandum (what needs explaining)
2. Reconstruct the weakest argument (charitable minimum)
3. Identify every strengthening move (each arrow is a separate problem)
4. Build the cheapest countermodel (rival explanation with fewer commitments)
5. Attempt discrimination (what observation would distinguish them)

### Step F — Annotate each verse
- Opponent reconstructed (whose view is being argued against)
- Precise explanandum (exactly what phenomenon is being explained)
- Suppressed premise (what must be true for the argument to work)
- Cheapest viable countermodel (the simplest rival explanation)

## 4. Truthmap Packet Creation

### The format
The truthmap expects specific JSON formats:
- **Information packet**: claims with claim_id, source_span, claim_text, targets, tradition_scope, paradigm, evidence_dimension, pramana, nn_expr, hetu, sadhya, vyapti_statement, vyapti_confidence, log_bayes_factor, w_rel, w_map, w_aux, falsifier, reasoning
- **Source map**: maps packet claims to candidates/cruxes/bridges; has nnexpr_mappings, argument_edges, structural_correspondences, directional_critique_pairs
- **Dossier**: defines the question, candidate explanations with hard-to-vary cores
- **Contention benchmark**: regression test with expected/forbidden outcomes

### Key gotchas (from debugging):
- Falsifier types: only `prasanga`, `arthapatti`, `empirical`, `formal`, `philological`, `phenomenological`, `semantic`, `operational` are valid (not `anumana`)
- Falsifier statuses: only `untested`, `tested_survived`, `tested_failed`, `not_currently_testable`, `unfalsifiable` are valid (not `pending`)
- Structural correspondences need: `left_term`, `left_scope`, `right_term`, `right_scope`, `shared_structure`, `important_difference`, `status`, optionally `bridge_probe_id`
- Open crux matching in benchmarks checks exact string against crux node `statement` field, which defaults to the crux ID (e.g., `crux:ambiguity-of-sarva-in-sarvarthasamvidam`)
- Bridge probe ID in correspondence overrides auto-generated ID
- Gate outcomes in source maps must match actual gate results (use `accepted`, `accepted_with_penalty`, `needs_review`, `hollow`, `outside_formal`, `refuted`)

### Ingestion command sequence:
```bash
# 1. Gate the claims
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 /root/projects/clean/scripts/nyaya-truthmap-gate.py /root/projects/clean/content/information-packets/{packet}.json

# 2. Ingest the dossier
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 /root/projects/clean/scripts/ingest-dossier.py --dossier /root/projects/clean/content/source-metaphysics/{dossier}.json

# 3. Run the contention benchmark
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 /root/projects/clean/scripts/evaluate-contention.py --benchmark /root/projects/clean/content/contention-benchmarks/{benchmark}.json

# 4. Run all tests
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest discover -p 'test*.py'
```

## 5. Final Assessment of the Session

### What worked
1. **Truthmap ingestion** — once the JSON format was debugged, the gate correctly flagged weak arguments and the state-of-play synthesis produced correct verdicts
2. **Manual translation** — for short philosophical texts (13-27 verses), direct translation with argument reconstruction is more efficient than pipeline processing
3. **Source discovery** — Wikisource, GRETIL dataset, and Archive.org were the most reliable text sources
4. **Hermes/Codex loop** — proven by Q17 Loops 7-10 but not used in this session

### What didn't work
1. **The Siddhitrayī texts don't contain the missing proof** — all translations converged on this. APS asserts without proving, SS assumes the framework, IS is deliberately dualistic
2. **Sanskritree pipeline wasn't needed** — the texts were short enough for manual translation, and the factor graph wouldn't have helped with argument reconstruction
3. **Source accessibility** — Muktabodha requires JS+Cloudflare, GRETIL URLs are dead, TITUS has empty directories. Wikisource and the GRETIL JSON dataset were the only reliable sources

### Lesson for future agents
Don't translate more Sanskrit looking for the missing nondual proof. It's not in any text — it's a philosophical problem (perspectival partition) that every theory faces. The truthmap now encodes this problem. Use it.

## 6. What Sambandhasiddhi Established

### Strong results:
- Relation is not reducible to convention, spatial contiguity, or causal dependence
- Relation = the intrinsic unity of what appears as multiple within a single cognitive act
- This unity is a function of consciousness's reflexive nature (vimarśa/parāmarśa)
- The knower is unified within each cognitive act — divided attention would split the subject

### Does not independently prove:
- That all cognitive acts belong to one universal subject
- That entities' essence is consciousness (cinmātravapus) — asserted from Pratyabhijñā framework

### Next text: Īśvarasiddhi
- May contain the transition from agency to Lordship
- The missing premise for universalization may be in the Lordship argument
