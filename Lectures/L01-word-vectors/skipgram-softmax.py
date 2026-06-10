#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: skipgram-softmax (WP03)

Demonstrates Skip-gram softmax probability calculation P(o|c).

Official anchors:
  - Slides p27-30 (objective function, softmax)
  - Notes §3.2 (Eq.4 softmax, Eq.5 cross-entropy loss)

Key formula (Notes Eq.4 / Slides p28):
  P(o|c) = exp(u_o^T v_c) / Σ_{w∈V} exp(u_w^T v_c)

This script:
  1. Defines a mini vocabulary with hand-crafted vectors
  2. Computes dot products between center word v_c and all context vectors u_w
  3. Applies softmax to get P(o|c) for every word in vocabulary
  4. Visualizes the probability distribution
  5. Demonstrates the computational cost of the denominator (partition function)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import json
from datetime import datetime, timezone

# ─── Reproducibility ─────────────────────────────────────────────
np.random.seed(42)

# ─── Mini Vocabulary ─────────────────────────────────────────────
# A small vocabulary around finance/banking theme
# This mirrors the Slides p25 example where "banking" is the center word
VOCAB = [
    "banking",      # 0 - center word in our example
    "crises",       # 1
    "into",         # 2
    "turning",      # 3
    "problems",     # 4
    "money",        # 5
    "economy",      # 6
    "policy",       # 7
    "cat",          # 8 - unrelated word (should get low P)
    "dog",          # 9 - unrelated word (should get low P)
]

VOCAB_SIZE = len(VOCAB)
DIM = 4  # Small dimension for transparency

# ─── Word Vectors ────────────────────────────────────────────────
# Center word vectors (v) and context word vectors (u)
# In real word2vec, these are learned; here we craft them to show the concept.
# Finance-related words are clustered; unrelated words are far away.

# Center vectors V (each row = v_w for word w when it's the center word)
V = np.array([
    [ 0.8,  0.6, -0.3,  0.1],   # banking
    [ 0.5,  0.7, -0.5,  0.2],   # crises
    [ 0.3,  0.2,  0.8, -0.1],   # into
    [ 0.4,  0.3,  0.6,  0.3],   # turning
    [ 0.6,  0.8, -0.4,  0.1],   # problems
    [ 0.7,  0.5, -0.2,  0.3],   # money
    [ 0.9,  0.4, -0.1,  0.2],   # economy
    [ 0.6,  0.3,  0.1,  0.4],   # policy
    [-0.8, -0.7,  0.5, -0.3],   # cat (unrelated)
    [-0.7, -0.9,  0.4, -0.2],   # dog (unrelated)
], dtype=np.float64)

# Context vectors U (each row = u_w for word w when it's a context word)
# These are DIFFERENT from V — each word has TWO vectors (Slides p28)
U = np.array([
    [ 0.7,  0.5, -0.2,  0.2],   # banking (as context)
    [ 0.6,  0.8, -0.6,  0.1],   # crises (as context)
    [ 0.2,  0.1,  0.7, -0.2],   # into (as context)
    [ 0.3,  0.4,  0.5,  0.2],   # turning (as context)
    [ 0.5,  0.9, -0.3,  0.0],   # problems (as context)
    [ 0.8,  0.4, -0.1,  0.3],   # money (as context)
    [ 0.9,  0.3,  0.0,  0.1],   # economy (as context)
    [ 0.5,  0.2,  0.2,  0.5],   # policy (as context)
    [-0.9, -0.6,  0.4, -0.4],   # cat (as context, unrelated)
    [-0.6, -0.8,  0.3, -0.1],   # dog (as context, unrelated)
], dtype=np.float64)

# ─── Softmax Function ────────────────────────────────────────────
def softmax(scores):
    """
    Softmax: R^n -> (0,1)^n
    Slides p30: ① Dot product → ② Exponentiation → ③ Normalize
    
    Numerically stable version: subtract max before exp.
    """
    scores = scores - np.max(scores)  # numerical stability
    exp_scores = np.exp(scores)
    return exp_scores / np.sum(exp_scores)

# ─── Compute P(o|c) ─────────────────────────────────────────────
# Pick "banking" as center word (index 0)
center_idx = 0
center_word = VOCAB[center_idx]
v_c = V[center_idx]  # center vector for "banking"

print("=" * 70)
print("CS224N L01 — Code Capsule: skipgram-softmax (WP03)")
print("=" * 70)
print()
print(f"Center word: '{center_word}' (index {center_idx})")
print(f"Center vector v_{center_word} = {v_c}")
print(f"Vocabulary size |V| = {VOCAB_SIZE}")
print(f"Vector dimension d = {DIM}")
print()

