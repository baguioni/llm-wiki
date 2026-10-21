---
type: Open Question
title: Does speculative decoding still help at large batch sizes?
description: Papers disagree on whether speculative decoding keeps a speedup above 1 when the server batches many requests.
tags: [speculative-decoding, batching, llm-serving]
sources:
  - id: suSynergySpeculativeDecoding2023
    resource: zotero://select/items/@suSynergySpeculativeDecoding2023
    title: The Synergy of Speculative Decoding and Batching in Serving Large Language Models
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# Does speculative decoding still help at large batch sizes?

## Question

Does speculative decoding keep a speedup above 1 at batch size or concurrency 16 to 64, and for which drafters?

## Why it matters

Production serving runs batched. A drafter that wins at batch size 1 and loses at batch size 32 changes what should be deployed.

## Evidence so far

| Paper | Finding | Setting |
|---|---|---|
| [Su et al.](../papers/suSynergySpeculativeDecoding2023.md) | Speedup falls from 2.73× at batch size 1 to 1.31× at batch size 32 | uniform traffic[^suSynergySpeculativeDecoding2023] |
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | 1.38x throughput at batch size 64 | SGLang, H100[^liEAGLE3ScalingInference2025] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | EAGLE-3 with 60 draft tokens at 0.6× at concurrency 32; DFlash at 1.6× | SGLang, LLaMA-3.1-8B, GSM8K[^chenDFlashBlockDiffusion2026] |
| [Aurora](../papers/wangWhenRLMeets2026.md) | 0.93×-0.94× at batch size 32 | Qwen3-Coder-Next[^wangWhenRLMeets2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | SSD falls back in 57%–96% of steps at batch 16 | Qwen3-14B[^liuWhenParallelDrafter2026] |
| [PARD](../papers/anPARDAcceleratingLLM2025.md) | PARD falls from 3.63 at batch size 1 to 1.33 at batch size 16, below vanilla SD (1.41); EAGLE falls from 1.86 to 1.19 | vLLM, A100-40GB, LLaMA3.1-8B, HumanEval[^anPARDAcceleratingLLM2025] |
| [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) | At batch size 64 the gain is smaller but PARD-2 still outperforms PARD (figure only) | vLLM, Llama-3.1-8B and Qwen3-8B[^anPARD2TargetAlignedParallel2026] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Throughput gain over EAGLE-3 is 24% at batch size 1 and 13% at batch size 16 (2855 vs 2534 tokens/s) | SGLang, one H100, Qwen3-8B[^bieOspreyTargetagnosticPretraining2026] |

## Conflicting claims

- EAGLE-3 reports a gain at batch size 64,[^liEAGLE3ScalingInference2025] while DFlash measures EAGLE-3 below 1× at concurrency 32.[^chenDFlashBlockDiffusion2026] The draft-token budget, drafting mode, hardware, and dataset differ.
- The SSD paper states that its method stays faster than speculative decoding at larger batch sizes (figure only),[^kumarSpeculativeSpeculativeDecoding2026] while DPara measures SSD falling back in most steps at batch 16.[^liuWhenParallelDrafter2026]

- PARD's parallel drafter loses its lead over vanilla SD by batch size 16 on vLLM,[^anPARDAcceleratingLLM2025] while DFlash, also a one-pass drafter, keeps 1.6× at concurrency 32 on SGLang.[^chenDFlashBlockDiffusion2026] Both use LLaMA-3.1-8B, but the tasks (HumanEval against GSM8K), engines (vLLM against SGLang), and GPUs (A100 against B200) differ.

## What would resolve it

A sweep over batch size on one serving stack and one GPU, with each drafter at its best draft length per batch size, as [Su et al.](../papers/suSynergySpeculativeDecoding2023.md) do for standard speculative decoding.[^suSynergySpeculativeDecoding2023]

## Related

- [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [PARD](../methods/pard.md), [Osprey](../methods/osprey.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md)
- [SGLang](../methods/sglang.md), [Continuous batching](../methods/continuous-batching.md)
- [Why do reported EAGLE-3 numbers differ so much between papers?](eagle-3-baseline-variance.md)

[^suSynergySpeculativeDecoding2023]: Su et al. 2023
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^wangWhenRLMeets2026]: Wang et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
