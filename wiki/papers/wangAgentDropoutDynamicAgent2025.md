---
type: Paper
title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
description: Topology optimization for LLM multi-agent systems that learns communication-graph adjacency matrices, then drops low-contribution agents per round (Node Dropout) and low-weight edges (Edge Dropout) to cut tokens and raise accuracy.
tags: [multi-agent-systems, communication-topology, graph-pruning, token-efficiency, agent-collaboration, ai899]
collections: [ai899]
authors: [Zhexuan Wang, Yutong Wang, Xuebo Liu, Liang Ding, Miao Zhang, Jie Liu, Min Zhang]
year: 2025
doi: 10.48550/arXiv.2503.18891
arxiv: "2503.18891"
arxiv_version: 2503.18891v1
code: https://github.com/wangzx1219/AgentDropout
sources:
  - id: wangAgentDropoutDynamicAgent2025
    resource: zotero://select/items/@wangAgentDropoutDynamicAgent2025
    title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
---

# AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration

Text source: arXiv HTML, version `2503.18891v1`.

## Summary

LLM-based [multi-agent systems](../methods/multi-agent-system.md) (MAS) suffer from high token consumption because agents generate and communicate frequently.[^wangAgentDropoutDynamicAgent2025] Prior work such as [AgentPrune](../methods/agentprune.md) prunes redundant communication edges with trainable graph masks, but keeps the same agent roles in every round and applies a uniform pruning strategy across communication rounds.[^wangAgentDropoutDynamicAgent2025] The paper argues that communication redundancy has two sources, redundant agent roles and redundant information exchange, and that different combinations of roles may suit different stages of task solving.[^wangAgentDropoutDynamicAgent2025]

[AgentDropout](../methods/agentdropout.md) optimizes the adjacency matrices of the multi-round communication graph with a small number of samples, then removes the least-contributing agents from each round (Node Dropout) and the least important intra- and inter-round edges (Edge Dropout).[^wangAgentDropoutDynamicAgent2025] Compared to state-of-the-art methods, it achieves an average reduction of 21.6% in prompt token consumption and 18.4% in completion token consumption, along with a performance improvement of 1.14 on the tasks.[^wangAgentDropoutDynamicAgent2025]

## Contributions

- The observation that, in MAS with both intra- and inter-round communication, involving different roles in distinct rounds of discussion is more efficient and performs better than engaging the same roles in every round.[^wangAgentDropoutDynamicAgent2025]
- AgentDropout, a simple and flexible optimization method for MAS that adjusts the overall communication topology in two steps, Node Dropout and Edge Dropout.[^wangAgentDropoutDynamicAgent2025]
- The observation that MAS built on larger and more powerful LLMs can still be improved through interaction, and that AgentDropout further enhances efficiency, domain transferability, and structural robustness.[^wangAgentDropoutDynamicAgent2025]

## Method

### MAS as a multi-round communication graph

A MAS is a directed communication graph $G=(V,E,F)$: each node is an agent, each edge $(v_i,v_j)$ is a communication path from agent $v_i$ to agent $v_j$, and $F$ abstracts agent inference. Node $v_i$ receives the query $q$ and the outputs of its in-neighbors and produces $o_i=f_i(q,Z_i)$.[^wangAgentDropoutDynamicAgent2025] Over $T$ rounds, intra-round edges connect nodes in the same round and inter-round edges pass the output of any node in step $t-1$ to any node in step $t$.[^wangAgentDropoutDynamicAgent2025] Communication redundancy exists if a subgraph with fewer edges satisfies $\mu(G_{\text{sub}})\geq\mu(G)$, where $\mu(\cdot)$ is the task-specified utility function.[^wangAgentDropoutDynamicAgent2025]

The graph is converted to a weighted graph in which each edge is a trainable continuous weight in the range of 0 to 1. The graph used at inference is drawn by `DAGSample`, which samples each edge with its weight as probability and guarantees a directed acyclic graph.[^wangAgentDropoutDynamicAgent2025]

### Step 1: Node Dropout

