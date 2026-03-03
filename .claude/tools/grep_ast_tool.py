#!/usr/bin/env python3
"""
.claude/tools/grep_ast_tool.py
Wrapper around the `grep-ast` CLI for use in LLM tool-calling pipelines.
Falls back to a pure-Python AST walk when grep-ast is not installed.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class GrepAstTool:
    """Tool-calling wrapper for grep-ast / AST search."""

    def __call__(
        self,
        pattern: str,
        paths: list[str] | None = None,
        languages: list[str] | None = None,
        context_depth: int = 2,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """
        Search for *pattern* across *paths* using AST context.

        Returns a dict conforming to the output_format in
        .claude/agent_tools/grep_ast_tool.yaml.
        """
        paths = paths or ["./"]
        return _run_grep_ast(
            pattern=pattern,
            paths=paths,
            languages=languages or [],
            context_depth=context_depth,
            max_results=max_results,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_grep_ast(
    pattern: str,
    paths: list[str],
    languages: list[str],
    context_depth: int,
    max_results: int,
) -> dict[str, Any]:
    """Try the grep-ast CLI first; fall back to the Python walker."""
    if _grep_ast_available():
        return _cli_search(pattern, paths, languages, context_depth, max_results)
    return _python_ast_search(pattern, paths, max_results)


def _grep_ast_available() -> bool:
    try:
        subprocess.run(
            ["grep-ast", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _cli_search(
    pattern: str,
    paths: list[str],
    languages: list[str],
    context_depth: int,
    max_results: int,
) -> dict[str, Any]:
    cmd = ["grep-ast", pattern, *paths, f"--context={context_depth}", "--output=json"]
    if languages:
        cmd.append(f"--languages={','.join(languages)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        data = json.loads(result.stdout)
        # Trim to max_results
        if "matches" in data:
            data["matches"] = data["matches"][:max_results]
        return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return _error_result(str(exc))


# ---------------------------------------------------------------------------
# Pure-Python fallback (Python files only)
# ---------------------------------------------------------------------------

def _python_ast_search(
    pattern: str,
    paths: list[str],
    max_results: int,
) -> dict[str, Any]:
    """
    Minimal fallback: walk Python files in *paths*, match node names against
    *pattern* (case-insensitive substring), return structured results.
    """
    import re

    regex = re.compile(pattern, re.IGNORECASE)
    matches: list[dict[str, Any]] = []
    files_scanned = 0
    parse_errors: list[str] = []

    py_files = _collect_py_files(paths)
    for filepath in py_files:
        files_scanned += 1
        try:
            source = Path(filepath).read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=filepath)
        except SyntaxError as exc:
            parse_errors.append(f"{filepath}: {exc}")
            continue

        for node in ast.walk(tree):
            name = getattr(node, "name", None)
            if name is None:
                continue
            if not regex.search(name):
                continue

            node_type = _ast_node_type(node)
            snippet = _extract_snippet(source, node)
            matches.append({
                "file": filepath,
                "node_type": node_type,
                "code_snippet": snippet,
                "ast_context": {"parent": _parent_name(tree, node)},
                "line_range": {
                    "start": getattr(node, "lineno", 0),
                    "end": getattr(node, "end_lineno", 0),
                },
            })
            if len(matches) >= max_results:
                break
        if len(matches) >= max_results:
            break

    return {
        "matches": matches,
        "search_metadata": {
            "files_scanned": files_scanned,
            "parse_errors": parse_errors,
        },
    }


def _collect_py_files(paths: list[str]) -> list[str]:
    result: list[str] = []
    for p in paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".py":
            result.append(str(path))
        elif path.is_dir():
            result.extend(str(f) for f in path.rglob("*.py"))
    return result


def _ast_node_type(node: ast.AST) -> str:
    mapping = {
        ast.FunctionDef: "function",
        ast.AsyncFunctionDef: "function",
        ast.ClassDef: "class",
    }
    return mapping.get(type(node), "unknown")


def _extract_snippet(source: str, node: ast.AST, max_lines: int = 6) -> str:
    lines = source.splitlines()
    start = max(0, getattr(node, "lineno", 1) - 1)
    end = min(len(lines), getattr(node, "end_lineno", start + max_lines))
    return "\n".join(lines[start:end])


def _parent_name(tree: ast.AST, target: ast.AST) -> str | None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            if child is target:
                return getattr(node, "name", type(node).__name__)
    return None


def _error_result(msg: str) -> dict[str, Any]:
    return {
        "matches": [],
        "search_metadata": {"files_scanned": 0, "parse_errors": [msg]},
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="AST-aware code search wrapper")
    parser.add_argument("pattern", help="Search pattern (regex)")
    parser.add_argument("paths", nargs="*", default=["./"], help="Files or dirs")
    parser.add_argument("--languages", default="", help="Comma-separated language filter")
    parser.add_argument("--context", type=int, default=2, dest="context_depth")
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--output", default="json", choices=["json", "text"])
    args = parser.parse_args()

    tool = GrepAstTool()
    result = tool(
        pattern=args.pattern,
        paths=args.paths,
        languages=[l for l in args.languages.split(",") if l],
        context_depth=args.context_depth,
        max_results=args.max_results,
    )

    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for m in result["matches"]:
            print(f"{m['file']}:{m['line_range']['start']}  [{m['node_type']}]")
            print(m["code_snippet"])
            print()


if __name__ == "__main__":
    main()
