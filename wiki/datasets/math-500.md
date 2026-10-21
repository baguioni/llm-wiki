---
type: Dataset
title: MATH-500
description: Math problem set that the wiki's speculative-decoding papers use as a prompt set for measuring speedup and acceptance length.
tags: [math, reasoning, speculative-decoding, evaluation]
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
---

# MATH-500

## Overview

Four speculative-decoding papers in this wiki use MATH-500 as a math prompt set for measuring speedup and acceptance length.[^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^liSpecForgeFlexibleEfficient2026] None of them reports task accuracy on it. I-DLM reports accuracy on it and also uses it as a serving workload.[^yuIntrospectiveDiffusionLanguage2026] The papers write the name as MATH-500, MATH, MATH500, and Math500.[^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^liSpecForgeFlexibleEfficient2026]

## Composition

The papers do not describe the dataset's size, splits, or format. They only place it in their math or mathematical-reasoning category.[^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^liSpecForgeFlexibleEfficient2026]

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Math prompt set for speedup and $\tau$, with and without thinking mode; SGLang and vLLM serving; drafter ablations | Qwen3 and Qwen3.5 targets, GPT-OSS | DFlash (16) on Q3-4B at temperature 0: 6.09×, $\tau$ 7.84[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | Math prompt set for accepted length | Qwen3-4B, 8B, 14B, Gemma4-12B; temperature 1.0 | DSpark $\tau$ from 5.70 to 5.78 across the four targets[^chengDSparkConfidenceScheduledSpeculative2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | Math prompt set for speedup and $\tau$ | Qwen3-8B and 14B; greedy and temperature 1.0 | DPara on Qwen3-8B, greedy: 3.95×, $\tau$ 5.41[^liuWhenParallelDrafter2026] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | Math prompt set for serving throughput; the benchmark for the training-data comparison | Seven targets on SGLang | SpecBundle speedup up to 3.76 (Llama-4-Scout)[^liSpecForgeFlexibleEfficient2026] |
| [PARD](../papers/anPARDAcceleratingLLM2025.md) | Math task for the DeepSeek-R1-Qwen targets | DeepSeek-R1-Qwen 7B and 14B; vLLM, A100-40GB | PARD on DS 14B: 133.98 tokens/s, 3.29[^anPARDAcceleratingLLM2025] |
| [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) | Math task for speedup and $\tau$ | Qwen3-8B, 14B, 32B, Llama3.1-8B; vLLM, temperature 0 | PARD-2 on Qwen3-8B: 6.87, $\tau$ 8.27[^anPARD2TargetAlignedParallel2026] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | 64 prompts for accepted length and throughput | MiniMax-M2.5, SGLang, FP8 on 4 B200 | AL 3.642 for Osprey against 2.924 for EAGLE-3[^bieOspreyTargetagnosticPretraining2026] |
| [Yu et al. 2026](../papers/yuIntrospectiveDiffusionLanguage2026.md) | Accuracy of [I-DLM](../methods/i-dlm.md); serving workload against EAGLE-3 and other DLMs | Qwen3 chat template with thinking, temperature 1.0, three runs; 500 problems; SGLang on H100 | I-DLM-8B 96.8 vs Qwen3-8B 95.8; 341 vs 238 tokens/s per request against EAGLE-3 at concurrency 1[^yuIntrospectiveDiffusionLanguage2026] |

## Speed metrics

Speculative-decoding speedup, acceptance length, and throughput measured with this dataset's prompts. These numbers say nothing about task accuracy. Each subsection is one paper and one setting, and rows from different subsections are not comparable.

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): Table 1, Transformers backend

Qwen3 (Q3) targets with thinking mode disabled, maximum of 2048 generated tokens. Speedup is end-to-end over the autoregressive baseline. The number in parentheses is the draft tree size for EAGLE-3 and the block size for DFlash. EAGLE-3 uses 7 draft steps and top-$k$ 10, with the checkpoints released by AngelSlim.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Q3-4B | 0 | EAGLE-3 (16) | 1.83× | 3.08 |
| Q3-4B | 0 | EAGLE-3 (60) | 2.10× | 3.52 |
| Q3-4B | 0 | DFlash (16) | 6.09× | 7.84 |
| Q3-8B | 0 | EAGLE-3 (16) | 1.81× | 3.02 |
| Q3-8B | 0 | EAGLE-3 (60) | 2.05× | 3.49 |
| Q3-8B | 0 | DFlash (16) | 6.08× | 7.87 |
| Q3-4B | 1 | EAGLE-3 (16) | 1.75× | 2.99 |
| Q3-4B | 1 | EAGLE-3 (60) | 1.97× | 3.44 |
| Q3-4B | 1 | DFlash (16) | 5.09× | 6.67 |
| Q3-8B | 1 | EAGLE-3 (16) | 1.73× | 2.91 |
| Q3-8B | 1 | EAGLE-3 (60) | 1.94× | 3.38 |
| Q3-8B | 1 | DFlash (16) | 4.84× | 6.40 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): reasoning models (Table 2)

