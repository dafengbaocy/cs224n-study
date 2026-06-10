#!/usr/bin/env bash
# run_lecture.sh — CS224N 全流程编排（worker → adversarial reviewer gate）
#
# 设计：每阶段 worker 完成产物后应停在 blocked/review-required,不能自我放行。
#       编排器派独立 reviewer agent 审批；reviewer PASS 后由编排器 complete 原任务。
#       debug 模式在 reviewer PASS 后暂停给人看，
#       auto 模式在 reviewer PASS 后直接进入下一阶段；BLOCK 则返工，最多 5 次。
# 完整说明见 docs/production-flow-v2/ORCHESTRATION-RUNBOOK.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HERMES_REPO="/vol2/1000/docker/hermes/workspace/cs224n-study"
LAUNCH_REPO="/vol2/1000/docker/cs224n-study"

# --- 优雅停止：捕获 Ctrl+C,清理子进程,可选地停掉已派任务 ---
DISPATCHED_TASKS=""  # 空格分隔的 task ID 列表
cleanup() {
  echo ""
  echo "=== 捕获中断信号(Ctrl+C),清理中 ==="
  # 杀掉此脚本启动的子进程(ssh/等待循环)
  jobs -p | xargs -r kill 2>/dev/null || true
  if [[ -n "$DISPATCHED_TASKS" ]]; then
    echo "已派任务: $DISPATCHED_TASKS"
    read -p "要停掉这些任务吗? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      for tid in $DISPATCHED_TASKS; do
        echo "  停止 $tid ..."
        sudo docker exec hermes hermes kanban --board cs224n-study block "$tid" "编排脚本被用户中断" 2>/dev/null || true
      done
    else
      echo "已派任务继续运行,可手动在 dashboard 管理: http://192.168.31.173:9119"
    fi
  fi
  exit 130
}
trap cleanup SIGINT SIGTERM

usage() {
  cat <<EOF
用法: $0 --lecture LECTURE_ID --parent PARENT_TASK_ID [--stage STAGE] [--mode MODE] [--dry-run] [--reuse-tasks "t_x t_y"]

模式（--mode，默认 debug）:
  dispatch      只派当前阶段任务,不等不评审（快速测试各 launcher）
  debug         worker 停在 review-required → reviewer PASS → 人工 UI 暂停 → 下一阶段
  auto          worker 停在 review-required → reviewer PASS → 直接下一阶段（生产用）

阶段（--stage，默认 all）:
  triage           Reading Triage（单任务,建 readings-map + 判 needs_deepresearch）
  paper-tutor      Paper Tutor（多任务,按 core readings）
  capsules         Code Capsules（多任务,读 code_capsules）
  deepresearch     DeepResearch（多任务,读 deepresearch_waypoints 只投 needs_deepresearch:true）
  weaver           Lecture Weaver（单任务,合并 bridge + 主入口 + glossary 收口）
  publisher-finalizer  Publisher/Finalizer（最终发布 Obsidian + 查缺补漏 + 可选清理旧发布残留）
  all              端到端:triage → paper-tutor → capsules → deepresearch → weaver → publisher-finalizer

在 debug/auto 模式下，--stage 表示"从该阶段开始继续跑后续阶段"。
例如 --stage paper-tutor --mode auto 会自动跑 paper-tutor → capsules → deepresearch → weaver → publisher-finalizer，
并且每阶段仍必须 worker → reviewer gate，不允许手动投递下一阶段。

选项:
  --lecture   讲次 ID（如 L01-word-vectors）
  --parent    父任务 ID
  --stage     阶段名（默认 all）
  --mode      dispatch / debug / auto（默认 debug）
  --dry-run   传给下游 launcher,只生成任务卡不投递
  --reuse-tasks 复用已存在的本阶段 worker task ids，只重新进入 gate/reviewer；用于编排器中断恢复

示例:
  # 调试模式（推荐）:每阶段后暂停,检查产物,按回车继续
  $0 --lecture L01-word-vectors --parent t_xxx --stage all --mode debug

  # 快速测试某阶段 launcher（只派不等）
  $0 --lecture L01-word-vectors --parent t_xxx --stage deepresearch --mode dispatch --dry-run

  # 全自动跑到底（生产用,测试通过后）
  $0 --lecture L01-word-vectors --parent t_xxx --stage all --mode auto
EOF
  exit 1
}

LECTURE="" ; PARENT="" ; STAGE="all" ; MODE="debug" ; DRY_RUN="" ; REUSE_TASKS=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --lecture) LECTURE="$2"; shift 2 ;;
    --parent)  PARENT="$2";  shift 2 ;;
    --stage)   STAGE="$2";   shift 2 ;;
    --mode)    MODE="$2";    shift 2 ;;
    --dry-run) DRY_RUN="--dry-run"; shift ;;
    --reuse-tasks) REUSE_TASKS="$2"; shift 2 ;;
    *) usage ;;
  esac
done
[[ -z "$LECTURE" || -z "$PARENT" ]] && usage

# One run tag for idempotency keys, stage snapshots, and log correlation.
RUN_TAG="${RUN_TAG:-orchestrator-$(date +%Y%m%d%H%M%S)}"
export RUN_TAG

# --- GitHub 同步纪律 ---
#
# 2026-06-10: 不再用 rsync 在 launch repo 和 Hermes workspace 之间搬阶段产物。
# 阶段产物的运行时真源是 Hermes workspace(`/workspace/cs224n-study`)。
# launch repo 只负责启动脚本/任务卡和 Git 镜像；需要长期留存的版本通过
# reviewer pass 后的 Git commit/push 记录，而不是编排器临时复制。
sync_repos() {
  echo "=== GitHub sync discipline: runtime source is Hermes workspace; no rsync ==="
}

sync_workspace_to_launch() {
  echo "=== No runtime mirror: reviewer reads Hermes workspace directly ==="
}

# --- 各阶段 dispatcher ---
dispatch_triage() {
  echo "=== STAGE: Reading Triage ==="
  local tag_args=()
  if [[ -n "${RUN_TAG:-}" ]]; then
    tag_args=(--run-tag "$RUN_TAG")
  fi
  local out=$(bash "$SCRIPT_DIR/launch_triage.sh" --lecture "$LECTURE" --parent "$PARENT" "${tag_args[@]}" $DRY_RUN 2>&1)
  echo "$out"
  local tasks=$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tr '\n' ' ')
  DISPATCHED_TASKS="$DISPATCHED_TASKS $tasks"
}
dispatch_paper_tutor() {
  echo "=== STAGE: Paper Tutor ==="
  local tag_args=()
  if [[ -n "${RUN_TAG:-}" ]]; then
    tag_args=(--run-tag "$RUN_TAG")
  fi
  local out=$(bash "$SCRIPT_DIR/launch_paper_tutor.sh" --lecture "$LECTURE" --parent "$PARENT" "${tag_args[@]}" $DRY_RUN 2>&1)
  echo "$out"
  local tasks=$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tr '\n' ' ')
  DISPATCHED_TASKS="$DISPATCHED_TASKS $tasks"
}
dispatch_capsules() {
  echo "=== STAGE: Code Capsules ==="
  echo "=== Prepare Code Capsules prerequisites: seed 00-concept-glossary.md ==="
  python3 "$SCRIPT_DIR/seed_concept_glossary.py" --root "$HERMES_REPO" --lecture "$LECTURE"
  local out=$(bash "$SCRIPT_DIR/launch_code_capsules.sh" --lecture "$LECTURE" --parent "$PARENT" $DRY_RUN 2>&1)
  echo "$out"
  # 抓 task ID 记录到全局变量
  local tasks=$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tr '\n' ' ')
  DISPATCHED_TASKS="$DISPATCHED_TASKS $tasks"
}
dispatch_deepresearch() {
  echo "=== STAGE: DeepResearch（只投 needs_deepresearch:true）==="
  local tag_args=()
  if [[ -n "${RUN_TAG:-}" ]]; then
    tag_args=(--run-tag "$RUN_TAG")
  fi
  local out=$(bash "$SCRIPT_DIR/launch_deepresearch.sh" --lecture "$LECTURE" --parent "$PARENT" "${tag_args[@]}" $DRY_RUN 2>&1)
  echo "$out"
  local tasks=$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tr '\n' ' ')
  DISPATCHED_TASKS="$DISPATCHED_TASKS $tasks"
}
dispatch_weaver() {
  echo "=== STAGE: Lecture Weaver ==="
  local tag_args=()
  if [[ -n "${RUN_TAG:-}" ]]; then
    tag_args=(--run-tag "$RUN_TAG")
  fi
  local out=$(bash "$SCRIPT_DIR/launch_weaver.sh" --lecture "$LECTURE" --parent "$PARENT" "${tag_args[@]}" $DRY_RUN 2>&1)
  echo "$out"
  local tasks=$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tr '\n' ' ')
  DISPATCHED_TASKS="$DISPATCHED_TASKS $tasks"
}
dispatch_publisher_finalizer() {
  echo "=== STAGE: Publisher / Finalizer ==="
  local tag_args=()
  if [[ -n "${RUN_TAG:-}" ]]; then
    tag_args=(--run-tag "$RUN_TAG")
  fi
  local out=$(bash "$SCRIPT_DIR/launch_publisher_finalizer.sh" --lecture "$LECTURE" --parent "$PARENT" "${tag_args[@]}" $DRY_RUN 2>&1)
  echo "$out"
  local tasks=$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tr '\n' ' ')
  DISPATCHED_TASKS="$DISPATCHED_TASKS $tasks"
}

