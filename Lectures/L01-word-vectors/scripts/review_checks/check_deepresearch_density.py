#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl


NUMBERED_MECHANISM_HEADING_RE = re.compile(r"^###\s+4\.(\d+)\s+(.+?)\s*$", re.M)
GENERIC_H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)
ANCHOR_RE = re.compile(r"\b(?:slides?|Slides?|notes?|Notes?|R0\d|Figure|Table|Eq\(|A1|lines?\s+\d+|page\s+\d+|§\d)", re.I)
FORMULA_RE = re.compile(r"```math|```text|(?<!\\)\$[^$\n]+(?<!\\)\$")
EXAMPLE_RE = re.compile(r"例子|样本|具体|比如|例如|banking|GloVe|cosine|analogy|motel|hotel", re.I)


def _section_rows(text: str, matches: list[re.Match[str]], *, id_prefix: str) -> list[dict]:
    sections: list[dict] = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else text.find("\n## ", start + 1)
        if end == -1:
            end = len(text)
        body = text[start:end]
        title = match.group(match.lastindex or 1).strip()
        sections.append(
            {
                "id": f"{id_prefix}{i + 1}",
                "title": title,
                "text": body,
                "chars": len(body),
                "lines": body.count("\n") + 1,
                "anchor_refs": len(ANCHOR_RE.findall(body)),
                "formula_refs": len(FORMULA_RE.findall(body)),
                "examples": len(EXAMPLE_RE.findall(body)),
            }
        )
    return sections


def _h3s_under_h2(text: str, h2_keywords: tuple[str, ...]) -> list[re.Match[str]]:
    h2s = list(H2_RE.finditer(text))
    for i, h2 in enumerate(h2s):
        if not any(keyword in h2.group(1) for keyword in h2_keywords):
            continue
        start = h2.end()
        end = h2s[i + 1].start() if i + 1 < len(h2s) else len(text)
        offset = start
        return [
            _OffsetMatch(match, offset)
            for match in GENERIC_H3_RE.finditer(text[start:end])
        ]
    return []


class _OffsetMatch:
    def __init__(self, match: re.Match[str], offset: int):
        self._match = match
        self._offset = offset
        self.lastindex = match.lastindex

    def start(self) -> int:
        return self._offset + self._match.start()

    def group(self, *args):
        return self._match.group(*args)


def waypoint_sections(text: str) -> list[dict]:
    numbered = list(NUMBERED_MECHANISM_HEADING_RE.finditer(text))
    if numbered:
        sections: list[dict] = []
        for i, match in enumerate(numbered):
            start = match.start()
            end = numbered[i + 1].start() if i + 1 < len(numbered) else text.find("\n## 5.", start)
            if end == -1:
                end = len(text)
            body = text[start:end]
            sections.append(
                {
                    "id": f"4.{match.group(1)}",
                    "title": match.group(2).strip(),
                    "text": body,
                    "chars": len(body),
                    "lines": body.count("\n") + 1,
                    "anchor_refs": len(ANCHOR_RE.findall(body)),
                    "formula_refs": len(FORMULA_RE.findall(body)),
                    "examples": len(EXAMPLE_RE.findall(body)),
                }
            )
        return sections

    mechanism = _h3s_under_h2(text, ("机制层解释", "机制解释"))
    if mechanism:
        return _section_rows(text, mechanism, id_prefix="mechanism.")

    generic = list(GENERIC_H3_RE.finditer(text))
    return _section_rows(text, generic, id_prefix="section.")


def density_score(section: dict) -> float:
    # Keep this intentionally simple and interpretable. Formula weight is lower
    # because some late waypoints are application/bridge sections, not derivations.
    return (
        section["chars"] / 100.0
        + section["anchor_refs"] * 1.5
        + section["formula_refs"] * 0.8
        + section["examples"] * 0.8
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DeepResearch waypoint density for possible context-pressure tail collapse.")
    parser.add_argument("path", help="DeepResearch markdown file")
    parser.add_argument("--output", default="", help="Optional JSONL output path")
    parser.add_argument("--threshold", type=float, default=0.70, help="Late/early density ratio below which review is needed")
    parser.add_argument("--min-waypoints", type=int, default=4, help="Minimum waypoint count before ratio check applies")
    parser.add_argument("--print-metrics", action="store_true", help="Print metrics JSON to stdout in addition to JSONL verdict")
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8", errors="replace")
    sections = waypoint_sections(text)
    metrics = []
    for section in sections:
        row = {k: v for k, v in section.items() if k != "text"}
        row["density_score"] = round(density_score(section), 2)
        metrics.append(row)

    errors = []
    status = "pass"
    reason = "DeepResearch waypoint density has no obvious late-section collapse."

    if len(sections) == 0:
        status = "needs_revision"
        errors.append({"issue": "no_parseable_deepresearch_sections"})
        reason = "No parseable DeepResearch sections found; density check cannot validate coverage."
    elif len(sections) < args.min_waypoints:
        status = "pass"
        reason = f"Only {len(sections)} waypoint sections found; ratio check skipped."
    else:
        n = max(1, len(sections) // 3)
        early = sections[:n]
        late = sections[-n:]
        early_avg = sum(density_score(s) for s in early) / len(early)
        late_avg = sum(density_score(s) for s in late) / len(late)
        ratio = late_avg / early_avg if early_avg else 1.0
        if ratio < args.threshold:
            status = "needs_revision"
            errors.append(
                {
                    "issue": "needs_revision_context_pressure",
                    "early_avg": round(early_avg, 2),
                    "late_avg": round(late_avg, 2),
                    "ratio": round(ratio, 3),
                    "threshold": args.threshold,
                }
            )
            reason = "Late waypoint density is much lower than early waypoint density; possible context-pressure tail collapse."
        else:
            reason = f"Late/early density ratio {ratio:.2f} is above threshold {args.threshold:.2f}."

    record = verdict(
        "deterministic.deepresearch_density",
        "deterministic",
        status,
        [
            {
                "path_or_url": str(path),
                "locator": f"waypoints={len(sections)}; threshold={args.threshold}",
                "metrics": metrics,
                "errors": errors,
            }
        ],
        reason,
    )
    if args.print_metrics:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    write_jsonl([record], args.output)
    return exit_for([record])


if __name__ == "__main__":
    sys.exit(main())