Qwen3 with thinking mode enabled, Transformers backend, drafters trained on target outputs with reasoning traces.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Q3-4B | 0 | DFlash | 4.59× | 5.74 |
| Q3-4B | 1 | DFlash | 3.93× | 4.89 |
| Q3-8B | 0 | DFlash | 4.64× | 5.82 |
| Q3-8B | 1 | DFlash | 4.03× | 5.06 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): serving on SGLang (Table 3)

Single B200 GPU, FA4 backend, Spec-v2 scheduling overlap enabled. Cells are throughput in tok/s at each concurrency level, with the DFlash speedup over the baseline in parentheses.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| Qwen3-4B | not stated | Baseline | 316 | 1145 | 2201 | 4100 | 7136 | – |
| Qwen3-4B | not stated | DFlash | 1531 (4.8×) | 4943 (4.3×) | 9066 (4.1×) | 14477 (3.5×) | 20417 (2.9×) | 8.01 |
| Qwen3-8B | not stated | Baseline | 230 | 861 | 1666 | 3133 | 5694 | – |
| Qwen3-8B | not stated | DFlash | 1175 (5.1×) | 3884 (4.5×) | 7485 (4.5×) | 12268 (3.9×) | 16076 (2.8×) | 8.01 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): more models on SGLang (Table 11)

One B200, concurrency 8. Speedup is over autoregressive decoding. MTP is the model's native MTP.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3.5-4B | not stated | MTP | 1.5× | 6.5 |
| Qwen3.5-4B | not stated | DFlash | 3.0× | 7.1 |
| Qwen3.5-9B | not stated | MTP | 1.7× | 6.7 |
| Qwen3.5-9B | not stated | DFlash | 3.5× | 7.3 |
| Qwen3.5-35B-A3B | not stated | MTP | 1.7× | 6.9 |
| Qwen3.5-35B-A3B | not stated | DFlash | 2.4× | 7.2 |
| Qwen3.5-27B | not stated | DFlash | 3.8× | 7.7 |
| Qwen3-Coder-Next | not stated | DFlash | 1.9× | 6.0 |
| GPT-OSS-20B | not stated | DFlash | 2.2× | 5.1 |
| GPT-OSS-120B | not stated | DFlash | 1.6× | 5.4 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): vLLM (Table 12)

DFlash throughput and speedup over autoregressive decoding at each concurrency level.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Concurrency | Throughput (tok/s) | Speedup |
|---|---|---|---|---|---|
| Qwen3.5-9B | not stated | DFlash | 1 | 849 | 4.0× |
| Qwen3.5-9B | not stated | DFlash | 8 | 5096 | 3.2× |
| Qwen3.5-9B | not stated | DFlash | 16 | 7669 | 2.5× |
| Qwen3.5-9B | not stated | DFlash | 32 | 9836 | 1.9× |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): drafter ablations (Tables 6, 7, 8, 13)

Ablation drafters are trained on 100K samples and run on a single H200 GPU with greedy decoding. The wiki's Paper page does not record the target model of these tables.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 3-L | 4.69× | 5.64 |
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 5-L | 4.71× | 5.99 |
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 8-L | 4.64× | 6.33 |
| not stated | 0 | Target hidden features (3 draft layers, block size 16; Table 7) 3-H | 4.49× | 5.38 |
| not stated | 0 | Target hidden features (3 draft layers, block size 16; Table 7) 5-H | 4.69× | 5.64 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b16 → b16 | 4.64x | 6.33 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b16 → b8 | 3.87x | 5.09 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b8 → b16 | 3.78x | 5.02 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b8 → b8 | 3.97x | 5.21 |
| not stated | 0 | Masked-block construction (3 layers, 5 features, block size 16; Table 13) Standard | 4.13x | 4.94 |
| not stated | 0 | Masked-block construction (3 layers, 5 features, block size 16; Table 13) Sample (random anchors) | 4.69x | 5.64 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): drafter without target features (Table 10)

