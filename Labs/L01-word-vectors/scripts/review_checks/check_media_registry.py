#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from common import exit_for, verdict, write_jsonl


MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
OBSIDIAN_IMAGE_RE = re.compile(r"!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
IGNORED_REMOTE_IMAGE_PATTERNS = [
    re.compile(r"^https://colab\.research\.google\.com/assets/colab-badge\.svg$"),
]
UPLOADED_STATUSES = {"uploaded", "success"}
DIRECT_URL_STATUSES = {"official_url", "source_url", "direct_url"}


def is_remote(target: str) -> bool:
    return target.startswith(("http://", "https://", "data:"))


def clean_optional(value: object) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    return "" if raw.lower() in {"none", "null"} else raw


def is_ignored_remote_image(target: str) -> bool:
    return any(pattern.search(target) for pattern in IGNORED_REMOTE_IMAGE_PATTERNS)


def parse_timestamp(value: object) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    cleaned = raw.replace("Z", "+00:00")
    for candidate in (cleaned, cleaned.replace(" ", "T", 1)):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    return None


def iter_markdown(root: Path, paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        abs_path = p if p.is_absolute() else root / p
        if abs_path.is_dir():
            out.extend(sorted(abs_path.rglob("*.md")))
        elif abs_path.exists() and abs_path.suffix == ".md":
            out.append(abs_path)
    return sorted(set(out))


def iter_assets(root: Path, paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        abs_path = p if p.is_absolute() else root / p
        if abs_path.is_dir():
            out.extend(sorted(x for x in abs_path.rglob("*") if x.is_file() and x.suffix.lower() in IMAGE_EXTS))
        elif abs_path.exists() and abs_path.is_file() and abs_path.suffix.lower() in IMAGE_EXTS:
            out.append(abs_path)
    return sorted(set(out))


def flatten(values: list) -> list[str]:
    out: list[str] = []
    for value in values:
        if isinstance(value, list):
            out.extend(str(item) for item in value)
        else:
            out.append(str(value))
    return out


def load_registry_files(root: Path, lecture: str, prefixes: list[str]) -> tuple[list[Path], list[dict], list[dict]]:
    media_dir = root / "Lectures" / lecture / "media-registry"
    if not media_dir.exists():
        return [], [], []
    files: list[Path] = []
    rows: list[dict] = []
    errors: list[dict] = []
    for path in sorted(media_dir.glob("*.json")):
        if prefixes and not any(path.name.startswith(prefix) for prefix in prefixes):
            continue
        files.append(path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append({"registry": path.relative_to(root).as_posix(), "issue": "registry_json_invalid", "detail": str(exc)})
            continue
        items = data.get("items")
        if not isinstance(items, list):
            legacy_hint = "assets" if isinstance(data.get("assets"), list) else ""
            errors.append({
                "registry": path.relative_to(root).as_posix(),
                "issue": "registry_items_missing_or_not_list",
                "hint": "use top-level items list, not assets" if legacy_hint else "",
            })
            continue
        for item in items:
            if not isinstance(item, dict):
                errors.append({"registry": path.relative_to(root).as_posix(), "issue": "registry_item_not_object"})
                continue
            row = dict(item)
            row["_registry"] = path.relative_to(root).as_posix()
            rows.append(row)
    return files, rows, errors


def collect_doc_images(paths: list[Path], root: Path) -> tuple[list[dict], list[dict]]:
    images: list[dict] = []
    errors: list[dict] = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for target, _alias in OBSIDIAN_IMAGE_RE.findall(text):
            target = target.strip()
            images.append({"doc": rel, "target": target, "kind": "obsidian"})
            errors.append({"path": rel, "target": target, "issue": "obsidian_image_embed_forbidden_in_user_facing_doc"})
        for alt, target in MD_IMAGE_RE.findall(text):
            target = target.strip()
            if is_ignored_remote_image(target):
                continue
            images.append({"doc": rel, "target": target, "kind": "markdown"})
            if not is_remote(target):
                errors.append({"path": rel, "target": target, "issue": "local_markdown_image_forbidden_in_user_facing_doc"})
            if not alt.strip():
                errors.append({"path": rel, "target": target, "issue": "image_alt_missing"})
    return images, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CS224N dual-track media registry for stage artifacts.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--lecture", required=True, help="Lecture id, e.g. L01-word-vectors")
    parser.add_argument("--prefix", action="append", nargs="+", default=[], help="Registry filename prefix to validate. May be repeated.")
    parser.add_argument("--doc-path", action="append", nargs="+", default=[], help="User-facing Markdown file/dir to inspect. May be repeated; shell-expanded globs are accepted.")
    parser.add_argument("--asset-path", action="append", nargs="+", default=[], help="Local image asset file/dir that implies registry coverage. May be repeated.")
    parser.add_argument("--require-registry", action="store_true", help="Require at least one matching registry file.")
    parser.add_argument("--require-for-assets", action="store_true", help="Require registry rows when matching local image assets exist.")
    parser.add_argument("--require-doc-remotes-known", action="store_true", help="Every remote image in inspected docs must appear in registry remote_url/source_url.")
    parser.add_argument("--min-attempts-when-blocked", type=int, default=0, help="If upload_status=blocked, require this many recorded upload attempts.")
    parser.add_argument("--min-gap-seconds-when-blocked", type=int, default=0, help="If upload_status=blocked, require at least this many seconds between adjacent upload attempt timestamps.")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    prefixes = flatten(args.prefix)
    doc_arg_paths = flatten(args.doc_path)
    asset_arg_paths = flatten(args.asset_path)
    doc_paths = iter_markdown(root, doc_arg_paths)
    asset_paths = iter_assets(root, asset_arg_paths)
    registry_files, rows, errors = load_registry_files(root, args.lecture, prefixes)

    doc_images, doc_errors = collect_doc_images(doc_paths, root)
    errors.extend(doc_errors)

    if args.require_registry and not registry_files:
        errors.append({"issue": "media_registry_missing", "prefixes": prefixes})
    if args.require_for_assets and asset_paths and not rows:
        errors.append({
            "issue": "media_registry_required_for_local_assets",
            "asset_count": len(asset_paths),
            "prefixes": prefixes,
        })

    local_rows: dict[str, dict] = {}
    remote_urls: set[str] = set()
    for row in rows:
        registry = str(row.get("_registry", ""))
        asset_id = clean_optional(row.get("asset_id", ""))
        local_path = clean_optional(row.get("local_path", ""))
        source_url = clean_optional(row.get("source_url", row.get("official_url", "")))
        remote_url = clean_optional(row.get("remote_url", ""))
        upload_status = clean_optional(row.get("upload_status", ""))
        source_provenance = clean_optional(row.get("source_provenance", ""))
        alt = clean_optional(row.get("alt", ""))
        attempts_raw = row.get("upload_attempts", [])
        attempts_count = row.get("upload_attempt_count", row.get("attempt_count", 0))
        if isinstance(attempts_raw, list):
            attempts_count = max(int(attempts_count or 0), len(attempts_raw))
        else:
            try:
                attempts_count = int(attempts_count or 0)
            except Exception:
                attempts_count = 0

        if not asset_id:
            errors.append({"registry": registry, "issue": "asset_id_missing"})
        if not source_provenance:
            errors.append({"registry": registry, "asset_id": asset_id, "issue": "source_provenance_missing"})
        if not alt:
            errors.append({"registry": registry, "asset_id": asset_id, "issue": "alt_missing"})
        if upload_status in UPLOADED_STATUSES:
            if not remote_url:
                errors.append({"registry": registry, "asset_id": asset_id, "issue": "uploaded_media_missing_remote_url"})
            elif not is_remote(remote_url):
                errors.append({"registry": registry, "asset_id": asset_id, "target": remote_url, "issue": "remote_url_not_http"})
        elif upload_status in DIRECT_URL_STATUSES:
            direct = source_url or remote_url
            if not direct:
                errors.append({"registry": registry, "asset_id": asset_id, "issue": "direct_url_media_missing_url"})
            elif not is_remote(direct):
                errors.append({"registry": registry, "asset_id": asset_id, "target": direct, "issue": "direct_url_not_http"})
        elif upload_status == "blocked":
            if args.min_attempts_when_blocked and attempts_count < args.min_attempts_when_blocked:
                errors.append({
                    "registry": registry,
                    "asset_id": asset_id,
                    "issue": "blocked_upload_without_required_retries",
                    "attempts": attempts_count,
                    "required_attempts": args.min_attempts_when_blocked,
                    "detail": str(row.get("upload_error", "")).strip(),
                })
            if args.min_gap_seconds_when_blocked:
                if not isinstance(attempts_raw, list) or len(attempts_raw) < max(args.min_attempts_when_blocked, 2):
                    errors.append({
                        "registry": registry,
                        "asset_id": asset_id,
                        "issue": "blocked_upload_missing_attempt_timestamps",
                        "attempts": len(attempts_raw) if isinstance(attempts_raw, list) else 0,
                        "required_attempts": max(args.min_attempts_when_blocked, 2),
                    })
                else:
                    sortable_attempts = []
                    for index, attempt in enumerate(attempts_raw):
                        if not isinstance(attempt, dict):
                            errors.append({"registry": registry, "asset_id": asset_id, "issue": "upload_attempt_not_object", "index": index})
                            continue
                        ts = parse_timestamp(attempt.get("timestamp"))
                        if ts is None:
                            errors.append({
                                "registry": registry,
                                "asset_id": asset_id,
                                "issue": "upload_attempt_timestamp_missing_or_invalid",
                                "index": index,
                                "timestamp": attempt.get("timestamp", ""),
                            })
                            continue
                        try:
                            attempt_no = int(attempt.get("attempt_no", index + 1))
                        except Exception:
                            attempt_no = index + 1
                        sortable_attempts.append((attempt_no, ts))
                    sortable_attempts.sort(key=lambda item: item[0])
                    for (prev_no, prev_ts), (next_no, next_ts) in zip(sortable_attempts, sortable_attempts[1:]):
                        gap = (next_ts - prev_ts).total_seconds()
                        if gap < args.min_gap_seconds_when_blocked:
                            errors.append({
                                "registry": registry,
                                "asset_id": asset_id,
                                "issue": "blocked_upload_retry_gap_too_short",
                                "prev_attempt_no": prev_no,
                                "next_attempt_no": next_no,
                                "gap_seconds": gap,
                                "required_gap_seconds": args.min_gap_seconds_when_blocked,
                            })
        elif local_path and not source_url:
            errors.append({"registry": registry, "asset_id": asset_id, "issue": "upload_status_missing_or_invalid"})
        if local_path:
            local_rows[local_path] = row
            if not (root / local_path).exists():
                errors.append({"registry": registry, "asset_id": asset_id, "local_path": local_path, "issue": "local_path_missing"})
        elif not source_url and not remote_url:
            errors.append({"registry": registry, "asset_id": asset_id, "issue": "local_or_source_url_missing"})
        if remote_url:
            remote_urls.add(remote_url)
        if source_url:
            remote_urls.add(source_url)

    if args.require_for_assets and asset_paths and rows:
        registered_locals = set(local_rows)
        for path in asset_paths:
            rel = path.relative_to(root).as_posix()
            if rel not in registered_locals:
                errors.append({"local_path": rel, "issue": "local_asset_missing_from_media_registry"})

    if args.require_doc_remotes_known:
        for image in doc_images:
            target = str(image.get("target", "")).strip()
            if is_remote(target) and target not in remote_urls:
                errors.append({"path": image.get("doc"), "target": target, "issue": "remote_image_missing_media_registry_provenance"})

    status = "pass" if not errors else "needs_revision"
    records = [verdict(
        "deterministic.media_registry",
        "deterministic",
        status,
        [{
            "path_or_url": f"Lectures/{args.lecture}/media-registry",
            "locator": (
                f"registries={len(registry_files)}; rows={len(rows)}; "
                f"docs={len(doc_paths)}; doc_images={len(doc_images)}; "
                f"local_assets={len(asset_paths)}; errors={len(errors)}"
            ),
            "errors": errors[:80],
        }],
        "Media registry and user-facing image policy are valid." if not errors else "Media registry or user-facing image policy has violations.",
    )]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
