---
type: Dataset
title: LiveCodeBench
description: Code benchmark that the wiki's speculative-decoding papers use as a coding prompt set for measuring speedup and acceptance length.
tags: [code-generation, speculative-decoding, evaluation]
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
---

# LiveCodeBench

## Overview

Three speculative-decoding papers in this wiki use LiveCodeBench (abbreviated LCB) as a code prompt set for measuring speedup, acceptance length, and serving throughput.[^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liSpecForgeFlexibleEfficient2026] None of them reports task accuracy on it. I-DLM reports pass@1 on LCB-v6 for a diffusion LM against its AR base.[^yuIntrospectiveDiffusionLanguage2026]

## Composition

The papers do not describe the dataset's size, splits, or format. They place it in their code or coding category.[^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liSpecForgeFlexibleEfficient2026]

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Code prompt set for speedup and $\tau$; SGLang serving with a coder model | Qwen3-4B and 8B on Transformers; Qwen3-Coder-30B-A3B on SGLang | DFlash (16) on Q3-8B at temperature 0: 5.51×, $\tau$ 7.27[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | Code prompt set for accepted length | Qwen3-4B, 8B, 14B, Gemma4-12B; temperature 1.0 | DSpark $\tau$ from 4.51 to 5.17 across the four targets[^chengDSparkConfidenceScheduledSpeculative2026] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | Coding prompt set for serving throughput with EAGLE3 draft models | Seven targets on SGLang | SpecBundle on Llama-4-Scout: speedup 4.48, the highest in the paper[^liSpecForgeFlexibleEfficient2026] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | 64 prompts for accepted length and throughput | MiniMax-M2.5, SGLang, FP8 on 4 B200 | AL 3.779 for Osprey against 2.508 for EAGLE-3[^bieOspreyTargetagnosticPretraining2026] |
| [Yu et al. 2026](../papers/yuIntrospectiveDiffusionLanguage2026.md) | Accuracy of [I-DLM](../methods/i-dlm.md) (LCB-v6) | Qwen3 chat template with thinking, temperature 1.0, three runs; 175 problems, pass@1 | I-DLM-8B 45.7 vs Qwen3-8B 50.3; LLaDA-2.1-mini (16B) 30.4; I-DLM-32B 57.1[^yuIntrospectiveDiffusionLanguage2026] |

## Speed metrics

Speculative-decoding speedup, acceptance length, and throughput measured with this dataset's prompts. These numbers say nothing about task accuracy. Each subsection is one paper and one setting, and rows from different subsections are not comparable.

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): Table 1, Transformers backend

Qwen3 (Q3) targets with thinking mode disabled, maximum of 2048 generated tokens. Speedup is end-to-end over the autoregressive baseline. The number in parentheses is the draft tree size for EAGLE-3 and the block size for DFlash. EAGLE-3 uses 7 draft steps and top-$k$ 10, with the checkpoints released by AngelSlim.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Q3-4B | 0 | EAGLE-3 (16) | 1.73× | 2.91 |
| Q3-4B | 0 | EAGLE-3 (60) | 1.90× | 3.22 |
| Q3-4B | 0 | DFlash (16) | 5.41× | 7.09 |
| Q3-8B | 0 | EAGLE-3 (16) | 1.57× | 2.65 |
| Q3-8B | 0 | EAGLE-3 (60) | 1.81× | 3.03 |
| Q3-8B | 0 | DFlash (16) | 5.51× | 7.27 |
| Q3-4B | 1 | EAGLE-3 (16) | 1.63× | 2.77 |
| Q3-4B | 1 | EAGLE-3 (60) | 1.82× | 3.14 |
| Q3-4B | 1 | DFlash (16) | 4.90× | 6.50 |
| Q3-8B | 1 | EAGLE-3 (16) | 1.56× | 2.57 |
| Q3-8B | 1 | EAGLE-3 (60) | 1.72× | 2.92 |
| Q3-8B | 1 | DFlash (16) | 4.93× | 6.69 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): serving on SGLang (Table 3)

Single B200 GPU, FA4 backend, Spec-v2 scheduling overlap enabled. Cells are throughput in tok/s at each concurrency level, with the DFlash speedup over the baseline in parentheses.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| Qwen3-Coder-30B-A3B | not stated | Baseline | 220 | 681 | 1112 | 1733 | 2823 | – |
| Qwen3-Coder-30B-A3B | not stated | DFlash | 569 (2.6×) | 1621 (2.4×) | 2554 (2.3×) | 4160 (2.4×) | 6401 (2.3×) | 6.42 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): accepted length (Table 1)

Accepted length $\tau$ per decoding round, including the bonus token. Standard speculative decoding with chain-based drafting. All three drafters are retrained in the same framework on the same data, with block size 7 for DFlash and DSpark and TTT horizon 7 for Eagle3. Eagle3 has 1 draft layer, DSpark and DFlash have 5. The confidence scheduler is disabled. No speedup is reported for this table.[^chengDSparkConfidenceScheduledSpeculative2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Qwen3-4B | 1.0 | Eagle3 | 3.77 |
| Qwen3-4B | 1.0 | DFlash | 4.18 |
| Qwen3-4B | 1.0 | DSpark | 4.86 |
| Qwen3-8B | 1.0 | Eagle3 | 4.17 |
| Qwen3-8B | 1.0 | DFlash | 4.39 |
| Qwen3-8B | 1.0 | DSpark | 5.17 |
| Qwen3-14B | 1.0 | Eagle3 | 4.01 |
| Qwen3-14B | 1.0 | DFlash | 4.33 |
| Qwen3-14B | 1.0 | DSpark | 5.02 |
| Gemma4-12B | 1.0 | Eagle3 | 4.16 |
| Gemma4-12B | 1.0 | DFlash | 3.70 |
| Gemma4-12B | 1.0 | DSpark | 4.51 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): SpecBundle inference (Table 3)

