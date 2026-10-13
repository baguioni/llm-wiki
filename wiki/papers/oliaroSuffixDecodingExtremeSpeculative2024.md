---
type: Paper
title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
description: Model-free speculative decoding that drafts tokens from suffix trees over the current request and prior outputs, with speculation length adapted to the pattern match length, aimed at repetitive agentic workloads.
tags: [speculative-decoding, model-free-speculation, suffix-tree, agentic-workloads, llm-serving, ai899]
collections: [ai899]
authors: [Gabriele Oliaro, Zhihao Jia, Daniel Campos, Aurick Qiao]
arxiv: "2411.04975"
arxiv_version: 2411.04975v3
code: https://github.com/snowflakedb/ArcticInference
sources:
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
---

# SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications

Text source: arXiv HTML, version `2411.04975v3`.

## Summary

Agentic applications such as multi-agent pipelines and self-refinement loops submit repetitive inference requests, which produce long and highly predictable token sequences that existing [speculative decoding](../methods/speculative-decoding.md) methods do not exploit well.[^oliaroSuffixDecodingExtremeSpeculative2024] Model-based methods can use significant GPU time when speculating long sequences, while model-free methods such as [prompt-lookup decoding (PLD)](../methods/prompt-lookup-decoding.md) speculate a fixed number of tokens regardless of acceptance likelihood.[^oliaroSuffixDecodingExtremeSpeculative2024]

SuffixDecoding is a model-free speculative decoding method that caches long token sequences from prompts and previous outputs in suffix trees, and speculates more tokens when acceptance likelihood is high and fewer when it is low.[^oliaroSuffixDecodingExtremeSpeculative2024] Draft tokens are generated in about 20 microseconds per token without GPU overhead.[^oliaroSuffixDecodingExtremeSpeculative2024] The abstract reports speedups of up to 5.3×, 2.8× faster than model-based approaches like EAGLE-2/3 and 1.9× faster than model-free approaches such as Token Recycling.[^oliaroSuffixDecodingExtremeSpeculative2024] For SWE-Bench, end-to-end task completion (prompt prefilling, token generation, and execution of external actions) shows speculative speedups of up to 4.5×.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Contributions

- SuffixDecoding, a model-free speculative decoding method for repetitive, agent-driven workloads, built on suffix trees over the current request and prior outputs.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Adaptive speculation length: the number of draft tokens is limited by the length of the pattern match, and frequency statistics in the suffix trees score and select the speculation candidate.[^oliaroSuffixDecodingExtremeSpeculative2024]
- A hybrid mode that uses suffix-tree speculation when its score is high and falls back to a model-based speculator such as EAGLE-3 otherwise.[^oliaroSuffixDecodingExtremeSpeculative2024]
- An implementation in [vLLM](../methods/vllm.md) and an end-to-end evaluation with the OpenHands agent running live on SWE-Bench.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Method

### Suffix trees

- Each node represents a token, and the path from the root to a node represents a distinct subsequence. Each child of a node is a possible continuation.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Two trees are kept: a *global* tree over previously generated outputs, and a *per-request* tree over the prompt and output of the ongoing request. This avoids synchronizing updates from concurrent requests.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The global tree can be built offline in $O(n)$ time (for example from historical logs) or updated online after each request completes. The per-request tree is built and updated online as tokens are generated.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Suffix trees take $O(n)$ space and need only CPU memory.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Pattern matching

Given the ongoing sequence $x_{1:t}$, the *pattern* is the suffix $x_{t-p+1:t}$ of length $p$. The tree is walked from the root, taking the child for each pattern token. If a child is missing, the pattern is not found and SuffixDecoding reverts to standard non-speculative decoding. Otherwise the walk ends at node $N_p$, whose descending paths are the possible continuations.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Speculation tree expansion

The speculation tree starts as the single node $N_p$ and grows greedily by one leaf at a time.[^oliaroSuffixDecodingExtremeSpeculative2024] With $\texttt{COUNT}(N)$ the number of occurrences of node $N$ in the reference corpus:[^oliaroSuffixDecodingExtremeSpeculative2024]

$$
C(N)=\frac{\texttt{COUNT}(N)}{\sum_{M\in\texttt{CHILDREN}(\texttt{PARENT}(N))}\texttt{COUNT}(M)}
$$

