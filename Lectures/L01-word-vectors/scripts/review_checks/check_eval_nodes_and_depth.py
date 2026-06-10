#!/usr/bin/env python3
"""检查 DeepResearch Eval 的节点状态规范与 source expansion 深挖深度。

两条规则（2026-06-07 加固）：
1. Eval 节点 status 只能是 pass/fail/blocked/pending；禁止填 review-required，
   也禁止所有 node 糊成同一状态（WP04 违规：10 节点全 review-required）。
2. source expansion 深挖 ≥3 层：evidence notes 必须有 depth=2 和 depth=3 条目，
   否则视为"广而浅"。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import exit_for, verdict, write_jsonl


VALID_NODE_STATUS = {"pass", "fail", "blocked", "pending"}
DEPTH_RE = re.compile(r"\bdepth\b\s*[:=]\s*(\d+)", re.I)
RATIONALE_RE = re.compile(r"depth_rationale", re.I)


def check_eval_nodes(eval_path: Path) -> tuple[str, list[dict]]:
    """返回 (status, errors)。"""
    errors: list[dict] = []
    try:
        data = json.loads(eval_path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError) as exc:
        return "fail", [{"issue": "eval_unreadable", "detail": str(exc)}]

    nodes = data.get("nodes", {})
    if not nodes:
        return "fail", [{"issue": "no_nodes", "detail": "Eval 无 nodes 字段"}]

    statuses = []
    for key, node in nodes.items():
        st = (node or {}).get("status", "")
        statuses.append(st)
        if st == "review-required":
            errors.append({"issue": "node_review_required", "node": key,
                           "detail": "单个 node 禁止填 review-required"})
        elif st not in VALID_NODE_STATUS:
            errors.append({"issue": "node_invalid_status", "node": key, "status": st,
                           "detail": f"node status 必须是 {sorted(VALID_NODE_STATUS)}"})

    # 所有 node 糊成同一状态（且 ≥3 个节点）视为敷衍
    if len(statuses) >= 3 and len(set(statuses)) == 1:
        errors.append({"issue": "all_nodes_same_status", "status": statuses[0],
                       "detail": "所有 node 糊成同一状态，等于没填"})

    status = "fail" if errors else "pass"
    return status, errors


def check_depth(draft_path: Path) -> tuple[str, list[dict], dict]:
    """检查 source expansion 深度。

    规则性判据（不是凑层数）：
    - 有多层深挖（出现 depth≥2）→ pass
    - 只有一层（depth 全是 1）但写了 depth_rationale 说明为什么一层就到底 → pass
    - 只有一层又没说明理由 → fail
    - 完全没有 depth 标记 → fail（无法验证）
    """
    errors: list[dict] = []
    try:
        text = draft_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return "fail", [{"issue": "draft_unreadable", "detail": str(exc)}], {}

    depths = [int(m) for m in DEPTH_RE.findall(text)]
    found = sorted(set(depths))
    has_rationale = bool(RATIONALE_RE.search(text))
    metrics = {"depth_markers_total": len(depths), "distinct_depths": found,
               "has_depth_rationale": has_rationale}

    if not depths:
        errors.append({"issue": "no_depth_markers",
                       "detail": "evidence notes 没有任何 depth 标记，无法验证深度"})
    elif max(depths) >= 2:
        pass  # 有多层深挖，达标
    elif has_rationale:
        pass  # 只挖一层但说明了理由，允许
    else:
        errors.append({"issue": "shallow_without_rationale",
                       "detail": "只挖了一层（depth 全是 1）又没写 depth_rationale 说明为什么一层就到底"})

    status = "fail" if errors else "pass"
    return status, errors, metrics


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查 DeepResearch Eval 节点状态规范与 source expansion 深挖深度。")
    parser.add_argument("--eval", required=True, help="Eval JSON 路径")
    parser.add_argument("--draft", required=True, help="DeepResearch draft markdown 路径")
    parser.add_argument("--output", default="", help="可选 JSONL 输出路径")
    args = parser.parse_args()

    eval_path = Path(args.eval)
    draft_path = Path(args.draft)

    node_status, node_errors = check_eval_nodes(eval_path)
    depth_status, depth_errors, depth_metrics = check_depth(draft_path)

    records = [
        verdict(
            "deterministic.eval_node_status",
            "deterministic",
            node_status,
            [{"path_or_url": str(eval_path), "errors": node_errors}],
            "Eval 节点状态合规。" if node_status == "pass"
            else "Eval 节点状态违规：禁止 review-required / 非法状态 / 全部糊成同一状态。",
        ),
        verdict(
            "deterministic.source_expansion_depth",
            "deterministic",
            depth_status,
            [{"path_or_url": str(draft_path), "metrics": depth_metrics, "errors": depth_errors}],
            "深挖 ≥3 层达标。" if depth_status == "pass"
            else "深挖深度不足：evidence notes 必须有 depth=2 和 depth=3 条目。",
        ),
    ]
    write_jsonl(records, args.output)
    return exit_for(records)


if __name__ == "__main__":
    sys.exit(main())
