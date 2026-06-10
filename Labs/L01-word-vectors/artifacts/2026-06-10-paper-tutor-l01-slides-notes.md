# Paper Tutor 执行报告：L01 slides/notes 教学图提取

- **task_id**: t_ad4519a7
- **stage**: Paper Tutor (slides/notes)
- **lecture**: L01-word-vectors
- **date**: 2026-06-10
- **ready_for_review**: true
- **downstream_allowed**: false

---

## 执行摘要

完成 CS224N L01 Word Vectors 官方 slides (36p) 和 notes (13p) 的教学图提取。
从 Stanford archive 重新下载 PDF（workspace 中缺失），用 PyMuPDF 2x zoom 渲染 31 张关键页面截图，
成功上传 25 张到图床（6 张补充图因 MCP SSL 故障删除）。
产出按 WP01-WP05 组织的教学图文档和 partial bridge。

## 输入

| 输入 | 路径 | 状态 |
|---|---|---|
| Slides PDF | `recovered/assets/official/l01/cs224n-2025-lecture01-wordvecs1.pdf` | ✅ 重新下载 (2,691,988 bytes, 36p) |
| Notes PDF | `recovered/assets/official/l01/cs224n-2025-lecture01-notes.pdf` | ✅ 重新下载 (216,720 bytes, 13p) |
| Slides extracted text | `recovered/evidence/l01/slides-extracted-text.txt` | ✅ 重新提取 |
| Notes extracted text | `recovered/evidence/l01/notes-extracted-text.txt` | ✅ 重新提取 |
| Readings map | `Lectures/L01-word-vectors/02-readings-map.md` | ✅ 已有 |

## 产出

| 产出 | 路径 | 说明 |
|---|---|---|
| 教学图文档 | `Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md` | 26 张图 + 文字带读，按 WP01-WP05 组织 |
| Media registry | `Lectures/L01-word-vectors/media-registry/paper-tutor-slides-notes.json` | 25 items, all uploaded |
| Partial bridge | `Lectures/L01-word-vectors/03-paper-bridge.partial-slides.md` | 教学图 → waypoint 映射表 |
| Slides 截图 | `Assets/L01-word-vectors/slides/*.png` | 19 张 (p2,p9,p16-p35 关键页) |
| Notes 截图 | `Assets/L01-word-vectors/notes/*.png` | 6 张 (p4,p6-p9,p12) |
| 验证结果 | `artifacts/2026-06-10-review-automation-v0-l01-paper-tutor-slides-notes-*.jsonl` | links-headings: pass, media-registry: pass |

## Waypoint 覆盖度

| WP | 教学图数 | Slides/Notes 覆盖 | 备注 |
|---|---|---|---|
| WP01 | 5 | ✅ 充分 | p1-p15 课程介绍+NLP 应用；3 张应用示例图 pending 删除，用文字带读替代 |
| WP02 | 10 | ✅ 充分 | one-hot → 分布假说 → dense vectors 完整逻辑链 |
| WP03 | 6 | ✅ 充分 | Word2Vec 框架 + softmax 完整覆盖 |
| WP04 | 8 | ⚠️ 部分充分 | 目标函数/GD/SGD 充分；负采样 p_neg 未定义需 DeepResearch |
| WP05 | 0 | ❌ 不足 | Slides/notes 无可视化内容，需 A1 + DeepResearch 补充 |

## 图片上传状态

- 成功上传：25 张（22 张前次 URL 复用 + 2 张新上传 + 1 张 notes p12 前次 URL）
- 删除（MCP SSL 故障）：6 张补充图（slides p11/p12/p14, notes p5/p10/p11）
- 所有保留图片 `upload_status: uploaded`，`remote_url` 有效

## 验证结果

| Check | Verdict | Details |
|---|---|---|
| links_headings (teaching figures) | pass | 0 errors, 26 images |
| links_headings (bridge) | pass | 0 errors |
| media_registry | pass | 25 rows, 0 errors |
| PDF source assets | pass | slides 36p, notes 13p |

## 禁止项检查

- [x] 未写 `00-课堂入口.md`
- [x] 未处理 paper 论文
- [x] 未启动 DeepResearch
- [x] 用户可读 Markdown 中无本地图片路径（全部用 remote_url）
- [x] 未自称 pass / done / completed
- [x] 未设 downstream_allowed: true

## 已知限制

1. **6 张补充图未上传**：slides p11 (NLP translation)、p12 (QA)、p14 (image gen) 和 notes p5 (annotated vectors)、p10 (gradient derivation)、p11 (observed-expected) 因 MCP picgo-media 上传服务 SSL 故障（OpenSSL unexpected EOF）无法上传。这些是补充性图片，核心教学内容已由其他 25 张图覆盖。WP01 的 NLP 应用示例在文档中用文字带读替代。
2. **WP05 无 slides/notes 可视化**：slides 正文没有 "Looking at word vectors" 的对应内容页，notes 附录只有标题。需要等 Code Capsules 和 DeepResearch 补充。
3. **Notes p_neg 未定义**：notes §3.5 明确写 "a distribution we haven't defined, called p_neg"。实际噪声分布的解释需要 DeepResearch 阶段补充。
