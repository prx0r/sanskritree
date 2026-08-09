# DeepSanskrit — Autonomous, Corpus-Connected Sanskrit Philology

## The paradigm shift

**Old model:** Pipeline translates via factor graph + sense ranker + constrained LLM.  
**New model:** DeepSeek is the philologist. The corpus is its library. The multipass process is its method.

DeepSeek can already jointly reason over morphology, syntax, compounds, genre, doctrinal context, authorial terminology, nearby passages, philosophical coherence, and ordinary vs technical meaning. Reducing all that to `tradition_proximity = 0.9` in a hand-built ranker was absurdly lossy.

## The process

```
entire clean text
+ surrounding passages
+ title, author and tradition
+ related texts
+ dictionaries and commentaries
+ existing translations of parallel works
+ full corpus search
        ↓
DeepSeek produces best complete first translation (Pass 1)
        ↓
DeepSeek builds whole-work concept map (Pass 2)
        ↓
DeepSeek revises using full-work understanding (Pass 3)
        ↓
DeepSeek investigates uncertainties via corpus search (Pass 4)
        ↓
Adversarial review attacks the translation (Pass 5)
        ↓
Comparative review against references (Pass 6)
        ↓
Stylistic and terminological revision (Pass 7)
```

## Pass details

### Pass 1 — Global translation
Give DeepSeek the work in coherent chapter-sized windows with title, author, historical context, preceding chapter summary, overlapping Sanskrit context, source metadata. Ask for the best translation it can produce. No constraints, no forced literal first pass, no ban on commentary.

### Pass 2 — Whole-work understanding
After Pass 1, ask DeepSeek to construct an evolving account of: central doctrines, technical vocabulary, recurring metaphors, ritual structures, named deities and practices, internal cross-references, how concepts change by context, unresolved passages. This becomes a living model of the work.

### Pass 3 — Retrospective revision
Give DeepSeek the full first translation, the whole-work concept map, later occurrences of important terms, and inconsistencies detected across chapters. Ask it to revise earlier passages now that it understands the whole work.

### Pass 4 — Corpus investigation
Let the model generate its own research queries: find occurrences of a term, compare grammatical constructions, retrieve definitions, locate commentarial glosses, contrast usage across texts. The system executes those searches and returns evidence. DeepSeek decides what it needs to investigate.

### Pass 5 — Adversarial review
Attack the translation: identify mistranslated compounds, find missing words, detect doctrinal assumptions, test alternative parses, compare Sanskrit and English clause by clause, challenge suspiciously fluent passages, search for internal contradictions. Let the primary translator respond and revise.

### Pass 6 — Comparative review
Compare against Sanskrit commentaries, editions and apparatus, parallel passages, related tantras, partial scholarly translations, quotations in later literature. Do not automatically obey any one source — let DeepSeek reason about disagreement.

### Pass 7 — Stylistic and terminological revision
Only after meaning stabilizes: improve English, harmonize recurring terminology where appropriate, preserve meaningful variation where the Sanskrit varies, add notes, distinguish supplied interpretation from explicit text.

## The basic loop

```python
translation = deepseek.translate(work_context)

while meaningful_questions_remain:
    questions = deepseek.identify_weak_points(
        sanskrit=source,
        translation=translation,
        global_model=work_model,
    )
    evidence = corpus.investigate(questions)
    translation = deepseek.reconsider(
        sanskrit=source,
        current_translation=translation,
        evidence=evidence,
        full_work_context=work_model,
    )
```

## What to build next

### Keep (from current pipeline)
- Clean work and passage ingestion
- Stable passage references
- Source edition provenance
- Full-text search
- Lemma and normalized search
- Chapter-context assembly
- Prompt/run versioning
- Saved translation revisions
- Comparison and diff tools
- Commentary alignment when available
- External corpus adapters (SARIT, GRETIL, Muktabodha)

### Pause
- Hand-building hundreds of lexical senses
- Elaborate tradition-distance scores
- Fixed semantic planners
- Prescriptive sense ranking
- Artificial C0/C1/C2 experiments
- Passage-level translation before whole-work understanding

### Build next

1. **Work-context assembler** — automatically provide previous passages, following passages, chapter summary, glossary inferred from previous translation, unresolved questions, relevant same-work occurrences.

2. **Revision ledger** — store every pass (draft_01_initial through draft_05_final) with diffs and reasons for major changes.

3. **Corpus research tools** — allow the model to request searches itself rather than feeding it preselected glossary results: exact phrase, normalized, lemma sequence, compounds, same-author, same-work, commentaries, parallel citations, definitions, editions, adjacent context.

4. **Global concept memory** — maintain a compact document updated after every chapter: what the work has established, technical terminology encountered, characters/deities/mantras, translation conventions, cross-references, open interpretive questions.

5. **Automated critic passes** — specific adversarial prompts examining grammar, compounds, doctrine, omissions, internal consistency, corpus evidence.

## What Sanskritree becomes

Not a pipeline that translates via hand-built rules. An autonomous, corpus-connected Sanskrit philologist. It creates a complete interpretation, rereads the entire work, investigates its own uncertainties across primary and secondary sources, invites adversarial criticism, and repeatedly revises the translation toward a defensible edition.

**DeepSeek is not a renderer at the end of our pipeline. DeepSeek is the philologist. The database, morphology, corpora and search tools are its library.**

## The first real target

Pick a clean, genuinely untranslated work. Run DeepSeek across it with rich context. Once you have the full draft, inspect what actually goes wrong. The work itself will tell you what tools are needed.

## The project's credible value

Not "better Sanskrit translation than the LLM." But:
- Verified source text with edition tracking
- Passage boundaries and structure
- Morphology and compound analysis
- Commentary and parallel-use retrieval
- Claim-level evidence and citation
- Uncertainty flags on genuinely ambiguous passages
- Consistent final edition across hundreds of verses
- Human correction memory
- Multipass audit trail
