<p align="center">
  <h1 align="center">Zero-Question Kit</h1>
  <p align="center">
    Drop-in autonomy for Claude Code. Give one instruction. Get a finished project back.<br>
    No clarifying questions. No permission prompts. No hand-holding.
  </p>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#the-problem">The Problem</a> •
  <a href="#two-kits">Two Kits</a> •
  <a href="#knowledge-base">Knowledge Base</a> •
  <a href="#tdd-loop">TDD Loop</a> •
  <a href="#cloud-routines">Cloud Routines</a> •
  <a href="#ultraplan-integration">Ultraplan</a> •
  <a href="#architecture">Architecture</a> •
  <a href="SETUP-GUIDE.md">Full Setup Guide</a>
</p>

---

## The Problem

Every AI coding assistant does the same thing: asks you 15 questions before writing a single line of code.

> *"What framework would you like?"*
> *"Should I add tests?"*
> *"Would you prefer REST or GraphQL?"*
> *"Can you confirm you want me to run this?"*

This happens because LLMs are optimized for helpfulness, and the training signal rewards *checking before acting*. The default is to ask. For builders who know what they want, this creates a bottleneck — you spend more time answering questions than the AI spends building.

**The fix isn't "tell it to stop asking."** The fix is to *eliminate every reason it would need to ask*:

1. **Encode your decisions upfront** → CLAUDE.md
2. **Give it tools to self-resolve** → MCP servers
3. **Teach it reusable workflows** → Skills
4. **Delegate to specialists** → Subagents & Agent Teams
5. **Mechanically enforce safety** → Hooks (not prompts)
6. **Build a self-compounding knowledge base** → Wiki (Karpathy pattern)
7. **Close the test loop** → PostToolUse auto-test + iteration cap (NVIDIA pattern)

This repo packages all of that into **94 drop-in files** across two kits.

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
| `/tdd <feature>` | Strict TDD loop with mechanical iteration cap + Opus debugger escalation |
| `/property-tests <problem>` | Generate Hypothesis property tests BEFORE implementation (for high-stakes code) |
| `/deep-research <topic>` | 5+ search angles, 15+ sources, comparison matrix, recommendations |
| `/team-build <feature>` | 5 parallel agents: researcher, backend, frontend, tester, reviewer |
| `/auto-implement <recs>` | Takes research recommendations → creates git worktrees → agent teams per phase |
| `/research-and-build <topic>` | Full loop: research → recommendations → worktrees → agent teams → build |
| `/from-ultraplan` | Bridges Anthropic's [ultraplan](https://code.claude.com/docs/en/ultraplan) to parallel worktree execution |
| `/scaffold` | Bootstraps entire project from your Quick Config |
| `/ingest <URL or file>` | Adds source to self-compounding knowledge base |
| `/ask <question>` | Answers from wiki — answer filed back, wiki grows |
| `/lint-wiki` | Health-checks the knowledge base, finds gaps and connections |

**Included:** 8 skills, 4 subagents, 12 commands, auto-test-on-edit hook, mechanical iteration cap, auto-formatting hooks, quality gates, native desktop notifications, workspace context injection, universal settings with pre-approved permissions for Python/Node/Go/Rust.

---

### `phd-research/` — Academic Research

For PhD candidates, research scientists, and anyone doing literature-heavy, experiment-driven work.

| Command | What Happens |
|---------|-------------|
| `/lit-review <topic>` | 20+ papers, classifies, synthesizes, identifies gaps, generates BibTeX |
| `/research-pipeline <topic>` | Full pipeline: lit review → experiment → implementation → results → paper |
| `/pre-submission-review` | 3 simulated harsh reviewers + methodology audit + completeness check |
| `/tdd <algorithm>` | Strict TDD loop for research implementations (PennyLane, PyTorch, etc.) |
| `/property-tests <spec>` | Property-based tests for correctness-critical algorithms |
| `/auto-implement <recs>` | Research recommendations → git worktrees → agent teams per phase |
| `/research-and-build <topic>` | Research → recommendations → worktrees → build |
| `/from-ultraplan` | Bridges Anthropic's ultraplan to parallel execution |
| `/ingest <paper URL>` | Compiles paper into wiki article with backlinks and concepts |
| `/ask <research question>` | Synthesizes from wiki — answer compounds the knowledge base |
| `/lint-wiki` | Broken links, orphan concepts, stale articles, connection suggestions |

**Included:** 8 skills, 4 subagents (methodology-advisor, peer-reviewer, research-engineer, opus-debugger), 11 commands, publication-quality figure defaults, LaTeX table generation, native desktop notifications.

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

**You rarely touch the wiki manually.** It's the LLM's domain. At ~100 articles, you have a searchable personal knowledge base that no generic RAG pipeline can match for your domain.

