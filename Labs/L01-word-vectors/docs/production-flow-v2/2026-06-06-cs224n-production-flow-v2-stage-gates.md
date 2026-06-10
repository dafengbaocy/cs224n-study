# CS224N 生产流程 v2：阶段闸门与失败恢复

日期：2026-06-06
状态：待用户评审草案

本文档把每个阶段的输入、输出、验收和失败恢复写清楚，避免 agent 靠“看起来完成了”过关。

## 1. 通用任务模板

每张 Kanban 任务卡必须包含：

- 对应 stage 名称。
- 上游依赖。
- 输入文件。
- 输出文件。
- 禁止事项。
- 验收命令。
- 失败时怎么 block。
- 是否允许写 Obsidian。
- 是否允许启动下游。

## 2. 通用完成状态

允许的状态：

- `done`：只用于非 agent 元数据操作，或 Codex Review Gate 之后的关闭动作。
- `review-required`：Hermes 生产任务的默认终态。
- `blocked`：缺工具、缺源、缺权限、用户要求暂停、流程不明确。
- `quarantined`：产物已经出现，但不符合流程或未被信任。

不允许：

- Hermes 自己说 `pass` 就放行。
- Codex 在没读回文件时放行。
- 用户已经质疑流程后继续开新生产卡。

## 3. Source Gate

检查：

- 官方 URL 是否真实可访问。
- PDF/zip 是否有 checksum。
- 提取工具是否记录。
- Stanford 网络问题是否复发。

失败恢复：

- 网络问题先排查代理/直连规则。
- PDF 提取失败可换 PyMuPDF / pdftotext / browser render。
- 仍失败则 block，不进入 reading triage。

## 4. Reading Gate

检查：

- 每篇 reading 是否有 canonical URL。
- 是否漏 slides references。
- core/support/optional 是否有理由。

失败恢复：

- canonical 不确定：标 `needs_human_check`。
- S4 资料 curl 失败：必须尝试 browser render 或写清 blocker。

## 5. Paper Gate

检查：

- 是否按 section / figure / equation 拆解。
- 是否回扣 lecture waypoint。
- 图表覆盖率，而不是“至少处理一个”：`03-paper-bridge.md` / `02-readings-map.md` 中每个 waypoint 引用的 figure/table/equation 是否都有对应的 `Assets/{lecture}/papers/*.png` 或 paper note 小节。出现“有 waypoint 引用但无对应图”即为覆盖不足。
- 必抽类是否齐全：证明方法有效的实验性能表、帮助理解调参的参数/消融表、论文 main result 可视化（PCA/t-SNE/几何图）三类，是否各自已抽取或写明“本篇无此类”。只抽了核心架构图就停 → `needs_revision`。
- 是否把非官方解释当成主线。
- `03-paper-bridge.md` 推荐给主入口使用的 wikilink 是否是 Obsidian vault-root 路径，并且定位到 heading / block id。
- 是否出现 `../`、`../../` 这类只适合文件系统、不适合正式 Obsidian 发布的跨文件相对 wikilink。

失败恢复：

- 图表抽取失败：记录 blocker 和替代文本解释。
- 公式看不清：保留原始截图/页码，等待人工或重跑。
- 相对 wikilink 但目标明确：Codex 可做确定性修正，状态记为 `pass_with_corrections`，并把规则补回对应子文档或 prompt。
- 链接目标不明确或 heading 不存在：回炉给 Paper Tutor，不允许下游使用。

## 5.5 DeepResearch Gate

DeepResearch Gate 是 `4B Course DeepResearch` 阶段的专用闸门。Source Expansion 可以提供候选源和 evidence notes，但不能替代正式 Course DeepResearch。DeepResearch Gate 必须按独立合约执行：

- `/Users/chen/Documents/飞牛/cs224n-study/docs/production-flow-v2/2026-06-06-cs224n-production-flow-v2-deepresearch.md`
- `/Users/chen/Documents/飞牛/cs224n-study/docs/production-flow-v2/course_deepresearch_eval_template.json`

检查：