1. Initialize all edge weights of the intra- and inter-round adjacency matrices to 0.5 (intra-round diagonals are 0; inter-round matrices are upper triangular with a 0 diagonal).[^wangAgentDropoutDynamicAgent2025]
2. Train only the intra-round matrices to maximize expected task performance $\mathbb{E}_{G\sim\mathbb{G}}[\mu(G)]$. Because $\mu(\cdot)$ is commonly non-differentiable, the method uses the unbiased policy gradient estimate of [GPTSwarm](../methods/gptswarm.md): sample $M$ graphs, score each, and update by gradient ascent on $\frac{1}{M}\sum_{m}\mu(G_m)\nabla\log p(G_m)$.[^wangAgentDropoutDynamicAgent2025]
3. In each round, remove the nodes with the smallest weighted in- and out-degree together with all their edges, keeping a ratio $1-\alpha$ of nodes, where $\alpha$ is the node dropout rate.[^wangAgentDropoutDynamicAgent2025]

### Step 2: Edge Dropout

1. Reinitialize the intra- and inter-round matrices after Node Dropout and train both from scratch.[^wangAgentDropoutDynamicAgent2025]
2. The objective adds token efficiency to task performance: maximize $\mathbb{E}[\mu(G)]$ minus the sum of the ranks of the adjacency matrices. Low-rank sparsity is a proxy for communication efficiency. Because low-rank optimization is NP-hard, the rank is replaced with the nuclear norm, following AgentPrune.[^wangAgentDropoutDynamicAgent2025]
3. In each intra- and inter-round matrix, keep the edges with the largest weights at ratio $1-\beta$ and delete the rest, where $\beta$ is the edge dropout rate.[^wangAgentDropoutDynamicAgent2025]

The final communication graph is sampled from the optimized matrices with `DAGSample`. Agents communicate over multiple rounds on that topology and their responses are aggregated into the final answer.[^wangAgentDropoutDynamicAgent2025] The number of training samples is in the order of tens, taken from the train or validation set.[^wangAgentDropoutDynamicAgent2025]

## Experiments & Results

### Setup

- Base models: Meta-Llama3-8B-Instruct, Qwen2.5-72B-Instruct, Deepseek-V3-671B-Instruct.[^wangAgentDropoutDynamicAgent2025]
- Tasks: general reasoning on [MMLU](../datasets/mmlu.md); mathematical reasoning on [GSM8K](../datasets/gsm8k.md), [MultiArith](../datasets/multiarith.md), [AQuA](../datasets/aqua.md), and [SVAMP](../datasets/svamp.md); code generation on [HumanEval](../datasets/humaneval.md).[^wangAgentDropoutDynamicAgent2025]
- Baselines: single-agent Vanilla (direct reasoning) and [Chain-of-Thought](../methods/chain-of-thought.md) (CoT); single-round MAS ($\text{MAS}_{round=1}$); multi-round MAS ($\text{MAS}_{round=T}$) and AgentPrune. AgentPrune and AgentDropout are both optimized on top of $\text{MAS}_{round=T}$.[^wangAgentDropoutDynamicAgent2025]
- Llama3 and Qwen2.5 run on [vLLM](../methods/vllm.md) on Nvidia A800 GPUs. Deepseek-V3 uses the Deepseek API.[^wangAgentDropoutDynamicAgent2025]
- Hyperparameters: temperature 1, sample times $M$ in {10, 20}, learning rate $\eta$ 0.1, node and edge dropout rates $\alpha$ and $\beta$ in {0.1, 0.2}, 40 training samples for all benchmarks, $T=2$ for general reasoning and mathematical tasks, $T=4$ for code generation. Agent configuration files are adopted from AgentPrune.[^wangAgentDropoutDynamicAgent2025]
- The main experiments initialize the intra-round communication graph as a fully connected graph.[^wangAgentDropoutDynamicAgent2025]

### Task performance (Table 1)

The source does not name the metric unit for these scores; the text calls the gains "accuracy".[^wangAgentDropoutDynamicAgent2025]

