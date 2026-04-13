# The Zero-Question Architecture: Full Autonomy with Claude's Ecosystem

> **Goal:** Give Claude a single instruction. Get a completed project back. No questions asked.

## The Problem You're Solving

LLMs ask questions because of a **decision vacuum**. Every ambiguity triggers a "should I ask the human?" check. The fix isn't suppressing questions — it's eliminating the reasons Claude would need to ask by:

1. **Encoding decisions** in CLAUDE.md (project memory)
2. **Giving tools** via MCP servers (so Claude can self-resolve)
3. **Delegating work** via subagents and agent teams (parallel autonomy)
4. **Automating workflows** via skills (reusable playbooks)
5. **Enforcing quality** via hooks (deterministic guardrails)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR ONE INSTRUCTION                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  CLAUDE.md  │ ← Decision protocol + defaults
                    │  (Memory)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼───┐ ┌─────▼─────┐
       │   Skills    │ │ MCP  │ │  Hooks    │
       │ (Playbooks) │ │(Tools)│ │(Guardrails)│
       └──────┬──────┘ └──┬───┘ └─────┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
       │  Subagents  │ │ Agent   │ │  Commands   │
       │ (Delegates) │ │ Teams   │ │  (Triggers) │
       └─────────────┘ └─────────┘ └─────────────┘
```

---

## Layer 1: CLAUDE.md — The Decision Protocol

**What it is:** A markdown file at your project root that acts as Claude's persistent memory. Every Claude Code session reads it automatically.

**Why it kills questions:** Claude checks CLAUDE.md *before* asking you anything. If the answer is there, it just acts.

### File: `CLAUDE.md`

```markdown
# Project: MyApp

## Decision Protocol — DO NOT ASK, JUST DO

When you encounter ambiguity, follow these rules. Never ask for clarification — make the decision and document it in DECISIONS.md.

### Tech Stack Defaults
- Backend: Python 3.12 + FastAPI
- Frontend: React 18 + Next.js 14 (App Router)
- Database: PostgreSQL 16 + SQLAlchemy
- Auth: JWT with httponly cookies
- Hosting: DigitalOcean App Platform
- CI/CD: GitHub Actions
- Testing: pytest (backend), Vitest (frontend)

### Architecture Decisions
- Always use repository pattern for data access
- All API endpoints must have OpenAPI docstrings
- Use Pydantic v2 models for all request/response schemas
- Environment variables via python-dotenv, never hardcoded
- All dates in UTC, ISO 8601 format

### When Requirements Are Ambiguous
1. Choose the simpler interpretation
2. Implement the minimum viable version
3. Add a TODO comment: `# TODO: Clarify with stakeholder — assumed X`
4. Log the decision in DECISIONS.md with rationale

### Error Handling Protocol
1. Attempt 3 different fixes before reporting failure
2. Log each attempt and why it failed
3. If all 3 fail, write a BLOCKER.md with reproduction steps

### Code Style
- Black formatter, 88 char line length
- isort for imports
- Type hints on all function signatures
- Docstrings on all public functions (Google style)

### Git Conventions
- Conventional commits: feat|fix|refactor|docs|test|chore
- Branch naming: feature/SHORT-DESCRIPTION
- Always run tests before committing
- Never commit to main directly

### Research Defaults
- Minimum 5 sources before synthesizing conclusions
- Prefer primary sources (docs, papers, official blogs) over aggregators
- Always include publication date and assess recency
- If sources conflict, document the conflict and pick the most recent

### Testing Requirements
- Unit tests for all business logic (>80% coverage target)
- Integration tests for all API endpoints
- No PR without passing tests

