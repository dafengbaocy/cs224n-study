#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
REQUIRED_PHRASES = [
    "这段代码在看什么",
    "运行后先看哪里",
    "输出怎么解释",
    "和本讲哪个 waypoint 对应",
    "容易误解的地方",
]


def cjk_count(text: str) -> int:
    return len(CJK_RE.findall(text))


def check_notebook(path: Path, root: Path) -> list[dict]:
    errors: list[dict] = []
    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [{"path": rel, "issue": "notebook_json_parse_failed", "error": str(exc)}]

    markdown_cells = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "markdown":
            src = cell.get("source", "")
            if isinstance(src, list):
                src = "".join(src)
            markdown_cells.append(str(src))

    joined = "\n".join(markdown_cells)
    if len(markdown_cells) < 3:
        errors.append({"path": rel, "issue": "too_few_markdown_cells", "markdown_cells": len(markdown_cells)})

    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in joined]
    if missing:
        errors.append({"path": rel, "issue": "missing_required_chinese_teaching_sections", "missing": missing})

    nonempty = [cell for cell in markdown_cells if cell.strip()]
    low_chinese_cells = []
    for idx, cell in enumerate(nonempty, 1):
        cjk = cjk_count(cell)
        ascii_letters = len(re.findall(r"[A-Za-z]", cell))
        if cjk < 20 and ascii_letters > cjk * 2:
            low_chinese_cells.append({"markdown_cell_no": idx, "cjk_chars": cjk, "ascii_letters": ascii_letters})
    if low_chinese_cells:
        errors.append({"path": rel, "issue": "learner_markdown_not_chinese_first", "cells": low_chinese_cells[:10]})

    if cjk_count(joined) < 300:
        errors.append({"path": rel, "issue": "notebook_chinese_explanation_too_thin", "cjk_chars": cjk_count(joined)})

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check learner-facing notebook Markdown cells are Chinese-first.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--paths", nargs="+", required=True, help="Notebook paths, directories, or globs")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    notebooks: list[Path] = []
    for raw in args.paths:
        matches = list(root.glob(raw)) if any(ch in raw for ch in "*?[]") else [root / raw]
        for match in matches:
            if match.is_dir():
                notebooks.extend(sorted(match.glob("*.ipynb")))
            elif match.suffix == ".ipynb":
                notebooks.append(match)

    seen = set()
    notebooks = [p for p in notebooks if not (p in seen or seen.add(p))]
    errors: list[dict] = []
    if not notebooks:
        errors.append({"issue": "no_notebooks_found", "paths": args.paths})
    for notebook in notebooks:
        if not notebook.exists():
            errors.append({"path": notebook.as_posix(), "issue": "notebook_missing"})
        else:
            errors.extend(check_notebook(notebook.resolve(), root))

    status = "pass" if not errors else "needs_revision"
    records = [verdict(
        "deterministic.notebook_chinese",
        "deterministic",
        status,
        [{"path_or_url": " ".join(args.paths), "locator": f"notebooks={len(notebooks)}; errors={len(errors)}", "errors": errors[:50]}],
        "Notebook Markdown cells are Chinese-first." if not errors else "Notebook Markdown cells are missing required Chinese teaching scaffolding.",
    )]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