# --- auto/debug 模式:worker → adversarial reviewer gate → debug pause/auto advance ---
# MAX_REWORKS 表示最多允许返工 5 次；因此总尝试次数 = 初稿 1 次 + 返工 5 次。
MAX_REWORKS="${MAX_REWORKS:-5}"
MAX_ATTEMPTS=$((MAX_REWORKS + 1))

latest_run_json() {
  local tid="$1"
  sudo docker exec hermes hermes kanban --board cs224n-study runs "$tid" --json 2>/dev/null \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); runs=d.get("runs", []) if isinstance(d, dict) else d; print(json.dumps(max(runs, key=lambda r: r.get("id", 0)) if runs else {}))' 2>/dev/null \
    || echo '{}'
}

latest_run_id() {
  latest_run_json "$1" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r.get("id") or 0)'
}

task_outcome() {
  latest_run_json "$1" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r.get("outcome") or r.get("status") or "unknown")'
}

task_summary() {
  latest_run_json "$1" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r.get("summary") or r.get("error") or "")'
}

task_already_reviewer_passed() {
  local tid="$1"
  local outcome summary
  outcome="$(task_outcome "$tid")"
  summary="$(task_summary "$tid")"
  [[ ( "$outcome" == "completed" || "$outcome" == "done" ) && "$summary" == reviewer_pass:* ]]
}

declared_output_paths() {
  local tid="$1"
  task_summary "$tid" | python3 -c 'import re,shlex,sys
text=sys.stdin.read()
m=re.search(r"outputs?\s*=\s*(.+?)(?:;|\n|$)", text, re.I)
if not m:
    sys.exit(0)
raw=m.group(1).strip()
raw=raw.replace(",", " ")
try:
    parts=shlex.split(raw)
except ValueError:
    parts=raw.split()
for part in parts:
    part=part.strip().strip("`").strip()
    if part and not part.startswith("<"):
        print(part)'
}

task_context() {
  sudo docker exec hermes hermes kanban --board cs224n-study context "$1" 2>/dev/null \
    || sudo docker exec hermes hermes kanban --board cs224n-study show "$1" 2>/dev/null \
    || true
}

deepresearch_target_token() {
  local tid="$1"
  task_context "$tid" | python3 -c 'import re,sys
text=sys.stdin.read()
m=re.search(r"waypoint:\s*`?\s*(WP\d+)\b", text, re.I)
if not m:
    m=re.search(r"DeepResearch\s+(WP\d+)\b", text, re.I)
print(m.group(1).lower() if m else "")'
}

code_capsule_slug() {
  sudo docker exec hermes hermes kanban --board cs224n-study show "$1" 2>/dev/null \
    | python3 -c 'import re,sys
text=sys.stdin.read()
m=re.search(r"Code Capsule\s+([A-Za-z0-9_.-]+)", text)
if not m:
    m=re.search(r"# CS224N [^\n]* Code Capsule [—-]\s*([A-Za-z0-9_.-]+)", text)
print(m.group(1) if m else "")' 2>/dev/null
}

paper_tutor_target_token() {
  sudo docker exec hermes hermes kanban --board cs224n-study show "$1" 2>/dev/null \
    | python3 -c 'import re,sys
text=sys.stdin.read()
m=re.search(r"\b(L\d+-R\d+)\b", text, re.I)
if m:
    print(m.group(1).split("-")[-1].lower())
elif re.search(r"Task\s+\S+:\s*[^\n]*Paper Tutor:\s*[^\n]*slides|Paper Tutor:\s*[^\n]*slides/notes|-[A-Za-z0-9]+-slides\b", text, re.I):
    print("slides")
elif re.search(r"^## Paper Tutor .*slides/notes", text, re.I | re.M):
    print("slides")
else:
    print("")' 2>/dev/null
}

paper_tutor_reading_id() {
  sudo docker exec hermes hermes kanban --board cs224n-study show "$1" 2>/dev/null \
    | python3 -c 'import re,sys
text=sys.stdin.read()
m=re.search(r"\b([A-Za-z]+[0-9]+-R[0-9]+)\b", text, re.I)
print(m.group(1).upper() if m else "")' 2>/dev/null
}

paper_tutor_source_check() {
  local lecture="$1"
  local token="$2"
  local reading_id="${3:-}"
  local py=".venv/bin/python"
  case "$token" in
    r01|r02)
      local upper
      upper="$(printf '%s' "$token" | tr '[:lower:]' '[:upper:]')"
      if [[ -z "$reading_id" ]]; then
        local prefix
        prefix="$(printf '%s' "$lecture" | sed -E 's/^([A-Za-z]+[0-9]+).*/\1/' | tr '[:lower:]' '[:upper:]')"
        reading_id="$prefix-$upper"
      fi
      printf '%s' "$py scripts/review_checks/check_required_sources.py --root . --lecture $lecture --kind paper --reading-id $reading_id"
      ;;
    slides)
      printf '%s' "$py scripts/review_checks/check_required_sources.py --root . --lecture $lecture --kind slides"
      ;;
    *)
      printf '%s' "$py scripts/review_checks/check_required_sources.py --root . --lecture $lecture --kind paper-tutor-integration"
      ;;
  esac
}

is_ready_for_review() {
  local outcome="$1"
  local summary="$2"
  [[ "$outcome" == "blocked" ]] || return 1
  printf '%s\n' "$summary" \
    | grep -Eiq 'review-required|ready_for_review|needs independent|可送.*review|可送审|待审|送审'
}

is_terminal_outcome() {
  [[ "$1" =~ ^(blocked|completed|failed|crashed|quarantined|done)$ ]]
}

wait_task_terminal() {
  local tid="$1"
  local interval=30
  echo "  轮询任务: $tid (每 ${interval}s)"
  while true; do
    local st
    st="$(task_outcome "$tid")"
    if is_terminal_outcome "$st"; then
      echo "  ✓ $tid 进入终态: $st"
      return 0
    fi
    sleep "$interval"
  done
}