The table gives speedup without a multiplication sign.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| not stated | 0 | 5-layer block diffusion drafter without target context features | 3.73 | 4.61 |
| not stated | 1 | 5-layer block diffusion drafter without target context features | 3.31 | 4.12 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): accepted length (Table 1)

Accepted length $\tau$ per decoding round, including the bonus token. Standard speculative decoding with chain-based drafting. All three drafters are retrained in the same framework on the same data, with block size 7 for DFlash and DSpark and TTT horizon 7 for Eagle3. Eagle3 has 1 draft layer, DSpark and DFlash have 5. The confidence scheduler is disabled. No speedup is reported for this table.[^chengDSparkConfidenceScheduledSpeculative2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Qwen3-4B | 1.0 | Eagle3 | 4.62 |
| Qwen3-4B | 1.0 | DFlash | 4.85 |
| Qwen3-4B | 1.0 | DSpark | 5.70 |
| Qwen3-8B | 1.0 | Eagle3 | 4.77 |
| Qwen3-8B | 1.0 | DFlash | 4.91 |
| Qwen3-8B | 1.0 | DSpark | 5.78 |
| Qwen3-14B | 1.0 | Eagle3 | 4.60 |
| Qwen3-14B | 1.0 | DFlash | 4.84 |
| Qwen3-14B | 1.0 | DSpark | 5.74 |
| Gemma4-12B | 1.0 | Eagle3 | 5.46 |
| Gemma4-12B | 1.0 | DFlash | 5.04 |
| Gemma4-12B | 1.0 | DSpark | 5.78 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): Tables 1 and 3

Batch size 1, up to 512 new tokens, draft length 7, speedup over AR. Temperature 0 rows are greedy decoding (Table 1). Temperature 1.0 rows use temperature 1.0 for both the target and the drafter (Table 3). SSD-E3 uses the EAGLE3 weight of the target as draft model. SSD, SD, and PEARL on Qwen3-14B use Qwen3-0.6B as draft model. The parallel methods (PEARL, SSD, DPara) use one additional GPU for drafting.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-8B | 0 | SSD-E3 | 1.54× | 2.42 |
| Qwen3-8B | 0 | EAGLE3 | 1.46× | 2.84 |
| Qwen3-8B | 0 | DFlash | 3.28× | 5.88 |
| Qwen3-8B | 0 | DSpark | 3.46× | 6.39 |
| Qwen3-8B | 0 | DPara | 3.95× | 5.41 |
| Qwen3-14B | 0 | SSD | 2.80× | 5.63 |
| Qwen3-14B | 0 | SSD-E3 | 1.80× | 2.48 |
| Qwen3-14B | 0 | PEARL | 3.58× | 3.85 |
| Qwen3-14B | 0 | SD | 2.28× | 5.65 |
| Qwen3-14B | 0 | EAGLE3 | 1.74× | 2.93 |
| Qwen3-14B | 0 | DFlash | 3.76× | 5.92 |
| Qwen3-14B | 0 | DSpark | 4.01× | 6.39 |
| Qwen3-14B | 0 | DPara | 4.32× | 5.37 |
| Qwen3-8B | 1.0 | DFlash | 2.66× | 5.15 |
| Qwen3-8B | 1.0 | DSpark | 3.00× | 5.96 |
| Qwen3-8B | 1.0 | DPara | 3.17× | 4.77 |
| Qwen3-14B | 1.0 | DFlash | 3.13× | 5.04 |
| Qwen3-14B | 1.0 | DSpark | 3.61× | 5.91 |
| Qwen3-14B | 1.0 | DPara | 3.74× | 4.88 |

All rows: [^liuWhenParallelDrafter2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): backbone finetuning ablation

