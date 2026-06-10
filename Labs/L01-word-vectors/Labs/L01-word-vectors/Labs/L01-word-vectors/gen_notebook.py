#!/usr/bin/env python3
"""Generate co-occurrence-matrix.ipynb notebook."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    'kernelspec': {
        'display_name': 'Python 3',
        'language': 'python',
        'name': 'python3'
    },
    'language_info': {
        'name': 'python',
        'version': '3.13.5'
    },
    'colab': {
        'provenance': [],
        'name': 'co-occurrence-matrix.ipynb'
    }
}

cells = []

cells.append(nbf.v4.new_markdown_cell(
    "# CS224N L01 - Code Capsule: co-occurrence-matrix (WP02)\n\n"
    "**Waypoint**: WP02\n"
    "**Concept**: Build co-occurrence matrix + SVD dimensionality reduction\n"
    "**Anchor**: Notes 3.1; A1 Part 1 Q1.1-1.3\n"
))

cells.append(nbf.v4.new_code_cell(
    "import numpy as np\n"
    "from collections import Counter\n"
    "import matplotlib.pyplot as plt\n"
    "from scipy.linalg import svd\n"
    "\n"
    "CORPUS = [\n"
    "    'banking money finance economy',\n"
    "    'money market invest finance',\n"
    "    'banking invest market economy',\n"
    "    'finance economy market money',\n"
    "    'invest banking economy finance',\n"
    "    'market economy banking money',\n"
    "    'river lake forest mountain',\n"
    "    'lake ocean valley forest',\n"
    "    'forest mountain river valley',\n"
    "    'mountain valley ocean river',\n"
    "    'ocean river lake mountain',\n"
    "    'valley forest ocean lake',\n"
    "    'the banking river flows',\n"
    "    'the forest economy grows',\n"
    "]\n"
    "print(f'Corpus: {len(CORPUS)} sentences')\n"
))

cells.append(nbf.v4.new_code_cell(
    "counter = Counter()\n"
    "for sent in CORPUS:\n"
    "    counter.update(sent.split())\n"
    "vocab = sorted(counter.keys())\n"
    "word2idx = {w: i for i, w in enumerate(vocab)}\n"
    "V = len(vocab)\n"
    "print(f'Vocabulary size |V| = {V}')\n"
    "print(f'Words: {vocab}')\n"
))

cells.append(nbf.v4.new_code_cell(
    "def build_cooccurrence(corpus, word2idx, vocab_size, window_size=2):\n"
    "    X = np.zeros((vocab_size, vocab_size), dtype=np.float64)\n"
    "    for sent in corpus:\n"
    "        tokens = sent.split()\n"
    "        for center_pos, center_word in enumerate(tokens):\n"
    "            if center_word not in word2idx:\n"
    "                continue\n"
    "            c_idx = word2idx[center_word]\n"
    "            start = max(0, center_pos - window_size)\n"
    "            end = min(len(tokens), center_pos + window_size + 1)\n"
    "            for ctx_pos in range(start, end):\n"
    "                if ctx_pos == center_pos:\n"
    "                    continue\n"
    "                ctx_word = tokens[ctx_pos]\n"
    "                if ctx_word not in word2idx:\n"
    "                    continue\n"
    "                x_idx = word2idx[ctx_word]\n"
    "                X[c_idx][x_idx] += 1.0\n"
    "    return X\n"
    "\n"
    "WINDOW_SIZE = 2\n"
    "X_raw = build_cooccurrence(CORPUS, word2idx, V, window_size=WINDOW_SIZE)\n"
    "X_log = np.log1p(X_raw)\n"
    "total_count = X_raw.sum()\n"
    "nonzero = np.count_nonzero(X_raw)\n"
    "sparsity = 1.0 - nonzero / (V * V)\n"
    "print(f'Matrix shape: ({V}, {V}), Total count: {total_count:.0f}, Nonzero: {nonzero}, Sparsity: {sparsity:.1%}')\n"
))

cells.append(nbf.v4.new_code_cell(
    "# Visualize co-occurrence matrix\n"
    "fig, axes = plt.subplots(1, 2, figsize=(16, 7))\n"
    "im1 = axes[0].imshow(X_raw, cmap='YlOrRd', aspect='auto')\n"
    "axes[0].set_xticks(range(V)); axes[0].set_yticks(range(V))\n"
    "axes[0].set_xticklabels(vocab, rotation=45, ha='right', fontsize=8)\n"
    "axes[0].set_yticklabels(vocab, fontsize=8)\n"
    "axes[0].set_title(f'Raw Co-occurrence Matrix (window={WINDOW_SIZE})')\n"
    "plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)\n"
    "im2 = axes[1].imshow(X_log, cmap='YlOrRd', aspect='auto')\n"
    "axes[1].set_xticks(range(V)); axes[1].set_yticks(range(V))\n"
    "axes[1].set_xticklabels(vocab, rotation=45, ha='right', fontsize=8)\n"
    "axes[1].set_yticklabels(vocab, fontsize=8)\n"
    "axes[1].set_title('Log-normalized: log(1 + X)')\n"
    "plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)\n"
    "plt.tight_layout(); plt.show()\n"
))

cells.append(nbf.v4.new_code_cell(
    "# SVD: V-dim -> k=2\n"
    "K = 2\n"
    "U, s, Vt = svd(X_log, full_matrices=False)\n"
    "word_vectors = U[:, :K] * s[:K][np.newaxis, :]\n"
    "explained_ratio = np.sum(s[:K]**2) / np.sum(s**2)\n"
    "print(f'Top-{K} singular values: {s[:K]}')\n"
    "print(f'Explained variance ratio: {explained_ratio:.1%}')\n"
    "for i, w in enumerate(vocab):\n"
    "    print(f'  {w:>12s}  [{word_vectors[i,0]:8.4f}, {word_vectors[i,1]:8.4f}]')\n"
))

cells.append(nbf.v4.new_code_cell(
    "# 2D scatter plot\n"
    "fig, ax = plt.subplots(1, 1, figsize=(10, 8))\n"
    "finance_words = [w for w in ['banking','money','finance','economy','market','invest'] if w in word2idx]\n"
    "nature_words = [w for w in ['river','lake','forest','mountain','valley','ocean'] if w in word2idx]\n"
    "colors = {'finance': '#e74c3c', 'nature': '#2ecc71', 'bridge': '#95a5a6'}\n"
    "markers = {'finance': 'o', 'nature': 's', 'bridge': '^'}\n"
    "for i, w in enumerate(vocab):\n"
    "    cl = 'finance' if w in finance_words else ('nature' if w in nature_words else 'bridge')\n"
    "    ax.scatter(word_vectors[i,0], word_vectors[i,1], c=colors[cl], marker=markers[cl],\n"
    "               s=100, zorder=5, edgecolors='white', linewidth=0.5)\n"
    "    ax.annotate(w, (word_vectors[i,0], word_vectors[i,1]), fontsize=9, ha='center', va='bottom',\n"
    "                xytext=(0, 8), textcoords='offset points')\n"
    "from matplotlib.lines import Line2D\n"
    "legend_elements = [\n"
    "    Line2D([0],[0], marker='o', color='w', markerfacecolor='#e74c3c', markersize=10, label='Finance'),\n"
    "    Line2D([0],[0], marker='s', color='w', markerfacecolor='#2ecc71', markersize=10, label='Nature'),\n"
    "    Line2D([0],[0], marker='^', color='w', markerfacecolor='#95a5a6', markersize=10, label='Bridge'),\n"
    "]\n"
    "ax.legend(handles=legend_elements, loc='upper right')\n"
    "ax.set_title(f'SVD 2D Embeddings (k={K}, explained variance={explained_ratio:.1%})')\n"
    "ax.grid(True, alpha=0.3); plt.tight_layout(); plt.show()\n"
))

cells.append(nbf.v4.new_code_cell(
    "# Cosine similarity\n"
    "def cosine_sim(a, b):\n"
    "    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)\n"
    "\n"
    "pairs = [\n"
    "    ('banking', 'money', 'within'), ('banking', 'finance', 'within'),\n"
    "    ('river', 'lake', 'within'), ('river', 'forest', 'within'),\n"
    "    ('banking', 'river', 'cross'), ('banking', 'lake', 'cross'),\n"
    "    ('money', 'forest', 'cross'),\n"
    "]\n"
    "for w1, w2, kind in pairs:\n"
    "    sim = cosine_sim(word_vectors[word2idx[w1]], word_vectors[word2idx[w2]])\n"
    "    print(f'  cos({w1}, {w2}) = {sim:.4f}  [{kind}]')\n"
))

nb.cells = cells

with open("Labs/L01-word-vectors/co-occurrence-matrix.ipynb", "w") as f:
    nbf.write(nb, f)
print("Notebook written successfully")