wait_new_run_after_rework() {
  local tid="$1"
  local old_run_id="$2"
  local interval=10
  echo "  等待 $tid 产生返工新 run（old_run_id=$old_run_id）"
  while true; do
    local new_run_id
    new_run_id="$(latest_run_id "$tid")"
    if [[ "$new_run_id" != "0" && "$new_run_id" != "$old_run_id" ]]; then
      echo "  ✓ $tid 新 run 已出现: $new_run_id"
      return 0
    fi
    sleep "$interval"
  done
}

wait_tasks_terminal() {
  local tasks="$1"
  for tid in $tasks; do
    wait_task_terminal "$tid"
  done
}

unblock_for_rework() {
  local tid="$1"
  local reason="$2"
  sudo docker exec hermes hermes kanban --board cs224n-study comment "$tid" "$reason" --author orchestrator >/dev/null 2>&1 || true
  sudo docker exec hermes hermes kanban --board cs224n-study block "$tid" "$reason" >/dev/null 2>&1 || true
  sudo docker exec hermes hermes kanban --board cs224n-study unblock "$tid" --reason "$reason" >/dev/null 2>&1 || true
  sudo docker exec hermes hermes kanban --board cs224n-study dispatch >/dev/null 2>&1 || true
}

complete_after_review_pass() {
  local tid="$1"
  local reviewer="$2"
  sudo docker exec hermes hermes kanban --board cs224n-study complete \
    --summary "reviewer_pass: $reviewer; stage passed by independent reviewer; downstream still controlled by orchestrator/debug gate" \
    --result "reviewer_pass: $reviewer" \
    "$tid" >/dev/null 2>&1 || true
}

review_artifacts_for_stage() {
  local stage="$1"
  local lecture="$2"
  local target="${3:-}"
  case "$stage" in
    triage)
      printf '%s' "Lectures/$lecture/02-readings-map.md artifacts/*reading-triage*.md"
      ;;
    paper-tutor)
      local token=""
      [[ -n "$target" ]] && token="$(paper_tutor_target_token "$target")"
      case "$token" in
        r01|r02)
          local upper
          upper="$(printf '%s' "$token" | tr '[:lower:]' '[:upper:]')"
          printf '%s' "Papers/$lecture/*$upper*.md Lectures/$lecture/03-paper-bridge.partial-$token.md Lectures/$lecture/media-registry/paper-tutor-$token.json Assets/$lecture/papers/*$upper* artifacts/*paper-tutor*-$token*.md artifacts/*paper-tutor*$token*.md"
          ;;
        slides)
          printf '%s' "Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/03-paper-bridge.partial-slides.md Lectures/$lecture/media-registry/paper-tutor-slides-notes.json Assets/$lecture/slides Assets/$lecture/notes artifacts/*paper-tutor*slides*.md"
          ;;
        *)
          printf '%s' "Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/03-paper-bridge*.md Lectures/$lecture/media-registry/paper-tutor-*.json Papers/$lecture/*.md Assets/$lecture/papers Assets/$lecture/slides Assets/$lecture/notes artifacts/*paper-tutor*.md"
          ;;
      esac
      ;;
    paper-tutor-integration)
      printf '%s' "Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/03-paper-bridge*.md Lectures/$lecture/media-registry/paper-tutor-*.json Papers/$lecture/*.md Assets/$lecture/papers Assets/$lecture/slides Assets/$lecture/notes artifacts/*paper-tutor*.md"
      ;;
    capsules)
      local slug=""
      [[ -n "$target" ]] && slug="$(code_capsule_slug "$target")"
      if [[ -n "$slug" ]]; then
        printf '%s' "Lectures/$lecture/code-capsules/$slug.md Lectures/$lecture/00-concept-glossary.md Lectures/$lecture/media-registry/code-capsule-$slug.json Labs/$lecture/run-log.md Labs/$lecture/$slug.py Labs/$lecture/$slug.ipynb Labs/$lecture/outputs/$slug* artifacts/*code-capsule*$slug*.md"
      else
        printf '%s' "Lectures/$lecture/code-capsules Lectures/$lecture/00-concept-glossary.md Lectures/$lecture/media-registry/code-capsule-*.json Labs/$lecture/run-log.md Labs/$lecture/*.py Labs/$lecture/*.ipynb Labs/$lecture/outputs artifacts/*code-capsule*.md"
      fi
      ;;
    capsules-integration)
      printf '%s' "Lectures/$lecture/04-code-capsules.md Lectures/$lecture/code-capsules Lectures/$lecture/00-concept-glossary.md Lectures/$lecture/media-registry/code-capsule-*.json Labs/$lecture/run-log.md Labs/$lecture/*.py Labs/$lecture/*.ipynb Labs/$lecture/outputs artifacts/*code-capsule*.md"
      ;;
    deepresearch)
      local token=""
      local declared=""
      [[ -n "$target" ]] && token="$(deepresearch_target_token "$target")"
      [[ -n "$target" ]] && declared="$(declared_output_paths "$target" | tr '\n' ' ')"
      if [[ -n "$token" ]]; then
        if [[ -n "$declared" ]]; then
          printf '%s' "$declared Lectures/$lecture/02-readings-map.md Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/media-registry Papers/$lecture Assets/$lecture"
        else
          printf '%s' "DeepResearch/$lecture/*$token*.md artifacts/*course-deepresearch-eval-$lecture-*$token*.json Lectures/$lecture/02-readings-map.md Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/media-registry Papers/$lecture Assets/$lecture"
        fi
      else
        printf '%s' "DeepResearch/$lecture Lectures/$lecture/02-readings-map.md Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/media-registry Papers/$lecture Assets/$lecture artifacts/*course-deepresearch-eval-$lecture*.json"
      fi
      ;;
    deepresearch-integration)
      printf '%s' "DeepResearch/$lecture artifacts/*course-deepresearch-eval-$lecture-*.json Lectures/$lecture/02-readings-map.md Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/code-capsules Lectures/$lecture/04-code-capsules.md Lectures/$lecture/media-registry Papers/$lecture Assets/$lecture"
      ;;
    weaver)
      printf '%s' "Lectures/$lecture/00-课堂入口.md Lectures/$lecture/00-concept-glossary.md Lectures/$lecture/publish-manifest.json Lectures/$lecture/media-registry artifacts/*weaver*.md"
      ;;
    publisher-finalizer)
      printf '%s' "Lectures/$lecture/publish-manifest.json Lectures/$lecture/00-课堂入口.md Lectures/$lecture/04-code-capsules.md Lectures/$lecture/00-concept-glossary.md Lectures/$lecture/code-capsules Math/$lecture Papers/$lecture DeepResearch/$lecture artifacts/*publisher-finalizer*.md artifacts/*vault*publish*.json artifacts/*vault*publish*.txt"
      ;;
    *)
      printf '%s' "Lectures/$lecture artifacts/*$stage*.md"
      ;;
  esac
}

review_check_for_stage() {
  local stage="$1"
  local lecture="$2"
  local target="${3:-}"
  local original_stage="$stage"
  local py=".venv/bin/python"
  case "$stage" in
    *-integration)
      stage="${stage%-integration}"
      ;;
  esac
  case "$stage" in
    triage)
      printf '%s' "$py scripts/parse_readings_map.py Lectures/$lecture/02-readings-map.md --field core_readings --json >/tmp/cs224n-review-core.json && $py scripts/parse_readings_map.py Lectures/$lecture/02-readings-map.md --field code_capsules --json >/tmp/cs224n-review-capsules.json && $py scripts/parse_readings_map.py Lectures/$lecture/02-readings-map.md --field deepresearch_waypoints --json >/tmp/cs224n-review-deepresearch.json && $py scripts/parse_readings_map.py Lectures/$lecture/02-readings-map.md --field deepresearch_waypoints --needs-deepresearch-only >/tmp/cs224n-review-needs.txt && PYTHON_BIN=$py bash scripts/launch_paper_tutor.sh --lecture $lecture --parent $PARENT --dry-run >/tmp/cs224n-review-paper-tutor-dryrun.txt && PYTHON_BIN=$py bash scripts/launch_code_capsules.sh --lecture $lecture --parent $PARENT --dry-run >/tmp/cs224n-review-code-capsules-dryrun.txt && PYTHON_BIN=$py bash scripts/launch_deepresearch.sh --lecture $lecture --parent $PARENT --dry-run >/tmp/cs224n-review-deepresearch-dryrun.txt && $py - <<'PY'