DPara with the same frozen AR head, comparing the original DSpark checkpoint with the finetuned M-DFlash backbone.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | $\tau$ with original DSpark checkpoint | $\tau$ with M-DFlash | Relative gain |
|---|---|---|---|---|---|
| Qwen3-8B | not stated | DPara | 4.06 | 5.41 | 33.3% |

All rows: [^liuWhenParallelDrafter2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): SpecBundle inference (Table 3)

SGLang on NVIDIA H200 GPUs, 8 concurrent requests for LLaMA-3.1-8B and 16 for larger models. The highest throughput among five (speculative steps, top-k, draft tokens) configurations is reported. Existing draft models come from the EAGLE3 authors or the LMSYS team. The tables do not state the unit of the throughput column.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | #GPUs | Throughput | Speedup |
|---|---|---|---|---|---|
| Llama-3.1-8B | not stated | none (target model alone) | 1 | 191.0 | 1 |
| Llama-3.1-8B | not stated | EAGLE3, existing open-source draft model | 1 | 422.4 | 2.21 |
| Llama-3.1-8B | not stated | EAGLE3, SpecBundle draft model | 1 | 638.0 | 3.34 |
| Llama-3.3-70B | not stated | none (target model alone) | 4 | 567.4 | 1 |
| Llama-3.3-70B | not stated | EAGLE3, existing open-source draft model | 4 | 1122.2 | 1.98 |
| Llama-3.3-70B | not stated | EAGLE3, SpecBundle draft model | 4 | 1524.9 | 2.69 |
| Llama-4-Scout | not stated | none (target model alone) | 8 | 561.8 | 1 |
| Llama-4-Scout | not stated | EAGLE3, existing open-source draft model | 8 | 1479.0 | 2.63 |
| Llama-4-Scout | not stated | EAGLE3, SpecBundle draft model | 8 | 2110.3 | 3.76 |
| Qwen-30B-A3B | not stated | none (target model alone) | 4 | 1469.0 | 1 |
| Qwen-30B-A3B | not stated | EAGLE3, SpecBundle draft model | 4 | 3636.1 | 1.48 |
| Qwen-235B-A22B | not stated | none (target model alone) | 8 | 587.4 | 1 |
| Qwen-235B-A22B | not stated | EAGLE3, existing open-source draft model | 8 | 821.8 | 1.39 |
| Qwen-235B-A22B | not stated | EAGLE3, SpecBundle draft model | 8 | 1399.2 | 2.38 |
| Ling-Flash-V2 | not stated | none (target model alone) | 8 | 762.7 | 1 |
| Ling-Flash-V2 | not stated | EAGLE3, SpecBundle draft model | 8 | 1685.6 | 2.21 |
| Kimi-K2 | not stated | none (target model alone) | 8 | 492.1 | 1 |
| Kimi-K2 | not stated | EAGLE3, SpecBundle draft model | 8 | 1022.7 | 2.08 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): MoE draft models (Table 4)

The table is captioned "Acceptance rate of MoE models with different settings", with MoE top-k = 1, EAGLE3 number of steps = 3, EAGLE3 top-k = 1, and EAGLE3 number of draft tokens = 4.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | Acceptance |
|---|---|---|---|
| not stated | not stated | MoE draft, Same Params, 2 experts | 1.17 |
| not stated | not stated | MoE draft, Same FLOPS, 2 experts | 1.67 |
| not stated | not stated | MoE draft, Same FLOPS, 3 experts | 1.77 |
| not stated | not stated | MoE draft, Same FLOPS, 4 experts | 1.79 |
| not stated | not stated | MoE draft, With Shared Experts, 2 experts | 1.75 |
| not stated | not stated | MoE draft, With Shared Experts, 3 experts | 1.75 |
| not stated | not stated | MoE draft, With Shared Experts, 4 experts | 1.81 |
| not stated | not stated | Dense Draft Model | 2.55 |

All rows: [^liSpecForgeFlexibleEfficient2026]


### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): training data and TTT length

- An EAGLE-3 draft for LLaMA-3.1-Instruct trained on [ShareGPT](sharegpt.md) and UltraChat reaches an acceptance length of 2.82 on Math500. The same draft trained on the [Perfect-Blend](perfectblend.md) dataset reaches 3.48, which the paper equates to an additional 1.17× inference speedup.[^liSpecForgeFlexibleEfficient2026]
- In the TTT-length sweep on Llama3.1-8B, a TTT length of approximately 13 gives the best acceptance length on Math500.[^liSpecForgeFlexibleEfficient2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): block size

