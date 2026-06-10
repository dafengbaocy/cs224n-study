# CS224N 编排手册（ORCHESTRATION RUNBOOK）

> **这份文档是单一事实来源。** 下一个接手的 agent（或未来的你）**不要手动编排**：
> 改 `02-readings-map.md` 的 YAML 配置 → 跑一条 `run_lecture.sh` 命令 → 各阶段自动起。
> 不要逐个 launch、不要手动挑 waypoint、不要走一步问一步。

---

## 0. 一句话流程

```
编辑 readings-map（配置）  →  run_lecture.sh  →  worker 停在 review-required  →  独立 reviewer 对抗审批  →  reviewer PASS 后原任务 done  →  debug 人工确认或 auto 进入下一阶段
```

waypoint 投不投、投哪几个，**全由 readings-map 的 YAML 字段决定**，脚本自动读，不需人工指定。

---

## 1. 配置在哪（你唯一要改的地方）

`Lectures/{lecture}/02-readings-map.md` 里两个 YAML 字段：

| 字段 | 驱动阶段 | 关键开关 |
|---|---|---|
| `code_capsules:` | Code Capsules | 列出哪些概念要跑代码胶囊 |
| `deepresearch_waypoints:` | DeepResearch | 每个 waypoint 的 `needs_deepresearch: true/false` |

**`needs_deepresearch` 由 Reading Triage 客观判定**（逐 waypoint 读官方材料判"讲透没"），不是人工拍脑袋。判 `true` 才投 DeepResearch，`false`（官方已讲透）自动跳过。

---

## 2. 怎么跑（一条命令）

```bash
# 在 feiniu 主机的 launch repo 跑
cd /vol2/1000/docker/cs224n-study

# === 三种模式 ===

# 1. debug 模式（默认,调试推荐）:worker review-required → reviewer PASS → 人工 UI 暂停 → 下一阶段
bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage all --mode debug
# 或省略 --mode（debug 是默认）
bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage all

# 2. dispatch 模式:只派任务,不等不评审（快速测试各 launcher）
bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage deepresearch --mode dispatch

# 3. auto 模式:全自动一口气跑到底,但每阶段仍必须 reviewer PASS 才把原任务标 done
bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage all --mode auto

# === 快捷选项 ===

# 先看会投什么,不真投
bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage all --mode dispatch --dry-run

# 重跑某阶段（换幂等键,否则命中旧任务不重投）
bash scripts/launch_deepresearch.sh --lecture L01-word-vectors --parent t_6cbffd16 --run-tag rerun3

# 编排器中断/旧 reviewer 输入失效时，复用已有 worker 任务继续 gate，不重投 worker
bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 \
  --stage paper-tutor --mode debug \
  --reuse-tasks "t_r01 t_r02 t_slides"
```

### 端到端6阶段（--stage all）

```
Triage → Paper Tutor → Glossary Seed → Code Capsules → DeepResearch → Lecture Weaver → Publisher/Finalizer
```

**现在 `--stage all` 是真正的端到端**(覆盖 6 个 agent 阶段 + 1 个确定性前置):
1. **Triage**(单任务): 建 readings-map,判 needs_deepresearch
2. **Paper Tutor**(多任务): 读 core_readings,建 paper bridge
3. **Glossary Seed**(确定性脚本): 在 Code Capsules 前、投任何 capsule worker 之前生成 `00-concept-glossary.md` 的稳定 heading seed
4. **Code Capsules**(多任务): 跑代码胶囊,生成 notebook + 图表
5. **DeepResearch**(多任务): 只跑 needs_deepresearch:true 的 waypoint
6. **Weaver**(单任务): 合并产物,更新主入口,补全/美化 `00-concept-glossary.md`,必要时生成 `Math/<lecture>/*.md`
7. **Publisher/Finalizer**(单任务): 最终发布族检查、写入 Obsidian/LiveSync、生成 vault read 证据、可选清理旧发布残留

### debug 模式流程（reviewer 先过,再人工看）

每个阶段都按同一条闸门链路走:

