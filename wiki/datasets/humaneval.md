---
type: Dataset
title: HumanEval
description: Code generation benchmark that the wiki's papers use as a coding prompt set for speculative-decoding speed measurements and as a pass@1 accuracy test.
tags: [code-generation, speculative-decoding, evaluation]
sources:
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
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
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: wangAgentDropoutDynamicAgent2025
    resource: zotero://select/items/@wangAgentDropoutDynamicAgent2025
    title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
---

# HumanEval

## Overview

HumanEval measures function body generation accuracy given natural language descriptions.[^shinnReflexionLanguageAgents2023] The papers in this wiki use it in two different ways. Speculative-decoding papers use its prompts as the code-generation workload for measuring speedup and acceptance length.[^liEAGLE3ScalingInference2025][^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^liSpecForgeFlexibleEfficient2026][^samarinLKLossesDirect2026][^kumarSpeculativeSpeculativeDecoding2026] Other papers report task accuracy on it, mostly as pass@1.[^shinnReflexionLanguageAgents2023][^muralidharanCompactLanguageModels2024][^xiaShearedLLaMAAccelerating2024][^wangAgentDropoutDynamicAgent2025] One paper uses it as training data for decoding policies.[^zhangLearningDraftAdaptive2026]

## Composition

- The Minitron paper uses it for Python code generation.[^muralidharanCompactLanguageModels2024]
- Reflexion translates a subset to Rust with MultiPL-E. Its HumanEval (RS) set is the hardest 50 problems from HumanEval Python translated to Rust.[^shinnReflexionLanguageAgents2023]
- The Learning to Draft paper states that, taking the Llama model as an example, HumanEval contains approximately 27829 new tokens of ground truth.[^zhangLearningDraftAdaptive2026]
- The Minitron paper labels its row "humaneval (n=20)".[^muralidharanCompactLanguageModels2024]
- The papers do not state the number of problems in the full dataset.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | Code-generation task for speedup and $\tau$ | Vicuna 13B, LLaMA-Instruct 3.1 8B and 3.3 70B, DeepSeek-R1-Distill-LLaMA 8B; temperature 0 and 1 | EAGLE-3 on Vicuna 13B at temperature 0: 6.47x, $\tau$ 7.54[^liEAGLE3ScalingInference2025] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Code prompt set for speedup, $\tau$, and serving throughput | Qwen3 on Transformers, SGLang, and vLLM; LLaMA-3.1-8B-Instruct on SGLang | DFlash (16) on Q3-4B at temperature 0: 5.21×, $\tau$ 6.64[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | Code prompt set for accepted length | Qwen3-4B, 8B, 14B, Gemma4-12B; temperature 1.0 | DSpark $\tau$ from 5.38 to 5.64 across the four targets[^chengDSparkConfidenceScheduledSpeculative2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | Coding prompt set for speedup, $\tau$, and batched throughput | Qwen3-8B and 14B; greedy and temperature 1.0 | DPara on Qwen3-8B, greedy: 3.50×, $\tau$ 4.78[^liuWhenParallelDrafter2026] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | Coding prompt set for serving throughput with EAGLE3 draft models | Seven targets on SGLang | SpecBundle speedup from 1.83 to 3.08[^liSpecForgeFlexibleEfficient2026] |
| [LK Losses](../papers/samarinLKLossesDirect2026.md) | Evaluation prompts for $\tau$ and speedup under chain sampling | Six targets; temperature 0 and 1 | Llama 3.3 70B EAGLE-3 with the LK loss at $T=0$: $\tau$ 5.21, speedup 3.87[^samarinLKLossesDirect2026] |
| [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md) | 128 prompts, 512 decoding tokens each | Llama-3.1-70B/1B and Qwen3-32B/0.6B, greedy | SSD on Llama-3.1 70B/1B: 283 tok/s, 5.17× over AR[^kumarSpeculativeSpeculativeDecoding2026] |
| [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md) | Training set for the depth and size policies, and the set on which the grid-search baseline is tuned | Eagle3 drafts for five targets | No HumanEval speedup is reported[^zhangLearningDraftAdaptive2026] |
| [Reflexion](../papers/shinnReflexionLanguageAgents2023.md) | Pass@1 accuracy, Python and Rust | GPT-4 baseline and Reflexion | Reflexion 91.0 on HumanEval (PY) against 80.1 for GPT-4[^shinnReflexionLanguageAgents2023] |
| [Minitron](../papers/muralidharanCompactLanguageModels2024.md) | Zero-shot pass@1 of pruned and baseline models | Minitron 8B and 4B and baselines; temperature 0.2, top-p 0.95 | Minitron 8B 31.6, Minitron 4B 23.3[^muralidharanCompactLanguageModels2024] |
| [Sheared-LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) | Pass@1 and Pass@5 | Sheared-LLaMA-2.7B and 3B-class baselines | Sheared-LLaMA-2.7B (Scaling): 4.9 Pass@1, 9.2 Pass@5[^xiaShearedLLaMAAccelerating2024] |
| [AgentDropout](../papers/wangAgentDropoutDynamicAgent2025.md) | Code-generation score of multi-agent systems | Llama3-8B-Instruct, Qwen2.5-72B-Instruct, Deepseek-V3-671B-Instruct; temperature 1 | AgentDropout: 55.84, 87.92, 91.74[^wangAgentDropoutDynamicAgent2025] |

## Speed metrics

Speculative-decoding speedup, acceptance length, and throughput measured with this dataset's prompts. These numbers say nothing about task accuracy. Each subsection is one paper and one setting, and rows from different subsections are not comparable.

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): Table 1

Speedup over vanilla autoregressive decoding and average acceptance length $\tau$. V = Vicuna, L31 = LLaMA-Instruct 3.1, L33 = LLaMA-Instruct 3.3, DSL = DeepSeek-R1-Distill-LLaMA. SpS is standard speculative sampling with Vicuna-68M as the draft model. The baseline (1.00x) is Huggingface.transformers with the PyTorch backend and a pre-allocated KV cache.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| V 13B | 0 | SpS | 2.23x | 2.57 |
| V 13B | 0 | PLD | 1.85x | 1.93 |
| V 13B | 0 | Medusa | 2.50x | 2.78 |
| V 13B | 0 | Lookahead | 1.71x | 1.75 |
| V 13B | 0 | Hydra | 3.28x | 3.87 |
| V 13B | 0 | EAGLE | 3.58x | 4.39 |
| V 13B | 0 | EAGLE-2 | 4.96x | 5.41 |
| V 13B | 0 | EAGLE-3 | 6.47x | 7.54 |
| L31 8B | 0 | EAGLE-2 | 3.66x | 4.71 |
| L31 8B | 0 | EAGLE-3 | 4.85x | 6.74 |
| L33 70B | 0 | EAGLE-2 | 3.12x | 4.09 |
| L33 70B | 0 | EAGLE-3 | 4.79x | 6.52 |
| DSL 8B | 0 | EAGLE-2 | 3.42x | 4.29 |
| DSL 8B | 0 | EAGLE-3 | 4.59x | 6.38 |
| V 13B | 1 | SpS | 1.72x | 1.97 |
| V 13B | 1 | EAGLE | 2.65x | 3.63 |
| V 13B | 1 | EAGLE-2 | 4.22x | 4.89 |
| V 13B | 1 | EAGLE-3 | 5.15x | 6.22 |
| L31 8B | 1 | EAGLE-2 | 3.39x | 4.39 |
| L31 8B | 1 | EAGLE-3 | 4.13x | 5.82 |
| L33 70B | 1 | EAGLE-2 | 2.89x | 3.81 |
| L33 70B | 1 | EAGLE-3 | 4.36x | 6.16 |
| DSL 8B | 1 | EAGLE-2 | 3.01x | 3.82 |
| DSL 8B | 1 | EAGLE-3 | 3.77x | 5.28 |

All rows: [^liEAGLE3ScalingInference2025]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): Table 1, Transformers backend