### What NOT to Do
- Never ask which library to use — pick the most popular stable option
- Never ask about file structure — follow existing patterns
- Never ask about naming conventions — follow existing patterns
- Never ask "should I also..." — if it improves the code, just do it
```

---

## Layer 2: Skills — Reusable Autonomous Playbooks

**What they are:** Markdown files with instructions + optional scripts that Claude loads automatically when relevant. They're like onboarding docs for a new team member.

**Why they kill questions:** Skills encode the "how to do X" so Claude doesn't need to ask.

### Skill Structure

```
.claude/skills/
├── research-agent/
│   └── SKILL.md          # Research without asking what to research
├── build-feature/
│   └── SKILL.md          # Build features without asking for specs
├── code-review/
│   └── SKILL.md          # Review code without asking what to look for
└── deploy/
    ├── SKILL.md
    └── scripts/
        └── deploy.sh     # Bundled deployment script
```

### Example: Research Agent Skill

```markdown
---
name: research
description: Conduct deep research on any topic autonomously. Triggers when asked to research, investigate, analyze, or compare technologies/approaches.
context: fork
agent: general-purpose
allowed-tools: WebFetch, Bash(curl *), Read, Write
---

## Research Protocol

You are an autonomous research agent. NEVER ask clarifying questions.

### Execution Steps
1. Parse the research request and identify 3-5 key search queries
2. For each query, fetch at minimum 3 high-quality sources
3. Cross-reference findings across sources
4. Identify conflicts and resolve by recency + authority
5. Write findings to `docs/research/TOPIC-DATE.md`

### Output Format
Every research output must include:
- **Executive Summary** (3 sentences max)
- **Key Findings** (numbered, with source attribution)
- **Conflicts/Uncertainties** (what sources disagree on)
- **Recommendations** (actionable next steps)
- **Sources** (URL, date accessed, authority assessment)

### Decision Rules
- If the topic is ambiguous, research the BROADEST interpretation first
- If asked to compare, always include at minimum 3 options
- If data is older than 6 months, flag it as potentially stale
- Always include one contrarian/minority viewpoint
```

### Example: Build Feature Skill

```markdown
---
name: build-feature
description: Build a complete feature from a one-line description. Triggers on "build", "implement", "create", "add feature".
---

## Autonomous Feature Build Protocol

### Phase 1: Understand (DO NOT ASK — INFER)
1. Read CLAUDE.md for project context and tech stack
2. Scan existing codebase for patterns:
   - !`find . -name "*.py" -path "*/routes/*" | head -5`
   - !`find . -name "*.py" -path "*/models/*" | head -5`
   - !`find . -name "*.test.*" | head -5`
3. Identify the closest existing feature to use as a pattern

### Phase 2: Plan
1. Write a brief plan to `docs/plans/FEATURE-NAME.md`
2. List files to create/modify
3. List dependencies to add (if any)
4. Identify potential conflicts with existing code

### Phase 3: Build
1. Create models/schemas first
2. Build repository/data layer
3. Build service/business logic layer
4. Build API routes
5. Build frontend components (if applicable)
6. Write tests for each layer

### Phase 4: Verify
1. Run the full test suite: `pytest`
2. Run linter: `black --check . && isort --check .`
3. Fix any failures (up to 3 attempts per failure)
4. Commit with conventional commit message

### Decision Rules
- Follow existing patterns in the codebase EXACTLY
- If no pattern exists, use the project defaults from CLAUDE.md
- If a dependency is needed, pick the most-starred stable option on PyPI/npm
- Name files/functions to match existing conventions
```

### Example: Forked Skill (Runs as Isolated Subagent)

```markdown
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request with:
1. One-sentence overview of the change
2. Files changed grouped by concern (API, models, tests, config)
3. Risk assessment (LOW/MEDIUM/HIGH) with reasoning
4. Suggested reviewers based on file ownership patterns
```

---

## Layer 3: Subagents — Autonomous Delegates

**What they are:** Isolated Claude instances with their own context window, system prompt, and tool permissions. They work independently and return results.

**Why they kill questions:** Each subagent is a specialist that knows exactly what to do. No ambiguity = no questions.

### Built-in Subagent Types

| Type | Purpose | Model | Tools |
|------|---------|-------|-------|
| **Explore** | Read-only codebase search | Haiku (fast/cheap) | Read, Grep, Glob |
| **Plan** | Architecture/strategy | Sonnet | Read, Grep, Glob |
| **General-purpose** | Complex multi-step tasks | Sonnet | Full access |

### Custom Subagents

Create in `.claude/agents/`:

#### `.claude/agents/security-reviewer.md`

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities and auth flaws
tools: Read, Grep, Glob
model: opus
---

You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling (PII exposure, missing encryption)
- OWASP Top 10 compliance

Output format:
SEVERITY: CRITICAL | HIGH | MEDIUM | LOW
FILE: path/to/file
LINE: number
ISSUE: description
FIX: recommended fix

Never ask clarifying questions. Scan everything. Report everything.
```