1. 派阶段 worker。
2. worker 正常完成生产后应停在 `blocked/review-required`,只代表"可送审",不代表通过。
3. 编排器自动派独立 reviewer agent。
4. reviewer 输出 `VERDICT: PASS`:
   - 编排器将原 worker 任务 `complete` 为 `done`
   - debug UI 才启动: `http://192.168.31.173:9120`
   - 用户在 UI 检查阶段产物,点击通过后才进入下一阶段。
5. reviewer 输出 `VERDICT: BLOCK` 或无明确 verdict:
   - 编排器把原 worker 任务 unblock 返工。
   - 最多返工 5 次;超过上限后整条编排停止。

debug 模式的人工确认是**第二道闸门**。它不能替代 reviewer,也不能发生在 reviewer 之前。

### auto 模式流程（全自动,但仍过 reviewer）

1. 派阶段 worker → 等全部进入 `blocked/review-required` 或其他终态。
2. 对每个 worker 任务派独立 reviewer。
3. reviewer `VERDICT: PASS` → 编排器将原 worker 任务 `complete` 为 `done`,然后自动进入下一阶段。
4. reviewer `VERDICT: BLOCK` → unblock 原 worker 返工,最多 5 次。
5. reviewer 自身失败/崩溃/无法运行 → 停止编排,不把基础设施问题算成 worker 质量问题。

### web UI（实时查看/手动操作）

Hermes dashboard 已在 feiniu 运行,浏览器打开:
```
http://192.168.31.173:9119
```
可以看 kanban board、任务状态、产物,手动 block/complete/comment 任务。

`run_lecture.sh` 启动时不再同步两 repo 的 readings-map。运行时真源是 Hermes workspace：`/workspace/cs224n-study`（宿主映射为 `/vol2/1000/docker/hermes/workspace/cs224n-study`）。启动 repo 只用于调度脚本和 Git 镜像。

---

## 3. 阶段全景（哪些自动、哪些单任务）

| 阶段 | 类型 | 怎么起 | 配置来源 |
|---|---|---|---|
| 1. Reading Triage | 单任务 | 手动投一次（建 readings-map + 判 needs_deepresearch） | 官方 readings |
| 2. Paper Tutor | 多任务并行 | `launch_paper_tutor.sh`（按 core readings） | readings-map core 列表 |
| 3. Glossary Seed | 确定性脚本 | `run_lecture.sh --stage capsules` 投 worker 前自动执行 | `code_capsules:` |
| 4. Code Capsules | 多任务并行 | `run_lecture.sh --stage capsules` | `code_capsules:` |
| 5. DeepResearch | 多任务并行 | `run_lecture.sh --stage deepresearch` | `deepresearch_waypoints:`（`needs_deepresearch`） |
| 6. Lecture Weaver | 单任务收口 | `run_lecture.sh --stage weaver` | 上游全部产物 |
| 7. Publisher/Finalizer | 单任务发布 | `run_lecture.sh --stage publisher-finalizer` | `publish-manifest.json` |

**多任务阶段**走 `run_lecture.sh`，脚本读 YAML 自动决定投几个、投哪几个。
**单任务阶段**（triage / weaver）一讲只跑一次，直接投任务卡即可，不需要 launcher。

### 3.1 父任务约束如何下发

父任务 body 只记录本轮 run 的目标和启动方式，不能假设所有子任务都会可靠继承父任务正文。父任务里的硬约束必须拆到对应位置：

- 编排方式，例如 `run_lecture.sh --mode auto --stage all`：由操作者/编排器保证，不塞给普通 worker。
- worker 终态协议：写在每个 worker stage prompt。
- reviewer 只能 verdict、不改 worker 状态：写在 reviewer prompt。
- 主入口必须是中文课堂讲义、深数学推导走 `Math/{lecture}`：写在 Weaver / Publisher-Finalizer prompt 和 reviewer rubric。
- 英文图片转写/翻译：写在 Paper Tutor / DeepResearch / Weaver prompt 和 reviewer rubric。
- notebook Markdown 与学习者注释中文优先：写在 Code Capsules / Publisher-Finalizer prompt 和 reviewer rubric。
- Obsidian 发布与 vault read evidence：写在 Publisher-Finalizer prompt 和 reviewer rubric。

