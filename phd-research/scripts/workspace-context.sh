#!/bin/bash
# workspace-context.sh — SessionStart hook
# Gathers "stable facts" about the repo and injects them into the environment
# This is Raschka's Component 1: Live Repo Context
#
# Outputs to CLAUDE_ENV_FILE so Claude has workspace state on every turn

ENV_FILE="${CLAUDE_ENV_FILE:-/dev/null}"

# ── Git State ──
if git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
    echo "GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)" >> "$ENV_FILE"
    echo "GIT_BRANCH=$(git branch --show-current 2>/dev/null)" >> "$ENV_FILE"
    echo "GIT_STATUS_SHORT=$(git status --short 2>/dev/null | head -20 | tr '\n' '|')" >> "$ENV_FILE"
    echo "GIT_RECENT_COMMITS=$(git log --oneline -5 2>/dev/null | tr '\n' '|')" >> "$ENV_FILE"
    echo "GIT_CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null | tr '\n' '|')" >> "$ENV_FILE"
    echo "GIT_STAGED_FILES=$(git diff --cached --name-only 2>/dev/null | tr '\n' '|')" >> "$ENV_FILE"
fi

# ── Project Type Detection ──
PROJECT_TYPE="unknown"
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
    PROJECT_TYPE="python"
elif [ -f "package.json" ]; then
    PROJECT_TYPE="node"
elif [ -f "go.mod" ]; then
    PROJECT_TYPE="go"
elif [ -f "Cargo.toml" ]; then
    PROJECT_TYPE="rust"
fi
echo "PROJECT_TYPE_DETECTED=$PROJECT_TYPE" >> "$ENV_FILE"

# ── Directory Skeleton (top 2 levels, no noise) ──
TREE=$(find . -maxdepth 2 -type d \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/__pycache__/*' \
    -not -path '*/venv/*' \
    -not -path '*/.venv/*' \
    -not -path '*/target/*' \
    -not -path '*/.next/*' \
    -not -path '*/dist/*' \
    -not -path '*/build/*' \
    2>/dev/null | sort | head -40 | tr '\n' '|')
echo "DIR_SKELETON=$TREE" >> "$ENV_FILE"

# ── Active TODOs and Blockers ──
if [ -f "BLOCKER.md" ]; then
    echo "HAS_BLOCKER=true" >> "$ENV_FILE"
fi

TODO_COUNT=$(grep -r "TODO:" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.go" --include="*.rs" . 2>/dev/null \
    | grep -v node_modules | grep -v .git | grep -v __pycache__ | wc -l | tr -d ' ')
echo "TODO_COUNT=$TODO_COUNT" >> "$ENV_FILE"

# ── Test Framework Detection ──
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] && grep -q "pytest" pyproject.toml 2>/dev/null; then
    echo "TEST_FRAMEWORK=pytest" >> "$ENV_FILE"
elif [ -f "jest.config.js" ] || [ -f "jest.config.ts" ]; then
    echo "TEST_FRAMEWORK=jest" >> "$ENV_FILE"
elif [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ]; then
    echo "TEST_FRAMEWORK=vitest" >> "$ENV_FILE"
elif [ -f "go.mod" ]; then
    echo "TEST_FRAMEWORK=go-test" >> "$ENV_FILE"
elif [ -f "Cargo.toml" ]; then
    echo "TEST_FRAMEWORK=cargo-test" >> "$ENV_FILE"
fi

# ── DECISIONS.md last entry (what was the last autonomous decision?) ──
if [ -f "DECISIONS.md" ]; then
    LAST_DECISION=$(tail -5 DECISIONS.md 2>/dev/null | tr '\n' '|')
    echo "LAST_DECISION=$LAST_DECISION" >> "$ENV_FILE"
fi

# ── Wiki Stats (if knowledge base exists) ──
if [ -d "wiki/articles" ]; then
    WIKI_ARTICLES=$(find wiki/articles -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    WIKI_RAW_UNPROCESSED=$(find wiki/raw -name "*.md" -newer wiki/indexes/_index.md 2>/dev/null | wc -l | tr -d ' ')
    echo "WIKI_ARTICLES=$WIKI_ARTICLES" >> "$ENV_FILE"
    echo "WIKI_RAW_UNPROCESSED=$WIKI_RAW_UNPROCESSED" >> "$ENV_FILE"
fi

echo "WORKSPACE_CONTEXT_LOADED=true" >> "$ENV_FILE"