import json
print('core_readings=', len(json.load(open('/tmp/cs224n-review-core.json'))))
print('code_capsules=', len(json.load(open('/tmp/cs224n-review-capsules.json'))))
print('deepresearch_waypoints=', len(json.load(open('/tmp/cs224n-review-deepresearch.json'))))
print('needs_deepresearch_only:')
print(open('/tmp/cs224n-review-needs.txt').read())
print('paper_tutor_dryrun_tail:')
print(open('/tmp/cs224n-review-paper-tutor-dryrun.txt').read()[-1200:])
print('code_capsules_dryrun_tail:')
print(open('/tmp/cs224n-review-code-capsules-dryrun.txt').read()[-1200:])
print('deepresearch_dryrun_tail:')
print(open('/tmp/cs224n-review-deepresearch-dryrun.txt').read()[-1200:])
PY"
      ;;
    paper-tutor)
      local token=""
      [[ -n "$target" ]] && token="$(paper_tutor_target_token "$target")"
      local reading_id=""
      [[ -n "$target" ]] && reading_id="$(paper_tutor_reading_id "$target")"
      local source_check
      source_check="$(paper_tutor_source_check "$lecture" "$token" "$reading_id")"
      if [[ "$original_stage" == "paper-tutor-integration" || -z "$token" ]]; then
        printf '%s' "$source_check && $py scripts/review_checks/check_links_headings.py --root . --paths Lectures/$lecture/02b-slides-notes-teaching-figures.md Lectures/$lecture/03-paper-bridge*.md Papers/$lecture --forbid-local-images && $py scripts/review_checks/check_media_registry.py --root . --lecture $lecture --prefix paper-tutor- --doc-path Lectures/$lecture/02b-slides-notes-teaching-figures.md --doc-path Lectures/$lecture/03-paper-bridge*.md --doc-path Papers/$lecture --asset-path Assets/$lecture/papers --asset-path Assets/$lecture/slides --asset-path Assets/$lecture/notes --require-for-assets --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5"
      elif [[ "$token" == "slides" ]]; then
        printf '%s' "$source_check && test -f Lectures/$lecture/03-paper-bridge.partial-slides.md && $py scripts/review_checks/check_links_headings.py --root . --paths Lectures/$lecture/02b-slides-notes-teaching-figures.md --forbid-local-images && $py scripts/review_checks/check_media_registry.py --root . --lecture $lecture --prefix paper-tutor-slides-notes --doc-path Lectures/$lecture/02b-slides-notes-teaching-figures.md --doc-path Lectures/$lecture/03-paper-bridge.partial-slides.md --asset-path Assets/$lecture/slides --asset-path Assets/$lecture/notes --require-for-assets --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5"
      else
        local upper
        upper="$(printf '%s' "$token" | tr '[:lower:]' '[:upper:]')"
        printf '%s' "$source_check && test -f Lectures/$lecture/03-paper-bridge.partial-$token.md && $py scripts/review_checks/check_links_headings.py --root . --paths Papers/$lecture/*$upper*.md --forbid-local-images && $py scripts/review_checks/check_media_registry.py --root . --lecture $lecture --prefix paper-tutor-$token --doc-path Papers/$lecture/*$upper*.md --doc-path Lectures/$lecture/03-paper-bridge.partial-$token.md --asset-path Assets/$lecture/papers/*$upper* --require-for-assets --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5"
      fi
      ;;
    capsules)
      local slug=""
      [[ -n "$target" ]] && slug="$(code_capsule_slug "$target")"
      local link_paths="Lectures/$lecture/code-capsules Lectures/$lecture/00-concept-glossary.md"
      if [[ "$original_stage" == "capsules-integration" ]]; then
        link_paths="Lectures/$lecture/04-code-capsules.md $link_paths"
      elif [[ -n "$slug" ]]; then
        link_paths="Lectures/$lecture/code-capsules/$slug.md Lectures/$lecture/00-concept-glossary.md"
      fi
      local registry_prefix="code-capsule-"
      local doc_paths="--doc-path Lectures/$lecture/code-capsules"
      if [[ "$original_stage" != "capsules-integration" && -n "$slug" ]]; then
        registry_prefix="code-capsule-$slug"
        doc_paths="--doc-path Lectures/$lecture/code-capsules/$slug.md"
      elif [[ "$original_stage" == "capsules-integration" ]]; then
        doc_paths="--doc-path Lectures/$lecture/code-capsules --doc-path Lectures/$lecture/04-code-capsules.md"
      fi
      local run_log_check="$py scripts/review_checks/check_code_capsule_run_log.py --root . --lecture $lecture"
      if [[ "$original_stage" != "capsules-integration" && -n "$slug" ]]; then
        run_log_check="$run_log_check --slug $slug --task-id $target"
      fi
      local notebook_check="$py scripts/review_checks/check_notebook_chinese.py --root . --paths Labs/$lecture/*.ipynb"
      if [[ "$original_stage" != "capsules-integration" && -n "$slug" ]]; then
        notebook_check="$py scripts/review_checks/check_notebook_chinese.py --root . --paths Labs/$lecture/$slug.ipynb"
      fi
      printf '%s' "$py scripts/review_checks/check_links_headings.py --root . --paths $link_paths --forbid-local-images && $py scripts/review_checks/check_media_registry.py --root . --lecture $lecture --prefix $registry_prefix $doc_paths --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5 && $run_log_check && $notebook_check && $py - <<'PY'
from pathlib import Path
bad = [p for p in [Path('Labs/$lecture/04-code-capsules.md')] if p.exists()]
if bad:
    print('forbidden_code_capsules_copies=', [str(p) for p in bad])
    raise SystemExit(2)
slug = '$slug'
integration = '$original_stage' == 'capsules-integration'
if integration:
    partials = sorted(Path('Lectures/$lecture/code-capsules').glob('*.md'))
else:
    if not slug:
        print('missing_code_capsule_slug_for_target=$target')
        raise SystemExit(2)
    partial = Path('Lectures/$lecture/code-capsules') / f'{slug}.md'
    if not partial.exists():
        print('missing_capsule_partial=', partial)
        raise SystemExit(2)
    partials = [partial]
print('capsule_partials=', [p.name for p in partials])
for p in partials:
    text = p.read_text(encoding='utf-8')
    if 'numeric_provenance' not in text:
        print('missing_numeric_provenance=', p)
        raise SystemExit(2)
if not integration and Path('Lectures/$lecture/04-code-capsules.md').exists():
    print('premature_merged_code_capsules_doc=Lectures/$lecture/04-code-capsules.md')
    raise SystemExit(2)
if integration and Path('Lectures/$lecture/04-code-capsules.md').exists():
    merged = Path('Lectures/$lecture/04-code-capsules.md').read_text(encoding='utf-8')
    if 'merge_code_capsules.py' not in merged:
        print('merged_doc_missing_generation_note')
        raise SystemExit(2)
PY"
      ;;
    deepresearch)
      local token=""
      local declared=""
      if [[ "$original_stage" != "deepresearch-integration" && -n "$target" ]]; then
        token="$(deepresearch_target_token "$target")"
        declared="$(declared_output_paths "$target" | tr '\n' ' ')"
      fi
      printf '%s' "$py - <<'PY'