#### `.claude/agents/test-writer.md`

```markdown
---
name: test-writer
description: Writes comprehensive tests for new or changed code
tools: Read, Write, Bash(pytest *), Bash(npm test *)
model: sonnet
memory: project
---

You are a test engineer. For any code changes:

1. Read the changed files
2. Identify all code paths, edge cases, and error conditions
3. Write unit tests covering >90% of branches
4. Write integration tests for API endpoints
5. Run tests and fix failures (up to 3 attempts)

Follow existing test patterns in the codebase.
Use pytest for Python, Vitest for TypeScript.
Never ask what to test — test EVERYTHING.
```

#### `.claude/agents/researcher.md`

```markdown
---
name: researcher
description: Deep autonomous research on any topic, technology, or competitor
tools: WebFetch, Read, Write, Bash(curl *)
model: sonnet
---

You are a research analyst. When given a topic:

1. Identify 5 search angles (technical, business, competitive, trend, risk)
2. Fetch 3+ sources per angle from authoritative sites
3. Cross-reference and synthesize
4. Write findings to docs/research/TOPIC-YYYY-MM-DD.md

Never ask what to research or how deep to go.
Default: comprehensive analysis with actionable recommendations.
Always include: executive summary, key findings, risks, next steps.
```

### Triggering Subagents

You can trigger them explicitly or let Claude auto-delegate:

```
# Explicit
"Use the security-reviewer agent to audit src/auth/"

# Claude auto-delegates based on description matching
"Build the patient billing module" 
→ Claude may spawn: Explore (scan codebase) + test-writer (after build)

# Parallel subagents (context stays clean)
"Research competing EHR platforms while building the appointment scheduler"
→ Claude spawns researcher + build-feature in parallel
```

---

## Layer 4: Agent Teams — Parallel Autonomous Workforce

**What they are:** Multiple Claude Code instances working in parallel, coordinating via messaging and a shared task list. One acts as team lead.

**Why they kill questions:** The team lead delegates, teammates execute independently, and they communicate with each other — not with you.

### Enable Agent Teams

In `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Example Prompts

#### Full Feature Build (Zero Questions)

```
Build the user notification feature for the project.

Create an agent team:
- "backend-dev": Build the FastAPI routes, models, and service layer for appointments
- "frontend-dev": Build the React components for the appointment calendar and booking flow  
- "test-engineer": Write comprehensive tests for both backend and frontend
- "docs-writer": Write API documentation and user-facing help docs

Use delegate mode. Coordinate through the task list.
All teammates should read CLAUDE.md first.
Backend-dev goes first, frontend-dev starts once the API contract is defined.
Test-engineer and docs-writer work in parallel after implementation.
```

#### Research + Build Pipeline

```
I need a pricing calculator for an upcoming product demo.

Create an agent team:
- "researcher": Research CMS CCM billing codes (99490, 99491, 99487, 99489), 
  reimbursement rates, and eligibility requirements. Write findings to docs/research/
- "designer": Once research is done, design the calculator UI as a React component
- "builder": Implement the calculator with real billing logic from the research
- "reviewer": Review the final implementation for accuracy against CMS guidelines

