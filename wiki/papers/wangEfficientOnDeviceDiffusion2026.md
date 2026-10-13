---
type: Paper
title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
description: llada.cpp, an NPU-aware inference framework that speeds up block-wise diffusion LLM generation on smartphones with multi-block speculative decoding, dual-path progressive revision, and a swap-optimized memory runtime.
tags: [diffusion-llm, on-device-inference, mobile-npu, kv-cache, block-wise-decoding, mobile-specedge]
collections: ["mobile-specedge"]
authors: [Tuowei Wang, Yanfan Sun, Ju Ren]
doi: 10.48550/arXiv.2606.13740
arxiv: "2606.13740"
arxiv_version: 2606.13740v1
sources:
  - id: wangEfficientOnDeviceDiffusion2026
    resource: zotero://select/items/@wangEfficientOnDeviceDiffusion2026
    title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
---

# Efficient On-Device Diffusion LLM Inference with Mobile NPU

Text source: arXiv HTML, version `2606.13740v1`.

## Summary

[Diffusion large language models](../methods/diffusion-llm.md) (dLLMs) denoise multiple tokens in parallel, which shifts the latency bottleneck from output length to the number of denoising steps, but the repeated denoising imposes substantial computation on smartphones.[^wangEfficientOnDeviceDiffusion2026] The paper observes that a dLLM block is a small token batch that maps to dense matrix workloads, which fits the tensor-computation capability of [mobile NPUs](../methods/mobile-npu.md), whereas autoregressive decoding advances one token per step and leaves the NPU underutilized.[^wangEfficientOnDeviceDiffusion2026]

The paper proposes [llada.cpp](../methods/llada-cpp.md), described as the first NPU-aware inference framework for accelerating dLLMs on smartphones.[^wangEfficientOnDeviceDiffusion2026] It reports that llada.cpp reduces [LLaDA](../methods/llada.md)-8B end-to-end latency by 17×-42× over the CPU baseline with prefix [KV cache](../methods/kv-cache.md) reuse while preserving generation quality, and achieves up to 3.9× speedup for LLaDA-8B over an equal-size autoregressive model.[^wangEfficientOnDeviceDiffusion2026]

## Contributions

- Identifies the mismatch between static mobile NPU execution and dynamic block-wise dLLM inference, and characterizes three challenges: token commitment, token revision, and memory access.[^wangEfficientOnDeviceDiffusion2026]
- Proposes llada.cpp, combining algorithmic and system-level optimizations across the NPU, CPU, and system memory.[^wangEfficientOnDeviceDiffusion2026]
- Evaluates llada.cpp across hardware platforms and dLLM workloads against autoregressive and CPU-only baselines.[^wangEfficientOnDeviceDiffusion2026]

## Method

### Background and motivation

- [Block-wise decoding](../methods/block-wise-decoding.md) partitions the output into consecutive blocks (e.g., 32 tokens), decodes blocks left to right so the prefix KV cache can be reused, and denoises tokens within a block in parallel.[^wangEfficientOnDeviceDiffusion2026]
- Four NPU properties are identified: stage-like matrix latency caused by fixed-size tiles, weak support for vector-style and irregular operations, a specialized memory layout (the FP16 path uses 32×32 matrix tiles), and a limited NPU virtual address space.[^wangEfficientOnDeviceDiffusion2026]
- Three mismatches follow. Token-commit level: late denoising steps leave few masked tokens, so NPU forwards are poorly amortized. Token-revision level: committed tokens may still need revision, which causes sparse and irregular KV cache updates. Memory-access level: the working set exceeds the NPU-visible address space, which forces buffer mapping and data swaps.[^wangEfficientOnDeviceDiffusion2026]

Accuracy impact of block-wise decoding with prefix KV cache reuse (Table 1):[^wangEfficientOnDeviceDiffusion2026]

