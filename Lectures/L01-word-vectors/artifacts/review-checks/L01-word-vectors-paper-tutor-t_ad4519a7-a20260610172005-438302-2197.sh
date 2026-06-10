#!/usr/bin/env sh
set -eu
cd "/workspace/cs224n-study"
export PATH="/workspace/cs224n-study/.venv/bin:$PATH"
python3 scripts/review_checks/check_required_sources.py --root . --lecture L01-word-vectors --kind slides && test -f Lectures/L01-word-vectors/03-paper-bridge.partial-slides.md && python3 scripts/review_checks/check_links_headings.py --root . --paths Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md --forbid-local-images && python3 scripts/review_checks/check_media_registry.py --root . --lecture L01-word-vectors --prefix paper-tutor-slides-notes --doc-path Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md --doc-path Lectures/L01-word-vectors/03-paper-bridge.partial-slides.md --asset-path Assets/L01-word-vectors/slides --asset-path Assets/L01-word-vectors/notes --require-for-assets --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5
