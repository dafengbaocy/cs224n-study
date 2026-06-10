# Code Capsule 执行报告：one-hot-vs-dense (WP02)

- task_id: t_2397e6e3
- parent: t_2daaf65b
- capsule_slug: one-hot-vs-dense
- concept: One-hot 向量 vs 密集词向量的对比
- waypoint: WP02 — One-hot vs Dense Vectors
- official_anchor: Slides p19-22; Notes §2.2 Eq.1-2
- run_id: 20260610T094123Z__t_2397e6e3__one-hot-vs-dense
- ready_for_review: true
- downstream_allowed: false

## 产物清单

| 产物 | 路径 | 状态 |
|------|------|------|
| Python 脚本 | `Labs/L01-word-vectors/one-hot-vs-dense.py` | ✅ |
| Jupyter Notebook | `Labs/L01-word-vectors/one-hot-vs-dense.ipynb` | ✅ (中文教学版) |
| stdout | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt` | ✅ |
| stderr | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-stderr.txt` | ✅ (empty) |
| JSON 数据 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-comparison.json` | ✅ |
| 热力图 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-heatmap.png` | ✅ |
| 柱状图 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-bar-comparison.png` | ✅ |
| Run-log | `Labs/L01-word-vectors/run-log.md` | ✅ (flock 原子追加) |
| Capsule partial | `Lectures/L01-word-vectors/code-capsules/one-hot-vs-dense.md` | ✅ |
| Media registry | `Lectures/L01-word-vectors/media-registry/code-capsule-one-hot-vs-dense.json` | ✅ |
| Colab 链接 | https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/Labs/L01-word-vectors/one-hot-vs-dense.ipynb | ✅ |

## 图片上传

| 图片 | 本地路径 | Remote URL | 上传次数 |
|------|----------|------------|----------|
| 热力图 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-heatmap.png` | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174129.png | 1 |
| 柱状图 | `Labs/L01-word-vectors/outputs/one-hot-vs-dense-bar-comparison.png` | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174141.png | 1 |

## 真实输出摘要

- 词表：6 词（hotel, motel, bank, atm, apple, tea），分 3 组
- One-hot 点积矩阵：所有非对角线 = 0.0（正交）
- Dense 余弦相似度矩阵：同组 ≈ 0.998，跨组 ≈ 0.05-0.12
- 同组平均 cos_sim = 0.9979
- 跨组平均 cos_sim = 0.0899
- 差值 = 0.9079
- exit_code: 0，无错误

## Notebook 中文教学规则自检

- [x] 所有 Markdown cell 使用中文解释
- [x] 英文术语紧跟中文解释（如 `softmax（把分数归一化成概率）`）
- [x] 包含中文小节：这段代码在看什么、运行后先看哪里、输出怎么解释、和本讲哪个 waypoint 对应、容易误解的地方
- [x] 输出图旁有中文读图说明
- [x] 不是 .py 的机械转换——Markdown cell 有独立教学叙事

## Wikilink 自检

- [x] `[[Lectures/L01-word-vectors/00-concept-glossary#one-hot-encoding|one-hot encoding]]` → glossary line 71 ✓
- [x] `[[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]]` → glossary line 37 ✓
- [x] `[[Lectures/L01-word-vectors/00-concept-glossary#dot-product|点积]]` → glossary line 43 ✓
- [x] `[[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|余弦相似度]]` → glossary line 29 ✓
- [x] 所有链接使用 vault-root 路径，无 `../` 相对路径

## 数字来源证明

所有正文中的数值（0.998, 0.053, 0.9979, 0.0899, 0.9079 等）均来自 `outputs/one-hot-vs-dense-stdout.txt` 的真实输出。

## 未触碰的文件

- 未写/改 `04-code-capsules.md`（由 merge 阶段处理）
- 未改其他 capsule partial
- 未改 `00-concept-glossary.md`

## Integration Risk

无。

## Requested Glossary Terms

无（所有需要的术语在 glossary seed 中已存在）。

## GitHub Push 备注

study-ops `github-push --path` 参数需要传 git repo 根目录（`.`），不能传子目录（`Labs/L01-word-vectors`），否则会在子目录初始化新 git repo。