| Dataset | Vanilla dLLM decoding | Block-Wise Decoding | Δ |
|---|---|---|---|
| [GSM8K](../datasets/gsm8k.md) | 78 / 200 (39.0%) | 65 / 200 (32.5%) | -6.5 |
| [BoolQ](../datasets/boolq.md) | 165 / 200 (82.5%) | 157 / 200 (78.5%) | -4.0 |
| [ARC-C](../datasets/arc-c.md) | 168 / 200 (84.0%) | 161 / 200 (80.5%) | -3.5 |
| [HellaSwag](../datasets/hellaswag.md) | 102 / 200 (51.0%) | 93 / 200 (46.5%) | -4.5 |

Latency of one LLaDA-8B denoising step pass on the CPU and NPU (Table 2):[^wangEfficientOnDeviceDiffusion2026]

| Token work | CPU latency | NPU latency | Speedup |
|---|---|---|---|
| 32 | 4239.6 ms | 478.1 ms | 8.87× |
| 64 | 7728.4 ms | 861.6 ms | 8.97× |
| 128 | 14758.7 ms | 1531.6 ms | 9.64× |

### Multi-Block Speculative Decoding (MBSD)

- The *decoding window* is the token range in each NPU forward pass. It may extend beyond the current block. Future-block tokens are marked as *draft*: they record early denoising progress but neither update the prefix KV cache nor affect the commitment order, and they are accepted only if they satisfy the commitment criterion when their block becomes current.[^wangEfficientOnDeviceDiffusion2026]
- **Continuous sliding.** Token commitment within a block follows a left-to-right frontier. Once tokens on the left side of the window are committed, the window slides right at unchanged size into the next block.[^wangEfficientOnDeviceDiffusion2026]
- **Adaptive lookahead.** When the count of remaining masked tokens in the current block drops below a threshold, the runtime greedily appends future-block tokens according to an offline-profiled NPU latency table of stepwise latency buckets. An expansion is accepted only if it stays within the profiled latency allowance and its memory usage fits the budget.[^wangEfficientOnDeviceDiffusion2026]

### Dual-Path Progressive Revision (DPPR)

- **Staged token stabilization (STS).** Each generated position is invisible (IV), visible (V), or stable (S). Tokens meeting the visibility threshold $\theta_{\text{visible}}$ become visible and tokens meeting the stability threshold $\theta_{\text{stable}}$ become stable. Both can be exposed for parallel decoding, but only stable tokens are permanently reused as prefix context. If no token meets $\theta_{\text{visible}}$, the most confident token is promoted to visible.[^wangEfficientOnDeviceDiffusion2026]
- **Sparse cache refresh (SCR).** A CPU-side path asynchronously recomputes token confidence, refreshes token identities, and updates KV states. It reuses the same HMX-specialized weights as the NPU model through specialized CPU kernels that decode the HMX tile permutation and quantized storage order. Under a delayed-merge policy, refreshed entries are merged into the prefix KV cache only at step boundaries.[^wangEfficientOnDeviceDiffusion2026]
- **Selective logits skipping (SLS).** Logits computation is offloaded to the CPU path. For stable tokens, output projection, confidence estimation, and sampling logic are skipped.[^wangEfficientOnDeviceDiffusion2026]

### Swap-Optimized Memory Runtime (SOMR)

- **Graph-guided buffer mapping.** Tensors are classified as long-lived (model weights, KV cache) or short-lived (activations, temporary tensors) from the computational graph. When the VA budget cannot keep all long-lived data resident, a profile-guided placement algorithm decides which objects stay resident, using the size of long-lived tensors, NPU execution time, and transfer time. Resident tensors get stable VA regions packed by consumption order; short-lived tensors with non-overlapping live ranges share the same VA range.[^wangEfficientOnDeviceDiffusion2026]
- **Pipeline-based data transfer.** Mapping metadata and staging data are prefetched while the NPU executes preceding operators. Double-buffered staging uses two reusable staging slots in the NPU-visible VA space that exchange roles after each operator.[^wangEfficientOnDeviceDiffusion2026]

### Implementation

