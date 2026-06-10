#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from common import exit_for, verdict, write_jsonl


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
OBSIDIAN_IMAGE_RE = re.compile(r"!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
BLOCK_RE = re.compile(r"(?:^|\s)(\^[A-Za-z0-9_-]+)\s*$")
MATH_BLOCK_RE = re.compile(r"\$\$.*?\$\$", re.S)
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(?!\$).*?(?<!\\)\$", re.S)
BARE_CALLOUT_RE = re.compile(
    r"^\[!(?:note|abstract|summary|tldr|info|todo|tip|hint|important|success|check|done|question|help|faq|warning|caution|attention|failure|fail|missing|danger|error|bug|example|quote|cite)\]",
    re.I,
)


def clean_heading(text: str) -> str:
    return re.sub(r"\s+#+\s*$", "", text.strip())


def strip_math(text: str) -> str:
    text = MATH_BLOCK_RE.sub("", text)
    text = INLINE_MATH_RE.sub("", text)
    return text


def resolve_existing_asset(root: Path, current: Path, raw_target: str) -> Path | None:
    """Resolve local non-markdown assets used in Obsidian/Markdown links."""
    target = raw_target.split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "data:")):
        return None
    if target.startswith(("/workspace/", "/vol2/", "/Users/")):
        return None
    candidates: list[Path] = []
    if target.startswith("../") or target.startswith("./"):
        candidates.append((current.parent / target).resolve())
    elif "/" in target:
        candidates.append((root / target).resolve())
        candidates.append((current.parent / target).resolve())
    else:
        candidates.append((current.parent / target).resolve())
        candidates.append((root / target).resolve())
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def collect_index(root: Path) -> tuple[dict[str, Path], dict[Path, set[str]], dict[Path, set[str]], dict[str, list[Path]]]:
    files = {}
    stems: dict[str, list[Path]] = defaultdict(list)
    headings: dict[Path, set[str]] = {}
    blocks: dict[Path, set[str]] = {}
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        key = rel.with_suffix("").as_posix()
        files[key] = path
        stems[path.stem].append(path)
        hset: set[str] = set()
        bset: set[str] = set()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = HEADING_RE.match(line)
            if m:
                hset.add(clean_heading(m.group(2)))
            bm = BLOCK_RE.search(line)
            if bm:
                bset.add(bm.group(1))
        headings[path] = hset
        blocks[path] = bset
    return files, headings, blocks, stems


