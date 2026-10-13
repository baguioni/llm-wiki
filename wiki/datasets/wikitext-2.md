---
type: Dataset
title: WikiText-2
description: Text dataset used in the wiki's papers as a prompt source for speculative decoding speed tests, as a perplexity test set for quantization, and as a calibration set for layer pruning.
tags: [dataset, perplexity, speculative-decoding, quantization, calibration]
sources:
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
---

# WikiText-2

Also written WikiText2 in one source.[^weiSDFPSpeculativeDecoding2026]

## Overview

The wiki's papers use WikiText-2 in three different roles:

- **Prompt source for speed tests.** SpecExec and SpecEdge draw prompts from it to measure [speculative decoding](../methods/speculative-decoding.md) speed.[^svirschevskiSpecExecMassivelyParallel2024][^parkSpecEdgeScalableEdgeAssisted2025]
- **Perplexity test set.** Cai et al. measure perplexity on it to compare two quantization settings.[^caiYourNPUReady2026]
- **Calibration set.** SDFP computes the Fisher Information Trace (FIT) score of each transformer layer on it, and calls it a general-purpose dataset.[^weiSDFPSpeculativeDecoding2026]

## Composition

- SpecExec refers to its items as WikiText-2 articles.[^svirschevskiSpecExecMassivelyParallel2024]
- Sizes and splits are not stated in the wiki's papers.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Svirschevski et al. 2024](../papers/svirschevskiSpecExecMassivelyParallel2024.md) | Prompts for [SpecExec](../methods/specexec.md) and [SpecInfer](../methods/specinfer.md) speed | Subsample of size 100, 32+ generated tokens per prompt | See the speed tables[^svirschevskiSpecExecMassivelyParallel2024] |
| [Park et al. 2025](../papers/parkSpecEdgeScalableEdgeAssisted2025.md) | Prompts for SpecEdge against server-only speculative decoding | Vicuna-33B and Llama2-13B-chat-hf targets, up to 256 output tokens per query | See the speed tables[^parkSpecEdgeScalableEdgeAssisted2025] |
| [Cai et al. 2026](../papers/caiYourNPUReady2026.md) | Perplexity under W4 and W4A16 quantization | Llama-3.2-1B, Llama-3.2-3B | See the quality table[^caiYourNPUReady2026] |
| [Wei et al. 2026](../papers/weiSDFPSpeculativeDecoding2026.md) | Calibration data for FIT-based layer pruning | LLaMA-2 family | No number on WikiText-2 itself[^weiSDFPSpeculativeDecoding2026] |

### Protocols

- Svirschevski et al. use subsamples of size 100 from each of their prompt datasets and measure the speed of generating 32+ tokens per prompt.[^svirschevskiSpecExecMassivelyParallel2024]
- Park et al. generate up to 256 output tokens per query, report metrics over the output tokens after prefill, and use off-the-shelf target and draft models without fine-tuning.[^parkSpecEdgeScalableEdgeAssisted2025]
- Wei et al. compute FIT scores on WikiText2, rank layers by sensitivity, and state that this general dataset generalizes across tasks, so no task-specific dataset is needed.[^weiSDFPSpeculativeDecoding2026] Their layer-wise FIT heatmaps are computed on WikiText2 for LLaMA-2-13B and LLaMA-2-7B.[^weiSDFPSpeculativeDecoding2026]

### Task quality: perplexity

Lower is better. W4 is 4-bit weight quantization, and W4A16 is 4-bit weight and 16-bit activation quantization.[^caiYourNPUReady2026]

| Model | Setting | PPL | Relative $\Delta$ PPL (%) | Reported by |
|---|---|---|---|---|
| Llama-3.2-1B | W4 | 16.73 | baseline | [^caiYourNPUReady2026] |
| Llama-3.2-1B | W4A16 | 21.81 | +30.36% | [^caiYourNPUReady2026] |
| Llama-3.2-3B | W4 | 11.50 | baseline | [^caiYourNPUReady2026] |
| Llama-3.2-3B | W4A16 | 11.62 | +1.04% | [^caiYourNPUReady2026] |

The paper reads this as strong model dependence of the accuracy cost of activation quantization.[^caiYourNPUReady2026]

### Speed: SpecExec with RAM offloading

A100 GPU, base models. Gen. rate is the average number of draft model tokens accepted for one target model iteration. Budget is the draft token budget.[^svirschevskiSpecExecMassivelyParallel2024]

| Draft / target | Method | Setting | Gen. rate | Speed (tok/s) | Speedup | Reported by |
|---|---|---|---|---|---|---|
| Llama 2-7B / 70B | SpecExec | t=0.6, budget 2048, offloading | 9.57 | 1.54 | 9.2x | [^svirschevskiSpecExecMassivelyParallel2024] |
| Llama 2-7B / 70B | SpecInfer | t=0.6, budget 1024, offloading | 4.69 | 0.77 | 4.6x | [^svirschevskiSpecExecMassivelyParallel2024] |
| Llama 2-7B / 70B | SpecExec | t=0, budget 2048, offloading | 11.74 | 1.88 | 11.3x | [^svirschevskiSpecExecMassivelyParallel2024] |
| Llama 2-7B / 70B | SpecInfer | t=0, budget 1024, offloading | 3.71 | 0.62 | 3.6x | [^svirschevskiSpecExecMassivelyParallel2024] |
| Llama 2-7B / 70B GPTQ | SpecExec | t=0.6, budget 256, offloading | 6.99 | 3.72 | 5.5x | [^svirschevskiSpecExecMassivelyParallel2024] |
| Llama 2-7B / 70B GPTQ | SpecExec | t=0, budget 256, offloading | 8.81 | 4.54 | 6.7x | [^svirschevskiSpecExecMassivelyParallel2024] |
| Mistral-7B / Mixtral-8x7B | SpecExec | t=0.6, budget 128, offloading | 6.56 | 3.23 | 3.2x | [^svirschevskiSpecExecMassivelyParallel2024] |

