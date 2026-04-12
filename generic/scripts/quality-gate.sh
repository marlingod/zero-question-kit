#!/bin/bash
# quality-gate.sh — Universal quality gate for TaskCompleted hook
# Auto-detects project type and runs appropriate checks
# Exit 2 = reject completion | Exit 0 = allow

set -e
ERRORS=""

# ── Python ──
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
    if command -v pytest &>/dev/null; then
        if ! python -m pytest --quiet --tb=no 2>/dev/null; then
            ERRORS="${ERRORS}\n❌ Python tests failing"
        fi
    fi
    if command -v black &>/dev/null; then
        if ! black --check --quiet . 2>/dev/null; then
            ERRORS="${ERRORS}\n❌ Python formatting (run black)"
        fi
    fi
fi

# ── Node/JS/TS ──
if [ -f "package.json" ]; then
    if grep -q '"test"' package.json 2>/dev/null; then
        if ! npm test --silent 2>/dev/null; then
            ERRORS="${ERRORS}\n❌ JavaScript/TypeScript tests failing"
        fi
    fi
    if grep -q '"lint"' package.json 2>/dev/null; then
        if ! npm run lint --silent 2>/dev/null; then
            ERRORS="${ERRORS}\n❌ Lint errors found"
        fi
    fi
fi

# ── Go ──
if [ -f "go.mod" ]; then
    if ! go test ./... -count=1 -short 2>/dev/null; then
        ERRORS="${ERRORS}\n❌ Go tests failing"
    fi
    if ! go vet ./... 2>/dev/null; then
        ERRORS="${ERRORS}\n❌ Go vet found issues"
    fi
fi

# ── Rust ──
if [ -f "Cargo.toml" ]; then
    if ! cargo test --quiet 2>/dev/null; then
        ERRORS="${ERRORS}\n❌ Rust tests failing"
    fi
    if ! cargo clippy --quiet 2>/dev/null; then
        ERRORS="${ERRORS}\n❌ Clippy warnings found"
    fi
fi

# ── Report ──
if [ -n "$ERRORS" ]; then
    echo -e "Quality gate FAILED:${ERRORS}"
    exit 2
fi

echo "✅ Quality gate passed"
exit 0