---

## TDD Loop

Inspired by [NVIDIA NeMo Agent Toolkit's code generation pattern](https://developer.nvidia.com/blog/improve-ai-code-generation-using-nvidia-nemo-agent-toolkit/). The kit enforces a closed-loop test-execute-reflect discipline — mechanically, via hooks, not via prompts.

**Three enforcement layers:**

### Layer 1: Auto-test-on-edit hook
After every `Write|Edit|MultiEdit`, the relevant test suite runs and the failure tail is injected back into context. Claude physically cannot claim tests pass without evidence.

```json
"PostToolUse": [
  { "matcher": "Write|Edit|MultiEdit",
    "hooks": [{"command": "pytest tests/unit -x --tb=short | tail -40"}] }
]
```

### Layer 2: Mechanical iteration cap (hooks, not prompts)
After 3 failed test runs, a `PreToolUse` hook *blocks the test command itself*. Prompt-level caps ("max 3 iterations") get ignored by turn 4. A hook returning exit 1 cannot be ignored.

```bash
# scripts/tdd-counter.sh blocks further test runs after 3 failures
# scripts/tdd-post-test.sh increments on fail, resets on pass
```

### Layer 3: Context-isolated debugger (`opus-debugger` subagent)
When the loop gets stuck at iteration 2, escalate to an `opus-debugger` subagent running Opus 4.7 at `xhigh` effort. The subagent reads the failure trace with a fresh context — no half-built implementation polluting the analysis. Returns a specific hypothesis + minimum fix.

### Usage
```bash
/tdd user authentication with JWT, password reset, and rate limiting
```

Claude writes the tests first, implements, runs tests (automatically), self-corrects up to 3 times (escalating to Opus debugger if needed), and either commits working code or writes a blocker doc and moves on.

### For correctness-critical code: property-based tests FIRST
```bash
/property-tests medical record PHI handling — SSN must never appear in logs or error messages
```

Generates Hypothesis-library property tests covering invariants (not examples) before any implementation. For HIPAA, finance, auth, or any domain where "almost correct" means "wrong."

---

## Cloud Routines

Ready-to-use [Claude Code Routines](https://code.claude.com/docs/en/routines) that run autonomously on Anthropic's cloud — even when your laptop is closed.

| Routine | Trigger | What It Does |
|---------|---------|-------------|
| `nightly-code-review.md` | Daily 3 AM | Reviews all open PRs: security, quality, style. Leaves inline comments. |
| `dependency-audit.md` | Weekly Monday 2 AM | Audits deps, applies safe minor/patch upgrades, opens PR if tests pass |
| `wiki-maintenance.md` | Weekly Sunday 8 AM | Lints wiki, discovers connections, synthesizes themes, updates indexes |
| `test-coverage.md` | Weekly Wednesday 4 AM | Finds coverage gaps, writes tests for top 5 uncovered files, opens PR |
| `issue-triage.md` | GitHub: issues.opened | Auto-labels, checks duplicates, drafts response on new issues |

Setup: go to [claude.ai/code/routines](https://claude.ai/code/routines), paste the prompt from any template, add your repo, set the trigger. See `routines/README.md` for details.

---

## Ultraplan Integration

[Ultraplan](https://code.claude.com/docs/en/ultraplan) is Anthropic's cloud-based planning feature — it drafts implementation plans in the browser with inline comments and iterative revision. The kit bridges ultraplan's planning to parallel execution:

```bash
# 1. Anthropic plans it (cloud, browser review, inline comments)
/ultraplan migrate the auth service from sessions to JWTs

# 2. You review, comment, iterate in browser
# 3. Click "Approve plan and teleport back to terminal"

# 4. Kit executes it (worktrees, 5 parallel agents, quality gates)
/from-ultraplan
```

Or skip ultraplan and go straight from research to build:

```bash
# Research produces recommendations → auto-creates worktrees → agent teams build each phase
/research-and-build lab order tracking and result management

# Or feed existing recommendations directly
/auto-implement Phase 1: internal tracking model. Phase 2: external API integration.
```

Each phase gets its own git worktree. Each worktree gets its own agent team (architect → backend → frontend → tester → reviewer). Phases run in parallel when independent, sequentially when dependent.

---

## Opus 4.7 + Model Specialization

The kit defaults to **Claude Opus 4.7** (released April 16, 2026) with effort-level-aware subagents. Model choice matches task difficulty — the NVIDIA specialization idea, stripped of vendor-specific orchestration overhead.

| Agent | Model | Effort | Why |
|-------|-------|--------|-----|
| Security reviewer | Opus | `xhigh` | Security needs deep reasoning, no shortcuts |
| Methodology advisor | Opus | `xhigh` | Catching validity threats requires exhaustive checking |
| Peer reviewer | Opus | `xhigh` | Simulating a tough reviewer needs thorough analysis |
| **Opus debugger** | **Opus** | **`xhigh`** | **Stuck-loop rescue with fresh context** |
| Test writer | Sonnet | `high` | Fast + good enough for test generation |
| Researcher | Sonnet | `high` | Balance between depth and cost |
| Research engineer | Sonnet | `high` | Implementation doesn't need max reasoning |

For cloud-hosted autonomous execution without managing infrastructure, see [MANAGED-AGENTS.md](MANAGED-AGENTS.md) — Anthropic's fully managed agent harness via API.

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
  │ (Playbooks) │  │  Base (Wiki)│  │ (TDD loop + │
  │             │  │             │  │ formatters) │
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
           └──────┬──────┘
                  │
            ┌─────▼──────┐
            │  Routines  │  Cloud-hosted, scheduled
            └────────────┘
```

| Layer | What | Why It Kills Questions |
|-------|------|----------------------|
| **CLAUDE.md** | Decision protocol with defaults | Claude checks here BEFORE asking |
| **Skills** | Reusable autonomous playbooks | Encodes "how to do X" |
| **Knowledge Base** | Self-compounding wiki | Claude searches wiki instead of asking you |
| **Subagents** | Specialist delegates with effort levels | Each knows exactly what to do, at the right reasoning depth |
| **Agent Teams** | Parallel workforce in worktrees | Teammates coordinate with each other, not you |
| **Hooks (TDD)** | Auto-test + mechanical iteration cap | Tests run mechanically; blocked after 3 failures |
| **Hooks (safety)** | Pre-approve safe, block dangerous | No permission prompts on safe commands |
| **MCP Servers** | External tools | Claude looks things up instead of asking |
| **Commands** | One-shot triggers | `/command` invokes full autonomous pipeline |
| **Routines** | Cloud-scheduled automation | Runs while laptop is closed |

---

## Intellectual Foundations

The kit is a synthesis of four ideas, each solving a different part of "AI asks too many questions":

- **Sebastian Raschka** — ["Components of a Coding Agent"](https://sebastianraschka.com/) — a lot of apparent model quality is really context quality. The kit's `orchestrator.py` implements Raschka's 6 components (workspace context, prompt caching, structured tools, context compaction, session memory, bounded subagents).
- **Andrej Karpathy** — [LLM knowledge base pattern](https://x.com/karpathy) — the LLM owns a self-compounding wiki; every exploration files back and compounds. The kit's wiki + `/ingest`, `/ask`, `/lint-wiki` commands implement this.
- **NVIDIA NeMo Agent Toolkit** — [code generation pattern](https://developer.nvidia.com/blog/improve-ai-code-generation-using-nvidia-nemo-agent-toolkit/) — closed-loop test-execute-reflect with hard iteration cap. The kit's `/tdd` command + PostToolUse hooks + mechanical iteration counter implement this (without NVIDIA's multi-model orchestration overhead).
- **Anthropic April 2026 releases** — Opus 4.7 with `xhigh` effort, Ultraplan (cloud planning), Routines (cloud scheduled tasks), Managed Agents (hosted agent API). The kit natively integrates all four.

---

## Repository Structure

```
zero-question-kit/
├── README.md                        # This file
├── SETUP-GUIDE.md                   # Step-by-step setup instructions
├── DEEP-DIVE-GUIDE.md               # Technical deep-dive on all 8 layers
├── RASCHKA-UPGRADE.md               # Raschka's 6 components applied
├── MANAGED-AGENTS.md                # Anthropic's managed agent alternative
├── setup.sh                         # One-command installer
├── scripts/
│   └── wiki-bootstrap.sh            # Initialize knowledge base
│
├── generic/                         # ── Any app project ──
│   ├── CLAUDE.md                    # Decision protocol (6-field Quick Config)
│   ├── orchestrator.py              # Standalone API agentic loop (Raschka's 6 components)
│   ├── scripts/                     # quality-gate, assign-next-task, workspace-context,
│   │                                # tdd-counter (iteration cap),
│   │                                # tdd-post-test (counter update),
│   │                                # wiki-bootstrap
│   ├── routines/   (5 routines)     # Cloud-hosted: nightly-code-review,
│   │                                # dependency-audit, wiki-maintenance,
│   │                                # test-coverage, issue-triage
│   └── .claude/
│       ├── settings.json            # Opus 4.7 + permissions + TDD hooks + MCP + notifications
│       ├── skills/    (8 skills)    # build-feature, code-review, research,
│       │                            # data-pipeline, knowledge-base, wiki-lint,
│       │                            # worktree-manager, tdd-code-gen
│       ├── agents/    (4 agents)    # security-reviewer (Opus/xhigh),
│       │                            # opus-debugger (Opus/xhigh),
│       │                            # test-writer (Sonnet/high),
│       │                            # researcher (Sonnet/high)
│       └── commands/ (12 commands)  # ship-feature, tdd, property-tests,
│                                    # deep-research, team-build, scaffold,
│                                    # auto-implement, from-ultraplan,
│                                    # research-and-build, ingest, ask, lint-wiki
│
└── phd-research/                    # ── Academic research ──
    ├── CLAUDE.md                    # Research domain config
    ├── scripts/                     # Hook scripts including TDD counter
    ├── routines/   (5 routines)     # Same cloud automations, research-adapted
    └── .claude/
        ├── settings.json            # Opus 4.7 + permissions + TDD hooks + notifications
        ├── skills/    (8 skills)    # lit-review, experiment, paper-writing,
        │                            # data-analysis, knowledge-base, wiki-lint,
        │                            # worktree-manager, tdd-code-gen
        ├── agents/    (4 agents)    # methodology-advisor (Opus/xhigh),
        │                            # peer-reviewer (Opus/xhigh),
        │                            # opus-debugger (Opus/xhigh),
        │                            # research-engineer (Sonnet/high)
        └── commands/  (11 commands) # lit-review, research-pipeline,
                                     # pre-submission-review, tdd, property-tests,
                                     # auto-implement, from-ultraplan,
                                     # research-and-build, ingest, ask, lint-wiki
```

---

## Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Claude Code** | Latest | Latest |
| **Node.js** | 18+ | 20+ |
| **Claude Plan** | Pro (single agent + subagents) | Max (Agent Teams, Opus 4.7, Routines) |
| **Default Model** | Opus 4.7 (set in settings.json) | Opus 4.7 with `xhigh` effort for critical agents |
| **OS** | macOS, Linux | macOS, Linux |

Install Claude Code: `npm install -g @anthropic-ai/claude-code`

---

## Token Cost Awareness

| Mode | Multiplier | Best For |
|------|-----------|----------|
| Single agent + skills | 1x | Most daily work |
| With subagents | 4-7x | Complex features, audits |
| TDD loop (auto-test on every edit) | 2-3x | Serious implementation work |
| Opus debugger escalation | +1x per invocation | Stuck bugs only |
| Agent Teams (5 agents) | ~15x | Large features, parallel research |
| Cloud Routines | Per-run cost, runs unattended | Scheduled automation |

---

## Docs

| Document | What's In It |
|----------|-------------|
| [SETUP-GUIDE.md](SETUP-GUIDE.md) | Step-by-step install, configuration, first run, daily workflow |
| [DEEP-DIVE-GUIDE.md](DEEP-DIVE-GUIDE.md) | Technical deep-dive: how each layer works, real code examples |
| [RASCHKA-UPGRADE.md](RASCHKA-UPGRADE.md) | How we applied Raschka's 6 coding agent components |
| [MANAGED-AGENTS.md](MANAGED-AGENTS.md) | Anthropic's managed agent API as cloud alternative to orchestrator.py |

---

## Motivation

AI coding assistants are powerful but needy. Every question they ask is a context switch that breaks your flow.

LLMs don't ask because they're incapable — they ask because they're in a **decision vacuum**. When you encode your decisions, teach workflows, give tools, pre-approve safe actions, and mechanically enforce test runs, the questions vanish. What remains is an autonomous collaborator that takes a single instruction and delivers a finished result.

The knowledge base layer (Karpathy) adds compounding: every AI exploration feeds back into a searchable knowledge store. The TDD loop layer (NVIDIA) adds mechanical correctness: tests run automatically, failures get attention automatically, and the iteration cap prevents death-spirals. Together, you get autonomy that doesn't cut corners.

---

## Related Work

- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)
- [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Agent Teams Docs](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Ultraplan Docs](https://code.claude.com/docs/en/ultraplan)
- [Claude Code Routines Docs](https://code.claude.com/docs/en/routines)
- [Claude Managed Agents Docs](https://docs.anthropic.com/en/docs/managed-agents)
- [Agent Skills Open Standard](https://github.com/anthropics/skills)
- [ruvnet/ruflo](https://github.com/ruvnet/ruflo) — Enterprise multi-agent orchestration platform with swarm intelligence and RAG. Use this if you need a production-grade framework; our kit is a lighter config pattern for solo builders and small teams.
- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 38 agents, 156 skills
- [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) — Community patterns

---

## Contributing

PRs welcome for new skills, subagent specializations, MCP configs, hook scripts, routine templates, and knowledge base improvements.

---

## License

MIT