SGLang on NVIDIA H200 GPUs, 8 concurrent requests for LLaMA-3.1-8B and 16 for larger models. The highest throughput among five (speculative steps, top-k, draft tokens) configurations is reported. Existing draft models come from the EAGLE3 authors or the LMSYS team. The tables do not state the unit of the throughput column.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | #GPUs | Throughput | Speedup |
|---|---|---|---|---|---|
| Llama-3.1-8B | not stated | none (target model alone) | 1 | 189.7 | 1 |
| Llama-3.1-8B | not stated | EAGLE3, existing open-source draft model | 1 | 398.4 | 2.10 |
| Llama-3.1-8B | not stated | EAGLE3, SpecBundle draft model | 1 | 516.9 | 2.72 |
| Llama-3.3-70B | not stated | none (target model alone) | 4 | 560.9 | 1 |
| Llama-3.3-70B | not stated | EAGLE3, existing open-source draft model | 4 | 1303.4 | 2.32 |
| Llama-3.3-70B | not stated | EAGLE3, SpecBundle draft model | 4 | 1459.4 | 2.60 |
| Llama-4-Scout | not stated | none (target model alone) | 8 | 484.3 | 1 |
| Llama-4-Scout | not stated | EAGLE3, existing open-source draft model | 8 | 1601.3 | 3.31 |
| Llama-4-Scout | not stated | EAGLE3, SpecBundle draft model | 8 | 2170.2 | 4.48 |
| Qwen-30B-A3B | not stated | none (target model alone) | 4 | 1492.6 | 1 |
| Qwen-30B-A3B | not stated | EAGLE3, SpecBundle draft model | 4 | 3413.0 | 2.29 |
| Qwen-235B-A22B | not stated | none (target model alone) | 8 | 598.2 | 1 |
| Qwen-235B-A22B | not stated | EAGLE3, existing open-source draft model | 8 | 803.8 | 1.34 |
| Qwen-235B-A22B | not stated | EAGLE3, SpecBundle draft model | 8 | 1155.7 | 1.93 |
| Ling-Flash-V2 | not stated | none (target model alone) | 8 | 770.4 | 1 |
| Ling-Flash-V2 | not stated | EAGLE3, SpecBundle draft model | 8 | 1366.4 | 1.77 |
| Kimi-K2 | not stated | none (target model alone) | 8 | 500.1 | 1 |
| Kimi-K2 | not stated | EAGLE3, SpecBundle draft model | 8 | 904.4 | 1.81 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): MoE draft models (Table 4)

The table is captioned "Acceptance rate of MoE models with different settings", with MoE top-k = 1, EAGLE3 number of steps = 3, EAGLE3 top-k = 1, and EAGLE3 number of draft tokens = 4.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | Acceptance |
|---|---|---|---|
| not stated | not stated | MoE draft, Same Params, 2 experts | 1.14 |
| not stated | not stated | MoE draft, Same FLOPS, 2 experts | 1.46 |
| not stated | not stated | MoE draft, Same FLOPS, 3 experts | 1.57 |
| not stated | not stated | MoE draft, Same FLOPS, 4 experts | 1.59 |
| not stated | not stated | MoE draft, With Shared Experts, 2 experts | 1.52 |
| not stated | not stated | MoE draft, With Shared Experts, 3 experts | 1.52 |
| not stated | not stated | MoE draft, With Shared Experts, 4 experts | 1.54 |
| not stated | not stated | Dense Draft Model | 3.12 |

All rows: [^liSpecForgeFlexibleEfficient2026]


# Contradictions

### Same drafter, target, and temperature in different papers

More than one paper reports the same drafter on the same Qwen3 target and temperature with this dataset. The values are side by side below, and most of them differ.

| Target | Temp. | Method | DFlash paper[^chenDFlashBlockDiffusion2026] (speedup / $\tau$) | DSpark paper[^chengDSparkConfidenceScheduledSpeculative2026] ($\tau$) |
|---|---|---|---|---|
| Qwen3-4B | 1 | EAGLE-3 | 1.63× / 2.77 (tree size 16); 1.82× / 3.14 (tree size 60) | 3.77 |
| Qwen3-4B | 1 | DFlash | 4.90× / 6.50 (block size 16) | 4.18 |
| Qwen3-8B | 1 | EAGLE-3 | 1.56× / 2.57 (tree size 16); 1.72× / 2.92 (tree size 60) | 4.17 |
| Qwen3-8B | 1 | DFlash | 4.93× / 6.69 (block size 16) | 4.39 |

The settings differ in ways that the papers state. The DFlash paper runs the Transformers backend on H200 GPUs with up to 2048 generated tokens, uses the EAGLE-3 checkpoints released by AngelSlim with tree drafting, and uses DFlash block size 16.[^chenDFlashBlockDiffusion2026] The DSpark paper retrains all three drafters in one framework on the same data, uses chain-based drafting with block size 7 (TTT horizon 7 for Eagle3), and reports only $\tau$.[^chengDSparkConfidenceScheduledSpeculative2026]


## Related

- Methods measured on it: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md)
- Serving engines used for the measurements: [SGLang](../methods/sglang.md)
- Datasets evaluated alongside it: [HumanEval](humaneval.md), [MBPP](mbpp.md), [GSM8K](gsm8k.md), [MATH-500](math-500.md), [MT-Bench](mt-bench.md), [Alpaca](alpaca.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
