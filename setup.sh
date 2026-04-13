#!/bin/bash
# setup.sh — Install the Zero-Question Kit into any project
# Usage: ./setup.sh [generic|phd] /path/to/your/project
# 
# Examples:
#   ./setup.sh generic /home/user/my-app
#   ./setup.sh phd /home/user/my-research
#   ./setup.sh generic .    # current directory

set -e

KIT_TYPE="${1:-generic}"
TARGET="${2:-.}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$KIT_TYPE" != "generic" ] && [ "$KIT_TYPE" != "phd" ]; then
    echo "Usage: ./setup.sh [generic|phd] /path/to/your/project"
    echo "  generic  — Universal app/API/fullstack kit"
    echo "  phd      — PhD research kit (lit review, experiments, paper writing)"
    exit 1
fi

# Map kit type to source directory
if [ "$KIT_TYPE" = "phd" ]; then
    SOURCE="$SCRIPT_DIR/phd-research"
else
    SOURCE="$SCRIPT_DIR/generic"
fi

if [ ! -d "$SOURCE" ]; then
    echo "ERROR: Source kit not found at $SOURCE"
    exit 1
fi

echo "═══════════════════════════════════════════════"
echo "  Zero-Question Kit Installer"
echo "  Kit: $KIT_TYPE"
echo "  Target: $(cd "$TARGET" 2>/dev/null && pwd || echo "$TARGET")"
echo "═══════════════════════════════════════════════"

# Create target if it doesn't exist
mkdir -p "$TARGET"

# Copy .claude directory (merge, don't overwrite)
if [ -d "$TARGET/.claude" ]; then
    echo "⚠  .claude/ already exists — merging (won't overwrite existing files)"
    cp -rn "$SOURCE/.claude/." "$TARGET/.claude/" 2>/dev/null || true
else
    cp -r "$SOURCE/.claude" "$TARGET/.claude"
fi

# Copy CLAUDE.md (only if not present)
if [ ! -f "$TARGET/CLAUDE.md" ]; then
    cp "$SOURCE/CLAUDE.md" "$TARGET/CLAUDE.md"
    echo "✅ Created CLAUDE.md — EDIT THIS with your project details"
else
    echo "⚠  CLAUDE.md already exists — skipping (review $SOURCE/CLAUDE.md for additions)"
fi

# Copy DECISIONS.md (only if not present)
if [ ! -f "$TARGET/DECISIONS.md" ]; then
    cp "$SOURCE/DECISIONS.md" "$TARGET/DECISIONS.md"
fi

# Copy scripts
mkdir -p "$TARGET/scripts"
cp -n "$SOURCE/scripts/"* "$TARGET/scripts/" 2>/dev/null || true
chmod +x "$TARGET/scripts/"*.sh 2>/dev/null || true

# Create docs directories
if [ "$KIT_TYPE" = "phd" ]; then
    mkdir -p "$TARGET/docs/literature" "$TARGET/docs/experiments" "$TARGET/docs/papers" "$TARGET/docs/figures"
    mkdir -p "$TARGET/experiments" "$TARGET/results" "$TARGET/src"
else
    mkdir -p "$TARGET/docs/plans" "$TARGET/docs/research" "$TARGET/docs/changelog"
fi

# Bootstrap knowledge base wiki
echo ""
read -p "Initialize knowledge base wiki? (y/N) " INIT_WIKI
if [ "$INIT_WIKI" = "y" ] || [ "$INIT_WIKI" = "Y" ]; then
    bash "$TARGET/scripts/wiki-bootstrap.sh" "$TARGET/wiki"
fi

echo ""
echo "✅ Kit installed! Next steps:"
echo ""
echo "  1. cd $TARGET"
echo "  2. Edit CLAUDE.md (fill in the Quick Config section)"
if [ "$KIT_TYPE" = "phd" ]; then
    echo "  3. Try: /lit-review quantum continual learning"
    echo "     or:  /research-pipeline compare approaches on benchmark datasets"
    echo "     or:  /pre-submission-review"
    echo "     or:  /ingest <URL or file> (add to knowledge base)"
    echo "     or:  /ask <research question> (answer compounds the wiki)"
else
    echo "  3. Try: /ship-feature user authentication with JWT"
    echo "     or:  /deep-research best payment processors for SaaS"
    echo "     or:  /team-build patient appointment scheduling"
    echo "     or:  /scaffold (bootstrap from Quick Config)"
    echo "     or:  /ingest <URL or file> (add to knowledge base)"
    echo "     or:  /ask <question> (answer compounds the wiki)"
fi
echo ""
echo "  Enable agent teams (optional):"
echo "    Add to ~/.claude/settings.json:"
echo '    { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }'
echo ""
