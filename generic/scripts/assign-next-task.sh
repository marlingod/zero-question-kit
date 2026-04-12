#!/bin/bash
# assign-next-task.sh — TeammateIdle hook
# Exit 2 = assign work (keeps teammate active) | Exit 0 = let go idle

# Check for untested changed files
CHANGED=$(git diff --name-only --cached 2>/dev/null || git diff --name-only 2>/dev/null)
if [ -n "$CHANGED" ]; then
    UNTESTED=""
    for f in $CHANGED; do
        case "$f" in
            *test*|*spec*|*__pycache__*|*.json|*.md|*.yml|*.yaml) continue ;;
        esac
        # Check if corresponding test exists
        BASE=$(basename "$f" | sed 's/\.[^.]*$//')
        if ! find . -name "*${BASE}*test*" -o -name "*${BASE}*spec*" 2>/dev/null | grep -q .; then
            UNTESTED="${UNTESTED} ${f}"
        fi
    done
    if [ -n "$UNTESTED" ]; then
        echo "Write tests for these files lacking test coverage:${UNTESTED}"
        exit 2
    fi
fi

# Check for TODO comments that need documentation
if grep -r "TODO: Clarify" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.go" --include="*.rs" . 2>/dev/null | grep -v node_modules | grep -v .git | grep -v target > /dev/null; then
    echo "Document all 'TODO: Clarify' assumptions in DECISIONS.md"
    exit 2
fi

exit 0
