---
type: Result
title: Speculative decoding speedup falls from 2.73× to 1.31× as batch size grows from 1 to 32
description: Su et al. measure that the speedup of speculative decoding shrinks as batch size grows and that the best speculation length gets shorter.
tags: [speculative-decoding, batching]
sources:
  - id: suSynergySpeculativeDecoding2023
    resource: zotero://select/items/@suSynergySpeculativeDecoding2023
    title: The Synergy of Speculative Decoding and Batching in Serving Large Language Models
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
---

# Speculative decoding speedup falls from 2.73× to 1.31× as batch size grows from 1 to 32

## Claim

The speedup of speculative decoding over no speculation falls as batch size grows, and the optimal speculation length shrinks with batch size.[^suSynergySpeculativeDecoding2023]

## Conditions

- Uniform traffic, speculation length chosen per batch size from a profiled look-up table.[^suSynergySpeculativeDecoding2023]

## Numbers

| Batch size | Speedup |
|---|---|
| 1 | 2.73×[^suSynergySpeculativeDecoding2023] |
| 32 | 1.31×[^suSynergySpeculativeDecoding2023] |
| average | 1.94×[^suSynergySpeculativeDecoding2023] |

## Comparisons

- Aurora reports 0.93×-0.94× at batch size 32 on Qwen3-Coder-Next.[^wangWhenRLMeets2026]
- EAGLE-3 reports 1.38x at batch size 64 on SGLang.[^liEAGLE3ScalingInference2025]

## Related

- [Su et al. paper](../papers/suSynergySpeculativeDecoding2023.md)
- [Speculative decoding](../methods/speculative-decoding.md), [Continuous batching](../methods/continuous-batching.md)
- [Does speculative decoding still help at large batch sizes?](../questions/speculative-decoding-at-large-batch.md)

[^suSynergySpeculativeDecoding2023]: Su et al. 2023
[^wangWhenRLMeets2026]: Wang et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
