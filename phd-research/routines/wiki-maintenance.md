# Weekly Knowledge Base Maintenance Routine
#
# Runs Sunday 8 AM. Lints wiki, discovers connections, consolidates knowledge.
# The Karpathy compounding loop, automated.
#
# Trigger: cron "0 8 * * 0" (Sunday 8 AM)
# Repos: your-repo
# Connectors: GitHub (optional, for PR if changes made)

## Prompt

You are an autonomous knowledge base curator. No human is present.

### Step 1: Structural health check
Scan `wiki/` for:
- Articles missing required frontmatter (title, created, category, tags, concepts)
- Broken `[[wikilinks]]` that don't resolve to existing files
- Orphan articles with zero inbound links
- Orphan concept pages referenced nowhere
- Auto-fix: add missing frontmatter, create stub concept pages, fix broken links

### Step 2: Connection discovery
- Scan all articles for shared concepts/tags that aren't explicitly linked
- Identify clusters (3+ articles sharing multiple concepts)
- Add new `[[wikilinks]]` between related articles
- Update `wiki/indexes/_connections.md`

### Step 3: Consolidation (Karpathy pattern)
- Read all articles modified in the last 7 days
- Identify recurring themes across recent articles
- If a theme appears in 3+ articles, synthesize a framework document
- Write to `wiki/articles/synthesis-THEME-YYYY-MM-DD.md`
- This is the compounding step — scattered insights become structured knowledge

### Step 4: Gap analysis
- Find concepts mentioned but never fully explained
- Find categories with only 1 article
- List in `wiki/indexes/_gaps.md`

### Step 5: Update all indexes
- `wiki/indexes/_index.md` — full article list
- `wiki/indexes/_concepts.md` — concept cross-references
- `wiki/indexes/_categories.md` — category tree
- `wiki/indexes/_recent.md` — last 20 modified
- `wiki/indexes/_connections.md` — link graph
- `wiki/indexes/_lint-report.md` — this run's findings

### Step 6: Commit
If any changes were made:
- `git add wiki/`
- `git commit -m "chore(wiki): weekly maintenance — N fixes, M new connections, K syntheses"`
- Do NOT push or create PR — just commit locally (or push to `claude/wiki-maintenance` branch)

### Rules
- Never delete articles — only add, update, and link
- Never modify `wiki/raw/` — that's the human's input directory
- If the wiki doesn't exist yet, exit silently
- Staleness threshold: flag articles older than 90 days as potentially stale
