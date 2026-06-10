#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: list[str], *, cwd: Path | None = None) -> dict:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def vault_read(path: str) -> dict:
    cmd = [
        "sh",
        "-lc",
        f". /home/dafengbaocy/obsidian-livecli/env && "
        f"/opt/data/obsidian-vault-cli-venv/bin/vault read --path {json.dumps(path)} --json",
    ]
    return run(cmd)


def write_vault(rel_under_hermes: str, content_file: Path) -> dict:
    return run([
        "/opt/data/scripts/vault-write-hermes-container",
        rel_under_hermes,
        str(content_file),
    ])


def course_entry_markdown(lecture: str, docs: list[dict]) -> str:
    def rows(role: str) -> list[str]:
        out = []
        for doc in docs:
            if doc.get("role") == role:
                path = doc["path"]
                out.append(f"- [[Hermes/Courses/CS224N-2025/{path}|{Path(path).stem}]]")
        return out

    sections = [
        ("主入口", rows("main_entry")),
        ("代码胶囊", rows("code_capsules") + rows("code_capsule_detail")),
        ("论文精读", rows("paper_note")),
        ("DeepResearch", rows("deepresearch_detail")),
        ("Math 扶手", rows("math_note")),
        ("术语表", rows("glossary")),
    ]
    lines = [
        f"# CS224N-2025 {lecture} 入口",
        "",
        "> [!info] 学习入口",
        "> 这页只做入口导航；真正学习从主入口开始。后台日志和评审文件不放在这里。",
        "",
    ]
    for title, items in sections:
        if not items:
            continue
        lines.extend([f"## {title}", "", *items, ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish CS224N manifest documents to Obsidian LiveSync via vault writer.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--lecture", required=True, help="Lecture id, e.g. L01-word-vectors")
    parser.add_argument("--manifest", required=True, help="Publish manifest path")
    parser.add_argument("--evidence", default="", help="Output evidence JSON path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / args.manifest
    evidence_path = root / (args.evidence or f"artifacts/{args.lecture}-vault-read-evidence.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    documents = [
        doc for doc in manifest.get("documents", [])
        if isinstance(doc, dict)
        and doc.get("user_facing") is True
        and str(doc.get("path", "")).endswith(".md")
    ]

    evidence: dict = {
        "lecture": args.lecture,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "manifest": args.manifest,
        "dry_run": args.dry_run,
        "published_documents": [],
        "vault_reads": [],
        "errors": [],
    }

    course_entry_rel = f"Courses/CS224N-2025/CS224N-2025 {args.lecture} 入口.md"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as tmp:
        tmp.write(course_entry_markdown(args.lecture, documents))
        course_entry_tmp = Path(tmp.name)

    publish_plan: list[tuple[str, Path, str]] = [(course_entry_rel, course_entry_tmp, f"Hermes/{course_entry_rel}")]
    for doc in documents:
        rel = str(doc["path"])
        src = root / rel
        if not src.exists():
            evidence["errors"].append({"path": rel, "issue": "source_missing"})
            continue
        vault_rel = f"Courses/CS224N-2025/{rel}"
        publish_plan.append((vault_rel, src, f"Hermes/{vault_rel}"))

    for vault_rel, src, vault_full in publish_plan:
        record = {"vault_rel": vault_rel, "vault_path": vault_full, "source": str(src.relative_to(root)) if src.is_relative_to(root) else str(src)}
        if args.dry_run:
            record["write"] = {"returncode": 0, "stdout": "dry-run", "stderr": ""}
        else:
            record["write"] = write_vault(vault_rel, src)
        evidence["published_documents"].append(record)
        if record["write"]["returncode"] != 0:
            evidence["errors"].append({"path": vault_full, "issue": "vault_write_failed", "write": record["write"]})

    required_reads = [
        f"Hermes/{course_entry_rel}",
        f"Hermes/Courses/CS224N-2025/Lectures/{args.lecture}/00-课堂入口.md",
        f"Hermes/Courses/CS224N-2025/Lectures/{args.lecture}/04-code-capsules.md",
    ]
    for role in ("paper_note", "deepresearch_detail", "math_note"):
        match = next((d for d in documents if d.get("role") == role), None)
        if match:
            required_reads.append(f"Hermes/Courses/CS224N-2025/{match['path']}")
    seen = set()
    required_reads = [p for p in required_reads if not (p in seen or seen.add(p))]

    for path in required_reads:
        read_result = {"path": path}
        if args.dry_run:
            read_result["read"] = {"returncode": 0, "stdout": "dry-run", "stderr": ""}
        else:
            read_result["read"] = vault_read(path)
        evidence["vault_reads"].append(read_result)
        if read_result["read"]["returncode"] != 0:
            evidence["errors"].append({"path": path, "issue": "vault_read_failed", "read": read_result["read"]})

    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(evidence_path)
    return 1 if evidence["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
