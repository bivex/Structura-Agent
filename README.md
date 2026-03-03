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
- Supports **150+ file extensions** across 100+ languages (see [Supported languages](#supported-languages))

### Key frontmatter

| Field   | Value                    |
|---------|--------------------------|
| `model` | `haiku` (fast/cheap)     |
| `tools` | `Bash, Read, Glob, Grep` |

### Example prompts

The agent activates automatically when Claude needs structural code understanding.
You can also invoke it explicitly:

**Finding entry points**
```
Find all @KafkaListener handlers in src/
```
```
Show every @GetMapping and @PostMapping controller method in the project
```
```
Find all functions named handle_* or process_* in src/services/
```

**Exploring class hierarchies**
```
Show every class that extends BaseRepository in src/
```
```
Find all abstract methods in the domain layer
```
```
List all dataclasses decorated with @dataclass in models/
```

**Cross-language search**
```
Search for all async def functions in the Python codebase
```
```
Find every TODO or FIXME comment across all Go files in pkg/
```
```
Show the definition of the connect() method in the Kotlin service layer
```

**Iterative exploration** (how the agent thinks)
```
1. First find class OrderService
2. Then list all public methods inside it
3. Then show which methods call the database layer
```

---

## Supported languages

`grep-ast` uses **tree-sitter** grammar packs and recognises the following
languages out of the box:

| Language | Extensions |
|---|---|
| Python | `.py` |
| JavaScript | `.js`, `.mjs`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Go | `.go`, `go.mod`, `go.sum` |
| Rust | `.rs` |
| Java | `.java` |
| Kotlin | `.kt`, `.kts` |
| C / C++ | `.c`, `.h`, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.h++`, `.hxx` |
| C# | `.cs` |
| Ruby | `.rb` |
| PHP | `.php` |
| Swift | `.swift` |
| Scala | `.scala`, `.sc` |
| Elixir | `.ex`, `.exs` |
| Erlang | `.erl`, `.hrl` |
| Haskell | `.hs` |
| Lua | `.lua` |
| Dart | `.dart` |
| Bash / Zsh | `.sh`, `.bash`, `.zsh` |
| PowerShell | `.ps1`, `.psm1` |
| SQL | `.sql` |
| HTML | `.html`, `.htm` |
| CSS / SCSS | `.css`, `.scss` |
| Vue / Svelte | `.vue`, `.svelte` |
| JSON / TOML / YAML | `.json`, `.toml` |
| Markdown | `.md`, `.markdown` |
| Dockerfile | `Dockerfile` |
| Terraform / HCL | `.tf`, `.hcl`, `.tfvars` |
| Protobuf | `.proto` |
| Solidity | `.sol` |
| Zig | `.zig` |
| OCaml | `.ml`, `.mli` |
| Clojure | `.clj`, `.cljs`, `.cljc`, `.edn` |
| Nix | `.nix` |
| R | `.r`, `.R` |
| Julia | `.jl` |
| CUDA | `.cu`, `.cuh` |
| Makefile / CMake | `Makefile`, `CMakeLists.txt` |
| … and more | Ada, Agda, Cairo, Elm, Fortran, Gleam, Groovy, Odin, Pascal, Perl, Racket, Scheme, VHDL, WebGPU (WGSL), and others |

Run `python3 -c "from grep_ast.parsers import PARSERS; [print(ext, lang) for ext, lang in sorted(PARSERS.items())]"` to see the full list on your installation.

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
