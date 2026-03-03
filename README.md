# claude-code-boilerplate-agent

Boilerplate repository for Claude Code agents. Includes a ready-to-use
**`grep-ast-search`** subagent that performs tree-sitter-powered, AST-aware
code search and returns structured JSON output.

## Requirements

| Dependency | Version | Purpose |
|---|---|---|
| [Claude Code](https://claude.ai/code) | latest | runs the agent |
| Python | ≥ 3.10 | executes the tool wrapper |
| [grep-ast](https://github.com/Aider-AI/grep-ast) | ≥ 0.9 | tree-sitter search engine |

## Installation

### 1. Install Claude Code

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Verify:

```bash
claude --version
```

> If `command not found`, add `~/.local/bin` to your PATH:
> ```bash
> echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
> ```

### 2. Install grep-ast

```bash
pip install grep-ast
```

On macOS with Homebrew Python (PEP 668 restriction):

```bash
pip install grep-ast --break-system-packages
```

Or inside a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install grep-ast
```

Verify:

```bash
python3 -c "from grep_ast.grep_ast import TreeContext; print('OK')"
```

### 3. Clone this repository

```bash
git clone https://github.com/bivex/Structura-Agent.git
cd Structura-Agent
```

All agent configuration lives inside `.claude/` — Claude Code picks it up
automatically when you run `claude` from this directory.

---

## Repository layout

```
.claude/
  agents/
    grep-ast-search.md      # Claude Code subagent definition
  agent_tools/
    grep_ast_tool.yaml      # Tool spec: input/output schema, usage guidelines
  tools/
    grep_ast_tool.py        # Python wrapper around grep-ast library
```

---

## Included agent: `grep-ast-search`

Defined in [.claude/agents/grep-ast-search.md](.claude/agents/grep-ast-search.md).  
Claude Code loads it automatically at session start (no restart needed after clone).

### What it does

- Uses **tree-sitter** (via `grep-ast`) to parse source files — not plain-text grep
- Returns structured JSON: file path, node type, code snippet, full AST parent
  scope chain, line range, and search metadata
- Supports 40+ languages: Python, Go, JavaScript, TypeScript, Kotlin, Java,
  Rust, Ruby, Elixir, C/C++, and more

### Key frontmatter

| Field   | Value                    |
|---------|--------------------------|
| `model` | `haiku` (fast/cheap)     |
| `tools` | `Bash, Read, Glob, Grep` |

### Example invocations

```
Find all @KafkaListener handlers in src/
```
```
Use grep-ast-search to show every class that extends BaseHandler
```
```
Search for read_text|write_text in the pathlib module
```

---

## Tool files

### `.claude/agent_tools/grep_ast_tool.yaml`

YAML specification consumed by the agent: input schema, output format, CLI
execution template, and LLM usage guidelines for formulating precise queries.

### `.claude/tools/grep_ast_tool.py`

Python wrapper around `grep_ast.grep_ast.TreeContext`. Can be used standalone:

```bash
# JSON output (for LLM consumption)
python3 .claude/tools/grep_ast_tool.py "def handle_" src/ --output json

# Human-readable output
python3 .claude/tools/grep_ast_tool.py "@KafkaListener" src/ --output text

# Case-insensitive, filter by language
python3 .claude/tools/grep_ast_tool.py "repository" src/ -i --languages python,go

# As a Python module
from claude.tools.grep_ast_tool import GrepAstTool

result = GrepAstTool()(
    pattern="@KafkaListener",
    paths=["./src"],
    languages=["kotlin"],
    context_depth=3,
)
print(result["search_metadata"])   # {"files_scanned": 42, "parse_errors": []}
```

#### Output schema

```json
{
  "matches": [
    {
      "file": "src/handlers/order.py",
      "node_type": "function",
      "matched_line": 42,
      "code_snippet": "def handle_order(self, event): ...",
      "ast_context": {
        "parent_scopes": ["OrderService", "class OrderService(BaseHandler):"]
      },
      "line_range": { "start": 42, "end": 58 }
    }
  ],
  "search_metadata": {
    "files_scanned": 134,
    "parse_errors": []
  }
}
```

---

## License

MIT — see [LICENSE.md](LICENSE.md).
