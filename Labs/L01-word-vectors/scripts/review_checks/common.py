#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


PASS_STATUSES = {"pass", "pass_with_corrections"}


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def root_arg() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project/vault root")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    return parser


def verdict(
    check_id: str,
    check_type: str,
    verdict_status: str,
    evidence: list[dict] | None,
    reason: str,
    *,
    reviewer: str = "deterministic_script",
    generated_by: str = "",
    model: str = "",
) -> dict:
    return {
        "check_id": check_id,
        "type": check_type,
        "verdict": verdict_status,
        "evidence": evidence or [],
        "reason": reason,
        "reviewer": reviewer,
        "generated_by": generated_by or os.environ.get("CS224N_GENERATED_BY", ""),
        "model": model or os.environ.get("CS224N_GENERATED_MODEL", ""),
        "timestamp": iso_now(),
    }


def write_jsonl(records: Iterable[dict], output: str = "") -> None:
    text = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def exit_for(records: Iterable[dict]) -> int:
    return 0 if all(r.get("verdict") in PASS_STATUSES for r in records) else 1