- 是否先创建课程版 DeepResearch Eval。
- Eval 是否包含 0-9 全部节点：Course Anchor、Official Material Readback、Source Pool、Source Triage、Source Expansion、Media Evidence、Research Draft、Course Alignment、Publish Handoff、Review & Archive。旧模板里该节点可能仍叫 `Obsidian Write`，但当前语义是发布交接，不是默认即时写入 vault。
- 是否有明确 official anchor，且官方材料已读回。
- 每个外部源是否有 tier、用途、可访问性、triage reason。
- 是否进入原文/教程/issue/中文资料正文，而不是只看搜索结果或二手摘要。
- 是否区分了 Source Triage 和 Source Expansion：只写候选表、HTTP 状态、标题、目录、简短 teaching move，不等于完成 expansion。
- 每个 accepted source 是否有 waypoint evidence note，说明 source evidence、official anchor、fusion target、teaching move 和 risk boundary。
- 用户或任务点名的 S4 中文扶手源，例如 ShowMeAI / 飞书 wiki，是否完成正文抽取并消化；如果只停在 `helper_pending_render`，是否明确 block 或 scope out。
- 是否有可见 media evidence，或有合理 scope-out / 辅助示意图计划。
- 是否有 bridge map，说明内容回嵌到哪个 waypoint / paper section / code capsule / assignment。
- 是否评估 context budget 风险：复杂讲次是否分段执行；单阶段产物是否通过后期 waypoint 密度检查。
- 是否写清发布交接状态。DeepResearch worker 默认不直接写入 Obsidian/LiveSync；应记录 `publish_deferred_to_weaver_or_publisher`，由 Lecture Weaver / Study Publisher 在 `publish-manifest.json` 阶段统一写回并 `vault read` 验证。只有任务卡显式 `publish_now: true` 时，本 Gate 才要求 DeepResearch worker 自己完成 `vault-write-hermes-container` + `vault read`。
- Codex 是否只做评审和回炉，不手改正文冒充 pass。
- 判断性放行是否来自独立评审 agent，而不是生成者自评；评审必须按 §10.5 的 `judgment-grounded` / `judgment` verdict 体系记录。
- 用户是否有覆盖失败反馈。

失败恢复：

- official anchor 不清：回到 Course Harvest / Reading Triage，不能继续 source expansion。
- 外部源不可访问：记录 blocker，降级 optional 或 reject。
- only-triage：如果只有 source pool / source triage，没有正文证据和 waypoint evidence notes，直接判 `needs_revision`；不能交给 lecture-weaver / publisher。
- 指定中文扶手 pending：如果 ShowMeAI / 飞书 wiki 等指定 S4 源只停在 `helper_pending_render` 且本讲仍需要中文扶手，判 `needs_revision` 或 `blocked`，不能把 pending 当作已吸收素材。
- 中文资料喧宾夺主：改为 `chinese_bridge`，只允许消化后进入 waypoint。
- 没有 media evidence：回到 Paper Tutor / Visual rules / Code Capsule Runner，或写明为什么本轮 scope-out。
- 没有 bridge map：不能交给 lecture-weaver / publisher。
- 出现 `needs_revision_context_pressure`：后期 waypoint 明显比前期稀薄，必须人工检查后期 waypoint；如果确认为 context 压力收尾，则按 §5.5.1 分段重跑，不允许直接交给 lecture-weaver。
- 未通过 Review：标记 `quarantined` 或 `rerun_required`，不能下游使用。
- 回炉后一致性检查：如果新证据已经推翻旧 blocker / 旧 pending 状态 / 旧不可用判断，必须删除或改写旧结论。不得让同一文件或 Eval 同时出现“已取得正文证据”和“未作为正文证据使用”这类矛盾状态。

### 5.5.1 Context Budget 与分段执行

DeepResearch 不能假设单个 agent 一定能在一个上下文里读完所有证据、写完所有 waypoint、再认真补 Eval。复杂讲次必须主动分段，避免后期 waypoint 因 context 压力被草草收尾。

必须分段的触发条件：

- core papers `>= 4` 篇。
- waypoint `>= 8` 个。
- 官方 PDF/notes/slides/handout 合计 `>= 50` 页。
- accepted helper sources `>= 5` 个，且每个都需要正文证据或 waypoint evidence note。
- 生成过程中出现上下文压缩、摘要接力、或 agent 明确报告 context/budget 压力。

