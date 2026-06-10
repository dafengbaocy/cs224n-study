# Execution Report: Code Capsule one-hot-vs-dense (WP01)

- **Task**: `t_a3b87099`
- **Parent**: `t_f684dfec`
- **Capsule**: one-hot-vs-dense
- **Concept**: One-hot 向量 vs 密集词向量的对比
- **Waypoint**: WP01 — 为什么需要词向量？
- **Official anchor**: Slides p19-22; Notes §2.2
- **Date**: 2026-06-10
- **Run ID**: `20260610T080902Z__t_a3b87099__one-hot-vs-dense`

## Changed Files

- `Labs/L01-word-vectors/one-hot-vs-dense.py` — 主脚本
- `Labs/L01-word-vectors/one-hot-vs-dense.ipynb` — Jupyter notebook
- `Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt` — 真实 stdout
- `Labs/L01-word-vectors/outputs/one-hot-vs-dense-stderr.txt` — stderr (empty)
- `Labs/L01-word-vectors/outputs/one-hot-vs-dense-comparison.png` — 对比图
- `Labs/L01-word-vectors/outputs/one-hot-vs-dense-results.json` — 结构化结果
- `Labs/L01-word-vectors/run-log.md` — 共享 run-log（flock 原子追加）
- `Lectures/L01-word-vectors/code-capsules/one-hot-vs-dense.md` — capsule partial
- `Lectures/L01-word-vectors/media-registry/code-capsule-one-hot-vs-dense.json` — 图片登记

## 真实输出摘要

- vocab_size = 6 (hotel, motel, book, cat, dog, fish)
- One-hot dot products: hotel·motel=0.0, cat·dog=0.0, book·fish=0.0
- Dense cosine: cos(hotel,motel)=0.9949, cos(cat,dog)=0.9430, cos(book,fish)=-0.3162
- 图表：左=one-hot 单位矩阵热图，右=2D 密集向量散点图+cosine 标注

## Colab 链接

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/one-hot-vs-dense.ipynb

## 图片上传

| 图片 | 状态 | URL |
|------|------|-----|
| one-hot-vs-dense-comparison.png | uploaded | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161145.png |

## GitHub 发布

- Repo: `dafengbaocy/cs224n-study` (public)
- Branch: `main`
- Commit: `1cbc203`
- Notebook path: `L01-word-vectors/one-hot-vs-dense.ipynb`
- 验证：raw.githubusercontent.com 返回 HTTP 200

## 自检结果

- [x] capsule partial 存在于 `Lectures/L01-word-vectors/code-capsules/one-hot-vs-dense.md`
- [x] heading 为 `## one-hot-vs-dense ... {#one-hot-vs-dense}`
- [x] .py, .ipynb, stdout, run-log, Colab 链接都存在
- [x] run-log 中有唯一 section 匹配 task_id: t_a3b87099, capsule_slug: one-hot-vs-dense
- [x] 正文中关键数值能在 stdout 中找到
- [x] glossary 链接使用 vault-root 路径
- [x] 图片使用 remote_url，不是本地路径
- [x] media-registry 已写入
- [x] 未写/改 `04-code-capsules.md`

## requested_glossary_terms

无需新增——本 capsule 使用的所有术语（one-hot-encoding, dense-vector, cosine-similarity）已在 glossary seed 中存在。

## integration_risk

无。本 capsule 是独立 partial，不影响其他 capsule。

## 终态

- ready_for_review: true
- downstream_allowed: false
