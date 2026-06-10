#!/bin/bash
set -euo pipefail
cd /workspace/cs224n-study

# Source token
set -a
source /opt/data/.env
set +a

# Build auth header
CREDENTIAL="x-access-token:${GITHUB_TOKEN}"
AUTH=$(printf '%s' "$CREDENTIAL" | base64)

# Add remaining files
git add Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt \
       Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt \
       Labs/L01-word-vectors/run-log.md 2>&1 || true

echo "=== status ==="
git status --short | grep -E 'co-occurrence|run-log' | head -10

echo "=== commit ==="
git commit -m "Add co-occurrence-matrix run outputs and run-log entry" 2>&1 || echo "nothing to commit"

echo "=== push ==="
git -c "http.https://github.com/.extraheader=AUTHORIZATION: basic ${AUTH}" \
  push origin main 2>&1 | cat
echo "PUSH_EXIT=$?"
