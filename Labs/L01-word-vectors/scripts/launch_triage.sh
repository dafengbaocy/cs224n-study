#!/usr/bin/env bash
# launch_triage.sh — Reading Triage launcher(单任务,流水线源头)
#
# 用真正的 prompt 库(2026-06-08-stage-prompts-triage.md),替换
# {lecture_id}/{lecture_short}/{topic}/{date} 占位符后投递。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPT_LIB="$REPO_ROOT/docs/production-flow-v2/2026-06-08-stage-prompts-triage.md"

usage() {
  cat <<EOF
用法: $0 --lecture LECTURE_ID --parent PARENT_TASK_ID [--topic TOPIC] [--run-tag TAG] [--dry-run]

从 prompt 库渲染并投递 Reading Triage 任务(单任务,建 readings-map)。

选项:
  --lecture   讲次 ID（如 L01-word-vectors）
  --parent    父任务 ID
  --topic     讲次主题（如 "Word Vectors"，可选，默认从 lecture-id 推导）
  --run-tag   重跑标签，加入 idempotency key，避免复用旧归档任务
  --dry-run   只渲染任务卡不投递

示例:
  $0 --lecture L01-word-vectors --parent t_6cbffd16 --topic "Word Vectors"
EOF
  exit 1
}

LECTURE="" ; PARENT="" ; TOPIC="" ; DRY_RUN="" ; RUN_TAG="${RUN_TAG:-}"
while [[ $# -gt 0 ]]; do
  case $1 in
    --lecture) LECTURE="$2"; shift 2 ;;
    --parent)  PARENT="$2";  shift 2 ;;
    --topic)   TOPIC="$2";   shift 2 ;;
    --run-tag) RUN_TAG="$2"; shift 2 ;;
    --dry-run) DRY_RUN="1"; shift ;;
    *) usage ;;
  esac
done
[[ -z "$LECTURE" || -z "$PARENT" ]] && usage
[[ ! -f "$PROMPT_LIB" ]] && { echo "错误: prompt 库不存在: $PROMPT_LIB"; exit 1; }

# lecture_short: L01-word-vectors -> l01
LECTURE_SHORT=$(echo "$LECTURE" | sed -E 's/^([A-Za-z]+[0-9]+).*/\1/' | tr '[:upper:]' '[:lower:]')
# lecture_short_upper: l01 -> L01（core_readings slug 前缀用）
LECTURE_SHORT_UPPER=$(echo "$LECTURE_SHORT" | tr '[:lower:]' '[:upper:]')
# topic 默认从 lecture-id 推导（L01-word-vectors -> word vectors）
[[ -z "$TOPIC" ]] && TOPIC=$(echo "$LECTURE" | sed -E 's/^[A-Za-z]+[0-9]+-//; s/-/ /g')

DATE="$(date +%Y-%m-%d)"
CARD="$REPO_ROOT/artifacts/$DATE-kanban-$LECTURE-triage.md"
TAG_SUFFIX=""
[[ -n "$RUN_TAG" ]] && TAG_SUFFIX="-$RUN_TAG"

# 渲染:截取模板正文(到 "## 使用说明" 前),替换占位符
python3 - "$PROMPT_LIB" "$LECTURE" "$LECTURE_SHORT" "$LECTURE_SHORT_UPPER" "$TOPIC" "$DATE" > "$CARD" <<'PY'
import sys
lib_path, lecture, lec_short, lec_short_upper, topic, date = sys.argv[1:7]
text = open(lib_path, encoding="utf-8").read()
marker = "\n## 使用说明"
if marker in text:
    text = text.split(marker)[0]
text = (text
        .replace("{lecture_id}", lecture)
        .replace("{lecture_short_upper}", lec_short_upper)
        .replace("{lecture_short}", lec_short)
        .replace("{topic}", topic)
        .replace("{date}", date))
print(text.rstrip())
PY

if [[ -n "$DRY_RUN" ]]; then
  echo "[dry-run] Reading Triage 任务卡: $CARD (topic=$TOPIC)"
  exit 0
fi

echo "投递 Reading Triage: $LECTURE (topic=$TOPIC)"
bash "$SCRIPT_DIR/create_cs224n_task_with_notify.sh" \
  --title "CS224N $LECTURE Reading Triage" \
  --body-file "$CARD" \
  --parent "$PARENT" \
  --idempotency-key "cs224n-$LECTURE-triage$TAG_SUFFIX" \
  --assignee cs224n \
  --priority 95 \
  --max-runtime 2h