推荐分段：

```text
Phase 1: Evidence Gathering + 前 2/3 waypoints
  - 读官方材料、core papers、helper source 证据。
  - 写前 2/3 waypoint 和 evidence index。
  - 输出 deepresearch-phase1.md，并更新 Eval nodes 0-6。

Phase 2: 后 1/3 waypoints + bridge map + Eval 完成
  - 读回 phase1 精炼产物和后期 waypoint 所需证据。
  - 写后期 waypoint、course alignment bridge map、media/publish handoff/review nodes。
  - 合并最终 DeepResearch。
```

如果单阶段执行没有触发上面的必须分段条件，也必须在 DeepResearch Gate 运行密度检查。检查器优先识别 `### 4.x` 机制段；如果讲次自然采用其他结构，则识别 `## 机制层解释` 下的三级标题；如果仍识别不到任何段落，必须判 `needs_revision`，不能把 `waypoints=0` 当作通过：

```bash
/workspace/cs224n-study/.venv/bin/python scripts/review_checks/check_deepresearch_density.py DeepResearch/Lxx-topic/<file>.md
```

检查原则：

- 后期 waypoint 的密度不得明显低于前期。默认阈值是 late/early density ratio `>= 0.70`。
- 密度只是警报，不是唯一判断。某些后期 waypoint 天然偏应用/bridge，公式少是合理的；但如果字数、证据锚点、例子、公式解释都一起塌陷，必须回炉。
- 检查结果必须归档到 JSONL，并写入 Eval 的 deterministic verdicts 或 review artifact。

如果密度检查失败：

- 不能只让同一个生成者补一句“我检查过了”。
- Codex / 独立 review agent 必须读后期 waypoint 和对应证据，判断是否真是 context-pressure tail collapse。
- 确认为真问题时，标 `needs_revision_context_pressure`，按 Phase 1 / Phase 2 分段重跑或开 targeted supplement；不能直接放行下游。

试运行警示：

- `t_b67c68e2` 表面上有 Eval、source pool、bridge map 和 deterministic verdict，但 ShowMeAI 未抽正文、accepted source 只有 triage 级 teaching move，最终被 Codex Review Gate 判为 `needs_revision`。
- 后续评审遇到同类情况，不允许因“结构齐全”或“deterministic pass”而放行；deterministic pass 只说明文件/链接存在，不能证明 DeepResearch 内容充分。
- `t_11cca9b6` 修复了 ShowMeAI API 正文证据和 waypoint evidence notes，但第一次回炉后仍残留旧的 pending/render-blocker 文案，导致 Codex 判 `needs_revision_minor`。后续回炉评审必须增加 stale-conclusion cleanup：用 grep 或等价检查确认旧 blocker、旧 verdict、旧状态词不会继续污染下游。
- `t_d11a3470` 是小规模 L01 单阶段 DeepResearch；事后密度检查显示 WP05 没有明显变薄，因此不作为回炉依据。但这只是 L01 没暴露问题，不代表后续复杂讲次可以跳过 context budget 检查。

## 6. Lecture Gate

检查：

- 是否是学习脚本，不是目录。
- 是否按 waypoint 编排。
- 是否引用 paper-tutor 和 source-expansion 产物。
- 是否使用文件 + heading / block id 的精确跳转，而不是只链接到 md 文件。
- 是否有 Obsidian 视觉层级。
- 是否有图/公式/code slot/assignment bridge 的合理安排。
- 最终课件中的图片是否全部使用图床/远程 URL；不得使用 `/workspace/...`、`/vol2/...`、`Assets/...png` 或 `![[Assets/...png]]` 这类本地图片引用。

失败恢复：

- source mapping 错：回炉修正。
- 视觉层级差：只修格式，不重写内容。
- 图片使用本地路径：优先由 Codex 做确定性修正，上传图床、替换正文 URL、记录 provenance，并把规则补回任务规格/visuals/obsidian-style；如果无法上传则 block。
- 结构偏离：block，回到文档确认。

## 7. Code Gate

检查：

