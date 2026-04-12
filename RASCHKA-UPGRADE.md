# Raschka Upgrade: What Changed and Why

Based on Sebastian Raschka's ["Components of a Coding Agent"](https://magazine.sebastianraschka.com/p/components-of-a-coding-agent) (April 2026), we identified 4 missing components and implemented them.

## Summary of Changes

### New Files

| File | Raschka Component | What It Does |
|------|-------------------|-------------|
| `orchestrator_v2.py` | All 6 components | Complete rewrite with caching, compaction, memory, subagents |
| `scripts/workspace-context.sh` | #1 Live Repo Context | SessionStart hook that injects git state, project type, dir skeleton |
| `settings-patch.json` | — | How to wire the SessionStart hook into existing settings |

### What orchestrator_v2.py Adds Over v1

| Feature | v1 (old) | v2 (new) |
|---------|----------|----------|
| **Workspace context** | None — starts cold | Gathers git branch, commits, dir tree, CLAUDE.md, blockers before first turn |
| **Prompt caching** | Rebuilds everything each turn | Stable prefix (instructions + workspace) marked with `cache_control` — cached across turns |
| **Tool validation** | Basic blocklist | Path sandboxing (can't escape workspace), schema validation, read-only mode for subagents |
| **Context compaction** | None — grows until token limit | Clips outputs >8K chars, deduplicates repeated file reads, compresses old transcript keeping recent turns rich |
| **Session memory** | Stateless — loses everything on exit | Two-layer: working memory (distilled, key notes/decisions/files) + full JSONL transcript on disk |
| **Session resumption** | Not possible | `--resume` flag picks up where you left off, full transcript + working memory restored |
| **Subagents** | Not supported | `delegate` tool spawns read-only bounded subagent with separate iteration budget, no recursive spawning |
| **Working notes** | Not supported | `note` tool lets the model persist key findings across context compactions |
| **Search tool** | Not supported | `search_files` for grep across the codebase |

### Key Insight Applied

Raschka's core argument: **"A lot of apparent model quality is really context quality."**

The old orchestrator treated every turn as independent — no memory of what files were already read, no compression of old history, no workspace awareness. The model was effectively starting with less context each turn as the conversation grew, because useful information was buried in noise.

The v2 orchestrator actively manages context quality:
- **Deduplication**: if the model reads `src/auth.py` 3 times, only the latest read is kept at full fidelity — older reads become one-line stubs
- **Compaction**: after 10 turns, older events get compressed to single-line summaries while recent events stay full
- **Working memory**: the model can `note` important findings that survive compaction — these persist even when old transcript entries are summarized
- **Prompt caching**: the stable prefix (system instructions + workspace context + tool schemas) is cached on Anthropic's side, so only the changing suffix (memory + transcript + request) costs new compute each turn

## Usage

### Standalone (API)

```bash
# New session
python orchestrator_v2.py "Build patient appointment scheduling for MyApp"

# Named session
python orchestrator_v2.py --session myapp-appointments "Build patient appointment scheduling"

# Resume after interruption
python orchestrator_v2.py --resume

# Resume specific session
python orchestrator_v2.py --resume --session myapp-appointments

# Custom model and iteration limit
python orchestrator_v2.py --model claude-opus-4-6 --max-iterations 50 "Complex task..."
```

### Session files on disk

```
.sessions/
└── 20260408-143022/          # or your named session
    ├── transcript.jsonl       # Full history — every event, appendable
    ├── working_memory.json    # Distilled state — current task, notes, decisions, key files
    └── meta.json              # Session metadata — model, workspace, timestamps
```

### Claude Code (SessionStart hook)

```bash
# 1. Copy the workspace-context.sh script
cp scripts/workspace-context.sh /path/to/your/project/scripts/

# 2. Add to your .claude/settings.json hooks section:
"SessionStart": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "./scripts/workspace-context.sh"
      }
    ]
  }
]
```

This ensures every Claude Code session starts with full workspace awareness — git state, project type, directory structure, active blockers, wiki stats — injected as environment variables before the first prompt.
