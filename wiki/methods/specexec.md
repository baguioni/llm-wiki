---
type: Method
title: SpecExec
description: Speculative decoding method that deterministically builds a large draft tree of the most probable continuations with a parallel shortest-path search and validates it as a cache in one target-model pass.
tags: [speculative-decoding, tree-based-speculation, draft-tree, parameter-offloading, consumer-gpu]
sources:
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
---

# SpecExec

## Overview

SpecExec (Speculative Execution) is a [speculative decoding](../methods/speculative-decoding.md) method for running large models on consumer hardware with RAM offloading. It uses a capable draft model to deterministically build a large tree of the most probable continuations, treats the tree as a "cache" of target-model probabilities, and validates it with the target model in a single pass.[^svirschevskiSpecExecMassivelyParallel2024] It generates up to 20 tokens per target model iteration, and runs 50B+ parameter LLMs on consumer GPUs with RAM offloading at 4–6 tokens per second with 4-bit quantization or 2–3 tokens per second with 16-bit weights.[^svirschevskiSpecExecMassivelyParallel2024]

The SpecEdge paper groups SpecExec with [Sequoia](../methods/sequoia.md) as [tree-based](../methods/tree-based-speculation.md) methods that prune unpromising branches, and uses its tree-based drafting on edge GPUs.[^parkSpecEdgeScalableEdgeAssisted2025]

## How it works

- **Motivation.** With offloading, the total processing time is the maximum of the time to load all parameters and the total computation time, so 70B models on a consumer desktop can process thousands of tokens within nearly the same time as a single token. Because each offloaded forward pass takes significantly more than a second, a large (7B) draft model is justified.[^svirschevskiSpecExecMassivelyParallel2024]
- **Speculative cache.** SpecExec does not propose a new sampling procedure. It runs standard sequential sampling and precomputes, in parallel, the target-model probabilities it expects to need in future steps. Whenever it uses target model probabilities, it looks them up in a speculative cache.[^svirschevskiSpecExecMassivelyParallel2024]
- **Any tree is valid.** The algorithm does not need the draft tree to follow a known probability distribution, so it produces correct samples with any draft tree, even a deterministic one.[^svirschevskiSpecExecMassivelyParallel2024]
- **Acceptance.** A token is accepted with probability $P(x_{t+1}|x_{0:t},\theta_{\text{target}})$, which is lower than the acceptance probability of the original speculative decoding for any individual token.[^svirschevskiSpecExecMassivelyParallel2024]
- **Draft tree search.** The best tree of $K$ tokens is the set of $K$ tokens with the highest cumulative draft probability, a single-source shortest path (SSSP) problem. SpecExec solves it with a modified parallel Dijkstra algorithm that expands $B>1$ nodes per iteration, with a depth limit $D$.[^svirschevskiSpecExecMassivelyParallel2024]
- **Equivalence.** For every seed of the random number generator, SpecExec produces exactly the same outputs as sequential sampling with the same seed.[^svirschevskiSpecExecMassivelyParallel2024]
- **Implementation.** All draft tokens are processed in parallel with a merged attention mask, similar to [SpecInfer](../methods/specinfer.md). The code is based on PyTorch and Transformers.[^svirschevskiSpecExecMassivelyParallel2024]

The SpecEdge paper describes the tree construction it adopts from Sequoia and SpecExec as follows: given a tree size, each forward pass of the draft model generates multiple parallel candidate tokens, which are pruned by cumulative log probability so that the total stays within the tree budget. The number of forward passes (the draft tree depth) is a hyperparameter.[^parkSpecEdgeScalableEdgeAssisted2025]

## Variants

- **Beam search variant.** A version of SpecExec that uses beam search in place of the parallel SSSP search is suboptimal. The SSSP algorithm generalizes a variant that does not prune out-of-beam hypotheses, without manual tuning of length and width.[^svirschevskiSpecExecMassivelyParallel2024]
- **SpecExec drafting in SpecEdge.** SpecEdge uses SpecExec's tree-based drafting for its initial draft, with draft tree size 32 per request, and extends the tree proactively from the single path with the highest cumulative log probability while the server verifies.[^parkSpecEdgeScalableEdgeAssisted2025]

## Papers using it

### Original paper ([Svirschevski et al. 2024](../papers/svirschevskiSpecExecMassivelyParallel2024.md))

Inference speed with RAM offloading on an A100 GPU, batch size 1. Gen. rate is the average number of draft model tokens accepted for one target model iteration.[^svirschevskiSpecExecMassivelyParallel2024]