$$
D(N)=\begin{cases}D(\texttt{PARENT}(N))\times C(N),&\text{if $N\neq N_{p}$}\\ 1,&\text{otherwise}\end{cases}
$$

At each step the child of any current leaf with the highest $D(N)$ is added, until the sub-tree reaches the size limit `MAX_SPEC`.[^oliaroSuffixDecodingExtremeSpeculative2024] $D(N)$ estimates the probability that the token of $N$ is accepted by speculative tree verification.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Adaptive speculation length

The number of accepted tokens typically increases with the pattern length $p$, so the limit is set to $\texttt{MAX\_SPEC}(p)=\alpha p$, where $\alpha$ is a user-defined max speculation factor.[^oliaroSuffixDecodingExtremeSpeculative2024] The paper found that $\alpha\in[1,4]$ works well for agentic applications.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Speculation tree scoring

Speculation trees are built from both suffix trees and for a range of $p$ (from 1 to a max pattern size $P$). The tree with the highest $\texttt{SCORE}(T_{spec})=\sum_{N\in T_{spec}}D(N)$ is verified. The score estimates the expected number of accepted tokens.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Hybrid suffix speculative decoding

In each decoding iteration SuffixDecoding speculates first. If $\texttt{SCORE}(T_{spec})>\tau$, its draft tokens are used. Otherwise a fallback speculator such as [EAGLE-3](../methods/eagle-3.md) is used.[^oliaroSuffixDecodingExtremeSpeculative2024] The paper's guideline is to set $\tau$ close to the mean accepted tokens (MAT) of the fallback speculator for mixed workloads, and to use SuffixDecoding alone ($\tau=0$) for highly repetitive agentic tasks.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Predicting effectiveness with empirical entropy

"Structuredness" is measured by building a suffix tree from example outputs (100 examples is typically enough), computing the entropy of each node's child distribution, and taking a weighted average across nodes. Lower entropy generally suggests better SuffixDecoding performance.[^oliaroSuffixDecodingExtremeSpeculative2024]

| Dataset | Average Entropy |
|---|---|
| AgenticSQL (Enrich) | 0.171 |
| AgenticSQL (Classify) | 0.738 |
| AgenticSQL (Extract) | 0.0862 |
| AgenticSQL (SQL1) | 1.52 |
| AgenticSQL (SQL2) | 1.49 |
| AgenticSQL (SQL3) | 1.51 |
| AgenticSQL (Combine) | 1.49 |
| Spider | 2.50 |
| WildChat | 3.43 |
| Magicoder | 2.95 |

All rows (Table 1): [^oliaroSuffixDecodingExtremeSpeculative2024]

## Experiments & Results

### Setup

- Baselines, run through the [Spec-Bench](../benchmarks/spec-bench.md) codebase: [EAGLE-2](../methods/eagle-2.md) and [EAGLE-3](../methods/eagle-3.md) (model-based), [PLD](../methods/prompt-lookup-decoding.md) (model-free n-gram matching), and [Token Recycling](../methods/token-recycling.md) (model-free, uses the prompt and previous outputs).[^oliaroSuffixDecodingExtremeSpeculative2024]
- Agentic workloads: traces of OpenHands on [SWE-Bench](../benchmarks/swe-bench.md), and [AgenticSQL](../datasets/agenticsql.md), a proprietary multi-agent SQL generation workflow with Classify, Extract, Enrich, parallel text-to-SQL, and Combine steps.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Non-agentic workload: Spec-Bench, open-ended single-turn tasks across 13 categories, including 8 [MT-Bench](../datasets/mt-bench.md) categories.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Baseline comparison (Sec. 4.2): Llama-3.1-8B-Instruct on a single H100 GPU with batch size 1. Speedup is the ratio of wall-clock time-per-output-token relative to vanilla decoding.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Hardware: a single p5.48xlarge AWS instance with 8× NVIDIA H100 80G GPUs and 2TB of main memory (Sec. 4.1). Appendix A.1.1 states an 8xH100 80GB GPU cluster with 1TB RAM.[^oliaroSuffixDecodingExtremeSpeculative2024]
- "Suffix (tree)" and "Hybrid (tree)" use tree speculation. "Suffix (linear)" and "Hybrid (linear)" allow only sequential token chains. Hybrid variants combine SuffixDecoding with EAGLE-3.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Ablations use a simulated verifier on offline traces, which checks speculated tokens against a ground-truth response under greedy sampling.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Overall results per benchmark (Appendix A.1.2, "Overall" column)

