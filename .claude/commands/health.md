---
description: Run the full health gate and summarise it
allowed-tools: Bash(python check_health.py)
---

Run `python check_health.py`. Report in three lines: modules/schemas/fallback counts, test summary
(passed/failed/total), and the first failing test with its one-line error if any. If the total differs
from the baseline in CLAUDE.md §1, say so explicitly.
