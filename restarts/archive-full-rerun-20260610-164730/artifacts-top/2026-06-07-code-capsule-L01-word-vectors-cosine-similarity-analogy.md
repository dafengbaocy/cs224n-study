# Execution Report: Code Capsule cosine-similarity-analogy (WP06)

**Task**: t_18fe1985
**Parent**: t_f684dfec
**Capsule**: cosine-similarity-analogy
**Concept**: 余弦相似度与词类比算术
**Status**: review-required
**ready_for_review**: true
**downstream_allowed**: false

## Summary

为 L01-word-vectors WP06 制作了 cosine-similarity-analogy code capsule。演示了：
1. Cosine similarity 计算（10 词 toy vocabulary，4 维向量）
2. 经典类比 king - man + woman = queen（cos_sim = 0.9981）
3. 6 组类比测试全部通过
4. 2 组跨域类比失败案例
5. 3 张可视化图表（热力图、2D 投影、结果柱状图）

## Changed Files

- `Labs/L01-word-vectors/cosine-similarity-analogy.py` — 主脚本
- `Labs/L01-word-vectors/cosine-similarity-analogy.ipynb` — Jupyter notebook
- `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stdout.txt` — 运行输出
- `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-heatmap.png` — 热力图
- `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-2d-projection.png` — 2D 投影
- `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-results-chart.png` — 结果柱状图
- `Labs/L01-word-vectors/run-log.md` — 共享运行日志（追加了本任务条目）
- `Lectures/L01-word-vectors/code-capsules/cosine-similarity-analogy.md` — capsule partial
- `Lectures/L01-word-vectors/media-registry/code-capsule-cosine-similarity-analogy.json` — 图片注册

## Real Output Summary

- cos(king, queen) = 0.6157
- cos(king, man) = 0.6738
- cos(man, woman) = 0.3204
- king - man + woman = queen (cos_sim = 0.9981)
- prince - man + woman = princess (cos_sim = 0.9955)
- 6/6 analogy tests passed
- 2 failure cases demonstrated (cross-domain)

## Colab Link

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/cosine-similarity-analogy.ipynb

Verified: HTTP 200 on raw.githubusercontent.com/dafengbaocy/cs224n-study/main/cosine-similarity-analogy.ipynb

## Run-log

- run_id: 20260610T081806Z__t_18fe1985__cosine-similarity-analogy
- exit_code: 0
- No errors, no cells skipped, no cache

## Self-check Results

- [x] Capsule partial exists at correct path with correct heading
- [x] All .py, .ipynb, stdout, outputs, run-log, Colab link exist
- [x] Run-log has unique section matching task_id t_18fe1985
- [x] Key numeric values (0.9981, 0.6157) found in stdout
- [x] Wikilinks use vault-root paths and point to valid glossary headings
- [x] Media registry has correct schema (top-level `items` list)
- [x] All images uploaded to picgo and referenced by remote_url
- [x] No `04-code-capsules.md` written or modified
- [x] No glossary modifications

## Integration Risks

None detected. No sibling capsule partials were modified or found missing.

## Requested Glossary Terms

None — all needed terms (cosine-similarity, analogy, dense-vector) already exist in glossary seed.
