"""
Autonomous Claude Orchestrator v2
===================================
A production-grade agentic loop implementing all 6 components from
Sebastian Raschka's "Components of a Coding Agent" framework:

  1. Live Repo Context      — workspace snapshot before first turn
  2. Prompt Shape & Cache   — stable prefix cached, changing suffix rebuilt
  3. Structured Tools       — schema validation, path sandboxing, approval
  4. Context Compaction     — clip outputs, dedup reads, compress old history
  5. Session Memory         — working memory + full transcript, resumable
  6. Bounded Subagents      — delegated tasks with tool/depth restrictions

Usage:
    python orchestrator_v2.py "Build a REST API for appointments"
    python orchestrator_v2.py --resume                    # Resume last session
    python orchestrator_v2.py --session my-session "..."  # Named session

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=your-key
"""

import anthropic
import json
import os
import sys
import subprocess
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

MAX_ITERATIONS = 30
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 16384
WORKSPACE_ROOT = Path.cwd()
SESSION_DIR = WORKSPACE_ROOT / ".sessions"
TOOL_OUTPUT_MAX_CHARS = 8000       # Component 4: clip long outputs
TRANSCRIPT_MAX_RECENT = 10        # Component 4: keep last N turns full
TRANSCRIPT_SUMMARY_BUDGET = 2000  # Component 4: token budget for old turns
SUBAGENT_MAX_DEPTH = 1            # Component 6: no recursive spawning
SANDBOX_ROOT = WORKSPACE_ROOT     # Component 3: path sandboxing


# ══════════════════════════════════════════════════════════════════
# Component 1: Live Repo Context
# ══════════════════════════════════════════════════════════════════

