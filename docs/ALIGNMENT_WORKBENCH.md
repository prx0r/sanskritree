# Alignment workbench

Open `frontend/v2-alignment.html` locally. It is deliberately source-neutral: reviewers paste an exact reading and one translation, select both spans, select an explicit relation, and record evidence. Notes/commentary are held separately from alignment data.

The export maps directly to the V2 `alignments` table except for `translation_id`, which the ingestion/review API supplies. It supports many-to-many and uncertainty records; it does not make automatic claims about Sanskrit syntax or translator intent.

Before production deployment, the next step is a small authenticated API that accepts only reviewed JSON records, writes `review_events`, and validates the translation's exact `reading_id` provenance.