Acceptance histograms on Math500 show that a DFlash drafter with block size 8 fully accepts entire blocks 35.7% of the time, which the paper reads as block size 8 being underutilized.[^chenDFlashBlockDiffusion2026]

## Known issues

- In SpecForge's Table 3, the Qwen-30B-A3B SpecBundle row gives a Math500 throughput of 3636.1 against 1469.0 for the target alone, with a speedup of 1.48. The same row's other columns give 3413.0 against 1492.6 with a speedup of 2.29, and 3070.0 against 1366.6 with a speedup of 2.25.[^liSpecForgeFlexibleEfficient2026]
- The SpecForge text gives the range of SpecBundle speedups on the coding and mathematics benchmarks as 1.61× to 4.48×, while that Math500 cell is 1.48.[^liSpecForgeFlexibleEfficient2026]
- DFlash reports Math500 with thinking mode both disabled (Table 1) and enabled (Table 2), and the two are separate drafters and settings.[^chenDFlashBlockDiffusion2026]

# Contradictions

### Same drafter, target, and temperature in different papers

More than one paper reports the same drafter on the same Qwen3 target and temperature with this dataset. The values are side by side below, and most of them differ.

| Target | Temp. | Method | DFlash paper[^chenDFlashBlockDiffusion2026] (speedup / $\tau$) | DSpark paper[^chengDSparkConfidenceScheduledSpeculative2026] ($\tau$) | DPara paper[^liuWhenParallelDrafter2026] (speedup / $\tau$) |
|---|---|---|---|---|---|
| Qwen3-4B | 1 | EAGLE-3 | 1.75× / 2.99 (tree size 16); 1.97× / 3.44 (tree size 60) | 4.62 | – |
| Qwen3-4B | 1 | DFlash | 5.09× / 6.67 (block size 16) | 4.85 | – |
| Qwen3-8B | 0 | EAGLE-3 | 1.81× / 3.02 (tree size 16); 2.05× / 3.49 (tree size 60) | – | 1.46× / 2.84 |
| Qwen3-8B | 0 | DFlash | 6.08× / 7.87 (block size 16) | – | 3.28× / 5.88 |
| Qwen3-8B | 1 | EAGLE-3 | 1.73× / 2.91 (tree size 16); 1.94× / 3.38 (tree size 60) | 4.77 | – |
| Qwen3-8B | 1 | DFlash | 4.84× / 6.40 (block size 16) | 4.91 | 2.66× / 5.15 |
| Qwen3-8B | 1 | DSpark | – | 5.78 | 3.00× / 5.96 |
| Qwen3-14B | 1 | DFlash | – | 4.84 | 3.13× / 5.04 |
| Qwen3-14B | 1 | DSpark | – | 5.74 | 3.61× / 5.91 |

The settings differ in ways that the papers state. The DFlash paper runs the Transformers backend on H200 GPUs with up to 2048 generated tokens, uses the EAGLE-3 checkpoints released by AngelSlim with tree drafting, and uses DFlash block size 16.[^chenDFlashBlockDiffusion2026] The DSpark paper retrains all three drafters in one framework on the same data, uses chain-based drafting with block size 7 (TTT horizon 7 for Eagle3), and reports only $\tau$.[^chengDSparkConfidenceScheduledSpeculative2026] The DPara paper uses batch size 1, draft length 7, and up to 512 new tokens on an H800 node.[^liuWhenParallelDrafter2026]


## Related

- Methods measured on it: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [PEARL](../methods/pearl.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [Multi-token prediction](../methods/multi-token-prediction.md), [KV injection](../methods/kv-injection.md)
- Serving engines used for the measurements: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets evaluated alongside it: [GSM8K](gsm8k.md), [HumanEval](humaneval.md), [MBPP](mbpp.md), [LiveCodeBench](livecodebench.md), [MT-Bench](mt-bench.md), [Alpaca](alpaca.md)
- Training data compared on it: [ShareGPT](sharegpt.md), [Open-PerfectBlend](perfectblend.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
