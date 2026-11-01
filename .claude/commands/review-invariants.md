---
description: Review the current diff against the project invariants (read-only)
argument-hint: [git range, default = working tree]
---

Use the `invariant-reviewer` subagent on the diff `$ARGUMENTS` (empty = uncommitted changes).
Relay its table and verdict unchanged. If the verdict is FAIL, propose the smallest fix for each
blocking row and ask before applying it.
