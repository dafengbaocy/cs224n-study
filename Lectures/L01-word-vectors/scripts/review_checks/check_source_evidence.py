#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

from common import exit_for, verdict, write_jsonl

try:
    import fitz  # type: ignore
except Exception:
    fitz = None


URL_RE = re.compile(r"url:\s*[\"']?(https?://[^\"'\s]+)")
PATH_KEYS = {
    "local_path",
    "headers_path",
    "evidence_html",
    "evidence_text",
    "zip_manifest",
    "schedule_row",
    "slides_text",
    "notes_text",
    "a1_notebook_text",
    "url_probe_evidence",
}
SHA_RE = re.compile(r"sha256:\s*[\"']?([a-fA-F0-9]{64})")
SIZE_BLOCK_RE = re.compile(r"local_path:\s*[\"']?([^\"'\n]+).*?size_bytes:\s*(\d+).*?sha256:\s*[\"']?([a-fA-F0-9]{64})", re.S)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_readable(path: Path) -> tuple[bool, str]:
    if fitz is not None:
        try:
            doc = fitz.open(str(path))
            page_count = doc.page_count
            doc.close()
            return page_count > 0, f"pymupdf_pages={page_count}"
        except Exception as e:
            return False, f"pymupdf_open_failed={repr(e)}"
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        return False, "missing_pdf_header"
    page_markers = len(re.findall(rb"/Type\s*/Page\b", data))
    if page_markers <= 0:
        return False, "no_page_markers_without_pymupdf"
    return True, f"pdf_header_marker_fallback_pages={page_markers}"


def http_status(url: str, timeout: int) -> tuple[bool, str]:
    try:
        req = Request(url, method="HEAD", headers={"User-Agent": "cs224n-review-check/0.1"})
        with urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400, str(resp.status)
    except Exception as e:
        try:
            req = Request(url, method="GET", headers={"User-Agent": "cs224n-review-check/0.1", "Range": "bytes=0-0"})
            with urlopen(req, timeout=timeout) as resp:
                return 200 <= resp.status < 400, str(resp.status)
        except Exception as e2:
            return False, f"{type(e).__name__}/{type(e2).__name__}"


def iter_path_values(text: str) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("-"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key.strip() not in PATH_KEYS:
            continue
        value = value.strip().strip('"').strip("'")
        if not value or value in {"null", "false", "true", "[]"}:
            continue
        if value.startswith(("http://", "https://")):
            continue
        values.append(value)
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Check source evidence locks: URLs, local files, sha256, PDF/zip readability.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--locks", nargs="*", default=["Sources/course-source-lock.yaml", "Sources/readings-canonical-lock.yaml"], help="Lock/evidence files relative to root")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    parser.add_argument("--check-http", action="store_true", help="Probe URLs live; off by default to avoid slow runs")
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = []
    evidence = []
    urls = []
    checked_files = 0
    checked_hashes = 0
    checked_pdfs = 0
    checked_zips = 0

    for lock_raw in args.locks:
        lock = root / lock_raw
        if not lock.exists():
            errors.append({"source": lock_raw, "issue": "lock_missing"})
            continue
        text = lock.read_text(encoding="utf-8", errors="replace")
        urls.extend(URL_RE.findall(text))
        for raw in iter_path_values(text):
            p = root / raw
            checked_files += 1
            if not p.exists():
                errors.append({"source": lock_raw, "path": raw, "issue": "evidence_path_missing"})
        for local_path, expected_size, expected_sha in SIZE_BLOCK_RE.findall(text):
            raw = local_path.strip().strip('"').strip("'")
            p = root / raw
            if not p.exists():
                errors.append({"source": lock_raw, "path": raw, "issue": "hashed_file_missing"})
                continue
            checked_hashes += 1
            actual_size = p.stat().st_size
            if actual_size != int(expected_size):
                errors.append({"source": lock_raw, "path": raw, "issue": "size_mismatch", "expected": int(expected_size), "actual": actual_size})
            actual_sha = sha256(p)
            if actual_sha.lower() != expected_sha.lower():
                errors.append({"source": lock_raw, "path": raw, "issue": "sha256_mismatch", "expected": expected_sha, "actual": actual_sha})
            if p.suffix.lower() == ".pdf":
                checked_pdfs += 1
                ok, detail = pdf_readable(p)
                if not ok:
                    errors.append({"source": lock_raw, "path": raw, "issue": "pdf_readability_failed", "detail": detail})
            if p.suffix.lower() == ".zip":
                checked_zips += 1
                try:
                    with zipfile.ZipFile(p) as zf:
                        bad = zf.testzip()
                        if bad:
                            errors.append({"source": lock_raw, "path": raw, "issue": "zip_bad_entry", "entry": bad})
                except Exception as e:
                    errors.append({"source": lock_raw, "path": raw, "issue": "zip_open_failed", "error": repr(e)})

    http_bad = []
    if args.check_http:
        for url in sorted(set(urls)):
            ok, status = http_status(url, args.timeout)
            if not ok:
                http_bad.append({"url": url, "status": status})
        errors.extend({"source": "url_probe", "issue": "http_probe_failed", **item} for item in http_bad)

    evidence.append({
        "path_or_url": str(root),
        "locator": f"locks={len(args.locks)}; urls={len(set(urls))}; files={checked_files}; hashes={checked_hashes}; pdfs={checked_pdfs}; zips={checked_zips}; http_checked={args.check_http}; errors={len(errors)}",
        "errors": errors[:80],
    })
    status = "pass" if not errors else "needs_revision"
    records = [verdict(
        "deterministic.source_evidence",
        "deterministic",
        status,
        evidence,
        "Source evidence files, checksums, and readable PDF/zip assets passed." if not errors else "Source evidence has missing files, hash mismatches, unreadable assets, or failed HTTP probes.",
    )]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