llada.cpp is built on [llama.cpp](../methods/llama-cpp.md) and extends it with over 12K lines of code. It targets Qualcomm Hexagon NPUs. It consists of a Hexagon NPU operator library (FP16 matrix multiplication, Q4\_0 matrix multiplication, FlashAttention over FP16 KV states, RMSNorm, elementwise operators, shared-memory mapping, a device-side worker pool) and an Android host runtime that invokes the device library through FastRPC and uses RPCMEM shared memory.[^wangEfficientOnDeviceDiffusion2026]

## Experiments & Results

### Setup

| Device | SoC | Memory | NPU INT8 TOPS |
|---|---|---|---|
| OnePlus 12 | SM8650 | 16 GB LPDDR5X | 45 |
| OnePlus Ace5 Pro | SM8750 | 16 GB LPDDR5X | 65.25 |
| OnePlus 15 | SM8850 | 16 GB LPDDR5X | 89.4 |

All rows: [^wangEfficientOnDeviceDiffusion2026]

- The OnePlus Ace5 Pro (SM8750) is the primary platform for all end-to-end, ablation, and energy experiments. SM8850 uses the CPU FlashAttention operator due to runtime support limitations.[^wangEfficientOnDeviceDiffusion2026]
- Models: LLaDA-8B-Instruct (primary), Llama-3-8B-Instruct as an autoregressive reference, and [Dream](../methods/dream.md)-7B for a cross-model test. All models use Q4\_0 low-bit weight quantization.[^wangEfficientOnDeviceDiffusion2026]
- Tasks: 200-sample subsets of GSM8K, BoolQ, ARC-C, and HellaSwag.[^wangEfficientOnDeviceDiffusion2026]
- Baselines: CPU baseline (vanilla dLLM decoding), CPU with prefix KV cache reuse, and NPU baseline (vanilla denoising schedule with dense Transformer computation on the NPU). Their denoising step count is set to the number of target generated tokens by default.[^wangEfficientOnDeviceDiffusion2026]
- Settings: visibility and stability thresholds of 0.7 and 0.9; default block size of 32 tokens; temperature 0; latency measured for 32, 64, or 128 target tokens over five cases per dataset, each run repeated three times.[^wangEfficientOnDeviceDiffusion2026]

### End-to-end latency

- For 128-token generation, llada.cpp is slower than Llama on SM8650 but faster than Llama on SM8750 and SM8850.[^wangEfficientOnDeviceDiffusion2026]
- The relative speedup does not grow monotonically across SoC generations, because the baselines also benefit from newer platforms.[^wangEfficientOnDeviceDiffusion2026]
- Dream-7B on SM8750 shows acceleration trends similar to LLaDA-8B.[^wangEfficientOnDeviceDiffusion2026]
- Per-device and per-dataset latencies are given only in Figures 11 and 12; exact values are not stated in the text.

### Performance breakdown (Table 6)

128-token generation, GSM8K, SM8750. Each row adds one component to the row above.[^wangEfficientOnDeviceDiffusion2026]

| Method | Latency | Rel. Gain | Tot. Gain |
|---|---|---|---|
| CPU | 2996.2 s | 1.00× | 1.00× |
| CPU + prefix KV cache | 607.0 s | 4.94× | 4.94× |
| NPU | 341.2 s | 1.78× | 8.78× |
| NPU + prefix KV cache | 87.0 s | 3.92× | 34.44× |
| + SOMR | 71.6 s | 1.22× | 41.87× |
| + MBSD | 59.8 s | 1.20× | 50.08× |
| + STS | 16.4 s | 3.65× | 182.55× |
| + SLS | 15.8 s | 1.04× | 189.38× |
| + SCR | 16.1 s | 0.98× | 186.34× |

Selective logits skipping reduces latency by more than 10% in some cases.[^wangEfficientOnDeviceDiffusion2026]

### Generation quality (Table 5)

Accuracy on four 200-sample datasets.[^wangEfficientOnDeviceDiffusion2026]

