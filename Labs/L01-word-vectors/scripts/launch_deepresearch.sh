#!/usr/bin/env bash
# CS224N DeepResearch 启动脚本（泛化版）
# 读取 02-readings-map.md 的 deepresearch_waypoints 字段，为每个 waypoint 生成任务卡并投递

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPT_TEMPLATE="$REPO_ROOT/docs/production-flow-v2/2026-06-07-stage-prompts-deepresearch.md"
if [[ -z "${PYTHON_BIN:-}" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
  if [[ ! -x "$PYTHON_BIN" ]] || ! "$PYTHON_BIN" -c "import yaml" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  fi
fi

usage() {
  cat <<EOF
用法: $0 --lecture LECTURE_ID --parent PARENT_TASK_ID [--dry-run]

参数:
  --lecture   讲次 ID（如 L01-word-vectors）
  --parent    父任务 ID（如 t_6cbffd16）
  --dry-run   只生成任务卡，不投递

示例:
  $0 --lecture L01-word-vectors --parent t_6cbffd16
EOF
  exit 1
}

# 解析参数
LECTURE=""
PARENT=""
DRY_RUN=false
RUN_TAG="${RUN_TAG:-}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --lecture) LECTURE="$2"; shift 2 ;;
    --parent) PARENT="$2"; shift 2 ;;
    --run-tag) RUN_TAG="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) usage ;;
  esac
done

[[ -z "$LECTURE" || -z "$PARENT" ]] && usage

READINGS_MAP="$REPO_ROOT/Lectures/$LECTURE/02-readings-map.md"
[[ ! -f "$READINGS_MAP" ]] && { echo "错误: $READINGS_MAP 不存在"; exit 1; }

# 用 Python 解析器读 deepresearch_waypoints，只取 needs_deepresearch: true 的条目
# （健壮处理多行 reason/research_question 块；自动跳过官方已讲透的 waypoint）
PARSER="$SCRIPT_DIR/parse_readings_map.py"
[[ ! -f "$PARSER" ]] && { echo "错误: 解析器 $PARSER 不存在"; exit 1; }

PARSED=$("$PYTHON_BIN" "$PARSER" "$READINGS_MAP" --field deepresearch_waypoints --needs-deepresearch-only)
if [[ -z "$PARSED" ]]; then
  echo "没有 needs_deepresearch: true 的 waypoint（可能官方材料都讲透了，或 readings-map 未判定）"
  exit 0
fi

echo "$PARSED" | while IFS=$'\t' read -r waypoint title question anchor; do

  SLUG=$(echo "$waypoint" | tr '[:upper:]' '[:lower:]' | sed 's/wp//')
  TAG_SUFFIX=""
  [[ -n "$RUN_TAG" ]] && TAG_SUFFIX="-$RUN_TAG"
  TASK_CARD="$REPO_ROOT/artifacts/$(date +%Y-%m-%d)-kanban-$LECTURE-deepresearch-$SLUG$TAG_SUFFIX.md"
  IDEMPOTENCY_KEY="cs224n-$LECTURE-deepresearch-$SLUG-$(date +%Y%m%d)$TAG_SUFFIX"

  echo "生成任务卡: $waypoint - $title"

  # 从模板生成任务卡（替换占位符）
  sed "s|{lecture_id}|$LECTURE|g; \
       s|{waypoint_id_and_title}|$waypoint - $title|g; \
       s|{具体问题}|$question|g; \
       s|{downstream_consumer}|lecture-weaver / code-capsule-runner|g; \
       s|{slides 页 / notes 页 / paper section/equation/figure}|$anchor|g" \
    "$PROMPT_TEMPLATE" > "$TASK_CARD"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] 任务卡: $TASK_CARD"
  else
    echo "  投递任务..."
    "$SCRIPT_DIR/create_cs224n_task_with_notify.sh" \
      --title "CS224N $LECTURE DeepResearch $waypoint" \
      --body-file "$TASK_CARD" \
      --parent "$PARENT" \
      --idempotency-key "$IDEMPOTENCY_KEY" \
      --assignee cs224n \
      --priority 85 \
      --max-runtime 3h \
      --goal \
      --goal-max-turns 8
  fi
done

echo "DeepResearch 任务批量生成完成"