# Step 1: Compute dot products u_w^T v_c for ALL words w in V
print("─" * 70)
print("Step 1: Dot products u_w^T v_c (Slides p30: ① Dot product)")
print("─" * 70)
dot_products = np.zeros(VOCAB_SIZE)
for i, word in enumerate(VOCAB):
    u_w = U[i]
    dot = np.dot(u_w, v_c)
    dot_products[i] = dot
    print(f"  u_{word:>10s}^T v_{center_word:<8s} = {dot:+.6f}")

print()

# Step 2: Exponentiate (Slides p30: ② Exponentiation)
print("─" * 70)
print("Step 2: Exponentiation exp(u_w^T v_c) (Slides p30: ② Exponentiation)")
print("─" * 70)
exp_scores = np.exp(dot_products)
for i, word in enumerate(VOCAB):
    print(f"  exp({dot_products[i]:+.6f}) = {exp_scores[i]:.6f}")

print()

# Step 3: Normalize — THE PARTITION FUNCTION (Slides p30: ③ Normalize)
print("─" * 70)
print("Step 3: Partition function Z = Σ exp(u_w^T v_c) (Slides p30: ③ Normalize)")
print("─" * 70)
partition = np.sum(exp_scores)
print(f"  Z = Σ_{{w∈V}} exp(u_w^T v_c) = {partition:.6f}")
print(f"  (We had to compute exp for ALL {VOCAB_SIZE} words!)")
print()

# Step 4: Final probabilities P(o|c)
print("─" * 70)
print("Step 4: P(o|c) = exp(u_o^T v_c) / Z")
print("─" * 70)
probs = softmax(dot_products)
print()
print(f"  {'Word':>12s}  {'dot product':>12s}  {'exp(score)':>12s}  {'P(o|c)':>10s}  {'bar'}")
print(f"  {'─'*12}  {'─'*12}  {'─'*12}  {'─'*10}  {'─'*20}")
for i, word in enumerate(VOCAB):
    bar = "█" * int(probs[i] * 50)
    marker = " ← context" if i in [1, 2, 3, 4] else ""
    print(f"  {word:>12s}  {dot_products[i]:>+12.6f}  {exp_scores[i]:>12.6f}  {probs[i]:>10.6f}  {bar}{marker}")

print()
print(f"  Sum of all P(o|c) = {np.sum(probs):.10f} (must = 1.0)")
print()

# ─── Key Observations ────────────────────────────────────────────
print("─" * 70)
print("Key Observations")
print("─" * 70)

# Context words vs unrelated
context_indices = [1, 2, 3, 4]  # crises, into, turning, problems
unrelated_indices = [8, 9]       # cat, dog
related_indices = [5, 6, 7]      # money, economy, policy

p_context = sum(probs[i] for i in context_indices)
p_unrelated = sum(probs[i] for i in unrelated_indices)
p_related = sum(probs[i] for i in related_indices)

print(f"  P(context words | banking) = {p_context:.6f}  (crises, into, turning, problems)")
print(f"  P(related words | banking) = {p_related:.6f}  (money, economy, policy)")
print(f"  P(unrelated words | banking) = {p_unrelated:.6f}  (cat, dog)")
print()

# The partition function cost
print(f"  Partition function cost: computed exp() for {VOCAB_SIZE} words")
print(f"  Real vocabulary: |V| ≈ 50,000+ → each training step needs 50,000+ exp() calls")
print(f"  This is WHY negative sampling (WP05) replaces full softmax!")
print()

# ─── Cross-entropy loss (Notes Eq.5) ────────────────────────────
print("─" * 70)
print("Cross-entropy loss (Notes Eq.5)")
print("─" * 70)
# Suppose the actual observed context word is "problems" (index 4)
observed_idx = 4
observed_word = VOCAB[observed_idx]
loss = -np.log(probs[observed_idx])
print(f"  Observed context word: '{observed_word}' (index {observed_idx})")
print(f"  P('{observed_word}' | '{center_word}') = {probs[observed_idx]:.6f}")
print(f"  L = -log P('{observed_word}' | '{center_word}') = -log({probs[observed_idx]:.6f}) = {loss:.6f}")
print()

# ─── Visualization 1: Probability Distribution Bar Chart ─────────
output_dir = "Labs/L01-word-vectors/outputs"
os.makedirs(output_dir, exist_ok=True)

