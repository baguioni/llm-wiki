---
type: Dataset
title: MT-Bench
description: Multi-turn conversation benchmark that the wiki's papers use mostly as a chat prompt set for speculative-decoding speed measurements, and once as a quality score.
tags: [chat, multi-turn, speculative-decoding, evaluation]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
---

# MT-Bench

## Overview

The papers in this wiki use MT-Bench as their multi-turn conversation or chat workload when they measure [speculative decoding](../methods/speculative-decoding.md) speedup and acceptance length.[^liEAGLE3ScalingInference2025][^zhangLearningDraftAdaptive2026][^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^samarinLKLossesDirect2026][^liSpecForgeFlexibleEfficient2026][^parkSpecEdgeScalableEdgeAssisted2025][^svirschevskiSpecExecMassivelyParallel2024] One paper uses it for its original purpose and reports an MT-Bench score for instruction-tuned models.[^muralidharanCompactLanguageModels2024] The papers write the name as MT-bench, MT-Bench, and MTBench.[^liEAGLE3ScalingInference2025][^chenDFlashBlockDiffusion2026][^liSpecForgeFlexibleEfficient2026]

## Composition

- Eight MT-Bench categories are part of [Spec-Bench](../benchmarks/spec-bench.md): Writing, Roleplay, Reasoning, Math, Coding, Extraction, STEM, and Humanities.[^oliaroSuffixDecodingExtremeSpeculative2024]
- SpecForge lists it as its instruction-following benchmark.[^liSpecForgeFlexibleEfficient2026] The Minitron paper uses it for instruction-following and roleplay.[^muralidharanCompactLanguageModels2024]
- The papers do not state the number of questions.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | Multi-turn conversation task for speedup and $\tau$; also the dataset for the ablation, the scaling-law figure, and the SGLang and vLLM batch-size tables | Vicuna 13B, LLaMA-Instruct 3.1 8B and 3.3 70B, DeepSeek-R1-Distill-LLaMA 8B | EAGLE-3 on Vicuna 13B at temperature 0: 5.58x, $\tau$ 6.65[^liEAGLE3ScalingInference2025] |
| [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md) | Multi-turn conversation task for speedup and $\tau$ | Five targets with Eagle3 drafts | LTD on V 13B at temperature 0: 4.64, $\tau$ 8.24[^zhangLearningDraftAdaptive2026] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Chat prompt set | Qwen3 on Transformers; more models on SGLang and vLLM | DFlash (16) on Q3-4B at temperature 0: 2.85×, $\tau$ 4.35[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | Chat prompt set for accepted length | Qwen3-4B, 8B, 14B, Gemma4-12B; temperature 1.0 | DSpark $\tau$ from 3.49 to 3.72 across the four targets[^chengDSparkConfidenceScheduledSpeculative2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | Chat prompt set for speedup and $\tau$ | Qwen3-8B and 14B; greedy and temperature 1.0 | DPara on Qwen3-8B, greedy: 2.25×, $\tau$ 3.12[^liuWhenParallelDrafter2026] |
| [LK Losses](../papers/samarinLKLossesDirect2026.md) | Evaluation prompts (full MT-Bench) for $\tau$ and speedup under chain sampling | Six targets; temperature 0 and 1 | Llama 3.3 70B EAGLE-3 trained with KL at $T=0$: $\tau$ 4.01, speedup 3.01[^samarinLKLossesDirect2026] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | Instruction-following prompt set for serving throughput | Seven targets on SGLang | SpecBundle speedup from 1.24 to 2.61[^liSpecForgeFlexibleEfficient2026] |
| [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md) | One of four datasets in the appendix evaluation | Vicuna 33B and Llama2 13B targets; temperature 0.7 | SpecEdge server throughput up to 1.87x the server-only baseline[^parkSpecEdgeScalableEdgeAssisted2025] |
| [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md) | 100-prompt subsample for offloaded inference speed; draft-budget study | Llama 2-7B / 70B and Llama 3-8B / 70B | SpecExec on Llama 3-8B / 70B at $t=0$: 21.58 accepted tokens per iteration, 17.5x[^svirschevskiSpecExecMassivelyParallel2024] |
| [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) | Indirectly: eight MT-Bench categories are part of the Spec-Bench workload | Llama-3.1-8B-Instruct | Reported per Spec-Bench category, see [Spec-Bench](../benchmarks/spec-bench.md)[^oliaroSuffixDecodingExtremeSpeculative2024] |
| [Minitron](../papers/muralidharanCompactLanguageModels2024.md) | MT-Bench score of instruction-tuned small models | Minitron 4B-instruct and five baselines | Minitron 4B-instruct: 6.46[^muralidharanCompactLanguageModels2024] |

## Speed metrics

Speculative-decoding speedup, acceptance length, and throughput measured with this dataset's prompts. These numbers say nothing about task accuracy. Each subsection is one paper and one setting, and rows from different subsections are not comparable.

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): Table 1

Speedup over vanilla autoregressive decoding and average acceptance length $\tau$. V = Vicuna, L31 = LLaMA-Instruct 3.1, L33 = LLaMA-Instruct 3.3, DSL = DeepSeek-R1-Distill-LLaMA. SpS is standard speculative sampling with Vicuna-68M as the draft model. The baseline (1.00x) is Huggingface.transformers with the PyTorch backend and a pre-allocated KV cache.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| V 13B | 0 | SpS | 1.93x | 2.27 |
| V 13B | 0 | PLD | 1.58x | 1.63 |
| V 13B | 0 | Medusa | 2.07x | 2.59 |
| V 13B | 0 | Lookahead | 1.65x | 1.69 |
| V 13B | 0 | Hydra | 2.88x | 3.65 |
| V 13B | 0 | EAGLE | 3.07x | 3.98 |
| V 13B | 0 | EAGLE-2 | 4.26x | 4.83 |
| V 13B | 0 | EAGLE-3 | 5.58x | 6.65 |
| L31 8B | 0 | EAGLE-2 | 3.16x | 4.05 |
| L31 8B | 0 | EAGLE-3 | 4.40x | 6.13 |
| L33 70B | 0 | EAGLE-2 | 2.83x | 3.67 |
| L33 70B | 0 | EAGLE-3 | 4.11x | 5.63 |
| DSL 8B | 0 | EAGLE-2 | 2.92x | 3.80 |
| DSL 8B | 0 | EAGLE-3 | 4.05x | 5.58 |
| V 13B | 1 | SpS | 1.62x | 1.84 |
| V 13B | 1 | EAGLE | 2.32x | 3.20 |
| V 13B | 1 | EAGLE-2 | 3.80x | 4.40 |
| V 13B | 1 | EAGLE-3 | 4.57x | 5.42 |
| L31 8B | 1 | EAGLE-2 | 2.44x | 3.16 |
| L31 8B | 1 | EAGLE-3 | 3.07x | 4.24 |
| L33 70B | 1 | EAGLE-2 | 2.73x | 3.51 |
| L33 70B | 1 | EAGLE-3 | 3.96x | 5.45 |
| DSL 8B | 1 | EAGLE-2 | 2.69x | 3.41 |
| DSL 8B | 1 | EAGLE-3 | 3.20x | 4.49 |

All rows: [^liEAGLE3ScalingInference2025]

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): ablation (Table 2)

