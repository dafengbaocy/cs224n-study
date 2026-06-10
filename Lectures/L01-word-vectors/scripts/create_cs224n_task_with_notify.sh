#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  create_cs224n_task_with_notify.sh \
    --title TITLE \
    --body-file PATH \
    --parent TASK_ID \
    --idempotency-key KEY \
    [--assignee cs224n] [--priority 90] [--max-runtime 2h]
    [--goal] [--goal-max-turns N]

Creates a task on board cs224n-study, subscribes the bound Weixin DM through
the default gateway, and dispatches one pass. The chat id is read from the
existing Hermes Weixin binding and is never printed.
EOF
}

TITLE=""
BODY_FILE=""
PARENT=""
IDEMPOTENCY_KEY=""
ASSIGNEE="cs224n"
PRIORITY="90"
MAX_RUNTIME="2h"
GOAL=false
GOAL_MAX_TURNS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE="${2:-}"; shift 2 ;;
    --body-file) BODY_FILE="${2:-}"; shift 2 ;;
    --parent) PARENT="${2:-}"; shift 2 ;;
    --idempotency-key) IDEMPOTENCY_KEY="${2:-}"; shift 2 ;;
    --assignee) ASSIGNEE="${2:-}"; shift 2 ;;
    --priority) PRIORITY="${2:-}"; shift 2 ;;
    --max-runtime) MAX_RUNTIME="${2:-}"; shift 2 ;;
    --goal) GOAL=true; shift ;;
    --goal-max-turns) GOAL_MAX_TURNS="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$TITLE" || -z "$BODY_FILE" || -z "$PARENT" || -z "$IDEMPOTENCY_KEY" ]]; then
  usage >&2
  exit 2
fi

if [[ ! -s "$BODY_FILE" ]]; then
  echo "body file missing or empty: $BODY_FILE" >&2
  exit 2
fi

HERMES=(sudo docker exec hermes /opt/hermes/.venv/bin/hermes)
CREATE_EXTRA=()
if [[ "$GOAL" == "true" ]]; then
  CREATE_EXTRA+=(--goal)
  if [[ -n "$GOAL_MAX_TURNS" ]]; then
    CREATE_EXTRA+=(--goal-max-turns "$GOAL_MAX_TURNS")
  fi
fi

task_json="$("${HERMES[@]}" kanban --board cs224n-study create "$TITLE" \
  --body "$(cat "$BODY_FILE")" \
  --assignee "$ASSIGNEE" \
  --parent "$PARENT" \
  --workspace dir:/workspace/cs224n-study \
  --priority "$PRIORITY" \
  --max-runtime "$MAX_RUNTIME" \
  --idempotency-key "$IDEMPOTENCY_KEY" \
  "${CREATE_EXTRA[@]}" \
  --json)"

task_id="$(printf '%s' "$task_json" | python3 -c 'import json, sys; obj=json.load(sys.stdin); print(obj.get("id") or obj.get("task_id") or obj.get("task", {}).get("id") or "")')"

if [[ -z "$task_id" ]]; then
  echo "failed to parse task id" >&2
  echo "$task_json" >&2
  exit 1
fi

chat_id="$(sudo docker exec -i hermes python3 - <<'PY'
import json
from pathlib import Path

accounts = Path("/opt/data/weixin/accounts")
found = []

def walk(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(k, str) and k.endswith("@im.wechat"):
                found.append(k)
            if isinstance(v, str) and v.endswith("@im.wechat"):
                found.append(v)
            if isinstance(v, (dict, list)):
                walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)

for p in sorted(accounts.glob("*.context-tokens.json")):
    try:
        walk(json.loads(p.read_text()))
    except Exception:
        continue

print(found[0] if found else "")
PY
)"

if [[ -z "$chat_id" ]]; then
  echo "task=$task_id"
  echo "warning: no bound Weixin chat id found; task was created but not subscribed" >&2
else
  "${HERMES[@]}" kanban --board cs224n-study notify-subscribe "$task_id" \
    --platform weixin \
    --chat-id "$chat_id" \
    --notifier-profile default >/dev/null
  echo "task=$task_id"
  echo "notify=weixin:default"
fi

"${HERMES[@]}" kanban --board cs224n-study dispatch
