#!/usr/bin/env bash
# snapshot_stage.sh — save launch/workspace state before a stage starts.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  snapshot_stage.sh --lecture LECTURE --stage STAGE --run-tag TAG

Creates:
  artifacts/stage-snapshots/<lecture>/<tag>/<stage>-<timestamp>/
    launch-state.tar.gz
    hermes-state.tar.gz
    manifest.txt
EOF
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LAUNCH_REPO="${LAUNCH_REPO:-/vol2/1000/docker/cs224n-study}"
HERMES_REPO="${HERMES_REPO:-/vol2/1000/docker/hermes/workspace/cs224n-study}"

LECTURE=""
STAGE=""
RUN_TAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lecture) LECTURE="${2:-}"; shift 2 ;;
    --stage) STAGE="${2:-}"; shift 2 ;;
    --run-tag) RUN_TAG="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "unknown argument: $1" >&2; usage ;;
  esac
done

[[ -z "$LECTURE" || -z "$STAGE" || -z "$RUN_TAG" ]] && usage

TS="$(date +%Y%m%d-%H%M%S)"
SNAP_DIR="$LAUNCH_REPO/artifacts/stage-snapshots/$LECTURE/$RUN_TAG/$STAGE-$TS"
mkdir -p "$SNAP_DIR"

mutable_paths=(
  "Lectures/$LECTURE"
  "Papers/$LECTURE"
  "Assets/$LECTURE"
  "Labs/$LECTURE"
  "DeepResearch/$LECTURE"
  "Math/$LECTURE"
)

tar_existing() {
  local repo="$1"
  local out="$2"
  local list
  list="$(mktemp)"
  for rel in "${mutable_paths[@]}"; do
    if [[ -e "$repo/$rel" ]]; then
      printf '%s\n' "$rel" >> "$list"
    fi
  done
  if [[ -s "$list" ]]; then
    tar -C "$repo" -czf "$out" -T "$list"
  else
    tar -C "$repo" -czf "$out" --files-from /dev/null
  fi
  rm -f "$list"
}

tar_existing "$LAUNCH_REPO" "$SNAP_DIR/launch-state.tar.gz"
if [[ -d "$HERMES_REPO" ]]; then
  tar_existing "$HERMES_REPO" "$SNAP_DIR/hermes-state.tar.gz"
else
  tar -C "$LAUNCH_REPO" -czf "$SNAP_DIR/hermes-state.tar.gz" --files-from /dev/null
fi

cat > "$SNAP_DIR/manifest.txt" <<EOF
lecture=$LECTURE
stage=$STAGE
run_tag=$RUN_TAG
timestamp=$TS
launch_repo=$LAUNCH_REPO
hermes_repo=$HERMES_REPO
mutable_paths="${mutable_paths[*]}"
restore_command='bash scripts/restore_stage_snapshot.sh --snapshot "$SNAP_DIR"'
EOF

ln -sfn "$SNAP_DIR" "$LAUNCH_REPO/artifacts/stage-snapshots/$LECTURE/$RUN_TAG/latest-$STAGE"
echo "$SNAP_DIR"
