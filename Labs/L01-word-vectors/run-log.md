
## run_id 20260610T035926Z__t_50c67b60__one-hot-vs-dense

task_id: t_50c67b60
capsule_slug: one-hot-vs-dense
timestamp: 2026-06-10T03:59:26Z
hostname: 0d61b5cf12fa
command: .venv/bin/python Labs/L01-word-vectors/one-hot-vs-dense.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt
stderr: Labs/L01-word-vectors/outputs/one-hot-vs-dense-stderr.txt (no errors)
outputs:
  - Labs/L01-word-vectors/outputs/one-hot-vs-dense-results.json
  - Labs/L01-word-vectors/outputs/one-hot-vs-dense-similarity-heatmap.png
  - Labs/L01-word-vectors/outputs/one-hot-vs-dense-2d-projection.png
notebook: Labs/L01-word-vectors/one-hot-vs-dense.ipynb
notes: Script ran cleanly with no errors. All 3 output files generated. Python venv with numpy 2.4.6 + matplotlib 3.10.9. No cells skipped, no cache used.

## run_id 20260610T035951Z__t_c7e1b594__skipgram-softmax

task_id: t_c7e1b594
capsule_slug: skipgram-softmax
timestamp: 2026-06-10T03:59:51Z
hostname: 0d61b5cf12fa
command: .venv/bin/python Labs/L01-word-vectors/skipgram-softmax.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/skipgram-softmax-stdout.txt
stderr: Labs/L01-word-vectors/outputs/skipgram-softmax-stderr.txt (empty — no errors)
outputs: Labs/L01-word-vectors/outputs/skipgram-softmax-prob-distribution.png, Labs/L01-word-vectors/outputs/skipgram-softmax-dot-product-heatmap.png, Labs/L01-word-vectors/outputs/skipgram-softmax-partition-cost.png
notebook: Labs/L01-word-vectors/skipgram-softmax.ipynb

Notes:
- No errors. Script ran cleanly with numpy 2.4.6 + matplotlib 3.10.9.
- All cells executed; no cells skipped.
- No cache used; all outputs freshly generated.
- Mini vocabulary (10 words, d=4) demonstrates softmax P(o|c) computation.
- Partition function Z=18.273793 computed over all 10 words.
- Cross-entropy loss for observed word 'problems': 1.875468.


## run_id 20260610T040115Z__t_67005255__negative-sampling-loss

task_id: t_67005255
capsule_slug: negative-sampling-loss
timestamp: 2026-06-10T04:01:15Z
hostname: 0d61b5cf12fa
command: .venv/bin/python Labs/L01-word-vectors/negative-sampling-loss.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt
stderr: Labs/L01-word-vectors/outputs/negative-sampling-loss-stderr.txt (empty — no errors)
outputs:
  - Labs/L01-word-vectors/outputs/negative-sampling-loss-softmax-probs.png
  - Labs/L01-word-vectors/outputs/negative-sampling-loss-efficiency-scaling.png
  - Labs/L01-word-vectors/outputs/negative-sampling-loss-k-effect.png
  - Labs/L01-word-vectors/outputs/negative-sampling-loss-gradient-comparison.png
  - Labs/L01-word-vectors/outputs/negative-sampling-loss-summary.json
notebook: Labs/L01-word-vectors/negative-sampling-loss.ipynb

Notes on run:
- Used .venv/bin/python (has numpy/matplotlib); Colab also has both pre-installed.
- No errors, no skipped cells.
- k=20 uses replace=True because toy vocab (12 words) has only 11 available negatives.
- Efficiency test uses realistic d=300, |V| up to 100,000.

## run_id 20260610T040413Z__t_d8fef150__co-occurrence-matrix

task_id: t_d8fef150
capsule_slug: co-occurrence-matrix
timestamp: 2026-06-10T04:04:13Z
hostname: 0d61b5cf12fa
command: python Labs/L01-word-vectors/co-occurrence-matrix.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt
stderr: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt (empty — no errors)
outputs: Labs/L01-word-vectors/outputs/co-occurrence-matrix-overview.png, Labs/L01-word-vectors/outputs/co-occurrence-matrix-2d-embeddings.png
notebook: Labs/L01-word-vectors/co-occurrence-matrix.ipynb
colab_url: https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/co-occurrence-matrix.ipynb

Notes:
- Script ran without errors on first attempt.
- No cells skipped; all code executed sequentially.
- No cached results; fresh run from source.
- Corpus: 14 sentences, 105 tokens, |V|=32.
- Window=2, log-normalized SVD to 2D.
- Key finding: same-cluster cosine similarities (banking-money=0.9638, river-lake=0.9911) are generally higher than cross-cluster (finance-mountain=0.6404), demonstrating distributional semantics.
- Toy corpus limitation: function words (the, and) still dominate; cross-cluster similarities remain high due to small corpus size.

