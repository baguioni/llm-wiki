---
type: Method
title: SpecInfer
description: Speculative inference system with tree-structured drafts and token tree verification, used by the wiki's papers as a baseline and as a reference setup.
tags: [speculative-decoding, tree-based-speculation, token-tree-verification, llm-serving, baseline]
sources:
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
---

# SpecInfer

## Overview

SpecInfer is a [speculative decoding](../methods/speculative-decoding.md) system by Miao et al. The wiki has no paper page for SpecInfer itself, so this page records only what the wiki's papers say about it. They cite it under two titles: "Specinfer: Accelerating generative llm serving with speculative inference and token tree verification" and "Specinfer: Accelerating large language model serving with tree-based speculative inference and verification".[^svirschevskiSpecExecMassivelyParallel2024][^gaoCollaborativeSpeculativeInference]

- The SuffixDecoding paper lists SpecInfer among model-based speculative decoding methods and states that it introduced [tree-based speculation](../methods/tree-based-speculation.md).[^oliaroSuffixDecodingExtremeSpeculative2024]
- The CoSine paper describes it as a speculative inference system that utilizes multiple drafters to generate tree-structured drafts while maintaining coupled synchronization for collective candidate evaluation.[^gaoCollaborativeSpeculativeInference]
- The SpecExec paper describes it as an algorithm that shares a large token budget across multiple stems in a tree.[^svirschevskiSpecExecMassivelyParallel2024]
- The SpecEdge paper lists it among tree-based approaches that explore multiple paths simultaneously.[^parkSpecEdgeScalableEdgeAssisted2025]

## How it works

Only the following properties are stated in the wiki's papers.

- SpecInfer must sample its draft tokens to guarantee correctness, while [SpecExec](../methods/specexec.md) builds its draft from the most likely tokens.[^svirschevskiSpecExecMassivelyParallel2024]
- The SpecExec paper gives the per-token acceptance probability of the original speculative decoding, with SpecInfer as its example, as ${P(x_{t+1}|x_{0:t},\theta_{\text{target}})}/{P(x_{t+1}|x_{0:t},\theta_{\text{draft}})}$.[^svirschevskiSpecExecMassivelyParallel2024]
- A speculative generation algorithm is equivalent to sequential sampling if it is locally equivalent in every node, a fact the SpecExec paper takes from the SpecInfer paper.[^svirschevskiSpecExecMassivelyParallel2024]
- All draft tokens are processed in parallel by the target model with a merged attention mask. SpecExec does the same and cites SpecInfer for it.[^svirschevskiSpecExecMassivelyParallel2024]

## Papers using it

### [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md): baseline for large draft budgets

SpecInfer is the baseline because it shares a large token budget across multiple stems in a tree, where a single long draft sequence would waste most of the budget.[^svirschevskiSpecExecMassivelyParallel2024] Inference speed with RAM offloading on an A100 GPU, Llama 2-7B draft and Llama 2-70B target. SX = SpecExec, SI = SpecInfer. Gen. rate is the average number of draft model tokens accepted for one target model iteration.[^svirschevskiSpecExecMassivelyParallel2024]

| Dataset | t | Method | Budget | Gen. rate | Speed, tok/s | Speedup |
|---|---|---|---|---|---|---|
| OAsst | 0.6 | SI | 1024 | 8.41 | 1.34 | 8.0x |
| OAsst | 0.6 | SX | 2048 | 20.60 | 3.12 | 18.7x |
| OAsst | 0 | SI | 1024 | 7.86 | 1.18 | 7.1x |
| OAsst | 0 | SX | 1024 | 18.8 | 2.74 | 16.4x |
| [C4](../datasets/c4.md) | 0.6 | SI | 1024 | 6.48 | 1.03 | 6.2x |
| C4 | 0.6 | SX | 2048 | 12.9 | 1.97 | 11.8x |
| C4 | 0 | SI | 1024 | 4.78 | 0.75 | 4.5x |
| C4 | 0 | SX | 2048 | 16.1 | 2.38 | 14.3x |
| [WikiText-2](../datasets/wikitext-2.md) | 0.6 | SI | 1024 | 4.69 | 0.77 | 4.6x |
| WikiText-2 | 0.6 | SX | 2048 | 9.57 | 1.54 | 9.2x |
| WikiText-2 | 0 | SI | 1024 | 3.71 | 0.62 | 3.6x |
| WikiText-2 | 0 | SX | 2048 | 11.74 | 1.88 | 11.3x |

