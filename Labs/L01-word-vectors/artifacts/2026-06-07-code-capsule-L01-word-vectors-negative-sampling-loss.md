# Code Capsule 执行报告: negative-sampling-loss (WP05)

- task_id: t_87d53a54
- parent: t_2daaf65b
- capsule_slug: negative-sampling-loss
- concept: 负采样目标函数 vs 全 softmax
- waypoint: WP05
- official_anchor: Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3
- timestamp: 2026-06-10T09:45:08Z
- ready_for_review: true
- downstream_allowed: false

## 产物清单

| 产物 | 路径 | 状态 |
|------|------|------|
| Python 脚本 | `Labs/L01-word-vectors/negative-sampling-loss.py` | ✅ |
| Jupyter Notebook | `Labs/L01-word-vectors/negative-sampling-loss.ipynb` | ✅ |
| 图表 | `Labs/L01-word-vectors/outputs/negative-sampling-loss-gradient-and-comparison.png` | ✅ |
| stdout | `Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt` | ✅ |
| stderr | `Labs/L01-word-vectors/outputs/negative-sampling-loss-stderr.txt` | ✅ |
| summary JSON | `Labs/L01-word-vectors/outputs/negative-sampling-loss-summary.json` | ✅ |
| run-log | `Labs/L01-word-vectors/run-log.md` | ✅ (run_id: 20260610T094508Z__t_87d53a54__negative-sampling-loss) |
| capsule partial | `Lectures/L01-word-vectors/code-capsules/negative-sampling-loss.md` | ✅ |
| media registry | `Lectures/L01-word-vectors/media-registry/code-capsule-negative-sampling-loss.json` | ✅ |
| 执行报告 | `artifacts/2026-06-07-code-capsule-L01-word-vectors-negative-sampling-loss.md` | ✅ (本文件) |

## Colab 链接

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/negative-sampling-loss.ipynb

## 图片上传

| 图片 | remote_url | upload_status |
|------|-----------|---------------|
| negative-sampling-loss-gradient-and-comparison.png | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174103.png | uploaded (1 attempt) |

## 真实输出摘要

- 全 softmax 损失 J_full = 2.7730（随机初始化下 P('dog'|'cat') = 0.062471）
- SGNS 损失 J_sgns = 4.0589（k=5 个负样本：house, woman, fish, swim, man）
- 正样本 sigma(u_o^T v_c) = 0.5474
- 计算量对比：|V|=100,000 时 SGNS 加速 ~20,000x
- 梯度方向：正样本拉近 v_c → u_o，负样本推离 v_c ← u_w

## Notebook 中文教学检查

- [x] 所有 Markdown cell 使用中文解释
- [x] 包含"这段代码在看什么"小节
- [x] 包含"运行后先看哪里"小节
- [x] 包含"输出怎么解释"小节
- [x] 包含"和本讲哪个 waypoint 对应"小节
- [x] 包含"容易误解的地方"小节
- [x] 图表旁有中文读图说明
- [x] 代码注释中文优先

## Glossary 链接检查

使用的 glossary heading（均在 `00-concept-glossary.md` 中存在）：
- `[[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]]` ✅
- `[[Lectures/L01-word-vectors/00-concept-glossary#negative-sampling|负采样]]` ✅

requested_glossary_terms: 无（所有需要的术语都已在 seed 中）

## integration_risk

- 另一个 worker (t_45780d20) 之前已推送过一版 negative-sampling-loss capsule。我的版本覆盖了它的文件（`Labs/L01-word-vectors/negative-sampling-loss.py` 等）。如果 integration 阶段需要合并两个版本，需要注意冲突。
- repo 结构存在嵌套目录问题（`Labs/L01-word-vectors/Labs/L01-word-vectors/`），这是之前 worker 的嵌套 git repo 导致的。我的文件在正确路径。

## 自检结果

- [x] capsule partial 存在于 `Lectures/L01-word-vectors/code-capsules/negative-sampling-loss.md`
- [x] heading 为 `## negative-sampling-loss ... {#negative-sampling-loss}`
- [x] .py、.ipynb、stdout/output、run-log、Colab 链接和正文路径都存在
- [x] run-log 中有唯一匹配当前任务的 section（task_id: t_87d53a54, capsule_slug: negative-sampling-loss）
- [x] 正文中的关键数值能在 stdout/output/run-log 中找到
- [x] 没有写 `04-code-capsules.md`
- [x] 没有用短 wikilink 跨目录引用 glossary
- [x] 图片使用 remote_url，不是本地路径
- [x] glossary heading 验证通过：`## softmax` 和 `## negative-sampling` 均存在于 `00-concept-glossary.md`

## 未完成项

- [ ] Obsidian/LiveSync vault write：SSH 到飞牛不可用（Connection closed），CouchDB 在本容器不可达。文件已在本地 workspace 和 GitHub 上，待网络恢复后补写。
