# Execution Report: one-hot-vs-dense Code Capsule (WP01)

**Task ID**: t_a1b9e9f6
**Capsule**: one-hot-vs-dense
**Waypoint**: WP01 — 为什么需要词向量？
**Concept**: One-hot 向量 vs 密集词向量的对比
**Status**: review-required
**ready_for_review**: true
**downstream_allowed**: false

---

## 产物清单

| 产物 | 路径 | 状态 |
|------|------|------|
| Python 脚本 | `Labs/L01-word-vectors/one-hot-vs-dense.py` | ✅ |
| Jupyter Notebook | `Labs/L01-word-vectors/one-hot-vs-dense.ipynb` | ✅ |
| stdout | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt` | ✅ |
| stderr | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-stderr.txt` | ✅ (empty) |
| 对比图 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-comparison.png` | ✅ |
| JSON 输出 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-output.json` | ✅ |
| Run-log | `Labs/L01-word-vectors/run-log.md` | ✅ |
| Capsule partial | `Lectures/L01-word-vectors/code-capsules/one-hot-vs-dense.md` | ✅ |
| Media registry | `Lectures/L01-word-vectors/media-registry/code-capsule-one-hot-vs-dense.json` | ✅ |
| Glossary (restored) | `Lectures/L01-word-vectors/00-concept-glossary.md` | ✅ |

## 运行信息

- **Run ID**: `20260610T102535Z__t_a1b9e9f6__one-hot-vs-dense`
- **Hostname**: 0d61b5cf12fa
- **Command**: `.venv/bin/python Labs/L01-word-vectors/one-hot-vs-dense.py`
- **Exit code**: 0
- **stderr**: empty (no errors)
- **依赖**: stdlib + numpy + matplotlib (venv 和 Colab 均预装)

## Colab 链接

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/one-hot-vs-dense.ipynb

## 图片上传

| 图片 | 本地路径 | Remote URL | 上传状态 |
|------|----------|------------|----------|
| 对比图 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-comparison.png` | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181637.png | uploaded (1 attempt, MCP) |

## 关键数值（来自真实 stdout）

| 词对 | 关系 | One-hot 点积 | Dense cos_sim |
|------|------|-------------|---------------|
| hotel-motel | 近义词 | 0.0 | 0.9949 |
| cat-dog | 同类动物 | 0.0 | 0.9430 |
| book-fish | 无关 | 0.0 | -0.3162 |

## 自检结果

- ✅ Capsule partial 存在于 `Lectures/L01-word-vectors/code-capsules/one-hot-vs-dense.md`
- ✅ Heading: `## one-hot-vs-dense — One-hot 向量 vs Dense 向量 {#one-hot-vs-dense}`
- ✅ .py, .ipynb, stdout, run-log, Colab 链接均存在
- ✅ Run-log 有唯一 section 匹配 task_id: t_a1b9e9f6
- ✅ 正文关键数值可在 stdout 中找到
- ✅ `check_links_headings.py` 返回 0 errors (verdict: pass)
- ✅ Notebook 中文教学规则：所有 Markdown cell 使用中文，包含必需章节
- ✅ Glossary 链接使用 vault-root 路径

## 注意事项

- 之前的 run (t_ec7c208c) 的产物在 git rebase 中被覆盖/丢失，本次为全新 re-run
- 恢复了被 rebase 删除的 `00-concept-glossary.md`
- 清理了 `Labs/L01-word-vectors/` 下的嵌入式 git repository（.git 目录）

## integration_risk

无。本 capsule 只修改自己允许的文件。

## requested_glossary_terms

无。所有需要的 glossary heading 均已存在：`one-hot-encoding`, `dense-vector`, `cosine-similarity`, `dot-product`。