不要把完整父任务硬约束整段注入所有 stage。那会让 Triage、Paper Tutor、Reviewer 等任务背上不属于自己的职责，制造误判和 prompt 噪音。正确做法是：通用协议进通用 prompt，阶段要求进阶段 prompt。

---

## 4. 已知坑（务必记住）

1. **两 repo drift**：worker 写 `/vol2/1000/docker/hermes/workspace/cs224n-study/`。2026-06-10 后不再用 rsync 消除 drift；launcher 若需要上游产物，必须直接读 Hermes workspace。阶段通过 reviewer 后再用 Git commit/push 记录长期版本。
2. **PyYAML 只在 feiniu 主机有**，容器 venv 没有。`parse_readings_map.py` 在主机跑，OK。
3. **幂等键含日期**：同一天同 waypoint 重投不会再 spawn（命中旧任务）。重跑用 `--run-tag`。
4. **review gate 是故意的**：worker 正常产出后必须停在 `blocked/review-required`。`done` 只应由编排器在独立 reviewer `VERDICT: PASS` 后写入。debug 模式还会在 reviewer PASS 后再等人工确认。
5. **readings-map 的 YAML fence 不能手工 sed 猜修**：`code_capsules:` 和 `deepresearch_waypoints:` 必须各自放在完整的 ```yaml 围栏块里。坏例子是 `code_capsules` 开了 fence 后没有在字段结束处闭合，结果 `## 9` heading 被吞进 YAML，debug 模式会卡在第一阶段。
6. **所有 launcher 都走 `parse_readings_map.py`**：`launch_code_capsules.sh` 和 `launch_deepresearch.sh` 都必须通过同一个解析器读字段，禁止再用 `awk '/^```yaml$/,/^```$/'` 这种只抓第一个 YAML 块的方式。解析器会优先读完整 fence；发现坏 fence 时会报行号，并用字段级 fallback 临时提取字段。fallback 只用于止血，看到 warning 后必须修 `02-readings-map.md` 的 fence。
7. **不要重投 worker 来修 reviewer 输入陈旧**：如果 reviewer 任务卡里已经写死了旧 deterministic output（例如旧脚本误报 `exit=1`），这张 reviewer 不能作为有效评审。归档旧 reviewer 后，用 `run_lecture.sh --reuse-tasks "..."` 从同一阶段继续 gate，让编排器重新同步产物、重新跑 deterministic checks、重新派 reviewer。
8. **媒体双轨是阶段契约,不是最后补锅**：本地 `Assets/` / `Labs/.../outputs` 文件只作为 agent 识别、复查和 provenance 轨保留；凡写进用户可读 Markdown 正文的图片,从 Paper Tutor / Code Capsules / DeepResearch 开始就必须使用图床或官方远程 URL。生产图片的阶段负责立即上传并写 `Lectures/<lecture>/media-registry/*.json`。Weaver 只消费 registry,不能把批量上传本地图片当作主流程。
9. **Code Capsules 采用 partial 架构，worker 禁写总入口**：每个 capsule worker 可以并行跑代码，但只能写自己的 `Lectures/<lecture>/code-capsules/<slug>.md`。禁止写、改、创建 canonical `Lectures/<lecture>/04-code-capsules.md`；总入口只能由 integration 阶段的 `scripts/merge_code_capsules.py` 从 partial 确定性合并生成。禁止创建 `Labs/<lecture>/04-code-capsules.md` 副本。
10. **Code Capsules 的数字必须可追溯**：partial 里的 probability/cosine/loss/shape/ranking/nearest-neighbor 等数值只能复制本轮 stdout/output/run-log。每个 capsule partial 必须包含 `numeric_provenance` 证据块；没有真实输出的数值要写“未产生该数值”，不能靠模型补。此前 L01 `pretrained-analogy` 曾因旧 toy 数值混入真实 GloVe 输出而被 Content Gate 挡回，这是正例警报。
11. **重跑必须换 idempotency key**：`launch_code_capsules.sh` 支持 `RUN_TAG`。需要重新跑一轮时使用 `RUN_TAG=<unique>`，否则可能复用旧任务，看起来“重跑”实际只是旧卡片被 promoted。
12. **DeepResearch 必须使用 Hermes goal mode**：普通 one-shot worker 多次忽略终态协议并直接 `completed`，所以 `launch_deepresearch.sh` 必须通过 `create_cs224n_task_with_notify.sh --goal --goal-max-turns 8` 创建任务。DeepResearch worker 没有停在 `blocked/review-required` 时，该轮无效，归档后用 fresh task id 重启。
13. **`00-concept-glossary.md` 是 Code 前置 seed，不是 Weaver 才生成**：Code / DeepResearch 会链接 `Lectures/<lecture>/00-concept-glossary.md#term`。因此 `run_lecture.sh --stage capsules` 在投任何 Code worker 前必须先跑 `scripts/seed_concept_glossary.py` 生成稳定 heading，并同步到 Hermes workspace。Weaver 后续只能补全、去重和美化同一个 `00-concept-glossary.md`，不要再新造 `99-glossary.md` 当主 glossary。若 worker/reviewer 发现 seed 缺失，这是编排器错误：先停链路修 orchestration，不把责任甩给单个 capsule。
14. **Capsule 单项 review 只审当前 capsule，integration 才审全阶段**：per-capsule Rule Gate 只检查当前 `code-capsules/<slug>.md`、当前 `Labs/<lecture>/<slug>.*`、当前 `outputs/<slug>*`、当前 `media-registry/code-capsule-<slug>.json` 和 `00-concept-glossary.md`。不要把整个 `Labs/<lecture>`、全部 sibling partial 或旧 Paper Tutor 复制件算到某一个 capsule 头上。全量链接、merge 后 `04-code-capsules.md` 和 sibling 冲突只在 `capsules-integration` 查。
15. **Code Capsule 入口当前 canonical 是 `04-code-capsules.md`**：每个 capsule worker 只写 `Lectures/<lecture>/code-capsules/<slug>.md`，integration 阶段用 `merge_code_capsules.py` 合并成 `04-code-capsules.md`。旧设计文档里的 `06-code-capsules.md` 只作为历史兼容；新 prompt、manifest、Weaver 不得把 `06` 当主入口。
16. **共享 run-log 可以保留，但必须 tagged + locked**：`Labs/<lecture>/run-log.md` 是全讲共享审计日志。并行 capsule worker 不能直接 `>>` 多行追加；必须先写临时 run entry，再用 `flock Labs/<lecture>/run-log.lock ...` 原子追加。每个 section 必须包含 `run_id / task_id / capsule_slug / command / exit_code / stdout / outputs`，per-capsule reviewer 只检查当前 `task_id + capsule_slug` 的唯一 section。
17. **Code Capsule 的 GitHub/Colab push 必须加锁**：多个 capsule 会并行推同一个公开 `cs224n-study` repo/branch，即使 study-ops 有 pull-before-push，也必须用 `flock /workspace/cs224n-study/artifacts/github-push.lock` 包住 `github-push`，避免 `.git` index、main 分支更新或 Colab 链接发布互相打架。Colab 链接必须用未登录环境验证可访问，不能发布到 private repo 后假定用户能打开。
18. **Notebook 面向用户的 Markdown 必须中文优先**：`.ipynb` 不是纯运行副本。所有 Markdown cell、读图说明、输出解释、面向学习者的注释都必须中文优先；API 名/变量名可以英文。Rule Gate 使用 `scripts/review_checks/check_notebook_chinese.py`，Content Gate 仍要判断解释是否真正服务课堂。
19. **英文图片要翻译/转写，不让用户硬啃图**：Paper Tutor 抽 slides/notes/paper 图时，文字型图片必须做 `图片文字带读`：摘关键英文、中文翻译、读图顺序、学习结论。Weaver 嵌入图片时必须复用或补齐这段中文读图卡。只贴全英文 slide/table 截图，没有中文读图说明，应被 reviewer BLOCK。
20. **较深数学推导走 Math 扶手**：主入口保留结论、直觉和学习用途；SVD、特征值/特征向量、矩阵形状、cosine、softmax、负采样损失等会影响课堂/作业的深推导，写到 `Math/<lecture>/*.md` 并从主入口精确链接。Math 文档存在即进入 `publish-manifest.json`，最终同步到 Obsidian。
21. **Publisher/Finalizer 是独立阶段，不是 Weaver reviewer**：Weaver 负责写课；Reviewer 负责挑刺；Publisher/Finalizer 负责发布族总检、小修、Obsidian 写入、vault read 证据和可选旧文件清理。它不能偷偷重写教学主线；发现主入口太薄、notebook 英文、Math 扶手缺失时，退回对应阶段。
22. **Code Capsules 有两份必须同步的来源**：`docs/production-flow-v2/2026-06-07-stage-prompts-code-capsules.md` 是规范库，但真实 worker 任务卡目前由 `scripts/launch_code_capsules.sh` 手写模板生成。修改 Code Capsule 规则时，不能只改 prompt 库；必须同步修改 launcher 模板，并用 `launch_code_capsules.sh --dry-run` 检查生成卡片里真的出现新规则。否则会出现“reviewer 按新规则挡回，但 worker 任务卡从未收到规则”的假返工。
23. **Code Capsule reviewer 必须同时跑 notebook 中文检查**：per-capsule Rule Gate 应只检查当前 `Labs/<lecture>/<slug>.ipynb`，integration Gate 才检查全部 notebook。`check_notebook_chinese.py` 失败是 Rule Gate blocker；通过后 reviewer 仍要做 Content Gate，判断中文解释是否真的服务课堂，而不是只满足关键词。