def resolve_target(root: Path, current: Path, raw_target: str, files: dict[str, Path], stems: dict[str, list[Path]]) -> tuple[Path | None, str, str | None]:
    if raw_target.startswith("#"):
        return current, "", raw_target[1:]
    if "#" in raw_target:
        path_part, anchor = raw_target.split("#", 1)
    else:
        path_part, anchor = raw_target, None
    path_part = path_part.strip()
    if not path_part:
        return current, "", anchor
    if path_part.startswith("../") or path_part.startswith("./"):
        try:
            return (current.parent / path_part).resolve(), "relative", anchor
        except Exception:
            return None, "relative", anchor
    key = Path(path_part).with_suffix("").as_posix()
    if "/" in path_part:
        return files.get(key), "vault-root", anchor
    same_dir = current.parent / f"{path_part}.md"
    if same_dir.exists():
        return same_dir, "same-dir-short", anchor
    matches = stems.get(Path(path_part).stem, [])
    if len(matches) == 1:
        return matches[0], "global-short", anchor
    return None, "unresolved-short", anchor


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Obsidian wikilinks, headings/block ids, and image paths.")
    parser.add_argument("--root", default=".", help="Vault/project root")
    parser.add_argument("--paths", nargs="*", help="Markdown files or directories to check; default all markdown under root")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    parser.add_argument("--allow-global-short", action="store_true", help="Allow basename links that resolve outside the current directory")
    parser.add_argument("--forbid-local-images", action="store_true", help="Require final-document images to use remote URLs; local/Obsidian image embeds fail")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files, headings, blocks, stems = collect_index(root)

    targets: list[Path] = []
    if args.paths:
        for raw in args.paths:
            p = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
            if p.is_dir():
                targets.extend(sorted(p.rglob("*.md")))
            elif p.exists():
                targets.append(p)
    else:
        targets = sorted(root.rglob("*.md"))

    records = []
    errors = []
    checked_links = 0
    checked_images = 0
    for path in targets:
        text = strip_math(path.read_text(encoding="utf-8", errors="replace"))
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if BARE_CALLOUT_RE.match(line.strip()):
                errors.append({
                    "source": path.relative_to(root).as_posix(),
                    "line": lineno,
                    "issue": "bare_obsidian_callout_missing_blockquote",
                    "detail": "Use '> [!type]' instead of '[!type]' so Obsidian renders the callout.",
                })
        for raw_image, alias in OBSIDIAN_IMAGE_RE.findall(text):
            raw_image = raw_image.strip()
            checked_images += 1
            rel_source = path.relative_to(root).as_posix()
            if args.forbid_local_images:
                errors.append({"source": rel_source, "target": raw_image, "issue": "local_obsidian_image_embed_forbidden"})
                continue
            if raw_image.startswith(("http://", "https://", "data:")):
                continue
            target_file, mode, anchor = resolve_target(root, path, raw_image, files, stems)
            if mode == "relative":
                errors.append({"source": rel_source, "target": raw_image, "issue": "relative_image_wikilink"})
                continue
            if target_file is None or not target_file.exists():
                if resolve_existing_asset(root, path, raw_image):
                    continue
                errors.append({"source": rel_source, "target": raw_image, "issue": "image_missing"})
                continue
        for match in WIKILINK_RE.finditer(text):
            raw_target = match.group(1).strip()
            if match.start() > 0 and text[match.start() - 1] == "!":
                continue
            if raw_target.startswith(("http://", "https://", "data:")):
                continue
            checked_links += 1
            target_file, mode, anchor = resolve_target(root, path, raw_target, files, stems)
            rel_source = path.relative_to(root).as_posix()
            if mode == "relative":
                errors.append({"source": rel_source, "target": raw_target, "issue": "relative_cross_file_wikilink"})
                continue
            if mode == "global-short" and not args.allow_global_short:
                errors.append({"source": rel_source, "target": raw_target, "issue": "global_short_link_not_vault_root_or_same_dir"})
                continue
            if target_file is None or not target_file.exists():
                if resolve_existing_asset(root, path, raw_target):
                    continue
                errors.append({"source": rel_source, "target": raw_target, "issue": "target_file_missing"})
                continue
            if anchor:
                if anchor.startswith("^"):
                    if anchor not in blocks.get(target_file, set()):
                        errors.append({"source": rel_source, "target": raw_target, "issue": "block_id_missing"})
                elif anchor not in headings.get(target_file, set()):
                    errors.append({"source": rel_source, "target": raw_target, "issue": "heading_missing"})
            else:
                errors.append({"source": rel_source, "target": raw_target, "issue": "file_level_link_without_heading_or_block"})
        for raw_image in MD_IMAGE_RE.findall(text):
            raw_image = raw_image.strip()
            if raw_image.startswith(("http://", "https://", "data:")):
                checked_images += 1
                continue
            checked_images += 1
            if args.forbid_local_images:
                errors.append({"source": path.relative_to(root).as_posix(), "target": raw_image, "issue": "local_markdown_image_forbidden"})
                continue
            if raw_image.startswith(("/workspace/", "/vol2/", "/Users/")):
                errors.append({"source": path.relative_to(root).as_posix(), "target": raw_image, "issue": "absolute_local_image_path_forbidden"})
                continue
            if not resolve_existing_asset(root, path, raw_image):
                errors.append({"source": path.relative_to(root).as_posix(), "target": raw_image, "issue": "image_missing"})

    status = "pass" if not errors else "needs_revision"
    records.append(verdict(
        "deterministic.links_headings",
        "deterministic",
        status,
        [{"path_or_url": str(root), "locator": f"links={checked_links}; images={checked_images}; errors={len(errors)}", "errors": errors[:50]}],
        "All checked wikilinks/images resolve." if not errors else "Some wikilinks/images are invalid or not publish-safe.",
    ))
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
