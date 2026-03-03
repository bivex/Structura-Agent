#!/usr/bin/env python3
"""
.claude/tools/grep_ast_tool.py

Wrapper around the `grep-ast` library (https://github.com/Aider-AI/grep-ast).
Uses tree-sitter to parse source files and returns structured JSON with
AST context for every match.

Install:
    pip install grep-ast
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Node-type mapping from tree-sitter type strings → canonical labels
# ---------------------------------------------------------------------------

_NODE_TYPE_MAP: dict[str, str] = {
    # Python
    "function_definition": "function",
    "async_function_definition": "function",
    "class_definition": "class",
    "decorated_definition": "function",
    # JavaScript / TypeScript
    "function_declaration": "function",
    "function_expression": "function",
    "arrow_function": "function",
    "method_definition": "method",
    "class_declaration": "class",
    # Go
    "method_declaration": "method",
    "type_declaration": "class",
    # Java / Kotlin
    "method_declaration": "method",
    "constructor_declaration": "method",
    "interface_declaration": "class",
    # Annotation-like
    "decorator": "annotation",
    "annotation": "annotation",
    # Call expressions
    "call": "call",
    "call_expression": "call",
    "invocation_expression": "call",
}


def _canonical_type(ts_type: str) -> str:
    return _NODE_TYPE_MAP.get(ts_type, ts_type)


# ---------------------------------------------------------------------------
# Core: find matches using grep_ast.TreeContext
# ---------------------------------------------------------------------------

def _search_file(
    filepath: str,
    pattern: str,
    ignore_case: bool,
    context_depth: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Search *filepath* for *pattern* using TreeContext. Returns (matches, errors)."""
    from grep_ast.grep_ast import TreeContext

    try:
        code = Path(filepath).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [], [f"{filepath}: {exc}"]

    try:
        tc = TreeContext(
            filepath,
            code,
            color=False,
            verbose=False,
            line_number=False,
            parent_context=True,
            child_context=True,
            last_line=False,
            margin=0,
            mark_lois=False,
            header_max=context_depth,
            loi_pad=0,
        )
    except Exception as exc:
        return [], [f"{filepath}: {exc}"]

    loi = tc.grep(pattern, ignore_case)
    if not loi:
        return [], []

    lines = code.splitlines()
    matches: list[dict[str, Any]] = []

    for line_num in sorted(loi):
        # ---- nearest named tree-sitter node at this line ----
        node_type = "unknown"
        start_line = line_num
        end_line = line_num

        nodes_at_line = tc.nodes[line_num] if line_num < len(tc.nodes) else []
        for node in nodes_at_line:
            if node.is_named:
                node_type = _canonical_type(node.type)
                start_line = node.start_point[0]
                end_line = node.end_point[0]
                break

        # ---- AST context: parent scope chain ----
        scope_starts = sorted(tc.scopes[line_num]) if line_num < len(tc.scopes) else []
        parent_names: list[str] = []
        for scope_line in scope_starts:
            if scope_line == line_num:
                continue
            scope_nodes = tc.nodes[scope_line] if scope_line < len(tc.nodes) else []
            for n in scope_nodes:
                if n.is_named and n.type not in ("module", "program", "source_file"):
                    name = _node_name(n, lines)
                    if name:
                        parent_names.append(name)
                    break

        # ---- code snippet (matched line + context lines) ----
        snippet_start = max(0, line_num - 1)
        snippet_end = min(len(lines), line_num + context_depth)
        snippet = "\n".join(lines[snippet_start:snippet_end])

        matches.append({
            "file": filepath,
            "node_type": node_type,
            "matched_line": line_num + 1,
            "code_snippet": snippet,
            "ast_context": {
                "parent_scopes": parent_names,
            },
            "line_range": {
                "start": start_line + 1,
                "end": end_line + 1,
            },
        })

    return matches, []


def _node_name(node: Any, lines: list[str]) -> str:
    """Extract a human-readable name from a tree-sitter node."""
    for child in node.children:
        if child.type in ("identifier", "name", "property_identifier"):
            return child.text.decode("utf-8", errors="replace")
    start = node.start_point[0]
    if start < len(lines):
        return lines[start].strip()[:60]
    return ""


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def _collect_files(paths: list[str], languages: list[str]) -> list[str]:
    """Return all supported source files under *paths*, optionally filtered by language."""
    from grep_ast.parsers import PARSERS

    if languages:
        allowed_exts = {
            ext for ext, lang in PARSERS.items()
            if any(lang.startswith(l) for l in languages)
        }
    else:
        allowed_exts = set(PARSERS.keys())

    result: list[str] = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            if not languages or path.suffix in allowed_exts:
                result.append(str(path))
        elif path.is_dir():
            for f in sorted(path.rglob("*")):
                if f.is_file() and f.suffix in allowed_exts:
                    result.append(str(f))
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class GrepAstTool:
    """LLM tool-calling wrapper using the grep-ast / tree-sitter library."""

    def __call__(
        self,
        pattern: str,
        paths: list[str] | None = None,
        languages: list[str] | None = None,
        context_depth: int = 2,
        ignore_case: bool = False,
        max_results: int = 50,
    ) -> dict[str, Any]:
        paths = paths or ["./"]
        languages = languages or []

        files = _collect_files(paths, languages)
        all_matches: list[dict[str, Any]] = []
        all_errors: list[str] = []

        for filepath in files:
            if len(all_matches) >= max_results:
                break
            matches, errors = _search_file(filepath, pattern, ignore_case, context_depth)
            all_matches.extend(matches)
            all_errors.extend(errors)

        return {
            "matches": all_matches[:max_results],
            "search_metadata": {
                "files_scanned": len(files),
                "parse_errors": all_errors,
            },
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="AST-aware code search using grep-ast / tree-sitter"
    )
    parser.add_argument("pattern", help="Search pattern (regex)")
    parser.add_argument("paths", nargs="*", default=["./"], help="Files or directories")
    parser.add_argument("--languages", default="", help="Comma-separated language filter (e.g. python,go)")
    parser.add_argument("--context", type=int, default=2, dest="context_depth")
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--output", default="json", choices=["json", "text"])
    args = parser.parse_args()

    tool = GrepAstTool()
    result = tool(
        pattern=args.pattern,
        paths=args.paths,
        languages=[l for l in args.languages.split(",") if l],
        context_depth=args.context_depth,
        ignore_case=args.ignore_case,
        max_results=args.max_results,
    )

    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        meta = result["search_metadata"]
        print(f"Files scanned: {meta['files_scanned']}  |  Matches: {len(result['matches'])}")
        for m in result["matches"]:
            parents = " > ".join(m["ast_context"]["parent_scopes"]) or "module"
            print(f"\n  [{m['node_type']:10}] {m['file']}:{m['matched_line']}  (scope: {parents})")
            for line in m["code_snippet"].splitlines()[:3]:
                print(f"               {line}")


if __name__ == "__main__":
    main()
