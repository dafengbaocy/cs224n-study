#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that vault publish evidence exists and contains required paths.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--evidence", required=True, help="vault read output file, JSON or text")
    parser.add_argument("--required-path", action="append", default=[], help="Required vault path/string expected in evidence; may repeat")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    evidence_path = root / args.evidence
    errors = []
    content = ""
    if not evidence_path.exists():
        errors.append({"path": args.evidence, "issue": "vault_read_evidence_missing"})
    else:
        content = evidence_path.read_text(encoding="utf-8", errors="replace")
        if not content.strip():
            errors.append({"path": args.evidence, "issue": "vault_read_evidence_empty"})
        try:
            json.loads(content)
            parsed = True
        except Exception:
            parsed = False
        for required in args.required_path:
            if required not in content:
                errors.append({"path": args.evidence, "issue": "required_path_not_found_in_vault_evidence", "required": required})
        if "error" in content.lower() and not parsed:
            errors.append({"path": args.evidence, "issue": "vault_evidence_contains_error_text"})

    status = "pass" if not errors else "needs_revision"
    records = [verdict(
        "deterministic.vault_publish",
        "deterministic",
        status,
        [{"path_or_url": args.evidence, "locator": f"required={len(args.required_path)}; errors={len(errors)}", "errors": errors[:50]}],
        "Vault publish readback evidence passed." if not errors else "Vault publish readback evidence is missing, empty, or does not include required paths.",
    )]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
