---
type: Dataset
title: GSM8K
description: Grade-school math word problem dataset that the wiki's papers use as a math prompt set for speculative-decoding speed measurements and as a math accuracy test.
tags: [math, reasoning, speculative-decoding, evaluation]
sources:
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
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
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: wangAgentDropoutDynamicAgent2025
    resource: zotero://select/items/@wangAgentDropoutDynamicAgent2025
    title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: wangEfficientOnDeviceDiffusion2026
    resource: zotero://select/items/@wangEfficientOnDeviceDiffusion2026
    title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
---

# GSM8K

## Overview

GSM8K contains multi-step grade-school math word problems.[^wangWhenRLMeets2026] The papers in this wiki use it in two different ways. Most use its prompts as the mathematical-reasoning workload for measuring [speculative decoding](../methods/speculative-decoding.md) speedup and acceptance length.[^liEAGLE3ScalingInference2025][^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^liSpecForgeFlexibleEfficient2026][^samarinLKLossesDirect2026][^zhangLearningDraftAdaptive2026][^kumarSpeculativeSpeculativeDecoding2026][^weiSDFPSpeculativeDecoding2026] A smaller group reports task accuracy on it.[^wangAgentDropoutDynamicAgent2025][^muralidharanCompactLanguageModels2024][^xiaShearedLLaMAAccelerating2024][^wangEfficientOnDeviceDiffusion2026][^zhouDistillSpecImprovingSpeculative2024]

## Composition

- The LK Losses paper describes it as grade-school math problems.[^samarinLKLossesDirect2026] The llada.cpp paper lists it as a grade-school math problem dataset.[^wangEfficientOnDeviceDiffusion2026] The DistillSpec paper describes its task as arithmetic reasoning.[^zhouDistillSpecImprovingSpeculative2024]
- The Aurora paper characterizes its outputs as numerical symbols and multi-step reasoning traces with relatively consistent answer structures.[^wangWhenRLMeets2026]
- The papers do not state the dataset's size or splits. The subsets they use are in the table below.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | Mathematical-reasoning task for speedup and $\tau$ | Vicuna 13B, LLaMA-Instruct 3.1 8B and 3.3 70B, DeepSeek-R1-Distill-LLaMA 8B; temperature 0 and 1 | EAGLE-3 on Vicuna 13B at temperature 0: 5.32x, $\tau$ 6.29[^liEAGLE3ScalingInference2025] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Math prompt set for speedup and $\tau$ | Qwen3-4B and 8B on Transformers; LLaMA-3.1-8B-Instruct on SGLang | DFlash (16) on Q3-4B at temperature 0: 5.15×, $\tau$ 6.53[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | Math prompt set for accepted length | Qwen3-4B, 8B, 14B, Gemma4-12B; temperature 1.0 | DSpark $\tau$ from 6.05 to 6.21 across the four targets[^chengDSparkConfidenceScheduledSpeculative2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | Math prompt set for speedup, $\tau$, batched throughput, and the latency breakdown | Qwen3-8B and 14B; greedy and temperature 1.0 | DPara on Qwen3-8B, greedy: 4.17×, $\tau$ 5.82[^liuWhenParallelDrafter2026] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | Math prompt set for serving throughput with EAGLE3 draft models | Seven targets on SGLang | SpecBundle speedup from 1.40 to 2.13[^liSpecForgeFlexibleEfficient2026] |
| [LK Losses](../papers/samarinLKLossesDirect2026.md) | Evaluation prompts (full GSM8K) for $\tau$ and speedup under chain sampling | Six targets; temperature 0 and 1 | DeepSeek V3 MTP fine-tuned with the LK loss at $T=0$: $\tau$ 5.72, speedup 2.97[^samarinLKLossesDirect2026] |
| [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md) | Mathematical-reasoning task for speedup and $\tau$ | Five targets with Eagle3 drafts | LTD on L31 8B at temperature 0: 3.79, $\tau$ 6.73[^zhangLearningDraftAdaptive2026] |
| [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md) | 128 prompts, 512 decoding tokens each | Llama-3.1-70B/1B and Qwen3-32B/0.6B, greedy | SSD on Llama-3.1 70B/1B: 301 tok/s, 5.50× over AR[^kumarSpeculativeSpeculativeDecoding2026] |
| [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md) | Distillation and evaluation task for the draft model; accuracy as the quality metric | T5-XL target, T5-Small draft | At $\gamma=3$, $T=0$: speedup from 1.51× to 1.69× with distillation[^zhouDistillSpecImprovingSpeculative2024] |
| [SDFP](../papers/weiSDFPSpeculativeDecoding2026.md) | Reasoning task, 5-shot, 1,000 sampled test instances | LLaMA-2-13B, 13B-Chat, 70B; greedy | SDFP on LLaMA-2-13B: 1.36×[^weiSDFPSpeculativeDecoding2026] |
| [llada.cpp](../papers/wangEfficientOnDeviceDiffusion2026.md) | 200-sample subset for accuracy; main latency experiment | LLaDA-8B-Instruct and Llama-3-8B-Instruct on phones | LLaDA accuracy 39.0 on CPU and 43.5 with llada.cpp[^wangEfficientOnDeviceDiffusion2026] |
| [Aurora](../papers/wangWhenRLMeets2026.md) | Source of the mathematical-reasoning prompts, 7k of a 44k mixed request stream | Online draft training with EAGLE-3 | No per-dataset number[^wangWhenRLMeets2026] |
| [AgentDropout](../papers/wangAgentDropoutDynamicAgent2025.md) | Mathematical-reasoning accuracy of multi-agent systems | Llama3-8B-Instruct, Qwen2.5-72B-Instruct, Deepseek-V3-671B-Instruct; temperature 1 | AgentDropout: 73.13, 93.75, 95.63[^wangAgentDropoutDynamicAgent2025] |
| [Minitron](../papers/muralidharanCompactLanguageModels2024.md) | 5-shot accuracy of pruned and baseline models | Minitron 8B and 4B and baselines | Minitron 8B 51.3, Minitron 4B 24.1[^muralidharanCompactLanguageModels2024] |
| [Sheared-LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) | 8-shot exact match | Sheared-LLaMA-2.7B and 3B-class baselines | Sheared-LLaMA-2.7B: 2.7 (Source), 2.4 (Scaling)[^xiaShearedLLaMAAccelerating2024] |

## Speed metrics

Speculative-decoding speedup, acceptance length, and throughput measured with this dataset's prompts. These numbers say nothing about task accuracy. Each subsection is one paper and one setting, and rows from different subsections are not comparable.

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): Table 1