Qwen3 (Q3) targets with thinking mode disabled, maximum of 2048 generated tokens. Speedup is end-to-end over the autoregressive baseline. The number in parentheses is the draft tree size for EAGLE-3 and the block size for DFlash. EAGLE-3 uses 7 draft steps and top-$k$ 10, with the checkpoints released by AngelSlim.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Q3-4B | 0 | EAGLE-3 (16) | 1.84× | 3.05 |
| Q3-4B | 0 | EAGLE-3 (60) | 2.12× | 3.47 |
| Q3-4B | 0 | DFlash (16) | 5.21× | 6.64 |
| Q3-8B | 0 | EAGLE-3 (16) | 1.89× | 3.17 |
| Q3-8B | 0 | EAGLE-3 (60) | 2.17× | 3.65 |
| Q3-8B | 0 | DFlash (16) | 5.14× | 6.50 |
| Q3-4B | 1 | EAGLE-3 (16) | 1.74× | 3.01 |
| Q3-4B | 1 | EAGLE-3 (60) | 1.94× | 3.39 |
| Q3-4B | 1 | DFlash (16) | 4.74× | 6.04 |
| Q3-8B | 1 | EAGLE-3 (16) | 1.75× | 3.05 |
| Q3-8B | 1 | EAGLE-3 (60) | 2.05× | 3.54 |
| Q3-8B | 1 | DFlash (16) | 4.32× | 5.52 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): serving on SGLang (Table 3)

Single B200 GPU, FA4 backend, Spec-v2 scheduling overlap enabled. Cells are throughput in tok/s at each concurrency level, with the DFlash speedup over the baseline in parentheses.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| Qwen3-4B | not stated | Baseline | 312 | 1162 | 2217 | 4184 | 7143 | – |
| Qwen3-4B | not stated | DFlash | 1247 (4.0×) | 4147 (3.6×) | 6997 (3.2×) | 11234 (2.7×) | 15703 (2.2×) | 6.63 |
| Qwen3-8B | not stated | Baseline | 229 | 868 | 1649 | 3253 | 5462 | – |
| Qwen3-8B | not stated | DFlash | 955 (4.2×) | 3092 (3.6×) | 6010 (3.6×) | 9919 (3.0×) | 13116 (2.4×) | 6.50 |
| Qwen3-Coder-30B-A3B | not stated | Baseline | 229 | 686 | 1068 | 1681 | 2713 | – |
| Qwen3-Coder-30B-A3B | not stated | DFlash | 802 (3.5×) | 2078 (3.0×) | 3442 (3.2×) | 5429 (3.2×) | 8314 (3.1×) | 8.09 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): same training data as EAGLE-3, SGLang (Table 5)

DFlash is trained on UltraChat and ShareGPT and compared with the official EAGLE-3 checkpoints. SGLang with Spec-v1 (without scheduling overlap), Flashinfer backend, single B200 GPU. EAGLE-3 uses 7 draft steps with top-$k{=}10$ and either 10 or 60 draft tokens. DFlash uses block size 10. The baseline row is absolute throughput in tokens/s. The other rows are speedup over the baseline at each concurrency level.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| LLaMA-3.1-8B-Instruct | not stated | Baseline (TPS) | 245 | 922 | 1778 | 3336 | 5854 | – |
| LLaMA-3.1-8B-Instruct | not stated | EAGLE-3 (10) | 2.0× | 1.9× | 1.8× | 1.5× | 1.2× | 3.62 |
| LLaMA-3.1-8B-Instruct | not stated | EAGLE-3 (60) | 2.0× | 1.7× | 1.3× | 0.9× | 0.6× | 4.65 |
| LLaMA-3.1-8B-Instruct | not stated | DFlash (10) | 2.8× | 2.6× | 2.5× | 2.1× | 1.8× | 4.91 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): more models on SGLang (Table 11)

