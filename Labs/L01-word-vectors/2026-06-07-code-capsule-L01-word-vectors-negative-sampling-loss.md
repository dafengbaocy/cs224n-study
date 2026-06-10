# Execution Report: Code Capsule negative-sampling-loss (WP05)

**task_id**: t_9ab44084
**capsule_slug**: negative-sampling-loss
**run_id**: 20260610T102037Z__t_9ab44084__negative-sampling-loss
**timestamp**: 2026-06-10T10:20:37Z
**hostname**: 0d61b5cf12fa
**status**: ready_for_review: true, downstream_allowed: false

## Concept

负采样目标函数 vs 全 Softmax (Notes §3.5 Eq.14-15; R02 Section 3)

## Changed Files

| File | Action |
|------|--------|
| `Labs/L01-word-vectors/negative-sampling-loss.py` | Created — core computation (pure stdlib) |
| `Labs/L01-word-vectors/negative-sampling-loss-plots.py` | Created — matplotlib plot generation |
| `Labs/L01-word-vectors/negative-sampling-loss.ipynb` | Created — Chinese teaching notebook |
| `Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt` | Created — run stdout |
| `Labs/L01-word-vectors/outputs/negative-sampling-loss-stderr.txt` | Created — empty (no errors) |
| `Labs/L01-word-vectors/outputs/negative-sampling-loss-output.json` | Created — structured output |
| `Labs/L01-word-vectors/outputs/negative-sampling-loss-comparison.png` | Created — loss & computation bar chart |
| `Labs/L01-word-vectors/outputs/negative-sampling-loss-scaling.png` | Created — real-world scaling plot |
| `Labs/L01-word-vectors/outputs/negative-sampling-loss-gradient.png` | Created — gradient analysis plot |
| `Labs/L01-word-vectors/run-log.md` | Appended (flock) — run entry |
| `Lectures/L01-word-vectors/code-capsules/negative-sampling-loss.md` | Created — capsule partial |
| `Lectures/L01-word-vectors/media-registry/code-capsule-negative-sampling-loss.json` | Created — media registry |

## Outputs Summary

- **Softmax loss** = 1.390153 (P(money|banking) = 0.249037, 6 dot products)
- **NS loss (k=5)** = 1.564948 (6 dot products, gradient cosine vs softmax = -0.919196)
- **Real-world scaling**: |V|=100K, k=5 → 16,667x speedup
- **Key insight**: NS reframes multi-class as binary classification (NCE)

## Colab Link

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/negative-sampling-loss.ipynb

## Image Uploads

| Image | URL | Status |
|-------|-----|--------|
| comparison | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181803.png | uploaded (1 attempt) |
| scaling | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181807.png | uploaded (1 attempt) |
| gradient | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181810.png | uploaded (1 attempt) |

## Self-check Results

- [x] Capsule partial exists at `Lectures/L01-word-vectors/code-capsules/negative-sampling-loss.md`
- [x] Heading: `## negative-sampling-loss — 负采样目标函数 vs 全 Softmax {#negative-sampling-loss}`
- [x] .py, .ipynb, stdout, run-log, Colab link all present
- [x] Run-log entry has unique task_id/capsule_slug/run_id with command/exit_code/stdout/outputs
- [x] Key numeric values traceable to stdout/output files
- [x] `check_links_headings.py` returns 0 errors (pass)
- [x] No local image paths in capsule partial (all use remote_url)
- [x] Glossary links use vault-root paths
- [x] Did NOT write/modify `04-code-capsules.md`
- [x] Did NOT modify other capsule partials
- [x] Notebook uses Chinese teaching content throughout

## Integration Risks

None detected.

## Requested Glossary Terms

None — all linked terms already exist in seed glossary:
- softmax, skip-gram

## Run-log Path

`Labs/L01-word-vectors/run-log.md#run_id 20260610T102037Z__t_9ab44084__negative-sampling-loss`
