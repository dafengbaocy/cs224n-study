#!/usr/bin/env bash
# launch_publisher_finalizer.sh — final publish/sync stage launcher
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPT_LIB="$REPO_ROOT/docs/production-flow-v2/2026-06-09-stage-prompts-publisher-finalizer.md"

usage() {
  cat <<'EOF'
Usage:
  launch_publisher_finalizer.sh --lecture LECTURE --parent TASK_ID [--run-tag TAG] [--dry-run]
EOF
  exit 1
}

LECTURE=""
PARENT=""
RUN_TAG=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lecture) LECTURE="${2:-}"; shift 2 ;;
    --parent) PARENT="${2:-}"; shift 2 ;;
    --run-tag) RUN_TAG="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage ;;
    *) echo "unknown argument: $1" >&2; usage ;;
  esac
done

[[ -z "$LECTURE" || -z "$PARENT" ]] && usage
[[ ! -f "$PROMPT_LIB" ]] && { echo "missing prompt library: $PROMPT_LIB" >&2; exit 1; }

DATE="$(date +%Y-%m-%d)"
TAG_SUFFIX=""
if [[ -n "$RUN_TAG" ]]; then
  TAG_SUFFIX="-$RUN_TAG"
fi

TOPIC="$LECTURE"
if [[ -f "$REPO_ROOT/Lectures/$LECTURE/02-readings-map.md" ]]; then
  TOPIC="$(python3 - <<PY
from pathlib import Path
import re
p=Path('$REPO_ROOT/Lectures/$LECTURE/02-readings-map.md')
text=p.read_text(encoding='utf-8', errors='replace')
m=re.search(r'(?im)^topic:\\s*(.+)$', text)
print(m.group(1).strip() if m else '$LECTURE')
PY
)"
fi

CARD="$REPO_ROOT/artifacts/$DATE-kanban-$LECTURE-publisher-finalizer$TAG_SUFFIX.md"
sed "s|{lecture_id}|$LECTURE|g; s|{topic}|$TOPIC|g" "$PROMPT_LIB" > "$CARD"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[dry-run] publisher-finalizer card: $CARD"
  exit 0
fi

"$SCRIPT_DIR/create_cs224n_task_with_notify.sh" \
  --title "CS224N $LECTURE Publisher Finalizer" \
  --body-file "$CARD" \
  --parent "$PARENT" \
  --idempotency-key "cs224n-$LECTURE-publisher-finalizer$TAG_SUFFIX-$DATE" \
  --assignee cs224n \
  --priority 94 \
  --max-runtime 1h