- 是否真实运行。
- 是否有输出。
- 是否有 Colab 或替代方案。
- 是否有 run-log。

失败恢复：

- 本地环境失败：记录错误，尝试 Colab。
- Colab 发布失败：保留 notebook 和本地输出，publisher 后补链接。

## 7.5 Assignment Prerequisite Scan

Assignment Runner 开始前，必须先扫描官方 assignment handout / notebook / starter code，列出每个题目依赖的概念、公式和 API。这个扫描不是正式作业解答，也不能直接给答案；它只判断“前面的课堂脚手架是否足够支撑用户开始做题”。

输出：

- `Assignments/Ax/prerequisite-scan.md`

扫描表至少包含：

| A1 Part / Question | prerequisite | covered_in | status |
| --- | --- | --- | --- |
| Part 1 Q1 co-occurrence matrix | co-occurrence 定义、window 统计 | DeepResearch / Lecture Weaver / Code Capsule 的具体 heading 或 `not_covered` | `covered` / `partial` / `gap` |
| Part 1 Q2 SVD reduction | SVD 降维、奇异值、几何直觉 | DeepResearch / Lecture Weaver / Code Capsule 的具体 heading 或 `not_covered` | `covered` / `partial` / `gap` |
| Part 2 pretrained vectors | GloVe、cosine similarity、Gensim / torch API | DeepResearch / Lecture Weaver / Code Capsule 的具体 heading 或 `not_covered` | `covered` / `partial` / `gap` |

检查：

- 每个 assignment part / question 是否有明确 prerequisite。
- 每个 prerequisite 是否能定位到已通过 Review Gate 的 DeepResearch / Lecture Weaver / Code Capsule 产物。
- `covered_in` 不能只写“讲过”，必须写具体文件 + heading / block id，或明确 `not_covered`。
- `partial` 必须说明缺的是概念解释、公式推导、代码 API、还是 debugging note。

失败恢复：

- 如果存在 `gap` 且属于核心前置知识，不能直接启动 Assignment Runner。
- 对范围内小缺口，走 §11 Supplement Request：回 DeepResearch / Lecture Weaver / Code Capsule 补一个小节或注释。
- 如果缺口超出 L01 官方范围，例如用户要求加入额外主题，必须 block 并请求用户决策。
- 如果决定 scope-out 某个 assignment part，必须在 README 和 prerequisite scan 中写清楚原因，不能默默跳过。

## 8. Assignment Gate

检查：

- 是否用官方 handout/starter code。
- 是否 run-log 真实。
- 是否 attempt-and-hints 三段式。
- 是否避免直接给最终答案。

失败恢复：

- 作业运行失败：记录错误和最小复现。
- 长训练超时：缓存策略和后续刷新规则必须写清。

## 9. Publisher Gate

检查：

- 是否只使用通过 review 的上游产物。
- 是否破坏主入口节奏。
- 是否链接可点，并且关键链接定位到具体 heading / block id。
- 是否 Obsidian `vault read` 可验证。

失败恢复：

- 回嵌太乱：回退为 bridge note，不进主入口。
- 链接不可用：block，不发布。

## 10. Completion Gate

整讲完成必须检查：

- 官方资料完成。
- readings 完成。
- paper notes 完成。
- source expansion 完成或明确 scope out。
- course deepresearch 完成或明确 scope out。
- 主入口完成。
- code capsules 完成。
- assignment prerequisite scan 完成。
- assignment runner 完成或明确 scope out。
- publisher 完成。
- 用户反馈没有 unresolved blocker。

任何一项未通过，都不能标 lecture complete。

## 10.5 Review Gate 自动化演进路线

Review Gate 的终态是尽量自动化；当前 Codex 人工/半人工 Review 是信任校准期，不是长期终态。自动化演进必须避免“生成者自己验收自己”的失败模式。

### 10.5.1 检查项分类

每个 Gate 的检查项必须先分类，再决定自动化方式：

