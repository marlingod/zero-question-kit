# Managed Agents: Anthropic-Hosted Alternative to orchestrator.py

Claude Managed Agents (launched April 8, 2026) is Anthropic's fully managed agent harness. It provides secure sandboxing, built-in tools, and server-sent event streaming — everything our `orchestrator.py` does, but hosted by Anthropic.

**When to use Managed Agents vs. orchestrator.py:**

| | orchestrator.py | Managed Agents |
|---|---|---|
| **Hosting** | Your machine | Anthropic's cloud |
| **Uptime** | Runs while your terminal is open | Runs independently |
| **Sandboxing** | DIY path validation | Anthropic-grade container isolation |
| **Tools** | Custom (read, write, run_command) | Built-in (code execution, file ops) |
| **Skills** | Not supported | Supports Agent Skills (pptx, xlsx, etc.) |
| **Cost control** | Manual token counting | Task budgets built in |
| **Session persistence** | JSONL on disk | Managed by Anthropic |
| **Setup** | `pip install anthropic` | API call with beta header |

**Use orchestrator.py when:** you need full local control, custom tools, or offline capability.
**Use Managed Agents when:** you want zero infrastructure, Anthropic-grade sandboxing, and always-on availability.

## Quick Start

```python
"""
Managed Agents — Anthropic-hosted autonomous agent
Replaces orchestrator.py for cloud-hosted execution.

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=your-key
"""

import anthropic
import json

client = anthropic.Anthropic()


def run_managed_agent(task: str, skill_ids: list[str] = None):
    """
    Run a task on Anthropic's managed agent infrastructure.
    
    Args:
        task: The task description
        skill_ids: Optional list of skills (e.g., ["pptx", "xlsx", "pdf"])
    """
    
    # Build container config
    container = {
        "type": "code_execution",
    }
    
    # Add skills if specified
    if skill_ids:
        container["skills"] = [{"skill_id": sid} for sid in skill_ids]
    
    # System prompt — same decision protocol as orchestrator.py
    system = """You are an autonomous software engineer. Execute tasks to completion 
    WITHOUT asking questions. If requirements are ambiguous, choose the simpler 
    interpretation and document assumptions. If blocked after 3 fix attempts, 
    report what failed and move on."""
    
    # Create the agent session
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16384,
        system=system,
        messages=[{"role": "user", "content": task}],
        tools=[{"type": "code_execution"}],
        extra_headers={
            "anthropic-beta": "code-execution-2025-08-25"
        },
        **({"container": container} if skill_ids else {})
    )
    
    # Process response
    for block in response.content:
        if block.type == "text":
            print(f"🤖 {block.text[:500]}")
        elif block.type == "tool_use":
            print(f"🔧 {block.name}: {json.dumps(block.input)[:200]}")
        elif block.type == "tool_result":
            print(f"📋 Result: {str(block)[:200]}")
    
    return response


# ── Examples ──

# Simple task
run_managed_agent("Build a Python CLI that converts CSV to JSON with data validation")

# With skills (e.g., generate a report)
run_managed_agent(
    "Analyze this sales data and create an Excel report with charts",
    skill_ids=["xlsx"]
)

# With presentation skill
run_managed_agent(
    "Create a 10-slide pitch deck for a SaaS product",
    skill_ids=["pptx"]
)
```

## Task Budgets (Opus 4.7 feature)

Task budgets give you control over how Claude allocates reasoning tokens on long-running tasks. Use them to cap cost on agent team runs:

```python
# With task budget — cap total reasoning at 50K tokens
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16384,
    system="...",
    messages=[{"role": "user", "content": task}],
    # Task budget controls (when available)
    extra_headers={
        "anthropic-beta": "task-budgets-2026-04-16"
    }
)
```

## Effort Levels (Opus 4.7 feature)

Opus 4.7 introduces `xhigh` effort — finer control between `high` and `max`:

| Level | Use Case | Token Cost |
|-------|----------|-----------|
| `low` | Simple lookups, formatting | Minimal |
| `medium` | Standard tasks | Moderate |
| `high` | Complex coding, analysis | High |
| `xhigh` | Hard problems needing deep reasoning | Very high |
| `max` | Hardest problems, exhaustive exploration | Maximum |

**Recommendation for our kit:**
- Subagents (Explore, read-only): `high`
- Test writer, researcher: `high`
- Security reviewer, methodology advisor, peer reviewer: `xhigh`
- Complex architecture decisions: `max` (use sparingly)

## Migration Path

If you're currently using `orchestrator.py` and want to try Managed Agents:

1. **Same decision protocol** — copy the system prompt from orchestrator.py
2. **Same task format** — the task description works identically
3. **No session management needed** — Anthropic handles persistence
4. **No context compaction needed** — Anthropic handles this internally
5. **Skills available** — add `skill_ids` for document generation capabilities

The main tradeoff: you lose custom tools (our `delegate`, `note`, `search_files`) and local file access. For pure cloud tasks, that's fine. For local repo work, stick with orchestrator.py or Claude Code.