Speedup over vanilla autoregressive decoding and average acceptance length $\tau$. V = Vicuna, L31 = LLaMA-Instruct 3.1, L33 = LLaMA-Instruct 3.3, DSL = DeepSeek-R1-Distill-LLaMA. SpS is standard speculative sampling with Vicuna-68M as the draft model. The baseline (1.00x) is Huggingface.transformers with the PyTorch backend and a pre-allocated KV cache.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| V 13B | 0 | SpS | 1.77x | 2.01 |
| V 13B | 0 | PLD | 1.68x | 1.73 |
| V 13B | 0 | Medusa | 2.23x | 2.64 |
| V 13B | 0 | Lookahead | 1.81x | 1.90 |
| V 13B | 0 | Hydra | 2.93x | 3.66 |
| V 13B | 0 | EAGLE | 3.08x | 3.97 |
| V 13B | 0 | EAGLE-2 | 4.22x | 4.79 |
| V 13B | 0 | EAGLE-3 | 5.32x | 6.29 |
| L31 8B | 0 | EAGLE-2 | 3.39x | 4.24 |
| L31 8B | 0 | EAGLE-3 | 4.48x | 6.23 |
| L33 70B | 0 | EAGLE-2 | 2.83x | 3.69 |
| L33 70B | 0 | EAGLE-3 | 4.34x | 6.15 |
| DSL 8B | 0 | EAGLE-2 | 3.40x | 4.40 |
| DSL 8B | 0 | EAGLE-3 | 5.01x | 6.93 |
| V 13B | 1 | SpS | 1.46x | 1.73 |
| V 13B | 1 | EAGLE | 2.57x | 3.60 |
| V 13B | 1 | EAGLE-2 | 3.77x | 4.41 |
| V 13B | 1 | EAGLE-3 | 4.71x | 5.58 |
| L31 8B | 1 | EAGLE-2 | 2.86x | 3.74 |
| L31 8B | 1 | EAGLE-3 | 3.32x | 4.59 |
| L33 70B | 1 | EAGLE-2 | 2.52x | 3.36 |
| L33 70B | 1 | EAGLE-3 | 4.17x | 5.95 |
| DSL 8B | 1 | EAGLE-2 | 3.16x | 4.05 |
| DSL 8B | 1 | EAGLE-3 | 4.38x | 6.10 |

All rows: [^liEAGLE3ScalingInference2025]

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): ablation (Table 2)

Each row adds one change to EAGLE-2: removing the feature prediction constraint ("remove fea con"), then replacing top-layer features with fused low, middle, and high-level features. The first and last rows carry the same values as the Temperature=0 rows of Table 1.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| LLaMA-Instruct 3.1 8B | not stated | EAGLE-2 | 3.39x | 4.24 |
| LLaMA-Instruct 3.1 8B | not stated | + remove fea con | 3.77x | 5.22 |
| LLaMA-Instruct 3.1 8B | not stated | + fused features (ours) | 4.48x | 6.23 |

All rows: [^liEAGLE3ScalingInference2025]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): Table 1, Transformers backend

Qwen3 (Q3) targets with thinking mode disabled, maximum of 2048 generated tokens. Speedup is end-to-end over the autoregressive baseline. The number in parentheses is the draft tree size for EAGLE-3 and the block size for DFlash. EAGLE-3 uses 7 draft steps and top-$k$ 10, with the checkpoints released by AngelSlim.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Q3-4B | 0 | EAGLE-3 (16) | 1.99× | 3.30 |
| Q3-4B | 0 | EAGLE-3 (60) | 2.27× | 3.77 |
| Q3-4B | 0 | DFlash (16) | 5.15× | 6.53 |
| Q3-8B | 0 | EAGLE-3 (16) | 1.94× | 3.23 |
| Q3-8B | 0 | EAGLE-3 (60) | 2.23× | 3.71 |
| Q3-8B | 0 | DFlash (16) | 5.15× | 6.54 |
| Q3-4B | 1 | EAGLE-3 (16) | 1.89× | 3.22 |
| Q3-4B | 1 | EAGLE-3 (60) | 2.12× | 3.68 |
| Q3-4B | 1 | DFlash (16) | 4.71× | 6.00 |
| Q3-8B | 1 | EAGLE-3 (16) | 1.87× | 3.12 |
| Q3-8B | 1 | EAGLE-3 (60) | 2.07× | 3.59 |
| Q3-8B | 1 | DFlash (16) | 4.67× | 5.98 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): same training data as EAGLE-3, SGLang (Table 5)

DFlash is trained on UltraChat and ShareGPT and compared with the official EAGLE-3 checkpoints. SGLang with Spec-v1 (without scheduling overlap), Flashinfer backend, single B200 GPU. EAGLE-3 uses 7 draft steps with top-$k{=}10$ and either 10 or 60 draft tokens. DFlash uses block size 10. The baseline row is absolute throughput in tokens/s. The other rows are speedup over the baseline at each concurrency level.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| LLaMA-3.1-8B-Instruct | not stated | Baseline (TPS) | 249 | 923 | 1739 | 3245 | 5349 | – |
| LLaMA-3.1-8B-Instruct | not stated | EAGLE-3 (10) | 1.6× | 1.5× | 1.4× | 1.2× | 1.0× | 3.49 |
| LLaMA-3.1-8B-Instruct | not stated | EAGLE-3 (60) | 1.9× | 1.6× | 1.3× | 0.9× | 0.6× | 4.55 |
| LLaMA-3.1-8B-Instruct | not stated | DFlash (10) | 2.4× | 2.2× | 2.1× | 1.8× | 1.6× | 4.32 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): KV injection vs input fusion (Table 9)

5-layer draft models, draft block size 8. The ablation section states greedy decoding on a single H200 GPU.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-4B | 0 | EAGLE-3-5L, Input injection, autoregressive drafting | 2.1× | 4.2 |
| Qwen3-4B | 0 | DFlash-AR, KV injection, autoregressive drafting | 2.4× | 4.8 |
| Qwen3-4B | 0 | DFlash, Input injection, block diffusion drafting | 2.9× | 3.5 |
| Qwen3-4B | 0 | DFlash, KV injection, block diffusion drafting | 3.3× | 4.2 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): drafter without target features (Table 10)

The table gives speedup without a multiplication sign.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| not stated | 0 | 5-layer block diffusion drafter without target context features | 2.83 | 3.38 |
| not stated | 1 | 5-layer block diffusion drafter without target context features | 2.76 | 3.29 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): accepted length (Table 1)

Accepted length $\tau$ per decoding round, including the bonus token. Standard speculative decoding with chain-based drafting. All three drafters are retrained in the same framework on the same data, with block size 7 for DFlash and DSpark and TTT horizon 7 for Eagle3. Eagle3 has 1 draft layer, DSpark and DFlash have 5. The confidence scheduler is disabled. No speedup is reported for this table.[^chengDSparkConfidenceScheduledSpeculative2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Qwen3-4B | 1.0 | Eagle3 | 5.14 |
| Qwen3-4B | 1.0 | DFlash | 5.40 |
| Qwen3-4B | 1.0 | DSpark | 6.11 |
| Qwen3-8B | 1.0 | Eagle3 | 5.30 |
| Qwen3-8B | 1.0 | DFlash | 5.33 |
| Qwen3-8B | 1.0 | DSpark | 6.17 |
| Qwen3-14B | 1.0 | Eagle3 | 5.24 |
| Qwen3-14B | 1.0 | DFlash | 5.41 |
| Qwen3-14B | 1.0 | DSpark | 6.21 |
| Gemma4-12B | 1.0 | Eagle3 | 5.87 |
| Gemma4-12B | 1.0 | DFlash | 5.45 |
| Gemma4-12B | 1.0 | DSpark | 6.05 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): Tables 1 and 3