| Base model | Method | MMLU | GSM8K | AQuA | MultiArith | SVAMP | HumanEval | Avg. |
|---|---|---|---|---|---|---|---|---|
| Llama3-8B-Instruct | Vanilla | 53.59 | 70.23 | 41.67 | 91.11 | 75.00 | 53.33 | 64.16 |
| Llama3-8B-Instruct | CoT | 56.86 | 70.47 | 43.75 | 92.25 | 76.17 | 54.17 | 65.61 |
| Llama3-8B-Instruct | $\text{MAS}_{round=1}$ | 56.21 | 69.30 | 45.29 | 91.67 | 76.67 | 48.33 | 64.58 |
| Llama3-8B-Instruct | $\text{MAS}_{round=T}$ | 60.13 | 71.48 | 45.41 | 90.56 | 77.56 | 49.17 | 65.72 |
| Llama3-8B-Instruct | AgentPrune | 60.78 | 71.02 | 47.22 | 90.00 | 78.34 | 51.67 | 66.51 |
| Llama3-8B-Instruct | AgentDropout | 62.75 | 73.13 | 47.78 | 92.59 | 80.11 | 55.84 | 68.70 |
| Qwen2.5-72B-Instruct | Vanilla | 82.35 | 91.02 | 83.75 | 98.89 | 92.67 | 85.28 | 88.99 |
| Qwen2.5-72B-Instruct | CoT | 83.66 | 92.19 | 84.58 | 100 | 93.35 | 86.67 | 90.08 |
| Qwen2.5-72B-Instruct | $\text{MAS}_{round=1}$ | 82.35 | 93.52 | 84.58 | 100 | 92.36 | 84.17 | 89.50 |
| Qwen2.5-72B-Instruct | $\text{MAS}_{round=T}$ | 84.31 | 93.28 | 85.83 | 100 | 94.07 | 87.08 | 90.76 |
| Qwen2.5-72B-Instruct | AgentPrune | 83.66 | 93.67 | 87.08 | 99.44 | 94.33 | 86.67 | 90.81 |
| Qwen2.5-72B-Instruct | AgentDropout | 84.97 | 93.75 | 87.50 | 100 | 95.34 | 87.92 | 91.58 |
| Deepseek-V3-671B-Instruct | Vanilla | 84.97 | 94.68 | 84.58 | 100 | 93.67 | 88.43 | 91.06 |
| Deepseek-V3-671B-Instruct | CoT | 84.31 | 95.15 | 85.42 | 100 | 93.94 | 89.26 | 91.34 |
| Deepseek-V3-671B-Instruct | $\text{MAS}_{round=1}$ | 89.98 | 95.54 | 86.67 | 100 | 93.50 | 89.17 | 92.63 |
| Deepseek-V3-671B-Instruct | $\text{MAS}_{round=T}$ | 89.54 | 95.49 | 87.50 | 100 | 94.33 | 89.26 | 92.69 |
| Deepseek-V3-671B-Instruct | AgentPrune | 90.20 | 95.49 | 87.92 | 100 | 95.00 | 90.91 | 93.25 |
| Deepseek-V3-671B-Instruct | AgentDropout | 90.85 | 95.63 | 88.33 | 100 | 95.79 | 91.74 | 93.72 |

All rows: [^wangAgentDropoutDynamicAgent2025]

Average accuracy over AgentPrune improves by 2.19 with Llama3, 0.77 with Qwen2.5, and 0.47 with Deepseek-V3.[^wangAgentDropoutDynamicAgent2025] With the weaker Llama3, single-agent CoT gives more significant gains while gains from multi-agent interaction (MAS, AgentPrune) are less stable; with stronger models single-agent gains diminish and multi-agent methods are more stable.[^wangAgentDropoutDynamicAgent2025]

### Token consumption (Tables 2 and 7)

Ptok. = prompt tokens, Ctok. = completion tokens. Average over the six datasets.[^wangAgentDropoutDynamicAgent2025]

| Method | Llama3 Ptok. | Llama3 Ctok. | Qwen2.5 Ptok. | Qwen2.5 Ctok. | Deepseek-V3 Ptok. | Deepseek-V3 Ctok. |
|---|---|---|---|---|---|---|
| Vanilla | 68K | 67K | 68K | 69K | 67K | 70K |
| CoT | 76K | 102K | 76K | 106K | 75K | 92K |
| $\text{MAS}_{round=1}$ | 2.4M | 567K | 2.4M | 520K | 2.1M | 463K |
| $\text{MAS}_{round=T}$ | 4.7M | 1.0M | 4.9M | 1.0M | 4.5M | 953K |
| AgentPrune | 4.2M | 1.0M | 4.1M | 979K | 3.7M | 947K |
| AgentDropout | 3.3M | 839K | 3.1M | 769K | 3.0M | 780K |

