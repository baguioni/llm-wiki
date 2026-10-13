---
type: Paper
title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
description: Speculative decoding method that builds a large deterministic draft tree with a parallel shortest-path search and validates it as a cache in one offloaded target-model pass, for running 50B+ models on consumer GPUs.
tags: [speculative-decoding, draft-tree, parameter-offloading, consumer-gpu, quantization, on-device-inference, mobile-specedge]
collections: [mobile-specedge]
authors: [Ruslan Svirschevski, Avner May, Zhuoming Chen, Beidi Chen, Zhihao Jia, Max Ryabinin]
year: 2024
doi: 10.48550/arXiv.2406.02532
arxiv: "2406.02532"
arxiv_version: 2406.02532v3
code: https://github.com/yandex-research/specexec
sources:
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
---

# SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices

Text source: arXiv HTML, version `2406.02532v3`.

## Summary

Many open-access LLMs do not fit on consumer GPUs, so their parameters must be offloaded to CPU RAM or SSD. Offloaded inference is bandwidth-bound: generating a single token with Llama 2-70B in 16 bit with offloading on an RTX 3090 takes at least 4.5 seconds (assuming PCIe-4.0 and at least 140GB of DDR5 RAM).[^svirschevskiSpecExecMassivelyParallel2024] With offloading, hundreds or thousands of tokens can be processed in a batch within the same time as one token, which makes the setting a natural fit for [speculative decoding](../methods/speculative-decoding.md).[^svirschevskiSpecExecMassivelyParallel2024] Existing methods do not scale with the draft token budget: the number of tokens accepted by the target model is empirically upper-bounded (approximately by 10 for Llama 2-7B / Llama 2-70B on MTBench) regardless of the number of speculated tokens.[^svirschevskiSpecExecMassivelyParallel2024]

[SpecExec](../methods/specexec.md) (Speculative Execution) uses a capable draft model to deterministically build a large tree of the most probable continuations, treats the tree as a "cache" of target-model probabilities, and validates it with the target model in a single pass.[^svirschevskiSpecExecMassivelyParallel2024] It generates up to 20 tokens per target model iteration, and runs 50B+ parameter LLMs on consumer GPUs with RAM offloading at 4-6 tokens per second with 4-bit quantization or 2-3 tokens per second with 16-bit weights.[^svirschevskiSpecExecMassivelyParallel2024]

## Contributions

- An analysis of the empirical behavior of speculative decoding algorithms with large language models, identifying ways to improve their acceptance rate when scaling to thousands of draft tokens.[^svirschevskiSpecExecMassivelyParallel2024]
- SpecExec, a speculative decoding algorithm that improves the structure of generated draft trees for very large token budgets, producing draft trees that result in 10-20 accepted tokens with sufficiently large budgets.[^svirschevskiSpecExecMassivelyParallel2024]
- A system that runs Llama 2-70B or comparable models interactively at 4-6 tokens/second using 4-bit quantization or 2-3 tokens/second with 16-bit weights on consumer GPUs with offloading, with 10-18x speedups compared to sequential inference on the same hardware.[^svirschevskiSpecExecMassivelyParallel2024]

## Method

### Observations that motivate the design

- With [parameter offloading](../methods/parameter-offloading.md), the total processing time is the maximum of the time to load all parameters and the total computation time. 70B models on a consumer desktop can process thousands of tokens within nearly the same time as a single token.[^svirschevskiSpecExecMassivelyParallel2024]
- Because each offloaded forward pass takes significantly more than a second, a large draft model (7B) is justified, contrary to the popular intuition that favors smaller draft models.[^svirschevskiSpecExecMassivelyParallel2024]
- Sampling from modern LLMs often yields a few high-probability tokens that add up nearly to a probability of 1. For Llama-2 Chat 70B, the top 1-4 tokens cover 90-98% of the entire probability mass.[^svirschevskiSpecExecMassivelyParallel2024]

### Speculative Execution (Algorithm 1)

SpecExec does not propose a new sampling procedure. It runs standard sequential sampling and precomputes, in parallel, the target-model probabilities it expects to need in future steps.[^svirschevskiSpecExecMassivelyParallel2024] Whenever it needs target model probabilities, it looks them up in a speculative cache. On a cache miss it queries the target model for that token and at the same time computes probabilities for potential future tokens chosen with the draft model. Sampling then continues from the cache without querying the target model until the cache is exhausted.[^svirschevskiSpecExecMassivelyParallel2024] Inputs are the prompt, the two models, output length $L$, budget $K$, max depth $D$, and batch size $B$.[^svirschevskiSpecExecMassivelyParallel2024]

Comparison to regular speculative decoding:[^svirschevskiSpecExecMassivelyParallel2024]