One B200, concurrency 8. Speedup is over autoregressive decoding. MTP is the model's native MTP.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3.5-4B | not stated | MTP | 1.6× | 6.3 |
| Qwen3.5-4B | not stated | DFlash | 2.9× | 7.3 |
| Qwen3.5-9B | not stated | MTP | 1.7× | 6.6 |
| Qwen3.5-9B | not stated | DFlash | 3.4× | 7.9 |
| Qwen3.5-35B-A3B | not stated | MTP | 1.6× | 7.1 |
| Qwen3.5-35B-A3B | not stated | DFlash | 2.3× | 7.9 |
| Qwen3.5-27B | not stated | DFlash | 3.9× | 9.1 |
| Qwen3-Coder-Next | not stated | DFlash | 1.9× | 7.2 |
| GPT-OSS-20B | not stated | DFlash | 2.2× | 4.3 |
| GPT-OSS-120B | not stated | DFlash | 1.7× | 4.4 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): vLLM (Table 12)

DFlash throughput and speedup over autoregressive decoding at each concurrency level.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Concurrency | Throughput (tok/s) | Speedup |
|---|---|---|---|---|---|
| Qwen3.5-9B | not stated | DFlash | 1 | 969 | 4.6× |
| Qwen3.5-9B | not stated | DFlash | 8 | 5434 | 3.4× |
| Qwen3.5-9B | not stated | DFlash | 16 | 8131 | 2.7× |
| Qwen3.5-9B | not stated | DFlash | 32 | 10258 | 2.1× |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): drafter ablations (Tables 6, 7, 8, 13)

Ablation drafters are trained on 100K samples and run on a single H200 GPU with greedy decoding. The wiki's Paper page does not record the target model of these tables.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 3-L | 3.90× | 4.61 |
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 5-L | 3.96× | 4.94 |
| not stated | 0 | Draft layers (block size 16, 5 target features; Table 6) 8-L | 3.96× | 5.29 |
| not stated | 0 | Target hidden features (3 draft layers, block size 16; Table 7) 3-H | 3.80× | 4.47 |
| not stated | 0 | Target hidden features (3 draft layers, block size 16; Table 7) 5-H | 3.90× | 4.61 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b16 → b16 | 3.96x | 5.29 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b16 → b8 | 3.39x | 4.44 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b8 → b16 | 3.24x | 4.28 |
| not stated | 0 | Train BS → test BS (8 layers, 5 features; Table 8) b8 → b8 | 3.53x | 4.61 |
| not stated | 0 | Masked-block construction (3 layers, 5 features, block size 16; Table 13) Standard | 3.29x | 3.86 |
| not stated | 0 | Masked-block construction (3 layers, 5 features, block size 16; Table 13) Sample (random anchors) | 3.90x | 4.61 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): KV injection vs input fusion (Table 9)

5-layer draft models, draft block size 8. The ablation section states greedy decoding on a single H200 GPU.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-4B | 0 | EAGLE-3-5L, Input injection, autoregressive drafting | 2.2× | 4.3 |
| Qwen3-4B | 0 | DFlash-AR, KV injection, autoregressive drafting | 2.3× | 4.6 |
| Qwen3-4B | 0 | DFlash, Input injection, block diffusion drafting | 2.9× | 3.5 |
| Qwen3-4B | 0 | DFlash, KV injection, block diffusion drafting | 3.2× | 4.0 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): accepted length (Table 1)

Accepted length $\tau$ per decoding round, including the bonus token. Standard speculative decoding with chain-based drafting. All three drafters are retrained in the same framework on the same data, with block size 7 for DFlash and DSpark and TTT horizon 7 for Eagle3. Eagle3 has 1 draft layer, DSpark and DFlash have 5. The confidence scheduler is disabled. No speedup is reported for this table.[^chengDSparkConfidenceScheduledSpeculative2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Qwen3-4B | 1.0 | Eagle3 | 4.16 |
| Qwen3-4B | 1.0 | DFlash | 4.74 |
| Qwen3-4B | 1.0 | DSpark | 5.38 |
| Qwen3-8B | 1.0 | Eagle3 | 4.33 |
| Qwen3-8B | 1.0 | DFlash | 4.64 |
| Qwen3-8B | 1.0 | DSpark | 5.52 |
| Qwen3-14B | 1.0 | Eagle3 | 4.14 |
| Qwen3-14B | 1.0 | DFlash | 4.59 |
| Qwen3-14B | 1.0 | DSpark | 5.43 |
| Gemma4-12B | 1.0 | Eagle3 | 5.37 |
| Gemma4-12B | 1.0 | DFlash | 4.95 |
| Gemma4-12B | 1.0 | DSpark | 5.64 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): Tables 1 and 3

Batch size 1, up to 512 new tokens, draft length 7, speedup over AR. Temperature 0 rows are greedy decoding (Table 1). Temperature 1.0 rows use temperature 1.0 for both the target and the drafter (Table 3). SSD-E3 uses the EAGLE3 weight of the target as draft model. SSD, SD, and PEARL on Qwen3-14B use Qwen3-0.6B as draft model. The parallel methods (PEARL, SSD, DPara) use one additional GPU for drafting.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-8B | 0 | SSD-E3 | 1.72× | 2.75 |
| Qwen3-8B | 0 | EAGLE3 | 1.67× | 3.26 |
| Qwen3-8B | 0 | DFlash | 2.93× | 5.25 |
| Qwen3-8B | 0 | DSpark | 3.15× | 5.82 |
| Qwen3-8B | 0 | DPara | 3.50× | 4.78 |
| Qwen3-14B | 0 | SSD | 2.36× | 4.87 |
| Qwen3-14B | 0 | SSD-E3 | 2.02× | 2.80 |
| Qwen3-14B | 0 | PEARL | 2.95× | 3.18 |
| Qwen3-14B | 0 | SD | 1.99× | 4.86 |
| Qwen3-14B | 0 | EAGLE3 | 2.01× | 3.35 |
| Qwen3-14B | 0 | DFlash | 3.36× | 5.20 |
| Qwen3-14B | 0 | DSpark | 3.66× | 5.79 |
| Qwen3-14B | 0 | DPara | 3.84× | 4.76 |
| Qwen3-8B | 1.0 | DFlash | 2.39× | 4.64 |
| Qwen3-8B | 1.0 | DSpark | 2.78× | 5.53 |
| Qwen3-8B | 1.0 | DPara | 2.95× | 4.46 |
| Qwen3-14B | 1.0 | DFlash | 2.86× | 4.61 |
| Qwen3-14B | 1.0 | DSpark | 3.33× | 5.46 |
| Qwen3-14B | 1.0 | DPara | 3.38× | 4.39 |