fig, ax = plt.subplots(figsize=(12, 6))
colors = ['#2ecc71' if i in context_indices else 
          '#3498db' if i in related_indices else 
          '#e74c3c' for i in range(VOCAB_SIZE)]
bars = ax.bar(range(VOCAB_SIZE), probs, color=colors, edgecolor='black', linewidth=0.5)

ax.set_xlabel('Output word w', fontsize=12)
ax.set_ylabel('P(w | "banking")', fontsize=12)
ax.set_title('Skip-gram Softmax: P(o|c) for center word "banking"\n'
             '(Green=context window, Blue=semantically related, Red=unrelated)', 
             fontsize=13, fontweight='bold')
ax.set_xticks(range(VOCAB_SIZE))
ax.set_xticklabels(VOCAB, rotation=45, ha='right')

# Add probability values on bars
for i, (bar, prob) in enumerate(zip(bars, probs)):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
            f'{prob:.4f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#2ecc71', edgecolor='black', label='Context window'),
                   Patch(facecolor='#3498db', edgecolor='black', label='Semantically related'),
                   Patch(facecolor='#e74c3c', edgecolor='black', label='Unrelated')]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plot1_path = os.path.join(output_dir, "skipgram-softmax-prob-distribution.png")
plt.savefig(plot1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot1_path}")

# ─── Visualization 2: Dot Product Heatmap ────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
# Full dot product matrix: U @ V^T
full_dots = U @ V.T

im = ax.imshow(full_dots, cmap='RdYlBu_r', aspect='auto', vmin=-1.5, vmax=1.5)
ax.set_xticks(range(VOCAB_SIZE))
ax.set_xticklabels(VOCAB, rotation=45, ha='right', fontsize=9)
ax.set_yticks(range(VOCAB_SIZE))
ax.set_yticklabels(VOCAB, fontsize=9)
ax.set_xlabel('Center word c (v_c)', fontsize=11)
ax.set_ylabel('Context word o (u_o)', fontsize=11)
ax.set_title('Dot Products u_o^T v_c for All (center, context) Pairs\n'
             '(Higher = more compatible → higher P(o|c))', 
             fontsize=12, fontweight='bold')

# Add text annotations
for i in range(VOCAB_SIZE):
    for j in range(VOCAB_SIZE):
        val = full_dots[i, j]
        color = 'white' if abs(val) > 0.8 else 'black'
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=7, color=color)

plt.colorbar(im, ax=ax, label='u_o^T v_c (dot product)', shrink=0.8)
plt.tight_layout()
plot2_path = os.path.join(output_dir, "skipgram-softmax-dot-product-heatmap.png")
plt.savefig(plot2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot2_path}")

# ─── Visualization 3: Partition Function Cost Scaling ─────────────
fig, ax = plt.subplots(figsize=(10, 5))
vocab_sizes = [10, 100, 1000, 10000, 50000, 100000]
# Simulate: each exp() takes ~1 microsecond
time_per_exp_us = 1.0  # microseconds
total_time_ms = [v * time_per_exp_us / 1000 for v in vocab_sizes]

ax.bar(range(len(vocab_sizes)), total_time_ms, color='#9b59b6', edgecolor='black', linewidth=0.5)
ax.set_xticks(range(len(vocab_sizes)))
ax.set_xticklabels([f'{v:,}' for v in vocab_sizes])
ax.set_xlabel('Vocabulary size |V|', fontsize=12)
ax.set_ylabel('Time for one softmax (ms)', fontsize=12)
ax.set_title('Partition Function Cost: O(|V|) per Training Step\n'
             '(Each step requires exp() for EVERY word in vocabulary)',
             fontsize=12, fontweight='bold')

for i, (v, t) in enumerate(zip(vocab_sizes, total_time_ms)):
    ax.text(i, t + 0.5, f'{t:.1f} ms', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.annotate('Real word2vec\n|V| ≈ 50K-100K', 
            xy=(4, total_time_ms[4]), xytext=(3, total_time_ms[4] + 15),
            fontsize=10, ha='center',
            arrowprops=dict(arrowstyle='->', color='red'),
            color='red', fontweight='bold')

plt.tight_layout()
plot3_path = os.path.join(output_dir, "skipgram-softmax-partition-cost.png")
plt.savefig(plot3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot3_path}")

# ─── Save stdout ─────────────────────────────────────────────────
print()
print("─" * 70)
print("Output files")
print("─" * 70)
print(f"  Plot 1 (probability distribution): {plot1_path}")
print(f"  Plot 2 (dot product heatmap):      {plot2_path}")
print(f"  Plot 3 (partition function cost):  {plot3_path}")
print()
print("Done.")