Batch size 1, up to 512 new tokens, draft length 7, speedup over AR. Temperature 0 rows are greedy decoding (Table 1). Temperature 1.0 rows use temperature 1.0 for both the target and the drafter (Table 3). SSD-E3 uses the EAGLE3 weight of the target as draft model. SSD, SD, and PEARL on Qwen3-14B use Qwen3-0.6B as draft model. The parallel methods (PEARL, SSD, DPara) use one additional GPU for drafting.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-8B | 0 | SSD-E3 | 1.51× | 2.39 |
| Qwen3-8B | 0 | EAGLE3 | 1.44× | 2.83 |
| Qwen3-8B | 0 | DFlash | 3.38× | 6.08 |
| Qwen3-8B | 0 | DSpark | 3.48× | 6.51 |
| Qwen3-8B | 0 | DPara | 4.17× | 5.82 |
| Qwen3-14B | 0 | SSD | 2.70× | 5.47 |
| Qwen3-14B | 0 | SSD-E3 | 1.76× | 2.48 |
| Qwen3-14B | 0 | PEARL | 3.35× | 3.70 |
| Qwen3-14B | 0 | SD | 2.21× | 5.47 |
| Qwen3-14B | 0 | EAGLE3 | 1.76× | 2.94 |
| Qwen3-14B | 0 | DFlash | 3.86× | 6.03 |
| Qwen3-14B | 0 | DSpark | 4.07× | 6.53 |
| Qwen3-14B | 0 | DPara | 4.53× | 5.73 |
| Qwen3-8B | 1.0 | DFlash | 2.71× | 5.28 |
| Qwen3-8B | 1.0 | DSpark | 3.06× | 6.15 |
| Qwen3-8B | 1.0 | DPara | 3.45× | 5.29 |
| Qwen3-14B | 1.0 | DFlash | 3.29× | 5.35 |
| Qwen3-14B | 1.0 | DSpark | 3.74× | 6.18 |
| Qwen3-14B | 1.0 | DPara | 4.00× | 5.31 |

All rows: [^liuWhenParallelDrafter2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): batched inference (Table 2)

Throughput in tok/s at each batch size, with speedup over AR in parentheses.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | b=1 | b=2 | b=4 | b=8 | b=16 |
|---|---|---|---|---|---|---|---|
| Qwen3-8B | not stated | AR | 141 | 277 | 529 | 937 | 1520 |
| Qwen3-8B | not stated | DSpark | 491 (3.48×) | 901 (3.25×) | 1507 (2.85×) | 2426 (2.59×) | 3627 (2.39×) |
| Qwen3-8B | not stated | DPara | 588 (4.17×) | 1052 (3.80×) | 1772 (3.35×) | 2736 (2.92×) | 3869 (2.55×) |
| Qwen3-14B | not stated | AR | 87 | 171 | 330 | 597 | 1020 |
| Qwen3-14B | not stated | DSpark | 355 (4.07×) | 647 (3.79×) | 1142 (3.47×) | 1813 (3.03×) | 2847 (2.79×) |
| Qwen3-14B | not stated | DPara | 395 (4.53×) | 721 (4.22×) | 1269 (3.85×) | 1999 (3.35×) | 3010 (2.95×) |

All rows: [^liuWhenParallelDrafter2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): backbone finetuning ablation

DPara with the same frozen AR head, comparing the original DSpark checkpoint with the finetuned M-DFlash backbone.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | $\tau$ with original DSpark checkpoint | $\tau$ with M-DFlash | Relative gain |
|---|---|---|---|---|---|
| Qwen3-8B | not stated | DPara | 4.07 | 5.82 | 43.1% |

All rows: [^liuWhenParallelDrafter2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): SpecBundle inference (Table 3)

SGLang on NVIDIA H200 GPUs, 8 concurrent requests for LLaMA-3.1-8B and 16 for larger models. The highest throughput among five (speculative steps, top-k, draft tokens) configurations is reported. Existing draft models come from the EAGLE3 authors or the LMSYS team. The tables do not state the unit of the throughput column.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | #GPUs | Throughput | Speedup |
|---|---|---|---|---|---|
| Llama-3.1-8B | not stated | none (target model alone) | 1 | 181.8 | 1 |
| Llama-3.1-8B | not stated | EAGLE3, existing open-source draft model | 1 | 228.6 | 1.26 |
| Llama-3.1-8B | not stated | EAGLE3, SpecBundle draft model | 1 | 329.7 | 1.81 |
| Llama-3.3-70B | not stated | none (target model alone) | 4 | 453.2 | 1 |
| Llama-3.3-70B | not stated | EAGLE3, existing open-source draft model | 4 | 521.5 | 1.15 |
| Llama-3.3-70B | not stated | EAGLE3, SpecBundle draft model | 4 | 722.0 | 1.59 |
| Llama-4-Scout | not stated | none (target model alone) | 8 | 455.9 | 1 |
| Llama-4-Scout | not stated | EAGLE3, existing open-source draft model | 8 | 816.6 | 1.79 |
| Llama-4-Scout | not stated | EAGLE3, SpecBundle draft model | 8 | 971.9 | 2.13 |
| Qwen-30B-A3B | not stated | none (target model alone) | 4 | 1071.3 | 1 |
| Qwen-30B-A3B | not stated | EAGLE3, SpecBundle draft model | 4 | 1499.6 | 1.40 |
| Qwen-235B-A22B | not stated | none (target model alone) | 8 | 469.1 | 1 |
| Qwen-235B-A22B | not stated | EAGLE3, existing open-source draft model | 8 | 697.0 | 1.49 |
| Qwen-235B-A22B | not stated | EAGLE3, SpecBundle draft model | 8 | 758.3 | 1.62 |
| Ling-Flash-V2 | not stated | none (target model alone) | 8 | 674.3 | 1 |
| Ling-Flash-V2 | not stated | EAGLE3, SpecBundle draft model | 8 | 1323.0 | 1.96 |
| Kimi-K2 | not stated | none (target model alone) | 8 | 337.9 | 1 |
| Kimi-K2 | not stated | EAGLE3, SpecBundle draft model | 8 | 544.2 | 1.61 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): MoE draft models (Table 4)

The table is captioned "Acceptance rate of MoE models with different settings", with MoE top-k = 1, EAGLE3 number of steps = 3, EAGLE3 top-k = 1, and EAGLE3 number of draft tokens = 4.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | Acceptance |
|---|---|---|---|
| not stated | not stated | MoE draft, Same Params, 2 experts | 1.05 |
| not stated | not stated | MoE draft, Same FLOPS, 2 experts | 1.59 |
| not stated | not stated | MoE draft, Same FLOPS, 3 experts | 1.7 |
| not stated | not stated | MoE draft, Same FLOPS, 4 experts | 1.72 |
| not stated | not stated | MoE draft, With Shared Experts, 2 experts | 1.61 |
| not stated | not stated | MoE draft, With Shared Experts, 3 experts | 1.61 |
| not stated | not stated | MoE draft, With Shared Experts, 4 experts | 1.67 |
| not stated | not stated | Dense Draft Model | 3.48 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [LK Losses](../papers/samarinLKLossesDirect2026.md): Table 4

