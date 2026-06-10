#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl


MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
OBSIDIAN_IMAGE_RE = re.compile(r"!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
CONFLICT_MARKER_RE = re.compile(r"^(<<<<<<<|>>>>>>>)(?:\s|$)", re.MULTILINE)
RELATED_CONFLICT_SUFFIXES = {
    ".md",
    ".py",
    ".ipynb",
    ".json",
    ".txt",
    ".csv",
    ".yaml",
    ".yml",
}
RELATED_CONFLICT_SKIP_DIRS = {
    ".git",
    "__pycache__",
    "outputs",
    "media-registry",
}
NON_USER_FACING_MD_NAMES = {
    "run-log.md",
}


def is_remote(target: str) -> bool:
    return target.startswith(("https://", "http://", "data:"))


def has_conflict_marker(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False
    return bool(CONFLICT_MARKER_RE.search(text))


def scan_related_conflict_markers(root: Path, lecture: str) -> list[dict]:
    """Catch stale merge conflict markers in publish-family docs and code/log files.

    We intentionally ignore generated output/media folders here: those are covered
    by run-log/provenance checks and often contain arbitrary model/stdout text.
    The publish gate cares about files a learner or later stage may open directly.
    """
    errors: list[dict] = []
    if not lecture:
        return errors
    roots = [
        root / "Lectures" / lecture,
        root / "Labs" / lecture,
        root / "Papers" / lecture,
        root / "DeepResearch" / lecture,
        root / "Math" / lecture,
    ]
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in RELATED_CONFLICT_SUFFIXES:
                continue
            rel_parts = path.relative_to(base).parts
            if any(part in RELATED_CONFLICT_SKIP_DIRS for part in rel_parts):
                continue
            if has_conflict_marker(path):
                errors.append({
                    "path": path.relative_to(root).as_posix(),
                    "issue": "git_conflict_marker_present_in_publish_related_file",
                })
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate final Obsidian publish manifest and image policy.")
    parser.add_argument("--root", default=".", help="Project/vault root")
    parser.add_argument("--manifest", required=True, help="Publish manifest JSON path")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = (root / args.manifest).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest).resolve()
    records = []
    errors: list[dict] = []

    if not manifest_path.exists():
        records.append(verdict(
            "deterministic.publish_manifest",
            "deterministic",
            "needs_revision",
            [{"path_or_url": str(manifest_path), "errors": [{"issue": "manifest_missing"}]}],
            "Final publish manifest is missing.",
        ))
        write_jsonl(records, args.output)
        return exit_for(records)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        records.append(verdict(
            "deterministic.publish_manifest",
            "deterministic",
            "needs_revision",
            [{"path_or_url": str(manifest_path), "errors": [{"issue": "manifest_json_invalid", "detail": str(exc)}]}],
            "Final publish manifest is not valid JSON.",
        ))
        write_jsonl(records, args.output)
        return exit_for(records)

    documents = manifest.get("documents")
    if not isinstance(documents, list) or not documents:
        errors.append({"issue": "documents_missing_or_empty"})
        documents = []

    lecture = str(manifest.get("lecture", "")).strip()
    if not lecture:
        errors.append({"issue": "lecture_missing"})

    manifest_paths = {
        str(d.get("path", "")).strip()
        for d in documents
        if isinstance(d, dict) and str(d.get("path", "")).strip()
    }

    expected_paths: set[str] = set()
    if lecture:
        fixed_candidates = [
            f"Lectures/{lecture}/00-课堂入口.md",
            f"Lectures/{lecture}/00-concept-glossary.md",
            f"Lectures/{lecture}/01-官方课件带读.md",
            f"Lectures/{lecture}/03-本讲概念卡.md",
            f"Lectures/{lecture}/04-code-capsules.md",
            f"Lectures/{lecture}/05-复习检查.md",
            # Legacy compatibility only. The current canonical code-capsule
            # entry is 04-code-capsules.md.
            f"Lectures/{lecture}/06-code-capsules.md",
            f"Lectures/{lecture}/99-glossary.md",
        ]
        expected_paths.add(f"Lectures/{lecture}/00-课堂入口.md")
        for rel in fixed_candidates[1:]:
            if (root / rel).exists():
                expected_paths.add(rel)
        for pattern in [
            f"DeepResearch/{lecture}/*.md",
            f"Papers/{lecture}/*.md",
            f"Math/{lecture}/*.md",
            f"Lectures/{lecture}/code-capsules/*.md",
        ]:
            for path in root.glob(pattern):
                if path.is_file() and path.suffix == ".md":
                    name = path.name
                    if ".partial-" not in name and not name.endswith(".partial.md"):
                        if name in NON_USER_FACING_MD_NAMES:
                            continue
                        expected_paths.add(path.relative_to(root).as_posix())
        for assignment_dir in sorted((root / "Assignments").glob("A*")) if (root / "Assignments").exists() else []:
            if assignment_dir.is_dir():
                for path in assignment_dir.glob("*.md"):
                    expected_paths.add(path.relative_to(root).as_posix())

    missing_from_manifest = sorted(expected_paths - manifest_paths)
    for rel in missing_from_manifest:
        errors.append({"path": rel, "issue": "fixed_publish_family_doc_missing_from_manifest"})

    main_entries = [d for d in documents if isinstance(d, dict) and d.get("role") == "main_entry" and d.get("user_facing") is True]
    if not main_entries:
        errors.append({"issue": "main_entry_missing"})

    checked_docs = 0
    checked_images = 0
    for doc in documents:
        if not isinstance(doc, dict):
            errors.append({"issue": "document_entry_not_object", "entry": repr(doc)[:200]})
            continue
        rel = str(doc.get("path", "")).strip()
        if not rel:
            errors.append({"issue": "document_path_missing", "entry": doc})
            continue
        user_facing = doc.get("user_facing") is True
        image_policy = doc.get("image_policy", "")
        path = (root / rel).resolve()
        if user_facing and image_policy != "remote_url_only":
            errors.append({"path": rel, "issue": "user_facing_doc_without_remote_url_only_policy"})
        if not path.exists():
            errors.append({"path": rel, "issue": "document_missing"})
            continue
        if not user_facing:
            continue
        checked_docs += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        if CONFLICT_MARKER_RE.search(text):
            errors.append({"path": rel, "issue": "git_conflict_marker_present_in_user_facing_doc"})
        for target, _alias in OBSIDIAN_IMAGE_RE.findall(text):
            checked_images += 1
            errors.append({"path": rel, "target": target, "issue": "obsidian_local_image_embed_forbidden_in_user_facing_doc"})
        for alt, target in MD_IMAGE_RE.findall(text):
            checked_images += 1
            target = target.strip()
            if not is_remote(target):
                errors.append({"path": rel, "target": target, "issue": "local_markdown_image_forbidden_in_user_facing_doc"})
            if not alt.strip():
                errors.append({"path": rel, "target": target, "issue": "image_alt_missing"})

    image_upload_map = manifest.get("image_upload_map", [])
    direct_urls = manifest.get("source_url_used_directly", [])
    if image_upload_map is None:
        image_upload_map = []
    if direct_urls is None:
        direct_urls = []
    if not isinstance(image_upload_map, list):
        errors.append({"issue": "image_upload_map_not_list"})
        image_upload_map = []
    if not isinstance(direct_urls, list):
        errors.append({"issue": "source_url_used_directly_not_list"})
        direct_urls = []

    for row in image_upload_map:
        if not isinstance(row, dict):
            errors.append({"issue": "image_upload_map_entry_not_object", "entry": repr(row)[:200]})
            continue
        status = str(row.get("upload_status", "")).strip()
        remote = str(row.get("remote_url", "")).strip()
        local = str(row.get("local_path", "")).strip()
        if status == "uploaded" and not remote:
            errors.append({"local_path": local, "issue": "uploaded_media_missing_remote_url"})
        if remote and not is_remote(remote):
            errors.append({"local_path": local, "target": remote, "issue": "media_remote_url_not_http"})

    remote_images_in_docs: set[str] = set()
    for doc in documents:
        if not isinstance(doc, dict) or doc.get("user_facing") is not True:
            continue
        rel = str(doc.get("path", "")).strip()
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for _alt, target in MD_IMAGE_RE.findall(text):
            if is_remote(target.strip()):
                remote_images_in_docs.add(target.strip())

    known_remote_urls = {
        str(row.get("remote_url", "")).strip()
        for row in image_upload_map
        if isinstance(row, dict)
    } | {
        str(row.get("source_url", "")).strip()
        for row in image_upload_map
        if isinstance(row, dict)
    } | {
        str(row.get("url", "")).strip()
        for row in direct_urls
        if isinstance(row, dict)
    }
    missing_provenance = sorted(url for url in remote_images_in_docs if url and url not in known_remote_urls)
    for url in missing_provenance:
        errors.append({"target": url, "issue": "remote_image_missing_manifest_provenance"})

    errors.extend(scan_related_conflict_markers(root, lecture))

    status = "pass" if not errors else "needs_revision"
    records.append(verdict(
        "deterministic.publish_manifest",
        "deterministic",
        status,
        [{
            "path_or_url": str(manifest_path),
            "locator": f"user_facing_docs={checked_docs}; images={checked_images}; errors={len(errors)}",
            "errors": errors[:80],
        }],
        "Publish manifest and final image policy are valid." if not errors else "Publish manifest or final image policy has violations.",
    ))
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
