#!/usr/bin/env sh
set -eu
cd "/workspace/cs224n-study"
export PATH="/workspace/cs224n-study/.venv/bin:$PATH"
python3 scripts/review_checks/check_required_sources.py --root . --lecture L01-word-vectors --kind paper-tutor-integration && python3 scripts/review_checks/check_links_headings.py --root . --paths Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md Lectures/L01-word-vectors/03-paper-bridge*.md Papers/L01-word-vectors --forbid-local-images && python3 scripts/review_checks/check_media_registry.py --root . --lecture L01-word-vectors --prefix paper-tutor- --doc-path Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md --doc-path Lectures/L01-word-vectors/03-paper-bridge*.md --doc-path Papers/L01-word-vectors --asset-path Assets/L01-word-vectors/papers --asset-path Assets/L01-word-vectors/slides --asset-path Assets/L01-word-vectors/notes --require-for-assets --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5
