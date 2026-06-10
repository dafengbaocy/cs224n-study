#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


try:
    import fitz  # type: ignore
except Exception as e:  # pragma: no cover - deterministic environment check
    print(f"missing_pymupdf={e!r}")
    sys.exit(2)


def readable_pdf(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    try:
        doc = fitz.open(str(path))
        pages = doc.page_count
        doc.close()
    except Exception as e:
        return False, f"open_failed={e!r}"
    if pages <= 0:
        return False, "zero_pages"
    return True, f"pages={pages}"


def lecture_short(lecture: str) -> str:
    m = re.match(r"^([A-Za-z]+[0-9]+)", lecture)
    return m.group(1).lower() if m else lecture.lower()


def lecture_prefix(lecture: str) -> str:
    m = re.match(r"^([A-Za-z]+[0-9]+)", lecture)
    return m.group(1).upper() if m else lecture.split("-", 1)[0].upper()


def readings_map_path(root: Path, lecture: str) -> Path:
    return root / "Lectures" / lecture / "02-readings-map.md"


def read_map(root: Path, lecture: str) -> str:
    path = readings_map_path(root, lecture)
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def extract_core_reading_pdf(root: Path, lecture: str, reading_id: str) -> Path | None:
    text = read_map(root, lecture)
    block_match = re.search(
        rf"(?:slug|id):\s*{re.escape(reading_id)}\b(?P<body>.*?)(?=\n\s*-\s*(?:slug|id):|\n```|\Z)",
        text,
        re.S,
    )
    if block_match:
        body = block_match.group("body")
        local_match = re.search(r"local_pdf:\s*[\"']?([^\"'\n]+?\.pdf)[\"']?\s*(?:\n|$)", body)
        if local_match:
            return root / local_match.group(1).strip()
    local_matches = re.findall(r"local_pdf:\s*[\"']?([^\"'\n]+?\.pdf)[\"']?\s*(?:\n|$)", text)
    for raw in local_matches:
        path = root / raw.strip()
        if reading_id.lower() in path.as_posix().lower():
            return path
    short = lecture_short(lecture)
    candidates = sorted((root / "recovered/assets/papers" / short).glob(f"*{reading_id}*.pdf"))
    return candidates[0] if candidates else None


def extract_official_pdfs(root: Path, lecture: str) -> list[Path]:
    text = read_map(root, lecture)
    short = lecture_short(lecture)
    paths: list[Path] = []
    seen: set[Path] = set()
    for raw in re.findall(r"`([^`]+\.pdf)`", text) + re.findall(r"['\"]([^'\"]+\.pdf)['\"]", text):
        path = root / raw.strip()
        normalized = path.resolve()
        raw_lower = raw.lower()
        if "recovered/assets/official" in raw_lower:
            if normalized not in seen:
                paths.append(path)
                seen.add(normalized)
    official_dir = root / "recovered/assets/official" / short
    if official_dir.exists():
        for path in sorted(official_dir.glob("*.pdf")):
            normalized = path.resolve()
            if normalized not in seen:
                paths.append(path)
                seen.add(normalized)
    return paths


def extract_core_reading_ids(root: Path, lecture: str) -> list[str]:
    text = read_map(root, lecture)
    prefix = lecture_prefix(lecture)
    ids: list[str] = []
    for match in re.findall(r"(?:slug|id):\s*([A-Za-z0-9]+-R[0-9]+)\b", text):
        if match.upper().startswith(prefix + "-") and match not in ids:
            ids.append(match)
    if ids:
        return ids
    return [m for m in re.findall(r"\b[A-Za-z0-9]+-R[0-9]+\b", text) if m not in ids]


def main() -> int:
    parser = argparse.ArgumentParser(description="Scoped source asset check for one production subtask.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--lecture", required=True)
    parser.add_argument("--kind", choices=["paper", "slides", "paper-tutor-integration"], required=True)
    parser.add_argument("--reading-id", default="", help="Required for --kind paper, e.g. {lecture_prefix}-Rxx")
    args = parser.parse_args()

    root = Path(args.root)
    required: list[Path]

    if args.kind == "paper":
        reading_id = args.reading_id or ""
        if not reading_id:
            print("missing_reading_id")
            return 2
        pdf = extract_core_reading_pdf(root, args.lecture, reading_id)
        if not pdf:
            print(f"missing_required_pdf={reading_id}")
            return 2
        required = [pdf]
    elif args.kind == "slides":
        required = extract_official_pdfs(root, args.lecture)
        if not required:
            print(f"missing_official_pdfs_for_lecture={args.lecture}")
            return 2
    else:
        required = [readings_map_path(root, args.lecture)]
        required.extend(extract_official_pdfs(root, args.lecture))
        for reading_id in extract_core_reading_ids(root, args.lecture):
            pdf = extract_core_reading_pdf(root, args.lecture, reading_id)
            if pdf:
                required.append(pdf)

    failures = []
    for path in required:
        if path.suffix.lower() == ".pdf":
            ok, detail = readable_pdf(path)
            if not ok:
                failures.append({"path": str(path), "issue": detail})
        elif not path.exists():
            failures.append({"path": str(path), "issue": "missing"})

    if failures:
        print("required_source_failures=", failures)
        return 2
    print("required_sources_ok=", [str(p) for p in required])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
