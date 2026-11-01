---
description: Produce an implementation plan for a change, with no code written yet
argument-hint: <goal in one sentence>
---

Goal: $ARGUMENTS

Do not edit any file. Read what you need, then answer with exactly these sections:

1. **Understanding**: the goal restated in one sentence, and the reading you chose if it was ambiguous.
2. **Files**: every file to create or change, with `path` and a one-line reason. Mark files you read
   but will not change.
3. **Invariants at risk**: each AGENTS.md principle or CLAUDE.md §5 contract this touches, and how the
   plan keeps it.
4. **Tests first**: the test names to add (characterization tests for moved code, negative tests for
   every "never guess" rule) and the file each goes in.
5. **Steps**: numbered, each small enough to keep `python check_health.py` green after it.
6. **Open questions**: only those that change the design. If none, say "none".