| type | 含义 | 默认执行者 | 例子 |
| --- | --- | --- | --- |
| `deterministic` | 代码能直接验证，不需要 LLM 判断 | 脚本 / asset check | URL 状态、checksum、PDF 页数、文件存在、wikilink heading 解析、图片路径、frontmatter 字段、run-log schema |
| `judgment-grounded` | 需要判断，但必须回扣明确证据锚点 | 独立对抗式评审 agent | 是否乱编、是否误读 paper、是否把非官方资料当主线、是否和 slides/notes/paper 原文冲突 |
| `judgment` | 主要是教学体验判断，证据锚点不完全充分 | 独立对抗式评审 agent + 人工抽查 | 中文扶手是否不跳步、主次是否清楚、主入口节奏是否顺 |
| `human_escalation` | 自动评审分歧、低置信、或用户覆盖失败 | 用户 / Codex 人工闸门 | 用户说看不懂、不信任、内容像拼贴；多个评审 agent 结论冲突 |

优先级：能做 `deterministic` 的不交给 LLM；能做 `judgment-grounded` 的不降级成纯 `judgment`。

### 10.5.2 确定性检查优先自动化

`deterministic` 项一律优先做成脚本或 asset check，不靠 agent 自报。

通用要求：

- 确定性检查结果必须由脚本 / harness 亲自执行并抓取 stdout、退出码和 JSONL verdict；不能让 agent 转述“我运行过了”。
- 在 Hermes 容器内运行 CS224N 检查脚本时，优先使用 `/workspace/cs224n-study/.venv/bin/python`。该 venv 已安装 PyMuPDF，可用于 PDF 页数/可读性验证；系统 `python3` 可能没有 `fitz`，只能触发 PDF header/page-marker fallback。
- 脚本 fallback 可以保留，但不能把“fallback 通过”写成“PyMuPDF 已验证”。

第一批最高价值脚本只允许做 3-4 个，不搭框架、不阻塞 L01 内容产出：

- `check_links_headings.py`：验证所有 `[[path#heading|alias]]` / block id / 图片路径可解析，跨文件链接必须是 Obsidian vault-root 路径。
- `check_source_evidence.py`：验证 source lock、canonical URL、HTTP 状态、PDF/zip 文件大小、sha256、PDF 页数和提取证据。
- `check_run_log.py`：验证 code capsule / assignment run-log 由受信执行器产生，包含命令、退出码、stdout/stderr、输出文件和时间戳。
- `check_vault_publish.py`：验证需要发布的文件已经写入 Obsidian/LiveSync，并能被 `vault read` 读回。

Review Automation v0 的范围封顶为：文档分类 + 上面 3-4 个小脚本。v0 不引入 Dagster，不改 Kanban 架构，不把 L01 内容生产停下来等平台化完成。

### 10.5.3 Code Gate 自动化前提

Code Gate 只有在 run-log 由受信执行器亲自执行并抓取时，才允许自动化。

允许的受信执行器：

- `nbclient`
- `papermill`
- `jupyter nbconvert --execute`
- 后续明确批准的等价 notebook executor

禁止：

- agent 在 Markdown 里自报 stdout 后让 Review Gate 直接相信。
- 只写 `.py` 调用、不执行、不记录退出码。
- 由生成代码的同一 agent 口头声明“运行通过”。

如果 run-log 不是受信执行器产生，Code Gate 最多进入 `judgment` / `human_escalation`，不得转为全自动 pass。

### 10.5.4 评审独立性

自动评审 agent 必须独立于生成者：

- 评审模型不得等于该任务的生成模型，例如 qwen 生成时，评审应使用 codex / deepseek 等不同模型；codex 生成时，评审应使用 qwen / deepseek / Claude 等不同模型。
- 评审 agent 不得读取生成者草稿、隐藏思维链、内部自检文字或“我为什么这么写”的解释，只能读取任务规格、输入证据、输出文件、run-log、source evidence 和公开 review rubric。
- 评审 prompt 的目标是挑刺、反驳和找证据缺口，不是确认生成者说法。
- 每条 `judgment-grounded` 放行结论都必须引用证据锚点，例如原文行号、PDF 页码、slides 页码、notes section、截图路径、run-log 记录。

投票 / 仲裁规则：

