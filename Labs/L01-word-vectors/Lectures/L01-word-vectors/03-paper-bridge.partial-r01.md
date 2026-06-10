<!-- Paper Bridge Partial: L01-R01 -->
<!-- Producer: paper-tutor / L01-R01 -->
<!-- Covers: WP03, WP04 -->
<!-- Generated: 2026-06-09 -->

## L01-R01 Bridge: Efficient Estimation of Word Representations in Vector Space

> 本片段由 Paper Tutor (L01-R01) 生成，供 Lecture Weaver 汇总到 `03-paper-bridge.md` 和 `00-课堂入口.md`。
> 所有 wikilink 使用 vault-root 路径，定位到具体 heading。

### WP03 → L01-R01 推荐链接

- **CBOW 和 Skip-gram 架构对比图**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§3.1 Continuous Bag-of-Words Model (CBOW)|CBOW 架构（§3.1）]] — 用上下文词的平均向量预测当前词，复杂度 Eq.4
- **Skip-gram 架构**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§3.2 Continuous Skip-gram Model|Skip-gram 架构（§3.2）]] — 用当前词预测上下文，复杂度 Eq.5，窗口 C=10
- **Figure 1 架构图**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§3.1 Continuous Bag-of-Words Model (CBOW)|Figure 1: CBOW vs Skip-gram 可视化]] — 两种架构的输入→投影→输出结构
- **训练复杂度框架**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#Eq.1 训练复杂度|Eq.1 O=E×T×Q]] — 理解为什么去掉隐层能大幅提升效率
- **架构对比实验结果**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§4.3 Comparison of Model Architectures|Table 3: Skip-gram 语义 55% vs CBOW 语法 64%]] — Skip-gram 在语义任务大幅领先
- **向量关系示例**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§5 Examples of Learned Relationships（p10）|Table 8: France-Paris → Italy:Rome]] — 向量加减法表达类比关系
- **Hierarchical softmax**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§2.1 NNLM 复杂度|hierarchical softmax 说明（§2.1）]] — Huffman 树将输出复杂度降到 O(log V)

### WP04 → L01-R01 推荐链接

- **经验损失与 SGD**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§3 New Log-linear Models（p4-p5）：本文核心贡献|§3 核心决策：去掉隐层换数据规模]] — 论文的核心 trade-off
- **训练效率对比**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§4.4 Large Scale Parallel Training|Table 6: Skip-gram 1000d 仅需 2.5天×125核]] — 大规模训练的可行性证明
- **维度×数据量消融**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§4.2 Maximization of Accuracy|§4.2: 维度和数据必须同时增大]] — 单独增大任一个收益递减
- **Softmax 差异说明**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#公式汇总与中文直觉|公式汇总：论文 hierarchical softmax vs notes 标准 softmax]] — 两种实现的区别和联系
- **Parallel training**：[[Papers/L01-word-vectors/L01-R01-efficient-estimation-word-representations-vector#§2.3 Parallel Training|§2.3: DistBelief + Adagrad]] — 分布式训练框架