All rows: [^liuWhenParallelDrafter2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): batched inference (Table 2)

Throughput in tok/s at each batch size, with speedup over AR in parentheses.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | b=1 | b=2 | b=4 | b=8 | b=16 |
|---|---|---|---|---|---|---|---|
| Qwen3-8B | not stated | AR | 141 | 269 | 532 | 957 | 1684 |
| Qwen3-8B | not stated | DSpark | 445 (3.15×) | 815 (3.02×) | 1464 (2.75×) | 2283 (2.39×) | 3382 (2.01×) |
| Qwen3-8B | not stated | DPara | 495 (3.50×) | 914 (3.39×) | 1565 (2.94×) | 2567 (2.68×) | 3654 (2.17×) |
| Qwen3-14B | not stated | AR | 87 | 170 | 333 | 622 | 1080 |
| Qwen3-14B | not stated | DSpark | 319 (3.66×) | 598 (3.52×) | 1082 (3.25×) | 1688 (2.71×) | 2523 (2.34×) |
| Qwen3-14B | not stated | DPara | 335 (3.84×) | 634 (3.74×) | 1140 (3.42×) | 1824 (2.93×) | 2724 (2.52×) |

All rows: [^liuWhenParallelDrafter2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): backbone finetuning ablation

DPara with the same frozen AR head, comparing the original DSpark checkpoint with the finetuned M-DFlash backbone.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | $\tau$ with original DSpark checkpoint | $\tau$ with M-DFlash | Relative gain |
|---|---|---|---|---|---|
| Qwen3-8B | not stated | DPara | 3.81 | 4.78 | 25.5% |

All rows: [^liuWhenParallelDrafter2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): SpecBundle inference (Table 3)

SGLang on NVIDIA H200 GPUs, 8 concurrent requests for LLaMA-3.1-8B and 16 for larger models. The highest throughput among five (speculative steps, top-k, draft tokens) configurations is reported. Existing draft models come from the EAGLE3 authors or the LMSYS team. The tables do not state the unit of the throughput column.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | #GPUs | Throughput | Speedup |
|---|---|---|---|---|---|
| Llama-3.1-8B | not stated | none (target model alone) | 1 | 190.9 | 1 |
| Llama-3.1-8B | not stated | EAGLE3, existing open-source draft model | 1 | 480.3 | 2.52 |
| Llama-3.1-8B | not stated | EAGLE3, SpecBundle draft model | 1 | 571.5 | 2.99 |
| Llama-3.3-70B | not stated | none (target model alone) | 4 | 561.0 | 1 |
| Llama-3.3-70B | not stated | EAGLE3, existing open-source draft model | 4 | 1282.8 | 2.29 |
| Llama-3.3-70B | not stated | EAGLE3, SpecBundle draft model | 4 | 1506.0 | 2.68 |
| Llama-4-Scout | not stated | none (target model alone) | 8 | 631.9 | 1 |
| Llama-4-Scout | not stated | EAGLE3, existing open-source draft model | 8 | 1556.5 | 2.46 |
| Llama-4-Scout | not stated | EAGLE3, SpecBundle draft model | 8 | 1944.8 | 3.08 |
| Qwen-30B-A3B | not stated | none (target model alone) | 4 | 1366.6 | 1 |
| Qwen-30B-A3B | not stated | EAGLE3, SpecBundle draft model | 4 | 3070.0 | 2.25 |
| Qwen-235B-A22B | not stated | none (target model alone) | 8 | 553.1 | 1 |
| Qwen-235B-A22B | not stated | EAGLE3, existing open-source draft model | 8 | 889.9 | 1.61 |
| Qwen-235B-A22B | not stated | EAGLE3, SpecBundle draft model | 8 | 1267.5 | 2.29 |
| Ling-Flash-V2 | not stated | none (target model alone) | 8 | 740.2 | 1 |
| Ling-Flash-V2 | not stated | EAGLE3, SpecBundle draft model | 8 | 1359.0 | 1.83 |
| Kimi-K2 | not stated | none (target model alone) | 8 | 466.1 | 1 |
| Kimi-K2 | not stated | EAGLE3, SpecBundle draft model | 8 | 897.9 | 1.93 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): MoE draft models (Table 4)

The table is captioned "Acceptance rate of MoE models with different settings", with MoE top-k = 1, EAGLE3 number of steps = 3, EAGLE3 top-k = 1, and EAGLE3 number of draft tokens = 4.[^liSpecForgeFlexibleEfficient2026]

| Model | Temp. | Method | Acceptance |
|---|---|---|---|
| not stated | not stated | MoE draft, Same Params, 2 experts | 1.2 |
| not stated | not stated | MoE draft, Same FLOPS, 2 experts | 1.64 |
| not stated | not stated | MoE draft, Same FLOPS, 3 experts | 1.67 |
| not stated | not stated | MoE draft, Same FLOPS, 4 experts | 1.69 |
| not stated | not stated | MoE draft, With Shared Experts, 2 experts | 1.53 |
| not stated | not stated | MoE draft, With Shared Experts, 3 experts | 1.53 |
| not stated | not stated | MoE draft, With Shared Experts, 4 experts | 1.64 |
| not stated | not stated | Dense Draft Model | 3.34 |

All rows: [^liSpecForgeFlexibleEfficient2026]

### [LK Losses](../papers/samarinLKLossesDirect2026.md): Table 4

