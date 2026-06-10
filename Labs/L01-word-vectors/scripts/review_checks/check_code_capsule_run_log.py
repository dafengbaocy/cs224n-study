#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl


SECTION_RE = re.compile(r"^##\s+run_id\s+(.+?)\s*$", re.M)


def parse_sections(text: str) -> list[dict]:
    matches = list(SECTION_RE.finditer(text))
    sections: list[dict] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        fields: dict[str, str] = {"run_id": match.group(1).strip(), "_body": body}
        for line in body.splitlines()[1:]:
            m = re.match(r"^\s*[-*]?\s*([A-Za-z0-9_-]+)\s*[:=]\s*(.+?)\s*$", line)
            if m:
                fields[m.group(1).strip()] = m.group(2).strip()
        sections.append(fields)
    return sections


def load_capsule_slugs(root: Path, lecture: str) -> list[str]:
    parser = root / "scripts" / "parse_readings_map.py"
    readings = root / "Lectures" / lecture / "02-readings-map.md"
    out = subprocess.check_output(
        [sys.executable, str(parser), str(readings), "--field", "code_capsules", "--json"],
        text=True,
    )
    data = json.loads(out)
    return [str(item["slug"]) for item in data if isinstance(item, dict) and item.get("slug")]


def section_matches(section: dict, slug: str, task_id: str = "") -> bool:
    body = str(section.get("_body", ""))
    run_id = str(section.get("run_id", ""))
    capsule = str(section.get("capsule_slug", section.get("slug", "")))
    task = str(section.get("task_id", ""))
    slug_ok = capsule == slug or f"__{slug}" in run_id or re.search(rf"\b{re.escape(slug)}\b", body)
    task_ok = not task_id or task == task_id or task_id in run_id or task_id in body
    return slug_ok and task_ok


def validate_section(section: dict, slug: str, task_id: str = "") -> list[dict]:
    errors: list[dict] = []
    body = str(section.get("_body", ""))
    run_id = str(section.get("run_id", ""))
    if not run_id:
        errors.append({"slug": slug, "issue": "run_id_missing"})
    if str(section.get("capsule_slug", section.get("slug", ""))) != slug:
        errors.append({"slug": slug, "run_id": run_id, "issue": "capsule_slug_missing_or_mismatch"})
    if task_id and str(section.get("task_id", "")) != task_id:
        errors.append({"slug": slug, "run_id": run_id, "issue": "task_id_missing_or_mismatch", "expected": task_id})
    for key in ["timestamp", "command", "exit_code"]:
        if not str(section.get(key, "")).strip():
            errors.append({"slug": slug, "run_id": run_id, "issue": f"{key}_missing"})
    if str(section.get("exit_code", "")).strip() not in {"0", "0.0"}:
        errors.append({"slug": slug, "run_id": run_id, "issue": "exit_code_not_zero", "exit_code": section.get("exit_code", "")})
    has_stdout = bool(str(section.get("stdout", section.get("stdout_path", ""))).strip()) or f"{slug}-stdout" in body
    has_outputs = bool(str(section.get("outputs", section.get("output_files", ""))).strip()) or "Labs/" in body
    if not has_stdout and not has_outputs:
        errors.append({"slug": slug, "run_id": run_id, "issue": "stdout_or_outputs_missing"})
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check shared Code Capsule run-log sections.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--lecture", required=True)
    parser.add_argument("--slug", default="", help="Single capsule slug for scoped review.")
    parser.add_argument("--task-id", default="", help="Kanban task id for scoped review.")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    log = root / "Labs" / args.lecture / "run-log.md"
    errors: list[dict] = []
    checked: list[str] = []
    if not log.exists():
        errors.append({"path": log.relative_to(root).as_posix(), "issue": "run_log_missing"})
        sections: list[dict] = []
    else:
        sections = parse_sections(log.read_text(encoding="utf-8", errors="replace"))
        if not sections:
            errors.append({"path": log.relative_to(root).as_posix(), "issue": "no_run_id_sections"})

    slugs = [args.slug] if args.slug else load_capsule_slugs(root, args.lecture)
    for slug in slugs:
        matches = [section for section in sections if section_matches(section, slug, args.task_id if args.slug else "")]
        checked.append(slug)
        if not matches:
            errors.append({"slug": slug, "task_id": args.task_id, "issue": "matching_run_log_section_missing"})
            continue
        if args.slug and len(matches) != 1:
            errors.append({"slug": slug, "task_id": args.task_id, "issue": "matching_run_log_section_not_unique", "matches": len(matches)})
            continue
        errors.extend(validate_section(matches[-1], slug, args.task_id if args.slug else ""))

    status = "pass" if not errors else "needs_revision"
    records = [verdict(
        "deterministic.code_capsule_run_log",
        "deterministic",
        status,
        [{
            "path_or_url": log.relative_to(root).as_posix() if log.exists() else f"Labs/{args.lecture}/run-log.md",
            "locator": f"slugs={checked}; sections={len(sections)}; errors={len(errors)}",
            "errors": errors[:80],
        }],
        "Shared run-log has scoped tagged section(s) for code capsule execution."
        if not errors else
        "Shared run-log is missing a unique task-tagged capsule section or required execution fields.",
    )]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    raise SystemExit(main())
