# Zero-Question Kit: Step-by-Step Setup

## Prerequisites

Before you start, you need:

```bash
# 1. Claude Code installed
npm install -g @anthropic-ai/claude-code

# 2. Node.js 18+ (for MCP servers)
node --version  # Should be 18+

# 3. A Claude subscription
#    - Pro plan: Single agent + subagents
#    - Max plan: Agent Teams (Opus 4.6 required)

# 4. GitHub token (optional, for MCP GitHub integration)
export GITHUB_TOKEN=your-github-personal-access-token
```

---

## PART 1: Install the Kit

### Step 1: Download the kit files

Copy the `universal-kit/` folder to your machine. You need the whole folder.

### Step 2: Run the installer

```bash
cd universal-kit/

# ─── For any app project (web app, API, SaaS platform, etc.) ───
./setup.sh generic /path/to/your/project

# ─── For PhD research (any research project) ───
./setup.sh phd /path/to/your/research

# ─── Current directory ───
./setup.sh generic .
```

When prompted "Initialize knowledge base wiki?", type `y`.

### Step 3: Verify the install

```bash
cd /path/to/your/project
ls -la .claude/
```

You should see:
```
.claude/
├── settings.json          ✓ Permissions + hooks + MCP
├── skills/                ✓ Autonomous playbooks
├── agents/                ✓ Specialist subagents
└── commands/              ✓ Slash commands
```

---

## PART 2: Configure Your Project

### Step 4: Edit CLAUDE.md

This is the most important step. Open `CLAUDE.md` and fill in the blanks:

#### For Generic Kit:
```bash
# Open in your editor
code CLAUDE.md   # or vim, nano, etc.
```

Fill in the Quick Config section at the top:
```
PROJECT_TYPE: fullstack
BACKEND: python-fastapi
FRONTEND: react-next
DATABASE: postgres
HOSTING: digitalocean
TESTING: pytest
```

Add your project-specific context at the bottom:
```markdown
### Domain Rules
- All monetary values stored in cents
- Patient data requires HIPAA compliance
- Appointment times in 15-minute increments

### External Integrations
- Stripe for payments
- SendGrid for email
- S3 for file storage

### Known Constraints
- Must support mobile browsers
- API response time < 200ms
- HIPAA audit logging required
```

#### For PhD Kit:
```
### Research Domain Defaults
- Primary field: Quantum Computing
- Subfield: Quantum Continual Learning
- Methodology: Theoretical + Empirical
- Target venues: NeurIPS, ICML, QIP
- Citation style: IEEE

### Tech Stack Defaults
- Language: Python 3.11+
- ML framework: PyTorch
- Quantum framework: PennyLane
- Experiment tracking: Weights & Biases
```

### Step 5: Enable Agent Teams (optional, requires Max plan)

```bash
# Check if you have a global settings file
cat ~/.claude/settings.json

# If it doesn't exist, create it:
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
EOF

# If it already exists, add the env key manually
```

### Step 6: Set up MCP servers (optional)

The kit includes a GitHub MCP config. To activate it:

```bash
# Set your GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Add to your shell profile for persistence:
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.zshrc  # or ~/.bashrc
```

To add more MCP servers, edit `.claude/settings.json`:
```json
{
  "mcpServers": {
    "github": { ... },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}"
      }
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

---

## PART 3: First Run

### Step 7: Launch Claude Code in your project

```bash
cd /path/to/your/project
claude
```

Claude Code reads your CLAUDE.md, loads skills, and connects MCP servers automatically.

### Step 8: Verify everything loaded

Type in Claude Code:
```
/help
```

You should see your custom commands listed:
```
/ship-feature     - End-to-end autonomous feature build
/deep-research    - Autonomous deep research
/team-build       - Spawn agent team for parallel build
/scaffold         - Bootstrap new project
/ingest           - Add source to knowledge base
/ask              - Research question (answer compounds wiki)
/lint-wiki        - Health-check the knowledge base
```

For PhD kit, you'll also see:
```
/lit-review        - Autonomous literature review
/research-pipeline - Full lit→experiment→paper pipeline
/pre-submission-review - Simulated peer review
```

---

## PART 4: Use It

### Quick Wins (try these first)

#### Generic Kit:

```bash
# Build a feature — zero questions
/ship-feature user authentication with JWT and email verification

# Research a technology decision
/deep-research best ORM for FastAPI with async support

# Bootstrap a whole project from your Quick Config
/scaffold patient portal with appointment booking
```

#### PhD Kit:

```bash
# Literature review
/lit-review quantum Fisher information matrix for continual learning

# Full research pipeline
/research-pipeline compare transformer vs LSTM architectures on benchmark datasets

# Pre-submission review
/pre-submission-review docs/papers/my-paper/
```

#### Knowledge Base (both kits):

```bash
# Initialize the wiki (if you didn't during setup)
./scripts/wiki-bootstrap.sh

# Ingest a URL
/ingest https://arxiv.org/abs/2312.xxxxx

# Ingest a local file
/ingest wiki/raw/papers/karpathy-knowledge-base-notes.md

# Ingest everything in raw/
/ingest all

# Ask a question (answer becomes a wiki article)
/ask how does elastic weight consolidation relate to Fisher information?

# Health-check the wiki
/lint-wiki
```

### Agent Teams (Max plan only):

```bash
# Full team build — 5 parallel agents
/team-build payment processing module with Stripe integration

