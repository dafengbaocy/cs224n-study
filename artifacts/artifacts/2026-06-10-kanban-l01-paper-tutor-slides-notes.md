## Paper Tutor — slides/notes 教学图抽取（模板，每讲一份）

**你是 CS224N paper-tutor，只负责官方 slides / notes 的教学示意图抽取**。

### 输入

- `Lectures/L01-word-vectors/02-readings-map.md`（waypoint 清单）
- `recovered/assets/official/<lecture>/slides.pdf`（slides，?p）
- `recovered/assets/official/<lecture>/notes.pdf`（notes，?p）
- `recovered/evidence/l01/slides-extracted-text.txt`
- `recovered/evidence/l01/notes-extracted-text.txt`

### 任务

1. 扫本讲 slides / notes 所有与 waypoint 相关的页面。
2. **图片处理优先级（同 paper 图）**：
   - **优先级 1**：查 CS224N 官网是否有该 slides 的在线 HTML 版或图片资源；有则直接引用，记录 provenance。
   - **优先级 2**：无则截图存 `Assets/L01-word-vectors/slides/`，文件名必须含内容语义：
     - `slides-p{page}-{content_slug}.png`，例如 `slides-p24-skipgram-window-sampling.png`
     - `notes-p{page}-{content_slug}.png`，例如 `notes-p07-negative-sampling-objective.png`
     - 禁止只用页码（`slides-p17.png`）
   - 本地截图保存后立即上传图床，并写 `Lectures/L01-word-vectors/media-registry/paper-tutor-slides-notes.json`。后续阶段用 `local_path / asset_id` 识别图片，用 `remote_url` 发布图片。
   - 上传失败不能只试一次就放弃。每张需要上传的本地图片必须最多尝试 **5 次**，必须退避等待，最少保证相邻尝试间隔 5 秒；推荐使用 `5s / 10s / 20s / 40s`；5 次后仍失败，才允许写 `upload_status: blocked`。blocked 图片必须在 registry 写 `upload_attempt_count: 5` 和 5 条 `upload_attempts` 证据，用户可读正文不能用本地路径兜底。
3. 不要用"每个主概念至少一个"作为停止标准；扫完所有 waypoint 相关 slides/notes 页面，能帮理解的就抽。
4. 输出 `Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md`，按 waypoint 组织教学图，每张标页码来源和"先看哪里"。
5. 对文字型 / 英文较多的 slide 或 notes 截图，必须做 `图片文字带读`：抽取或 OCR 关键英文，给中文翻译和学习结论。不能只贴全英文截图。
6. 输出 `partial-slides.md` bridge 片段，映射教学图 → waypoint。wikilink 用 vault-root 路径。
7. 若某 waypoint 在 slides/notes 都找不到可视化证据且无法用后续 code 输出补充，写 blocker。

### 输出

- `Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md`
- `Assets/L01-word-vectors/slides/*.png`（文件名含语义）
- `Lectures/L01-word-vectors/media-registry/paper-tutor-slides-notes.json`
- `Lectures/L01-word-vectors/03-paper-bridge.partial-slides.md`
- `artifacts/2026-06-10-paper-tutor-l01-slides-notes.md`

### 验证命令

```bash
/workspace/cs224n-study/.venv/bin/python - <<'PY'
from pathlib import Path
import fitz
required = [
    Path("recovered/assets/official/<lecture>/slides.pdf"),
    Path("recovered/assets/official/<lecture>/notes.pdf"),
]
for pdf in required:
    assert pdf.exists(), f"missing required PDF: {pdf}"
    doc = fitz.open(str(pdf))
    assert doc.page_count > 0, f"unreadable PDF: {pdf}"
    doc.close()
print("slides/notes source assets ok:", [str(p) for p in required])
PY
test -f Lectures/L01-word-vectors/03-paper-bridge.partial-slides.md
/workspace/cs224n-study/.venv/bin/python scripts/review_checks/check_links_headings.py --root . --paths Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md --forbid-local-images
/workspace/cs224n-study/.venv/bin/python scripts/review_checks/check_media_registry.py --root . --lecture L01-word-vectors --prefix paper-tutor-slides-notes --doc-path Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md --doc-path Lectures/L01-word-vectors/03-paper-bridge.partial-slides.md --asset-path Assets/L01-word-vectors/slides --asset-path Assets/L01-word-vectors/notes --require-for-assets --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5
```

结果写到：
- `artifacts/2026-06-10-review-automation-v0-l01-paper-tutor-slides-notes-source-evidence.jsonl`
- `artifacts/2026-06-10-review-automation-v0-l01-paper-tutor-slides-notes-links-headings.jsonl`

### 禁止

- 不写 `00-课堂入口.md`
- 不处理 paper 论文（那是兄弟任务范围）
- 不启动 DeepResearch
- 不在用户可读 Markdown 中使用本地图片路径；教学图正文显示必须用 `remote_url`，本地路径只放 provenance / registry。

### 完成状态

正常完成生产时必须停在 `review-required`：Kanban 状态用 `blocked`，summary / comment 第一行写 `review-required`，执行报告写 `ready_for_review: true` 与 `downstream_allowed: false`。

不允许把 worker 任务直接标成 `done` / `completed`。`done` 只能由编排器在独立 reviewer `VERDICT: PASS` 后写入。

**终态执行命令（硬规则）**：产物写完、验证命令跑完、执行报告写完后，你必须先确认当前 Kanban task id，然后执行：

```bash
hermes kanban --board cs224n-study block <当前task_id> "review-required: ready_for_review=true downstream_allowed=false; outputs=<主要产物路径>"
```

命令成功后才可以结束回复。禁止用 `complete` / `done` / `completed` 结束 worker 任务；如果无法确认当前 task id，就在最终回复中明确 `protocol_blocker: cannot_determine_task_id`，不要自称完成。

只有遇到真实外部 blocker、越界风险、官方 PDF/evidence 无法读取或工具链无法产生可验证产物时，才使用 `blocked` / `quarantined`。不允许自称 pass，不允许 `downstream_allowed: true`。

---

## 使用说明（给 launcher / 人工）

1. **paper 任务**：launcher 读 readings-map 的 `core_readings`，每篇 core reading 复制"单篇论文精读"模板，替换占位符（`{reading_id}`、`{paper_title}`、`{local_pdf}` 等）。
2. **slides/notes 任务**：每讲固定一个，复制"slides/notes 教学图抽取"模板，替换讲次占位符 + slides/notes PDF 路径和页数。
3. `{reading_short_lower}` 是 `{reading_short}` 的小写（R01 → r01），用于文件名。
4. 任务卡只含模板正文，不引用 `AGENTS.md` / flow docs —— 规则已内联。
5. worker 只读少量数据文件（`02-readings-map.md`、PDF、extracted-text），context 压力减半。