24. **所有多任务阶段的合并评审都必须有 repair loop**：`paper-tutor`、`capsules`、`deepresearch` 等 sibling worker 全部 scoped PASS 后，会进入 `*-integration` 集合评审。集合评审 BLOCK 不能直接让编排器停死，因为 integration target 是 synthetic task，不能像普通 worker 一样 unblock 返工。`run_lecture.sh` 必须启动 `Stage Integration Repair` 小任务做最小集成修复，然后重新跑 integration reviewer，最多 5 次；只有 repair 超范围、reviewer 基础设施失败或达到返工上限才停止。

### YAML 配置验证命令

debug / auto 前先做 dry-run，不要直接投任务：

```bash
cd /vol2/1000/docker/cs224n-study

python3 scripts/parse_readings_map.py Lectures/L01-word-vectors/02-readings-map.md --field code_capsules
python3 scripts/parse_readings_map.py Lectures/L01-word-vectors/02-readings-map.md --field deepresearch_waypoints --needs-deepresearch-only

bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage capsules --mode dispatch --dry-run
bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage deepresearch --mode dispatch --dry-run

# 真重跑 Code Capsules 时显式换 tag，避免复用旧 task idempotency key
RUN_TAG=rerun-$(date +%Y%m%d%H%M%S) bash scripts/run_lecture.sh --lecture L01-word-vectors --parent t_6cbffd16 --stage capsules --mode debug
```

