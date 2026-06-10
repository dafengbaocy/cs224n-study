#!/usr/bin/env python3
"""render_paper_tutor_cards.py — 从 paper-tutor prompt 库渲染任务卡。

读 readings-map 的 core_readings + slides/notes 元数据,把 prompt 库模板里的
占位符替换成本讲次/本篇具体值,每篇 core reading 输出一个 paper 任务卡,
外加一个 slides/notes 任务卡。

用法:
  render_paper_tutor_cards.py \
    --readings-map PATH --prompt-lib PATH --lecture L01-word-vectors \
    --out-dir artifacts --date 2026-06-08

输出: 打印每个任务卡的 "kind\tslug\ttitle\tcard_path"(TSV),供 bash 消费。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_readings_map import extract_field  # noqa: E402


def lecture_short(lecture_id: str) -> str:
    """L01-word-vectors -> l01"""
    m = re.match(r"^([A-Za-z]+[0-9]+)", lecture_id)
    return m.group(1).lower() if m else lecture_id.lower()


def reading_short(slug: str) -> str:
    """取末尾 R\\d+ 作为阅读短码；取不到则用整 slug。"""
    m = re.search(r"(R[0-9]+)$", slug)
    return m.group(1) if m else slug


def split_templates(lib_text: str) -> dict[str, str]:
    """把 prompt 库按 '## Paper Tutor —' 切成模板段。返回 {kind: text}。"""
    parts = re.split(r"^## Paper Tutor — ", lib_text, flags=re.M)
    templates = {}
    for p in parts[1:]:
        head = p.splitlines()[0]
        body = "## Paper Tutor — " + p
        if "单篇论文" in head:
            templates["paper"] = body
        elif "slides" in head or "notes" in head:
            templates["slides"] = body
    return templates


def paper_slug(reading_id: str, title: str) -> str:
    """从标题生成文件名 slug(取前几个有意义的词)。"""
    words = re.findall(r"[A-Za-z]+", title.lower())
    stop = {"of", "in", "the", "a", "an", "and", "for", "to", "their"}
    kept = [w for w in words if w not in stop][:5]
    return "-".join(kept) if kept else reading_id.lower()


def extract_slides_meta(text: str) -> dict[str, str]:
    """从 readings-map 的 '- Slides: `path`, N pages' 行提取元数据。"""
    meta = {}
    for label, key in [("Slides", "slides"), ("Notes", "notes")]:
        m = re.search(rf"^- {label}:\s*`([^`]+)`,\s*(\d+)\s*page", text, re.M)
        if m:
            meta[f"{key}_pdf"] = m.group(1)
            meta[f"{key}_pages"] = m.group(2)
        else:
            meta[f"{key}_pdf"] = f"recovered/assets/official/<lecture>/{key}.pdf"
            meta[f"{key}_pages"] = "?"
    return meta


def render(template: str, repl: dict[str, str]) -> str:
    out = template
    for k, v in repl.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readings-map", required=True)
    ap.add_argument("--prompt-lib", required=True)
    ap.add_argument("--lecture", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--date", required=True)
    args = ap.parse_args()

    rm_text = open(args.readings_map, encoding="utf-8").read()
    lib_text = open(args.prompt_lib, encoding="utf-8").read()
    templates = split_templates(lib_text)
    if "paper" not in templates or "slides" not in templates:
        print("ERROR: prompt 库缺 paper 或 slides 模板", file=sys.stderr)
        return 1

    lec = args.lecture
    lec_short = lecture_short(lec)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base = {
        "lecture_id": lec,
        "lecture_short": lec_short,
        "date": args.date,
    }

    rows = []

    # 1. 每篇 core reading 一个 paper 任务卡
    readings, _, _ = extract_field(rm_text, "core_readings")
    for r in readings:
        if not isinstance(r, dict):
            continue
        rid = str(r.get("slug") or r.get("id") or "")
        if not rid:
            continue
        rshort = reading_short(rid)
        title = str(r.get("title") or "")
        repl = dict(base)
        repl.update({
            "reading_id": rid,
            "reading_short": rshort,
            "reading_short_lower": rshort.lower(),
            "paper_title": title,
            "paper_slug": paper_slug(rid, title),
            "paper_url": str(r.get("paper_url") or ""),
            "canonical_url": str(r.get("canonical_url") or ""),
            "local_pdf": str(r.get("local_pdf") or ""),
            "official_anchor": str(r.get("official_anchor") or ""),
            "waypoint_focus": ", ".join(r.get("waypoint_focus") or []) if isinstance(r.get("waypoint_focus"), list) else str(r.get("waypoint_focus") or ""),
            "paper_tutor_focus": str(r.get("paper_tutor_focus") or ""),
        })
        card = render(templates["paper"], repl)
        card_path = out_dir / f"{args.date}-kanban-{lec_short}-paper-tutor-{rshort.lower()}.md"
        card_path.write_text(card, encoding="utf-8")
        rows.append(f"paper\t{rid}\t{title}\t{card_path}")

    # 2. slides/notes 任务卡(每讲一个)
    slides_meta = extract_slides_meta(rm_text)
    repl = dict(base)
    repl.update(slides_meta)
    card = render(templates["slides"], repl)
    card_path = out_dir / f"{args.date}-kanban-{lec_short}-paper-tutor-slides-notes.md"
    card_path.write_text(card, encoding="utf-8")
    rows.append(f"slides\t{lec}-slides\tslides/notes 教学图\t{card_path}")

    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
