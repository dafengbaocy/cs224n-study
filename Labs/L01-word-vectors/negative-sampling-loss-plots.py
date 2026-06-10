#!/usr/bin/env python3
"""Generate plots for negative-sampling-loss capsule."""
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
with open(os.path.join(out_dir, "negative-sampling-loss-output.json")) as f:
    data = json.load(f)

# Plot 1: Loss comparison + computation cost
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
k_values = [r["k"] for r in data["k_sweep"]]
ns_losses = [r["loss"] for r in data["k_sweep"]]
softmax_loss = data["softmax"]["loss"]

x = np.arange(len(k_values) + 1)
bars_data = [softmax_loss] + ns_losses
colors = ['#e74c3c'] + ['#3498db'] * len(k_values)
labels = ['Softmax\n(full)'] + [f'NS\nk={k}' for k in k_values]

bars = axes[0].bar(x, bars_data, 0.6, color=colors, alpha=0.85, edgecolor='white', linewidth=1.5)
axes[0].set_xticks(x)
axes[0].set_xticklabels(labels, fontsize=9)
axes[0].set_ylabel('Loss value', fontsize=11)
axes[0].set_title('Loss: Softmax vs Negative Sampling (different k)', fontsize=12, fontweight='bold')
for bar, val in zip(bars, bars_data):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.03,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
axes[0].set_ylim(0, max(bars_data) * 1.25)

softmax_dots = data["softmax"]["dot_products"]
dots_data = [softmax_dots] + [r["dot_products"] for r in data["k_sweep"]]
colors2 = ['#e74c3c'] + ['#2ecc71'] * len(k_values)
bars2 = axes[1].bar(x, dots_data, 0.6, color=colors2, alpha=0.85, edgecolor='white', linewidth=1.5)
axes[1].set_xticks(x)
axes[1].set_xticklabels(labels, fontsize=9)
axes[1].set_ylabel('Dot products needed', fontsize=11)
axes[1].set_title('Computation Cost: Dot Products per Step', fontsize=12, fontweight='bold')
for bar, val in zip(bars2, dots_data):
    axes[1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                f'{val}', ha='center', va='bottom', fontsize=9, fontweight='bold')
axes[1].set_ylim(0, max(dots_data) * 1.3)
plt.tight_layout()
p1 = os.path.join(out_dir, "negative-sampling-loss-comparison.png")
plt.savefig(p1, dpi=150, bbox_inches='tight')
plt.close()
print(f"Plot 1 saved: {p1}")

# Plot 2: Real-world scaling
fig, ax = plt.subplots(figsize=(10, 5))
vocab_sizes = [1000, 10000, 50000, 100000]
speedups = [vs / 6 for vs in vocab_sizes]
ax.bar(range(len(vocab_sizes)), vocab_sizes, color='#3498db', alpha=0.7, label='Softmax dots (= |V|)')
ax_twin = ax.twinx()
ax_twin.plot(range(len(vocab_sizes)), speedups, 'ro-', linewidth=2.5, markersize=10, label='NS speedup (k=5)')
for i, (vs, sp) in enumerate(zip(vocab_sizes, speedups)):
    ax_twin.annotate(f'{int(sp):,}x', (i, sp), textcoords="offset points",
                    xytext=(0, 12), ha='center', fontsize=10, fontweight='bold', color='red')
ax.set_xticks(range(len(vocab_sizes)))
ax.set_xticklabels([f'{vs:,}' for vs in vocab_sizes])
ax.set_xlabel('Vocabulary size |V|', fontsize=11)
ax.set_ylabel('Dot products per step', fontsize=11, color='#3498db')
ax_twin.set_ylabel('Speedup factor (NS vs Softmax)', fontsize=11, color='red')
ax.set_title('Real-world Scaling: Why Negative Sampling Matters', fontsize=13, fontweight='bold')
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax_twin.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
plt.tight_layout()
p2 = os.path.join(out_dir, "negative-sampling-loss-scaling.png")
plt.savefig(p2, dpi=150, bbox_inches='tight')
plt.close()
print(f"Plot 2 saved: {p2}")

# Plot 3: Gradient + softmax probs
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
k_vals_plot = [r["k"] for r in data["k_sweep"] if r["k"] <= 20]
grad_norms = [r["grad_norm"] for r in data["k_sweep"] if r["k"] <= 20]
softmax_grad_norm = data["gradient_comparison"]["softmax_grad_norm"]

x3 = np.arange(len(k_vals_plot) + 1)
norm_data = [softmax_grad_norm] + grad_norms
colors3 = ['#e74c3c'] + ['#9b59b6'] * len(k_vals_plot)
labels3 = ['Softmax'] + [f'k={k}' for k in k_vals_plot]
bars3 = axes[0].bar(x3, norm_data, 0.6, color=colors3, alpha=0.85, edgecolor='white', linewidth=1.5)
axes[0].set_xticks(x3)
axes[0].set_xticklabels(labels3, fontsize=9)
axes[0].set_ylabel('||gradient||', fontsize=11)
axes[0].set_title('Gradient Magnitude by Method', fontsize=12, fontweight='bold')
for bar, val in zip(bars3, norm_data):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
axes[0].set_ylim(0, max(norm_data) * 1.3)

probs = data["softmax"]["probs"]
words = list(probs.keys())
prob_vals = [probs[w] for w in words]
colors4 = ['#e74c3c' if w == 'money' else '#3498db' for w in words]
axes[1].barh(range(len(words)), prob_vals, color=colors4, alpha=0.85, edgecolor='white')
axes[1].set_yticks(range(len(words)))
axes[1].set_yticklabels(words, fontsize=10)
axes[1].set_xlabel('P(w | center="banking")', fontsize=11)
axes[1].set_title('Softmax Probability Distribution', fontsize=12, fontweight='bold')
for i, (w, p) in enumerate(zip(words, prob_vals)):
    marker = " <- output" if w == "money" else ""
    axes[1].text(p + 0.01, i, f'{p:.4f}{marker}', va='center', fontsize=9)
plt.tight_layout()
p3 = os.path.join(out_dir, "negative-sampling-loss-gradient.png")
plt.savefig(p3, dpi=150, bbox_inches='tight')
plt.close()
print(f"Plot 3 saved: {p3}")
print("All plots generated successfully.")