### Speed: SpecExec without offloading

A100 GPU, SpecExec, draft budget 128.[^svirschevskiSpecExecMassivelyParallel2024]

| Draft / target | Method | Setting | Gen. rate | Speed (tok/s) | Speedup | Reported by |
|---|---|---|---|---|---|---|
| SL-1.3B / Vicuna-33B | SpecExec | t=0.6, budget 128, no offloading | 4.87 | 30.19 | 1.90x | [^svirschevskiSpecExecMassivelyParallel2024] |
| SL-1.3B / Vicuna-33B | SpecExec | t=0, budget 128, no offloading | 5.24 | 33.15 | 2.08x | [^svirschevskiSpecExecMassivelyParallel2024] |

### Speed: SpecEdge vs server-only speculative decoding

Batch size 1, temperature 0.7, a server-side NVIDIA A100 and edge-side NVIDIA RTX4090 GPUs. SL is Sheared Llama-1.3B, TL is Tiny Llama-1.1B, JF is JackFram-160M. The ratio in parentheses is SpecEdge over server-only.[^parkSpecEdgeScalableEdgeAssisted2025]

| Target / draft | Setting | Gen. tokens per verify: server-only | SpecEdge | Server throughput (tok/s): server-only | SpecEdge | Cost efficiency (1k toks/$): server-only | SpecEdge | Reported by |
|---|---|---|---|---|---|---|---|---|
| Vicuna 33B / SL 1.3B | batch size 1, temperature 0.7 | 3.42±1.45 | 4.19±1.98 | 27.26 | 47.94 (1.76x) | 24.23 | 36.42 (1.50x) | [^parkSpecEdgeScalableEdgeAssisted2025] |
| Llama2 13B / TL 1.1B | batch size 1, temperature 0.7 | 3.52±1.37 | 3.61±1.40 | 37.69 | 70.21 (1.86x) | 33.50 | 53.30 (1.59x) | [^parkSpecEdgeScalableEdgeAssisted2025] |
| Llama2 13B / JF 160M | batch size 1, temperature 0.7 | 2.72±1.37 | 2.72±1.39 | 37.87 | 55.39 (1.46x) | 33.66 | 42.08 (1.25x) | [^parkSpecEdgeScalableEdgeAssisted2025] |

Inter token latency (ITL) and speedup compared to autoregressive decoding:[^parkSpecEdgeScalableEdgeAssisted2025]

| Target / draft | Setting | ITL (ms): server-only | SpecEdge | Speedup: server-only | SpecEdge | Reported by |
|---|---|---|---|---|---|---|
| Vicuna 33B / SL 1.3B | batch size 1, temperature 0.7 | 34.77 | 30.631 | 1.69x | 1.92x | [^parkSpecEdgeScalableEdgeAssisted2025] |
| Llama2 13B / TL 1.1B | batch size 1, temperature 0.7 | 23.883 | 21.338 | 1.59x | 1.78x | [^parkSpecEdgeScalableEdgeAssisted2025] |
| Llama2 13B / JF 160M | batch size 1, temperature 0.7 | 26.222 | 24.579 | 1.45x | 1.54x | [^parkSpecEdgeScalableEdgeAssisted2025] |

## Known issues

- The speed rows measure decoding speed on WikiText-2 prompts and say nothing about language modeling quality on the dataset.[^svirschevskiSpecExecMassivelyParallel2024][^parkSpecEdgeScalableEdgeAssisted2025]
- The same pair, Sheared Llama-1.3B as draft and Vicuna-33B as target, appears in both speed papers with different numbers, under different settings. SpecExec reports 30.19 tok/s and a 1.90x speedup at t=0.6 with a draft budget of 128, in-memory on an A100.[^svirschevskiSpecExecMassivelyParallel2024] The server-only baseline of SpecEdge reports a server throughput of 27.26 tok/s and a 1.69x speedup at temperature 0.7 with draft tree size 32, on an A100 server.[^parkSpecEdgeScalableEdgeAssisted2025] The settings differ, so these rows are not a contradiction.

## Related

- Datasets: [C4](c4.md), [MT-Bench](mt-bench.md)
- Methods: [Speculative decoding](../methods/speculative-decoding.md), [SpecExec](../methods/specexec.md), [SpecInfer](../methods/specinfer.md), [Tree-based speculation](../methods/tree-based-speculation.md), [Sheared-LLaMA](../methods/sheared-llama.md)

[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^caiYourNPUReady2026]: Cai et al. 2026
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
