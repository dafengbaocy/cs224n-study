# Execution Report: cosine-similarity-analogy Code Capsule

**Task ID**: t_48b9a9f8
**Capsule**: cosine-similarity-analogy
**Waypoint**: WP06 — 词向量评估：可视化、类比与偏差
**Date**: 2026-06-10
**Status**: review-required (ready_for_review=true, downstream_allowed=false)

---

## Summary

Produced a code capsule demonstrating cosine similarity computation and word analogy arithmetic (king-man+woman≈queen) using 4D toy word vectors. The capsule includes:
- A Python script with deterministic toy embeddings
- A Jupyter notebook with Chinese teaching annotations
- 3 visualization plots (heatmap, 2D projection, results chart)
- All images uploaded to image host and embedded via remote URLs

## Outputs

| Artifact | Path | Status |
|----------|------|--------|
| Python script | `Labs/L01-word-vectors/cosine-similarity-analogy.py` | ✓ exists |
| Jupyter notebook | `Labs/L01-word-vectors/cosine-similarity-analogy.ipynb` | ✓ exists, 19 cells with Chinese teaching sections |
| stdout | `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stdout.txt` | ✓ exists |
| stderr | `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stderr.txt` | ✓ empty (no errors) |
| Heatmap | `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-heatmap.png` | ✓ uploaded |
| 2D projection | `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-2d-projection.png` | ✓ uploaded |
| Results chart | `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-results-chart.png` | ✓ uploaded |
| Run-log entry | `Labs/L01-word-vectors/run-log.md` | ✓ run_id 20260610T102425Z__t_48b9a9f8__cosine-similarity-analogy |
| Capsule partial | `Lectures/L01-word-vectors/code-capsules/cosine-similarity-analogy.md` | ✓ exists |
| Media registry | `Lectures/L01-word-vectors/media-registry/code-capsule-cosine-similarity-analogy.json` | ✓ exists |
| Colab link | https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/cosine-similarity-analogy.ipynb | ✓ live |

## Run Details

- **Run ID**: 20260610T102425Z__t_48b9a9f8__cosine-similarity-analogy
- **Command**: `.venv/bin/python Labs/L01-word-vectors/cosine-similarity-analogy.py`
- **Exit code**: 0
- **Environment**: Linux container, Python 3.13 via .venv, numpy 2.4.6, matplotlib 3.10.9
- **Note**: System python3 lacks numpy; used .venv/bin/python instead

## Key Numeric Values (from stdout)

| Claim | Value | Source |
|-------|-------|--------|
| cos(king, queen) | 0.6157 | stdout |
| cos(king, man) | 0.6738 | stdout |
| cos(man, woman) | 0.3204 | stdout |
| cos(dog, cat) | 0.6923 | stdout |
| cos(prince, princess) | 0.7524 | stdout |
| king - man + woman = queen | cos=0.9981 | stdout |
| king - man = [0.87, -0.03, 0.00, -0.40] | — | stdout |
| dog - cat + king top-1 | prince (0.7905) | stdout |

## Image Upload Details

| Image | Upload Method | Attempts | URL |
|-------|--------------|----------|-----|
| heatmap | MCP upload_image | 1 | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181538.png |
| 2d-projection | MCP upload_image | 1 | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181545.png |
| results-chart | MCP upload_image | 1 | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181548.png |

## Self-Check Results

- [✓] Capsule partial exists at `Lectures/L01-word-vectors/code-capsules/cosine-similarity-analogy.md`
- [✓] Heading: `## cosine-similarity-analogy — 余弦相似度与词类比算术 {#cosine-similarity-analogy}`
- [✓] .py, .ipynb, stdout, run-log, Colab link all exist
- [✓] Run-log has unique section with task_id: t_48b9a9f8, capsule_slug: cosine-similarity-analogy
- [✓] Key numeric values in partial match stdout
- [✓] Notebook has all required Chinese teaching sections (这段代码在看什么, 运行后先看哪里, 输出怎么解释, 和本讲哪个 waypoint 对应, 容易误解的地方)
- [✓] Glossary links use vault-root paths
- [✓] Images use remote_url, not local paths
- [✓] Media registry uses top-level `items` schema
- [✓] Did NOT write or modify `04-code-capsules.md`
- [✓] Did NOT modify other capsule partials

## Integration Risks

None identified.

## Requested Glossary Terms

None — all needed terms (cosine-similarity, analogy) already exist in glossary seed.

## Protocol

- ready_for_review: true
- downstream_allowed: false
