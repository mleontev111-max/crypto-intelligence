# AGENTS

Rules for every human or AI contributor.

## Before work

- Read `START_HERE.md`, `PROJECT_STATE.json`, and current checkpoint.
- Verify current `main`; do not trust stale local state or chat memory.
- Preserve safety boundaries and project constitution.
- If facts are unknown, write `UNKNOWN`; do not guess.

## During work

- Prefer small, reviewable changes.
- Keep RAW data immutable; derived data must be reproducible from known inputs and code/model versions.
- Never rewrite a published forecast or its original evidence snapshot.
- Do not promote a challenger model because it looks better on training data.
- Do not connect real-money execution unless the roadmap explicitly reaches the allowed phase and the owner approves it.

## Before ending work

Every session that materially changes project state must leave a durable handoff in GitHub. Update the checkpoint/state pointers so another contributor can resume without the old chat.

Required checkpoint sections: GOAL, WHAT CHANGED, VERIFIED, UNKNOWN, BLOCKERS, DECISIONS, FILES CHANGED, VALIDATION, SAFETY BOUNDARIES, ONE NEXT ACTION.

If work is partial, checkpoint the partial result rather than hiding it.