Speedup over vanilla decoding:[^oliaroSuffixDecodingExtremeSpeculative2024]

| System | AgenticSQL | SWE-Bench | Spec-Bench |
|---|---|---|---|
| suffix (linear) | 5.345 | 2.452 | 1.659 |
| suffix (tree) | 5.175 | 2.433 | 1.661 |
| hybrid (tree) | 4.068 | - | 2.458 |
| hybrid (linear) | 3.799 | - | 2.500 |
| recycling | 2.710 | 1.358 | 2.169 |
| pld | 2.105 | 1.495 | 1.448 |
| eagle2 | 1.864 | - | 1.825 |
| eagle3 | 1.623 | - | 2.367 |
| eagle | 1.595 | - | 1.752 |
| vanilla | 1.000 | 1.000 | 1.000 |

Mean accepted tokens (tokens/step):[^oliaroSuffixDecodingExtremeSpeculative2024]

| System | AgenticSQL | SWE-Bench | Spec-Bench |
|---|---|---|---|
| suffix (linear) | 6.349 | 7.821 | 1.766 |
| suffix (tree) | 6.236 | 7.552 | 1.750 |
| hybrid (tree) | 7.500 | - | 4.684 |
| hybrid (linear) | 7.262 | - | 4.553 |
| recycling | 3.169 | 3.054 | 2.548 |
| pld | 2.373 | 3.168 | 1.606 |
| eagle2 | 3.572 | - | 3.466 |
| eagle3 | 3.160 | - | 4.647 |
| eagle | 2.851 | - | 3.065 |

Time per output token (ms):[^oliaroSuffixDecodingExtremeSpeculative2024]

| System | AgenticSQL | SWE-Bench | Spec-Bench |
|---|---|---|---|
| suffix (linear) | 7.306 | 27.436 | 16.936 |
| suffix (tree) | 7.592 | 27.711 | 16.875 |
| hybrid (tree) | 9.604 | - | 11.153 |
| hybrid (linear) | 10.874 | - | 10.747 |
| recycling | 9.782 | 43.774 | 11.947 |
| pld | 15.169 | 37.758 | 19.190 |
| eagle2 | 14.677 | - | 14.387 |
| eagle3 | 18.966 | - | not stated |
| eagle | 17.887 | - | 14.925 |
| vanilla | 25.924 | 50.074 | 25.076 |

Note: the Spec-Bench "Time per output token" table in the source has no eagle3 row, so that cell is not stated.[^oliaroSuffixDecodingExtremeSpeculative2024]

Speculation time per generated token (ms):[^oliaroSuffixDecodingExtremeSpeculative2024]

| System | AgenticSQL | SWE-Bench | Spec-Bench |
|---|---|---|---|
| suffix (linear) | 0.043 | 0.171 | 0.088 |
| suffix (tree) | 0.047 | 0.175 | 0.091 |
| pld | 0.298 | 0.191 | 0.395 |
| recycling | 0.592 | 10.582 | 0.340 |
| hybrid (tree) | 1.299 | - | 2.344 |
| hybrid (linear) | 1.604 | - | 2.259 |
| eagle | 2.700 | - | 2.289 |
| eagle2 | 3.487 | - | 2.936 |
| eagle3 | 4.854 | - | 2.634 |

Mean acceptance rate:[^oliaroSuffixDecodingExtremeSpeculative2024]

| System | AgenticSQL | SWE-Bench | Spec-Bench |
|---|---|---|---|
| suffix (linear) | 0.415 | 0.296 | 0.190 |
| suffix (tree) | 0.375 | 0.274 | 0.179 |
| hybrid (tree) | 0.304 | - | 0.070 |
| hybrid (linear) | 0.302 | - | 0.070 |
| pld | 0.173 | 0.225 | 0.099 |
| eagle | 0.074 | - | 0.083 |
| eagle2 | 0.043 | - | 0.041 |
| eagle3 | 0.036 | - | 0.061 |
| recycling | 0.028 | 0.026 | 0.020 |