Chain sampling in vLLM v0.11.0, batch size 1, speedup relative to decoding without speculative decoding. $\tau$ includes the bonus token. EAGLE-3 and DeepSeek-MTP drafts are evaluated with $K=7$. "Trained with" rows are the paper's own drafts trained with the named loss. Public checkpoints are HuggingFace checkpoints run through the same pipeline (RH = RedHatAI, YH = yuhuili, ZK = zhuyksir, DS = deepseek-ai).[^samarinLKLossesDirect2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with KL | 3.30 | 4.82 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with TV | 2.39 | 3.42 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.28 | 4.82 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}$, $\lambda=0.5$ | 3.32 | 4.84 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=0.7$ | 3.31 | 4.88 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=1$ | 3.33 | 4.83 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.35 | 4.89 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=10$ | 3.33 | 4.85 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint RH-8B | 2.65 | 3.90 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint YH-8B | 3.07 | 4.37 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 0 | public checkpoint ZK-8B | 3.08 | 4.49 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with KL | 3.87 | 5.18 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.82 | 5.12 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.87 | 5.21 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | public checkpoint RH-70B | 2.99 | 3.99 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 0 | public checkpoint YH-70B | 3.12 | 3.96 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with KL | 1.32 | 3.08 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.32 | 3.07 |
| GPT-OSS 20B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.34 | 3.11 |
| GPT-OSS 20B (EAGLE-3) | 0 | public checkpoint RH-20B† | 1.17 | 2.70 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with KL | 1.54 | 2.47 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.57 | 2.51 |
| GPT-OSS 120B (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.60 | 2.51 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with KL | 2.73 | 4.65 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.77 | 4.68 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.78 | 4.74 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | public checkpoint RH-235B | 2.42 | 4.06 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 0 | public checkpoint ZK-235B‡ | 2.70 | 4.54 |
| DeepSeek V3 0324 (MTP) | 0 | trained with KL | 2.62 | 4.74 |
| DeepSeek V3 0324 (MTP) | 0 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$ | 2.64 | 4.77 |
| DeepSeek V3 0324 (MTP) | 0 | public checkpoint DS-685B | 1.84 | 3.28 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with KL | 3.00 | 4.31 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with TV | 2.26 | 3.25 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.03 | 4.48 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}$, $\lambda=0.5$ | 3.03 | 4.36 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=0.7$ | 2.98 | 4.45 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=1$ | 3.01 | 4.47 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.08 | 4.52 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=10$ | 3.01 | 4.51 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint RH-8B | 2.31 | 3.36 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint YH-8B | 2.50 | 3.75 |
| LLaMA 3.1 8B Instruct (EAGLE-3) | 1 | public checkpoint ZK-8B | 2.82 | 3.96 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with KL | 3.66 | 4.86 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.71 | 4.94 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.77 | 5.08 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | public checkpoint RH-70B | 2.69 | 3.62 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | 1 | public checkpoint YH-70B | 2.63 | 3.49 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with KL | 1.20 | 2.89 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.25 | 2.97 |
| GPT-OSS 20B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.26 | 3.01 |
| GPT-OSS 20B (EAGLE-3) | 1 | public checkpoint RH-20B† | 1.04 | 2.43 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with KL | 1.19 | 2.27 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 1.45 | 2.39 |
| GPT-OSS 120B (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 1.48 | 2.44 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with KL | 2.37 | 4.09 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.46 | 4.31 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.52 | 4.42 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | public checkpoint RH-235B | 2.06 | 3.52 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | 1 | public checkpoint ZK-235B‡ | 2.36 | 4.03 |
| DeepSeek V3 0324 (MTP) | 1 | trained with KL | 2.17 | 4.39 |
| DeepSeek V3 0324 (MTP) | 1 | trained with $\mathcal{L}_{\text{LK}}^{\lambda}$ | 2.42 | 4.64 |
| DeepSeek V3 0324 (MTP) | 1 | public checkpoint DS-685B | 1.59 | 3.17 |

All rows: [^samarinLKLossesDirect2026]

### [LK Losses](../papers/samarinLKLossesDirect2026.md): MEDUSA and MLP speculator drafts (Table 1)

Average acceptance length only, evaluated with $K=6$.[^samarinLKLossesDirect2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Llama-3.1-8B-Instruct | 0 | MEDUSA KL | 2.41 |
| Llama-3.1-8B-Instruct | 0 | MEDUSA $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.42 |
| Llama-3.1-8B-Instruct | 0 | MEDUSA $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 2.44 |
| Llama-3.1-8B-Instruct | 0 | MLP KL | 2.42 |
| Llama-3.1-8B-Instruct | 0 | MLP $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.46 |
| Llama-3.1-8B-Instruct | 0 | MLP $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 2.83 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA KL | 2.02 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.09 |
| Llama-3.1-8B-Instruct | 1 | MEDUSA $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 2.22 |
| Llama-3.1-8B-Instruct | 1 | MLP KL | 2.16 |
| Llama-3.1-8B-Instruct | 1 | MLP $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.19 |
| Llama-3.1-8B-Instruct | 1 | MLP $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 2.62 |

All rows: [^samarinLKLossesDirect2026]

### [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md): end-to-end decoding speed (Appendix B.3)

The paper's own AR, SD, and SSD implementations. Batch size 1, greedy decoding, target on 4×H100, SSD draft on a separate H100. 128 prompts from the dataset, 512 decoding tokens each, decoding throughput excluding prefill. Temperature 0 is the paper's stated default of greedy decoding. Its appendix also says it uses vanilla sampling (not top-p or top-k). The Model column is target/draft.[^kumarSpeculativeSpeculativeDecoding2026]

| Model | Temp. | Method | Decode tok/s | Speedup over SD | Speedup over AR |
|---|---|---|---|---|---|
| Llama-3.1-Instruct 70B/1B | 0 | AR | 54.7 | – | – |
| Llama-3.1-Instruct 70B/1B | 0 | SD | 176 | – | – |
| Llama-3.1-Instruct 70B/1B | 0 | SSD | 283 | 1.60× | 5.17× |
| Qwen-3 32B/0.6B | 0 | AR | 88.8 | – | – |
| Qwen-3 32B/0.6B | 0 | SD | 146 | – | – |
| Qwen-3 32B/0.6B | 0 | SSD | 222 | 1.52× | 2.50× |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]


### [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md): policy training

The depth and size policies are trained on HumanEval with PPO, 100k steps for the size policy and 1M steps for the depth policy.[^zhangLearningDraftAdaptive2026] The grid-search baseline searches Eagle3 draft depths from 4 to 12 and verification sizes from 40 to 240 on HumanEval.[^zhangLearningDraftAdaptive2026] The paper then evaluates on other datasets, so it reports no HumanEval speedup.[^zhangLearningDraftAdaptive2026]

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) and [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): observations

