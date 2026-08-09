# Post-Mortem / Summary Notes

## What We Actually Built vs What We Thought We Were Building

### Original thesis (from THESIS.md)
> Formal derivation from Sanskrit philosophical texts to machine-verifiable proofs.

Three systems were built toward this:
- **Sanskritree** — factor graph translation pipeline (10 works, 59 tests)
- **Truth files** — strategic research, translation protocol, comparative analysis
- **Truthmap** — Nyaya-gated claim engine, bridge probes, contention benchmarks

### What actually happened

The project set out to test whether Utpaladeva has a non-circular argument from local reflexivity to one universal subject. After translating all three Siddhitrayī texts and running them through the truthmap engine, the finding is:

**The Siddhitrayī texts do not contain the missing nondual proof.** All three translations converged on the same result:
- *Ajadapramātṛsiddhi*: asserts universalization but the quantifier scope of "sarvārthasaṃvidām" is ambiguous. Abhinavagupta himself limits anusandhāna to one body (Tantrāloka 16.242).
- *Sambandhasiddhi*: assumes the Pratyabhijñā ontology (cinmātravapus) rather than arguing for it. Its theory of relation as consciousness's self-unifying activity is consistent with universal consciousness but does not prove it.
- *Īśvarasiddhi*: deliberately dualistic design argument. Verse 56 defers the nondual proof to "elsewhere" (the ĪPK).

This was valuable — it saved someone from translating more texts looking for the missing argument. But the answer is: it's not in the Siddhitrayī.

**Checkpoint 10 then reframed the entire project.** The problem isn't "is consciousness one or many?" — it's "what establishes the domains within which manifestation is jointly present and outside which it is absent?" Every theory converges on the same missing object: Λ, the law of perspectival partition.

## Were the Systems Actually Useful?

### Truthmap: ✅ Genuinely useful
The Nyaya gate, state-of-play synthesis, and contention benchmarks worked as intended:
- Gate correctly identified weak vyapti on all 3 universalization claims
- State-of-play correctly ranked Nyāya as leader and Pratyabhijñā as pressured
- Bridge probes correctly defaulted to OVERLAPS
- 61 tests, 5 contention benchmarks, all passing
- The perspectival partition benchmark has 4 source maps, 13 claims, 5 candidates

The truthmap provided machine-verifiable verdicts for debates that would otherwise be purely verbal. The perspectival partition benchmark now encodes Checkpoint 10's 10 contentions as testable regression guards.

### Truth files: ✅ Genuinely useful
- truthagent provided the translation protocol that was actually followed
- truthadvice provided the 4-dossier strategy (even though the nondual proof wasn't there)
- truthtranslation provided the completed APS translation
- checkpointcharlie provided the final reframing that changed the project's direction

These files functioned as the project's strategic intelligence. Every useful direction came from them.

### Sanskritree pipeline: ⚠️ Not used for this problem
The factor graph, semantic plans, and English renderer were not used. The translations in this session were done manually — reading Sanskrit Wikisource or the GRETIL dataset and producing three-tier translations. This was the right call: the texts are short philosophical arguments (not corpus-scale), and the manual translation produced higher-quality argument reconstruction.

Sanskritree's value was as a **text repository** (we used its sources/ directory and truth/ directory extensively) and as a **reference for how translations should be structured** (the truthtranslation format). The pipeline itself is more suited to large-scale text processing than the targeted philosophical translation we needed.

## What We Have Now

### In the truthmap (clean project) — all new this session:
| File | Purpose |
|------|---------|
| `q-perspectival-partition.argument.json` | Dossier with 5 candidates across traditions |
| `q-perspectival-partition.sheaf-map.json` | Sheaf-theoretic gluing constraint |
| `q-perspectival-partition.saiva-decombination-map.json` | Bind from translated Siddhis |
| `q-perspectival-partition.scientific-exclusion-map.json` | IIT/lesion/split-brain constraints |
| `q-perspectival-partition.constructed-ownership-map.json` | Ownership decomposition |
| `perspectival-partition-sheaf-gluing-claims.json` | Sheaf objection + privacy + meta-claim |
| `saiva-decombination-bind-claims.json` | 4 claims from 3 Siddhis + trilemma |
| `scientific-exclusion-principles-claims.json` | IIT/lesion/non-transitive unity |
| `constructed-ownership-claims.json` | P decomposition + mattering hypothesis |
| `q-perspectival-partition.benchmark.json` | 5 live candidates, 3 cruxes, all constrained |

### In Sanskritree/truth/ — translations:
| File | Content |
|------|---------|
| `truthtranslation` | Ajadapramātṛsiddhi (27 verses) |
| `sambandhasiddhi_translation.md` | Sambandhasiddhi (21 verses) with commentary |
| `isvarasiddhi_translation.md` | Īśvarasiddhi (13 verses) |
| `checkpointcharlie` | Complete reframing (3104 lines) |
| `agent_handoff.md` | Full project state for next agent |

### Skills and process:
- `~/.hermes/skills/research/sanskritree-translate/SKILL.md` — reusable translation protocol
- `process_notes.md` — gotchas from source discovery and ingestion
- `devplan.md` — this file

## What the 5 Contention Benchmarks Currently Say

| Benchmark | Verdict |
|-----------|---------|
| **reflexivity** | 3 positions live (Dignāga, Abhinavagupta, Ñāṇavīra). All compatible at different levels. |
| **Q17** | 3 candidates live (interface, appearance, filter). Recovery wager + phenomenological interview specified. |
| **universalization** | Nyāya leads (1.65), Utpaladeva pressured (-0.99). Bridge = OVERLAPS. |
| **śakti** | Legacy benchmark, passes. |
| **perspectival partition** | 5 candidates live. All converge on missing Λ. Pratyabhijñā most pressured (-0.52 net). |

## The Next Useful Step

The partition problem is now formalized in the truthmap. The remaining Proof-sets from Checkpoint 10 are:

1. **Proof-set 1 — Formal phenomenal topology** — if the partition problem needs mathematical formalization (sheaf theory, hypergraphs)
2. **Proof-set 5 — Vimarśa decomposition** — if clinical dissociation data is wanted to test whether V₁-V₇ dissociate

But honestly, the most important thing that happened this session is that **the project found its real question**: not "does universal consciousness exist?" but "what makes phenomenal domains exclusive?" That question is now encoded in the truthmap and can survive whatever tool is used to work on it.

The Sanskritree pipeline is useful for large-scale text processing. The truthmap is useful for philosophical claim tracking. The truth files are useful for strategy. Use them as needed.