通过标准：

- `code_capsules` 应输出 5 个 L01 capsule（或当前讲次配置的全部 capsule）。
- `deepresearch_waypoints --needs-deepresearch-only` 只输出 `needs_deepresearch: true` 的 waypoint。
- 没有 `field fallback` warning。若出现 warning，可以说明 parser 暂时救回了字段，但 Markdown 源仍要修。

---

## 5. 核心原则（给接手的 agent）

> **改配置，不改脚本。** 要让某 waypoint 做 DeepResearch，去 readings-map 把它的 `needs_deepresearch` 改成 `true`，不要去脚本里硬编码。要加 capsule，往 `code_capsules:` 加一条。脚本是泛化的，跨讲次、跨课程复用，不该为某一讲改它。

> **不要手动编排、不要走一步问一步。** 配置定好就跑 `run_lecture.sh`，让它自己读配置投任务。判断"投不投"的依据写在 readings-map 里（由 triage 客观判定），不靠人临场拍脑袋。

---

## 6. 独立 reviewer 架构（debug/auto 共用质量闸门）

每个阶段的 worker 终态只表示"这一轮 worker 已经停下"。正式的待审终态只有 `blocked/review-required`；worker 自己写 `completed/done` 是协议违规。编排器按下面的规则处理:

1. worker 是 `blocked` 且 summary/reason/comment 含 `review-required` / `ready_for_review` / `可送审`:
   - 编排器派 reviewer。
   - reviewer PASS 后,编排器把原 worker `complete` 成 `done`。