researcher goes first. designer and builder work in sequence after.
reviewer validates at the end. No one asks me anything.
```

### Key Team Controls

| Control | How | Purpose |
|---------|-----|---------|
| **Delegate mode** | `Shift+Tab` | Lead only coordinates, never writes code |
| **Split panes** | tmux/iTerm2 | See all teammates simultaneously |
| **Direct messaging** | `Shift+Up/Down` | Talk to specific teammates |
| **Task dependencies** | Built-in | Tasks auto-unblock when prerequisites complete |

---

## Layer 5: MCP Servers — External Tool Access

**What they are:** The Model Context Protocol connects Claude to external services — GitHub, databases, APIs, Slack, etc.

**Why they kill questions:** Claude can look things up instead of asking you. Need the DB schema? Claude queries it. Need the latest PR? Claude fetches it.

### Configure MCP Servers

In `.claude/settings.json` (project-level):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

### MCP + Skills Combination

This is where the real power emerges. MCP provides the tools, Skills provide the knowledge of *how* to use them:

```markdown
---
name: db-migrate
description: Create and run database migrations autonomously
allowed-tools: Bash(alembic *), mcp__postgres__query
---

## Migration Protocol

1. Query current schema: use MCP postgres tool to inspect tables
2. Compare with SQLAlchemy models in src/models/
3. Generate migration: `alembic revision --autogenerate -m "description"`
4. Review generated migration for safety
5. Run migration: `alembic upgrade head`
6. Verify: query schema again to confirm changes applied

Never ask which tables to migrate. Compare models to schema and migrate ALL differences.
```

---

## Layer 6: Hooks — Deterministic Guardrails

**What they are:** Event-driven scripts that fire before/after Claude takes actions. They're *not* prompts — they're guaranteed execution.

**Why they kill questions:** Hooks auto-approve safe actions and auto-reject dangerous ones, removing permission prompts.

### Configure Hooks

In `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(npm run *|pytest *|black *|isort *)",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"decision\": \"allow\"}'",
            "async": false
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\" 2>/dev/null || true"
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/quality-gate.sh"
          }
        ]
      }
    ],
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/assign-next-task.sh"
          }
        ]
      }
    ]
  }
}
```

### Hook Types

| Type | Use Case | Blocking? |
|------|----------|-----------|
| `command` | Run bash script, deterministic rules | Yes (unless async) |
| `http` | Call external API (CI, Slack notification) | Yes (unless async) |
| `prompt` | Send to fast model (Haiku) for judgment | Yes |
| `agent` | Spawn subagent for codebase verification | Yes |

### Key Hook Events

| Event | When | Common Use |
|-------|------|------------|
| `PreToolUse` | Before any tool call | Auto-approve safe commands, block dangerous ones |
| `PostToolUse` | After any tool call | Auto-format, run linter, log changes |
| `SessionStart` | Session begins | Set environment variables, load context |
| `TaskCompleted` | Agent team task done | Quality gates (tests must pass) |
| `TeammateIdle` | Teammate finishes | Auto-assign follow-up work |
| `SubagentStart` | Subagent spawns | Environment prep |

---

## Layer 7: Commands — One-Shot Triggers

**What they are:** Slash commands you type to invoke specific workflows. They're user-triggered (unlike skills which can auto-trigger).

### Create Commands

Commands live in `.claude/commands/` as markdown files:

#### `.claude/commands/ship-feature.md`

```markdown
---
description: End-to-end autonomous feature build from a one-line description
---

Build this feature autonomously with zero questions: $ARGUMENTS

Follow this exact sequence:
1. Read CLAUDE.md for project context
2. Scan codebase for existing patterns
3. Write a plan to docs/plans/
4. Implement (models → services → routes → frontend → tests)
5. Run all tests and fix failures
6. Format code (black, isort, prettier)
7. Commit with conventional commit message
8. Write a summary of what was built to docs/changelog/

If anything is ambiguous, choose the simpler interpretation and document the assumption in DECISIONS.md.
```

#### `.claude/commands/deep-research.md`

```markdown
---
description: Autonomous deep research on any topic
allowed-tools: WebFetch, Bash(curl *), Read, Write
context: fork
agent: general-purpose
---