| Property | SpecExec | Regular speculative decoding |
|---|---|---|
| Draft tree | Any tree is valid, including a deterministic one built from the most likely tokens | Must be sampled stochastically from draft probabilities |
| Per-token acceptance probability | $P(x_{t+1}\|x_{0:t},\theta_{\text{target}})$ | Higher: ${P(x_{t+1}\|x_{0:t},\theta_{\text{target}})}/{P(x_{t+1}\|x_{0:t},\theta_{\text{draft}})}$ (e.g. [SpecInfer](../methods/specinfer.md)) |
| Equivalence to sequential sampling | For every seed of the random number generator, exactly the same outputs as sequential sampling with the same seed | Only guarantees correct probabilities for the overall generation procedure |

For a small number of draft tokens (for instance, one token) SpecExec is less effective than traditional speculative decoding. With more draft tokens it produces better-structured trees and accepts more tokens for the same draft size.[^svirschevskiSpecExecMassivelyParallel2024]

### Draft tree search (Algorithm 2)

The goal is the tree of $K$ tokens with the highest expected number of accepted tokens, $\arg\max_{\tau\in\mathcal{T}^{K}}\sum_{x_{i}\in\tau}P_{\text{reach}}(x_{i}|\tau)\cdot P_{\text{accept}}(x_{i}|\tau)$, where both terms are approximated with draft model probabilities.[^svirschevskiSpecExecMassivelyParallel2024] This reduces to selecting the $K$ tokens with the highest cumulative draft probability, which is a single-source shortest path (SSSP) problem with non-negative edge weights $-\log P$.[^svirschevskiSpecExecMassivelyParallel2024] SpecExec solves it with a modified parallel Dijkstra algorithm that expands $B>1$ nodes per iteration and keeps the $K$ nearest nodes in a priority queue ordered by negative cumulative log-probability.[^svirschevskiSpecExecMassivelyParallel2024] The depth limit $D$ covers the edge case where the draft model is very confident and the solution is a single sequence of length $K$.[^svirschevskiSpecExecMassivelyParallel2024]

Standard [beam search](../methods/beam-search.md) is suboptimal for this task: it looks for complete sequences while SpecExec needs a tree of partial drafts, and a variant that does not prune out-of-beam hypotheses outperforms it. Algorithm 2 generalizes that variant without manual tuning of length and width.[^svirschevskiSpecExecMassivelyParallel2024]

### Implementation

- The next layer's parameters are loaded in parallel with computing the previous layer's activations, using a dedicated CUDA stream.[^svirschevskiSpecExecMassivelyParallel2024]
- The first few layers of the target model are preloaded on the GPU in the background while drafting.[^svirschevskiSpecExecMassivelyParallel2024]
- All draft tokens are processed in parallel with a merged attention mask, similar to SpecInfer.[^svirschevskiSpecExecMassivelyParallel2024]
- The past key/value caches of both draft and main models stay in GPU memory at all times.[^svirschevskiSpecExecMassivelyParallel2024]
- Target models (and the 7B draft model) are optionally quantized to 4 bits with [GPTQ](../methods/gptq.md), chosen because it is popular among practitioners.[^svirschevskiSpecExecMassivelyParallel2024]
- The code is based on PyTorch and Transformers.[^svirschevskiSpecExecMassivelyParallel2024]

## Experiments & Results

### Setup

- Target models: Llama 2-70B (regular and chat) in 16 bits or quantized to 4 bits with GPTQ; Mixtral 8x7B (quantized with GPTQ) and Llama 3 in fewer setups.[^svirschevskiSpecExecMassivelyParallel2024]
- Baseline: SpecInfer, chosen because it shares a large token budget across multiple stems in a tree.[^svirschevskiSpecExecMassivelyParallel2024]
- Prompts: subsamples of size 100 from [OpenAssistant](../datasets/oasst1.md) conversations, [WikiText-2](../datasets/wikitext-2.md), [MTBench](../datasets/mt-bench.md), and [C4](../datasets/c4.md), measuring the speed of generating 32+ tokens per prompt.[^svirschevskiSpecExecMassivelyParallel2024]
- Hardware: A100, RTX 4090, RTX 4060, RTX 3090, RTX 2080Ti. Batch size 1 in all experiments.[^svirschevskiSpecExecMassivelyParallel2024]
- On the A100 no layers were kept in VRAM, to emulate GPUs like RTX4090 or L40. Observed VRAM use with offloading was in the 12-22 GB range for draft trees up to 2048 tokens with Llama-2-70B RAM offloading.[^svirschevskiSpecExecMassivelyParallel2024]
- Generation rate ("Gen. rate") is the average number of draft model tokens accepted for one target model iteration.[^svirschevskiSpecExecMassivelyParallel2024]

