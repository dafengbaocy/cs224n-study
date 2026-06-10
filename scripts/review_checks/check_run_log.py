#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl


TRUSTED_EXECUTORS = {"nbclient", "papermill", "nbconvert", "jupyter nbconvert --execute"}
CONFLICT_MARKER_RE = re.compile(r"^(<<<<<<<|>>>>>>>)(?:\s|$)", re.MULTILINE)


def load_record(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    data: dict[str, object] = {}
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.+?)\s*$", line)
        if m:
            data[m.group(1)] = m.group(2)
    data["_raw_text"] = text
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Check code/assignment run-log provenance and required execution fields.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--logs", nargs="*", required=True, help="Run-log JSON or simple key:value files")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = []
    checked = 0
    for raw in args.logs:
        path = root / raw
        if not path.exists():
            errors.append({"path": raw, "issue": "run_log_missing"})
            continue
        checked += 1
        try:
            record = load_record(path)
        except Exception as e:
            errors.append({"path": raw, "issue": "run_log_parse_failed", "error": repr(e)})
            continue
        raw_text = str(record.get("_raw_text", ""))
        if raw_text and CONFLICT_MARKER_RE.search(raw_text):
            errors.append({"path": raw, "issue": "git_conflict_marker_present_in_run_log"})
        executor = str(record.get("executor", "")).strip()
        if executor not in TRUSTED_EXECUTORS:
            errors.append({"path": raw, "issue": "untrusted_or_missing_executor", "executor": executor})
        for key in ["command", "exit_code", "timestamp"]:
            if key not in record or str(record.get(key, "")).strip() == "":
                errors.append({"path": raw, "issue": f"missing_{key}"})
        if str(record.get("exit_code", "")).strip() not in {"0", "0.0"}:
            errors.append({"path": raw, "issue": "nonzero_or_unknown_exit_code", "exit_code": record.get("exit_code")})
        has_stdout = bool(str(record.get("stdout", "")).strip()) or bool(record.get("stdout_path"))
        has_output = bool(record.get("output_files")) or bool(record.get("outputs"))
        if not has_stdout and not has_output:
            errors.append({"path": raw, "issue": "missing_stdout_or_output_files"})
        for out in record.get("output_files", []) if isinstance(record.get("output_files"), list) else []:
            if not (root / str(out)).exists():
                errors.append({"path": raw, "issue": "output_file_missing", "output": out})

    status = "pass" if not errors else "needs_revision"
    records = [verdict(
        "deterministic.run_log",
        "deterministic",
        status,
        [{"path_or_url": str(root), "locator": f"logs={checked}; errors={len(errors)}", "errors": errors[:80]}],
        "Run-log provenance and execution fields passed." if not errors else "Run-log is missing trusted executor provenance, exit status, stdout, or output evidence.",
    )]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