Research this topic exhaustively: $ARGUMENTS

1. Generate 5+ search queries from different angles
2. Fetch 3+ authoritative sources per query
3. Cross-reference all findings
4. Identify conflicts and resolve by recency/authority
5. Write comprehensive findings to docs/research/

Include: executive summary, detailed findings, risk assessment, actionable recommendations, and all sources with dates.

Do NOT ask any clarifying questions. If the topic is broad, research ALL major aspects.
```

Usage:
```bash
/ship-feature patient appointment scheduling with recurring visits
/deep-research HIPAA compliance requirements for AI-generated clinical notes
```

---

## Putting It All Together: The Complete Project Structure

```
your-project/
├── CLAUDE.md                          # Decision protocol (Layer 1)
├── DECISIONS.md                       # Auto-generated decision log
├── .claude/
│   ├── settings.json                  # MCP servers + hooks config
│   ├── skills/
│   │   ├── research/SKILL.md          # Research playbook
│   │   ├── build-feature/SKILL.md     # Feature build playbook
│   │   ├── code-review/SKILL.md       # Review playbook
│   │   └── deploy/
│   │       ├── SKILL.md
│   │       └── scripts/deploy.sh
│   ├── agents/
│   │   ├── security-reviewer.md       # Security specialist
│   │   ├── test-writer.md             # Test specialist
│   │   └── researcher.md              # Research specialist
│   └── commands/
│       ├── ship-feature.md            # /ship-feature <description>
│       ├── deep-research.md           # /deep-research <topic>
│       └── full-build.md              # /full-build (agent team)
├── docs/
│   ├── plans/                         # Auto-generated build plans
│   ├── research/                      # Auto-generated research
│   └── changelog/                     # Auto-generated changelogs
├── scripts/
│   ├── quality-gate.sh                # Hook: test gate
│   └── assign-next-task.sh            # Hook: idle teammate assignment
└── src/
    └── ...                            # Your actual code
```

---

## The Cheat Sheet: When to Use What

| I want to... | Use this |
|---------------|----------|
| Set project defaults so Claude never asks | **CLAUDE.md** |
| Teach Claude a reusable workflow | **Skill** |
| Give Claude access to external tools/data | **MCP Server** |
| Delegate a focused task to a specialist | **Subagent** |
| Run multiple agents in parallel | **Agent Team** |
| Auto-approve/reject/format actions | **Hook** |
| Create a repeatable user-triggered workflow | **Command** |
| Run a skill in isolation (own context) | **Skill + `context: fork`** |
| Give a subagent persistent memory | **Agent + `memory: project`** |
| Inject live data into a skill prompt | **Skill + `!`command` syntax`** |

---

## Critical Settings for Zero-Question Mode

### `~/.claude/settings.json` (global)

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(pytest *)",
      "Bash(black *)",
      "Bash(isort *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(alembic *)",
      "Read",
      "Write",
      "Edit",
      "MultiEdit",
      "Grep",
      "Glob"
    ]
  },
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000"
  }
}
```

This pre-approves safe operations so Claude never pauses to ask "can I run pytest?"

---

## Anti-Patterns to Avoid

1. **Don't put "never ask questions" in CLAUDE.md** — This is a symptom-level fix. Instead, provide the ANSWERS to every question Claude would ask.

2. **Don't make skills too prescriptive** — Give goals and constraints, not step-by-step scripts. Claude is smart enough to figure out the path if you define the destination.

3. **Don't over-spawn agent teams** — Each teammate is a full Claude instance consuming tokens. 3-5 teammates is the sweet spot. Beyond that, coordination overhead eats your gains.

4. **Don't skip hooks** — Without hooks, Claude will still pause for permissions on every bash command. Pre-approve your safe commands.

5. **Don't forget `context: fork`** — If a skill does heavy exploration, fork it into a subagent. Otherwise it fills your main context window with noise.
