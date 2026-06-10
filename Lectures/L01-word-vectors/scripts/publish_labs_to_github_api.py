#!/usr/bin/env python3
"""Publish lab files to a GitHub repo through the Contents API.

This is a fallback for small notebook/script drops when git push fails due to
pack transport errors. It reuses study-ops credential discovery and never prints
tokens.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
from pathlib import Path


def load_study_ops(path: Path):
    spec = importlib.util.spec_from_file_location("study_ops", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load study-ops module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--dest-prefix", required=True)
    parser.add_argument("--study-ops", default="/workspace/study-ops/study_ops.py")
    parser.add_argument("--suffix", action="append", default=[".ipynb", ".py"])
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    study_ops = load_study_ops(Path(args.study_ops))
    suffixes = set(args.suffix)
    files = sorted(p for p in source_dir.iterdir() if p.is_file() and p.suffix in suffixes)
    results = []

    for path in files:
        dest = f"{args.dest_prefix.strip('/')}/{path.name}"
        sha = None
        try:
            existing = study_ops.github_request(
                "GET",
                f"/repos/{args.repo}/contents/{dest}?ref={args.branch}",
            )
            sha = existing.get("sha")
        except Exception as exc:
            if "GitHub HTTP 404" not in str(exc):
                raise

        body = {
            "message": f"Publish {dest}",
            "content": base64.b64encode(path.read_bytes()).decode("ascii"),
            "branch": args.branch,
        }
        if sha:
            body["sha"] = sha
        result = study_ops.github_request("PUT", f"/repos/{args.repo}/contents/{dest}", body)
        results.append({
            "path": dest,
            "action": "updated" if sha else "created",
            "sha": result.get("content", {}).get("sha"),
        })

    print(json.dumps({
        "repo": args.repo,
        "branch": args.branch,
        "files": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