- `judgment-grounded` 和 `judgment` 项在影子模式或自动化候选阶段，至少运行 `N >= 2` 个独立评审 agent。
- 两个评审 agent 的模型都不得等于生成模型；两个评审 agent 之间也应尽量不同模型 / 不同 provider。
- 任一独立评审 agent 带证据判 `needs_revision` / `blocked` / `quarantined`，该检查不得自动 pass。
- 如果评审结论冲突，例如一个 pass、一个 needs_revision，进入 `human_escalation`。
- 多评审一致 pass 也只代表自动 verdict 可记录；是否真正解锁仍受 §10.5.5 的连续零 false-pass 阈值约束。

### 10.5.5 影子模式与解锁阈值

自动评审不得一次性取代人工。每个 Gate 必须先进入影子模式：

```text
Hermes 生成
-> deterministic checks 自动出 verdict
-> independent adversarial review agents 自动出 verdict
-> Codex / 用户仍给人工 verdict
-> 逐条对比自动 verdict 与人工 verdict
```

影子模式下，人工 verdict 和自动 verdict 必须使用同一套字段，才能逐条计算 false-pass：

```yaml
check_id: R2.source_coverage
type: deterministic | judgment-grounded | judgment | human_escalation
verdict: pass | pass_with_corrections | needs_revision | blocked | quarantined
evidence:
  - path_or_url: ...
    locator: line/page/heading/timestamp/sha256
reason: ...
reviewer: human_codex | deterministic_script | adversarial_agent_codex | adversarial_agent_deepseek | adversarial_agent_qwen
generated_by: ...
model: ...
timestamp: ...
```

解锁判据是 false-pass 率，不是总体一致率。

- `false-pass`：自动 verdict 为 `pass` / `pass_with_corrections`，但人工 verdict 为 `needs_revision` / `blocked` / `quarantined`，或用户覆盖失败。
- `false-fail`：自动 verdict 更严格，把人工可接受的产物判为失败。false-fail 可容忍，因为它只会增加回炉成本，不会污染下游。
- 某个 Gate 只有在连续 `>=20` 次影子评审中出现 `0` 次 false-pass，才允许从影子模式转正。
- 解锁按 Gate 和 check type 分开进行。Source Gate 的 deterministic 项可以先转正，不代表 Lecture Gate 的 judgment 项也转正。
- 任意一次用户覆盖失败会重置对应 Gate / check type 的连续零 false-pass 计数。

一次 shadow sample 的计数规则：

- 对 `deterministic` 项，sample 通常是一个独立 check item，例如一个 URL、一个 checksum 文件、一个 wikilink、一个 output file、一个 run-log。Source / Code Gate 可能一讲积累多个 sample。
- 对 `judgment-grounded` 项，sample 是一个可被证据锚定的 claim 或 mapping，例如“这段解释是否对齐 notes Eq(15)”“这个 paper section 是否支撑 WP04”。每个 sample 必须有行号、页码、heading、截图或 run-log 锚点。
- 对 `judgment` 项，sample 通常是一个完整 note / waypoint / section 的教学体验判断。
- 对 Completion Gate，sample 通常是一讲的一次 completion verdict；因此 Completion Gate 会长期留在人工或强人工抽查状态，不能因为底层 Source/Code sample 很快满 20 就提前解锁。

转正后也必须保留抽样人工复核；一旦出现 false-pass，立即退回影子模式。

## 11. Supplement Request 补充申请

Supplement Request 解决的是“上游合格，但后续发现范围内小补充不够用”的问题。它不是质量回炉，也不是后续阶段越权重写上游产物的许可。

核心区分：

- `feedback card`：上游做错了、做漏了必做项、违反规则，必须打回或回炉。
- `supplement request`：上游当时合格，但后续编排、写代码或扫作业时发现需要范围内的小补充。

### 11.1 什么时候需要补充而非打回

允许：

- Lecture Weaver 编排 waypoint 时，发现某个 paper figure / table / equation 对学习路径关键，但 Paper Tutor 当时合理 scope-out 或优先级判断不同。
- Code Capsule Runner 写代码时，发现某个工程细节，例如 `unigram^0.75` 为什么不是 `^1.0`，需要小节解释；DeepResearch 主线已覆盖概念，只是没有展开这个工程 insight。
- Assignment Runner 扫描 A1 题目时，发现某个预备知识，例如 SVD、co-occurrence matrix、cosine similarity 公式，属于 L01 官方范围但前面没有明确讲。