Each row adds one change to EAGLE-2: removing the feature prediction constraint ("remove fea con"), then replacing top-layer features with fused low, middle, and high-level features. The first and last rows carry the same values as the Temperature=0 rows of Table 1.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| LLaMA-Instruct 3.1 8B | not stated | EAGLE-2 | 3.16x | 4.05 |
| LLaMA-Instruct 3.1 8B | not stated | + remove fea con | 3.82x | 5.37 |
| LLaMA-Instruct 3.1 8B | not stated | + fused features (ours) | 4.40x | 6.13 |

All rows: [^liEAGLE3ScalingInference2025]

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): throughput improvement in SGLang by batch size (Table 3)

Single H100 GPU, SGLang v0.4.4, baseline SGLang without speculative sampling (1.00x), no tree structure, chain length 3. Column headers are batch sizes. The paper states that the SGLang team ran these experiments.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 | 64 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LLaMA-Instruct 3.1 8B | not stated | EAGLE | 1.40x | 1.38x | 1.23x | 1.02x | 0.93x | 0.94x | 0.88x | 0.99x | 0.99x |
| LLaMA-Instruct 3.1 8B | not stated | EAGLE-3 | 1.81x | 1.82x | 1.62x | 1.48x | 1.39x | 1.32x | 1.38x | 1.34x | 1.38x |

All rows: [^liEAGLE3ScalingInference2025]

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): SGLang throughput at batch size 1 (Table 4)

H100, same model and dataset as Table 3.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | Throughput (bs=1) |
|---|---|---|---|
| LLaMA-Instruct 3.1 8B | not stated | SGLang (w/o speculative, 1x H100) | 158.34 tokens/s |
| LLaMA-Instruct 3.1 8B | not stated | SGLang + EAGLE-2 (1x H100) | 244.10 tokens/s |
| LLaMA-Instruct 3.1 8B | not stated | SGLang + EAGLE-3 (1x H100) | 373.25 tokens/s |

All rows: [^liEAGLE3ScalingInference2025]

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): throughput improvement in vLLM by batch size (Table 5)

Baseline vLLM without speculative sampling (1.00x), no tree structure, maximum chain length 2. Column headers are batch sizes. The body text gives the GPU as RTX3090 and the table caption gives it as A100.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 |
|---|---|---|---|---|---|---|---|---|---|---|
| LLaMA-Instruct 3.1 8B | not stated | EAGLE | 1.30x | 1.25x | 1.21x | 1.10x | 1.03x | 0.93x | 0.82x | 0.71x |
| LLaMA-Instruct 3.1 8B | not stated | EAGLE-3 | 1.75x | 1.68x | 1.58x | 1.49x | 1.42x | 1.36x | 1.21x | 1.01x |

All rows: [^liEAGLE3ScalingInference2025]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): Table 1, Transformers backend

