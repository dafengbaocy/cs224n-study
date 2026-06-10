#!/usr/bin/env python3
"""解析 02-readings-map.md 里的 YAML 字段，供 launch 脚本读取。

readings-map 里有多个 ```yaml 围栏块（code_capsules、deepresearch_waypoints）。
本脚本提取指定字段，输出 TSV（每行一个条目），供 bash while-read 消费。
比 awk 行解析健壮：能处理多行 `reason: >` 块、缩进变化、字段顺序变化。

用法:
  parse_readings_map.py FILE --field deepresearch_waypoints [--needs-deepresearch-only]
  parse_readings_map.py FILE --field code_capsules
  parse_readings_map.py FILE --field core_readings
"""
from __future__ import annotations

import argparse
import json
import re
import sys

import yaml

YAML_FENCE_OPEN_RE = re.compile(r"^```ya?ml\s*$", re.I)
FENCE_CLOSE_RE = re.compile(r"^```\s*$")
FIELD_LINE_RE = re.compile(r"^{field}:\s*$")
FALLBACK_STOP_RE = re.compile(r"^(?:```|---\s*$|##\s+)")


def iter_yaml_fences(text: str):
    """按行提取 ```yaml 围栏块，并保留行号用于诊断。"""
    lines = text.splitlines()
    in_yaml = False
    start_line = 0
    block_lines: list[str] = []

    for idx, line in enumerate(lines, start=1):
        if not in_yaml:
            if YAML_FENCE_OPEN_RE.match(line):
                in_yaml = True
                start_line = idx
                block_lines = []
            continue

        if FENCE_CLOSE_RE.match(line):
            yield {
                "start": start_line,
                "end": idx,
                "text": "\n".join(block_lines),
            }
            in_yaml = False
            start_line = 0
            block_lines = []
        else:
            block_lines.append(line)

    if in_yaml:
        yield {
            "start": start_line,
            "end": None,
            "text": "\n".join(block_lines),
            "unclosed": True,
        }


def yaml_summary(text: str) -> list[str]:
    """返回 YAML fence 诊断摘要，帮助 debug 模式定位坏块。"""
    summary: list[str] = []
    for block in iter_yaml_fences(text):
        where = f"lines {block['start']}-{block.get('end') or 'EOF'}"
        if block.get("unclosed"):
            summary.append(f"{where}: unclosed yaml fence")
            continue
        try:
            data = yaml.safe_load(block["text"])
        except yaml.YAMLError as exc:
            first_line = str(exc).splitlines()[0]
            summary.append(f"{where}: YAML error: {first_line}")
            continue
        if isinstance(data, dict):
            keys = ", ".join(str(k) for k in data.keys()) or "<empty>"
            summary.append(f"{where}: keys=[{keys}]")
        else:
            summary.append(f"{where}: parsed {type(data).__name__}")
    return summary


def clean(val) -> str:
    """把多行 YAML 标量压成单行（去换行、压空格），列表 join 成分号串。"""
    if isinstance(val, list):
        val = "; ".join(str(v) for v in val)
    return re.sub(r"\s+", " ", str(val or "")).strip()


def emit(items, args) -> int:
    """输出 TSV：waypoint/slug \t title \t question \t anchor。"""
    n = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        if args.needs_deepresearch_only and not it.get("needs_deepresearch"):
            continue
        if args.field == "deepresearch_waypoints":
            key = clean(it.get("waypoint"))
            question = clean(it.get("research_question"))
            anchor = clean(it.get("official_anchor"))
        elif args.field == "code_capsules":
            key = clean(it.get("slug"))
            question = clean(it.get("concept"))
            anchor = clean(it.get("official_anchor"))
        else:  # core_readings
            key = clean(it.get("slug") or it.get("id"))
            question = clean(it.get("title") or it.get("reading"))
            anchor = clean(it.get("official_anchor") or it.get("canonical_url") or it.get("url"))
        title = clean(it.get("title") or it.get("concept"))
        if not key:
            continue
        print(f"{key}\t{title}\t{question}\t{anchor}")
        n += 1
    if n == 0:
        print("WARN: 没有符合条件的条目", file=sys.stderr)
    return 0