2. worker 是 `blocked` 但不是待审语义,或是 `failed/crashed/quarantined`:
   - 编排器写入返工原因,unblock 原任务,重新 dispatch。
   - 最多返工 5 次。
3. worker 是 `completed/done`:
   - 这是协议违规，不送 reviewer，不进入 debug UI。
   - 编排器写入 `protocol_violation` comment，unblock 原任务返工。
   - 返工后的 worker 仍必须以 `blocked/review-required` 结束，才会被送独立 reviewer。
4. reviewer `VERDICT: PASS`:
   - debug 模式:启动 debug UI,等待用户人工通过。
   - auto 模式:直接进入下一阶段。
5. reviewer `VERDICT: BLOCK` 或 summary 没有明确 verdict:
   - 编排器把原 worker unblock 返工。
   - 最多返工 5 次。
6. reviewer 自身 `blocked/failed/crashed`:
   - 这是评审基础设施失败,编排器停止。
   - 不自动让 worker 背锅返工。

这套设计保留了抓 WP04 第一次"广而浅但自称完成"那种问题的能力,同时不需要人工逐个核验——reviewer 是 agent,但**独立于** worker(对抗性)。

reviewer 不是只跑规则检查。正式 reviewer gate 必须拆成两层:

1. **Rule Gate**: deterministic checks,负责文件/链接/YAML/run-log/证据路径等机器可验证项。
2. **Content Gate**: 独立 reviewer 读取产物和阶段 prompt,判断内容是否忠于官方材料、是否讲清楚、是否遗漏关键学习点、是否能安全交给下游。

Rule Gate pass 只表示"结构没有坏",不表示"内容可以学"。只有 Rule Gate 和 Content Gate 都 pass,worker 才能被编排器标为 `done`。

### 6.1 reviewer 独立性硬规则

- reviewer 不能是同一个 worker session 的自评。
- reviewer 只看产物、公开任务日志、deterministic check 输出和可验证证据,不读取/依赖 worker 隐藏思考过程。
- reviewer prompt 的目标是找缺陷,不是替 worker 背书。
- reviewer 不允许直接 `block/unblock/complete` 被评审的 worker task。它只能完成自己的 reviewer task,并在 summary 第一行写 `VERDICT: PASS` 或 `VERDICT: BLOCK`。原 worker 的状态流转由 `run_lecture.sh` 编排器统一处理。
- reviewer 即使判 `BLOCK`,自身也必须 completed/done。reviewer 自身 blocked/failed/crashed 属于评审基础设施失败,不能转嫁给 worker。
- 有证据锚点的判断必须抽查至少 3 个原文/页码/行号；如果产物包含 paper/slides/notes 三类来源,至少各抽 1 个。
- reviewer summary 必须同时写 `rule_gate` 和 `content_gate` 结论；缺少 `content_gate` 或 `downstream_allowed` 的 PASS 视为无效 PASS。
- worker 自己写 `done/status/pass` 不构成通过依据；正式流程里 worker 不应自行 done。
- 每个 worker prompt 必须包含统一的终态执行命令：`hermes kanban --board cs224n-study block <当前task_id> "review-required: ready_for_review=true downstream_allowed=false; outputs=<主要产物路径>"`。具体输出路径写在执行报告，不在通用协议里硬编码。

### 6.2 Content Gate 最低要求

Content Gate 的问题不是"格式好不好",而是"用户能不能靠它学下去"。不同阶段至少检查:

- `triage`: core/support/optional 分层是否忠于官方锚点；deepresearch waypoint 是否客观；code capsule 是否覆盖关键可运行理解点。
- `paper-tutor`: paper section / figure / table / equation 是否忠于原文；中文陪读是否按"先人话、再技术名、再回原文"；bridge 是否精确回嵌到 lecture waypoint / code / assignment。
- `capsules`: 代码是否真实运行并有可信输出；输出是否解释课堂概念；是否有边界提醒。
- `deepresearch`: 是否只补官方薄弱点；非官方来源是否分层且不盖过官方；每个 waypoint 是否有 evidence note 和回嵌位置。
- `weaver`: 主入口是否按学习节奏串起来；Obsidian 可见图片/链接/重点层级是否真的服务阅读；不得把内容隔离成资料仓库。