Qwen3 (Q3) targets with thinking mode disabled, maximum of 2048 generated tokens. Speedup is end-to-end over the autoregressive baseline. The number in parentheses is the draft tree size for EAGLE-3 and the block size for DFlash. EAGLE-3 uses 7 draft steps and top-$k$ 10, with the checkpoints released by AngelSlim.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Q3-4B | 0 | EAGLE-3 (16) | 1.74× | 3.02 |
| Q3-4B | 0 | EAGLE-3 (60) | 2.04× | 3.49 |
| Q3-4B | 0 | DFlash (16) | 2.85× | 4.35 |
| Q3-8B | 0 | EAGLE-3 (16) | 1.63× | 2.83 |
| Q3-8B | 0 | EAGLE-3 (60) | 1.90× | 3.26 |
| Q3-8B | 0 | DFlash (16) | 2.75× | 4.24 |
| Q3-4B | 1 | EAGLE-3 (16) | 1.70× | 2.95 |
| Q3-4B | 1 | EAGLE-3 (60) | 1.91× | 3.36 |
| Q3-4B | 1 | DFlash (16) | 2.67× | 4.07 |
| Q3-8B | 1 | EAGLE-3 (16) | 1.58× | 2.70 |
| Q3-8B | 1 | EAGLE-3 (60) | 1.70× | 3.05 |
| Q3-8B | 1 | DFlash (16) | 2.47× | 3.80 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): more models on SGLang (Table 11)

One B200, concurrency 8. Speedup is over autoregressive decoding. MTP is the model's native MTP.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3.5-4B | not stated | MTP | 1.3× | 5.3 |
| Qwen3.5-4B | not stated | DFlash | 2.3× | 5.6 |
| Qwen3.5-9B | not stated | MTP | 1.3× | 5.3 |
| Qwen3.5-9B | not stated | DFlash | 2.5× | 5.5 |
| Qwen3.5-35B-A3B | not stated | MTP | 1.2× | 5.2 |
| Qwen3.5-35B-A3B | not stated | DFlash | 1.7× | 5.4 |
| Qwen3.5-27B | not stated | DFlash | 2.5× | 5.5 |
| Qwen3-Coder-Next | not stated | DFlash | 1.2× | 3.9 |
| GPT-OSS-20B | not stated | DFlash | 2.0× | 4.2 |
| GPT-OSS-120B | not stated | DFlash | 1.3× | 3.7 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): vLLM (Table 12)

DFlash throughput and speedup over autoregressive decoding at each concurrency level.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Concurrency | Throughput (tok/s) | Speedup |
|---|---|---|---|---|---|
| Qwen3.5-9B | not stated | DFlash | 1 | 627 | 3.0× |
| Qwen3.5-9B | not stated | DFlash | 8 | 3536 | 2.2× |
| Qwen3.5-9B | not stated | DFlash | 16 | 5297 | 1.7× |
| Qwen3.5-9B | not stated | DFlash | 32 | 6787 | 1.3× |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): drafter ablations (Tables 6, 7, 8, 13)

Ablation drafters are trained on 100K samples and run on a single H200 GPU with greedy decoding. The wiki's Paper page does not record the target model of these tables.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 3-L | 2.38× | 3.18 |
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 5-L | 2.35× | 3.37 |
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 8-L | 2.23× | 3.50 |
| not stated | 0 | Target hidden features (3 draft layers, block size 16; Table 7) 3-H | 2.32× | 3.07 |
| not stated | 0 | Target hidden features (3 draft layers, block size 16; Table 7) 5-H | 2.38× | 3.18 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b16 → b16 | 2.23x | 3.50 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b16 → b8 | 2.12x | 3.18 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b8 → b16 | 2.09x | 3.09 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b8 → b8 | 2.22x | 3.29 |
| not stated | 0 | Masked-block construction (3 layers, 5 features, block size 16; Table 13) Standard | 2.13x | 2.80 |
| not stated | 0 | Masked-block construction (3 layers, 5 features, block size 16; Table 13) Sample (random anchors) | 2.38x | 3.18 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): KV injection vs input fusion (Table 9)

5-layer draft models, draft block size 8. The ablation section states greedy decoding on a single H200 GPU.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-4B | 0 | EAGLE-3-5L, Input injection, autoregressive drafting | 1.4× | 3.1 |
| Qwen3-4B | 0 | DFlash-AR, KV injection, autoregressive drafting | 1.5× | 3.4 |
| Qwen3-4B | 0 | DFlash, Input injection, block diffusion drafting | 2.0× | 2.6 |
| Qwen3-4B | 0 | DFlash, KV injection, block diffusion drafting | 2.2× | 3.0 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): accepted length (Table 1)

Accepted length $\tau$ per decoding round, including the bonus token. Standard speculative decoding with chain-based drafting. All three drafters are retrained in the same framework on the same data, with block size 7 for DFlash and DSpark and TTT horizon 7 for Eagle3. Eagle3 has 1 draft layer, DSpark and DFlash have 5. The confidence scheduler is disabled. No speedup is reported for this table.[^chengDSparkConfidenceScheduledSpeculative2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Qwen3-4B | 1.0 | Eagle3 | 2.39 |
| Qwen3-4B | 1.0 | DFlash | 3.07 |
| Qwen3-4B | 1.0 | DSpark | 3.64 |
| Qwen3-8B | 1.0 | Eagle3 | 2.66 |
| Qwen3-8B | 1.0 | DFlash | 3.11 |
| Qwen3-8B | 1.0 | DSpark | 3.72 |
| Qwen3-14B | 1.0 | Eagle3 | 2.62 |
| Qwen3-14B | 1.0 | DFlash | 3.10 |
| Qwen3-14B | 1.0 | DSpark | 3.70 |
| Gemma4-12B | 1.0 | Eagle3 | 3.19 |
| Gemma4-12B | 1.0 | DFlash | 2.98 |
| Gemma4-12B | 1.0 | DSpark | 3.49 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): Tables 1 and 3

