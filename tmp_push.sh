#!/bin/bash
set -euo pipefail
cd /workspace/cs224n-study

# Source token
set -a
source /opt/data/.env
set +a

AUTH=$(echo -n "x-access-token:$GITHUB_TOKEN" | base64)

# Add my files
git add Labs/L01-word-vectors/co-occurrence-matrix.py \
       Labs/L01-word-vectors/co-occurrence-matrix.ipynb \
       Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt \
       Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt \
       Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d.png \
       Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d-window2.png \
       Labs/L01-word-vectors/outputs/co-occurrence-matrix-summary.json \
       Labs/L01-word-vectors/run-log.md

echo "=== git status ==="
git status --short | head -20

echo "=== commit ==="
git commit -m "Add co-occurrence-matrix capsule (WP02) - t_4443cc6a" 2>&1 || echo "nothing to commit"

echo "=== push ==="
git -c "http.https://github.com/.extraheader=AUTHORIZATION: basic $AUTH" \
  push -u origin main 2>&1 | cat
echo "PUSH_EXIT=$?"
