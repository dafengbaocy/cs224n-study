#!/usr/bin/env bash
# launch_reviewer.sh - dispatch an independent adversarial reviewer task.
#
# Worker completion only means "ready for review". This launcher creates a
# separate reviewer card whose summary must start with VERDICT: PASS/BLOCK.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPT_TEMPLATE="$REPO_ROOT/docs/production-flow-v2/2026-06-07-stage-prompts-reviewer.md"
HERMES_HOST_REPO="${HERMES_HOST_REPO:-/vol2/1000/docker/hermes/workspace/cs224n-study}"
HERMES_CONTAINER_REPO="${HERMES_CONTAINER_REPO:-/workspace/cs224n-study}"

usage() {
  cat <<'EOF'
Usage:
  launch_reviewer.sh \
    --stage STAGE \
    --lecture LECTURE \
    --target TASK_ID \
    [--parent TASK_ID] \
    [--run-tag TAG] \
    [--artifacts "PATHS"] \
    [--check CMD] \
    [--dry-run]

Options:
  --stage      Stage under review: triage / paper-tutor / capsules / deepresearch / weaver
  --lecture    Lecture id, for example L01-word-vectors
  --target     Worker task id being reviewed
  --parent     Parent for reviewer task; defaults to target
  --run-tag    Unique review attempt tag; re-review after rework must use a new tag
  --artifacts  Space-separated artifact paths for reviewer context
  --check      Optional deterministic check command; output is injected into the card
  --dry-run    Generate reviewer card only; do not create a kanban task
EOF
  exit 1
}

STAGE=""
LECTURE=""
TARGET=""
PARENT=""
RUN_TAG=""
ARTIFACTS=""
CHECK_CMD=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage) STAGE="${2:-}"; shift 2 ;;
    --lecture) LECTURE="${2:-}"; shift 2 ;;
    --target) TARGET="${2:-}"; shift 2 ;;
    --parent) PARENT="${2:-}"; shift 2 ;;
    --run-tag) RUN_TAG="${2:-}"; shift 2 ;;
    --artifacts) ARTIFACTS="${2:-}"; shift 2 ;;
    --check) CHECK_CMD="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage ;;
    *) echo "unknown argument: $1" >&2; usage ;;
  esac
done

[[ -z "$STAGE" || -z "$LECTURE" || -z "$TARGET" ]] && usage
[[ -z "$PARENT" ]] && PARENT="$TARGET"
[[ -z "$RUN_TAG" ]] && RUN_TAG="$(date +%Y%m%d%H%M%S)"
[[ ! -f "$PROMPT_TEMPLATE" ]] && { echo "missing reviewer prompt: $PROMPT_TEMPLATE" >&2; exit 1; }

CHECK_OUT="(no deterministic check)"
CHECK_RC=0
if [[ -n "$CHECK_CMD" ]]; then
  echo "=== deterministic check: $CHECK_CMD ==="
  mkdir -p "$HERMES_HOST_REPO/artifacts/review-checks"
  check_slug="$(printf '%s-%s-%s-%s' "$LECTURE" "$STAGE" "$TARGET" "$RUN_TAG" | tr -c 'A-Za-z0-9_.-' '-')"
  check_host_path="$HERMES_HOST_REPO/artifacts/review-checks/$check_slug.sh"
  check_container_path="$HERMES_CONTAINER_REPO/artifacts/review-checks/$check_slug.sh"
  cat > "$check_host_path" <<EOF
#!/usr/bin/env sh
set -eu
cd "$HERMES_CONTAINER_REPO"
export PATH="$HERMES_CONTAINER_REPO/.venv/bin:\$PATH"
$CHECK_CMD
EOF
  chmod +x "$check_host_path"
  CHECK_OUT="$(sudo docker exec hermes sh "$check_container_path" 2>&1)" || CHECK_RC=$?
  echo "$CHECK_OUT"
  echo "check exit=$CHECK_RC"
fi

CARD="$REPO_ROOT/artifacts/$(date +%Y-%m-%d)-kanban-$LECTURE-reviewer-$STAGE-${TARGET}-${RUN_TAG}.md"
sed "s|{stage}|$STAGE|g; \
     s|{lecture}|$LECTURE|g; \
     s|{target_task}|$TARGET|g; \
     s|{artifact_paths}|$ARTIFACTS|g; \
     s|{check_results}|see deterministic check output below (exit=$CHECK_RC)|g" \
  "$PROMPT_TEMPLATE" > "$CARD"

{
  echo ""
  echo "### deterministic check output (exit=$CHECK_RC)"
  echo '```'
  echo "$CHECK_OUT"
  echo '```'
} >> "$CARD"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[dry-run] reviewer card: $CARD (check exit=$CHECK_RC)"
  exit 0
fi

if [[ "$CHECK_RC" -ne 0 ]]; then
  echo "=== deterministic check failed; creating automatic BLOCK reviewer for $TARGET ==="
  card_body="$(cat "$CARD")"
  json="$(sudo docker exec hermes hermes kanban --board cs224n-study create \
    "CS224N $LECTURE Reviewer [$STAGE] -> $TARGET (deterministic BLOCK)" \
    --body "$card_body" \
    --assignee default \
    --parent "$PARENT" \
    --workspace dir:/workspace/cs224n-study \
    --priority 1 \
    --idempotency-key "cs224n-$LECTURE-reviewer-$STAGE-$TARGET-$RUN_TAG-deterministic-block" \
    --json)"
  reviewer="$(printf '%s' "$json" | python3 -c 'import json,sys; o=json.load(sys.stdin); print(o.get("id") or o.get("task_id") or o.get("task",{}).get("id") or "")')"
  if [[ -z "$reviewer" ]]; then
    echo "failed to create deterministic BLOCK reviewer task" >&2
    exit 2
  fi
  sudo docker exec hermes hermes kanban --board cs224n-study complete \
    --summary "VERDICT: BLOCK

target_task: $TARGET
stage: $STAGE

rule_gate:
  verdict: block
  reason: deterministic check exited $CHECK_RC; LLM content review is not allowed to override Rule Gate failure.

content_gate:
  verdict: not_run
  reason: blocked before content review.

downstream_allowed: false" \
    --result "deterministic_check_failed_exit_$CHECK_RC" \
    "$reviewer" >/dev/null
  echo "task=$reviewer"
  echo "deterministic_block=1"
  exit 0
fi

echo "=== dispatch independent reviewer for $TARGET ==="
"$SCRIPT_DIR/create_cs224n_task_with_notify.sh" \
  --title "CS224N $LECTURE Reviewer [$STAGE] -> $TARGET" \
  --body-file "$CARD" \
  --parent "$PARENT" \
  --idempotency-key "cs224n-$LECTURE-reviewer-$STAGE-$TARGET-$RUN_TAG" \
  --assignee cs224n \
  --priority 92 \
  --max-runtime 1h