Chain sampling in vLLM v0.11.0, batch size 1, speedup relative to decoding without speculative decoding. $\tau$ includes the bonus token. EAGLE-3 and DeepSeek-MTP drafts are evaluated with $K=7$. "Trained with" rows are the paper's own drafts trained with the named loss. Public checkpoints are HuggingFace checkpoints run through the same pipeline (RH = RedHatAI, YH = yuhuili, ZK = zhuyksir, DS = deepseek-ai).[^samarinLKLossesDirect2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with KL | 3.05 | 4.50 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with TV | 2.28 | 3.34 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.07 | 4.55 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}$, $\lambda=0.5$ | 3.07 | 4.53 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=0.7$ | 3.07 | 4.54 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=1$ | 3.08 | 4.54 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.10 | 4.57 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=10$ | 3.06 | 4.53 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint RH-8B | 2.37 | 3.57 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint YH-8B | 2.65 | 3.84 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint ZK-8B | 2.71 | 3.97 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with KL | 3.78 | 5.16 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.78 | 5.13 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.83 | 5.21 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | public checkpoint RH-70B | 2.68 | 3.62 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | public checkpoint YH-70B | 2.90 | 3.76 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with KL | 1.63 | 4.01 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.63 | 4.03 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.63 | 4.00 |
| GPT-OSS 20B (EAGLE-3) | 0 | public checkpoint RH-20B† | 1.45 | 3.49 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with KL | 1.77 | 3.00 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.82 | 3.08 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.82 | 3.06 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with KL | 2.88 | 4.76 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.91 | 4.82 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.93 | 4.87 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | public checkpoint RH-235B | 2.63 | 4.31 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | public checkpoint ZK-235B‡ | 2.94 | 4.90 |
| DeepSeek V3 0324 (MTP) | 0 | trained with KL | 2.95 | 5.67 |
| DeepSeek V3 0324 (MTP) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$ | 2.97 | 5.72 |
| DeepSeek V3 0324 (MTP) | 0 | public checkpoint DS-685B | 1.82 | 3.41 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with KL | 2.63 | 3.88 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with TV | 2.11 | 3.12 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.72 | 3.98 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}$, $\lambda=0.5$ | 2.68 | 3.95 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=0.7$ | 2.66 | 3.98 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=1$ | 2.70 | 3.96 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.72 | 4.02 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=10$ | 2.72 | 4.03 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint RH-8B | 2.05 | 3.08 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint YH-8B | 2.14 | 3.21 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint ZK-8B | 2.28 | 3.36 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with KL | 3.61 | 4.89 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.66 | 4.91 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.69 | 5.01 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | public checkpoint RH-70B | 2.44 | 3.29 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | public checkpoint YH-70B | 2.50 | 3.34 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with KL | 1.44 | 3.51 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.49 | 3.65 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.49 | 3.65 |
| GPT-OSS 20B (EAGLE-3) | 1 | public checkpoint RH-20B† | 1.26 | 3.00 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with KL | 1.32 | 2.57 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.63 | 2.78 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.66 | 2.81 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with KL | 2.50 | 4.27 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.61 | 4.50 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.68 | 4.65 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | public checkpoint RH-235B | 2.22 | 3.78 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | public checkpoint ZK-235B‡ | 2.57 | 4.43 |
| DeepSeek V3 0324 (MTP) | 1 | trained with KL | 2.30 | 5.23 |
| DeepSeek V3 0324 (MTP) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$ | 2.71 | 5.51 |
| DeepSeek V3 0324 (MTP) | 1 | public checkpoint DS-685B | 1.47 | 3.27 |

All rows: [^samarinLKLossesDirect2026]

### [LK Losses](../papers/samarinLKLossesDirect2026.md): MEDUSA and MLP speculator drafts (Table 1)

