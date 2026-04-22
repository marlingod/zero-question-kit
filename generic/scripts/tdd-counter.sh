#!/usr/bin/env bash
# tdd-counter.sh — mechanical iteration cap for TDD loops
#
# Called by PreToolUse hook on Bash commands matching pytest/jest/go test.
# Tracks failed test runs per-session in .claude/.tdd-state and blocks
# further test invocations after N failures.
#
# Prompt-level iteration caps get ignored past turn 4.
# This hook cannot be ignored — it blocks the tool call itself.

set -euo pipefail

STATE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude"
STATE_FILE="$STATE_DIR/.tdd-state"
MAX_FAILURES="${ZQK_MAX_TEST_FAILURES:-3}"

mkdir -p "$STATE_DIR"

# Initialize or read state
if [[ ! -f "$STATE_FILE" ]]; then
    echo "failures=0" > "$STATE_FILE"
fi

# shellcheck disable=SC1090
source "$STATE_FILE"

# Check if we've hit the cap
if [[ "${failures:-0}" -ge "$MAX_FAILURES" ]]; then
    cat <<EOF >&2
╔═══════════════════════════════════════════════════════════════╗
║  TDD ITERATION CAP REACHED ($MAX_FAILURES failed test runs)                 ║
╠═══════════════════════════════════════════════════════════════╣
║  Further test invocations are blocked in this session.        ║
║                                                                ║
║  Required action:                                              ║
║    1. Stop trying to fix the current approach                 ║
║    2. Write docs/blockers/YYYY-MM-DD-TASK.md with:           ║
║       - what you were trying to do                            ║
║       - what you tried across all iterations                  ║
║       - what you suspect is actually wrong                    ║
║    3. Mark failing tests xfail/skip with blocker link         ║
║    4. Commit partial progress                                  ║
║    5. Hand control back to the user                            ║
║                                                                ║
║  To reset the counter:                                         ║
║    rm $STATE_FILE                                  ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    exit 1  # Blocks the tool call
fi

exit 0
