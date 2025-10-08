#!/usr/bin/env python3
"""Run the project's line-length checker but show only violations for one file.

Preserves the original checker's exit code so CI behaviour is unchanged while
reducing console noise during local fixes.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """
    Runs a line-length checker script and filters its output to show only violations
    for a specified file.

    The function executes an external line-length checker (default: scripts/check_line_length.py),
    captures its output, and filters the reported violations to include only those that pertain to
    the file provided as an argument. It prints the filtered violations, or a message if none are
    found, and preserves the original exit code of the checker script for CI compatibility.

    Returns:
        int: The exit code from the line-length checker script.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run scripts/check_line_length.py and filter its output to only show "
            "violations that belong to the given file."
        )
    )
    parser.add_argument("file", help="Path to the file to filter violations for")
    parser.add_argument(
        "--checker",
        default="scripts/check_line_length.py",
        help="Path to the line-length checker script",
    )
    args = parser.parse_args()

    target = Path(args.file).resolve()

    # Run the real checker and capture output
    proc = subprocess.run(
        [sys.executable, args.checker], capture_output=True, text=True, check=False
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    if "Line length violations:" not in stdout:
        # No violations printed by checker; show original output and return
        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, file=sys.stderr, end="")
        return proc.returncode

    # Extract violations lines after the header
    lines = stdout.splitlines()
    try:
        header_idx = lines.index("Line length violations:")
    except ValueError:
        header_idx = -1

    violations = lines[header_idx + 1 :] if header_idx >= 0 else lines

    # Filter violations for the target file path
    filtered = []
    for v in violations:
        # Violation format: path:lineno: N > 99
        # Compare resolved path suffix to match inside repo
        parts = v.split(":", 1)
        if not parts:
            continue
        path_part = parts[0]
        try:
            p = Path(path_part).resolve()
        except OSError:
            # If path can't be resolved, fallback to simple substring match
            if str(target).endswith(path_part) or path_part.endswith(str(target.name)):
                filtered.append(v)
            continue

        if p == target or p.samefile(target) if p.exists() and target.exists() else p == target:
            filtered.append(v)
        else:
            # also allow matching by suffix inside the repo
            if str(p).endswith(str(target)) or str(p).endswith(target.name):
                filtered.append(v)

    # Print filtered results
    if filtered:
        print("Filtered violations for:", target)
        print("\n".join(filtered))
    else:
        print(f"No line-length violations found for: {target}")

    # Print stderr if present to not lose diagnostic info
    if stderr:
        print(stderr, file=sys.stderr, end="")

    # Preserve the original checker's exit code to keep CI semantics
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