Average acceptance length only, evaluated with $K=6$.[^samarinLKLossesDirect2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Llama-3.1-8B-Instruct | 0 | MEDUSA KL | 2.11 |
| Llama-3.1-8B-Instruct | 0 | MEDUSA $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.11 |
| Llama-3.1-8B-Instruct | 0 | MEDUSA $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 2.13 |
| Llama-3.1-8B-Instruct | 0 | MLP KL | 2.42 |
| Llama-3.1-8B-Instruct | 0 | MLP $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.46 |
| Llama-3.1-8B-Instruct | 0 | MLP $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 2.46 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA KL | 1.81 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.85 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 1.92 |
| Llama-3.1-8B-Instruct | 1 | MLP KL | 2.16 |
| Llama-3.1-8B-Instruct | 1 | MLP $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.19 |
| Llama-3.1-8B-Instruct | 1 | MLP $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 2.18 |

All rows: [^samarinLKLossesDirect2026]

### [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md): Tables 1 and 5

Temperature 0 rows are Table 1 and temperature 1 rows are the per-task part of Table 5. Policies are trained only at greedy decoding. Speedup relative to vanilla auto-regressive decoding. L31 8B = Llama-3.1-8B-Instruct, V 13B = Vicuna-13B-v1.3, Dpsk 8B = DeepSeek-R1-Distill-LLaMA 8B. Default Eagle3 uses verification size 60 and 50 for the 8B and 13B LLMs, draft depth 8, and 10 nodes selected during expansion. GS is grid search over draft depth and verification size on HumanEval. LTD is the paper's learned policy.[^zhangLearningDraftAdaptive2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| L31 8B | 0 | Eagle3 | 3.58 | 6.44 |
| L31 8B | 0 | Eagle3+DDD | 3.55 | 5.48 |
| L31 8B | 0 | Eagle3+Svip | 3.47 | 6.21 |
| L31 8B | 0 | Eagle3+GT | 3.64 | 5.77 |
| L31 8B | 0 | Eagle3+C2T | 3.57 | 6.44 |
| L31 8B | 0 | Eagle3+Disco | 3.56 | 6.18 |
| L31 8B | 0 | Eagle3+Spec++ | 3.65 | 6.08 |
| L31 8B | 0 | Eagle3+GS | 3.78 | 6.91 |
| L31 8B | 0 | Eagle3+LTD | 3.79 | 6.73 |
| V 13B | 0 | Eagle3 | 4.36 | 6.58 |
| V 13B | 0 | Eagle3+DDD | 4.25 | 6.22 |
| V 13B | 0 | Eagle3+Svip | 3.86 | 6.79 |
| V 13B | 0 | Eagle3+GT | 4.07 | 6.00 |
| V 13B | 0 | Eagle3+C2T | 3.97 | 6.58 |
| V 13B | 0 | Eagle3+Disco | 4.13 | 6.49 |
| V 13B | 0 | Eagle3+Spec++ | 4.09 | 6.16 |
| V 13B | 0 | Eagle3+GS | 4.47 | 7.27 |
| V 13B | 0 | Eagle3+LTD | 4.59 | 7.38 |
| Dpsk 8B | 0 | Eagle3 | 4.73 | 7.39 |
| Dpsk 8B | 0 | Eagle3+GS | 4.83 | 8.37 |
| Dpsk 8B | 0 | Eagle3+LTD | 4.98 | 8.53 |
| Qwen3 14B | 0 | Eagle3+GS | 2.75 | 3.95 |
| Qwen3 14B | 0 | Eagle3+LTD | 2.82 | 3.92 |
| Qwen3 32B | 0 | Eagle3+GS | 2.26 | 4.10 |
| Qwen3 32B | 0 | Eagle3+LTD | 3.02 | 3.90 |
| L31 8B | 1 | Eagle3 | 3.43 | 5.24 |
| L31 8B | 1 | Eagle3+DDD | 3.35 | 4.09 |
| L31 8B | 1 | Eagle3+Svip | 3.21 | 4.92 |
| L31 8B | 1 | Eagle3+GT | 3.28 | 4.27 |
| L31 8B | 1 | Eagle3+C2T | 3.28 | 5.24 |
| L31 8B | 1 | Eagle3+Disco | 3.26 | 5.08 |
| L31 8B | 1 | Eagle3+Spec++ | 3.33 | 4.74 |
| L31 8B | 1 | Eagle3+GS | 3.36 | 5.50 |
| L31 8B | 1 | Eagle3+LTD | 3.35 | 5.09 |
| V 13B | 1 | Eagle3 | 3.68 | 5.64 |
| V 13B | 1 | Eagle3+DDD | 3.58 | 5.46 |
| V 13B | 1 | Eagle3+Svip | 3.26 | 5.78 |
| V 13B | 1 | Eagle3+GT | 3.32 | 5.26 |
| V 13B | 1 | Eagle3+C2T | 3.41 | 5.63 |
| V 13B | 1 | Eagle3+Disco | 3.67 | 5.74 |
| V 13B | 1 | Eagle3+Spec++ | 3.64 | 5.63 |
| V 13B | 1 | Eagle3+GS | 3.81 | 6.39 |
| V 13B | 1 | Eagle3+LTD | 3.75 | 6.38 |
| Dpsk 8B | 1 | Eagle3 | 3.97 | 6.89 |
| Dpsk 8B | 1 | Eagle3+GS | 4.14 | 7.64 |
| Dpsk 8B | 1 | Eagle3+LTD | 4.02 | 7.95 |
| Qwen3 14B | 1 | Eagle3+GS | 2.62 | 3.83 |
| Qwen3 14B | 1 | Eagle3+LTD | 2.73 | 3.85 |
| Qwen3 32B | 1 | Eagle3+GS | 2.10 | 3.95 |
| Qwen3 32B | 1 | Eagle3+LTD | 2.83 | 3.76 |

All rows: [^zhangLearningDraftAdaptive2026]

### [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md): end-to-end decoding speed (Appendix B.3)

The paper's own AR, SD, and SSD implementations. Batch size 1, greedy decoding, target on 4×H100, SSD draft on a separate H100. 128 prompts from the dataset, 512 decoding tokens each, decoding throughput excluding prefill. Temperature 0 is the paper's stated default of greedy decoding. Its appendix also says it uses vanilla sampling (not top-p or top-k). The Model column is target/draft.[^kumarSpeculativeSpeculativeDecoding2026]

| Model | Temp. | Method | Decode tok/s | Speedup over SD | Speedup over AR |
|---|---|---|---|---|---|
| Llama-3.1-Instruct 70B/1B | 0 | AR | 54.7 | – | – |
| Llama-3.1-Instruct 70B/1B | 0 | SD | 188 | – | – |
| Llama-3.1-Instruct 70B/1B | 0 | SSD | 301 | 1.60× | 5.50× |
| Qwen-3 32B/0.6B | 0 | AR | 88.8 | – | – |
| Qwen-3 32B/0.6B | 0 | SD | 152 | – | – |
| Qwen-3 32B/0.6B | 0 | SSD | 234 | 1.54× | 2.64× |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]

### [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md): block efficiency and speedup (Table C.1)

The Model column is target / draft. $\gamma$ is the block size. $\tau$ is block efficiency. Batch size 1 on a TPUv4 device.[^zhouDistillSpecImprovingSpeculative2024]

| Model | Temp. | Method | $\gamma$ | Speedup | $\tau$ |
|---|---|---|---|---|---|
| T5-XL (3B) / T5-Small (77M) | 0 | SD, draft without distillation | 3 | 1.51× | 2.60 |
| T5-XL (3B) / T5-Small (77M) | 0 | SD, draft distilled with GKD | 3 | 1.69× | 2.96 |
| T5-XL (3B) / T5-Small (77M) | 0 | SD, draft without distillation | 5 | 1.42× | 3.06 |
| T5-XL (3B) / T5-Small (77M) | 0 | SD, draft distilled with GKD | 5 | 1.65× | 3.68 |
| T5-XL (3B) / T5-Small (77M) | 0 | SD, draft without distillation | 7 | 1.36× | 3.27 |
| T5-XL (3B) / T5-Small (77M) | 0 | SD, draft distilled with GKD | 7 | 1.60× | 4.14 |
| T5-XL (3B) / T5-Small (77M) | 1 | SD, draft without distillation | 3 | 1.48× | 2.58 |
| T5-XL (3B) / T5-Small (77M) | 1 | SD, draft distilled with f-Distill | 3 | 1.64× | 2.84 |
| T5-XL (3B) / T5-Small (77M) | 1 | SD, draft without distillation | 5 | 1.39× | 3.03 |
| T5-XL (3B) / T5-Small (77M) | 1 | SD, draft distilled with f-Distill | 5 | 1.58× | 3.45 |
| T5-XL (3B) / T5-Small (77M) | 1 | SD, draft without distillation | 7 | 1.33× | 3.23 |
| T5-XL (3B) / T5-Small (77M) | 1 | SD, draft distilled with f-Distill | 7 | 1.53× | 3.84 |

All rows: [^zhouDistillSpecImprovingSpeculative2024]

### [SDFP](../papers/weiSDFPSpeculativeDecoding2026.md): Table I

Greedy decoding, batch size 1, 5-shot prompts, maximum output length 64, 1,000 randomly sampled test instances. Speedup is wall-time over vanilla autoregressive decoding. $\alpha$ is the token acceptance rate.[^weiSDFPSpeculativeDecoding2026]

