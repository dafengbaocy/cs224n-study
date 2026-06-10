#!/usr/bin/env sh
set -eu
cd "/workspace/cs224n-study"
export PATH="/workspace/cs224n-study/.venv/bin:$PATH"
.venv/bin/python scripts/review_checks/check_links_headings.py --root . --paths Lectures/L01-word-vectors/code-capsules/one-hot-vs-dense.md Lectures/L01-word-vectors/00-concept-glossary.md --forbid-local-images && .venv/bin/python scripts/review_checks/check_media_registry.py --root . --lecture L01-word-vectors --prefix code-capsule-one-hot-vs-dense --doc-path Lectures/L01-word-vectors/code-capsules/one-hot-vs-dense.md --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5 && .venv/bin/python scripts/review_checks/check_code_capsule_run_log.py --root . --lecture L01-word-vectors --slug one-hot-vs-dense --task-id t_a1b9e9f6 && .venv/bin/python scripts/review_checks/check_notebook_chinese.py --root . --paths Labs/L01-word-vectors/one-hot-vs-dense.ipynb && .venv/bin/python - <<'PY'
from pathlib import Path
bad = [p for p in [Path('Labs/L01-word-vectors/04-code-capsules.md')] if p.exists()]
if bad:
    print('forbidden_code_capsules_copies=', [str(p) for p in bad])
    raise SystemExit(2)
slug = 'one-hot-vs-dense'
integration = 'capsules' == 'capsules-integration'
if integration:
    partials = sorted(Path('Lectures/L01-word-vectors/code-capsules').glob('*.md'))
else:
    if not slug:
        print('missing_code_capsule_slug_for_target=t_a1b9e9f6')
        raise SystemExit(2)
    partial = Path('Lectures/L01-word-vectors/code-capsules') / f'{slug}.md'
    if not partial.exists():
        print('missing_capsule_partial=', partial)
        raise SystemExit(2)
    partials = [partial]
print('capsule_partials=', [p.name for p in partials])
for p in partials:
    text = p.read_text(encoding='utf-8')
    if 'numeric_provenance' not in text:
        print('missing_numeric_provenance=', p)
        raise SystemExit(2)
if not integration and Path('Lectures/L01-word-vectors/04-code-capsules.md').exists():
    print('premature_merged_code_capsules_doc=Lectures/L01-word-vectors/04-code-capsules.md')
    raise SystemExit(2)
if integration and Path('Lectures/L01-word-vectors/04-code-capsules.md').exists():
    merged = Path('Lectures/L01-word-vectors/04-code-capsules.md').read_text(encoding='utf-8')
    if 'merge_code_capsules.py' not in merged:
        print('merged_doc_missing_generation_note')
        raise SystemExit(2)
PY