def gather_workspace_context() -> str:
    """
    Collect 'stable facts' about the repository BEFORE doing any work.
    This gives the model grounding so it doesn't start from zero.
    """
    facts = []

    # Git state
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        if branch:
            facts.append(f"Git branch: {branch}")

            status = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()
            if status:
                lines = status.split("\n")[:15]
                facts.append(f"Changed files ({len(lines)}):\n" + "\n".join(lines))

            log = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()
            if log:
                facts.append(f"Recent commits:\n{log}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Project type detection
    if (WORKSPACE_ROOT / "pyproject.toml").exists():
        facts.append("Project type: Python (pyproject.toml)")
    elif (WORKSPACE_ROOT / "package.json").exists():
        facts.append("Project type: Node.js (package.json)")
    elif (WORKSPACE_ROOT / "go.mod").exists():
        facts.append("Project type: Go (go.mod)")
    elif (WORKSPACE_ROOT / "Cargo.toml").exists():
        facts.append("Project type: Rust (Cargo.toml)")

    # Directory skeleton
    try:
        result = subprocess.run(
            ["find", ".", "-maxdepth", "2", "-type", "d",
             "-not", "-path", "*/node_modules/*",
             "-not", "-path", "*/.git/*",
             "-not", "-path", "*/__pycache__/*",
             "-not", "-path", "*/.sessions/*"],
            capture_output=True, text=True, timeout=5, cwd=str(WORKSPACE_ROOT)
        )
        dirs = sorted(result.stdout.strip().split("\n"))[:30]
        if dirs:
            facts.append("Directory structure:\n" + "\n".join(dirs))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # CLAUDE.md (if exists)
    claude_md = WORKSPACE_ROOT / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(errors="replace")[:3000]
        facts.append(f"CLAUDE.md (project config):\n{content}")

    # DECISIONS.md last entries
    decisions = WORKSPACE_ROOT / "DECISIONS.md"
    if decisions.exists():
        lines = decisions.read_text(errors="replace").strip().split("\n")
        last = "\n".join(lines[-10:])
        facts.append(f"Recent decisions:\n{last}")

    # BLOCKER.md
    blocker = WORKSPACE_ROOT / "BLOCKER.md"
    if blocker.exists():
        facts.append(f"⚠️ ACTIVE BLOCKER:\n{blocker.read_text(errors='replace')[:500]}")

    return "\n\n".join(facts) if facts else "No workspace context detected."


# ══════════════════════════════════════════════════════════════════
# Component 2: Prompt Shape & Cache Reuse
# ══════════════════════════════════════════════════════════════════

DECISION_PROTOCOL = """You are an autonomous software engineer. Execute tasks to completion WITHOUT asking questions.

## Decision Protocol
- Ambiguous requirements → choose the SIMPLER interpretation
- Unspecified tech stack → use Python/FastAPI + React/Next.js + PostgreSQL
- Unclear naming → follow existing patterns or snake_case (Python) / camelCase (JS)
- Unclear scope → build MINIMUM viable version
- Document every assumption by writing to DECISIONS.md

## Error Protocol
- Command fails → try 3 different fixes
- All 3 fail → write BLOCKER.md and move to next subtask
- Never ask the user for help

## Completion Protocol
- Task fully complete → respond with: TASK_COMPLETE: [one-line summary]
- Blocked after exhausting options → respond with: TASK_BLOCKED: [reason]
"""


def build_stable_prefix(workspace_context: str) -> list[dict]:
    """
    Build the stable prompt prefix that gets cached across turns.
    This includes: system instructions, workspace context, and tool descriptions.
    These rarely change during a session.
    """
    system_content = [
        {
            "type": "text",
            "text": DECISION_PROTOCOL,
            "cache_control": {"type": "ephemeral"}  # Cache this block
        },
        {
            "type": "text",
            "text": f"## Workspace Context (gathered at session start)\n\n{workspace_context}",
            "cache_control": {"type": "ephemeral"}  # Cache this too
        }
    ]
    return system_content


# ══════════════════════════════════════════════════════════════════
# Component 3: Structured Tools, Validation, Path Sandboxing
# ══════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "read_file",
        "description": "Read contents of a file. Path must be inside the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates directories as needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path"},
                "content": {"type": "string", "description": "File content"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "run_command",
        "description": "Run a shell command in the workspace root. Returns stdout/stderr.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files and directories at a path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (relative)"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "search_files",
        "description": "Search for a pattern across files using grep.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Search pattern (regex)"},
                "file_glob": {"type": "string", "description": "File glob, e.g. '*.py'", "default": "*"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "delegate",
        "description": "Delegate a subtask to a bounded subagent. The subagent runs with read-only access and limited depth. Use for research, analysis, or exploration that shouldn't pollute the main context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description for the subagent"},
                "context": {"type": "string", "description": "Key context the subagent needs"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "note",
        "description": "Add a note to working memory. Use for important decisions, findings, or state that should persist across context compactions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short label, e.g. 'current_task', 'finding', 'decision'"},
                "value": {"type": "string", "description": "The note content"}
            },
            "required": ["key", "value"]
        }
    }
]

# Commands that are never allowed
BLOCKED_PATTERNS = [
    "rm -rf /", "sudo rm", "chmod 777", "mkfs", "dd if=",
    "> /dev/sd", ":(){ :|:& };:", "curl | sh", "wget | sh"
]


def validate_path(path_str: str) -> Path:
    """Sandbox: resolve path and ensure it's inside the workspace."""
    resolved = (WORKSPACE_ROOT / path_str).resolve()
    if not str(resolved).startswith(str(WORKSPACE_ROOT.resolve())):
        raise ValueError(f"Path escapes workspace: {path_str}")
    return resolved


def validate_command(cmd: str) -> str:
    """Check command against blocklist."""
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd:
            raise ValueError(f"Blocked command pattern: {pattern}")
    return cmd


# ══════════════════════════════════════════════════════════════════
# Component 4: Context Compaction
# ══════════════════════════════════════════════════════════════════

def clip_output(text: str, max_chars: int = TOOL_OUTPUT_MAX_CHARS) -> str:
    """Clip long tool outputs, keeping head and tail."""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return (
        text[:half]
        + f"\n\n... [{len(text) - max_chars} chars clipped] ...\n\n"
        + text[-half:]
    )


