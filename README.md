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

`grep-ast` uses **tree-sitter** grammar packs. Full list as of v0.9.0 (150+ extensions, 100+ languages):

### Systems & compiled

| Language | Extensions |
|---|---|
| C | `.c`, `.h` |
| C++ | `.cc`, `.cpp`, `.cxx`, `.h++`, `.hpp`, `.hxx` |
| C# | `.cs` |
| Rust | `.rs` |
| Go | `.go` |
| Zig | `.zig` |
| D | `.d` |
| Fortran | `.f`, `.f03`, `.f08`, `.f90`, `.f95` |
| Ada | `.adb`, `.ads` |
| CUDA | `.cu`, `.cuh` |
| ISPC | `.ispc` |
| Objective-C | `.mm` |
| Arduino | `.ino` |

### JVM & Android

| Language | Extensions |
|---|---|
| Java | `.java` |
| Kotlin | `.kt`, `.kts` |
| Scala | `.scala`, `.sc` |
| Groovy | `.groovy` |
| Smali (Android bytecode) | `.smali` |

### Web & scripting

| Language | Extensions |
|---|---|
| JavaScript | `.js`, `.mjs`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| HTML | `.html`, `.htm` |
| CSS | `.css` |
| SCSS | `.scss` |
| Vue | `.vue` |
| Svelte | `.svelte` |
| Astro | `.astro` |
| Twig | `.twig` |
| PHP | `.php` |
| Ruby | `.rb` |
| Python | `.py` |
| Lua | `.lua`, `.luau` |
| Luadoc | `.luadoc` |
| Luap (Lua patterns) | `.luap` |
| Perl | `.pl`, `.pm` |
| Tcl | `.tcl` |
| QML | `.qml` |
| qmldir | `qmldir` |

### Functional

| Language | Extensions |
|---|---|
| Haskell | `.hs` |
| OCaml | `.ml` |
| OCaml interface | `.mli` |
| Erlang | `.erl`, `.hrl` |
| Elixir | `.ex`, `.exs` |
| HEEx (Elixir templates) | `.heex` |
| Elm | `.elm` |
| Clojure | `.clj`, `.cljs`, `.cljc`, `.edn` |
| Racket | `.rkt` |
| Scheme | `.scm`, `.ss` |
| Common Lisp | `.cl`, `.lisp` |
| Emacs Lisp | `.el` |
| Fennel | `.fnl` |
| Agda | `.agda` |
| PureScript | `.purs` |
| Haxe | `.hx` |

### Mobile & cross-platform

| Language | Extensions |
|---|---|
| Swift | `.swift` |
| Dart | `.dart` |
| GDScript (Godot) | `.gd` |

### Infrastructure & config

| Language | Extensions |
|---|---|
| Terraform / HCL | `.tf`, `.hcl`, `.tfvars` |
| Dockerfile | `Dockerfile` |
| Makefile | `Makefile`, `.mk` |
| CMake | `CMakeLists.txt`, `.cmake` |
| Meson | `meson.build` |
| Ninja | `.ninja` |
| Starlark / Bazel | `.bzl`, `BUILD`, `WORKSPACE` |
| Kconfig | `Kconfig` |
| Nix | `.nix` |
| TOML | `.toml` |
| JSON | `.json` |
| JSON5 / Jsonnet | `.jsonnet`, `.libsonnet` |
| YAML (via tree-sitter) | — |
| XML / XSL / SVG | `.xml`, `.xsl`, `.svg` |
| Properties | `.properties` |
| Prisma | `.prisma` |
| Bicep | `.bicep` |
| KDL | `.kdl` |
| RON | `.ron` |

### Data & query

| Language | Extensions |
|---|---|
| SQL | `.sql` |
| SPARQL | `.rq` |
| CSV / TSV / PSV | `.csv`, `.tsv`, `.psv` |
| Beancount | `.bean` |
| BibTeX | `.bib` |
| PGN (chess) | `.pgn` |

### Shells & scripting tools

| Language | Extensions |
|---|---|
| Bash / Zsh / Shell | `.sh`, `.bash`, `.zsh` |
| Fish | `.fish` |
| PowerShell | `.ps1`, `.psm1` |
| Awk | — |

### Docs & markup

| Language | Extensions |
|---|---|
| Markdown | `.md`, `.markdown` |
| reStructuredText | `.rst` |
| LaTeX | `.tex`, `.cls`, `.sty` |
| Org-mode | `.org` |
| Typst | `.typ` |
| Mermaid | `.mermaid` |

### Hardware & shaders

| Language | Extensions |
|---|---|
| Verilog / SystemVerilog | `.v`, `.sv` |
| VHDL | `.vhd`, `.vhdl` |
| GLSL | `.glsl`, `.frag`, `.vert` |
| HLSL | `.hlsl` |
| WGSL (WebGPU) | `.wgsl` |
| Firrtl | `.fir` |
| Tablegen (LLVM) | `.td` |
| LLVM IR | `.ll` |

### Blockchain & smart contracts

| Language | Extensions |
|---|---|
| Solidity | `.sol` |
| Cairo (StarkNet) | `.cairo` |
| Clarity (Stacks) | `.clar` |
| Func (TON) | `.fc` |
| Move | — |

### Other / niche

| Language | Extensions |
|---|---|
| R | `.r`, `.R` |
| Julia | `.jl` |
| MATLAB | `.m`, `.mat` |
| Protobuf | `.proto` |
| Thrift | `.thrift` |
| Cap'n Proto | `.capnp` |
| Smithy | `.smithy` |
| Odin | `.odin` |
| Gleam | `.gleam` |
| Pony | `.pony` |
| Janet | `.janet` |
| Hare | `.ha` |
| Squirrel | `.nut` |
| Magik | `.magik` |
| Pascal | `.pas`, `.pp` |
| ActionScript | `.as` |
| Hack | `.hack` |
| Bitbake (Yocto) | `.bb`, `.bbappend`, `.bbclass` |
| Starlark | `.bzl`, `BUILD`, `WORKSPACE` |
| Assembly | `.asm`, `.s` |
| Git files | `.gitignore`, `.gitattributes`, `.gitcommit` |
| Python manifest | `MANIFEST.in`, `requirements.txt` |
| Go modules | `go.mod`, `go.sum` |
| Vim script | `.vim`, `.vimrc` |
| Readline | `.inputrc` |
| Chatito | `.chatito` |
| Linker script | `.ld` |
| udev rules | `.rules` |
| Hyprland config | `.hypr` |
| GStreamer launch | `.launch` |
| Uxntal | `.tal` |
| Re2c | `.re2c` |
| NQC | `.nqc` |
| XCompose | `.XCompose` |
| DTD | `.dtd` |
| CPON | `.cpon` |
| Gettext PO | `.po`, `.pot` |
| Ungrammar | `.ungram` |
| Yuck (EWW) | `.yuck` |

Run the following to see the live list on your installation:
```bash
python3 -c "from grep_ast.parsers import PARSERS; [print(f'{ext:25} {lang}') for ext, lang in sorted(PARSERS.items())]"
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
