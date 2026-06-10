#!/usr/bin/env bash
# launch_weaver.sh — Lecture Weaver launcher(单任务,最后收口)
#
# 用真正的 prompt 库(2026-06-07-stage-prompts-lecture-weaver.md),
# 替换 {lecture_id}/{topic}/{date} 占位符后投递。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HERMES_REPO="/vol2/1000/docker/hermes/workspace/cs224n-study"
PROMPT_LIB="$REPO_ROOT/docs/production-flow-v2/2026-06-07-stage-prompts-lecture-weaver.md"

usage() {
  cat <<EOF
用法: $0 --lecture LECTURE_ID --parent PARENT_TASK_ID [--run-tag TAG] [--dry-run]

从 prompt 库渲染并投递 Lecture Weaver 任务(单任务收口)。

选项:
  --lecture   讲次 ID（如 L01-word-vectors）
  --parent    父任务 ID
  --run-tag   本次重跑标签，进入 idempotency key
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

[[ ! -f "$PROMPT_LIB" ]] && { echo "错误: prompt 库不存在: $PROMPT_LIB"; exit 1; }

READINGS_MAP="$HERMES_REPO/Lectures/$LECTURE/02-readings-map.md"
[[ ! -f "$READINGS_MAP" ]] && READINGS_MAP="$REPO_ROOT/Lectures/$LECTURE/02-readings-map.md"

# 从 readings-map 提取 topic(行格式: "- L01 topic: ... — Word Vectors")
TOPIC="$LECTURE"
if [[ -f "$READINGS_MAP" ]]; then
  EXTRACTED=$(grep -oE "topic:[^—]*—\s*.+" "$READINGS_MAP" | head -1 | sed -E 's/.*—\s*//' || true)
  [[ -n "$EXTRACTED" ]] && TOPIC="$EXTRACTED"
fi

DATE="$(date +%Y-%m-%d)"
CARD="$REPO_ROOT/artifacts/$DATE-kanban-$LECTURE-weaver.md"

# 渲染:截取模板正文(到 "## 使用说明" 前),替换占位符
python3 - "$PROMPT_LIB" "$LECTURE" "$TOPIC" "$DATE" > "$CARD" <<'PY'
import sys
lib_path, lecture, topic, date = sys.argv[1:5]
text = open(lib_path, encoding="utf-8").read()
# 去掉文末 "## 使用说明" 元说明段(那是给 launcher 的,不进任务卡)
marker = "\n## 使用说明"
if marker in text:
    text = text.split(marker)[0]
text = (text
        .replace("{lecture_id}", lecture)
        .replace("{topic}", topic)
        .replace("{date}", date))
print(text.rstrip())
PY

if [[ -n "$DRY_RUN" ]]; then
  echo "[dry-run] Lecture Weaver 任务卡: $CARD (topic=$TOPIC)"
  exit 0
fi

echo "投递 Lecture Weaver: $LECTURE (topic=$TOPIC)"
TAG_SUFFIX=""
[[ -n "$RUN_TAG" ]] && TAG_SUFFIX="-$RUN_TAG"
bash "$SCRIPT_DIR/create_cs224n_task_with_notify.sh" \
  --title "CS224N $LECTURE Lecture Weaver" \
  --body-file "$CARD" \
  --parent "$PARENT" \
  --idempotency-key "cs224n-$LECTURE-weaver$TAG_SUFFIX" \
  --assignee cs224n \
  --priority 85 \
  --max-runtime 2h
