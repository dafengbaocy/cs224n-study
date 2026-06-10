#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: skipgram-softmax
Waypoint WP03: Skip-gram softmax probability calculation P(o|c)

Official anchors:
  - Slides p27-30 (objective function, softmax)
  - Notes §3.2 (Eq.4 softmax, Eq.5 cross-entropy loss)

What this capsule demonstrates:
  1. Each word has TWO vectors: v_w (center) and u_w (context)
  2. Softmax formula: P(o|c) = exp(u_o^T v_c) / Σ_{w∈V} exp(u_w^T v_c)
  3. The three steps: dot product → exponentiation → normalization
  4. The computational bottleneck: denominator sums over ALL |V| words

This script uses numpy and matplotlib, both pre-installed in Google Colab.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import json
import os
import sys

# ============================================================
# 1. Setup: Mini vocabulary with d=4 dimensional vectors
# ============================================================
print("=" * 70)
print("CS224N L01 Code Capsule: skipgram-softmax")
print("Waypoint WP03: Skip-gram softmax probability P(o|c)")
print("=" * 70)

np.random.seed(42)  # reproducibility

# Mini vocabulary (6 words — small enough to trace by hand)
vocab = ["banking", "money", "river", "bank", "crisis", "water"]
V = len(vocab)
d = 4  # embedding dimension (toy example; real models use d=100-300)

print(f"\nVocabulary size |V| = {V}")
print(f"Embedding dimension d = {d}")
print(f"Words: {vocab}")

# Each word has TWO vectors:
#   v_w = center vector (when word is the center/input word)
#   u_w = context vector (when word is the context/output word)
# In real word2vec, these are separate parameter matrices.

# Center vectors V_matrix: each row is v_w for one word
V_matrix = np.array([
    [ 0.5,  0.8, -0.2,  0.3],   # banking
    [ 0.4,  0.7, -0.1,  0.2],   # money
    [-0.3,  0.1,  0.9,  0.6],   # river
    [ 0.2,  0.5,  0.4,  0.5],   # bank
    [-0.5,  0.6, -0.3,  0.1],   # crisis
    [-0.2,  0.0,  0.8,  0.7],   # water
], dtype=np.float64)

# Context vectors U_matrix: each row is u_w for one word
U_matrix = np.array([
    [ 0.6,  0.7, -0.3,  0.2],   # banking
    [ 0.5,  0.8, -0.2,  0.1],   # money
    [-0.4,  0.2,  0.8,  0.5],   # river
    [ 0.3,  0.6,  0.3,  0.4],   # bank
    [-0.6,  0.5, -0.4,  0.0],   # crisis
    [-0.3,  0.1,  0.7,  0.6],   # water
], dtype=np.float64)

print("\n--- Center vectors (v_w) ---")
for i, w in enumerate(vocab):
    print(f"  v_{w:>8s} = {V_matrix[i]}")

print("\n--- Context vectors (u_w) ---")
for i, w in enumerate(vocab):
    print(f"  u_{w:>8s} = {U_matrix[i]}")

# ============================================================
# 2. Softmax P(o|c) computation — step by step
# ============================================================
print("\n" + "=" * 70)
print("STEP-BY-STEP: Computing P(o|c) for center word 'banking'")
print("=" * 70)

center_idx = 0  # "banking"
v_c = V_matrix[center_idx]
center_word = vocab[center_idx]

print(f"\nCenter word c = '{center_word}'")
print(f"v_c = {v_c}")

# Step 1: Dot products u_w^T v_c for ALL words w in vocabulary
print("\n--- Step 1: Dot products (u_w^T · v_c) for all w ∈ V ---")
dot_products = np.zeros(V)
for i, w in enumerate(vocab):
    u_w = U_matrix[i]
    dot = np.dot(u_w, v_c)
    dot_products[i] = dot
    print(f"  u_{w:>8s}^T · v_{center_word} = {dot:.6f}")

# Step 2: Exponentiation exp(u_w^T v_c)
print("\n--- Step 2: Exponentiation exp(u_w^T · v_c) ---")
exp_scores = np.exp(dot_products)
for i, w in enumerate(vocab):
    print(f"  exp({dot_products[i]:.6f}) = {exp_scores[i]:.6f}")

# Step 3: Normalization — divide each exp by the sum (partition function Z)
Z = np.sum(exp_scores)  # partition function = denominator
print(f"\n--- Step 3: Normalization ---")
print(f"  Partition function Z = Σ exp(u_w^T · v_c) = {Z:.6f}")
print(f"  (This sum requires iterating over ALL |V|={V} words!)")

probs = exp_scores / Z
print(f"\n--- Final: P(o|c='{center_word}') for each context word o ---")
for i, w in enumerate(vocab):
    bar = "█" * int(probs[i] * 50)
    print(f"  P({w:>8s} | {center_word}) = {probs[i]:.6f}  {bar}")

