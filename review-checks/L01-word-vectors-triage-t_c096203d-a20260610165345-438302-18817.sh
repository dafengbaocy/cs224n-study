#!/usr/bin/env sh
set -eu
cd "/workspace/cs224n-study"
export PATH="/workspace/cs224n-study/.venv/bin:$PATH"
python3 scripts/parse_readings_map.py Lectures/L01-word-vectors/02-readings-map.md --field core_readings --json >/tmp/cs224n-review-core.json && python3 scripts/parse_readings_map.py Lectures/L01-word-vectors/02-readings-map.md --field code_capsules --json >/tmp/cs224n-review-capsules.json && python3 scripts/parse_readings_map.py Lectures/L01-word-vectors/02-readings-map.md --field deepresearch_waypoints --json >/tmp/cs224n-review-deepresearch.json && python3 scripts/parse_readings_map.py Lectures/L01-word-vectors/02-readings-map.md --field deepresearch_waypoints --needs-deepresearch-only >/tmp/cs224n-review-needs.txt && bash scripts/launch_paper_tutor.sh --lecture L01-word-vectors --parent t_2daaf65b --dry-run >/tmp/cs224n-review-paper-tutor-dryrun.txt && bash scripts/launch_code_capsules.sh --lecture L01-word-vectors --parent t_2daaf65b --dry-run >/tmp/cs224n-review-code-capsules-dryrun.txt && bash scripts/launch_deepresearch.sh --lecture L01-word-vectors --parent t_2daaf65b --dry-run >/tmp/cs224n-review-deepresearch-dryrun.txt && python3 - <<'PY'
import json
print('core_readings=', len(json.load(open('/tmp/cs224n-review-core.json'))))
print('code_capsules=', len(json.load(open('/tmp/cs224n-review-capsules.json'))))
print('deepresearch_waypoints=', len(json.load(open('/tmp/cs224n-review-deepresearch.json'))))
print('needs_deepresearch_only:')
print(open('/tmp/cs224n-review-needs.txt').read())
print('paper_tutor_dryrun_tail:')
print(open('/tmp/cs224n-review-paper-tutor-dryrun.txt').read()[-1200:])
print('code_capsules_dryrun_tail:')
print(open('/tmp/cs224n-review-code-capsules-dryrun.txt').read()[-1200:])
print('deepresearch_dryrun_tail:')
print(open('/tmp/cs224n-review-deepresearch-dryrun.txt').read()[-1200:])
PY