def filter_items(items, args):
    """应用命令行过滤，例如只保留 needs_deepresearch:true。"""
    if not args.needs_deepresearch_only:
        return items
    return [
        it for it in items
        if isinstance(it, dict) and bool(it.get("needs_deepresearch"))
    ]


def load_mapping(block_text: str):
    data = yaml.safe_load(block_text)
    if isinstance(data, dict):
        return data
    return {}


def extract_field_from_fences(text: str, field: str):
    """优先从完整 ```yaml 围栏块提取字段。"""
    errors: list[str] = []
    for block in iter_yaml_fences(text):
        where = f"lines {block['start']}-{block.get('end') or 'EOF'}"
        if block.get("unclosed"):
            errors.append(f"{where}: unclosed yaml fence")
            continue
        try:
            data = load_mapping(block["text"])
        except yaml.YAMLError as exc:
            first_line = str(exc).splitlines()[0]
            errors.append(f"{where}: YAML error: {first_line}")
            continue
        if field in data:
            return data[field] or [], errors, "fence"
    return [], errors, None


def extract_field_by_anchor(text: str, field: str):
    """兜底：从字段行开始读到下一个 markdown/fence 边界。

    这个 fallback 专门处理 debug 期常见的人为编辑错误：
    code_capsules: 已经存在，但上一个 ```yaml 没有在字段结束处闭合。
    它只抓字段自己的 YAML 片段，不会继续吞后面的 markdown heading。
    """
    field_re = re.compile(FIELD_LINE_RE.pattern.format(field=re.escape(field)))
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if not field_re.match(line):
            continue

        snippet = [line]
        for next_line in lines[idx + 1:]:
            if FALLBACK_STOP_RE.match(next_line):
                break
            snippet.append(next_line)

        try:
            data = load_mapping("\n".join(snippet))
        except yaml.YAMLError as exc:
            return [], [f"field fallback at line {idx + 1}: {str(exc).splitlines()[0]}"], None
        if field in data:
            return data[field] or [], [f"field fallback at line {idx + 1}"], "field-fallback"
    return [], [], None


def extract_field(text: str, field: str):
    """返回字段列表、诊断信息、来源方式。"""
    items, errors, source = extract_field_from_fences(text, field)
    if items:
        return items, errors, source

    fallback_items, fallback_errors, fallback_source = extract_field_by_anchor(text, field)
    errors.extend(fallback_errors)
    if fallback_items:
        return fallback_items, errors, fallback_source

    return [], errors, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--field", required=True,
                    choices=["deepresearch_waypoints", "code_capsules", "core_readings"])
    ap.add_argument("--needs-deepresearch-only", action="store_true",
                    help="只输出 needs_deepresearch 为 true 的条目")
    ap.add_argument("--json", action="store_true",
                    help="输出 JSON 数组，供 launcher 结构化读取")
    args = ap.parse_args()

    text = open(args.path, encoding="utf-8").read()
    items, diagnostics, source = extract_field(text, args.field)
    if not items:
        print(f"ERROR: {args.path} 无 {args.field} 字段", file=sys.stderr)
        summary = yaml_summary(text)
        if summary:
            print("YAML fence diagnostics:", file=sys.stderr)
            for line in summary:
                print(f"  - {line}", file=sys.stderr)
        for line in diagnostics:
            print(f"  - {line}", file=sys.stderr)
        return 1
    if source == "field-fallback":
        print(
            f"WARN: {args.path} 的 {args.field} 使用字段级 fallback 解析；"
            "请修复对应 ```yaml 围栏，避免后续人工误读。",
            file=sys.stderr,
        )
        for line in diagnostics:
            print(f"  - {line}", file=sys.stderr)
    items = filter_items(items, args)
    if args.json:
        print(json.dumps(items, ensure_ascii=False))
        return 0
    return emit(items, args)


if __name__ == "__main__":
    sys.exit(main())