print(f"\n  Sum of all probabilities = {np.sum(probs):.10f} (should be 1.0)")

# ============================================================
# 3. Compare P(o|c) for different center words
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON: P(o|c) for different center words")
print("=" * 70)

# Compute P(o|c) for center words: banking, river, crisis
test_centers = ["banking", "river", "crisis"]
all_probs = {}

for cw in test_centers:
    c_idx = vocab.index(cw)
    v_c = V_matrix[c_idx]
    dots = U_matrix @ v_c  # all dot products at once
    exp_s = np.exp(dots)
    Z_c = np.sum(exp_s)
    p = exp_s / Z_c
    all_probs[cw] = p
    print(f"\nP(o | c='{cw}'), Z={Z_c:.4f}:")
    for i, w in enumerate(vocab):
        bar = "█" * int(p[i] * 50)
        marker = " ← (same word)" if w == cw else ""
        print(f"  P({w:>8s}|{cw}) = {p[i]:.6f}  {bar}{marker}")

# ============================================================
# 4. Key insight: similar context → higher probability
# ============================================================
print("\n" + "=" * 70)
print("KEY INSIGHT: Semantic similarity affects P(o|c)")
print("=" * 70)

# banking and money have similar vectors → should get high P(o|c) when c=banking
p_banking = all_probs["banking"]
idx_money = vocab.index("money")
idx_river = vocab.index("river")
print(f"\nWhen c='banking':")
print(f"  P(money|banking)  = {p_banking[idx_money]:.6f}  (semantically similar)")
print(f"  P(river|banking)  = {p_banking[idx_river]:.6f}  (semantically different)")
print(f"  Ratio = {p_banking[idx_money]/p_banking[idx_river]:.2f}x")
print(f"\nThis is because v_banking and u_money have similar directions,")
print(f"so their dot product is larger → higher exp → higher probability.")

# ============================================================
# 5. Computational bottleneck: partition function Z
# ============================================================
print("\n" + "=" * 70)
print("COMPUTATIONAL BOTTLENECK: Partition function Z")
print("=" * 70)

vocab_sizes = [6, 100, 1000, 10000, 50000, 100000]
print(f"\nFor each center word, computing Z requires |V| dot products:")
print(f"  Z = Σ_{{w∈V}} exp(u_w^T · v_c)")
print(f"\n  |V| (vocab size)  |  Dot products per center word")
print(f"  {'─'*20}┼{'─'*30}")
for vs in vocab_sizes:
    print(f"  {vs:>16,}  |  {vs:>16,} dot products + exp + sum")

print(f"\nIn a corpus with T=10M tokens, total operations ≈ T × |V|:")
T = 10_000_000
for vs in [10000, 50000, 100000]:
    ops = T * vs
    print(f"  |V|={vs:>7,}: {ops:.2e} operations per epoch")

print(f"\nThis is why Negative Sampling (WP05) replaces the full softmax")
print(f"with k binary classifiers — reducing O(|V|) to O(k) per step.")

# ============================================================
# 6. Visualization: Plot 1 — Probability distribution
# ============================================================
print("\n" + "=" * 70)
print("Generating plots...")
print("=" * 70)

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)

# Plot 1: P(o|c) bar chart for center word "banking"
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(V)
width = 0.25

for idx, cw in enumerate(test_centers):
    offset = (idx - 1) * width
    bars = ax.bar(x + offset, all_probs[cw], width, label=f"c='{cw}'", alpha=0.85)

