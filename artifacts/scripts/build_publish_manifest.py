#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def doc(path: Path, role: str, user_facing: bool = True) -> dict:
    return {
        "path": path.as_posix(),
        "role": role,
        "user_facing": user_facing,
        "image_policy": "remote_url_only" if user_facing else "local_assets_allowed",
    }


def add_if_exists(documents: list[dict], root: Path, rel: str, role: str, *, required: bool = False) -> None:
    path = Path(rel)
    if required or (root / path).exists():
        documents.append(doc(path, role, True))


NON_USER_FACING_MD_NAMES = {
    "run-log.md",
}


def add_glob(
    documents: list[dict],
    root: Path,
    pattern: str,
    role: str,
    *,
    exclude_partials: bool = True,
    exclude_names: set[str] | None = None,
) -> None:
    exclude_names = exclude_names or set()
    for path in sorted(root.glob(pattern)):
        if not path.is_file() or path.suffix != ".md":
            continue
        rel = path.relative_to(root)
        name = rel.name
        if exclude_partials and (".partial-" in name or name.endswith(".partial.md")):
            continue
        if name in exclude_names:
            continue
        documents.append(doc(rel, role, True))


def dedupe_documents(documents: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for item in documents:
        key = item["path"]
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def load_media_registry(root: Path, lecture: str) -> tuple[list[dict], list[dict]]:
    items: list[dict] = []
    direct_urls: list[dict] = []
    media_dir = root / "Lectures" / lecture / "media-registry"
    if not media_dir.exists():
        return items, direct_urls
    for path in sorted(media_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for item in data.get("items", []):
            if not isinstance(item, dict):
                continue
            row = {
                "asset_id": item.get("asset_id", ""),
                "local_path": item.get("local_path", ""),
                "remote_url": item.get("remote_url", ""),
                "source_url": item.get("source_url", item.get("official_url", "")),
                "source_provenance": item.get("source_provenance", ""),
                "used_in": item.get("used_in", item.get("used_for", [])),
                "alt": item.get("alt", ""),
                "upload_status": item.get("upload_status", ""),
                "registry": path.relative_to(root).as_posix(),
            }
            items.append(row)
            source_url = str(row.get("source_url") or "").strip()
            remote_url = str(row.get("remote_url") or "").strip()
            local_path = str(row.get("local_path") or "").strip()
            if source_url and (not local_path or source_url == remote_url):
                direct_urls.append({
                    "url": source_url,
                    "asset_id": row["asset_id"],
                    "source_provenance": row["source_provenance"],
                    "alt": row["alt"],
                    "registry": row["registry"],
                })
    return items, direct_urls


def merge_image_upload_map(existing_rows: list, registry_rows: list[dict]) -> list[dict]:
    merged: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for row in [*(existing_rows if isinstance(existing_rows, list) else []), *registry_rows]:
        if not isinstance(row, dict):
            continue
        key = (str(row.get("local_path", "")), str(row.get("remote_url", "")))
        if key in seen:
            continue
        seen.add(key)
        merged.append(row)
    return merged


def merge_direct_urls(existing_rows: list, registry_rows: list[dict]) -> list[dict]:
    merged: list[dict] = []
    seen: set[str] = set()
    for row in [*(existing_rows if isinstance(existing_rows, list) else []), *registry_rows]:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url", "")).strip()
        if not url or url in seen:
            continue
        seen.add(url)
        merged.append(row)
    return merged


def collect_direct_urls_from_docs(root: Path, documents: list[dict]) -> list[dict]:
    rows: list[dict] = []
    colab_badge = "https://colab.research.google.com/assets/colab-badge.svg"
    for item in documents:
        if not isinstance(item, dict) or item.get("user_facing") is not True:
            continue
        rel = str(item.get("path", "")).strip()
        path = root / rel
        if not path.exists() or path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if colab_badge in text:
            rows.append({
                "url": colab_badge,
                "asset_id": "colab-badge",
                "source_provenance": "Google Colab standard UI badge used in notebook launch links.",
                "alt": "Open In Colab",
                "used_in": rel,
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic CS224N publish manifest from the fixed publish family.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--lecture", required=True, help="Lecture id, e.g. L01-word-vectors")
    parser.add_argument("--output", default="", help="Output manifest path; default Lectures/<lecture>/publish-manifest.json")
    parser.add_argument("--assignment", action="append", default=[], help="Assignment id to include, e.g. A1. May be repeated.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    lecture = args.lecture
    output = Path(args.output) if args.output else Path("Lectures") / lecture / "publish-manifest.json"
    output_abs = (root / output).resolve() if not output.is_absolute() else output.resolve()

    existing: dict = {}
    if output_abs.exists():
        try:
            existing = json.loads(output_abs.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    documents: list[dict] = []

    # Fixed lecture publish family. This is a contract, not a link-discovery result.
    add_if_exists(documents, root, f"Lectures/{lecture}/00-课堂入口.md", "main_entry", required=True)
    add_if_exists(documents, root, f"Lectures/{lecture}/01-官方课件带读.md", "official_walkthrough")
    add_if_exists(documents, root, f"Lectures/{lecture}/03-本讲概念卡.md", "concept_cards")
    add_if_exists(documents, root, f"Lectures/{lecture}/04-code-capsules.md", "code_capsules")
    add_if_exists(documents, root, f"Lectures/{lecture}/05-复习检查.md", "review_check")
    add_if_exists(documents, root, f"Lectures/{lecture}/00-concept-glossary.md", "glossary")
    add_if_exists(documents, root, f"Lectures/{lecture}/06-code-capsules.md", "code_capsules_legacy")
    add_if_exists(documents, root, f"Lectures/{lecture}/99-glossary.md", "glossary_legacy")

    # Human-readable supplemental family. Include even when the main entry has not linked them yet.
    add_glob(documents, root, f"DeepResearch/{lecture}/*.md", "deepresearch_detail")
    add_glob(documents, root, f"Papers/{lecture}/*.md", "paper_note")
    add_glob(documents, root, f"Math/{lecture}/*.md", "math_note")
    add_glob(documents, root, f"Lectures/{lecture}/code-capsules/*.md", "code_capsule_detail")
    # Labs contains runnable code, outputs, and audit/provenance sidecars.
    # User-facing explanations live in Lectures/<lecture>/code-capsules/*.md.
    # Do not publish Labs/*.md by default; add explicit lab study notes later
    # only when an assignment/lab stage creates a learner-facing document.

    for assignment in args.assignment:
        add_glob(documents, root, f"Assignments/{assignment}/*.md", "assignment_study")

    registry_rows, direct_url_rows = load_media_registry(root, lecture)

    documents = dedupe_documents(documents)
    direct_doc_rows = collect_direct_urls_from_docs(root, documents)

    manifest = {
        "contract": "cs224n-publish-family-v1",
        "lecture": lecture,
        "generation": {
            "method": "scripts/build_publish_manifest.py",
            "rule": "fixed_publish_family_plus_existing_supplements_not_link_discovery",
        },
        "documents": documents,
        "image_upload_map": merge_image_upload_map(existing.get("image_upload_map", []), registry_rows),
        "source_url_used_directly": merge_direct_urls(existing.get("source_url_used_directly", []), [*registry_rows, *direct_doc_rows]),
    }

    output_abs.parent.mkdir(parents=True, exist_ok=True)
    output_abs.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_abs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