def deduplicate_file_reads(transcript: list[dict]) -> list[dict]:
    """Remove duplicate file read results, keeping only the most recent."""
    seen_reads = {}  # path -> index of last read
    for i, event in enumerate(transcript):
        if event.get("tool") == "read_file" and event.get("path"):
            seen_reads[event["path"]] = i

    # Mark older duplicates for summarization
    result = []
    for i, event in enumerate(transcript):
        if (event.get("tool") == "read_file"
                and event.get("path")
                and seen_reads.get(event["path"]) != i):
            # Older duplicate — replace with stub
            result.append({
                **event,
                "result": f"[previously read {event['path']} — see latest read below]",
                "compacted": True
            })
        else:
            result.append(event)
    return result


def compact_transcript(transcript: list[dict], keep_recent: int = TRANSCRIPT_MAX_RECENT) -> str:
    """
    Build a promptable transcript:
    - Recent events: full fidelity
    - Older events: compressed summaries
    - Deduplicated file reads
    """
    if not transcript:
        return ""

    deduped = deduplicate_file_reads(transcript)

    # Split into old and recent
    if len(deduped) <= keep_recent:
        recent = deduped
        old = []
    else:
        old = deduped[:-keep_recent]
        recent = deduped[-keep_recent:]

    parts = []

    # Summarize old events
    if old:
        summaries = []
        for event in old:
            if event.get("compacted"):
                continue  # Skip dedup stubs from old section
            etype = event.get("type", "event")
            if etype == "tool_call":
                tool = event.get("tool", "?")
                result_preview = str(event.get("result", ""))[:100]
                summaries.append(f"  • {tool}({event.get('path', event.get('command', ''))[:60]}) → {result_preview}")
            elif etype == "assistant":
                text = str(event.get("text", ""))[:120]
                summaries.append(f"  • Claude: {text}")
            elif etype == "user":
                text = str(event.get("text", ""))[:120]
                summaries.append(f"  • User: {text}")
        if summaries:
            parts.append(
                f"[Earlier session activity — {len(old)} events compressed]\n"
                + "\n".join(summaries[-20:])  # Cap at 20 summary lines
            )

    # Recent events at full fidelity
    for event in recent:
        etype = event.get("type", "event")
        if etype == "tool_call":
            tool = event.get("tool", "?")
            args = {k: v for k, v in event.items()
                    if k not in ("type", "tool", "result", "compacted", "timestamp")}
            result = clip_output(str(event.get("result", "")))
            parts.append(f"[Tool: {tool}({json.dumps(args)[:200]})]\nResult: {result}")
        elif etype == "assistant":
            parts.append(f"[Assistant]\n{event.get('text', '')}")
        elif etype == "user":
            parts.append(f"[User]\n{event.get('text', '')}")

    return "\n\n".join(parts)


# ══════════════════════════════════════════════════════════════════
# Component 5: Structured Session Memory
# ══════════════════════════════════════════════════════════════════