- EAGLE-3 performs best on HumanEval among its five tasks, which its authors attribute to the many fixed templates in code generation. DeepSeek-R1-Distill-LLaMA 8B is an exception.[^liEAGLE3ScalingInference2025]
- In SpecForge's TTT-length sweep on Llama3.1-8B, a TTT length of approximately 13 gives the best acceptance length on HumanEval.[^liSpecForgeFlexibleEfficient2026]

## Task accuracy

Scores on the dataset's own task. These are kept apart from the speed metrics above.

### [AgentDropout](../papers/wangAgentDropoutDynamicAgent2025.md): Tables 1, 3, 4, 5

The source does not name the metric unit and calls the gains "accuracy". Temperature 1. Methods are single-agent (Vanilla, CoT) and multi-agent systems (MAS, AgentPrune, AgentDropout). The main rows start from a fully connected intra-round graph. Rows after the first 18 are Llama3 ablations.[^wangAgentDropoutDynamicAgent2025]

| Model | Temp. | Method | Score |
|---|---|---|---|
| Llama3-8B-Instruct | 1 | Vanilla | 53.33 |
| Llama3-8B-Instruct | 1 | CoT | 54.17 |
| Llama3-8B-Instruct | 1 | $\text{MAS}_{round=1}$ | 48.33 |
| Llama3-8B-Instruct | 1 | $\text{MAS}_{round=T}$ | 49.17 |
| Llama3-8B-Instruct | 1 | AgentPrune | 51.67 |
| Llama3-8B-Instruct | 1 | AgentDropout | 55.84 |
| Qwen2.5-72B-Instruct | 1 | Vanilla | 85.28 |
| Qwen2.5-72B-Instruct | 1 | CoT | 86.67 |
| Qwen2.5-72B-Instruct | 1 | $\text{MAS}_{round=1}$ | 84.17 |
| Qwen2.5-72B-Instruct | 1 | $\text{MAS}_{round=T}$ | 87.08 |
| Qwen2.5-72B-Instruct | 1 | AgentPrune | 86.67 |
| Qwen2.5-72B-Instruct | 1 | AgentDropout | 87.92 |
| Deepseek-V3-671B-Instruct | 1 | Vanilla | 88.43 |
| Deepseek-V3-671B-Instruct | 1 | CoT | 89.26 |
| Deepseek-V3-671B-Instruct | 1 | $\text{MAS}_{round=1}$ | 89.17 |
| Deepseek-V3-671B-Instruct | 1 | $\text{MAS}_{round=T}$ | 89.26 |
| Deepseek-V3-671B-Instruct | 1 | AgentPrune | 90.91 |
| Deepseek-V3-671B-Instruct | 1 | AgentDropout | 91.74 |
| Llama3-8B-Instruct | 1 | MAS, layered initial graph | 52.89 |
| Llama3-8B-Instruct | 1 | AgentPrune, layered initial graph | 56.20 |
| Llama3-8B-Instruct | 1 | AgentDropout, layered initial graph | 57.02 |
| Llama3-8B-Instruct | 1 | MAS, random initial graph | 50.41 |
| Llama3-8B-Instruct | 1 | AgentPrune, random initial graph | 51.24 |
| Llama3-8B-Instruct | 1 | AgentDropout, random initial graph | 53.72 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.8 | 52.89 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.6 | 50.41 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.4 | 52.07 |
| Llama3-8B-Instruct | 1 | AgentDropout, dropout rate 0.2 | 55.84 |
| Llama3-8B-Instruct | 1 | MAS (ablation; edge dropout no, node dropout no) | 49.17 |
| Llama3-8B-Instruct | 1 | Random Dropout (ablation; edge dropout no, node dropout yes) | 52.89 |
| Llama3-8B-Instruct | 1 | Random Dropout (ablation; edge dropout yes, node dropout no) | 51.23 |
| Llama3-8B-Instruct | 1 | Learned Dropout (ablation; edge dropout no, node dropout yes) | 50.83 |
| Llama3-8B-Instruct | 1 | Learned Dropout (ablation; edge dropout yes, node dropout no) | 48.76 |
| Llama3-8B-Instruct | 1 | Single Learning (ablation; edge dropout yes, node dropout yes) | 48.73 |
| Llama3-8B-Instruct | 1 | AgentDropout (ablation; edge dropout yes, node dropout yes) | 55.84 |

All rows: [^wangAgentDropoutDynamicAgent2025]

### [Minitron](../papers/muralidharanCompactLanguageModels2024.md): Tables 2, 3, 18, 20

Zero-shot pass@1 with temperature 0.2 and top-p 0.95. The row label in the source is "humaneval (n=20) (0)". In Table 3, columns marked `*` are reported from the corresponding papers. Tables 18 and 20 are retraining ablations, and the wiki's Paper page does not restate their HumanEval metric.[^muralidharanCompactLanguageModels2024]

