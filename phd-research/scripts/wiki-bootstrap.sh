#!/bin/bash
# wiki-bootstrap.sh — Initialize the knowledge base wiki structure
# Usage: ./scripts/wiki-bootstrap.sh [wiki-name]
# Default wiki name: "wiki"

set -e

WIKI_DIR="${1:-wiki}"

echo "═══════════════════════════════════════════════"
echo "  Knowledge Base Wiki Bootstrap"
echo "  Directory: $WIKI_DIR/"
echo "═══════════════════════════════════════════════"

# Create directory structure
mkdir -p "$WIKI_DIR/raw/articles"
mkdir -p "$WIKI_DIR/raw/papers"
mkdir -p "$WIKI_DIR/raw/repos"
mkdir -p "$WIKI_DIR/raw/datasets"
mkdir -p "$WIKI_DIR/raw/images"
mkdir -p "$WIKI_DIR/raw/notes"
mkdir -p "$WIKI_DIR/articles"
mkdir -p "$WIKI_DIR/concepts"
mkdir -p "$WIKI_DIR/indexes"
mkdir -p "$WIKI_DIR/outputs/articles"
mkdir -p "$WIKI_DIR/outputs/slides"
mkdir -p "$WIKI_DIR/outputs/charts"

# Create master index
cat > "$WIKI_DIR/indexes/_index.md" << 'EOF'
---
title: Master Index
type: index
auto-generated: true
---

# Wiki Index

_Auto-generated. Do not edit manually — managed by the knowledge-base skill._

## Articles

<!-- Articles will be listed here alphabetically -->

| Article | Category | Created | Concepts |
|---------|----------|---------|----------|

## Stats
- Total articles: 0
- Total concepts: 0
- Total words: ~0
- Last updated: ---
EOF

# Create concepts index
cat > "$WIKI_DIR/indexes/_concepts.md" << 'EOF'
---
title: Concept Index
type: index
auto-generated: true
---

# Concepts

_Auto-generated. Each concept links to all articles that discuss it._

<!-- Concepts will be listed here -->
EOF

# Create categories index
cat > "$WIKI_DIR/indexes/_categories.md" << 'EOF'
---
title: Category Tree
type: index
auto-generated: true
---

# Categories

_Auto-generated category hierarchy._

<!-- Categories will be listed here -->
EOF

# Create recent index
cat > "$WIKI_DIR/indexes/_recent.md" << 'EOF'
---
title: Recent Changes
type: index
auto-generated: true
---

# Recently Modified

_Last 20 articles added or modified._

<!-- Recent articles will be listed here -->
EOF

# Create connections index
cat > "$WIKI_DIR/indexes/_connections.md" << 'EOF'
---
title: Connection Map
type: index
auto-generated: true
---

# Cross-Article Connections

_Auto-generated map of inter-article links._

<!-- Connections will be listed here as:
Article A → Article B (shared concepts: X, Y)
-->
EOF

# Create a welcome/readme article
cat > "$WIKI_DIR/articles/welcome.md" << 'EOF'
---
title: Welcome to the Knowledge Base
created: $(date +%Y-%m-%d)
category: meta
tags: [wiki, getting-started]
concepts: [knowledge-management]
status: published
---

# Welcome to the Knowledge Base

## Summary
This is a self-compounding LLM-managed knowledge base. Add raw sources, and the LLM compiles them into interconnected wiki articles. Every exploration grows the wiki.

## How to Use

### Adding Knowledge
1. Drop files into `wiki/raw/` (articles, papers, repos, datasets, notes)
2. Run `/ingest` or `/ingest all` to compile them into wiki articles
3. Or run `/ingest <URL>` to fetch and compile a web page

### Asking Questions
- Run `/ask <your question>` — the answer becomes a new wiki article
- Every answer compounds the wiki with new connections

### Maintaining Quality
- Run `/lint-wiki` to health-check the wiki
- Auto-fixes broken links, missing indexes, stale frontmatter
- Suggests new connections and identifies gaps

## Connections
- [[Concept: knowledge-management]]
EOF

# Create the knowledge-management concept page
cat > "$WIKI_DIR/concepts/knowledge-management.md" << 'EOF'
---
title: "Concept: Knowledge Management"
type: concept
articles: [welcome]
---

# Knowledge Management

The practice of capturing, organizing, and retrieving knowledge for future use.

## Related Articles
- [[welcome]] — Introduction to this knowledge base

## Key Ideas
- Self-compounding knowledge: every exploration adds to the base
- LLM-managed: the AI maintains structure, connections, and quality
- Raw → Compiled → Indexed → Queryable pipeline
EOF

echo ""
echo "✅ Wiki bootstrapped at $WIKI_DIR/"
echo ""
echo "   Structure:"
echo "   $WIKI_DIR/"
echo "   ├── raw/          ← Drop sources here"
echo "   │   ├── articles/"
echo "   │   ├── papers/"
echo "   │   ├── repos/"
echo "   │   ├── datasets/"
echo "   │   ├── images/"
echo "   │   └── notes/"
echo "   ├── articles/     ← Compiled wiki (LLM manages this)"
echo "   ├── concepts/     ← Auto-generated concept pages"
echo "   ├── indexes/      ← Auto-generated navigation"
echo "   └── outputs/      ← Generated content filed back"
echo ""
echo "   Next steps:"
echo "   1. Drop some files into $WIKI_DIR/raw/"
echo "   2. Run: /ingest all"
echo "   3. Run: /ask <your research question>"
echo "   4. Run: /lint-wiki (periodically)"
echo ""
