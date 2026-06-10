#!/usr/bin/env bash
# restore_stage_snapshot.sh — restore launch/workspace state from a stage snapshot.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  restore_stage_snapshot.sh --snapshot SNAPSHOT_DIR

Restores the mutable lecture product paths in both launch repo and Hermes
workspace. Current mutable paths are moved to artifacts/stage-restore-backups/
before restore. Logs and artifacts are not deleted.
EOF
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LAUNCH_REPO="${LAUNCH_REPO:-/vol2/1000/docker/cs224n-study}"
HERMES_REPO="${HERMES_REPO:-/vol2/1000/docker/hermes/workspace/cs224n-study}"

SNAPSHOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --snapshot) SNAPSHOT="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "unknown argument: $1" >&2; usage ;;
  esac
done
[[ -z "$SNAPSHOT" ]] && usage

if [[ ! -d "$SNAPSHOT" ]]; then
  echo "snapshot not found: $SNAPSHOT" >&2
  exit 2
fi
MANIFEST="$SNAPSHOT/manifest.txt"
if [[ ! -f "$MANIFEST" ]]; then
  echo "snapshot manifest missing: $SNAPSHOT/manifest.txt" >&2
  exit 2
fi

manifest_value() {
  local key="$1"
  sed -n "s/^${key}=//p" "$MANIFEST" | head -1 | sed -E 's/^"(.*)"$/\1/; s/^'\''(.*)'\''$/\1/'
}

LECTURE="$(manifest_value lecture)"
STAGE="$(manifest_value stage)"
RUN_TAG="$(manifest_value run_tag)"
[[ -z "$LECTURE" || -z "$STAGE" || -z "$RUN_TAG" ]] && {
  echo "snapshot manifest missing lecture/stage/run_tag: $MANIFEST" >&2
  exit 2
}
TS="$(date +%Y%m%d-%H%M%S)"

mutable_paths=(
  "Lectures/$LECTURE"
  "Papers/$LECTURE"
  "Assets/$LECTURE"
  "Labs/$LECTURE"
  "DeepResearch/$LECTURE"
  "Math/$LECTURE"
)

restore_repo() {
  local repo="$1"
  local tarball="$2"
  local label="$3"
  [[ -d "$repo" ]] || return 0
  local backup="$LAUNCH_REPO/artifacts/stage-restore-backups/$LECTURE/$RUN_TAG/$STAGE-$TS/$label"
  mkdir -p "$backup"
  for rel in "${mutable_paths[@]}"; do
    if [[ -e "$repo/$rel" ]]; then
      mkdir -p "$backup/$(dirname "$rel")"
      mv "$repo/$rel" "$backup/$rel"
    fi
  done
  tar -C "$repo" -xzf "$tarball"
  echo "$label restored; previous state backed up at $backup"
}

restore_repo "$LAUNCH_REPO" "$SNAPSHOT/launch-state.tar.gz" "launch"
restore_repo "$HERMES_REPO" "$SNAPSHOT/hermes-state.tar.gz" "hermes"

echo "restored_snapshot=$SNAPSHOT"
echo "lecture=$LECTURE stage=$STAGE run_tag=$RUN_TAG"