| Model | Temp. | Method | Speedup | $\alpha$ |
|---|---|---|---|---|
| LLaMA-2-13B | 0 | VANILLA | 1.00× | N/A |
| LLaMA-2-13B | 0 | PARALLEL | 0.99× | N/A |
| LLaMA-2-13B | 0 | LOOKAHEAD | 1.29× | N/A |
| LLaMA-2-13B | 0 | SWIFT | 1.31× | 0.98 |
| LLaMA-2-13B | 0 | SDFP | 1.36× | 0.95 |
| LLaMA-2-13B-Chat | 0 | VANILLA | 1.00× | N/A |
| LLaMA-2-13B-Chat | 0 | PARALLEL | 0.97× | N/A |
| LLaMA-2-13B-Chat | 0 | LOOKAHEAD | 1.31× | N/A |
| LLaMA-2-13B-Chat | 0 | SWIFT | 1.25× | 0.92 |
| LLaMA-2-13B-Chat | 0 | SDFP | 1.27× | 0.92 |
| LLaMA-2-70B | 0 | VANILLA | 1.00× | N/A |
| LLaMA-2-70B | 0 | PARALLEL | 0.97× | N/A |
| LLaMA-2-70B | 0 | LOOKAHEAD | 1.35× | N/A |
| LLaMA-2-70B | 0 | SWIFT | 1.39× | 0.98 |
| LLaMA-2-70B | 0 | SDFP | 1.37× | 0.95 |

All rows: [^weiSDFPSpeculativeDecoding2026]

### [llada.cpp](../papers/wangEfficientOnDeviceDiffusion2026.md): on-device latency breakdown (Table 6)

Latency of a diffusion LLM on a phone, not a speedup over autoregressive decoding. 128-token generation on SM8750. Each row adds one component to the row above.[^wangEfficientOnDeviceDiffusion2026]

| Model | Temp. | Method | Latency | Rel. Gain | Tot. Gain |
|---|---|---|---|---|---|
| LLaDA-8B-Instruct | 0 | CPU | 2996.2 s | 1.00× | 1.00× |
| LLaDA-8B-Instruct | 0 | CPU + prefix KV cache | 607.0 s | 4.94× | 4.94× |
| LLaDA-8B-Instruct | 0 | NPU | 341.2 s | 1.78× | 8.78× |
| LLaDA-8B-Instruct | 0 | NPU + prefix KV cache | 87.0 s | 3.92× | 34.44× |
| LLaDA-8B-Instruct | 0 | + SOMR | 71.6 s | 1.22× | 41.87× |
| LLaDA-8B-Instruct | 0 | + MBSD | 59.8 s | 1.20× | 50.08× |
| LLaDA-8B-Instruct | 0 | + STS | 16.4 s | 3.65× | 182.55× |
| LLaDA-8B-Instruct | 0 | + SLS | 15.8 s | 1.04× | 189.38× |
| LLaDA-8B-Instruct | 0 | + SCR | 16.1 s | 0.98× | 186.34× |

All rows: [^wangEfficientOnDeviceDiffusion2026]


## Task accuracy

Scores on the dataset's own task. These are kept apart from the speed metrics above.

### [AgentDropout](../papers/wangAgentDropoutDynamicAgent2025.md): Tables 1, 3, 4, 5, 6

The source does not name the metric unit and calls the gains "accuracy". Temperature 1. Methods are single-agent (Vanilla, CoT) and multi-agent systems (MAS, AgentPrune, AgentDropout). The main rows start from a fully connected intra-round graph. Rows after the first 18 are Llama3 ablations.[^wangAgentDropoutDynamicAgent2025]

| Model | Temp. | Method | Score |
|---|---|---|---|
| Llama3-8B-Instruct | 1 | Vanilla | 70.23 |
| Llama3-8B-Instruct | 1 | CoT | 70.47 |
| Llama3-8B-Instruct | 1 | $\text{MAS}_{round=1}$ | 69.30 |
| Llama3-8B-Instruct | 1 | $\text{MAS}_{round=T}$ | 71.48 |
| Llama3-8B-Instruct | 1 | AgentPrune | 71.02 |
| Llama3-8B-Instruct | 1 | AgentDropout | 73.13 |
| Qwen2.5-72B-Instruct | 1 | Vanilla | 91.02 |
| Qwen2.5-72B-Instruct | 1 | CoT | 92.19 |
| Qwen2.5-72B-Instruct | 1 | $\text{MAS}_{round=1}$ | 93.52 |
| Qwen2.5-72B-Instruct | 1 | $\text{MAS}_{round=T}$ | 93.28 |
| Qwen2.5-72B-Instruct | 1 | AgentPrune | 93.67 |
| Qwen2.5-72B-Instruct | 1 | AgentDropout | 93.75 |
| Deepseek-V3-671B-Instruct | 1 | Vanilla | 94.68 |
| Deepseek-V3-671B-Instruct | 1 | CoT | 95.15 |
| Deepseek-V3-671B-Instruct | 1 | $\text{MAS}_{round=1}$ | 95.54 |
| Deepseek-V3-671B-Instruct | 1 | $\text{MAS}_{round=T}$ | 95.49 |
| Deepseek-V3-671B-Instruct | 1 | AgentPrune | 95.49 |
| Deepseek-V3-671B-Instruct | 1 | AgentDropout | 95.63 |
| Llama3-8B-Instruct | 1 | MAS, layered initial graph | 71.72 |
| Llama3-8B-Instruct | 1 | AgentPrune, layered initial graph | 71.09 |
| Llama3-8B-Instruct | 1 | AgentDropout, layered initial graph | 72.27 |
| Llama3-8B-Instruct | 1 | MAS, random initial graph | 70.63 |
| Llama3-8B-Instruct | 1 | AgentPrune, random initial graph | 69.61 |
| Llama3-8B-Instruct | 1 | AgentDropout, random initial graph | 72.03 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.8 | 70.86 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.6 | 71.09 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.4 | 73.36 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.2 | 73.13 |
| Llama3-8B-Instruct | 1 | MAS (ablation; edge dropout no, node dropout no) | 71.48 |
| Llama3-8B-Instruct | 1 | Random Dropout (ablation; edge dropout no, node dropout yes) | 70.53 |
| Llama3-8B-Instruct | 1 | Random Dropout (ablation; edge dropout yes, node dropout no) | 71.41 |
| Llama3-8B-Instruct | 1 | Learned Dropout (ablation; edge dropout no, node dropout yes) | 70.70 |
| Llama3-8B-Instruct | 1 | Learned Dropout (ablation; edge dropout yes, node dropout no) | 70.63 |
| Llama3-8B-Instruct | 1 | Single Learning (ablation; edge dropout yes, node dropout yes) | 72.58 |
| Llama3-8B-Instruct | 1 | AgentDropout (ablation; edge dropout yes, node dropout yes) | 73.13 |
| Llama3-8B-Instruct | 1 | AgentDropout, topology learned on GSM8K | 73.13 |
| Llama3-8B-Instruct | 1 | AgentDropout, topology learned on AQuA | 73.84 |
| Llama3-8B-Instruct | 1 | AgentDropout, topology learned on MultiArith | 71.41 |
| Llama3-8B-Instruct | 1 | AgentDropout, topology learned on SVAMP | 70.86 |
| Llama3-8B-Instruct | 1 | AgentDropout, topology learned on AgentPrune | 71.02 |
| Llama3-8B-Instruct | 1 | AgentDropout, topology learned on AgentDropout | 73.13 |

