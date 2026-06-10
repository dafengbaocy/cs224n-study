# Execution Report: co-occurrence-matrix Code Capsule

## Task Info
- task_id: t_ab4e78fa
- capsule_slug: co-occurrence-matrix
- waypoint: WP02
- concept: 从语料构建共现矩阵并做 SVD 降维
- ready_for_review: true
- downstream_allowed: false

## Changed Files
- `Labs/L01-word-vectors/co-occurrence-matrix.py` — main script
- `Labs/L01-word-vectors/co-occurrence-matrix.ipynb` — Jupyter notebook (Chinese teaching)
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt` — stdout capture
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt` — stderr (empty)
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d.png` — SVD 2D scatter
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-window-comparison.png` — window comparison
- `Labs/L01-word-vectors/run-log.md` — shared run-log (appended with flock)
- `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md` — capsule partial
- `Lectures/L01-word-vectors/media-registry/code-capsule-co-occurrence-matrix.json` — media registry

## Run Summary
- Corpus: 15 sentences, 30 vocab words, 3 semantic groups (animal/tech/water)
- Window size: 1 (default), compared with 2 and 3
- Matrix: 30×30, 74 non-zero entries, total count 90
- SVD top-2 explained variance: 41.7%
- Singular values top 5: [5.6095, 5.1033, 4.5859, 3.7147, 3.5055]

## Key Results (from actual stdout)
| Pair | cos_sim | Relation |
|------|---------|----------|
| cat-dog | 1.0000 | Same category (animal) |
| book-tech | 1.0000 | Same topic (tech) |
| fish-water | 1.0000 | Strong collocation |
| cat-book | -0.0000 | Different topic (orthogonal) |
| dog-tech | 0.0000 | Different topic (orthogonal) |
| fish-book | -0.0000 | No shared context |

## Colab Link
https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/co-occurrence-matrix.ipynb

## Image Uploads
- SVD 2D: https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-182213.png (1 attempt, success)
- Window comparison: https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-182225.png (1 attempt, success)

## Run-log
- run_id: 20260610T101832Z__t_ab4e78fa__co-occurrence-matrix
- exit_code: 0
- No errors, no skipped cells

## Self-check Results
- [x] Capsule partial exists at `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md`
- [x] Heading: `## co-occurrence-matrix — 从语料构建共现矩阵并做 SVD 降维 {#co-occurrence-matrix}`
- [x] .py, .ipynb, stdout, run-log, Colab link all exist
- [x] Key numeric values (cos_sim, vocab_size, matrix shape) match stdout
- [x] Glossary links use vault-root paths (e.g., `[[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]]`)
- [x] Images use remote_url, not local paths
- [x] Media registry written with correct schema (top-level `items` list)
- [x] Did NOT write `04-code-capsules.md`
- [x] Did NOT modify other capsule partials

## Integration Risks
- The .py script was modified by concurrent processes during this run. The final version on disk may differ from what was actually executed. The stdout capture is authoritative for numeric values.
- The capsule partial was also modified by a concurrent process; I fixed a duplicate section.

## Requested Glossary Terms
- None missing; all linked terms (co-occurrence-matrix, svd, dense-vector, cosine-similarity) exist in the glossary seed.
