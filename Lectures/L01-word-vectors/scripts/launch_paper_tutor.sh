#!/usr/bin/env bash
# launch_paper_tutor.sh — Paper Tutor launcher
#
# 读 readings-map 的 core_readings + slides/notes 元数据,用 render 脚本从
# 真正的 prompt 库(2026-06-07-stage-prompts-paper-tutor.md)渲染任务卡:
#   - 每篇 core reading 一个 paper 任务
#   - slides/notes 教学图抽取一个任务
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HERMES_REPO="/vol2/1000/docker/hermes/workspace/cs224n-study"
PROMPT_LIB="$REPO_ROOT/docs/production-flow-v2/2026-06-07-stage-prompts-paper-tutor.md"
if [[ -z "${PYTHON_BIN:-}" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
  if [[ ! -x "$PYTHON_BIN" ]] || ! "$PYTHON_BIN" -c "import yaml" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  fi
fi

usage() {
  cat <<EOF
用法: $0 --lecture LECTURE_ID --parent PARENT_TASK_ID [--run-tag TAG] [--dry-run]

读 readings-map 的 core_readings,从 prompt 库渲染并投递 Paper Tutor 任务:
  - 每篇 core reading 一个 paper 精读任务
  - 一个 slides/notes 教学图抽取任务

选项:
  --lecture   讲次 ID（如 L01-word-vectors）
  --parent    父任务 ID
  --run-tag   本次重跑标签，进入 idempotency key 和任务卡名
  --dry-run   只渲染任务卡不投递

示例:
  $0 --lecture L01-word-vectors --parent t_6cbffd16
EOF
  exit 1
}

LECTURE="" ; PARENT="" ; DRY_RUN="" ; RUN_TAG="${RUN_TAG:-}"
while [[ $# -gt 0 ]]; do
  case $1 in
    --lecture) LECTURE="$2"; shift 2 ;;
    --parent)  PARENT="$2";  shift 2 ;;
    --run-tag) RUN_TAG="$2"; shift 2 ;;
    --dry-run) DRY_RUN="1"; shift ;;
    *) usage ;;
  esac
done
[[ -z "$LECTURE" || -z "$PARENT" ]] && usage

READINGS_MAP="$HERMES_REPO/Lectures/$LECTURE/02-readings-map.md"
[[ ! -f "$READINGS_MAP" ]] && READINGS_MAP="$REPO_ROOT/Lectures/$LECTURE/02-readings-map.md"
[[ ! -f "$READINGS_MAP" ]] && { echo "错误: readings-map 不存在 (先跑 Triage)"; exit 1; }
[[ ! -f "$PROMPT_LIB" ]] && { echo "错误: prompt 库不存在: $PROMPT_LIB"; exit 1; }

DATE="$(date +%Y-%m-%d)"

echo "=== 渲染 Paper Tutor 任务卡 (从 prompt 库) ==="
RENDER_OUT=$("$PYTHON_BIN" "$SCRIPT_DIR/render_paper_tutor_cards.py" \
  --readings-map "$READINGS_MAP" \
  --prompt-lib "$PROMPT_LIB" \
  --lecture "$LECTURE" \
  --out-dir "$REPO_ROOT/artifacts" \
  --date "$DATE") || { echo "render 失败"; exit 1; }

echo "$RENDER_OUT" | while IFS=$'\t' read -r kind slug title card_path; do
  [[ -z "$kind" ]] && continue
  if [[ -n "$DRY_RUN" ]]; then
    echo "[dry-run] $kind: $slug — $title"
    echo "          任务卡: $card_path"
    continue
  fi
  echo "投递 Paper Tutor [$kind]: $slug — $title"
  TAG_SUFFIX=""
  [[ -n "$RUN_TAG" ]] && TAG_SUFFIX="-$RUN_TAG"
  bash "$SCRIPT_DIR/create_cs224n_task_with_notify.sh" \
    --title "CS224N $LECTURE Paper Tutor: $slug" \
    --body-file "$card_path" \
    --parent "$PARENT" \
    --idempotency-key "cs224n-$LECTURE-paper-tutor-$slug$TAG_SUFFIX" \
    --assignee cs224n \
    --priority 90 \
    --max-runtime 2h
done

echo "Paper Tutor 任务批量处理完成"
