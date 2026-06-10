#!/bin/bash
set -euo pipefail
cd /workspace/cs224n-study

set -a
source /opt/data/.env
set +a

CREDENTIAL="x-ac...intf '%s' "$CREDENTIAL" | base64)

# Add updated .py and .ipynb
git add Labs/L01-word-vectors/co-occurrence-matrix.py \
       Labs/L01-word-vectors/co-occurrence-matrix.ipynb

echo "=== commit ==="
git commit -m "Update co-occurrence-matrix: fix CJK labels, add Chinese teaching notebook" 2>&1 || echo "nothing to commit"

echo "=== push ==="
git -c "http.https://github.com/.extraheader=AUTHORIZATION: basic ${AUTH}" \
  push origin main 2>&1 | cat
echo "PUSH_EXIT=$?"
