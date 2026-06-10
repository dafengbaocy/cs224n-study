## one-hot-vs-dense — One-hot 向量 vs 密集词向量 {#one-hot-vs-dense}

> **Waypoint**: WP01 — 为什么需要词向量？
> **Official anchor**: Slides p19-22; Notes §2.2 (one-hot vectors, Eq.1-2)
> **概念**：[[Lectures/L01-word-vectors/00-concept-glossary#one-hot-encoding|One-hot Encoding]] vs [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|Dense Vector]]
> **预计时间**：10-15 分钟

### 为什么不能只靠文字？

Slides p19-22 展示了 one-hot 和 dense vector 的概念，但只有**看实际向量维度和点积计算**才能真正理解为什么 one-hot 无法编码相似性。文字说"正交"，但亲手算出 `hotel · motel = 0.0` 和 `cos(hotel, motel) = 0.9949` 的对比，才能建立直觉。

### 核心问题

搜索 "Seattle motel" 应该匹配 "Seattle hotel"（Slides p20），但 one-hot 编码下：
- 任意两个不同词的点积 = 0（正交）
- 模型无法区分近义词（hotel/motel）和无关词（book/fish）

### 运行代码

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/one-hot-vs-dense.ipynb)

```python
# 核心演示：6 个词的词汇表
vocab = ["hotel", "motel", "book", "cat", "dog", "fish"]

# One-hot: 每个词一个位置为 1，其余为 0
# hotel = [1, 0, 0, 0, 0, 0]
# motel = [0, 1, 0, 0, 0, 0]

# 点积全部为 0：
# hotel · motel = 0.0  (近义词——应该相似)
# cat · dog   = 0.0  (同类——应该有些相似)
# book · fish = 0.0  (无关——应该不相似)

# Dense vectors (2D illustration):
# hotel = [+0.80, +0.70]    motel = [+0.70, +0.75]
# cos(hotel, motel) = 0.9949  ← 非常相似
# cos(cat, dog)     = 0.9430  ← 相似
# cos(book, fish)   = -0.3162 ← 不相似/方向相反
```

### 输出对比图

![one-hot-vs-dense-comparison](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161145.png)

> **先看哪里**：
> - 左图：One-hot 矩阵是单位矩阵——每行只有一个 1，行与行之间完全不重叠
> - 右图：密集向量在 2D 空间中，hotel/motel 聚在一起，cat/dog/fish 聚在一起，book 独立

> [!tip] 中文扶手
> One-hot 就像给每个词一个独立的身份证号——号码之间没有远近关系。密集向量则像 GPS 坐标——地理位置近的词，语义也近。Word2vec 的目标就是**从文本数据中自动学到这些"坐标"**。

### 关键数值

| 词对 | One-hot 点积 | Dense cosine | 含义 |
|------|:----------:|:-----------:|------|
| hotel vs motel | 0.0 | 0.9949 | 近义词：one-hot 无法区分，dense 高度相似 |
| cat vs dog | 0.0 | 0.9430 | 同类动物：dense 仍然相似 |
| book vs fish | 0.0 | -0.3162 | 无关词：dense 给出负值（方向相反） |

> [!question] 暂停复述
> 为什么 one-hot 向量的点积全是 0？如果词汇量是 50,000，one-hot 向量有多少维？其中多少个非零值？

### 对应 Slides / Notes

- Slides p19：one-hot 向量示例 `motel = [0 0 0 0 0 0 0 1 0 0 0 0 0 0 0]`
- Slides p20："There is no natural notion of similarity for one-hot vectors!"
- Slides p22：dense vectors 概念引入
- Notes §2.2：one-hot 向量定义、维度 = 词汇量

### 相关概念

- [[Lectures/L01-word-vectors/00-concept-glossary#one-hot-encoding|One-hot Encoding]]
- [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|Dense Vector]]
- [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|Cosine Similarity]]

---

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T080902Z__t_a3b87099__one-hot-vs-dense
  stdout: Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt
  checked_values:
    - claim: "hotel · motel = 0.0 (one-hot)"
      source: "stdout line: hotel · motel  = 0.0"
      status: copied_from_output
    - claim: "cat · dog = 0.0 (one-hot)"
      source: "stdout line: cat · dog    = 0.0"
      status: copied_from_output
    - claim: "book · fish = 0.0 (one-hot)"
      source: "stdout line: book · fish  = 0.0"
      status: copied_from_output
    - claim: "cos(hotel, motel) = 0.9949"
      source: "stdout line: cos(hotel, motel) = 0.9949"
      status: copied_from_output
    - claim: "cos(cat, dog) = 0.9430"
      source: "stdout line: cos(cat, dog) = 0.9430"
      status: copied_from_output
    - claim: "cos(book, fish) = -0.3162"
      source: "stdout line: cos(book, fish) = -0.3162"
      status: copied_from_output
    - claim: "vocab_size = 6"
      source: "stdout line: Vocabulary (6 words)"
      status: copied_from_output
```
