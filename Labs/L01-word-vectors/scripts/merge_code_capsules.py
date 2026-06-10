#!/usr/bin/env python3
"""Merge per-capsule partial notes into the canonical code-capsules note."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def parse_capsules(root: Path, lecture: str) -> list[dict]:
    readings_map = root / "Lectures" / lecture / "02-readings-map.md"
    parser = root / "scripts" / "parse_readings_map.py"
    out = subprocess.check_output(
        [sys.executable, str(parser), str(readings_map), "--field", "code_capsules", "--json"],
        text=True,
    )
    return json.loads(out)


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            return m.group(2).strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--lecture", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    lecture = args.lecture
    partial_dir = root / "Lectures" / lecture / "code-capsules"
    out_path = Path(args.out) if args.out else root / "Lectures" / lecture / "04-code-capsules.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    capsules = parse_capsules(root, lecture)
    missing: list[str] = []
    chunks: list[str] = []
    headings: dict[str, str] = {}
    for cap in capsules:
        slug = cap["slug"]
        partial = partial_dir / f"{slug}.md"
        if not partial.exists():
            missing.append(str(partial.relative_to(root)))
            continue
        text = partial.read_text(encoding="utf-8").strip()
        if "numeric_provenance" not in text:
            missing.append(f"{partial.relative_to(root)} (missing numeric_provenance)")
            continue
        heading = first_heading(text)
        if not heading:
            missing.append(f"{partial.relative_to(root)} (missing heading)")
            continue
        headings[slug] = heading
        chunks.append(text)

    if missing:
        print("merge_code_capsules: missing/invalid partials:", file=sys.stderr)
        for item in missing:
            print(f"  - {item}", file=sys.stderr)
        return 2

    lines = [
        f"# {lecture} Code Capsules",
        "",
        "> [!info] 生成方式",
        "> 本文件由 `scripts/merge_code_capsules.py` 从每个 capsule 的 partial 自动合并生成。worker 不直接写本文件，避免并发覆盖。",
        "",
        "## 文件清单",
        "",
    ]
    for cap in capsules:
        slug = cap["slug"]
        concept = cap.get("concept", "")
        waypoint = cap.get("waypoint", "")
        heading = headings[slug]
        lines.append(f"- [[Lectures/{lecture}/code-capsules/{slug}#{heading}|{slug}]] — {waypoint} / {concept}")
    lines.extend(["", "---", ""])
    lines.append("\n\n---\n\n".join(chunks))
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"merged={out_path.relative_to(root)}")
    print(f"capsules={len(capsules)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