from pathlib import Path
import subprocess, sys
token = '$token'
declared = '''$declared'''.split()
integration = '$original_stage' == 'deepresearch-integration'
if not token and not integration:
    print('missing_deepresearch_target_token_for_task=$target')
    sys.exit(2)
if integration:
    evals = sorted(Path('artifacts').glob('*course-deepresearch-eval-$lecture-*.json'))
    drafts = sorted(Path('DeepResearch/$lecture').glob('*.md')) + sorted(Path('Lectures/$lecture/deepresearch').glob('*.md'))
else:
    declared_paths = [Path(p) for p in declared]
    declared_drafts = [p for p in declared_paths if p.suffix == '.md' and 'DeepResearch/$lecture' in p.as_posix() and token in p.name]
    declared_evals = [p for p in declared_paths if p.suffix == '.json' and 'course-deepresearch-eval-$lecture' in p.name and token in p.name]
    if declared_paths:
        drafts = declared_drafts
        evals = declared_evals
        if len(drafts) != 1 or len(evals) != 1:
            print('invalid_declared_outputs_for_deepresearch_target=$target token=' + token)
            print('declared_paths=', [str(p) for p in declared_paths])
            print('declared_drafts=', [str(p) for p in drafts])
            print('declared_evals=', [str(p) for p in evals])
            sys.exit(2)
    else:
        evals = sorted(Path('artifacts').glob(f'*course-deepresearch-eval-$lecture-*{token}*.json'))
        drafts = sorted(Path('DeepResearch/$lecture').glob(f'*{token}*.md')) + sorted(Path('Lectures/$lecture/deepresearch').glob(f'*{token}*.md'))
        if len(drafts) != 1 or len(evals) != 1:
            print('ambiguous_deepresearch_outputs_require_declared_outputs=$target token=' + token)
            print('draft_candidates=', [str(p) for p in drafts])
            print('eval_candidates=', [str(p) for p in evals])
            sys.exit(2)
print('deepresearch_eval_candidates=', [str(p) for p in evals])
print('deepresearch_draft_candidates=', [str(p) for p in drafts])
if not evals:
    print('missing_deepresearch_eval_for_target=$target token=' + token)
    sys.exit(2)
if not drafts:
    print('missing_deepresearch_draft_for_target=$target token=' + token)
    sys.exit(2)
link_paths = [str(p) for p in drafts] + [
    'Lectures/$lecture/02-readings-map.md',
    'Lectures/$lecture/02b-slides-notes-teaching-figures.md',
    'Lectures/$lecture/code-capsules',
    'Lectures/$lecture/04-code-capsules.md',
    'Papers/$lecture',
    'Assets/$lecture',
]
user_docs = [str(p) for p in drafts]
rc = subprocess.call([sys.executable, 'scripts/review_checks/check_links_headings.py', '--root', '.', '--paths', *user_docs, '--forbid-local-images'])
if rc != 0:
    sys.exit(rc)
rc = subprocess.call([sys.executable, 'scripts/review_checks/check_links_headings.py', '--root', '.', '--paths', *link_paths])
if rc != 0:
    sys.exit(rc)
rc = subprocess.call([
    sys.executable, 'scripts/review_checks/check_media_registry.py',
    '--root', '.', '--lecture', '$lecture',
    '--doc-path', *user_docs,
    '--require-doc-remotes-known',
    '--min-attempts-when-blocked', '5',
    '--min-gap-seconds-when-blocked', '5',
])
if rc != 0:
    sys.exit(rc)
failed = False
for draft in drafts:
    matches = [p for p in evals if draft.stem in p.stem]
    if not matches:
        matches = evals if len(evals) == 1 and len(drafts) == 1 else []
    if not matches:
        print('missing_matching_eval_for_draft=', draft)
        failed = True
        continue
    eval_path = matches[-1]
    rc = subprocess.call([sys.executable, 'scripts/review_checks/check_eval_nodes_and_depth.py', '--eval', str(eval_path), '--draft', str(draft)])
    failed = failed or rc != 0
    density = subprocess.call([sys.executable, 'scripts/review_checks/check_deepresearch_density.py', str(draft)])
    failed = failed or density != 0
sys.exit(1 if failed else 0)
PY"
      ;;
    weaver)
      printf '%s' "$py scripts/review_checks/check_links_headings.py --root . --paths Lectures/$lecture/00-课堂入口.md Lectures/$lecture/00-concept-glossary.md Math/$lecture --forbid-local-images && $py scripts/review_checks/check_media_registry.py --root . --lecture $lecture --doc-path Lectures/$lecture/00-课堂入口.md --doc-path Lectures/$lecture/00-concept-glossary.md --doc-path Math/$lecture --require-doc-remotes-known --min-attempts-when-blocked 5 --min-gap-seconds-when-blocked 5 && $py scripts/review_checks/check_lecture_entry_richness.py --root . --entry Lectures/$lecture/00-课堂入口.md && $py scripts/review_checks/check_publish_manifest.py --root . --manifest Lectures/$lecture/publish-manifest.json"
      ;;
    publisher-finalizer)
      printf '%s' "$py scripts/review_checks/check_links_headings.py --root . --paths Lectures/$lecture/00-课堂入口.md Lectures/$lecture/04-code-capsules.md Lectures/$lecture/00-concept-glossary.md Lectures/$lecture/code-capsules Math/$lecture Papers/$lecture DeepResearch/$lecture --forbid-local-images && $py scripts/review_checks/check_lecture_entry_richness.py --root . --entry Lectures/$lecture/00-课堂入口.md && $py scripts/review_checks/check_notebook_chinese.py --root . --paths 'Labs/$lecture/*.ipynb' 'Lectures/$lecture/*.ipynb' && $py scripts/review_checks/check_publish_manifest.py --root . --manifest Lectures/$lecture/publish-manifest.json && $py scripts/review_checks/check_vault_publish.py --root . --evidence artifacts/$lecture-vault-read-evidence.json --required-path Hermes/Courses/CS224N-2025/Lectures/$lecture/00-课堂入口.md --required-path 'Hermes/Courses/CS224N-2025/CS224N-2025 $lecture 入口.md'"
      ;;
    *)
      printf '%s' "$py scripts/review_checks/check_links_headings.py --root . --paths Lectures/$lecture"
      ;;
  esac
}

review_once() {
  local stage="$1"
  local lecture="$2"
  local target="$3"
  local out reviewer reviewer_outcome verdict summary artifacts check_cmd

  echo "  派 reviewer 审批 $target ($stage)"
  artifacts="$(review_artifacts_for_stage "$stage" "$lecture" "$target")"
  check_cmd="$(review_check_for_stage "$stage" "$lecture" "$target")"
  # Reviewer 不能以被审 worker 为 parent：worker 此时通常停在 blocked/review-required，
  # 若挂到 target 下面会被依赖关系卡住。它通过 target_task 字段追查原任务。
  out="$(bash "$SCRIPT_DIR/launch_reviewer.sh" --stage "$stage" --lecture "$lecture" --target "$target" --parent "$PARENT" --artifacts "$artifacts" --check "$check_cmd" --run-tag "a$(date +%Y%m%d%H%M%S)-$$-$RANDOM" 2>&1)"
  echo "$out"
  reviewer="$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tail -1)"
  if [[ -z "$reviewer" ]]; then
    echo "  ✗ reviewer 派发失败：未解析到 reviewer task id"
    return 2
  fi

  echo "  等 reviewer $reviewer 完成..."
  wait_task_terminal "$reviewer"
  reviewer_outcome="$(task_outcome "$reviewer")"
  if [[ "$reviewer_outcome" != "completed" && "$reviewer_outcome" != "done" ]]; then
    echo "  ✗ reviewer 自身未完成: $reviewer_outcome（这是评审基础设施问题，不让 worker 背锅）"
    return 2
  fi
  summary="$(task_summary "$reviewer")"
  verdict="$(printf '%s\n' "$summary" | grep -Eio 'VERDICT:[[:space:]]*(PASS|BLOCK)' | head -1 | awk '{print toupper($2)}' || true)"
  if [[ "$verdict" == "PASS" ]]; then
    echo "  ✓ reviewer PASS: $reviewer"
    LAST_REVIEWER="$reviewer"
    return 0
  fi

  echo "  ✗ reviewer BLOCK/UNKNOWN: $reviewer"
  printf '%s\n' "$summary" | sed -n '1,12p'
  return 1
}