Batch size 1, up to 512 new tokens, draft length 7, speedup over AR. Temperature 0 rows are greedy decoding (Table 1). Temperature 1.0 rows use temperature 1.0 for both the target and the drafter (Table 3). SSD-E3 uses the EAGLE3 weight of the target as draft model. SSD, SD, and PEARL on Qwen3-14B use Qwen3-0.6B as draft model. The parallel methods (PEARL, SSD, DPara) use one additional GPU for drafting.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-8B | 0 | SSD-E3 | 1.34× | 2.26 |
| Qwen3-8B | 0 | EAGLE3 | 1.27× | 2.57 |
| Qwen3-8B | 0 | DFlash | 1.94× | 3.56 |
| Qwen3-8B | 0 | DSpark | 2.13× | 4.01 |
| Qwen3-8B | 0 | DPara | 2.25× | 3.12 |
| Qwen3-14B | 0 | SSD | 1.51× | 3.47 |
| Qwen3-14B | 0 | SSD-E3 | 1.57× | 2.28 |
| Qwen3-14B | 0 | PEARL | 2.03× | 2.20 |
| Qwen3-14B | 0 | SD | 1.42× | 3.47 |
| Qwen3-14B | 0 | EAGLE3 | 1.51× | 2.57 |
| Qwen3-14B | 0 | DFlash | 2.25× | 3.55 |
| Qwen3-14B | 0 | DSpark | 2.50× | 4.02 |
| Qwen3-14B | 0 | DPara | 2.53× | 3.16 |
| Qwen3-8B | 1.0 | DFlash | 1.65× | 3.18 |
| Qwen3-8B | 1.0 | DSpark | 1.89× | 3.74 |
| Qwen3-8B | 1.0 | DPara | 1.97× | 2.93 |
| Qwen3-14B | 1.0 | DFlash | 1.94× | 3.19 |
| Qwen3-14B | 1.0 | DSpark | 2.26× | 3.79 |
| Qwen3-14B | 1.0 | DPara | 2.28× | 2.93 |

All rows: [^liuWhenParallelDrafter2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): SpecBundle inference (Table 2)

SGLang on NVIDIA H200 GPUs, 8 concurrent requests for LLaMA-3.1-8B and 16 for larger models. The highest throughput among five (speculative steps, top-k, draft tokens) configurations is reported. Existing draft models come from the EAGLE3 authors or the LMSYS team. The tables do not state the unit of the throughput column.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | #GPUs | Throughput | Speedup |
|---|---|---|---|---|---|
| Llama-3.1-8B | not stated | none (target model alone) | 1 | 190.0 | 1 |
| Llama-3.1-8B | not stated | EAGLE3, existing open-source draft model | 1 | 454.7 | 2.39 |
| Llama-3.1-8B | not stated | EAGLE3, SpecBundle draft model | 1 | 450.0 | 2.37 |
| Llama-3.3-70B | not stated | none (target model alone) | 4 | 540.5 | 1 |
| Llama-3.3-70B | not stated | EAGLE3, existing open-source draft model | 4 | 1272.7 | 2.35 |
| Llama-3.3-70B | not stated | EAGLE3, SpecBundle draft model | 4 | 1253.0 | 2.31 |
| Llama-4-Scout | not stated | none (target model alone) | 8 | 502.1 | 1 |
| Llama-4-Scout | not stated | EAGLE3, existing open-source draft model | 8 | 1253.0 | 2.50 |
| Llama-4-Scout | not stated | EAGLE3, SpecBundle draft model | 8 | 1312.4 | 2.61 |
| Qwen-30B-A3B | not stated | none (target model alone) | 4 | 1341.3 | 1 |
| Qwen-30B-A3B | not stated | EAGLE3, SpecBundle draft model | 4 | 2086.1 | 1.55 |
| Qwen-235B-A22B | not stated | none (target model alone) | 8 | 529.9 | 1 |
| Qwen-235B-A22B | not stated | EAGLE3, existing open-source draft model | 8 | 642.7 | 1.21 |
| Qwen-235B-A22B | not stated | EAGLE3, SpecBundle draft model | 8 | 814.5 | 1.54 |
| Ling-Flash-V2 | not stated | none (target model alone) | 8 | 728.5 | 1 |
| Ling-Flash-V2 | not stated | EAGLE3, SpecBundle draft model | 8 | 1022.6 | 1.40 |
| Kimi-K2 | not stated | none (target model alone) | 8 | 430.9 | 1 |
| Kimi-K2 | not stated | EAGLE3, SpecBundle draft model | 8 | 533.8 | 1.24 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): MoE draft models (Table 4)

