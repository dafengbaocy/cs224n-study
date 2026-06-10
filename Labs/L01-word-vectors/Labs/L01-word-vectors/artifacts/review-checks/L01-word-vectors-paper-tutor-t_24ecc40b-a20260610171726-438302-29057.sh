#!/usr/bin/env sh
set -eu
cd "/workspace/cs224n-study"
export PATH="/workspace/cs224n-study/.venv/bin:$PATH"
python3 scripts/review_checks/check_required_sources.py --root . --lecture L01-word-vectors --kind paper --reading-id L01-R02 && test -f Lectures/L01-word-vectors/03-paper-bridge.partial-r02.md && python3 scripts/review_checks/check_links_headings.py --root . --paths Papers/L01-word-vectors/*R02*.md --forbid-local-images && python3 scripts/review_checks/check_media_registry.py --root . --lecture L01-word-vectors --prefix paper-tutor-r02 --doc-path Papers/L01-word-vectors/*R02*.md --doc-path Lectures/L01-word-vectors/03-paper-bridge.partial-r02.md --asset-path Assets/L01-word-vectors/papers/*R02* --require-for-assets --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5