task_count() {
  local tasks="$1"
  local n=0
  local tid
  for tid in $tasks; do
    n=$((n + 1))
  done
  printf '%s' "$n"
}

create_stage_review_target() {
  local stage="$1"
  local lecture="$2"
  local tasks="$3"
  local tag="$4"
  local body json target
  body="Synthetic stage integration target for $lecture / $stage.

This is not a worker output. It exists so an independent reviewer can judge the set of sibling tasks as a stage-level whole.

Child tasks under integration review:
$tasks

Integration reviewer must check cross-task coverage, consistency, duplicate/conflicting claims, and whether the stage can safely hand off to downstream."
  json="$(sudo docker exec hermes hermes kanban --board cs224n-study create \
    "CS224N $lecture Stage Integration Target [$stage]" \
    --body "$body" \
    --assignee default \
    --parent "$PARENT" \
    --workspace dir:/workspace/cs224n-study \
    --priority 1 \
    --idempotency-key "cs224n-$lecture-stage-target-$stage-$tag" \
    --json)"
  target="$(printf '%s' "$json" | python3 -c 'import json,sys; o=json.load(sys.stdin); print(o.get("id") or o.get("task_id") or o.get("task",{}).get("id") or "")')"
  if [[ -z "$target" ]]; then
    echo "  ✗ stage integration target 创建失败" >&2
    return 1
  fi
  sudo docker exec hermes hermes kanban --board cs224n-study complete \
    --summary "synthetic stage integration target; child_tasks=$tasks" \
    --result "ready_for_stage_integration_review" \
    "$target" >/dev/null 2>&1 || true
  printf '%s' "$target"
}

prepare_stage_integration_artifacts() {
  local stage="$1"
  local lecture="$2"
  case "$stage" in
    capsules)
      echo "=== Prepare capsules integration artifacts: merge partials → 04-code-capsules.md ==="
      (cd "$HERMES_REPO" && .venv/bin/python scripts/merge_code_capsules.py --lecture "$lecture")
      ;;
  esac
}