| Model | Temp. | Method / table | Metric | Score |
|---|---|---|---|---|
| Llama-3 (8B) | 0.2 | Table 2 | pass@1 | 28.1 |
| Llama-2 (6.7B) | 0.2 | Table 2 | pass@1 | 12 |
| Mistral (7.3B) | 0.2 | Table 2 | pass@1 | 28.7 |
| Gemma (8.5B) | 0.2 | Table 2 | pass@1 | 32 |
| Nemotron-4 (15.6B) | 0.2 | Table 2 | pass@1 | 35.4 |
| Nemotron-3 (8.5B) | 0.2 | Table 2 | pass@1 | 20.7 |
| Minitron 8B (8.3B) | 0.2 | Table 2 | pass@1 | 31.6 |
| Phi-2 (2.7B) | 0.2 | Table 3 | pass@1 | 50 |
| Gemma (2.5B) | 0.2 | Table 3 | pass@1 | 24 |
| Gemma2* (2.6B) | 0.2 | Table 3 | pass@1 | 17.7 |
| Qwen2* (1.5B) | 0.2 | Table 3 | pass@1 | 31.1 |
| Minitron 4B (4.2B) | 0.2 | Table 3 | pass@1 | 23.3 |
| Minitron 8B | 0.2 | Table 18, loss $L_{logits}+L_{is}$, 18.9B tokens | not restated | 26.8 |
| Minitron 8B | 0.2 | Table 18, loss $L_{logits}$, 18.9B tokens | not restated | 26.2 |
| Minitron 8B | 0.2 | Table 18, loss $L_{logits}$, 94B tokens | not restated | 30.4 |
| Minitron 8B-Width-pruned | 0.2 | Table 20, Phase1 + Phase2, 113B tokens | not restated | 25.6 |
| Minitron 8B-Width-pruned | 0.2 | Table 20, Phase2 only, 94B tokens | not restated | 30.5 |

All rows: [^muralidharanCompactLanguageModels2024]

### [Sheared-LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md): coding and math (Table 13)

Sheared-LLaMA-2.7B is pruned from LLaMA2-7B. "Source" and "Scaling" are the two reference-loss choices for dynamic batch loading.[^xiaShearedLLaMAAccelerating2024]

| Model | Temp. | Method | Metric | Score |
|---|---|---|---|---|
| LLaMA2-7B | not stated |  | Pass@1 | 12.8 |
| LLaMA2-7B | not stated |  | Pass@5 | 23.8 |
| OPT-2.7B | not stated |  | Pass@1 | 0.0 |
| OPT-2.7B | not stated |  | Pass@5 | 0.0 |
| Pythia-2.8B | not stated |  | Pass@1 | 5.1 |
| Pythia-2.8B | not stated |  | Pass@5 | 14.6 |
| INCITE-Base-3B | not stated |  | Pass@1 | 4.3 |
| INCITE-Base-3B | not stated |  | Pass@5 | 4.9 |
| Open-LLaMA-3B-v1 | not stated |  | Pass@1 | 0.0 |
| Open-LLaMA-3B-v1 | not stated |  | Pass@5 | 1.2 |
| Open-LLaMA-3B-v2 | not stated |  | Pass@1 | 10.4 |
| Open-LLaMA-3B-v2 | not stated |  | Pass@5 | 20.1 |
| Sheared-LLaMA-2.7B (Source) | not stated |  | Pass@1 | 3.7 |
| Sheared-LLaMA-2.7B (Source) | not stated |  | Pass@5 | 5.5 |
| Sheared-LLaMA-2.7B (Scaling) | not stated |  | Pass@1 | 4.9 |
| Sheared-LLaMA-2.7B (Scaling) | not stated |  | Pass@5 | 9.2 |

All rows: [^xiaShearedLLaMAAccelerating2024]

### [Reflexion](../papers/shinnReflexionLanguageAgents2023.md): pass@1 (Table 1)

PY is Python, RS is Rust. Rust versions are produced with MultiPL-E. The base strategy is a single code generation sample.[^shinnReflexionLanguageAgents2023]

| Model | Temp. | Method | Metric | Score |
|---|---|---|---|---|
| CodeT + GPT-3.5 | not stated | previous SOTA, HumanEval (PY) | Pass@1 | 65.8 |
| GPT-4 | not stated | single code generation sample, HumanEval (PY) | Pass@1 | 80.1 |
| not stated in the table | not stated | Reflexion, HumanEval (PY) | Pass@1 | 91.0 |
| GPT-4 | not stated | single code generation sample, HumanEval (RS) | Pass@1 | 60.0 |
| not stated in the table | not stated | Reflexion, HumanEval (RS) | Pass@1 | 68.0 |

All rows: [^shinnReflexionLanguageAgents2023]

### [Reflexion](../papers/shinnReflexionLanguageAgents2023.md): test generation quality (Table 2)

Base and Reflexion are pass@1 as fractions. TP: unit tests pass, solution pass. FN: unit tests fail, solution pass. FP: unit tests pass, solution fail. TN: unit tests fail, solution fail.[^shinnReflexionLanguageAgents2023]

| Model | Temp. | Benchmark + language | Base | Reflexion | TP | FN | FP | TN |
|---|---|---|---|---|---|---|---|---|
| not stated in the table | not stated | HumanEval (PY) | 0.80 | 0.91 | 0.99 | 0.40 | 0.01 | 0.60 |
| not stated in the table | not stated | HumanEval (RS) | 0.60 | 0.68 | 0.87 | 0.37 | 0.13 | 0.63 |

All rows: [^shinnReflexionLanguageAgents2023]

### [Reflexion](../papers/shinnReflexionLanguageAgents2023.md): ablation on HumanEval Rust (Table 3)

The 50 hardest HumanEval problems, translated to Rust.[^shinnReflexionLanguageAgents2023]

| Model | Temp. | Method | Pass@1 |
|---|---|---|---|
| GPT-4 | not stated | Base model (test generation False, self-reflection False) | 0.60 |
| GPT-4 | not stated | Test generation omission (test generation False, self-reflection True) | 0.52 |
| GPT-4 | not stated | Self-reflection omission (test generation True, self-reflection False) | 0.60 |
| GPT-4 | not stated | Reflexion (test generation True, self-reflection True) | 0.68 |

All rows: [^shinnReflexionLanguageAgents2023]


### [Reflexion](../papers/shinnReflexionLanguageAgents2023.md): weaker model

Pass@1 on HumanEval Python with starchat-beta, averaged over 8 trials, is 0.26 for the baseline and 0.26 for Reflexion.[^shinnReflexionLanguageAgents2023]

## Known issues