- EAGLE-2/3 and Token Recycling failed to run on several SWE-Bench tasks due to long context lengths (>8192 tokens). Token Recycling has no result for the flask, requests, and sympy repositories.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The main text states these results in rounded form: on AgenticSQL a mean speedup of 5.3× over vanilla decoding, a 2.8× improvement over EAGLE-2/3 and 1.9× higher than Token Recycling; on SWE-Bench a mean speedup of 2.5×, a 1.7× improvement over PLD, the next best baseline.[^oliaroSuffixDecodingExtremeSpeculative2024]
- On Spec-Bench, SuffixDecoding alone is outperformed by EAGLE-2/3 and Token Recycling. The hybrid obtains a mean speedup of 2.5×, compared to 2.4× for standalone EAGLE-3 and 2.2× for Token Recycling.[^oliaroSuffixDecodingExtremeSpeculative2024]

### AgenticSQL per-task speedup over vanilla decoding

| System | Classify | Extract | Enrich | Combine | SQL1 | SQL2 | SQL3 | Overall |
|---|---|---|---|---|---|---|---|---|
| suffix (linear) | 3.016 | 9.854 | 10.406 | 4.848 | 3.205 | 2.839 | 3.211 | 5.345 |
| suffix (tree) | 2.998 | 9.545 | 10.009 | 4.765 | 3.008 | 2.733 | 3.133 | 5.175 |
| hybrid (tree) | 2.338 | 7.672 | 8.191 | 3.613 | 2.057 | 2.496 | 2.077 | 4.068 |
| hybrid (linear) | 2.243 | 7.137 | 7.965 | 3.327 | 1.993 | 2.483 | 1.405 | 3.799 |
| recycling | 2.588 | 3.472 | 2.672 | 2.640 | 2.502 | 2.604 | 2.492 | 2.710 |
| pld | 1.330 | 3.695 | 1.255 | 3.298 | 1.936 | 1.311 | 1.905 | 2.105 |
| eagle2 | 1.591 | 2.751 | 1.673 | 1.855 | 1.527 | 2.119 | 1.527 | 1.864 |
| eagle3 | 1.328 | 1.720 | 2.025 | 1.619 | 1.108 | 2.496 | 1.056 | 1.623 |
| eagle | 1.324 | 2.246 | 1.598 | 1.669 | 1.229 | 1.955 | 1.138 | 1.595 |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

### SWE-Bench per-repository speedup over vanilla decoding

| System | astropy | django | matplotlib | seaborn | flask | requests | xarray | pylint | pytest | scikit-learn | sphinx | sympy | Overall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| suffix (linear) | 2.213 | 2.442 | 2.039 | 1.951 | 1.792 | 1.962 | 2.210 | 1.792 | 1.888 | 2.356 | 4.453 | 2.292 | 2.452 |
| suffix (tree) | 2.158 | 2.412 | 1.991 | 1.985 | 1.759 | 1.972 | 2.190 | 1.754 | 1.912 | 2.296 | 4.417 | 2.280 | 2.433 |
| pld | 1.440 | 1.516 | 1.425 | 1.360 | 1.242 | 1.399 | 1.486 | 1.270 | 1.326 | 1.429 | 2.006 | 1.483 | 1.495 |
| recycling | 1.427 | 1.458 | 1.483 | 1.264 | - | - | 1.360 | 1.311 | 1.290 | 1.399 | 1.328 | - | 1.358 |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

### Spec-Bench per-category speedup over vanilla decoding