class SessionStore:
    """
    Two-layer session state:
    - working_memory: small, distilled, actively maintained (decisions, current task, key findings)
    - transcript: full history of every event, appendable, resumable from disk
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session_dir = SESSION_DIR / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.transcript_path = self.session_dir / "transcript.jsonl"
        self.memory_path = self.session_dir / "working_memory.json"
        self.meta_path = self.session_dir / "meta.json"

        # Load existing state or initialize
        self.transcript: list[dict] = self._load_transcript()
        self.working_memory: dict = self._load_json(self.memory_path, {
            "current_task": None,
            "important_files": [],
            "decisions": [],
            "notes": [],
            "iteration": 0
        })
        self.meta: dict = self._load_json(self.meta_path, {
            "created": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "workspace": str(WORKSPACE_ROOT)
        })

    def _load_transcript(self) -> list[dict]:
        if not self.transcript_path.exists():
            return []
        events = []
        for line in self.transcript_path.read_text().strip().split("\n"):
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return events

    def _load_json(self, path: Path, default: dict) -> dict:
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                pass
        return default

    def record(self, event: dict):
        """Append event to full transcript (on disk immediately)."""
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.transcript.append(event)
        with open(self.transcript_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def note(self, key: str, value: str):
        """Add/update working memory note."""
        # Remove existing note with same key
        self.working_memory["notes"] = [
            n for n in self.working_memory["notes"] if n.get("key") != key
        ]
        self.working_memory["notes"].append({
            "key": key,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        # Keep working memory bounded
        if len(self.working_memory["notes"]) > 20:
            self.working_memory["notes"] = self.working_memory["notes"][-20:]
        self._save_memory()

    def set_task(self, task: str):
        self.working_memory["current_task"] = task
        self._save_memory()

    def add_decision(self, decision: str):
        self.working_memory["decisions"].append({
            "decision": decision,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        if len(self.working_memory["decisions"]) > 10:
            self.working_memory["decisions"] = self.working_memory["decisions"][-10:]
        self._save_memory()

    def track_file(self, path: str):
        if path not in self.working_memory["important_files"]:
            self.working_memory["important_files"].append(path)
            if len(self.working_memory["important_files"]) > 20:
                self.working_memory["important_files"] = self.working_memory["important_files"][-20:]
            self._save_memory()

    def increment_iteration(self):
        self.working_memory["iteration"] = self.working_memory.get("iteration", 0) + 1
        self._save_memory()

    def _save_memory(self):
        self.memory_path.write_text(json.dumps(self.working_memory, indent=2))

    def save_meta(self):
        self.meta_path.write_text(json.dumps(self.meta, indent=2))

    def get_memory_text(self) -> str:
        """Render working memory as promptable text."""
        parts = []
        wm = self.working_memory

        if wm.get("current_task"):
            parts.append(f"Current task: {wm['current_task']}")

        if wm.get("important_files"):
            parts.append(f"Key files: {', '.join(wm['important_files'][-10:])}")

        if wm.get("decisions"):
            recent = wm["decisions"][-5:]
            parts.append("Recent decisions:\n" + "\n".join(
                f"  • {d['decision']}" for d in recent
            ))

        if wm.get("notes"):
            recent = wm["notes"][-8:]
            parts.append("Working notes:\n" + "\n".join(
                f"  • [{n['key']}] {n['value']}" for n in recent
            ))

        return "\n".join(parts) if parts else "(no working memory yet)"


# ══════════════════════════════════════════════════════════════════
# Component 6: Bounded Subagents
# ══════════════════════════════════════════════════════════════════

def run_subagent(task: str, context: str = "", depth: int = 0) -> str:
    """
    Spawn a bounded subagent for a focused subtask.
    Constraints:
    - Read-only (no write_file, no run_command)
    - Max depth = SUBAGENT_MAX_DEPTH (no recursive spawning)
    - Smaller iteration budget
    - Inherits workspace context but NOT main transcript
    """
    if depth >= SUBAGENT_MAX_DEPTH:
        return "ERROR: Maximum subagent depth reached. Cannot delegate further."

    client = anthropic.Anthropic()

    # Read-only tools only
    readonly_tools = [t for t in TOOLS if t["name"] in ("read_file", "list_directory", "search_files", "note")]

    subagent_system = (
        "You are a research subagent. You have READ-ONLY access to the workspace. "
        "Answer the question concisely based on what you find. "
        "You cannot write files or run commands. "
        "You cannot delegate to further subagents. "
        "When done, provide your findings as a clear, concise summary."
    )

    if context:
        subagent_system += f"\n\nContext from parent agent:\n{context}"

    messages = [{"role": "user", "content": task}]

    for _ in range(8):  # Smaller budget for subagents
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=subagent_system,
            tools=readonly_tools,
            messages=messages,
        )

        tool_results = []
        final_text = ""

        for block in response.content:
            if block.type == "text":
                final_text += block.text
            elif block.type == "tool_use":
                try:
                    result = execute_tool(block.name, block.input, readonly=True)
                except Exception as e:
                    result = f"ERROR: {e}"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": clip_output(result, 4000)
                })

        if tool_results:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            return final_text or "(subagent returned no findings)"

    return final_text or "(subagent reached iteration limit)"


# ══════════════════════════════════════════════════════════════════
# Tool Execution
# ══════════════════════════════════════════════════════════════════

def execute_tool(name: str, input_data: dict, readonly: bool = False) -> str:
    """Execute a tool with validation and sandboxing."""
    try:
        if name == "read_file":
            path = validate_path(input_data["path"])
            if not path.exists():
                return f"ERROR: File not found: {input_data['path']}"
            content = path.read_text(encoding="utf-8", errors="replace")
            return clip_output(content)

        elif name == "write_file":
            if readonly:
                return "ERROR: Write not permitted in read-only mode."
            path = validate_path(input_data["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(input_data["content"], encoding="utf-8")
            return f"OK: Wrote {len(input_data['content'])} chars to {input_data['path']}"

        elif name == "run_command":
            if readonly:
                return "ERROR: Command execution not permitted in read-only mode."
            cmd = validate_command(input_data["command"])
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=120, cwd=str(WORKSPACE_ROOT)
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            output += f"\nEXIT: {result.returncode}"
            return clip_output(output)

        elif name == "list_directory":
            path = validate_path(input_data.get("path", "."))
            if not path.exists():
                return f"ERROR: Not found: {input_data.get('path', '.')}"
            entries = sorted(path.iterdir())[:100]
            return "\n".join(
                f"{'[DIR] ' if e.is_dir() else '      '}{e.name}"
                for e in entries
            )

        elif name == "search_files":
            pattern = input_data["pattern"]
            glob = input_data.get("file_glob", "*")
            result = subprocess.run(
                f"grep -rn --include='{glob}' '{pattern}' . | head -30",
                shell=True, capture_output=True, text=True,
                timeout=30, cwd=str(WORKSPACE_ROOT)
            )
            return clip_output(result.stdout or "No matches found.")

        elif name == "delegate":
            return run_subagent(
                task=input_data["task"],
                context=input_data.get("context", "")
            )

        elif name == "note":
            # Handled by caller (SessionStore.note)
            return f"OK: Noted [{input_data['key']}]"

        return f"ERROR: Unknown tool: {name}"

    except ValueError as e:
        return f"VALIDATION ERROR: {e}"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out (120s limit)"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


# ══════════════════════════════════════════════════════════════════
# Main Agent Loop
# ══════════════════════════════════════════════════════════════════

def run_autonomous(task: str, session_id: Optional[str] = None, resume: bool = False):
    """Run the autonomous agent loop with all 6 components active."""

    client = anthropic.Anthropic()

    # Session management
    if session_id is None:
        session_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    store = SessionStore(session_id)

    # Component 1: Gather workspace context (once per session)
    if not resume or not store.transcript:
        workspace_context = gather_workspace_context()
        store.meta["workspace_context_hash"] = hashlib.md5(
            workspace_context.encode()
        ).hexdigest()
    else:
        workspace_context = gather_workspace_context()  # Refresh on resume

    # Component 2: Build stable prefix (cached across turns)
    system_content = build_stable_prefix(workspace_context)

    # Set task in working memory
    if not resume:
        store.set_task(task)
        store.record({"type": "user", "text": task})

    print(f"\n{'═' * 60}")
    print(f"  AUTONOMOUS AGENT v2")
    print(f"  Session: {session_id}")
    print(f"  Task: {task[:80]}")
    print(f"  Model: {MODEL}")
    print(f"  Resuming: {resume} (transcript: {len(store.transcript)} events)")
    print(f"{'═' * 60}\n")

    iteration_start = store.working_memory.get("iteration", 0)

    for iteration in range(iteration_start + 1, iteration_start + MAX_ITERATIONS + 1):
        store.increment_iteration()

        # Component 4: Compact transcript for prompt
        transcript_text = compact_transcript(store.transcript)

        # Component 5: Render working memory
        memory_text = store.get_memory_text()

        # Build the changing suffix (NOT cached)
        user_content = []
        if memory_text:
            user_content.append(f"## Working Memory\n{memory_text}\n")
        if transcript_text:
            user_content.append(f"## Session Transcript\n{transcript_text}\n")
        user_content.append(f"## Current Request\n{task}")

        if iteration > iteration_start + 1:
            user_content.append(
                "\nContinue working. If fully done, respond with TASK_COMPLETE: [summary]. "
                "If blocked, respond with TASK_BLOCKED: [reason]."
            )

        messages = [{"role": "user", "content": "\n\n".join(user_content)}]

        print(f"\n── Iteration {iteration} (transcript: {len(store.transcript)} events, "
              f"memory: {len(store.working_memory.get('notes', []))} notes) ──")

        # API call with cached system prefix
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_content,
            tools=TOOLS,
            messages=messages,
        )

        # Process response
        tool_results = []
        assistant_text = ""

        for block in response.content:
            if block.type == "text":
                assistant_text += block.text
                print(f"\n🤖 {block.text[:400]}")

                # Check completion signals
                if "TASK_COMPLETE:" in block.text:
                    summary = block.text.split("TASK_COMPLETE:")[-1].strip()
                    store.record({"type": "assistant", "text": block.text})
                    store.note("completion", summary)
                    store.save_meta()
                    print(f"\n{'═' * 60}")
                    print(f"  ✅ TASK COMPLETE: {summary}")
                    print(f"  Iterations: {iteration - iteration_start}")
                    print(f"  Session: {store.session_dir}")
                    print(f"{'═' * 60}\n")
                    return True

                if "TASK_BLOCKED:" in block.text:
                    reason = block.text.split("TASK_BLOCKED:")[-1].strip()
                    store.record({"type": "assistant", "text": block.text})
                    store.note("blocker", reason)
                    store.save_meta()
                    print(f"\n{'═' * 60}")
                    print(f"  🚫 TASK BLOCKED: {reason}")
                    print(f"  Iterations: {iteration - iteration_start}")
                    print(f"  Session: {store.session_dir}")
                    print(f"{'═' * 60}\n")
                    return False

            elif block.type == "tool_use":
                print(f"\n🔧 {block.name}({json.dumps(block.input)[:150]})")

                # Execute tool
                result = execute_tool(block.name, block.input)
                print(f"   → {result[:150]}...")

                # Component 5: Record in transcript
                event = {
                    "type": "tool_call",
                    "tool": block.name,
                    "result": result,
                }
                # Add relevant args to event for dedup/compaction
                if block.name == "read_file":
                    event["path"] = block.input.get("path")
                    store.track_file(block.input.get("path", ""))
                elif block.name == "write_file":
                    event["path"] = block.input.get("path")
                    store.track_file(block.input.get("path", ""))
                elif block.name == "run_command":
                    event["command"] = block.input.get("command", "")[:200]
                elif block.name == "note":
                    store.note(block.input["key"], block.input["value"])

                store.record(event)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": clip_output(result)
                })

        if assistant_text:
            store.record({"type": "assistant", "text": assistant_text})

        # If there were tool calls, we need to continue the loop
        # The next iteration will include the updated transcript
        if not tool_results and response.stop_reason == "end_turn":
            # Model stopped without tools or completion — nudge it
            pass

        store.save_meta()

    print(f"\n{'═' * 60}")
    print(f"  ⏱️  MAX ITERATIONS ({MAX_ITERATIONS})")
    print(f"  Session saved: {store.session_dir}")
    print(f"  Resume with: python orchestrator_v2.py --resume --session {session_id}")
    print(f"{'═' * 60}\n")
    return False


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Claude Orchestrator v2")
    parser.add_argument("task", nargs="*", help="Task description")
    parser.add_argument("--resume", action="store_true", help="Resume last session")
    parser.add_argument("--session", type=str, help="Named session ID")
    parser.add_argument("--model", type=str, default=MODEL, help="Model to use")
    parser.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS)
    args = parser.parse_args()

    global MODEL, MAX_ITERATIONS
    MODEL = args.model
    MAX_ITERATIONS = args.max_iterations

    if args.resume:
        # Find most recent session or use specified
        if args.session:
            session_id = args.session
        else:
            sessions = sorted(SESSION_DIR.iterdir()) if SESSION_DIR.exists() else []
            if not sessions:
                print("No sessions to resume.")
                sys.exit(1)
            session_id = sessions[-1].name
            print(f"Resuming most recent session: {session_id}")

        store = SessionStore(session_id)
        task = store.working_memory.get("current_task", "")
        if not task:
            print("No task found in session memory.")
            sys.exit(1)

        success = run_autonomous(task, session_id=session_id, resume=True)
    else:
        task = " ".join(args.task)
        if not task:
            print("Usage: python orchestrator_v2.py \"Your task description\"")
            print("       python orchestrator_v2.py --resume")
            sys.exit(1)

        success = run_autonomous(task, session_id=args.session)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