不允许：

- 想扩大课程范围，例如 L01 临时加入 fastText、BERT 或 transformer 细节。此类是 scope 决策，必须用户批准。
- 上游明显做错，例如 Paper Tutor 抽错图、DeepResearch 误读 paper。此类是质量问题，走 feedback card。
- 想重写上游产物的主线逻辑。此类是架构问题，必须 block 并复盘。

### 11.2 补充申请格式

后续阶段先在自己的任务 comment / 产物文档里写轻量补充申请，不默认单独开 Kanban 卡：

```yaml
supplement_request:
  - requester: Lecture Weaver t_xxx
    target_stage: Paper Tutor
    item: R01 Table 8 semantic/syntactic analogy examples
    reason: WP05 vector relationship 需要具体例子，Paper Tutor 当时合理优先抽了 Figure 1 和 R02 图表
    use: embed in WP05, path `Assets/L01-word-vectors/papers/supplemented/L01-R01-table8-analogies.png`
    urgency: blocking

  - requester: Code Capsule Runner t_yyy
    target_stage: DeepResearch
    item: unigram^0.75 工程解释
    reason: negative-sampling-demo.py 需要解释采样分布平滑，DeepResearch 主线讲了 NEG 但没展开这个工程 insight
    use: 写进 `DeepResearch/.../word-vectors-main-path.md` 补充小节
    urgency: nice-to-have
```

字段要求：

- `requester` 必须包含角色和任务 ID。
- `target_stage` 必须是上游阶段，例如 Paper Tutor / Course DeepResearch / Lecture Weaver / Code Capsule Runner。
- `item` 必须具体到 paper figure/table/equation、section、公式、API、代码概念或 assignment prerequisite，不能只写“缺图”“缺解释”。
- `reason` 必须说明为什么这是合格后的补充，而不是上游质量失败。
- `use` 必须说明补充后放进哪个 waypoint / code capsule / assignment part。
- `urgency` 只能是 `blocking` 或 `nice-to-have`。

### 11.3 补充执行

- 如果补充 `<=2` 项且都是 `nice-to-have`，Codex Review 阶段可以做确定性小补充，例如抽一个已定位 paper table 截图、补一个链接、补一个 source evidence 路径；状态标 `pass_with_supplement`，并记录到 supplement log。
- 如果补充 `>=3` 项，或包含 `blocking` 概念解释 / 代码解释 / assignment prerequisite，必须开独立小任务，不重跑原阶段。
- 补充任务 parent 是申请者任务，不是原上游任务；这样依赖关系表示“后续阶段发现补充需求”。
- 补充产物 append 到原产物目录，例如 `Assets/.../supplemented/`、DeepResearch 文档新增“补充小节”heading、Code Capsule 增加 debug note；不得重写原文件主体。
- 补充任务也要过轻量 Gate，只检查：是否只做了申请的补充、是否有证据锚点、是否没有越权重写。

### 11.4 预算上限

补充通道有预算，防止滑坡成“后面随便重做前面”：

| 后续阶段 | 补充预算上限 | 超出信号 |
| --- | --- | --- |
| Lecture Weaver | 3 个 paper assets + 1 个 DeepResearch 概念小节 | 上游 Paper Tutor / DeepResearch 范围判断偏差 |
| Code Capsule Runner | 2 个工程细节小节 | DeepResearch 和 Code 的边界不清 |
| Assignment Runner | 1 个预备知识小节 + 2 个 API / debug 注释 | 前面漏了 Assignment Prerequisite Scan |

超出预算时，不能继续靠小补充堆过去；必须 block 并人工复盘是否需要重新规划整讲。

### 11.5 L01 当前阶段处理

L01 已经启动正式 Course DeepResearch `t_d11a3470`。后续如果 Lecture Weaver / Code Capsule Runner / Assignment Runner 发现缺口：

1. 先在自己的任务 comment / 产物文档中写 `supplement_request`。
2. Codex Review Gate 判断是 `feedback card`、`pass_with_supplement`，还是独立 supplement 小任务。
3. 所有补充必须记录到 `artifacts/2026-06-06-l01-supplement-log.md`，供 L02 决定是否引入 skeleton + integration 两轮制。