| Setting | GSM8K | BoolQ | ARC-C | HellaSwag |
|---|---|---|---|---|
| LLaDA CPU | 39.0 | 82.5 | 84.0 | 51.0 |
| LLaDA llada.cpp | 43.5 | 80.5 | 85.0 | 49.5 |
| Llama CPU | 30.0 | 83.5 | 71.0 | 67.0 |
| Llama NPU | 31.0 | 77.5 | 78.5 | 60.0 |
| Ablation: CPU | 39.0 | 82.5 | 84.0 | 51.0 |
| Ablation: NPU | 41.5 | 82.0 | 83.5 | 50.0 |
| Ablation: NPU + MBSD | 37.5 | 79.5 | 82.0 | 46.0 |
| Ablation: NPU + MBSD + DPPR | 43.5 | 80.5 | 85.0 | 49.5 |

Multi-block speculative decoding alone can reduce accuracy, and dual-path progressive revision brings quality back close to the CPU path.[^wangEfficientOnDeviceDiffusion2026]

### Sensitivity

- Triggering future-block admission at four remaining masked tokens gives the lowest latency.[^wangEfficientOnDeviceDiffusion2026]
- With the temporary staging budget fixed at 256 MB, the model remains runnable even when no weights are kept NPU-visible across steps, but synchronous staging time increases.[^wangEfficientOnDeviceDiffusion2026]

### Memory boundary (Table 7, SM8750)

| Method | Token Budget | Target | Output |
|---|---|---|---|
| No SOMR | 256 | 256 | failed |
| llada.cpp with SOMR | 256 | 256 | 224 |
| No SOMR | 512 | 512 | failed |
| Paging only | 512 | 512 | failed |
| llada.cpp with SOMR | 512 | 512 | 401 |

All rows: [^wangEfficientOnDeviceDiffusion2026]

### Energy

On SM8750 with a fixed 128-token workload, llada.cpp reduces both average power and per-request energy for LLaDA, while NPU-accelerated Llama shows higher average power than its CPU setting.[^wangEfficientOnDeviceDiffusion2026] Exact power and energy values are given only in Figure 14.

## Limitations

- The implementation targets Qualcomm Hexagon NPUs only; the paper states the core design can be adapted to other mobile platforms with similar execution paradigms.[^wangEfficientOnDeviceDiffusion2026]
- For 128-token generation llada.cpp is still slower than Llama on SM8650, where NPU compute is more limited.[^wangEfficientOnDeviceDiffusion2026]
- Quality is evaluated on 200-sample subsets, and llada.cpp scores below LLaDA CPU on BoolQ (80.5 vs 82.5) and HellaSwag (49.5 vs 51.0).[^wangEfficientOnDeviceDiffusion2026]
- In the memory-boundary runs, llada.cpp outputs 224 tokens for a 256 target and 401 tokens for a 512 target.[^wangEfficientOnDeviceDiffusion2026]
- Sparse cache refresh adds a small latency overhead (15.8 s to 16.1 s).[^wangEfficientOnDeviceDiffusion2026]
- The paper has no dedicated limitations section.

## Related

- Proposed system and techniques: [llada.cpp](../methods/llada-cpp.md), [Multi-block speculative decoding](../methods/multi-block-speculative-decoding.md)
- Builds on: [Diffusion LLM](../methods/diffusion-llm.md), [Block-wise decoding](../methods/block-wise-decoding.md), [KV cache](../methods/kv-cache.md), [Mobile NPU](../methods/mobile-npu.md), [llama.cpp](../methods/llama-cpp.md)
- Models: [LLaDA](../methods/llada.md), [Dream](../methods/dream.md)
- Related systems named by the paper: [llm.npu](../methods/llm-npu.md), [HeteroLLM](../methods/heterollm.md), [Fast-dLLM](../methods/fast-dllm.md)
- Datasets: [GSM8K](../datasets/gsm8k.md), [BoolQ](../datasets/boolq.md), [ARC-C](../datasets/arc-c.md), [HellaSwag](../datasets/hellaswag.md)

[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