Per-dataset token consumption, Llama3-8B-Instruct:[^wangAgentDropoutDynamicAgent2025]

| Method | MMLU Ptok. / Ctok. | GSM8K | AQuA | MultiArith | SVAMP | HumanEval |
|---|---|---|---|---|---|---|
| $\text{MAS}_{round=T}$ | 1.6M / 387K | 16M / 3.4M | 2.4M / 745K | 2.1M / 388K | 3.7M / 721K | 2.6M / 492K |
| AgentPrune | 1.3M / 367K | 15M / 3.6M | 2.0M / 759K | 1.9M / 393K | 3.4M / 714K | 1.5M / 465K |
| AgentDropout | 1.1M / 333K | 12M / 2.8M | 1.3M / 634K | 1.4M / 312K | 2.6M / 594K | 1.1M / 359K |

The paper states that AgentDropout achieves a 21.4% reduction in prompt tokens and 16.1% in completion tokens with Llama3, and 24.4% and 18.9% in prompt tokens and 21.4% and 17.6% in completion tokens for Qwen2.5 and Deepseek-V3 respectively.[^wangAgentDropoutDynamicAgent2025] It also states that AgentPrune primarily reduces prompt tokens while AgentDropout reduces both prompt and completion tokens.[^wangAgentDropoutDynamicAgent2025]

### Structure robustness (Table 3, Llama3)

| Initial graph | Method | MMLU | GSM8K | AQuA | MultiArith | SVAMP | HumanEval | Avg. | Ptok. | Ctok. |
|---|---|---|---|---|---|---|---|---|---|---|
| Layered | MAS | 57.52 | 71.72 | 47.92 | 87.26 | 78.84 | 52.89 | 66.13 | 4.3M | 1.1M |
| Layered | AgentPrune | 59.48 | 71.09 | 46.67 | 88.93 | 78.67 | 56.20 | 66.84 | 3.7M | 1.0M |
| Layered | AgentDropout | 61.44 | 72.27 | 49.17 | 90.25 | 79.75 | 57.02 | 68.32 | 2.8M | 797K |
| Random | MAS | 62.75 | 70.63 | 46.67 | 87.22 | 77.17 | 50.41 | 65.81 | 4.2M | 1.0M |
| Random | AgentPrune | 63.40 | 69.61 | 44.17 | 91.11 | 78.34 | 51.24 | 66.31 | 3.4M | 1.0M |
| Random | AgentDropout | 64.71 | 72.03 | 47.50 | 91.67 | 79.50 | 53.72 | 68.19 | 2.7M | 834K |

All rows: [^wangAgentDropoutDynamicAgent2025]

### Dropout rate (Table 4, Llama3)

| Dropout Rate | MMLU | GSM8K | AQuA | MultiArith | SVAMP | HumanEval | Avg. | Ptok. | Ctok. |
|---|---|---|---|---|---|---|---|---|---|
| 0.8 | 57.52 | 70.86 | 46.67 | 89.44 | 78.67 | 52.89 | 66.01 | 856K | 230K |
| 0.6 | 60.78 | 71.09 | 45.42 | 89.44 | 80.37 | 50.41 | 66.25 | 1.3M | 434K |
| 0.4 | 60.13 | 73.36 | 44.99 | 90.00 | 78.33 | 52.07 | 66.48 | 1.9M | 648K |
| 0.2 | 62.75 | 73.13 | 47.78 | 92.59 | 80.11 | 55.84 | 68.70 | 3.3M | 839K |

All rows: [^wangAgentDropoutDynamicAgent2025]

Higher dropout rates lower the average performance of MAS.[^wangAgentDropoutDynamicAgent2025]

### Dropout strategy ablation (Table 5, Llama3)

