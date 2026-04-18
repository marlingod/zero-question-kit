# Routines — Cloud Automation Templates

Ready-to-use [Claude Code Routines](https://code.claude.com/docs/en/routines) that run autonomously on Anthropic's cloud infrastructure. Your laptop can be closed.

## Setup

### Option A: Web UI
1. Go to [claude.ai/code/routines](https://claude.ai/code/routines)
2. Click **New routine**
3. Paste the prompt from any `.md` file below
4. Add your repo and connectors
5. Set the trigger (cron, API, or GitHub event)

### Option B: CLI
```bash
# Schedule-triggered routines
/schedule nightly code review at 3am

# Then paste the prompt from the template
```

Note: API and GitHub triggers must be configured from the web UI.

## Available Routines

| Routine | Trigger | What It Does |
|---------|---------|-------------|
| `nightly-code-review.md` | Cron: 3 AM daily | Reviews all open PRs for security, quality, style |
| `dependency-audit.md` | Cron: Monday 2 AM | Audits deps, applies safe upgrades, opens PR |
| `wiki-maintenance.md` | Cron: Sunday 8 AM | Lints wiki, discovers connections, synthesizes themes |
| `test-coverage.md` | Cron: Wednesday 4 AM | Finds coverage gaps, writes tests, opens PR |
| `issue-triage.md` | GitHub: issues.opened | Auto-labels, checks duplicates, drafts response |

## Important Notes

- **Routines require**: Pro, Max, Team, or Enterprise plan with Claude Code on the web enabled
- **Daily cap**: 15 runs per account during research preview
- **Branch security**: Claude can only push to branches prefixed `claude/` by default
- **Routines are NOT scripts**: they're agents that reason through problems, not static automation
- **Cost**: routines consume the same token budget as interactive sessions

## Customization

Each `.md` file is a self-contained prompt. Edit the rules section to match your project's conventions. For project-specific context, reference your CLAUDE.md in the routine prompt:

```
Read CLAUDE.md for project conventions, tech stack defaults,
and compliance rules. Apply them to all checks.
```