### Probability coverage

Measured on a sample of 512 OpenAssistant conversations, with 64 additional tokens per conversation sampled from the target 70B model's original probabilities.[^svirschevskiSpecExecMassivelyParallel2024] Draft models compared: JackFram-160M, TinyLlama-1.1B-Chat v1.0, Llama-2-Chat 7B and 13B.[^svirschevskiSpecExecMassivelyParallel2024] All draft models eventually get over 90% coverage rate, but Llama-2 Chat 7B makes much more accurate predictions with the first 1-4 tokens. The 13B draft model has roughly the same accuracy as 7B.[^svirschevskiSpecExecMassivelyParallel2024] The coverage curves are reported only as a figure.

### Inference speed with RAM offloading, A100, chat / instruct models (Table 1)

SX = SpecExec, SI = SpecInfer.[^svirschevskiSpecExecMassivelyParallel2024]

| Draft / Target models | Dataset | t | Method | Budget | Gen. rate | Speed, tok/s | Speedup |
|---|---|---|---|---|---|---|---|
| Llama 2-7B / 70B | OAsst | 0.6 | SX | 2048 | 20.60 | 3.12 | 18.7x |
| Llama 2-7B / 70B | OAsst | 0.6 | SI | 1024 | 8.41 | 1.34 | 8.0x |
| Llama 2-7B / 70B | OAsst | 0 | SX | 1024 | 18.8 | 2.74 | 16.4x |
| Llama 2-7B / 70B | OAsst | 0 | SI | 1024 | 7.86 | 1.18 | 7.1x |
| Llama 2-7B / 70B GPTQ | OAsst | 0.6 | SX | 128 | 12.10 | 6.02 | 8.9x |
| Llama 2-7B / 70B GPTQ | OAsst | 0 | SX | 256 | 13.43 | 6.17 | 9.1x |
| Mistral-7B / Mixtral-8x7B | OAsst | 0.6 | SX | 256 | 12.38 | 3.58 | 3.5x |
| Llama 3-8B / 70B | OAsst | 0.6 | SX | 1024 | 18.88 | 2.62 | 15.6x |
| Llama 3-8B / 70B | MTBench | 0.6 | SX | 1024 | 18.16 | 2.79 | 16.6x |
| Llama 3-8B / 70B | MTBench | 0 | SX | 2048 | 21.58 | 2.94 | 17.5x |

The paper states that [Sequoia](../methods/sequoia.md), which uses fixed trees, attains 2.2 tokens per second in the Llama 3-8B/70B setup, compared to 2.8 tokens per second for SpecExec.[^svirschevskiSpecExecMassivelyParallel2024]

### Inference speed with RAM offloading, A100, base models (Table 2)

| Draft / Target models | Dataset | t | Method | Budget | Gen. rate | Speed, tok/s | Speedup |
|---|---|---|---|---|---|---|---|
| Llama 2-7B / 70B | C4 | 0.6 | SX | 2048 | 12.9 | 1.97 | 11.8x |
| Llama 2-7B / 70B | C4 | 0.6 | SI | 1024 | 6.48 | 1.03 | 6.2x |
| Llama 2-7B / 70B | C4 | 0 | SX | 2048 | 16.1 | 2.38 | 14.3x |
| Llama 2-7B / 70B | C4 | 0 | SI | 1024 | 4.78 | 0.75 | 4.5x |
| Llama 2-7B / 70B | WikiText-2 | 0.6 | SX | 2048 | 9.57 | 1.54 | 9.2x |
| Llama 2-7B / 70B | WikiText-2 | 0.6 | SI | 1024 | 4.69 | 0.77 | 4.6x |
| Llama 2-7B / 70B | WikiText-2 | 0 | SX | 2048 | 11.74 | 1.88 | 11.3x |
| Llama 2-7B / 70B | WikiText-2 | 0 | SI | 1024 | 3.71 | 0.62 | 3.6x |
| Llama 2-7B / 70B GPTQ | WikiText-2 | 0.6 | SX | 256 | 6.99 | 3.72 | 5.5x |
| Llama 2-7B / 70B GPTQ | WikiText-2 | 0 | SX | 256 | 8.81 | 4.54 | 6.7x |
| Mistral-7B / Mixtral-8x7B | WikiText-2 | 0.6 | SX | 128 | 6.56 | 3.23 | 3.2x |

All rows: [^svirschevskiSpecExecMassivelyParallel2024]

### Consumer GPUs (Table 3)

SpecExec with offloading, chat/instruct models, Llama 2 70B-GPTQ target model, $t=0.6$, OpenAssistant dataset.[^svirschevskiSpecExecMassivelyParallel2024]