## 12. 本阶段任务 Prompt 范式

### 12.1 Codex Review Gate Prompt

```text
你是 CS224N Codex Review Gate。你的任务是验收 Hermes 产物是否可以被下游使用。你只评审、反馈和归档；不能手改正文来冒充通过。

目标：
- board: cs224n-study
- task id: {task_id}
- stage: {stage_name}
- output paths: {output_paths}
- upstream dependencies: {dependencies}

必须阅读：
- docs/production-flow-v2/2026-06-06-cs224n-production-flow-v2.md
- 本 stage 对应子文档
- docs/production-flow-v2/2026-06-06-cs224n-production-flow-v2-stage-gates.md
- artifacts/2026-06-06-cs224n-hermes-output-review-rubric.md

任务：
1. 读取任务卡、日志、输出文件。
2. 如果涉及 Obsidian/LiveSync，执行 `vault read` 或检查已有读回证据。
3. 对照 stage 子文档检查输入、输出、禁止事项、验收要求。
4. 列 Findings，按严重度排序。
5. 给出状态：
   - pass
   - pass_with_corrections
   - needs_revision
   - blocked
   - quarantined
6. 如果 needs_revision，写 feedback artifact，明确回炉节点和修复要求。
7. 如果发现的是可复发的流程/格式/prompt 缺陷，必须同步更新对应子文档的 prompt 和验收要求，而不是只在本次 review artifact 里记录。
8. 如果产物合格但后续需要范围内小补充，按 §11 判断是否记录 supplement_request、pass_with_supplement 或开独立 supplement 小任务。
9. 更新 README/AGENTS 或任务归档。

禁止：
- 不因为 Hermes 说 done 就放行。
- 不跳过读回验证。
- 不手工重写正文来提高分数。
- 不启动下游任务，除非当前 review 明确允许。
- 不把流程缺陷当成一次性小问题遗留给后续 agent 猜。
```

### 12.2 Completion Review Prompt

```text
你是 CS224N lecture-completion reviewer。你的任务是判断整讲是否真的完成，而不是判断某个子任务是否完成。

目标：
- lecture: {lecture_id}
- parent task: {parent_task_id}

任务：
1. 检查 Course Harvest、Reading Triage、Paper Tutor、Source Expansion、Course DeepResearch、Lecture Weaver、Code Capsule Runner、Assignment Prerequisite Scan、Assignment Runner、Study Publisher 是否各自通过或明确 scope out。
2. 检查 `00-课堂入口.md` 是否能作为用户唯一主入口。
3. 检查主入口是否有具体 slides/notes/paper/code/assignment 定位，并且不是文件级跳转，而是 heading / block id 级跳转。
4. 检查图、公式、代码输出是否自然嵌入学习节奏。
5. 检查 Colab / run-log / assignment hints 是否存在。
6. 检查 unresolved blockers 和用户覆盖失败。
7. 检查 supplement log：是否有未解决的 blocking supplement_request，补充次数是否超预算。
8. 写 completion report。

输出：
- Lectures/{lecture_id}/completion-report.md
- artifacts/{date}-completion-review-{lecture_id}.md

禁止：
- 不把 smoke test 当正式完成。
- 不把某个子任务 pass 当整讲 pass。
- 不忽略 quarantine 产物。
```

### 12.3 Feedback / Rerun Card Prompt

```text
你是 CS224N feedback-card writer。你的任务是把 Review Gate 的失败项变成 Hermes 可执行的回炉卡。

输入：
- failed task id: {task_id}
- review artifact: {review_artifact_path}
- failed stage: {stage_name}

任务：
1. 只提取 review artifact 中的失败项。
2. 每个失败项写 expected fix、affected files、forbidden changes、verification command。
3. 明确本回炉卡不能扩大范围。
4. 标记下游是否继续 blocked。

输出：
- artifacts/{date}-kanban-feedback-{task_id}.md

禁止：
- 不把用户新想法混进回炉范围。
- 不让回炉 agent 重做整讲。
- 不把还没通过的产物标 downstream_allowed。
```