### 6.3 返工上限

`MAX_REWORKS=5` 表示最多允许 5 次返工,不是总尝试 5 次。也就是:

- 初稿 1 次。
- reviewer 或 worker gate 挡回后,最多再返工 5 次。
- 第 6 次尝试仍未通过时,编排停止并保留任务状态给人工排查。

### 6.4 Rule Gate 作用域边界

Rule Gate 必须通用化,不能写死某一讲、某篇材料或某个固定子任务数量。所有源文件和阅读对象都应从当前讲次的 `Lectures/{lecture}/02-readings-map.md`、任务卡输入或当前 worker 产物解析。

并行阶段要分清两种检查:

- **单 worker scoped gate**: 只检查当前 worker 拥有的主文档、当前 registry、当前 run-log section 和当前 source asset。它可以要求 partial/index 文件存在,但不能因为 partial 里指向兄弟任务尚未稳定的 heading 而阻断当前 worker。
- **stage integration gate**: 所有兄弟 worker 都 scoped PASS 后才运行,负责检查 cross-partial wikilink、兄弟产物冲突、coverage 合并和下游接口稳定性。

2026-06-10 事故记录: Paper Tutor 的单 worker Rule Gate 曾检查 `03-paper-bridge.partial-*` 中指向兄弟 slides/notes 的 heading,导致单篇 paper 任务被 sibling stale heading 误杀。修复后,per-worker gate 只对当前 paper note 或 slides-note 主文档跑硬链接解析;partial bridge 的跨文件解析推迟到 `paper-tutor-integration`。

验证记录:

- `scripts/review_checks/check_required_sources.py` 已改为从当前 readings-map 读取 `local_pdf` 和 official PDF,不再使用固定讲次路径。
- Hermes workspace 中 `check_required_sources.py --lecture L01-word-vectors --kind paper/slides/paper-tutor-integration` 通过。
- Hermes workspace 中现有 R02 paper note 的 per-worker `check_links_headings.py --forbid-local-images` 通过;partial bridge 跨兄弟链接不再在单 worker gate 中硬失败。
- active scripts / reviewer prompt / paper-tutor prompt 未检出固定讲次 source 路径。

**相关文件**:
- `scripts/launch_reviewer.sh` — reviewer dispatcher,先跑 check、注入结果到 prompt、派独立 agent
- `docs/production-flow-v2/2026-06-07-stage-prompts-reviewer.md` — reviewer prompt 模板
- `scripts/run_lecture.sh` 的 `orchestrate_all()` — 等终态 → 批量派 reviewer → 推进
- `scripts/publish_manifest_to_vault.py` — Publisher/Finalizer 使用的 Obsidian 发布 helper,读 manifest、写 vault、生成 `artifacts/<lecture>-vault-read-evidence.json`

---

## 7. 文件清单（这次改了什么）

新增:
- `scripts/run_lecture.sh` — 单一编排入口(dispatch/orchestrate 两模式)
- `scripts/parse_readings_map.py` — 健壮 YAML 解析器(PyYAML,自动筛 `needs_deepresearch`，带 YAML fence 行号诊断和字段级 fallback)
- `scripts/launch_reviewer.sh` — reviewer dispatcher
- `scripts/launch_publisher_finalizer.sh` — Publisher/Finalizer dispatcher
- `scripts/publish_manifest_to_vault.py` — manifest → Obsidian/LiveSync 发布 helper
- `docs/production-flow-v2/2026-06-07-stage-prompts-reviewer.md` — reviewer prompt 模板
- `docs/production-flow-v2/2026-06-09-stage-prompts-publisher-finalizer.md` — Publisher/Finalizer prompt 模板
- `docs/production-flow-v2/ORCHESTRATION-RUNBOOK.md` — 本文档

改:
- `scripts/launch_deepresearch.sh` — 接上解析器,自动筛 `needs_deepresearch:true`,加 `--run-tag`
- `scripts/launch_code_capsules.sh` — 接上同一解析器读取 `code_capsules`，不再用 awk 抓第一个 YAML block
- `AGENTS.md` — 加编排层说明 + runbook 指针