- Reflexion measures the false positive test execution rate at 1.4% for HumanEval Python, against 16.3% for MBPP Python.[^shinnReflexionLanguageAgents2023]
- Accuracy settings differ across papers: zero-shot pass@1 at temperature 0.2 with top-p 0.95 on a row labelled n=20,[^muralidharanCompactLanguageModels2024] pass@1 and pass@5 with no stated temperature,[^xiaShearedLLaMAAccelerating2024] and multi-agent inference at temperature 1.[^wangAgentDropoutDynamicAgent2025]
- The speed tables use different subsets and output lengths: 128 prompts with 512 decoding tokens,[^kumarSpeculativeSpeculativeDecoding2026] 80 requests per benchmark with up to 512 new tokens in the DPara sampling table,[^liuWhenParallelDrafter2026] and a maximum of 2048 generated tokens in the DFlash Transformers table.[^chenDFlashBlockDiffusion2026]

# Contradictions

### Same drafter, target, and temperature in different papers

More than one paper reports the same drafter on the same Qwen3 target and temperature with this dataset. The values are side by side below, and most of them differ.

| Target | Temp. | Method | DFlash paper[^chenDFlashBlockDiffusion2026] (speedup / $\tau$) | DSpark paper[^chengDSparkConfidenceScheduledSpeculative2026] ($\tau$) | DPara paper[^liuWhenParallelDrafter2026] (speedup / $\tau$) |
|---|---|---|---|---|---|
| Qwen3-4B | 1 | EAGLE-3 | 1.74× / 3.01 (tree size 16); 1.94× / 3.39 (tree size 60) | 4.16 | – |
| Qwen3-4B | 1 | DFlash | 4.74× / 6.04 (block size 16) | 4.74 | – |
| Qwen3-8B | 0 | EAGLE-3 | 1.89× / 3.17 (tree size 16); 2.17× / 3.65 (tree size 60) | – | 1.67× / 3.26 |
| Qwen3-8B | 0 | DFlash | 5.14× / 6.50 (block size 16) | – | 2.93× / 5.25 |
| Qwen3-8B | 1 | EAGLE-3 | 1.75× / 3.05 (tree size 16); 2.05× / 3.54 (tree size 60) | 4.33 | – |
| Qwen3-8B | 1 | DFlash | 4.32× / 5.52 (block size 16) | 4.64 | 2.39× / 4.64 |
| Qwen3-8B | 1 | DSpark | – | 5.52 | 2.78× / 5.53 |
| Qwen3-14B | 1 | DFlash | – | 4.59 | 2.86× / 4.61 |
| Qwen3-14B | 1 | DSpark | – | 5.43 | 3.33× / 5.46 |

The settings differ in ways that the papers state. The DFlash paper runs the Transformers backend on H200 GPUs with up to 2048 generated tokens, uses the EAGLE-3 checkpoints released by AngelSlim with tree drafting, and uses DFlash block size 16.[^chenDFlashBlockDiffusion2026] The DSpark paper retrains all three drafters in one framework on the same data, uses chain-based drafting with block size 7 (TTT horizon 7 for Eagle3), and reports only $\tau$.[^chengDSparkConfidenceScheduledSpeculative2026] The DPara paper uses batch size 1, draft length 7, and up to 512 new tokens on an H800 node.[^liuWhenParallelDrafter2026]

### EAGLE-3 public checkpoints in different papers

Each cell is speedup / $\tau$ for EAGLE-3 on the same target. L31 8B = LLaMA-Instruct 3.1 8B, L33 70B = LLaMA-Instruct 3.3 70B, V 13B = Vicuna 13B, DSL 8B = DeepSeek-R1-Distill-LLaMA 8B.[^liEAGLE3ScalingInference2025]

| Target | Temp. | EAGLE-3 paper[^liEAGLE3ScalingInference2025] | LK Losses paper[^samarinLKLossesDirect2026] | DFlash paper, Table 5[^chenDFlashBlockDiffusion2026] |
|---|---|---|---|---|
| L31 8B | 0 | 4.85x / 6.74 | 3.07 / 4.37 (YH-8B) | 2.0× / 3.62 (EAGLE-3 (10); temperature not stated); 2.0× / 4.65 (EAGLE-3 (60); temperature not stated) |
| L33 70B | 0 | 4.79x / 6.52 | 3.12 / 3.96 (YH-70B) | – |
| L31 8B | 1 | 4.13x / 5.82 | 2.50 / 3.75 (YH-8B) | – |
| L33 70B | 1 | 4.36x / 6.16 | 2.63 / 3.49 (YH-70B) | – |

The EAGLE-3 paper measures against Huggingface.transformers and does not state the hardware for its Table 1.[^liEAGLE3ScalingInference2025] The LK Losses paper runs public HuggingFace checkpoints (YH = yuhuili) with chain sampling at $K=7$ in vLLM, not tree drafting.[^samarinLKLossesDirect2026] The DFlash paper runs the official EAGLE-3 checkpoint in SGLang with 10 or 60 draft tokens and reports speedup at concurrency 1.[^chenDFlashBlockDiffusion2026]

### GPT-4 baseline within Reflexion

Reflexion's Table 1 gives the GPT-4 pass@1 on HumanEval Python as 80.1, and its Table 2 gives the base value as 0.80.[^shinnReflexionLanguageAgents2023] The text that discusses Table 2 gives the baseline pass@1 accuracies of HumanEval and MBPP Python as 82% and 80%.[^shinnReflexionLanguageAgents2023] The paper does not explain the difference.

## Related

- Methods measured on it: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-2](../methods/eagle-2.md), [PEARL](../methods/pearl.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [Multi-token prediction](../methods/multi-token-prediction.md), [Medusa](../methods/medusa.md), [Reflexion](../methods/reflexion.md), [Sheared-LLaMA](../methods/sheared-llama.md)
- Serving engines used for the measurements: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets evaluated alongside it: [MBPP](mbpp.md), [LiveCodeBench](livecodebench.md), [GSM8K](gsm8k.md), [MATH-500](math-500.md), [MT-Bench](mt-bench.md), [Alpaca](alpaca.md)
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md)

[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^wangAgentDropoutDynamicAgent2025]: Wang et al. 2025
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
