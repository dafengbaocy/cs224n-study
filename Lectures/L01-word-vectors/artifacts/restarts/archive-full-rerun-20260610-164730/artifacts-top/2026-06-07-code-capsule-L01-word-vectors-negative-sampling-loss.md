# Execution Report: Code Capsule negative-sampling-loss (WP05)

**Task**: t_45780d20
**Parent**: t_f684dfec
**Date**: 2026-06-10
**Worker**: cs224n profile

## Summary

Code capsule for WP05 (负采样目标函数 vs 全 softmax) completed. Demonstrates why negative sampling makes word2vec training feasible by comparing softmax loss (O(|V|·d)) with NS loss (O(k·d)) through actual computation.

## Changed Files

- `Labs/L01-word-vectors/negative-sampling-loss.py` — main script (pure numpy + matplotlib)
- `Labs/L01-word-vectors/negative-sampling-loss.ipynb` — Jupyter notebook (14 cells)
- `Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt` — captured stdout
- `Labs/L01-word-vectors/outputs/negative-sampling-loss-stderr.txt` — empty (no errors)
- `Labs/L01-word-vectors/outputs/negative-sampling-loss-comparison.png` — loss vs k + efficiency plot
- `Labs/L01-word-vectors/outputs/negative-sampling-loss-sigmoid-gradients.png` — sigmoid + gradient viz
- `Labs/L01-word-vectors/outputs/negative-sampling-loss-landscape.png` — loss landscape
- `Labs/L01-word-vectors/run-log.md` — shared run log (appended via flock)
- `Lectures/L01-word-vectors/code-capsules/negative-sampling-loss.md` — capsule partial
- `Lectures/L01-word-vectors/media-registry/code-capsule-negative-sampling-loss.json` — media registry

## Capsule Concept

负采样目标函数 vs 全 softmax (Notes §3.5 Eq.14-15)

## Real Output Summary

- Softmax loss = 9.411909 (|V|=10000, requires all 10000 exp() evaluations)
- NS loss k=5 = 4.299113 (only 6 dot products)
- NS loss ≠ softmax loss (different objective: binary classification vs probability matching)
- Positive sample gradient has IDENTICAL form in both: (σ(score) - 1) · v_c
- Gradient speedup at |V|=100K: 7.9x (12.538ms vs 1.586ms per step)
- k=5-20 recommended (Mikolov et al. 2013)

## Colab Link

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/negative-sampling-loss.ipynb

## Image Uploads

| Image | URL | Status |
|-------|-----|--------|
| comparison | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161831.png | uploaded |
| sigmoid-gradients | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161834.png | uploaded |
| landscape | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161838.png | uploaded |

## Run-log Path

`Labs/L01-word-vectors/run-log.md#run_id 20260610T082213Z__t_45780d20__negative-sampling-loss`

## Self-check Results

- [x] Capsule partial exists at `Lectures/L01-word-vectors/code-capsules/negative-sampling-loss.md`
- [x] Heading: `## negative-sampling-loss — 负采样目标函数 vs 全 softmax {#negative-sampling-loss}`
- [x] .py, .ipynb, stdout, stderr, outputs, run-log, Colab link all exist
- [x] Run-log has unique section with task_id: t_45780d20, capsule_slug: negative-sampling-loss
- [x] Key numeric values (9.411909, 4.299113, 7.9x) traceable to stdout
- [x] Glossary links use vault-root paths: `[[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]]`
- [x] Images use remote_url (not local paths)
- [x] Media registry written with correct schema (top-level `items`)
- [x] No modification to `04-code-capsules.md` or other capsule partials
- [x] `check_links_headings.py` verdict: pass (links=4, images=4, errors=0)
- [x] Capsule partial readable from vault (162 lines, heading + provenance intact)
- [x] Colab URL returns HTTP 200

## Integration Risks

- Concurrent worker collision: another worker wrote to the same .py file during first run. Resolved by rewriting and re-running. The other worker's outputs (efficiency-scaling, gradient-comparison, k-effect, softmax-probs) remain in the outputs directory but are NOT referenced in this capsule's partial.

## Requested Glossary Terms

None — all needed terms (softmax, skip-gram, dense-vector) already exist in glossary seed.

## Status

ready_for_review: true
downstream_allowed: false
