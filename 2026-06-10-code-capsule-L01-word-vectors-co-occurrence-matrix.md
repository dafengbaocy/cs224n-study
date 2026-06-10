# Execution Report: co-occurrence-matrix Code Capsule

**task_id**: t_6ff7c879
**capsule_slug**: co-occurrence-matrix
**waypoint**: WP02 — 分布语义学
**date**: 2026-06-10
**status**: review-required
**ready_for_review**: true
**downstream_allowed**: false

## Summary

为 CS224N L01 的 WP02（分布语义学）制作了 co-occurrence-matrix code capsule。演示了从 15 句小语料构建 30×30 共现矩阵、SVD 降维到 2D、余弦相似度计算和窗口大小对比。

## Changed Files

| File | Description |
|------|-------------|
| `Labs/L01-word-vectors/co-occurrence-matrix.py` | 主脚本：构建共现矩阵 + SVD + 余弦相似度 |
| `Labs/L01-word-vectors/co-occurrence-matrix.ipynb` | Jupyter notebook（中文教学叙述） |
| `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt` | 脚本 stdout |
| `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt` | 脚本 stderr（空） |
| `Labs/L01-word-vectors/outputs/co-occurrence-matrix-output.json` | 结构化输出数据 |
| `Labs/L01-word-vectors/outputs/co-occurrence-matrix-heatmap.png` | 共现矩阵热力图 |
| `Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d.png` | SVD 2D 散点图 |
| `Labs/L01-word-vectors/outputs/co-occurrence-matrix-cosine-sim.png` | 余弦相似度柱状图 |
| `Labs/L01-word-vectors/outputs/co-occurrence-matrix-window-comparison.png` | 窗口大小对比图 |
| `Labs/L01-word-vectors/run-log.md` | 共享运行日志（追加） |
| `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md` | Capsule partial |
| `Lectures/L01-word-vectors/media-registry/code-capsule-co-occurrence-matrix.json` | 图片注册表 |

## Key Outputs

- 词汇量 V=30，共现矩阵 30×30，window=1 非零元素 74/900 (8.2%)
- M[cat,dog]=4, M[book,tech]=3, M[cat,book]=0
- SVD 前 2 奇异值占总能量 41.7%
- cat-dog cos=1.0000, book-tech cos=1.0000, cat-book cos=-0.0000
- 4 张图片全部上传成功

## Colab Link Blocker

**colab_link**: blocked
**reason**: GitHub push 因多 worker 并发 rebase 冲突失败（study-ops github-push 内部 git pull --rebase 遇到冲突）。本地 .ipynb 已生成，可手动上传或等待冲突解决后重试。
**local_notebook**: Labs/L01-word-vectors/co-occurrence-matrix.ipynb

## Self-check Results

- [x] Capsule partial 存在于 `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md`
- [x] Heading 为 `## co-occurrence-matrix — 从语料构建共现矩阵并做 SVD 降维 {#co-occurrence-matrix}`
- [x] .py, .ipynb, stdout, run-log 路径都存在
- [x] Colab 链接：blocked（已记录原因）
- [x] run-log 中有唯一 section：task_id=t_6ff7c879, capsule_slug=co-occurrence-matrix
- [x] 正文中的关键数值能在 stdout 中找到
- [x] 图片使用 remote_url，不使用本地路径
- [x] media-registry JSON 使用顶层 items 列表
- [x] glossary 链接使用 vault-root 路径
- [x] 未修改 04-code-capsules.md 或其他 capsule partial
- [x] notebook 使用中文教学叙述

## Integration Risks

无。本 capsule 未修改其他 capsule 的文件。

## Requested Glossary Terms

无。所有需要的术语（co-occurrence-matrix, svd, cosine-similarity）已在 glossary seed 中。
