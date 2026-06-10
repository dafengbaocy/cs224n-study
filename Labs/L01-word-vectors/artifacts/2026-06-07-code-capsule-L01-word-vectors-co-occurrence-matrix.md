# Execution Report: Code Capsule co-occurrence-matrix (WP02)

- task_id: t_4443cc6a
- parent: t_2daaf65b
- capsule_slug: co-occurrence-matrix
- concept: 从语料构建共现矩阵并做 SVD 降维
- official_anchor: Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3
- waypoint: WP02

## Status

- ready_for_review: true
- downstream_allowed: false

## Changed Files

- `Labs/L01-word-vectors/co-occurrence-matrix.py` — 主脚本（6 句 toy corpus, V=22, window 1/2/3 对比）
- `Labs/L01-word-vectors/co-occurrence-matrix.ipynb` — 中文教学 notebook（18 cells, 9 markdown + 9 code）
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt` — 真实 stdout
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt` — 空（无 warning）
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d.png` — window=1 散点图
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d-window2.png` — window=2 散点图
- `Labs/L01-word-vectors/outputs/co-occurrence-matrix-summary.json` — JSON 摘要
- `Labs/L01-word-vectors/run-log.md` — 共享 run-log（flock 追加）
- `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md` — capsule partial
- `Lectures/L01-word-vectors/media-registry/code-capsule-co-occurrence-matrix.json` — 图片注册

## Real Output Summary

- Corpus: 6 sentences, V=22
- Window=1: non-zero 56/484 = 11.6%, sparsity 88.4%
- Window=2: non-zero 92/484 = 19.0%
- Window=3: non-zero 113/484 = 23.3%
- Top-2 singular values (window=1): [5.988, 5.754]
- Key distances (window=1): cat-dog=0.1713, bank-river=0.1771, bank-money=2.0382, cat-money=2.2262
- Key distances (window=2): cat-dog=1.0407, bank-river=0.9898, bank-money=2.0619, cat-money=2.2063

## Colab Link

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/co-occurrence-matrix.ipynb

Verified: HTTP 200 from unauthenticated GET.

## Image Uploads

| asset | remote_url | status |
|-------|-----------|--------|
| svd-2d-window1 | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174805.png | uploaded (1 attempt) |
| svd-2d-window2 | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174808.png | uploaded (1 attempt) |

## Run-log

- run_id: 20260610T094147Z__t_4443cc6a__co-occurrence-matrix
- exit_code: 0
- stderr: empty (no warnings)
- notes: Clean run. CJK labels replaced with English for headless matplotlib compatibility.

## Self-check Results

- [x] Capsule partial exists at `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md`
- [x] Heading: `## co-occurrence-matrix — 从语料构建共现矩阵并做 SVD 降维 {#co-occurrence-matrix}`
- [x] .py, .ipynb, stdout, stderr, run-log, Colab link all exist
- [x] Run-log has unique section with task_id, capsule_slug, run_id, command, exit_code, stdout, outputs
- [x] All numeric values in partial traceable to stdout
- [x] Glossary links use vault-root paths (e.g., `[[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]]`)
- [x] No modification to `04-code-capsules.md` or other capsule partials
- [x] Media registry uses `items` schema (not `assets`)
- [x] All images in partial use `remote_url` (no local paths)
- [x] Notebook uses Chinese teaching content (not mechanical .py translation)

## Integration Risks

None detected. No sibling capsule partials were modified or found missing.

## Requested Glossary Terms

None — all needed terms already exist in glossary seed:
- co-occurrence-matrix
- svd
- dense-vector
- cosine-similarity