All rows: [^wangAgentDropoutDynamicAgent2025]

### [Minitron](../papers/muralidharanCompactLanguageModels2024.md): Tables 2, 3, 4

5-shot accuracy. The paper states that all evaluations in Table 2 were run by the authors. In Table 3, columns marked `*` are reported from the corresponding papers.[^muralidharanCompactLanguageModels2024]

| Model | Temp. | Method / table | Metric | Score |
|---|---|---|---|---|
| Llama-3 (8B) | not stated | Table 2 | acc | 50.3 |
| Llama-2 (6.7B) | not stated | Table 2 | acc | 14 |
| Mistral (7.3B) | not stated | Table 2 | acc | 37 |
| Gemma (8.5B) | not stated | Table 2 | acc | 50 |
| Nemotron-4 (15.6B) | not stated | Table 2 | acc | 48.5 |
| Nemotron-3 (8.5B) | not stated | Table 2 | acc | 24.0 |
| Minitron 8B (8.3B) | not stated | Table 2 | acc | 51.3 |
| Phi-2 (2.7B) | not stated | Table 3 | acc | 55 |
| Gemma (2.5B) | not stated | Table 3 | acc | 18 |
| Gemma2* (2.6B) | not stated | Table 3 | acc | 23.9 |
| Qwen2* (1.5B) | not stated | Table 3 | acc | 58.5 |
| MiniCPM* (2.7B) | not stated | Table 3 | acc | 53.8 |
| Minitron 4B (4.2B) | not stated | Table 3 | acc | 24.1 |
| Sheared LLaMa | not stated | Table 4 (4 Billion target) | acc | 23.96 |
| Minitron 4B | not stated | Table 4 (4 Billion target) | acc | 24.1 |

All rows: [^muralidharanCompactLanguageModels2024]

### [llada.cpp](../papers/wangEfficientOnDeviceDiffusion2026.md): Tables 1 and 5

Accuracy on a 200-sample subset, with Q4\_0 weight quantization. Table 1 gives correct / total and the percentage. Table 5 gives accuracy. "Ablation" rows are the LLaDA component ablation (MBSD = multi-block speculative decoding, DPPR = dual-path progressive revision).[^wangEfficientOnDeviceDiffusion2026]

| Model | Temp. | Method | Accuracy |
|---|---|---|---|
| LLaDA-8B-Instruct | 0 | Vanilla dLLM decoding (Table 1) | 78 / 200 (39.0%) |
| LLaDA-8B-Instruct | 0 | Block-wise decoding with prefix KV cache reuse (Table 1) | 65 / 200 (32.5%) |
| LLaDA-8B-Instruct | 0 | LLaDA CPU (Table 5) | 39.0 |
| LLaDA-8B-Instruct | 0 | LLaDA llada.cpp (Table 5) | 43.5 |
| Llama-3-8B-Instruct | 0 | Llama CPU (Table 5) | 30.0 |
| Llama-3-8B-Instruct | 0 | Llama NPU (Table 5) | 31.0 |
| LLaDA-8B-Instruct | 0 | Ablation: CPU (Table 5) | 39.0 |
| LLaDA-8B-Instruct | 0 | Ablation: NPU (Table 5) | 41.5 |
| LLaDA-8B-Instruct | 0 | Ablation: NPU + MBSD (Table 5) | 37.5 |
| LLaDA-8B-Instruct | 0 | Ablation: NPU + MBSD + DPPR (Table 5) | 43.5 |

All rows: [^wangEfficientOnDeviceDiffusion2026]

### [Sheared-LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md): coding and math (Table 13)

Sheared-LLaMA-2.7B is pruned from LLaMA2-7B. "Source" and "Scaling" are the two reference-loss choices for dynamic batch loading.[^xiaShearedLLaMAAccelerating2024]

| Model | Temp. | Method | Metric | Score |
|---|---|---|---|---|
| LLaMA2-7B | not stated | 8-shot | EM | 13.7 |
| OPT-2.7B | not stated | 8-shot | EM | 0.1 |
| Pythia-2.8B | not stated | 8-shot | EM | 1.7 |
| INCITE-Base-3B | not stated | 8-shot | EM | 1.8 |
| Open-LLaMA-3B-v1 | not stated | 8-shot | EM | 2.5 |
| Open-LLaMA-3B-v2 | not stated | 8-shot | EM | 2.7 |
| Sheared-LLaMA-2.7B (Source) | not stated | 8-shot | EM | 2.7 |
| Sheared-LLaMA-2.7B (Scaling) | not stated | 8-shot | EM | 2.4 |

All rows: [^xiaShearedLLaMAAccelerating2024]


### [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md): quality and latency

With the DistillSpec pipeline over a T5 model garden, relative latency on GSM8K falls from 15.0 to 1.4, a speedup improvement of 10.7$\times$, while accuracy goes from 33.1 to 34.8.[^zhouDistillSpecImprovingSpeculative2024] A draft distilled on GSM8K also transfers: on 23 BigBenchHard tasks with zero-shot chain-of-thought prompting it raises the average speedup from 1.93$\times$ and 1.78$\times$ to 2.21$\times$ and 2.02$\times$ for greedy and non-greedy decoding.[^zhouDistillSpecImprovingSpeculative2024]

## Known issues

- Papers evaluate on different subsets: full GSM8K,[^samarinLKLossesDirect2026] 128 prompts,[^kumarSpeculativeSpeculativeDecoding2026] 1,000 randomly sampled test instances,[^weiSDFPSpeculativeDecoding2026] and a 200-sample subset.[^wangEfficientOnDeviceDiffusion2026]
- Shot counts differ between accuracy reports: 5-shot[^muralidharanCompactLanguageModels2024] and 8-shot.[^xiaShearedLLaMAAccelerating2024]
- In the SpecForge text, SpecBundle speedups on the coding and mathematics benchmarks range from 1.61× to 4.48×, while its Table 3 lists GSM8K speedups of 1.40 (Qwen-30B-A3B) and 1.59 (Llama-3.3-70B).[^liSpecForgeFlexibleEfficient2026]
- Speedups in the DPara batched table and the DFlash SGLang table fall as batch size or concurrency rises, so a speedup is tied to its batch setting.[^liuWhenParallelDrafter2026][^chenDFlashBlockDiffusion2026]

# Contradictions

### Same drafter, target, and temperature in different papers

More than one paper reports the same drafter on the same Qwen3 target and temperature with this dataset. The values are side by side below, and most of them differ.

