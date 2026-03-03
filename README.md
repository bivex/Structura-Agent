# claude-code-boilerplate-agent

Helper specifications and wrappers for Claude Code agents, including an
AST-aware search tool and a ready-to-use subagent definition.

## Repository layout

```
.claude/
  agents/
    grep-ast-search.md      # Claude Code subagent definition
  agent_tools/
    grep_ast_tool.yaml      # Tool spec (input/output schema, execution)
  tools/
    grep_ast_tool.py        # Python wrapper with pure-AST fallback
```

## Included agent

### `grep-ast-search` subagent

Defined in `.claude/agents/grep-ast-search.md`.  
Claude Code loads it automatically at session start.  
Invoke it with:

```
Use the grep-ast-search agent to find all @KafkaListener handlers in src/
```

Or let Claude delegate to it automatically when you ask about code structure.

**What it does**

- Calls the `grep-ast` CLI (or `tools/grep_ast_tool.py` as fallback)
- Returns structured JSON: file, node type, code snippet, AST parent context,
  line range, and search metadata
- Understands Python, Go, Kotlin, Ruby, Elixir, PHP

**Key frontmatter**

| Field   | Value              |
|---------|--------------------|
| `model` | `haiku` (fast)     |
| `tools` | `Bash, Read, Glob, Grep` |

## Tool files

### `.claude/agent_tools/grep_ast_tool.yaml`

YAML specification used by the agent: input schema, output format, CLI
execution template, and LLM usage guidelines.

### `.claude/tools/grep_ast_tool.py`

Python wrapper with two modes:

1. **CLI delegate** — calls `grep-ast` binary if installed
2. **Pure-Python fallback** — walks Python ASTs with `ast.walk` when
   `grep-ast` is not available

```bash
# Direct CLI usage
python .claude/tools/grep_ast_tool.py "def handle_" src/ --output=json

# As a module
from .claude.tools.grep_ast_tool import GrepAstTool
result = GrepAstTool()("@KafkaListener", paths=["./"], context_depth=2)
```

## Quick start

```bash
# Optional: install grep-ast for full multi-language support
pip install grep-ast

# Run Claude Code — subagent loads automatically
claude
```
