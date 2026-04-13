<p align="center">
  <h1 align="center">Zero-Question Kit</h1>
  <p align="center">
    Drop-in autonomy for Claude Code. Give one instruction. Get a finished project back.<br>
    No clarifying questions. No permission prompts. No hand-holding.
  </p>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-the-problem">The Problem</a> •
  <a href="#-two-kits">Two Kits</a> •
  <a href="#-knowledge-base">Knowledge Base</a> •
  <a href="#-ultraplan-integration">Ultraplan</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="SETUP-GUIDE.md">Full Setup Guide</a>
</p>

---

## The Problem

Every AI coding assistant does the same thing: asks you 15 questions before writing a single line of code.

> *"What framework would you like?"*
> *"Should I add tests?"*
> *"Would you prefer REST or GraphQL?"*
> *"Can you confirm you want me to run this?"*

This happens because LLMs are optimized for helpfulness, and the training signal rewards *checking before acting*. The default is to ask. But for builders who know what they want, this creates a bottleneck — you spend more time answering questions than the AI spends building.

**The fix isn't "tell it to stop asking."** The fix is to *eliminate every reason it would need to ask*:

1. **Encode your decisions upfront** → CLAUDE.md
2. **Give it tools to self-resolve** → MCP servers
3. **Teach it reusable workflows** → Skills
4. **Delegate to specialists** → Subagents & Agent Teams
5. **Auto-approve safe actions** → Hooks
6. **Build a self-compounding knowledge base** → Wiki (Karpathy pattern)

This repo packages all of that into **67 drop-in files** across two kits.

---

## Quick Start

```bash
git clone https://github.com/marlingod/zero-question-kit.git
cd zero-question-kit

# For any app project
./setup.sh generic /path/to/your/project

# For PhD research
./setup.sh phd /path/to/your/research

# Then: edit CLAUDE.md, launch Claude Code, go
cd /path/to/your/project
claude
/ship-feature user authentication with JWT
```

See [SETUP-GUIDE.md](SETUP-GUIDE.md) for the detailed walkthrough.

---

## Two Kits

### `generic/` — Any App Project

For web apps, APIs, CLIs, fullstack platforms, data pipelines — anything you build with code. **Auto-detects** your language, framework, and conventions. Fill 6 config fields and everything adapts.

| Command | What Happens |
|---------|-------------|
| `/ship-feature <desc>` | Scans codebase → plans → builds → tests → formats → commits |
| `/deep-research <topic>` | 5+ search angles, 15+ sources, comparison matrix, recommendations |
| `/team-build <feature>` | 5 parallel agents: researcher, backend, frontend, tester, reviewer |
| `/auto-implement <recs>` | Takes research recommendations → creates git worktrees → agent teams per phase |
| `/from-ultraplan` | Bridges Anthropic's [ultraplan](https://code.claude.com/docs/en/ultraplan) to parallel worktree execution |
| `/research-and-build <topic>` | Full loop: research → recommendations → worktrees → agent teams → build |
| `/scaffold` | Bootstraps entire project from your Quick Config |
| `/ingest <URL or file>` | Adds source to self-compounding knowledge base |
| `/ask <question>` | Answers from wiki — answer filed back, wiki grows |
| `/lint-wiki` | Health-checks the knowledge base, finds gaps and connections |

**Included:** 7 skills, 3 subagents, 10 commands, auto-formatting hooks, quality gates, native desktop notifications, workspace context injection, universal settings with pre-approved permissions for Python/Node/Go/Rust.

---

### `phd-research/` — Academic Research

For PhD candidates, research scientists, and anyone doing literature-heavy, experiment-driven work.

| Command | What Happens |
|---------|-------------|
| `/lit-review <topic>` | 20+ papers, classifies, synthesizes, identifies gaps, generates BibTeX |
| `/research-pipeline <topic>` | Full pipeline: lit review → experiment → implementation → results → paper |
| `/pre-submission-review` | 3 simulated harsh reviewers + methodology audit + completeness check |
| `/auto-implement <recs>` | Research recommendations → git worktrees → agent teams per phase |
| `/from-ultraplan` | Bridges Anthropic's ultraplan to parallel execution |
| `/research-and-build <topic>` | Research → recommendations → worktrees → build |
| `/ingest <paper URL>` | Compiles paper into wiki article with backlinks and concepts |
| `/ask <research question>` | Synthesizes from wiki — answer compounds the knowledge base |
| `/lint-wiki` | Broken links, orphan concepts, stale articles, connection suggestions |