| Draft / Target models | Dataset | t | Budget | Gen. rate | Speed, tok/s | Speedup |
|---|---|---|---|---|---|---|
| Llama 2-7B / 70B | OAsst | 0.6 | 2048 | 20.60 | 3.12 | 18.7x |
| Llama 2-7B / 70B | OAsst | 0 | 1024 | 18.8 | 2.74 | 16.4x |
| Llama 2-7B / 70B GPTQ | OAsst | 0.6 | 128 | 12.10 | 6.02 | 8.9x |
| Llama 2-7B / 70B GPTQ | OAsst | 0 | 256 | 13.43 | 6.17 | 9.1x |
| Mistral-7B / Mixtral-8x7B | OAsst | 0.6 | 256 | 12.38 | 3.58 | 3.5x |
| Llama 3-8B / 70B | OAsst | 0.6 | 1024 | 18.88 | 2.62 | 15.6x |
| Llama 3-8B / 70B | [MTBench](../datasets/mt-bench.md) | 0.6 | 1024 | 18.16 | 2.79 | 16.6x |
| Llama 3-8B / 70B | MTBench | 0 | 2048 | 21.58 | 2.94 | 17.5x |
| Llama 2-7B / 70B | [C4](../datasets/c4.md) | 0.6 | 2048 | 12.9 | 1.97 | 11.8x |
| Llama 2-7B / 70B | C4 | 0 | 2048 | 16.1 | 2.38 | 14.3x |
| Llama 2-7B / 70B | [WikiText-2](../datasets/wikitext-2.md) | 0.6 | 2048 | 9.57 | 1.54 | 9.2x |
| Llama 2-7B / 70B | WikiText-2 | 0 | 2048 | 11.74 | 1.88 | 11.3x |
| Llama 2-7B / 70B GPTQ | WikiText-2 | 0.6 | 256 | 6.99 | 3.72 | 5.5x |
| Llama 2-7B / 70B GPTQ | WikiText-2 | 0 | 256 | 8.81 | 4.54 | 6.7x |
| Mistral-7B / Mixtral-8x7B | WikiText-2 | 0.6 | 128 | 6.56 | 3.23 | 3.2x |

All rows: [^svirschevskiSpecExecMassivelyParallel2024]

- The OAsst and MTBench rows use chat / instruct models and the C4 and WikiText-2 rows use base models.[^svirschevskiSpecExecMassivelyParallel2024]
- Against SpecInfer on Llama 2-7B / 70B, OAsst, t=0.6: SpecExec reaches 3.12 tok/s (18.7x) with budget 2048, and SpecInfer 1.34 tok/s (8.0x) with budget 1024.[^svirschevskiSpecExecMassivelyParallel2024]
- Against Sequoia: the paper states that Sequoia attains 2.2 tokens per second in the Llama 3-8B/70B setup, compared to 2.8 tokens per second for SpecExec.[^svirschevskiSpecExecMassivelyParallel2024]
- Consumer GPUs with a Llama 2 70B-GPTQ target, $t=0.6$, OpenAssistant: RTX 4090 5.66 tok/s (8.3x), RTX 4060 3.28 tok/s (4.6x), RTX 3090 3.68 tok/s (10.6x), and RTX 2080Ti with a [ShearedLlama-1.3B](../methods/sheared-llama.md) draft 1.86 tok/s (6.1x).[^svirschevskiSpecExecMassivelyParallel2024]
- The optimal draft tree size on the A100 is 128–512 for SpecInfer and 1024–2048 for SpecExec.[^svirschevskiSpecExecMassivelyParallel2024]

### SpecEdge ([Park et al. 2025](../papers/parkSpecEdgeScalableEdgeAssisted2025.md))

- SpecEdge employs SpecExec's tree-based drafting for the initial draft on the edge GPU, and states that its design is not tied to a specific drafting technique.[^parkSpecEdgeScalableEdgeAssisted2025]
- For both SpecEdge and its server-only speculative decoding baseline, the tree construction algorithm is adopted from Sequoia and SpecExec, with draft tree size 32 for each request. The server-only baseline uses the optimal draft tree depth found by exhaustive search.[^parkSpecEdgeScalableEdgeAssisted2025]
- With this drafting, the server-only baseline generates between 2.72±1.37 and 4.60±1.93 tokens per verification across the paper's batch-size-1 tables.[^parkSpecEdgeScalableEdgeAssisted2025]
- SpecEdge reports 1.91× better cost efficiency through 2.22× server throughput compared to the server-only baseline.[^parkSpecEdgeScalableEdgeAssisted2025]
- These generation rates are not comparable with the original paper's: the original paper uses budgets of 128 to 2048 draft tokens with a 7B draft model and RAM offloading, and SpecEdge uses a draft tree size of 32 with draft models from 160M to 1.7B.[^svirschevskiSpecExecMassivelyParallel2024][^parkSpecEdgeScalableEdgeAssisted2025]

## Strengths & Limitations

- With enough draft tokens SpecExec produces better-structured trees and accepts more tokens for the same draft size. Draft trees result in 10–20 accepted tokens with sufficiently large budgets.[^svirschevskiSpecExecMassivelyParallel2024]
- For a small number of draft tokens (for instance, one token) SpecExec is less effective than traditional speculative decoding.[^svirschevskiSpecExecMassivelyParallel2024]
- SpecExec can also deliver measurable speedups in inference without offloading. On an A100 with a Vicuna-33B target and budget 128 on C4 at t=0, the speedup is 2.42x at 35.62 tok/s.[^svirschevskiSpecExecMassivelyParallel2024]
- The offloading setting needs enough RAM to hold the whole model: at least 140 GB for Llama-2-70B in 16 bit.[^svirschevskiSpecExecMassivelyParallel2024]

## Related

- [Tree-based speculation](../methods/tree-based-speculation.md), [Sequoia](../methods/sequoia.md), [SpecInfer](../methods/specinfer.md), [Speculative decoding](../methods/speculative-decoding.md), [Sheared LLaMA](../methods/sheared-llama.md)
- Papers: [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md), [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md)
- [Quantization of the target and the draft in speculative decoding](../analyses/quantization-in-speculative-decoding.md) (4-bit GPTQ against 16-bit targets)

[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
