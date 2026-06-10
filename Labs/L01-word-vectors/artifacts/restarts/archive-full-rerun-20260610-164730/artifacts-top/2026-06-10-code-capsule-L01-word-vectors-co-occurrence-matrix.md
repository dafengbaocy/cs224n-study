# Code Capsule Execution Report: co-occurrence-matrix (WP02)

**Task ID**: t_64256cc7  
**Run ID**: 20260610T081828Z__t_64256cc7__co-occurrence-matrix  
**Date**: 2026-06-10  
**Worker**: cs224n profile  
**Status**: review-required  
**Ready for review**: true  
**Downstream allowed**: false  

---

## Summary

Built a code capsule demonstrating co-occurrence matrix construction and SVD dimensionality reduction for CS224N L01 WP02 (Distributional Semantics). The capsule shows how to build a co-occurrence matrix from a toy corpus (14 sentences, 15 words, 2 semantic clusters), apply log normalization per Notes §3.1, perform SVD to obtain 2D word embeddings, and visualize semantic cluster separation.

## Artifacts Produced

### Code & Notebook
- **Python script**: `Labs/L01-word-vectors/co-occurrence-matrix.py`
- **Jupyter notebook**: `Labs/L01-word-vectors/co-occurrence-matrix.ipynb`
- **Colab link**: https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/co-occurrence-matrix.ipynb

### Outputs
- **stdout**: `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt` (7516 bytes)
- **stderr**: `Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt` (empty — no errors)
- **Heatmap**: `Labs/L01-word-vectors/outputs/co-occurrence-matrix-heatmap.png` (105660 bytes)
  - Remote: https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-162027.png
- **2D embeddings**: `Labs/L01-word-vectors/outputs/co-occurrence-matrix-2d-embeddings.png` (90693 bytes)
  - Remote: https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-162035.png
- **Window comparison**: `Labs/L01-word-vectors/outputs/co-occurrence-matrix-window-comparison.png` (105025 bytes)
  - Remote: https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-162038.png
- **SVD coordinates JSON**: `Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-coordinates.json` (2094 bytes)

### Documentation
- **Capsule partial**: `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md`
- **Media registry**: `Lectures/L01-word-vectors/media-registry/code-capsule-co-occurrence-matrix.json`
- **Run-log entry**: `Labs/L01-word-vectors/run-log.md` (run_id: `20260610T081828Z__t_64256cc7__co-occurrence-matrix`)

### GitHub
- **Repository**: dafengbaocy/cs224n-study
- **Branch**: main
- **Notebook path in repo**: `co-occurrence-matrix.ipynb` (root — pushed by prior task 363d994)
- **Push status**: Notebook already present in public repo from prior run; current run updated local files

## Execution Details

### Run Environment
- **Hostname**: hermes container (Linux 6.18.18-trim)
- **Python**: 3.13.5 (venv: `/workspace/cs224n-study/.venv`)
- **Dependencies**: numpy 2.4.6, matplotlib 3.10.9, scipy 1.17.1
- **Exit code**: 0 (no errors)

### Corpus Design
- **Sentences**: 14 (6 Finance + 6 Nature + 2 bridge)
- **Vocabulary**: 15 words
- **Semantic clusters**:
  - Finance: banking, money, finance, economy, market, invest
  - Nature: river, lake, forest, mountain, valley, ocean
  - Bridge: the, flows, grows

### Key Parameters
- **Window size**: 2 (default), compared with 1 and 4
- **Normalization**: log(1 + x) per Notes §3.1
- **SVD dimensions**: k=2
- **Explained variance**: 75.3% (top-2)

### Key Results
**Matrix statistics**:
- Shape: 15×15
- Total co-occurrence count: 140
- Nonzero entries: 80
- Sparsity: 64.4%

**Cosine similarities** (log-normalized, window=2, 2D SVD):
- Same cluster:
  - banking ↔ money: 0.9910
  - banking ↔ finance: 0.9910
  - money ↔ finance: 1.0000
  - river ↔ lake: 0.9898
  - river ↔ forest: 0.9999
  - lake ↔ forest: 0.9875
- Cross cluster:
  - banking ↔ river: 0.2805
  - banking ↔ lake: 0.1406
  - money ↔ forest: 0.1642
- **Mean within-cluster: 0.9932**
- **Mean cross-cluster: 0.1508**
- **Difference: 0.8424**

**Window size comparison**:
| Window | Sparsity | Explained var | cos(banking,finance) | cos(banking,river) |
|---|---|---|---|---|
| 1 | 76.0% | 55.1% | 0.9920 | 0.4004 |
| 2 | 64.4% | 75.3% | 0.9910 | 0.2805 |
| 4 | 62.7% | 75.7% | 0.9908 | 0.2597 |

## Self-check Results

- [x] Capsule partial exists at `Lectures/L01-word-vectors/code-capsules/co-occurrence-matrix.md`
- [x] Heading: `## co-occurrence-matrix — 共现矩阵 + SVD 降维 {#co-occurrence-matrix}`
- [x] .py, .ipynb, stdout, outputs, run-log, Colab link all exist
- [x] Run-log has unique section with task_id: t_64256cc7, capsule_slug: co-occurrence-matrix
- [x] All numeric values in capsule partial traceable to stdout
- [x] Images uploaded to remote URLs, no local paths in capsule body
- [x] Media registry written with correct schema (top-level `items` list)
- [x] Glossary links use vault-root paths (e.g., `[[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]]`)
- [x] Did NOT write or modify `04-code-capsules.md`
- [x] Did NOT modify other capsule partials
- [x] Did NOT fabricate any numbers

## Integration Risks

- None detected. Other capsule partials (`one-hot-vs-dense.md`, `skipgram-softmax.md`, `cosine-similarity-analogy.md`) exist and were not modified.

## Requested Glossary Terms

- None. All needed terms (`co-occurrence-matrix`, `svd`, `dense-vector`, `cosine-similarity`) already exist in glossary seed.

## Colab Link Note

The notebook exists in the public repo at root path (`co-occurrence-matrix.ipynb`) from a prior task commit (363d994). The Colab link uses this path. Network issues prevented pushing the updated notebook to `L01-word-vectors/co-occurrence-matrix.ipynb` path during this run. The notebook content is functionally equivalent.

## Obsidian Vault Write

**Status**: BLOCKED — SSH to feiniu unavailable during this run. Could not execute `vault-write-hermes-container` to write capsule partial to Obsidian/LiveSync. All local artifacts are complete and correct; vault write should be retried by next worker or orchestrator.
