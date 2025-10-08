#!/usr/bin/env python
"""CI/Pre-commit guard: enforce 99 char physical line length across source tree."""
from __future__ import annotations

import sys
from pathlib import Path

MAX = 99
ROOTS = ["src"]

violations: list[str] = []

for root in ROOTS:
    for path in Path(root).rglob("*.py"):
        # Skip generated cache / compiled leftovers just in case
        if "__pycache__" in path.parts:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            length = len(line)
            if length > MAX:
                violations.append(f"{path}:{lineno}: {length} > {MAX}")

if violations:
    print("Line length violations:")
    print("\n".join(violations))
    sys.exit(1)

print("Line length check passed (<= 99 chars).")
