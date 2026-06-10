#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: skip-gram-shapes (WP03)

Concept: Skip-gram data flow: center/context pairs and U/V matrix shapes.
Official anchor: slides p25-p26 (window example); slides p28 (two vectors per word);
                 notes §3.2 (U,V in R^{|V| x d})
"""

import numpy as np
import json
import os

# 1. Toy corpus
corpus_text = [
    "banking crises into turning problems",
    "turning banking into crises",
    "problems into banking turning",
]
corpus_tokens = [sent.lower().split() for sent in corpus_text]

vocab_set = set()
for sent in corpus_tokens:
    vocab_set.update(sent)
vocab = sorted(vocab_set)
word2idx = {w: i for i, w in enumerate(vocab)}
idx2word = {i: w for i, w in enumerate(vocab)}
V = len(vocab)
d = 4

print("=" * 70)
print("CS224N L01 — Skip-gram Data Flow: Center/Context Pairs & U/V Matrix Shapes")
print("=" * 70)

print("\n## 1. Toy Corpus")
for i, sent in enumerate(corpus_tokens):
    print(f"  Sentence {i}: {' '.join(sent)}")

print(f"\n## 2. Vocabulary (|V| = {V})")
for w in vocab:
    print(f"  {word2idx[w]:2d} : {w}")

# 2. Generate skip-gram pairs (window=2)
window_size = 2
pairs = []
print(f"\n## 3. Skip-gram Center-Context Pairs (window={window_size})")
for sent in corpus_tokens:
    for t, center in enumerate(sent):
        for j in range(-window_size, window_size + 1):
            if j == 0:
                continue
            ctx_pos = t + j
            if 0 <= ctx_pos < len(sent):
                context = sent[ctx_pos]
                pairs.append((center, context))
                print(f"  center='{center}' (pos {t}) <- context='{context}' (pos {ctx_pos}, offset {j:+d})")

print(f"\n  Total training pairs: {len(pairs)}")

# 3. U and V matrices
print(f"\n## 4. Matrix Shapes (notes §3.2: U, V ∈ R^{{|V| x d}})")
np.random.seed(42)
V_matrix = np.random.randn(V, d).astype(np.float32) * 0.5
U_matrix = np.random.randn(V, d).astype(np.float32) * 0.5

print(f"  Vocabulary size |V| = {V}")
print(f"  Embedding dimension d = {d}")
print(f"  V matrix (center vectors):  shape = {V_matrix.shape}")
print(f"  U matrix (context vectors): shape = {U_matrix.shape}")

for w in vocab[:3]:
    idx = word2idx[w]
    print(f"    v_{w:10s} = [{', '.join(f'{x:+.4f}' for x in V_matrix[idx])}]")
    print(f"    u_{w:10s} = [{', '.join(f'{x:+.4f}' for x in U_matrix[idx])}]")

# 4. Softmax demo
center_word = "banking"
center_idx = word2idx[center_word]
v_c = V_matrix[center_idx]
scores = U_matrix @ v_c
scores_shifted = scores - np.max(scores)
exp_scores = np.exp(scores_shifted)
probs = exp_scores / np.sum(exp_scores)

print(f"\n## 5. Score Computation & Softmax (slides p28-p30)")
print(f"  Center word: '{center_word}' (idx={center_idx})")
print(f"  {'Word':>12s}  {'idx':>3s}  {'u_w^T v_c':>10s}  {'exp(score)':>12s}  {'P(o|c)':>8s}")
for i in range(V):
    w = idx2word[i]
    print(f"  {w:>12s}  {i:3d}  {scores[i]:+10.4f}  {exp_scores[i]:12.6f}  {probs[i]:8.4f}")
print(f"\n  Sum of probabilities: {np.sum(probs):.6f}")

# 5. Shape summary
print(f"\n## 6. Shape Summary Table")
print(f"  {'Component':<35s}  {'Shape':>15s}")
print(f"  {'V matrix (center vectors)':<35s}  {str(V_matrix.shape):>15s}")
print(f"  {'U matrix (context vectors)':<35s}  {str(U_matrix.shape):>15s}")
print(f"  {'Score vector (u_w^T v_c)':<35s}  {str(scores.shape):>15s}")
print(f"  {'Probability vector P(o|c)':<35s}  {str(probs.shape):>15s}")
print(f"  {'Training pairs (window=2)':<35s}  {len(pairs):>15d}")

# 6. Save outputs
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)

pairs_data = [{"center": c, "context": x} for c, x in pairs]
with open(os.path.join(output_dir, "skip-gram-shapes-pairs.json"), "w") as f:
    json.dump({"vocab": vocab, "V": V, "d": d, "window_size": window_size,
               "num_pairs": len(pairs), "pairs": pairs_data}, f, indent=2)

with open(os.path.join(output_dir, "skip-gram-shapes-shapes.json"), "w") as f:
    json.dump({"vocabulary_size": V, "embedding_dim": d,
               "V_matrix_shape": list(V_matrix.shape), "U_matrix_shape": list(U_matrix.shape),
               "score_vector_shape": list(scores.shape), "probability_vector_shape": list(probs.shape),
               "num_training_pairs": len(pairs), "prob_sum": float(np.sum(probs))}, f, indent=2)

# 7. Visualization
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax1 = axes[0]
context_words = set(x for c, x in pairs if c == center_word)
colors = ['#e74c3c' if idx2word[i] in context_words else '#3498db' for i in range(V)]
bars = ax1.bar(range(V), probs, color=colors, edgecolor='black', linewidth=0.5)
ax1.set_xlabel('Word index')
ax1.set_ylabel('P(o | c="banking")')
ax1.set_title('Softmax P(context | center="banking")')
ax1.set_xticks(range(V))
ax1.set_xticklabels(vocab, rotation=45, ha='right')
ax1.axhline(y=1.0/V, color='gray', linestyle='--', alpha=0.5)
for bar, prob in zip(bars, probs):
    if prob > 0.05:
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005,
                f'{prob:.3f}', ha='center', va='bottom', fontsize=8)

ax2 = axes[1]
ax2.axis('off')
v_rect = plt.Rectangle((0.05, 0.55), 0.25, 0.35, facecolor='#3498db', alpha=0.3, edgecolor='black', linewidth=1.5)
ax2.add_patch(v_rect)
ax2.text(0.175, 0.725, f'V matrix\n({V}x{d})', ha='center', va='center', fontsize=11, fontweight='bold')
ax2.text(0.175, 0.60, 'center vectors\nv_w', ha='center', va='center', fontsize=9, style='italic')
u_rect = plt.Rectangle((0.40, 0.55), 0.25, 0.35, facecolor='#e74c3c', alpha=0.3, edgecolor='black', linewidth=1.5)
ax2.add_patch(u_rect)
ax2.text(0.525, 0.725, f'U matrix\n({V}x{d})', ha='center', va='center', fontsize=11, fontweight='bold')
ax2.text(0.525, 0.60, 'context vectors\nu_w', ha='center', va='center', fontsize=9, style='italic')
ax2.text(0.82, 0.725, f'scores ({V},)', ha='center', va='center', fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f39c12', alpha=0.3))
ax2.text(0.82, 0.44, f'P(o|c) ({V},)', ha='center', va='center', fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#2ecc71', alpha=0.3))
ax2.text(0.92, 0.56, 'softmax', fontsize=9, style='italic')
ax2.text(0.5, 0.15, r'$P(o|c) = \frac{\exp(u_o^\top v_c)}{\sum_w \exp(u_w^\top v_c)}$',
        ha='center', va='center', fontsize=14, bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow'))
ax2.text(0.5, 0.02, 'slides p28; notes §3.2 Eq.4', ha='center', fontsize=8, color='gray')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "skip-gram-shapes-prob-and-matrices.png"), dpi=150, bbox_inches='tight')
plt.close()

print(f"\n  Saved outputs to {output_dir}")
print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