create_stage_integration_repair_task() {
  local stage="$1"
  local lecture="$2"
  local tasks="$3"
  local reviewer="$4"
  local attempt="$5"
  local tag="$6"
  local artifacts="$7"
  local check_cmd="$8"
  local card out repair

  card="$REPO_ROOT/artifacts/$(date +%Y-%m-%d)-kanban-$lecture-$stage-integration-repair-$tag-attempt$attempt.md"
  cat > "$card" <<EOF
# CS224N $lecture Stage Integration Repair: $stage

你是 **stage integration repair worker**，不是普通内容生成 worker，也不是 reviewer。

## 为什么有这个任务

同一阶段的多个 sibling worker 已分别通过 scoped reviewer，但 stage integration reviewer 对整体交付判定为 BLOCK。过去编排器遇到这种情况会直接停住，因为 integration target 是 synthetic task，不能像普通 worker 一样 unblock 返工。你的职责是做**最小集成修复**，然后重新交给 integration reviewer。

## 输入

- lecture: $lecture
- stage: $stage
- child tasks: $tasks
- blocking reviewer: $reviewer
- artifact paths: $artifacts
- deterministic check command:

\`\`\`bash
$check_cmd
\`\`\`

## 允许修什么

- 修复 integration 层面的接口问题：partial bridge / merged index / wikilink heading / block id / manifest entry / media registry 映射不一致。
- 对 paper-tutor integration：优先修 \`Lectures/$lecture/03-paper-bridge.partial-*.md\`；只有为了解决精确链接时，才允许给对应 paper note 增加稳定 heading 或 Obsidian block id。禁止重写论文解释正文。
- 对 capsules integration：优先重新运行/修复 \`scripts/merge_code_capsules.py\` 产物和 sibling partial 接口；禁止改作业答案或伪造 run-log。
- 对 deepresearch integration：只修 bridge / handoff / evidence index 的一致性；如果某 waypoint 内容本身不足，写 scope_exceeded，不要替原 DeepResearch 大改。

## 禁止

- 不准为了过 gate 大面积改写上游 worker 正文。
- 不准删除证据、删除失败记录、绕过 deterministic check。
- 不准把本地图片路径写进用户可读 Markdown。
- 不准把任务直接标成 done / completed。

## 必做

1. 读取 blocking reviewer 任务 summary / context / log，定位 BLOCK 的具体文件和原因。
2. 读取 artifact paths 中相关产物。
3. 做最小修复。
4. 在容器环境或等价环境重新运行上面的 deterministic check command。
5. 写执行报告：\`artifacts/$(date +%Y-%m-%d)-stage-integration-repair-$lecture-$stage-attempt$attempt.md\`，包含 changed_files / check_result / remaining_risk。
6. 正常修完后停在 review-required：

\`\`\`bash
hermes kanban --board cs224n-study block <当前task_id> "review-required: ready_for_review=true downstream_allowed=false; outputs=artifacts/$(date +%Y-%m-%d)-stage-integration-repair-$lecture-$stage-attempt$attempt.md"
\`\`\`

如果发现问题超出 integration repair 范围，仍然 block，但 summary 写 \`scope_exceeded\` 和应回退的具体 child task。
EOF

  out="$(bash "$SCRIPT_DIR/create_cs224n_task_with_notify.sh" \
    --title "CS224N $lecture Stage Integration Repair [$stage] attempt $attempt" \
    --body-file "$card" \
    --parent "$PARENT" \
    --idempotency-key "cs224n-$lecture-stage-integration-repair-$stage-$tag-attempt$attempt" \
    --assignee cs224n \
    --priority 93 \
    --max-runtime 45m 2>&1)"
  echo "$out" >&2
  repair="$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tail -1)"
  if [[ -z "$repair" ]]; then
    echo "  ✗ integration repair task 派发失败" >&2
    return 1
  fi
  printf '%s' "$repair"
}

stage_integration_review() {
  local stage="$1"
  local lecture="$2"
  local tasks="$3"
  local count attempt tag target out reviewer reviewer_outcome summary verdict artifacts check_cmd repair repair_outcome repair_summary accepted_repairs
  count="$(task_count "$tasks")"
  if [[ "$count" -le 1 ]]; then
    echo "=== Stage integration $stage: 单任务阶段，跳过集合审查 ==="
    return 0
  fi

  accepted_repairs=""
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    tag="stage-a$(date +%Y%m%d%H%M%S)-$$-$RANDOM"
    echo "=== Stage integration $stage: $count 个子任务均已通过 scoped reviewer，派集合 reviewer (attempt $attempt/$MAX_ATTEMPTS) ==="
    sync_workspace_to_launch
    prepare_stage_integration_artifacts "$stage" "$lecture" || return 2
    target="$(create_stage_review_target "$stage" "$lecture" "$tasks" "$tag")" || return 2
    artifacts="$(review_artifacts_for_stage "$stage-integration" "$lecture")"
    check_cmd="$(review_check_for_stage "$stage-integration" "$lecture")"
    out="$(bash "$SCRIPT_DIR/launch_reviewer.sh" --stage "$stage-integration" --lecture "$lecture" --target "$target" --parent "$PARENT" --artifacts "$artifacts" --check "$check_cmd" --run-tag "$tag" 2>&1)"
    echo "$out"
    reviewer="$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tail -1)"
    if [[ -z "$reviewer" ]]; then
      echo "  ✗ stage integration reviewer 派发失败"
      return 2
    fi
    echo "  等 stage integration reviewer $reviewer 完成..."
    wait_task_terminal "$reviewer"
    reviewer_outcome="$(task_outcome "$reviewer")"
    if [[ "$reviewer_outcome" != "completed" && "$reviewer_outcome" != "done" ]]; then
      echo "  ✗ stage integration reviewer 自身未完成: $reviewer_outcome"
      return 2
    fi
    summary="$(task_summary "$reviewer")"
    verdict="$(printf '%s\n' "$summary" | grep -Eio 'VERDICT:[[:space:]]*(PASS|BLOCK)' | head -1 | awk '{print toupper($2)}' || true)"
    if [[ "$verdict" == "PASS" ]]; then
      echo "  ✓ stage integration reviewer PASS: $reviewer"
      for repair in $accepted_repairs; do
        if [[ "$(task_outcome "$repair")" == "blocked" ]]; then
          sudo docker exec hermes hermes kanban --board cs224n-study complete \
            --summary "integration repair accepted by reviewer $reviewer" \
            --result "stage_integration_pass" \
            "$repair" >/dev/null 2>&1 || true
        fi
      done
      return 0
    fi

    echo "  ✗ stage integration reviewer BLOCK/UNKNOWN: $reviewer"
    printf '%s\n' "$summary" | sed -n '1,16p'
    if [[ "$attempt" -gt "$MAX_REWORKS" ]]; then
      echo "  ✗ stage integration 已达返工上限，停止"
      return 1
    fi
    echo "  启动 stage integration repair worker，修复后重新评审"
    repair="$(create_stage_integration_repair_task "$stage" "$lecture" "$tasks" "$reviewer" "$attempt" "$tag" "$artifacts" "$check_cmd")" || return 2
    echo "  等 integration repair $repair 完成..."
    wait_task_terminal "$repair"
    repair_outcome="$(task_outcome "$repair")"
    repair_summary="$(task_summary "$repair")"
    if is_ready_for_review "$repair_outcome" "$repair_summary"; then
      echo "  ✓ integration repair $repair 停在 review-required，重新跑 stage integration reviewer"
      accepted_repairs="$accepted_repairs $repair"
      continue
    fi
    echo "  ✗ integration repair $repair 未停在 review-required: $repair_outcome"
    printf '%s\n' "$repair_summary" | sed -n '1,12p'
    return 1
  done
  return 1
}

gate_task_until_pass() {
  local stage="$1"
  local lecture="$2"
  local tid="$3"
  local attempt outcome summary reason old_run_id

  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    echo "=== Gate $stage / $tid / attempt $attempt/$MAX_ATTEMPTS (最多返工 $MAX_REWORKS 次) ==="
    wait_task_terminal "$tid"
    outcome="$(task_outcome "$tid")"
    summary="$(task_summary "$tid")"

    if is_ready_for_review "$outcome" "$summary"; then
      echo "  ✓ $tid 停在 review-required，派 reviewer 审批"
    elif [[ "$outcome" == "completed" || "$outcome" == "done" ]]; then
      echo "  ✗ $tid 被 worker 标为 $outcome；这是协议违规，不送 reviewer，不尝试在 completed 任务上返工"
      reason="protocol_violation: worker ended as $outcome instead of blocked/review-required. This run is invalid and must be archived/restarted with a fresh task id; completed tasks are not a reliable rework target."
      sudo docker exec hermes hermes kanban --board cs224n-study comment "$tid" \
        "$reason" \
        --author orchestrator >/dev/null 2>&1 || true
      return 2
    else
      reason="orchestrator: worker outcome=$outcome; rework request $attempt/$MAX_REWORKS"
      if [[ "$attempt" -gt "$MAX_REWORKS" ]]; then
        echo "  ✗ $tid worker 未完成且已达返工上限: $outcome"
        return 1
      fi
      echo "  ✗ $tid worker 未通过: $outcome，返工"
      old_run_id="$(latest_run_id "$tid")"
      unblock_for_rework "$tid" "$reason"
      wait_new_run_after_rework "$tid" "$old_run_id"
      continue
    fi

    # Review checks run from the launch repo, while workers write in the Hermes
    # workspace. Sync immediately before reviewer launch so Rule Gate sees the
    # worker's actual latest artifacts instead of stale/missing files.
    sync_workspace_to_launch

    LAST_REVIEWER=""
    set +e
    review_once "$stage" "$lecture" "$tid"
    local review_rc=$?
    set -e
    if [[ "$review_rc" -eq 0 ]]; then
      if [[ "$outcome" == "blocked" ]]; then
        complete_after_review_pass "$tid" "$LAST_REVIEWER"
        echo "  ✓ 已由 reviewer PASS 将原任务 $tid 标为 done"
      fi
      return 0
    fi
    if [[ "$review_rc" -eq 2 ]]; then
      echo "  ✗ reviewer 基础设施失败，停止编排；不把问题转嫁给 worker"
      return 1
    fi

    reason="orchestrator: reviewer BLOCK; rework request $attempt/$MAX_REWORKS"
    if [[ "$attempt" -gt "$MAX_REWORKS" ]]; then
      echo "  ✗ $tid reviewer 未通过且已达返工上限"
      return 1
    fi
    old_run_id="$(latest_run_id "$tid")"
    unblock_for_rework "$tid" "$reason"
    wait_new_run_after_rework "$tid" "$old_run_id"
  done
  return 1
}

gate_stage_until_pass() {
  local stage="$1"
  local lecture="$2"
  local tasks="$3"
  local tid
  if [[ -z "$tasks" ]]; then
    echo "=== Gate $stage: 无任务，视为跳过 ==="
    return 0
  fi
  echo "=== Gate $stage: 等待本阶段所有子任务到终态 ==="
  wait_tasks_terminal "$tasks"
  for tid in $tasks; do
    if [[ -n "$REUSE_TASKS" && "$stage" == "$STAGE" ]] && task_already_reviewer_passed "$tid"; then
      echo "  ✓ $tid 已由 scoped reviewer PASS，reuse 模式跳过单 worker gate"
      continue
    fi
    gate_task_until_pass "$stage" "$lecture" "$tid" || return 1
  done
  stage_integration_review "$stage" "$lecture" "$tasks" || return 1
}

run_stage() {
  local stage="$1"
  local label="$2"
  local dispatch_fn="$3"
  local mode_name="$4"
  local out tasks

  if [[ -n "$REUSE_TASKS" && "$stage" == "$STAGE" ]]; then
    echo "--- 复用已有 $label 任务进入 reviewer gate ---"
    tasks="$REUSE_TASKS"
    echo "reuse_tasks=$tasks"
  else
    echo "--- 创建 $label 阶段开始快照 ---"
    local snapshot_dir
    snapshot_dir="$(bash "$SCRIPT_DIR/snapshot_stage.sh" --lecture "$LECTURE" --stage "$stage" --run-tag "$RUN_TAG")"
    echo "stage_snapshot=$snapshot_dir"
    echo "--- 派 $label ---"
    out="$($dispatch_fn 2>&1)"
    echo "$out"
    tasks="$(echo "$out" | grep -oE "task=t_[a-z0-9]+" | cut -d= -f2 | tr '\n' ' ')"
  fi

  gate_stage_until_pass "$stage" "$LECTURE" "$tasks" || {
    echo "=== $label 未通过 reviewer gate，编排停止 ==="
    exit 1
  }
  sync_workspace_to_launch

  if [[ "$mode_name" == "debug" ]]; then
    echo ""
    echo "=========================================="
    echo "✓ $label 已通过 reviewer gate"
    echo "启动 debug UI: http://192.168.31.173:9120"
    echo "=========================================="
    if ! launch_debug_ui "$stage" "$LECTURE" "$tasks"; then
      echo "用户标记返修,停止"
      exit 1
    fi
  fi
  return 0
}

orchestrate_all() {
  orchestrate_from_stage "$1" "all"
}

orchestrate_from_stage() {
  local mode_name="$1"
  local start_stage="$2"
  local active="false"
  local matched="false"
  echo "=== ${mode_name^^} MODE: 从 $start_stage 开始（worker → reviewer gate → ${mode_name}）==="
  if [[ -n "$DRY_RUN" ]]; then
    echo "[dry-run] ${mode_name} 模式不支持 dry-run（需真投才能等/评审）"
    exit 1
  fi

  local spec stage label fn
  for spec in \
    "triage|Reading Triage|dispatch_triage" \
    "paper-tutor|Paper Tutor|dispatch_paper_tutor" \
    "capsules|Code Capsules|dispatch_capsules" \
    "deepresearch|DeepResearch|dispatch_deepresearch" \
    "weaver|Lecture Weaver|dispatch_weaver" \
    "publisher-finalizer|Publisher Finalizer|dispatch_publisher_finalizer"; do
    IFS='|' read -r stage label fn <<< "$spec"
    if [[ "$start_stage" == "all" || "$start_stage" == "$stage" ]]; then
      active="true"
      matched="true"
    fi
    if [[ "$active" == "true" ]]; then
      run_stage "$stage" "$label" "$fn" "$mode_name"
    fi
  done

  if [[ "$matched" != "true" ]]; then
    echo "未知 stage: $start_stage"
    usage
  fi

  echo "=== ${mode_name^^} MODE 完成: 从 $start_stage 开始的后续阶段全部通过 reviewer gate ==="
}

# 启动 debug UI(web server),等用户决定,返回 0=通过继续 / 1=返修停止
launch_debug_ui() {
  local stage="$1"
  local lecture="$2"
  local tasks="$3"  # 暂不用,未来可传给 UI 显示任务列表

  # 为 UI 准备一个小而准的展示目录；不要让 UI 猜不存在的 stage 子目录。
  local artifacts_dir="$REPO_ROOT/artifacts/debug-ui/$lecture-$stage"
  rm -rf "$artifacts_dir"
  mkdir -p "$artifacts_dir"
  case "$stage" in
    triage)
      cp -f "$REPO_ROOT/Lectures/$lecture/02-readings-map.md" "$artifacts_dir/" 2>/dev/null || true
      cp -f "$REPO_ROOT"/artifacts/*reading-triage*.md "$artifacts_dir/" 2>/dev/null || true
      cp -f "$REPO_ROOT"/artifacts/*reviewer*triage*.md "$artifacts_dir/" 2>/dev/null || true
      ;;
    paper-tutor)
      find "$REPO_ROOT/Lectures/$lecture" "$REPO_ROOT/Papers" "$REPO_ROOT/Assets" \
        -maxdepth 4 -type f \( -name '*paper*' -o -name '*bridge*' -o -name '*.md' -o -name '*.jsonl' \) \
        -exec cp -f {} "$artifacts_dir/" \; 2>/dev/null || true
      ;;
    capsules)
      find "$REPO_ROOT/Lectures/$lecture" "$REPO_ROOT/Labs/$lecture" \
        -maxdepth 4 -type f \( -name '*.md' -o -name '*.py' -o -name '*.ipynb' -o -name '*.txt' -o -name '*.json' \) \
        -exec cp -f {} "$artifacts_dir/" \; 2>/dev/null || true
      ;;
    deepresearch)
      find "$REPO_ROOT/DeepResearch/$lecture" "$REPO_ROOT/Lectures/$lecture" "$REPO_ROOT/artifacts" \
        -maxdepth 4 -type f \( -path "*/DeepResearch/$lecture/*" -o -name '*course-deepresearch*' -o -name '02-readings-map.md' -o -name '02b-slides-notes-teaching-figures.md' -o -name '04-code-capsules.md' \) \
        -exec cp -f {} "$artifacts_dir/" \; 2>/dev/null || true
      ;;
    weaver)
      cp -f "$REPO_ROOT/Lectures/$lecture/00-课堂入口.md" "$artifacts_dir/" 2>/dev/null || true
      cp -f "$REPO_ROOT/Lectures/$lecture/00-concept-glossary.md" "$artifacts_dir/" 2>/dev/null || true
      cp -f "$REPO_ROOT"/artifacts/*weaver*.md "$artifacts_dir/" 2>/dev/null || true
      ;;
    publisher-finalizer)
      cp -f "$REPO_ROOT/Lectures/$lecture/00-课堂入口.md" "$artifacts_dir/" 2>/dev/null || true
      cp -f "$REPO_ROOT/Lectures/$lecture/publish-manifest.json" "$artifacts_dir/" 2>/dev/null || true
      cp -f "$REPO_ROOT"/artifacts/*publisher-finalizer*.md "$artifacts_dir/" 2>/dev/null || true
      cp -f "$REPO_ROOT"/artifacts/*vault*publish* "$artifacts_dir/" 2>/dev/null || true
      ;;
    *)
      find "$REPO_ROOT/Lectures/$lecture" -maxdepth 2 -type f -exec cp -f {} "$artifacts_dir/" \; 2>/dev/null || true
      ;;
  esac

  local control_file="$REPO_ROOT/artifacts/debug-control-$stage.txt"
  local feedback_file="$REPO_ROOT/artifacts/debug-feedback-$stage.txt"
  rm -f "$control_file" "$feedback_file"

  # 后台起 Python debug UI server
  python3 "$SCRIPT_DIR/debug_ui.py" \
    --stage "$stage" \
    --lecture "$lecture" \
    --port 9120 \
    --artifacts-dir "$artifacts_dir" \
    --control-file "$control_file" \
    > /tmp/debug-ui-$stage.log 2>&1 &
  local ui_pid=$!

  # 等 server 启动
  sleep 2

  # 轮询控制文件,等用户决定
  echo "  等待用户在 UI 做决定(通过/返修)..."
  while true; do
    if [[ -f "$control_file" ]]; then
      local decision=$(head -1 "$control_file")
      if [[ "$decision" == "CONTINUE" ]]; then
        echo "  ✓ 用户通过,继续下一阶段"
        kill $ui_pid 2>/dev/null || true
        return 0
      elif [[ "$decision" == "FEEDBACK" ]]; then
        echo "  ✗ 用户标记返修"
        tail -n +2 "$control_file" > "$feedback_file"
        kill $ui_pid 2>/dev/null || true
        return 1
      fi
    fi
    sleep 1
  done
}

# --- dispatch ---
sync_repos
if [[ "$MODE" == "dispatch" ]]; then
  case "$STAGE" in
    triage)       dispatch_triage ;;
    paper-tutor)  dispatch_paper_tutor ;;
    capsules)     dispatch_capsules ;;
    deepresearch) dispatch_deepresearch ;;
    weaver)       dispatch_weaver ;;
    publisher-finalizer) dispatch_publisher_finalizer ;;
    all)          dispatch_triage; dispatch_paper_tutor; dispatch_capsules; dispatch_deepresearch; dispatch_weaver; dispatch_publisher_finalizer ;;
    *) echo "未知 stage: $STAGE"; usage ;;
  esac
elif [[ "$MODE" == "debug" || "$MODE" == "auto" ]]; then
  orchestrate_from_stage "$MODE" "$STAGE"
else
  echo "未知 mode: $MODE"; usage
fi

echo "=== run_lecture 完成: lecture=$LECTURE stage=$STAGE mode=$MODE ${DRY_RUN:-} ==="
