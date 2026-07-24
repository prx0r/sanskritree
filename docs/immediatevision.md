# Immediate Vision — Checkpoint 1

> The first machine-assisted, fully auditable English translation of a complete Sanskrit work.

## The reframe

Not "build the platform." Not "commentary workbench." Not "120 random passages."

**Translate one complete text. Evaluate it. Publish it. Then explain why commentary matters.**

Everything else should earn its place by making translation measurably better.

## Checkpoint 1 goal

A complete draft translation of the **Spandakārikā (53 verses + Kṣemarāja commentary)** with:
- Every sentence has provenance
- Every lexical decision inspectable
- Uncertainty explicit
- Alternative readings preserved
- Lean verifies structural integrity
- A human scholar can improve it

## The forcing function

Let translation pull architecture into existence. Don't push architecture ahead of demonstrated need.

When translation gets stuck on a compound → build better parsing. When stuck on a word → build better lexical ranking. When commentary is needed → build commentary linking. When a parallel passage is needed → build intertext retrieval.

Each capability arises from a real failure, not from a planned ontology.

## Why Spandakārikā

- 53 verses + Kṣemarāja commentary — manageable
- Already 67% coverage, 370 commentary links in DB
- Stretches the system without breaking it
- Multiple translations exist for comparison, but our contribution is the audit trail + commentary integration
- Short enough to complete in weeks, not years

## What changes

Old path:
```
translate verses → commentary → platform → publish
```

New path:
```
translate ONE COMPLETE TEXT → evaluate → publish → then decide what's next
```

## Decision rule

If we can translate 53 consecutive verses with full audit trail, that's a stronger result than 120 random passages with partial annotation. Consecutive translation reveals discourse phenomena (pronouns, repeated terms, metaphors, topic continuity) that isolated verses never expose.
