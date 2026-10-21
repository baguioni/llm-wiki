---
type: Method
title: Lever
description: Speculative decoding system for smartphones with a flash-resident target, combining gain-per-latency token tree construction, early-exit pruning of the verification tree, and CPU-NPU split execution.
tags: [speculative-decoding, on-device-inference, mobile-npu, flash-offloading, tree-based-speculation, speculative-drafter]
sources:
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
---

# Lever

## Overview

Lever runs [speculative decoding](speculative-decoding.md) on a smartphone whose DRAM is too small for the target model. The draft model stays in DRAM, and the target's weights are streamed from flash layer by layer at each verification, so speculative decoding amortizes the flash I/O over several output tokens.[^wangLeverSpeculativeLLM2026a]

The design starts from phone measurements. Per-token verification of a flash-resident Qwen3-8B on a OnePlus 12 takes 1050.0 ms, of which 953.4 ms (90.8%) is I/O.[^wangLeverSpeculativeLLM2026a] At 64 verified tokens, a Snapdragon 8 Gen 3 NPU reaches 8.0x over single-token generation, against 20.6x for an RTX 3090 GPU (Figure 4).[^wangLeverSpeculativeLLM2026a]

## How it works

- **Drafting.** Lever builds a [token tree](tree-based-speculation.md) that maximizes expected output tokens per unit of cycle latency, $\hat{G}(T)/\hat{C}_{\mathrm{cycle}}(T)$. The gain uses calibrated draft probabilities. The cost uses a moving average of draft time and an online verification-latency profile indexed by node count and leaf count. Nodes are inserted greedily, and growth stops when no candidate beats the tree's current rate, so there is no fixed tree budget.[^wangLeverSpeculativeLLM2026a]
- **Verification pruning.** A linear early-exit predictor at an intermediate target layer scores the tree's branches. Low-scoring branches skip the upper target layers, with safeguards that keep ancestors and a backbone path. The full target still decides acceptance.[^wangLeverSpeculativeLLM2026a]
- **CPU-NPU execution.** Small draft expansions run serially on the CPU, and once the tree is large, high-value frontier nodes are expanded as a batch on the NPU. All target transformer layers run batched on the NPU. The output projection runs on demand on the CPU, only along the accepted path.[^wangLeverSpeculativeLLM2026a]

## Papers using it

### Lever paper ([Wang et al. 2026](../papers/wangLeverSpeculativeLLM2026a.md))

Three Snapdragon phones (OnePlus 12, Honor 500 Pro, Honor Magic V5), targets Llama-3.1-8B, Qwen3-4B, Qwen3-8B, and Qwen3-14B with EAGLE-3-trained drafts, Q4\_0 weights, greedy decoding, 128 output tokens.[^wangLeverSpeculativeLLM2026a]

- Geometric-mean decode speedup over 48 configurations: 2.93$\times$ over flash-backed autoregressive decoding (Flash-AR), 1.50$\times$ over chain speculative decoding, 1.27$\times$ over EdgeLLM.[^wangLeverSpeculativeLLM2026a]
- Lever's decode throughput ranges from 0.71 tokens/s (Qwen3-14B, MT-Bench, Honor 500 Pro) to 7.55 tokens/s (Qwen3-4B, MBPP, Honor Magic V5).[^wangLeverSpeculativeLLM2026a]
- With every target layer resident in DRAM, Lever reaches 3.401 tokens/s on Qwen3-8B MBPP, against 1.753 with all layers in flash.[^wangLeverSpeculativeLLM2026a]
- Verification pruning keeps about 48% of upper-layer rows, cuts verification latency by 12.2%, and keeps about 95% of accepted tokens.[^wangLeverSpeculativeLLM2026a]

## Strengths & Limitations

- Lever's draft-stage scheduler is faster than drafting only on the CPU or only on the NPU, and single-node NPU drafting is the slowest option because of launch and synchronization overhead.[^wangLeverSpeculativeLLM2026a]
- The baselines share Lever's flash weight streaming, so no result compares against a DRAM-resident target with a different method.[^wangLeverSpeculativeLLM2026a]
- The paper reports no energy measurements and does not name its inference framework or NPU runtime.

## Related

- Paper: [Lever](../papers/wangLeverSpeculativeLLM2026a.md)
- Draft trees: [Tree-based speculation](tree-based-speculation.md), [SpecInfer](specinfer.md)
- Draft model: [EAGLE-3](eagle-3.md)
- Verification pruning: [Early exit](early-exit.md)
- Other on-device or edge setups: [HAT](hat.md), [llama.cpp](llama-cpp.md)

## Open questions and results

- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)
- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)

[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