The table is captioned "Acceptance rate of MoE models with different settings", with MoE top-k = 1, EAGLE3 number of steps = 3, EAGLE3 top-k = 1, and EAGLE3 number of draft tokens = 4.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | Acceptance |
|---|---|---|---|
| not stated | not stated | MoE draft, Same Params, 2 experts | 1.16 |
| not stated | not stated | MoE draft, Same FLOPS, 2 experts | 1.61 |
| not stated | not stated | MoE draft, Same FLOPS, 3 experts | 1.62 |
| not stated | not stated | MoE draft, Same FLOPS, 4 experts | 1.63 |
| not stated | not stated | MoE draft, With Shared Experts, 2 experts | 1.52 |
| not stated | not stated | MoE draft, With Shared Experts, 3 experts | 1.52 |
| not stated | not stated | MoE draft, With Shared Experts, 4 experts | 1.53 |
| not stated | not stated | Dense Draft Model | 2.99 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [LK Losses](../papers/samarinLKLossesDirect2026.md): Table 4

Chain sampling in vLLM v0.11.0, batch size 1, speedup relative to decoding without speculative decoding. $\tau$ includes the bonus token. EAGLE-3 and DeepSeek-MTP drafts are evaluated with $K=7$. "Trained with" rows are the paper's own drafts trained with the named loss. Public checkpoints are HuggingFace checkpoints run through the same pipeline (RH = RedHatAI, YH = yuhuili, ZK = zhuyksir, DS = deepseek-ai).[^samarinLKLossesDirect2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with KL | 2.60 | 3.75 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with TV | 1.96 | 2.81 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.61 | 3.77 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}$, $\lambda=0.5$ | 2.63 | 3.78 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=0.7$ | 2.61 | 3.79 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=1$ | 2.64 | 3.80 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.62 | 3.84 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=10$ | 2.53 | 3.67 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint RH-8B | 2.09 | 3.08 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint YH-8B | 2.42 | 3.44 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint ZK-8B | 2.45 | 3.54 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with KL | 3.01 | 4.01 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.00 | 3.95 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.98 | 4.00 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | public checkpoint RH-70B | 2.35 | 3.11 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | public checkpoint YH-70B | 2.50 | 3.13 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with KL | 1.41 | 3.31 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.41 | 3.27 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.42 | 3.35 |
| GPT-OSS 20B (EAGLE-3) | 0 | public checkpoint RH-20B† | 1.26 | 2.90 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with KL | 1.57 | 2.81 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.59 | 2.80 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.62 | 2.86 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with KL | 2.09 | 3.33 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.10 | 3.29 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.13 | 3.36 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | public checkpoint RH-235B | 1.85 | 2.92 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | public checkpoint ZK-235B‡ | 1.94 | 3.06 |
| DeepSeek V3 0324 (MTP) | 0 | trained with KL | 2.22 | 3.96 |
| DeepSeek V3 0324 (MTP) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$ | 2.22 | 4.00 |
| DeepSeek V3 0324 (MTP) | 0 | public checkpoint DS-685B | 1.66 | 2.90 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with KL | 2.29 | 3.39 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with TV | 1.83 | 2.67 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.30 | 3.50 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}$, $\lambda=0.5$ | 2.36 | 3.35 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=0.7$ | 2.37 | 3.53 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=1$ | 2.30 | 3.51 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.39 | 3.48 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=10$ | 2.30 | 3.34 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint RH-8B | 1.83 | 2.67 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint YH-8B | 2.22 | 2.97 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint ZK-8B | 2.68 | 3.06 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with KL | 2.82 | 3.76 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.85 | 3.76 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.89 | 3.89 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | public checkpoint RH-70B | 2.10 | 2.88 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | public checkpoint YH-70B | 2.07 | 2.77 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with KL | 1.30 | 3.12 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.35 | 3.28 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.35 | 3.20 |
| GPT-OSS 20B (EAGLE-3) | 1 | public checkpoint RH-20B† | 1.12 | 2.63 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with KL | 1.20 | 2.53 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.49 | 2.67 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.48 | 2.69 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with KL | 1.84 | 2.96 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.96 | 3.11 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.98 | 3.18 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | public checkpoint RH-235B | 1.61 | 2.56 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | public checkpoint ZK-235B‡ | 1.63 | 2.64 |
| DeepSeek V3 0324 (MTP) | 1 | trained with KL | 1.85 | 3.66 |
| DeepSeek V3 0324 (MTP) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$ | 2.14 | 3.88 |
| DeepSeek V3 0324 (MTP) | 1 | public checkpoint DS-685B | 1.54 | 2.82 |

All rows: [^samarinLKLossesDirect2026]

### [LK Losses](../papers/samarinLKLossesDirect2026.md): MEDUSA and MLP speculator drafts (Table 1)