| Target | Temp. | Method | DFlash paper[^chenDFlashBlockDiffusion2026] (speedup / $\tau$) | DSpark paper[^chengDSparkConfidenceScheduledSpeculative2026] ($\tau$) | DPara paper[^liuWhenParallelDrafter2026] (speedup / $\tau$) |
|---|---|---|---|---|---|
| Qwen3-4B | 1 | EAGLE-3 | 1.89× / 3.22 (tree size 16); 2.12× / 3.68 (tree size 60) | 5.14 | – |
| Qwen3-4B | 1 | DFlash | 4.71× / 6.00 (block size 16) | 5.40 | – |
| Qwen3-8B | 0 | EAGLE-3 | 1.94× / 3.23 (tree size 16); 2.23× / 3.71 (tree size 60) | – | 1.44× / 2.83 |
| Qwen3-8B | 0 | DFlash | 5.15× / 6.54 (block size 16) | – | 3.38× / 6.08 |
| Qwen3-8B | 1 | EAGLE-3 | 1.87× / 3.12 (tree size 16); 2.07× / 3.59 (tree size 60) | 5.30 | – |
| Qwen3-8B | 1 | DFlash | 4.67× / 5.98 (block size 16) | 5.33 | 2.71× / 5.28 |
| Qwen3-8B | 1 | DSpark | – | 6.17 | 3.06× / 6.15 |
| Qwen3-14B | 1 | DFlash | – | 5.41 | 3.29× / 5.35 |
| Qwen3-14B | 1 | DSpark | – | 6.21 | 3.74× / 6.18 |

The settings differ in ways that the papers state. The DFlash paper runs the Transformers backend on H200 GPUs with up to 2048 generated tokens, uses the EAGLE-3 checkpoints released by AngelSlim with tree drafting, and uses DFlash block size 16.[^chenDFlashBlockDiffusion2026] The DSpark paper retrains all three drafters in one framework on the same data, uses chain-based drafting with block size 7 (TTT horizon 7 for Eagle3), and reports only $\tau$.[^chengDSparkConfidenceScheduledSpeculative2026] The DPara paper uses batch size 1, draft length 7, and up to 512 new tokens on an H800 node.[^liuWhenParallelDrafter2026]

### EAGLE-3 public checkpoints in different papers

Each cell is speedup / $\tau$ for EAGLE-3 on the same target. L31 8B = LLaMA-Instruct 3.1 8B, L33 70B = LLaMA-Instruct 3.3 70B, V 13B = Vicuna 13B, DSL 8B = DeepSeek-R1-Distill-LLaMA 8B.[^liEAGLE3ScalingInference2025]

| Target | Temp. | EAGLE-3 paper[^liEAGLE3ScalingInference2025] | Learning to Draft paper[^zhangLearningDraftAdaptive2026] | LK Losses paper[^samarinLKLossesDirect2026] | DFlash paper, Table 5[^chenDFlashBlockDiffusion2026] |
|---|---|---|---|---|---|
| DSL 8B | 0 | 5.01x / 6.93 | 4.73 / 7.39 | – | – |
| L31 8B | 0 | 4.48x / 6.23 | 3.58 / 6.44 | 2.65 / 3.84 (YH-8B) | 1.6× / 3.49 (EAGLE-3 (10); temperature not stated); 1.9× / 4.55 (EAGLE-3 (60); temperature not stated) |
| L33 70B | 0 | 4.34x / 6.15 | – | 2.90 / 3.76 (YH-70B) | – |
| V 13B | 0 | 5.32x / 6.29 | 4.36 / 6.58 | – | – |
| DSL 8B | 1 | 4.38x / 6.10 | 3.97 / 6.89 | – | – |
| L31 8B | 1 | 3.32x / 4.59 | 3.43 / 5.24 | 2.14 / 3.21 (YH-8B) | – |
| L33 70B | 1 | 4.17x / 5.95 | – | 2.50 / 3.34 (YH-70B) | – |
| V 13B | 1 | 4.71x / 5.58 | 3.68 / 5.64 | – | – |

The EAGLE-3 paper measures against Huggingface.transformers and does not state the hardware for its Table 1.[^liEAGLE3ScalingInference2025] The Learning to Draft paper runs the official Eagle3 releases with verification size 60 (50 for the 13B model), draft depth 8, and 10 nodes selected during expansion.[^zhangLearningDraftAdaptive2026] The LK Losses paper runs public HuggingFace checkpoints (YH = yuhuili) with chain sampling at $K=7$ in vLLM, not tree drafting.[^samarinLKLossesDirect2026] The DFlash paper runs the official EAGLE-3 checkpoint in SGLang with 10 or 60 draft tokens and reports speedup at concurrency 1.[^chenDFlashBlockDiffusion2026]

### Accuracy of the same model in different papers

- **Sheared-LLaMA.** The Minitron paper lists "Sheared LLaMa" (2.7B parameters) at 23.96 on gsm8k with 5 shots.[^muralidharanCompactLanguageModels2024] The Sheared-LLaMA paper itself reports 2.7 (Source) and 2.4 (Scaling) exact match for Sheared-LLaMA-2.7B with 8 shots.[^xiaShearedLLaMAAccelerating2024] The shot counts differ (5 and 8), and the Minitron paper's Table 4 does not say where its Sheared LLaMa number comes from. For LLaMA-2 the two papers are close: 14 for Llama-2 (6.7B) in the Minitron paper[^muralidharanCompactLanguageModels2024] and 13.7 for LLaMA2-7B in the Sheared-LLaMA paper.[^xiaShearedLLaMAAccelerating2024]
- **Llama-3-8B-Instruct.** AgentDropout reports 70.23 for single-agent Vanilla inference with Llama3-8B-Instruct at temperature 1.[^wangAgentDropoutDynamicAgent2025] The llada.cpp paper reports 30.0 (CPU) and 31.0 (NPU) for Llama-3-8B-Instruct.[^wangEfficientOnDeviceDiffusion2026] The llada.cpp numbers come from a 200-sample subset, Q4\_0 weight quantization, and temperature 0 on a phone.[^wangEfficientOnDeviceDiffusion2026] The Minitron paper reports 50.3 for "Llama-3" (8B) with 5 shots.[^muralidharanCompactLanguageModels2024]

## Related

- Methods measured on it: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-2](../methods/eagle-2.md), [PEARL](../methods/pearl.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [DistillSpec](../methods/distillspec.md), [Multi-token prediction](../methods/multi-token-prediction.md), [Medusa](../methods/medusa.md), [Sheared-LLaMA](../methods/sheared-llama.md)
- Serving engines used for the measurements: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets evaluated alongside it: [MATH-500](math-500.md), [HumanEval](humaneval.md), [MBPP](mbpp.md), [LiveCodeBench](livecodebench.md), [MT-Bench](mt-bench.md), [Alpaca](alpaca.md), [CNN/Daily Mail](cnn-dailymail.md), [MMLU](mmlu.md), [HellaSwag](hellaswag.md)
- Prompt streams that sample from it: [Spider](spider.md) and [chatbot_instruction_prompts](chatbot-instruction-prompts.md) share the Aurora request stream.
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md)

## Open questions and results

- [What is the GSM8K score of Sheared-LLaMA 2.7B?](../questions/sheared-llama-gsm8k-discrepancy.md)
- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)

[^wangWhenRLMeets2026]: Wang et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^wangAgentDropoutDynamicAgent2025]: Wang et al. 2025
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