**Included:** 7 skills, 3 subagents (methodology-advisor, peer-reviewer, research-engineer), 9 commands, publication-quality figure defaults, LaTeX table generation, native desktop notifications.

---

## Knowledge Base

Inspired by [Andrej Karpathy's LLM knowledge base architecture](https://x.com/karpathy) — a self-compounding markdown wiki where the LLM owns the content and every exploration makes it smarter.

```
wiki/
├── raw/              ← YOU add sources here (papers, URLs, notes)
├── articles/         ← LLM compiles raw → structured wiki articles
├── concepts/         ← LLM auto-generates concept pages with backlinks
├── indexes/          ← LLM maintains navigation (master index, concepts, categories)
└── outputs/          ← LLM files answers back — every question compounds
```

**The compounding loop:**

```
Drop a paper into wiki/raw/
  → /ingest compiles it into a wiki article with backlinks
    → /ask "how does this relate to my hypothesis?"
      → Answer filed back as a NEW article
        → /lint-wiki discovers 3 connections you didn't see
          → Next /ask has richer context
            → Repeat. Wiki grows smarter.
```

The key insight: **you rarely touch the wiki manually.** It's the LLM's domain. At ~100 articles / ~400K words, you have a searchable personal knowledge base that no generic RAG pipeline can match for your domain.

---

## Ultraplan Integration

[Ultraplan](https://code.claude.com/docs/en/ultraplan) is Anthropic's cloud-based planning feature — it drafts implementation plans in the browser with inline comments and iterative revision. Our kit bridges ultraplan's planning to parallel execution:

```bash
# 1. Anthropic plans it (cloud, browser review, inline comments)
/ultraplan migrate the auth service from sessions to JWTs

# 2. You review, comment, iterate in browser
# 3. Click "Approve plan and teleport back to terminal"

# 4. Our kit executes it (worktrees, 5 parallel agents, quality gates)
/from-ultraplan
```

Or skip ultraplan and go straight from research to build:

```bash
# Research produces recommendations → auto-creates worktrees → agent teams build each phase
/research-and-build lab order tracking and result management

# Or feed existing recommendations directly
/auto-implement Phase 1: internal tracking model. Phase 2: external API integration. Phase 3: interoperability layer.
```

Each phase gets its own git worktree. Each worktree gets its own agent team (architect → backend → frontend → tester → reviewer). Phases run in parallel when independent, sequentially when dependent.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR ONE INSTRUCTION                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  CLAUDE.md  │  Decision protocol
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
  │   Skills    │  │  Knowledge  │  │    Hooks    │
  │ (Playbooks) │  │  Base (Wiki)│  │ (Guardrails)│
  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
         │                │                 │
         └────────────────┼─────────────────┘
                          │
         ┌────────────────┼─────────────────┐
         │                │                 │
  ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼──────┐
  │  Subagents  │  │   Agent    │  │  Commands   │
  │ (Delegates) │  │   Teams    │  │ (Triggers)  │
  └──────┬──────┘  └─────┬──────┘  └─────────────┘
         └────────┬───────┘
           ┌──────▼──────┐
           │ MCP Servers  │  External tools
           └─────────────┘
```

| Layer | What | Why It Kills Questions |
|-------|------|----------------------|
| **CLAUDE.md** | Decision protocol with defaults | Claude checks here BEFORE asking |
| **Skills** | Reusable autonomous playbooks | Encodes "how to do X" |
| **Knowledge Base** | Self-compounding wiki | Claude searches wiki instead of asking you |
| **Subagents** | Specialist delegates | Each knows exactly what to do |
| **Agent Teams** | Parallel workforce | Teammates coordinate with each other, not you |
| **MCP Servers** | External tools | Claude looks things up instead of asking |
| **Hooks** | Deterministic guardrails | Auto-approve safe, auto-reject dangerous |
| **Commands** | One-shot triggers | `/command` invokes full autonomous pipeline |

---

## Repository Structure

```
zero-question-kit/
├── README.md                        # This file
├── SETUP-GUIDE.md                   # Step-by-step setup instructions
├── DEEP-DIVE-GUIDE.md               # Technical deep-dive on all 8 layers
├── RASCHKA-UPGRADE.md               # Raschka's 6 components applied to our kit
├── setup.sh                         # One-command installer
├── scripts/
│   └── wiki-bootstrap.sh            # Initialize knowledge base
│
├── generic/                         # ── Any app project ──
│   ├── CLAUDE.md                    # Decision protocol (6-field Quick Config)
│   ├── orchestrator.py              # API-based agentic loop (all 6 Raschka components)
│   ├── scripts/                     # Hook scripts (quality gate, idle assign,
│   │                                # wiki bootstrap, workspace context)
│   └── .claude/
│       ├── settings.json            # Permissions + hooks + MCP + notifications
│       ├── skills/    (7 skills)    # build-feature, code-review, research,
│       │                            # data-pipeline, knowledge-base, wiki-lint,
│       │                            # worktree-manager
│       ├── agents/    (3 agents)    # security-reviewer, test-writer, researcher
│       └── commands/ (10 commands)  # ship-feature, deep-research, team-build,
│                                    # scaffold, auto-implement, from-ultraplan,
│                                    # research-and-build, ingest, ask, lint-wiki
│
└── phd-research/                    # ── Academic research ──
    ├── CLAUDE.md                    # Research domain config
    ├── scripts/                     # Hook scripts
    └── .claude/
        ├── settings.json            # Permissions + hooks + notifications
        ├── skills/    (7 skills)    # lit-review, experiment, paper-writing,
        │                            # data-analysis, knowledge-base, wiki-lint,
        │                            # worktree-manager
        ├── agents/    (3 agents)    # methodology-advisor, peer-reviewer,
        │                            # research-engineer
        └── commands/  (9 commands)  # lit-review, research-pipeline,
                                     # pre-submission-review, auto-implement,
                                     # from-ultraplan, research-and-build,
                                     # ingest, ask, lint-wiki
```

---

## Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Claude Code** | Latest | Latest |
| **Node.js** | 18+ | 20+ |
| **Claude Plan** | Pro (single agent + subagents) | Max (Agent Teams, Opus 4.6) |
| **OS** | macOS, Linux | macOS, Linux |

Install Claude Code: `npm install -g @anthropic-ai/claude-code`

---

## Token Cost Awareness

| Mode | Multiplier | Best For |
|------|-----------|----------|
| Single agent + skills | 1x | Most daily work |
| With subagents | 4-7x | Complex features, audits |
| Agent Teams (5 agents) | ~15x | Large features, parallel research |

---

## Motivation

AI coding assistants are powerful but needy. Every question they ask is a context switch that breaks your flow.

LLMs don't ask because they're incapable — they ask because they're in a **decision vacuum**. When you encode your decisions, teach workflows, give tools, and pre-approve safe actions, the questions vanish. What remains is an autonomous collaborator that takes a single instruction and delivers a finished result.

The knowledge base layer (inspired by Karpathy) adds compounding: every AI exploration feeds back into a searchable knowledge store, making the next exploration richer. Over weeks, this becomes a personal research brain no generic tool can replicate.

---

## Docs

| Document | What's In It |
|----------|-------------|
| [SETUP-GUIDE.md](SETUP-GUIDE.md) | Step-by-step install, configuration, first run, daily workflow |
| [DEEP-DIVE-GUIDE.md](DEEP-DIVE-GUIDE.md) | Technical deep-dive: how each layer works, real code examples |
| [RASCHKA-UPGRADE.md](RASCHKA-UPGRADE.md) | How we applied Raschka's 6 coding agent components |

---

## Related Work

- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)
- [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Agent Teams Docs](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Ultraplan Docs](https://code.claude.com/docs/en/ultraplan)
- [Agent Skills Open Standard](https://github.com/anthropics/skills)
- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 38 agents, 156 skills
- [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) — Community patterns

---

## Contributing

PRs welcome for new skills, subagent specializations, MCP configs, hook scripts, and knowledge base improvements.

---

## License

MIT