## run_id 20260610T040425Z__t_dff9aa12__cosine-similarity-analogy

task_id: t_dff9aa12
capsule_slug: cosine-similarity-analogy
timestamp: 2026-06-10T04:04:25Z
hostname: 0d61b5cf12fa
command: .venv/bin/python Labs/L01-word-vectors/cosine-similarity-analogy.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stdout.txt
stderr: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stderr.txt
outputs: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-heatmap.png, Labs/L01-word-vectors/outputs/cosine-similarity-analogy-2d-projection.png, Labs/L01-word-vectors/outputs/cosine-similarity-analogy-results-chart.png
notebook: Labs/L01-word-vectors/cosine-similarity-analogy.ipynb
notes: Clean run, no errors. Toy 4D vectors designed with orthogonal semantic features (royalty/maleness/femaleness/youth). Classic analogy king-man+woman=queen achieves cos=0.9981. All 3 plots generated successfully.
<<<<<<< HEAD
=======

## run_id 20260610T080907Z__t_832bffea__skipgram-softmax

task_id: t_832bffea
capsule_slug: skipgram-softmax
timestamp: 2026-06-10T08:09:07Z
hostname: 0d61b5cf12fa
command: .venv/bin/python Labs/L01-word-vectors/skipgram-softmax.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/skipgram-softmax-stdout.txt
stderr: Labs/L01-word-vectors/outputs/skipgram-softmax-stderr.txt (empty — no errors)
outputs:
  - Labs/L01-word-vectors/outputs/skipgram-softmax-prob-distribution.png
  - Labs/L01-word-vectors/outputs/skipgram-softmax-three-steps.png
  - Labs/L01-word-vectors/outputs/skipgram-softmax-computation-cost.png
  - Labs/L01-word-vectors/outputs/skipgram-softmax-output.json
notebook: Labs/L01-word-vectors/skipgram-softmax.ipynb
notes: |
  Script ran cleanly with exit code 0. No errors or warnings.
  numpy seed=42 for reproducibility. Mini vocabulary of 6 words, d=4.
  All three plots generated successfully.
  Key output values: P(money|banking)=0.251396, P(river|banking)=0.091563, ratio=2.75x.
  Partition function Z=10.388761 for center word 'banking'.
  Previous run (t_c7e1b594) had different output file names; this revision supersedes it.


## run_id 20260610T081806Z__t_18fe1985__cosine-similarity-analogy

task_id: t_18fe1985
capsule_slug: cosine-similarity-analogy
timestamp: 2026-06-10T08:18:06Z
hostname: 0d61b5cf12fa
command: .venv/bin/python cosine-similarity-analogy.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stdout.txt
stderr: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stderr.txt (empty — no errors)
outputs: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-heatmap.png, Labs/L01-word-vectors/outputs/cosine-similarity-analogy-2d-projection.png, Labs/L01-word-vectors/outputs/cosine-similarity-analogy-results-chart.png
notebook: Labs/L01-word-vectors/cosine-similarity-analogy.ipynb
notes: Clean run, no errors. Toy 4D vectors with orthogonal semantic features (royalty/maleness/femaleness/youth). Classic analogy king-man+woman=queen achieves cos=0.9981. All 6 analogy tests pass. 2 failure cases demonstrated (cross-domain, no-relation). 3 plots generated. No cells skipped, no cache used.

## run_id 20260610T081828Z__t_64256cc7__co-occurrence-matrix

task_id: t_64256cc7
capsule_slug: co-occurrence-matrix
timestamp: 2026-06-10T08:18:28Z
hostname: 0d61b5cf12fa
environment: Python 3.13.5, venv /workspace/cs224n-study/.venv, numpy 2.4.6, matplotlib 3.10.9, scipy 1.17.1
command: .venv/bin/python Labs/L01-word-vectors/co-occurrence-matrix.py
workdir: /workspace/cs224n-study
exit_code: 0
stderr: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt (empty)
stdout: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt
outputs:
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-heatmap.png (105660 bytes)
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-2d-embeddings.png (90693 bytes)
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-window-comparison.png (105025 bytes)
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-coordinates.json (2094 bytes)
notebook: Labs/L01-word-vectors/co-occurrence-matrix.ipynb
notes: |
  No errors. Script ran once, all cells executed.
  Corpus: 14 sentences (6 finance + 6 nature + 2 bridge), 15 words vocabulary.
  Window size = 2 (default), compared with 1, 2, 4.
  Matrix: 15x15, 64.4% sparse, 140 total co-occurrence count.
  SVD k=2 explained variance: 75.3%.
  Within-cluster cosine mean: 0.9932, cross-cluster: 0.1508.
  No cells skipped. No cache used.
>>>>>>> 4f19d35 (Add one-hot-vs-dense capsule (WP02))