| System | coding | extraction | humanities | math | math_reasoning | qa | rag | reasoning | roleplay | stem | summarization | translation | writing | Overall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid (linear) | 3.441 | 2.795 | 2.800 | 3.139 | 2.866 | 2.404 | 2.542 | 2.496 | 2.461 | 2.871 | 2.573 | 1.759 | 2.833 | 2.500 |
| hybrid (tree) | 3.442 | 2.717 | 2.644 | 3.132 | 2.736 | 2.611 | 2.445 | 2.344 | 2.330 | 2.732 | 2.485 | 1.713 | 2.736 | 2.458 |
| eagle3 | 3.115 | 2.634 | 2.713 | 2.910 | 2.888 | 2.172 | 2.474 | 2.446 | 2.394 | 2.764 | 2.520 | 1.447 | 2.622 | 2.367 |
| recycling | 2.619 | 2.234 | 2.209 | 2.660 | 2.577 | 1.951 | 2.057 | 2.150 | 1.979 | 2.334 | 2.218 | 1.932 | 2.057 | 2.169 |
| eagle2 | 2.548 | 1.998 | 1.958 | 2.215 | 2.220 | 1.733 | 1.877 | 1.968 | 1.751 | 2.007 | 1.756 | 1.336 | 1.791 | 1.825 |
| eagle | 2.427 | 1.956 | 1.848 | 2.142 | 2.112 | 1.600 | 1.841 | 1.871 | 1.703 | 1.922 | 1.702 | 1.305 | 1.753 | 1.752 |
| suffix (tree) | 1.796 | 1.620 | 1.350 | 1.930 | 1.558 | 1.785 | 1.886 | 1.364 | 1.149 | 1.389 | 1.624 | 1.627 | 1.310 | 1.661 |
| suffix (linear) | 1.828 | 1.630 | 1.383 | 1.967 | 1.544 | 1.773 | 1.890 | 1.389 | 1.156 | 1.386 | 1.618 | 1.618 | 1.327 | 1.659 |
| pld | 1.712 | 1.484 | 1.231 | 1.753 | 1.323 | 1.326 | 1.807 | 1.320 | 1.055 | 1.275 | 1.628 | 1.219 | 1.232 | 1.448 |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

### End-to-end SWE-Bench on vLLM (Sec. 4.3)

- OpenHands runs live against vLLM with the model all-hands/openhands-lm-32b-v0.1-ep3, which was fine-tuned for SWE-Bench and achieves 37.2% on [SWE-Bench Verified](../benchmarks/swe-bench-verified.md).[^oliaroSuffixDecodingExtremeSpeculative2024]
- vLLM is deployed on 4 H100 GPUs with 4-way tensor parallelism and prefix caching enabled. Figure 6 states a concurrency of 8 tasks, and Appendix A.1.1 states a maximum of 16 concurrent workers.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The baseline is vLLM's native PLD, because no model-based method has a draft model trained for this LLM.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Decoding time takes a majority of the time across all SWE-Bench tasks, dominating prefilling and agentic actions (code execution).[^oliaroSuffixDecodingExtremeSpeculative2024]
- SuffixDecoding outperforms PLD by 1.3-3×, leading to a 1.8-4.5× speculative speedup over vanilla decoding.[^oliaroSuffixDecodingExtremeSpeculative2024]
- SuffixDecoding exactly preserves the output distribution of the LLM, so it matches the original model's 37.2% score on SWE-Bench Verified.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Hybrid fallback threshold $\tau$ (Appendix B.1)

Spec-Bench speedup (Table 3). EAGLE-3 achieves a MAT of approximately 4.65 tokens/step on Spec-Bench.[^oliaroSuffixDecodingExtremeSpeculative2024]

| $\tau$ | coding | qa | math | reasoning | stem | writing | Overall |
|---|---|---|---|---|---|---|---|
| 7 | 3.44 | 2.40 | 3.14 | 2.50 | 2.87 | 2.83 | 2.50 |
| 6 | 3.19 | 2.22 | 2.88 | 2.30 | 2.68 | 2.61 | 2.31 |
| 5 | 3.25 | 2.28 | 2.70 | 2.35 | 2.74 | 2.70 | 2.37 |
| 4 | 3.07 | 2.22 | 2.72 | 2.25 | 2.57 | 2.64 | 2.25 |
| 3 | 2.88 | 2.09 | 2.54 | 2.10 | 2.39 | 2.50 | 2.13 |
| 2 | 2.73 | 2.04 | 2.40 | 2.01 | 2.19 | 2.36 | 2.03 |
| 1 | 2.28 | 1.86 | 2.01 | 1.69 | 1.90 | 2.12 | 1.80 |
| 0 (suffix only) | 1.83 | 1.77 | 1.97 | 1.39 | 1.39 | 1.33 | 1.66 |

AgenticSQL speedup (Table 4):[^oliaroSuffixDecodingExtremeSpeculative2024]