Average acceptance length only, evaluated with $K=6$.[^samarinLKLossesDirect2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Llama-3.1-8B-Instruct | 0 | MEDUSA KL | 2.05 |
| Llama-3.1-8B-Instruct | 0 | MEDUSA $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.06 |
| Llama-3.1-8B-Instruct | 0 | MEDUSA $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 2.07 |
| Llama-3.1-8B-Instruct | 0 | MLP KL | 2.45 |
| Llama-3.1-8B-Instruct | 0 | MLP $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.48 |
| Llama-3.1-8B-Instruct | 0 | MLP $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 2.48 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA KL | 1.72 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.78 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 1.85 |
| Llama-3.1-8B-Instruct | 1 | MLP KL | 2.13 |
| Llama-3.1-8B-Instruct | 1 | MLP $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.17 |
| Llama-3.1-8B-Instruct | 1 | MLP $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 2.19 |

All rows: [^samarinLKLossesDirect2026]

### [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md): Tables 1 and 5

Temperature 0 rows are Table 1 and temperature 1 rows are the per-task part of Table 5. Policies are trained only at greedy decoding. Speedup relative to vanilla auto-regressive decoding. L31 8B = Llama-3.1-8B-Instruct, V 13B = Vicuna-13B-v1.3, Dpsk 8B = DeepSeek-R1-Distill-LLaMA 8B. Default Eagle3 uses verification size 60 and 50 for the 8B and 13B LLMs, draft depth 8, and 10 nodes selected during expansion. GS is grid search over draft depth and verification size on HumanEval. LTD is the paper's learned policy.[^zhangLearningDraftAdaptive2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| L31 8B | 0 | Eagle3 | 3.70 | 6.39 |
| L31 8B | 0 | Eagle3+DDD | 3.67 | 5.41 |
| L31 8B | 0 | Eagle3+Svip | 3.65 | 6.21 |
| L31 8B | 0 | Eagle3+GT | 3.79 | 5.86 |
| L31 8B | 0 | Eagle3+C2T | 3.80 | 6.39 |
| L31 8B | 0 | Eagle3+Disco | 3.70 | 6.11 |
| L31 8B | 0 | Eagle3+Spec++ | 3.82 | 6.09 |
| L31 8B | 0 | Eagle3+GS | 3.83 | 6.75 |
| L31 8B | 0 | Eagle3+LTD | 3.96 | 6.74 |
| V 13B | 0 | Eagle3 | 4.48 | 7.22 |
| V 13B | 0 | Eagle3+DDD | 4.15 | 6.69 |
| V 13B | 0 | Eagle3+Svip | 4.02 | 7.74 |
| V 13B | 0 | Eagle3+GT | 4.15 | 6.85 |
| V 13B | 0 | Eagle3+C2T | 4.33 | 7.22 |
| V 13B | 0 | Eagle3+Disco | 4.48 | 7.08 |
| V 13B | 0 | Eagle3+Spec++ | 4.25 | 6.78 |
| V 13B | 0 | Eagle3+GS | 4.53 | 7.99 |
| V 13B | 0 | Eagle3+LTD | 4.64 | 8.24 |
| Dpsk 8B | 0 | Eagle3 | 3.67 | 5.82 |
| Dpsk 8B | 0 | Eagle3+GS | 3.69 | 6.42 |
| Dpsk 8B | 0 | Eagle3+LTD | 4.05 | 6.32 |
| Qwen3 14B | 0 | Eagle3+GS | 2.34 | 3.40 |
| Qwen3 14B | 0 | Eagle3+LTD | 2.44 | 3.34 |
| Qwen3 32B | 0 | Eagle3+GS | 1.76 | 3.30 |
| Qwen3 32B | 0 | Eagle3+LTD | 2.42 | 3.17 |
| L31 8B | 1 | Eagle3 | 2.85 | 4.11 |
| L31 8B | 1 | Eagle3+DDD | 2.89 | 3.40 |
| L31 8B | 1 | Eagle3+Svip | 2.74 | 3.41 |
| L31 8B | 1 | Eagle3+GT | 2.75 | 3.54 |
| L31 8B | 1 | Eagle3+C2T | 2.78 | 4.11 |
| L31 8B | 1 | Eagle3+Disco | 2.82 | 3.82 |
| L31 8B | 1 | Eagle3+Spec++ | 2.92 | 4.20 |
| L31 8B | 1 | Eagle3+GS | 2.79 | 4.08 |
| L31 8B | 1 | Eagle3+LTD | 2.85 | 4.02 |
| V 13B | 1 | Eagle3 | 3.60 | 5.55 |
| V 13B | 1 | Eagle3+DDD | 3.40 | 5.05 |
| V 13B | 1 | Eagle3+Svip | 3.18 | 5.73 |
| V 13B | 1 | Eagle3+GT | 3.43 | 5.36 |
| V 13B | 1 | Eagle3+C2T | 3.38 | 5.66 |
| V 13B | 1 | Eagle3+Disco | 3.48 | 5.55 |
| V 13B | 1 | Eagle3+Spec++ | 3.61 | 5.58 |
| V 13B | 1 | Eagle3+GS | 3.58 | 6.30 |
| V 13B | 1 | Eagle3+LTD | 3.82 | 6.40 |
| Dpsk 8B | 1 | Eagle3 | 3.07 | 4.74 |
| Dpsk 8B | 1 | Eagle3+GS | 3.05 | 5.19 |
| Dpsk 8B | 1 | Eagle3+LTD | 3.18 | 5.20 |
| Qwen3 14B | 1 | Eagle3+GS | 2.05 | 3.13 |
| Qwen3 14B | 1 | Eagle3+LTD | 2.16 | 3.11 |
| Qwen3 32B | 1 | Eagle3+GS | 1.56 | 2.89 |
| Qwen3 32B | 1 | Eagle3+LTD | 2.17 | 2.78 |

All rows: [^zhangLearningDraftAdaptive2026]

### [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md): Tables 2 and 3

Batch size 1, draft tree size 32, up to 256 output tokens per query. The Model column is target/draft (SL = Sheared Llama, TL = Tiny Llama, JF = JackFram). Temperature is the paper's default of 0.7. Ratios in parentheses are SpecEdge over server-only. Speedup is over autoregressive decoding.[^parkSpecEdgeScalableEdgeAssisted2025]

| Model | Temp. | Method | Gen. tokens per verify | Server throughput (tok/s) | Cost efficiency (1k toks/$) | ITL (ms) | Speedup |
|---|---|---|---|---|---|---|---|
| Vicuna 33B/SL 1.3B | 0.7 | Server-only speculative decoding | 3.62±1.72 | 29.62 | 26.33 | 33.948 | 1.82x |
| Vicuna 33B/SL 1.3B | 0.7 | SpecEdge | 4.57±2.13 | 52.70 (1.78x) | 40.21 (1.53x) | 31.168 | 1.98x |
| Llama2 13B/TL 1.1B | 0.7 | Server-only speculative decoding | 3.67±1.43 | 40.96 | 36.41 | 23.136 | 1.66x |
| Llama2 13B/TL 1.1B | 0.7 | SpecEdge | 3.75±1.46 | 76.69 (1.87x) | 58.21 (1.60x) | 21.463 | 1.79x |
| Llama2 13B/JF 160M | 0.7 | Server-only speculative decoding | 2.80±1.39 | 40.80 | 36.42 | 23.458 | 1.64x |
| Llama2 13B/JF 160M | 0.7 | SpecEdge | 2.80±1.43 | 60.42 (1.48x) | 45.92 (1.26x) | 22.199 | 1.73x |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

### [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md): RAM offloading on A100 (Table 1)

The Model column is draft / target. Batch size 1. Gen. rate is the average number of draft tokens accepted per target model iteration. Budget is the draft token budget.[^svirschevskiSpecExecMassivelyParallel2024]

| Model | Temp. | Method | Budget | Gen. rate | Speed, tok/s | Speedup |
|---|---|---|---|---|---|---|
| Llama 3-8B / 70B | 0.6 | SpecExec | 1024 | 18.16 | 2.79 | 16.6x |
| Llama 3-8B / 70B | 0 | SpecExec | 2048 | 21.58 | 2.94 | 17.5x |

All rows: [^svirschevskiSpecExecMassivelyParallel2024]


### [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md): draft budget

For Llama 2-7B as draft and offloaded Llama 2-70B as target on MTBench at $t=0.6$ and top-p 0.9, the number of tokens accepted by earlier methods is empirically upper-bounded at approximately 10 regardless of the number of speculated tokens.[^svirschevskiSpecExecMassivelyParallel2024] SpecExec's margin over SpecInfer is higher on MTBench samples than on C4.[^svirschevskiSpecExecMassivelyParallel2024]

### Other observations

- EAGLE-3's ablation and its scaling-law figure (data scale relative to ShareGPT) are evaluated on MT-bench with LLaMA-Instruct 3.1 8B.[^liEAGLE3ScalingInference2025]
- In SpecForge's TTT-length sweep on Llama3.1-8B, a TTT length of 3 already achieves strong acceptance length on MT-Bench, while Math500, GSM8K, and HumanEval need approximately 13.[^liSpecForgeFlexibleEfficient2026]
- In SpecForge's Table 2, the existing draft model has slightly higher MT-Bench throughput than SpecBundle for the LLaMA-3 8B and 70B targets, which the paper describes as a trade-off.[^liSpecForgeFlexibleEfficient2026]
- In the DSpark and DPara tables, acceptance length on MT-Bench is lower than on the math and code sets for every drafter.[^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026]

## Task accuracy

Scores on the dataset's own task. These are kept apart from the speed metrics above.

### [Minitron](../papers/muralidharanCompactLanguageModels2024.md): MT-Bench score of instruction-tuned models (Table 6)

Minitron 4B-instruct is Minitron 4B after SFT.[^muralidharanCompactLanguageModels2024]

| Model | Temp. | Method | Metric | Score |
|---|---|---|---|---|
| Minitron 4B-instruct | not stated |  | MT-Bench Total | 6.46 |
| Phi-2 | not stated |  | MT-Bench Total | 4.29 |
| Qwen-1.5 Chat | not stated |  | MT-Bench Total | 5.29 |
| Gemma-2B-IT | not stated |  | MT-Bench Total | 5.19 |
| StableLM 2 Chat | not stated |  | MT-Bench Total | 5.42 |
| TinyLlama v1.0 Chat | not stated |  | MT-Bench Total | 3.46 |

All rows: [^muralidharanCompactLanguageModels2024]


## Known issues

- In SpecForge's Table 2, the Llama-4-Scout "Existing" row has the same MTBench throughput (1253.0) as the Llama-3.3-70B SpecBundle row, and the same holds for that row's GPQA and FinanceQA throughputs. The speedups differ (2.50 and 2.31).[^liSpecForgeFlexibleEfficient2026]
- Papers use different subsets: full MT-Bench,[^samarinLKLossesDirect2026] a subsample of 100 prompts,[^svirschevskiSpecExecMassivelyParallel2024] and 80 requests in the DPara sampling table.[^liuWhenParallelDrafter2026]
- The EAGLE-3 paper gives the GPU of its vLLM table as RTX3090 in the body text and as A100 in the table caption.[^liEAGLE3ScalingInference2025]

# Contradictions

### Same drafter, target, and temperature in different papers

More than one paper reports the same drafter on the same Qwen3 target and temperature with this dataset. The values are side by side below, and most of them differ.

| Target | Temp. | Method | DFlash paper[^chenDFlashBlockDiffusion2026] (speedup / $\tau$) | DSpark paper[^chengDSparkConfidenceScheduledSpeculative2026] ($\tau$) | DPara paper[^liuWhenParallelDrafter2026] (speedup / $\tau$) |
|---|---|---|---|---|---|
| Qwen3-4B | 1 | EAGLE-3 | 1.70× / 2.95 (tree size 16); 1.91× / 3.36 (tree size 60) | 2.39 | – |
| Qwen3-4B | 1 | DFlash | 2.67× / 4.07 (block size 16) | 3.07 | – |
| Qwen3-8B | 0 | EAGLE-3 | 1.63× / 2.83 (tree size 16); 1.90× / 3.26 (tree size 60) | – | 1.27× / 2.57 |
| Qwen3-8B | 0 | DFlash | 2.75× / 4.24 (block size 16) | – | 1.94× / 3.56 |
| Qwen3-8B | 1 | EAGLE-3 | 1.58× / 2.70 (tree size 16); 1.70× / 3.05 (tree size 60) | 2.66 | – |
| Qwen3-8B | 1 | DFlash | 2.47× / 3.80 (block size 16) | 3.11 | 1.65× / 3.18 |
| Qwen3-8B | 1 | DSpark | – | 3.72 | 1.89× / 3.74 |
| Qwen3-14B | 1 | DFlash | – | 3.10 | 1.94× / 3.19 |
| Qwen3-14B | 1 | DSpark | – | 3.70 | 2.26× / 3.79 |

The settings differ in ways that the papers state. The DFlash paper runs the Transformers backend on H200 GPUs with up to 2048 generated tokens, uses the EAGLE-3 checkpoints released by AngelSlim with tree drafting, and uses DFlash block size 16.[^chenDFlashBlockDiffusion2026] The DSpark paper retrains all three drafters in one framework on the same data, uses chain-based drafting with block size 7 (TTT horizon 7 for Eagle3), and reports only $\tau$.[^chengDSparkConfidenceScheduledSpeculative2026] The DPara paper uses batch size 1, draft length 7, and up to 512 new tokens on an H800 node.[^liuWhenParallelDrafter2026]

### EAGLE-3 public checkpoints in different papers

Each cell is speedup / $\tau$ for EAGLE-3 on the same target. L31 8B = LLaMA-Instruct 3.1 8B, L33 70B = LLaMA-Instruct 3.3 70B, V 13B = Vicuna 13B, DSL 8B = DeepSeek-R1-Distill-LLaMA 8B.[^liEAGLE3ScalingInference2025]

| Target | Temp. | EAGLE-3 paper[^liEAGLE3ScalingInference2025] | Learning to Draft paper[^zhangLearningDraftAdaptive2026] | LK Losses paper[^samarinLKLossesDirect2026] |
|---|---|---|---|---|
| DSL 8B | 0 | 4.05x / 5.58 | 3.67 / 5.82 | – |
| L31 8B | 0 | 4.40x / 6.13 | 3.70 / 6.39 | 2.42 / 3.44 (YH-8B) |
| L33 70B | 0 | 4.11x / 5.63 | – | 2.50 / 3.13 (YH-70B) |
| V 13B | 0 | 5.58x / 6.65 | 4.48 / 7.22 | – |
| DSL 8B | 1 | 3.20x / 4.49 | 3.07 / 4.74 | – |
| L31 8B | 1 | 3.07x / 4.24 | 2.85 / 4.11 | 2.22 / 2.97 (YH-8B) |
| L33 70B | 1 | 3.96x / 5.45 | – | 2.07 / 2.77 (YH-70B) |
| V 13B | 1 | 4.57x / 5.42 | 3.60 / 5.55 | – |

The EAGLE-3 paper measures against Huggingface.transformers and does not state the hardware for its Table 1.[^liEAGLE3ScalingInference2025] The Learning to Draft paper runs the official Eagle3 releases with verification size 60 (50 for the 13B model), draft depth 8, and 10 nodes selected during expansion.[^zhangLearningDraftAdaptive2026] The LK Losses paper runs public HuggingFace checkpoints (YH = yuhuili) with chain sampling at $K=7$ in vLLM, not tree drafting.[^samarinLKLossesDirect2026]


## Related

- Methods measured on it: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md), [Medusa](../methods/medusa.md), [PEARL](../methods/pearl.md), [SpecExec](../methods/specexec.md), [SpecInfer](../methods/specinfer.md), [Sequoia](../methods/sequoia.md), [Multi-token prediction](../methods/multi-token-prediction.md)
- Serving engines used for the measurements: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets evaluated alongside it: [Alpaca](alpaca.md), [GSM8K](gsm8k.md), [HumanEval](humaneval.md), [MATH-500](math-500.md), [MBPP](mbpp.md), [LiveCodeBench](livecodebench.md), [C4](c4.md), [WikiText-2](wikitext-2.md), [CNN/Daily Mail](cnn-dailymail.md)
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
