# START HERE

This file is the canonical entrypoint for every new human or AI contributor.

## Resume protocol

1. Read `PROJECT_STATE.json`.
2. Open the exact `current_checkpoint` referenced there.
3. Verify current `main` HEAD and the checkpoint's `Summarized state SHA`. The checkpoint SHA identifies the project state it summarizes; later checkpoint/pointer-only commits may make current `main` a descendant.
4. Read `AGENTS.md` and `PROJECT_CONSTITUTION.md` before making changes.
5. Read only the architecture/roadmap docs relevant to the selected task.
6. Continue from `one_next_action`; do not invent a new priority unless the current action is blocked or explicitly changed.
7. If canonical files disagree, stop implementation and repair state drift first.

## End-of-session protocol

Before considering work complete:

- record what changed;
- record what was actually verified;
- record UNKNOWNs and BLOCKERs explicitly;
- create or update a dated checkpoint;
- update `CHECKPOINT_INDEX.json`;
- update `PROJECT_STATE.json` so `current_checkpoint` and `one_next_action` are correct;
- record the exact SHA of the state being summarized. Do not attempt to store a checkpoint commit's own SHA inside itself; that is self-referential and impossible.

A chat summary is not a checkpoint. GitHub canonical files are the source of truth for project continuity.