All rows: [^svirschevskiSpecExecMassivelyParallel2024]

- The OAsst rows use chat models and the C4 and WikiText-2 rows use base models.[^svirschevskiSpecExecMassivelyParallel2024]
- Speculative decoding algorithms with single or multiple sequences, like SpecInfer, are effectively upper-bounded in the number of accepted tokens as the speculation budget grows.[^svirschevskiSpecExecMassivelyParallel2024]
- For smaller draft budgets SpecExec performs on par with SpecInfer, and it outscales SpecInfer as the number of draft tokens grows.[^svirschevskiSpecExecMassivelyParallel2024]
- The optimal draft tree size on the A100 is 128–512 for SpecInfer and 1024–2048 for SpecExec.[^svirschevskiSpecExecMassivelyParallel2024]

### [CoSine](../papers/gaoCollaborativeSpeculativeInference.md): serving baseline

SpecInfer is one of four baselines, with [vLLM](../methods/vllm.md), vanilla speculative inference, and PipeInfer. The settings are a fixed input of 256 tokens, an output of 128 tokens, and greedy sampling.[^gaoCollaborativeSpeculativeInference]

- For the LLaMA pair, CoSine reduces inference latency by 17.9%–27.1% relative to the strongest baselines, which the paper gives as SpecInfer for small batches and PipeInfer for large batches.[^gaoCollaborativeSpeculativeInference]
- For the LLaMA pair, CoSine achieves throughput improvements of $1.31\times$ to $1.62\times$ over SpecInfer as batch sizes increase from $B=1$ to $B=16$.[^gaoCollaborativeSpeculativeInference]
- Online serving with the LLaMA pair, where SpecInfer is the strongest baseline: CoSine has 1.2x-1.5x lower latency at a low arrival rate, 1.3x-1.6x at a high arrival rate, and 1.2x-1.4x at a fluctuated arrival rate.[^gaoCollaborativeSpeculativeInference]
- Cost efficiency table (the paper states neither the unit nor the reference of the percentages): SpecInfer has 43.34% (LLM) and 47.79% (Qwen) in the Low mode, 36.87% and 41.8% in the High mode, and 38.01% and 42.87% in the Volatile mode. CoSine has 29.98% and 34.34%, 21.18% and 26.36%, and 25.71% and 30.63%.[^gaoCollaborativeSpeculativeInference]

### [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md): reference setup

The paper implements speculative decoding in the Microsoft Deepspeed library with the same setup as SpecInfer: the draft model first generates draft tokens, then the target model verifies them. It uses batch size 1 and greedy decoding.[^yanDecodingSpeculativeDecoding2025]

### Other mentions

- The SuffixDecoding paper states that EAGLE-3 and Token Recycling both leverage tree speculation, citing SpecInfer.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The SpecEdge paper states that its design is compatible with tree-based methods including SpecInfer.[^parkSpecEdgeScalableEdgeAssisted2025]

## Strengths & Limitations

- SpecInfer spreads a large draft budget over a tree, which avoids wasting the budget on one long sequence that is truncated at the first rejection.[^svirschevskiSpecExecMassivelyParallel2024]
- Its number of accepted tokens saturates as the speculation budget grows.[^svirschevskiSpecExecMassivelyParallel2024]
- The CoSine paper describes it as maintaining coupled synchronization for collective candidate evaluation, and contrasts this with the decoupled pipeline architecture of PipeInfer.[^gaoCollaborativeSpeculativeInference]

## Related

- [Tree-based speculation](../methods/tree-based-speculation.md), [SpecExec](../methods/specexec.md), [Sequoia](../methods/sequoia.md), [Speculative decoding](../methods/speculative-decoding.md), [vLLM](../methods/vllm.md)
- Papers: [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md), [CoSine](../papers/gaoCollaborativeSpeculativeInference.md), [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md), [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md), [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md)

[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