# While running, use these controls:
#   Shift+Tab     → Toggle delegate mode (lead only coordinates)
#   Shift+Up/Down → Cycle through teammates
#   Enter         → View teammate's full session
#   Escape        → Interrupt a teammate
```

### Using Subagents Directly:

```bash
# In Claude Code, just describe what you want:
"Use the security-reviewer agent to audit src/auth/"

"Use the test-writer agent to write tests for the new billing module"

"Use the researcher agent to investigate HIPAA requirements for AI-generated notes"

# Claude auto-delegates based on description matching too:
"Review this code for vulnerabilities"
# → Claude automatically invokes security-reviewer

"Write tests for the appointment scheduler"
# → Claude automatically invokes test-writer
```

---

## PART 5: Customize and Extend

### Add a new skill

```bash
mkdir -p .claude/skills/my-skill
cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: When to trigger this skill (write for the model, not for humans)
---

## Instructions for Claude

Your instructions here. Be specific about:
- What to do (goals and constraints, not step-by-step scripts)
- What NOT to do
- Output format
- Decision rules for ambiguity
EOF
```

### Add a new subagent

```bash
cat > .claude/agents/my-agent.md << 'EOF'
---
name: my-agent
description: What this agent specializes in
tools: Read, Write, Grep, Glob        # Restrict tools
model: sonnet                          # sonnet | opus | haiku
memory: project                        # Optional: persistent memory
---

You are a [role]. Your job is to [task].

[Specific instructions, output format, decision rules]

Never ask clarifying questions. [Default behavior for ambiguity].
EOF
```

### Add a new command

```bash
cat > .claude/commands/my-command.md << 'EOF'
---
description: What /my-command does (shown in /help)
---

Do this with ZERO questions: $ARGUMENTS

[Instructions for Claude]
EOF
```

### Add a hook

Edit `.claude/settings.json`, add to the `hooks` section:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(dangerous-command *)",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"decision\": \"deny\", \"reason\": \"Blocked by policy\"}'"
          }
        ]
      }
    ]
  }
}
```

### Add an MCP server

Edit `.claude/settings.json`, add to `mcpServers`:
```json
{
  "mcpServers": {
    "your-service": {
      "command": "npx",
      "args": ["-y", "@your-org/mcp-server-name"],
      "env": {
        "API_KEY": "${YOUR_API_KEY}"
      }
    }
  }
}
```

---

## PART 6: Knowledge Base Workflow (Daily Use)

### Morning Routine
```bash
# 1. Ingest anything you read overnight
/ingest https://interesting-paper-url.com
/ingest wiki/raw/notes/meeting-notes-2026-04-05.md

# 2. Quick health check
/lint-wiki
```

### During Work
```bash
# Ask questions — answers compound the wiki
/ask what are the current best practices for quantum error mitigation in VQE?

# Research for a specific task
/deep-research CCM billing code reimbursement rates 2026
```

### Weekly Review
```bash
# Full lint — discover connections you missed
/lint-wiki

# Check the wiki stats
cat wiki/indexes/_index.md | head -20
```

### The Compounding Effect
```
Week 1:  ~5 articles   → basic lookups
Week 4:  ~25 articles  → connections emerge
Week 8:  ~60 articles  → cross-domain insights
Week 16: ~100 articles → personal research brain
```

---

## Troubleshooting

### "Claude keeps asking me questions"
Your CLAUDE.md is missing decision rules for that type of ambiguity.
Add a rule: "When [ambiguity type], do [default action]."

### "Permission denied on bash commands"
Add the command pattern to `permissions.allow` in `.claude/settings.json`:
```json
"Bash(your-command *)"
```

### "Agent teams not available"
- Requires Max plan (Opus 4.6)
- Enable the flag: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Check: `cat ~/.claude/settings.json`

### "Skills not triggering"
- Check the `description` field — it's a trigger, not a summary
- Write it from Claude's perspective: "When should I fire?"
- Test: `/your-skill-name` to invoke directly

### "Wiki getting messy"
- Run `/lint-wiki` — it auto-fixes structural issues
- Check `wiki/indexes/_lint-report.md` for the full report
- Merge duplicate articles manually (lint will suggest candidates)

### "Context window filling up"
- Add `context: fork` to skills that do heavy exploration
- Use subagents for research tasks
- Run `/compact` to compress conversation history

---

## File Reference (what's where)

| File | Purpose | You Edit? |
|------|---------|-----------|
| `CLAUDE.md` | Decision protocol + project config | **YES — this is your main config** |
| `DECISIONS.md` | Auto-generated decision log | No (Claude writes this) |
| `.claude/settings.json` | Permissions, hooks, MCP | Yes (to add MCP servers, hooks) |
| `.claude/skills/*/SKILL.md` | Autonomous playbooks | Yes (to add/edit skills) |
| `.claude/agents/*.md` | Specialist subagents | Yes (to add/edit agents) |
| `.claude/commands/*.md` | Slash commands | Yes (to add/edit commands) |
| `scripts/*.sh` | Hook scripts | Rarely (quality-gate, idle-assign) |
| `wiki/raw/` | Raw source material | **YES — drop sources here** |
| `wiki/articles/` | Compiled wiki articles | No (Claude manages this) |
| `wiki/concepts/` | Auto-generated concepts | No (Claude manages this) |
| `wiki/indexes/` | Auto-generated navigation | No (Claude manages this) |
| `wiki/outputs/` | Generated content filed back | No (Claude manages this) |