| GPU | Draft model | Budget | Gen. rate | Speed, tok/s | Speedup |
|---|---|---|---|---|---|
| RTX 4090 | Llama 2-7B | 256 | 13.46 | 5.66 | 8.3x |
| RTX 4060 | Llama 2-7B | 128 | 9.70 | 3.28 | 4.6x |
| RTX 3090 | Llama 2-7B | 256 | 14.3 | 3.68 | 10.6x |
| RTX 2080Ti | ShearedLlama-1.3B | 128 | 7.34 | 1.86 | 6.1x |

The RTX 2080Ti run uses [Sheared-Llama-1.3B](xiaShearedLLaMAAccelerating2024.md) as the draft model to lower VRAM requirements, and the whole experiment consumes just over 7 GB of VRAM.[^svirschevskiSpecExecMassivelyParallel2024]

### Draft budget

- For smaller draft budgets SpecExec performs on par with SpecInfer, and it outscales SpecInfer as the number of draft tokens grows.[^svirschevskiSpecExecMassivelyParallel2024]
- SpecExec's margin over SpecInfer is higher on MTBench samples than on C4, and it accepts more tokens with a lower temperature.[^svirschevskiSpecExecMassivelyParallel2024]
- The optimal draft tree size on the A100 is 128-512 for SpecInfer and 1024-2048 for SpecExec. It is typically smaller than the size that maximizes the token acceptance rate, because generation time grows at an accelerating rate beyond a size threshold.[^svirschevskiSpecExecMassivelyParallel2024]

### Inference without offloading (Table 4, A100)

SL-1.3B draft, Vicuna-33B target, SpecExec, budget 128.[^svirschevskiSpecExecMassivelyParallel2024]

| Dataset | t | Gen. rate | Speed, tok/s | Speedup |
|---|---|---|---|---|
| OASST-1 | 0.6 | 5.33 | 31.6 | 2.15x |
| OASST-1 | 0 | 5.4 | 32.94 | 2.24x |
| C4 | 0.6 | 5.1 | 33.3 | 2.26x |
| C4 | 0 | 5.36 | 35.62 | 2.42x |
| WikiText-2 | 0.6 | 4.87 | 30.19 | 1.90x |
| WikiText-2 | 0 | 5.24 | 33.15 | 2.08x |

### Draft model ablation and penalties

- The 7B draft model significantly outperforms JackFram/llama-160m and TinyLlama 1.1B Chat in accepted tokens, both unquantized and quantized to 4 bits with GPTQ. The unquantized 13B model obtains slightly more accepted tokens at the cost of a 26GB memory footprint.[^svirschevskiSpecExecMassivelyParallel2024]
- With token penalties (Llama 2-7B Chat target, TinyLlama-1.1B Chat draft, t=0.6, p=0.9, MT-Bench), accepted tokens per iteration stay stable only with lightweight penalties, and heavier penalties reduce the absolute speedups.[^svirschevskiSpecExecMassivelyParallel2024]

## Limitations

- SpecExec has a lower acceptance rate for any individual token than speculative decoding, and is less effective for small draft budgets.[^svirschevskiSpecExecMassivelyParallel2024]
- Speedups without offloading are less impressive than those for offload settings.[^svirschevskiSpecExecMassivelyParallel2024]
- The offloading experiments need enough RAM to hold the whole model: at least 140 GB for Llama-2-70B in 16 bit, with 192 GB recommended in practice.[^svirschevskiSpecExecMassivelyParallel2024]
- The authors state that the goal was not the fastest possible implementation of local LLM inference. Combining the approach with orthogonal performance improvements is left out of scope.[^svirschevskiSpecExecMassivelyParallel2024]
- The A100 results report forward pass time with offloading even though the GPU can fit a quantized model in memory.[^svirschevskiSpecExecMassivelyParallel2024]
- The paper has no dedicated limitations section.

## Related

- Methods: [SpecExec](../methods/specexec.md), [Speculative decoding](../methods/speculative-decoding.md), [Parameter offloading](../methods/parameter-offloading.md), [GPTQ](../methods/gptq.md), [Beam search](../methods/beam-search.md)
- Methods compared against: [SpecInfer](../methods/specinfer.md), [Sequoia](../methods/sequoia.md)
- Datasets: [OpenAssistant Conversations (OASST1)](../datasets/oasst1.md), [MT-Bench](../datasets/mt-bench.md), [C4](../datasets/c4.md), [WikiText-2](../datasets/wikitext-2.md)
- Papers in this wiki cited by this paper: [Sheared LLaMA](xiaShearedLLaMAAccelerating2024.md)

[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
