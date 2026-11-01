---
description: Record a completed milestone in CLAUDE.md §1 and PROJECT_STATE.md
argument-hint: <short milestone title>
---

Milestone: $ARGUMENTS

1. Run `python check_health.py` and take the counts from its output (never from memory).
2. Update CLAUDE.md §1 (version, active phase, baseline line). Keep §1 under 10 lines.
3. Append one entry at the top of PROJECT_STATE.md, in English: date (YYYY-MM-DD), title, 3–6 bullets
   of what changed with file paths, test count. No marketing words, no emoji.
4. If README.md or AGENTS.md quote a test count, update it to the same number.
5. Show the diff of the docs and stop. Do not commit.