| $\tau$ | Classify | Extract | Enrich | Combine | SQL | Overall |
|---|---|---|---|---|---|---|
| 0 (suffix only) | 3.02 | 9.85 | 10.41 | 4.85 | 3.09 | 5.35 |
| 1 | 2.31 | 7.03 | 8.37 | 3.38 | 2.17 | 3.95 |
| 2 | 2.24 | 7.14 | 7.97 | 3.33 | 2.29 | 3.80 |
| 3 | 2.22 | 5.51 | 5.68 | 3.52 | 2.20 | 3.22 |
| 7 | 2.06 | 6.79 | 7.10 | 3.44 | 2.29 | 3.66 |

### Ablations (simulated verifier)

- Global vs per-request tree on AgenticSQL: using both trees performs better than using one, except on the Enrich and Extract steps. The global tree outperforms the per-request tree on all tasks except Combine, which heavily re-uses tokens from its context.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Open-ended workloads ([WildChat](../datasets/wildchat.md) and [Magicoder](../datasets/magicoder.md), $\alpha=1$): with suffix tree sizes between 256 and 10,000 output examples, the speedup consistently improves as the tree grows, while the acceptance rate does not change much.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Input distribution shift: a tree trained on 4,000 WildChat output examples and then served [Spider](../datasets/spider.md) requests (DAIL-SQL prompts) achieves 1.5× speedup and 8% acceptance rate without adaptation, against 2.6× speedup and 20% acceptance rate if trained on 500 Spider examples. After observing 500 SpiderSQL requests and adapting online, performance is almost indistinguishable from offline training on the 500 SpiderSQL examples.[^oliaroSuffixDecodingExtremeSpeculative2024]

### Scalability and memory (Appendix B, Table 2, SWE-Bench requests)

| Total # entries | Total # tokens | Memory footprint (MB) | Avg update time per token (μs) | Avg lookup time per speculated token (μs) |
|---|---|---|---|---|
| 1 K entries | 27 M | 1670 MB | 3.95 | 12.18 |
| 5 K entries | 143 M | 2980 MB | 4.06 | 10.93 |
| 10 K entries | 285 M | 4070 MB | 4.05 | 12.00 |
| 15 K entries | 429 M | 5110 MB | 4.07 | 11.62 |
| 20 K entries | 572 M | 6150 MB | 4.04 | 11.64 |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

The paper estimates that with 144GB of CPU memory per A100 GPU (AWS p4d.24xlarge) and about 5000 tokens per second for Llama-8B on an A100, SuffixDecoding can cache 31 days of generated tokens per A100 GPU before hitting CPU memory limits.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Limitations

- On non-agentic workloads such as Spec-Bench, SuffixDecoding alone is outperformed by EAGLE-2/3 and Token Recycling. The paper includes Spec-Bench to stress-test this limitation.[^oliaroSuffixDecodingExtremeSpeculative2024]
- When both trees are present, SuffixDecoding may sometimes choose a speculation tree from the per-request tree when the global tree would have been better (small degradations on Enrich and Extract). The paper says improvements to the scoring mechanism may help.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The global tree can become large with many previous outputs. Beyond the CPU memory limit, cache eviction (for example LRU) is needed. It is described as straightforward to add, not as implemented.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Integration with batch-level speculation control (TurboSpec, AdaServe) is left to future work.[^oliaroSuffixDecodingExtremeSpeculative2024]
- AgenticSQL is a proprietary application.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The ablations use a simulated verifier under greedy sampling, not real hardware.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The paper has no dedicated limitations section.

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [SuffixDecoding](../methods/suffix-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Baselines: [EAGLE-2](../methods/eagle-2.md), [EAGLE-3](../methods/eagle-3.md), [Prompt-lookup decoding](../methods/prompt-lookup-decoding.md), [Token Recycling](../methods/token-recycling.md)
- Systems built on or used: [vLLM](../methods/vllm.md), [OpenHands](../methods/openhands.md)
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md), [SWE-Bench](../benchmarks/swe-bench.md), [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), [MT-Bench](../datasets/mt-bench.md)
- Datasets: [AgenticSQL](../datasets/agenticsql.md), [WildChat](../datasets/wildchat.md), [Magicoder](../datasets/magicoder.md), [Spider](../datasets/spider.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [TurboSpec (arXiv 2406.14066)](240614066v2OptimizingSpeculative.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md)

[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
