#!/usr/bin/env bash
# tdd-post-test.sh — update counter based on test result
#
# Called by PostToolUse hook after pytest/jest/go test commands.
# Reads the exit code from the last command and increments/resets the counter.

set -euo pipefail

STATE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude"
STATE_FILE="$STATE_DIR/.tdd-state"
LAST_EXIT="${CLAUDE_TOOL_EXIT_CODE:-0}"

mkdir -p "$STATE_DIR"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "failures=0" > "$STATE_FILE"
fi

# shellcheck disable=SC1090
source "$STATE_FILE"

current="${failures:-0}"

if [[ "$LAST_EXIT" -eq 0 ]]; then
    # Tests passed — reset counter
    echo "failures=0" > "$STATE_FILE"
    echo "✅ Tests passed. TDD counter reset." >&2
else
    # Tests failed — increment counter
    new=$((current + 1))
    echo "failures=$new" > "$STATE_FILE"
    echo "❌ Test run failed ($new/${ZQK_MAX_TEST_FAILURES:-3}). TDD counter incremented." >&2
fi

exit 0