ax.set_xlabel('Context word o', fontsize=12)
ax.set_ylabel('P(o|c)', fontsize=12)
ax.set_title('Skip-gram Softmax: P(o|c) for different center words\n'
             '(Mini vocabulary, d=4, randomly initialized vectors)', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(vocab, fontsize=10)
ax.legend(fontsize=10)
ax.set_ylim(0, max(max(p) for p in all_probs.values()) * 1.2)

# Add value labels on bars for "banking"
for i, p_val in enumerate(all_probs["banking"]):
    ax.text(i - width, p_val + 0.005, f'{p_val:.3f}', ha='center', fontsize=7, color='#1f77b4')

plt.tight_layout()
plot1_path = os.path.join(output_dir, "skipgram-softmax-prob-distribution.png")
fig.savefig(plot1_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"  Saved: {plot1_path}")

# Plot 2: Three-step softmax visualization
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel A: Dot products
ax = axes[0]
colors = ['#2196F3' if i != center_idx else '#FF5722' for i in range(V)]
ax.barh(range(V), dot_products, color=colors, alpha=0.85)
ax.set_yticks(range(V))
ax.set_yticklabels(vocab, fontsize=9)
ax.set_xlabel('u_w^T · v_c', fontsize=11)
ax.set_title('① Dot Product\n(similarity score)', fontsize=11)
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
for i, dp in enumerate(dot_products):
    ax.text(dp + 0.01, i, f'{dp:.3f}', va='center', fontsize=8)

# Panel B: Exponentiation
ax = axes[1]
ax.barh(range(V), exp_scores, color=colors, alpha=0.85)
ax.set_yticks(range(V))
ax.set_yticklabels(vocab, fontsize=9)
ax.set_xlabel('exp(u_w^T · v_c)', fontsize=11)
ax.set_title('② Exponentiation\n(make positive, amplify)', fontsize=11)
for i, es in enumerate(exp_scores):
    ax.text(es + 0.01, i, f'{es:.3f}', va='center', fontsize=8)

# Panel C: Normalized probabilities
ax = axes[2]
ax.barh(range(V), probs, color=colors, alpha=0.85)
ax.set_yticks(range(V))
ax.set_yticklabels(vocab, fontsize=9)
ax.set_xlabel('P(o|c="banking")', fontsize=11)
ax.set_title('③ Normalize\n(divide by Z)', fontsize=11)
for i, p in enumerate(probs):
    ax.text(p + 0.005, i, f'{p:.4f}', va='center', fontsize=8)
ax.set_xlim(0, max(probs) * 1.3)

plt.suptitle('Softmax Three Steps: Dot Product → Exponentiation → Normalize\n'
             'Center word c = "banking"', fontsize=13, y=1.02)
plt.tight_layout()
plot2_path = os.path.join(output_dir, "skipgram-softmax-three-steps.png")
fig.savefig(plot2_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"  Saved: {plot2_path}")

# Plot 3: Vocabulary size vs computation cost
fig, ax = plt.subplots(figsize=(9, 5))
realistic_sizes = [100, 1000, 5000, 10000, 50000, 100000]
ops_per_step = realistic_sizes  # one dot product per word
ops_per_epoch = [T * vs for vs in realistic_sizes]

ax.semilogy(realistic_sizes, ops_per_epoch, 'bo-', linewidth=2, markersize=8)
ax.set_xlabel('Vocabulary size |V|', fontsize=12)
ax.set_ylabel('Operations per epoch (T=10M)', fontsize=12)
ax.set_title('Softmax Computational Cost vs Vocabulary Size\n'
             '(T × |V| dot products + exponentials per epoch)', fontsize=13)
ax.grid(True, alpha=0.3)

# Annotate key points
for vs in [10000, 50000, 100000]:
    ops = T * vs
    label = f'|V|={vs:,}\n{ops:.1e} ops'
    ax.annotate(label, (vs, ops), textcoords="offset points",
                xytext=(10, 10), fontsize=9,
                arrowprops=dict(arrowstyle='->', color='gray'))

ax.axvspan(30000, 100000, alpha=0.1, color='red', label='Typical production range')
ax.legend(fontsize=10)
plt.tight_layout()
plot3_path = os.path.join(output_dir, "skipgram-softmax-computation-cost.png")
fig.savefig(plot3_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"  Saved: {plot3_path}")

# ============================================================
# 7. Save structured output for provenance
# ============================================================
output_data = {
    "capsule": "skipgram-softmax",
    "waypoint": "WP03",
    "vocabulary": vocab,
    "vocab_size": V,
    "embedding_dim": d,
    "center_word": center_word,
    "dot_products": {w: round(float(dot_products[i]), 6) for i, w in enumerate(vocab)},
    "exp_scores": {w: round(float(exp_scores[i]), 6) for i, w in enumerate(vocab)},
    "partition_function_Z": round(float(Z), 6),
    "probabilities": {w: round(float(probs[i]), 6) for i, w in enumerate(vocab)},
    "probability_sum": round(float(np.sum(probs)), 10),
    "comparison": {
        cw: {w: round(float(all_probs[cw][i]), 6) for i, w in enumerate(vocab)}
        for cw in test_centers
    },
    "key_insight": {
        "P_money_given_banking": round(float(p_banking[idx_money]), 6),
        "P_river_given_banking": round(float(p_banking[idx_river]), 6),
        "ratio": round(float(p_banking[idx_money] / p_banking[idx_river]), 2),
    },
    "plots": {
        "prob_distribution": "outputs/skipgram-softmax-prob-distribution.png",
        "three_steps": "outputs/skipgram-softmax-three-steps.png",
        "computation_cost": "outputs/skipgram-softmax-computation-cost.png",
    }
}

json_path = os.path.join(output_dir, "skipgram-softmax-output.json")
with open(json_path, 'w') as f:
    json.dump(output_data, f, indent=2)
print(f"  Saved: {json_path}")

# Also save stdout to file for provenance
print("\n" + "=" * 70)
print("CAPSULE COMPLETE")
print("=" * 70)
print(f"\nAll outputs in: {output_dir}/")
print(f"  - skipgram-softmax-prob-distribution.png")
print(f"  - skipgram-softmax-three-steps.png")
print(f"  - skipgram-softmax-computation-cost.png")
print(f"  - skipgram-softmax-output.json")