For Random Dropout, the mark shows the step where the random strategy replaces the learned one; the other step is unchanged from AgentDropout.[^wangAgentDropoutDynamicAgent2025]

| Method | Edge DR. | Node DR. | MMLU | GSM8K | AQuA | MultiArith | SVAMP | HumanEval | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| MAS | no | no | 60.13 | 71.48 | 45.41 | 90.56 | 77.56 | 49.17 | 65.72 |
| Random Dropout | no | yes | 61.72 | 70.53 | 43.75 | 92.23 | 79.00 | 52.89 | 66.69 |
| Random Dropout | yes | no | 60.13 | 71.41 | 46.05 | 90.27 | 77.67 | 51.23 | 66.13 |
| Learned Dropout | no | yes | 63.76 | 70.70 | 46.25 | 90.28 | 79.17 | 50.83 | 66.83 |
| Learned Dropout | yes | no | 61.87 | 70.63 | 47.08 | 90.00 | 78.03 | 48.76 | 66.06 |
| Single Learning | yes | yes | 60.78 | 72.58 | 46.25 | 91.67 | 78.83 | 48.73 | 66.47 |
| AgentDropout | yes | yes | 62.75 | 73.13 | 47.78 | 92.59 | 80.11 | 55.84 | 68.70 |

All rows: [^wangAgentDropoutDynamicAgent2025]

"Single Learning" trains the intra- and inter-round matrices simultaneously once and applies both dropouts directly. The paper attributes AgentDropout's advantage to the new inference chains that appear after Node Dropout, which need a second training round.[^wangAgentDropoutDynamicAgent2025]

### Domain transferability (Table 6, Llama3)

Rows are the training set used for graph topology learning; columns are the test set.[^wangAgentDropoutDynamicAgent2025]

| Training set | GSM8K | AQuA | MultiArith | SVAMP | Avg. |
|---|---|---|---|---|---|
| GSM8K | 73.13 | 46.67 | 92.22 | 80.33 | 73.09 |
| AQuA | 73.84 | 47.78 | 93.13 | 78.21 | 73.24 |
| MultiArith | 71.41 | 47.50 | 92.59 | 78.33 | 72.46 |
| SVAMP | 70.86 | 47.50 | 91.95 | 80.11 | 72.61 |
| AgentPrune | 71.02 | 47.22 | 90.00 | 78.34 | 71.65 |
| AgentDropout | 73.13 | 47.78 | 92.59 | 80.11 | 73.40 |

All rows: [^wangAgentDropoutDynamicAgent2025]

Training on AQuA gives an average improvement of 1.59 over the SOTA method, and training on MultiArith gives 0.81.[^wangAgentDropoutDynamicAgent2025]

## Limitations

- The validated tasks are relatively limited: conventional reasoning, mathematical, and code generation tasks.[^wangAgentDropoutDynamicAgent2025]
- The framework is constrained by predefined agent roles and prompts. Tasks in unfamiliar domains still need carefully designed initial roles and prompts.[^wangAgentDropoutDynamicAgent2025]
- Token consumption of MAS remains relatively high after AgentDropout.[^wangAgentDropoutDynamicAgent2025]
- The method needs training instances of the current task (or of a similar dataset) to optimize the communication graph.[^wangAgentDropoutDynamicAgent2025]
- For AQuA and HumanEval, MAS shows lower sensitivity to dropout rates.[^wangAgentDropoutDynamicAgent2025]

## Related

- Methods: [AgentDropout](../methods/agentdropout.md), [Multi-agent system](../methods/multi-agent-system.md), [Chain-of-Thought](../methods/chain-of-thought.md)
- Methods compared against or built on: [AgentPrune](../methods/agentprune.md), [GPTSwarm](../methods/gptswarm.md)
- Systems used: [vLLM](../methods/vllm.md)
- Datasets: [MMLU](../datasets/mmlu.md), [GSM8K](../datasets/gsm8k.md), [AQuA](../datasets/aqua.md), [MultiArith](../datasets/multiarith.md), [SVAMP](../datasets/svamp.md)
- Benchmarks: [HumanEval](../datasets/humaneval.md)

[^wangAgentDropoutDynamicAgent2025]: Wang et al. 2025
