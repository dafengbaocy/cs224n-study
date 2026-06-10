
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

