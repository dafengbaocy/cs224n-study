#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
HEADING_RE = re.compile(r"(?m)^(#{2,4})\s+(.+)$")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")
LINK_RE = re.compile(r"\[\[[^\]]+\]\]|\[[^\]]+\]\([^)]+\)")


def cjk_count(text: str) -> int:
    return len(CJK_RE.findall(text))


def waypoint_sections(text: str) -> list[tuple[str, str]]:
    headings = list(HEADING_RE.finditer(text))
    sections: list[tuple[str, str]] = []
    for idx, match in enumerate(headings):
        title = match.group(2).strip()
        if not re.search(r"\bWP\d+\b|Waypoint|路标|学习点", title, re.I):
            continue
        start = match.end()
        end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
        sections.append((title, text[start:end]))
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Check 00-课堂入口.md is a rich Chinese handout, not a thin link index.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--entry", required=True, help="Lecture main entry path")
    parser.add_argument("--min-cjk-per-waypoint", type=int, default=350)
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    entry = root / args.entry
    errors: list[dict] = []

    if not entry.exists():
        errors.append({"path": args.entry, "issue": "main_entry_missing"})
        text = ""
    else:
        text = entry.read_text(encoding="utf-8", errors="replace")

    sections = waypoint_sections(text)
    if not sections:
        errors.append({"path": args.entry, "issue": "no_waypoint_sections_found"})

    for title, body in sections:
        cjk = cjk_count(body)
        links = len(LINK_RE.findall(body))
        images = list(IMAGE_RE.finditer(body))
        if cjk < args.min_cjk_per_waypoint:
            errors.append({"waypoint": title, "issue": "waypoint_chinese_explanation_too_thin", "cjk_chars": cjk, "min": args.min_cjk_per_waypoint})
        if links and cjk < links * 45:
            errors.append({"waypoint": title, "issue": "link_density_too_high_for_explanation", "links": links, "cjk_chars": cjk})
        if images:
            for image in images:
                following = body[image.end(): image.end() + 700]
                if not re.search(r"先看|看哪里|英文|意思|结论|说明|支持", following):
                    errors.append({"waypoint": title, "issue": "image_missing_chinese_reading_card", "image": image.group(1)[:120]})
        if "现在你应该能说出" not in body and "暂停复述" not in body:
            errors.append({"waypoint": title, "issue": "missing_return_to_mainline_recap"})

    status = "pass" if not errors else "needs_revision"
    records = [verdict(
        "deterministic.lecture_entry_richness",
        "deterministic",
        status,
        [{"path_or_url": args.entry, "locator": f"waypoints={len(sections)}; errors={len(errors)}", "errors": errors[:80]}],
        "Lecture main entry has enough Chinese teaching prose per waypoint." if not errors else "Lecture main entry is too thin or lacks image/link reading scaffolding.",
    )]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
