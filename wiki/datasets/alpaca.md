---
type: Dataset
title: Alpaca
description: Instruction-following prompt set that the wiki's speculative-decoding papers use for measuring speedup and acceptance length.
tags: [instruction-following, chat, speculative-decoding, evaluation]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
---

# Alpaca

## Overview

The papers in this wiki use Alpaca as an instruction-following or chat prompt set for measuring [speculative decoding](../methods/speculative-decoding.md) speedup and acceptance length.[^liEAGLE3ScalingInference2025][^zhangLearningDraftAdaptive2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^chenDFlashBlockDiffusion2026][^kumarSpeculativeSpeculativeDecoding2026][^gaoCollaborativeSpeculativeInference] None of them reports task accuracy on it.

## Composition

- EAGLE-3, Learning to Draft, and CoSine label it as their instruction-following task.[^liEAGLE3ScalingInference2025][^zhangLearningDraftAdaptive2026][^gaoCollaborativeSpeculativeInference] DSpark, DPara, and DFlash group it under chat.[^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^chenDFlashBlockDiffusion2026]
- The papers do not state its size. The subsets they use are 128 prompts[^kumarSpeculativeSpeculativeDecoding2026] and 80 requests in the DPara sampling table.[^liuWhenParallelDrafter2026] CoSine samples it as one of five sources for 8192 prompts.[^gaoCollaborativeSpeculativeInference]

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | Instruction-following task for speedup and $\tau$ | Vicuna 13B, LLaMA-Instruct 3.1 8B and 3.3 70B, DeepSeek-R1-Distill-LLaMA 8B; temperature 0 and 1 | EAGLE-3 on Vicuna 13B at temperature 0: 5.16x, $\tau$ 6.17[^liEAGLE3ScalingInference2025] |
| [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md) | Instruction-following task for speedup and $\tau$ | Five targets with Eagle3 drafts | LTD on L31 8B at temperature 0: 4.53, $\tau$ 7.31[^zhangLearningDraftAdaptive2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | Chat prompt set for accepted length; also the dataset of the confidence reliability diagram | Qwen3-4B, 8B, 14B, Gemma4-12B; temperature 1.0 | DSpark $\tau$ from 3.35 to 3.58 across the four targets[^chengDSparkConfidenceScheduledSpeculative2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | Chat prompt set for speedup and $\tau$ | Qwen3-8B and 14B; greedy and temperature 1.0 | DPara on Qwen3-8B, greedy: 2.10×, $\tau$ 2.92[^liuWhenParallelDrafter2026] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Chat prompt set in the same-training-data comparison with EAGLE-3 | LLaMA-3.1-8B-Instruct on SGLang | DFlash (10): 2.2× at concurrency 1, $\tau$ 3.73[^chenDFlashBlockDiffusion2026] |
| [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md) | 128 prompts, 512 decoding tokens each | Llama-3.1-70B/1B and Qwen3-32B/0.6B, greedy | SSD on Llama-3.1 70B/1B: 224 tok/s, 4.10× over AR[^kumarSpeculativeSpeculativeDecoding2026] |
| [CoSine](../papers/gaoCollaborativeSpeculativeInference.md) | One of five prompt sources; a row of the drafter specialization table | Six domain-specialized drafters | Acceptance ratio from 1.82 to 2.86 depending on the drafter[^gaoCollaborativeSpeculativeInference] |

## Speed metrics

Speculative-decoding speedup, acceptance length, and throughput measured with this dataset's prompts. These numbers say nothing about task accuracy. Each subsection is one paper and one setting, and rows from different subsections are not comparable.

### [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md): Table 1

Speedup over vanilla autoregressive decoding and average acceptance length $\tau$. V = Vicuna, L31 = LLaMA-Instruct 3.1, L33 = LLaMA-Instruct 3.3, DSL = DeepSeek-R1-Distill-LLaMA. SpS is standard speculative sampling with Vicuna-68M as the draft model. The baseline (1.00x) is Huggingface.transformers with the PyTorch backend and a pre-allocated KV cache.[^liEAGLE3ScalingInference2025]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| V 13B | 0 | SpS | 1.76x | 2.03 |
| V 13B | 0 | PLD | 1.16x | 1.19 |
| V 13B | 0 | Medusa | 2.08x | 2.45 |
| V 13B | 0 | Lookahead | 1.46x | 1.51 |
| V 13B | 0 | Hydra | 2.86x | 3.53 |
| V 13B | 0 | EAGLE | 3.03x | 3.95 |
| V 13B | 0 | EAGLE-2 | 4.25x | 4.89 |
| V 13B | 0 | EAGLE-3 | 5.16x | 6.17 |
| L31 8B | 0 | EAGLE-2 | 3.28x | 4.12 |
| L31 8B | 0 | EAGLE-3 | 4.82x | 6.70 |
| L33 70B | 0 | EAGLE-2 | 3.03x | 3.92 |
| L33 70B | 0 | EAGLE-3 | 4.30x | 6.09 |
| DSL 8B | 0 | EAGLE-2 | 3.01x | 3.80 |
| DSL 8B | 0 | EAGLE-3 | 3.65x | 5.37 |
| V 13B | 1 | SpS | 1.52x | 1.78 |
| V 13B | 1 | EAGLE | 2.45x | 3.57 |
| V 13B | 1 | EAGLE-2 | 3.78x | 4.37 |
| V 13B | 1 | EAGLE-3 | 4.49x | 5.39 |
| L31 8B | 1 | EAGLE-2 | 2.83x | 3.65 |
| L31 8B | 1 | EAGLE-3 | 3.90x | 5.56 |
| L33 70B | 1 | EAGLE-2 | 2.77x | 3.73 |
| L33 70B | 1 | EAGLE-3 | 4.14x | 5.87 |
| DSL 8B | 1 | EAGLE-2 | 2.64x | 3.29 |
| DSL 8B | 1 | EAGLE-3 | 3.16x | 4.30 |

All rows: [^liEAGLE3ScalingInference2025]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): same training data as EAGLE-3, SGLang (Table 5)

DFlash is trained on UltraChat and ShareGPT and compared with the official EAGLE-3 checkpoints. SGLang with Spec-v1 (without scheduling overlap), Flashinfer backend, single B200 GPU. EAGLE-3 uses 7 draft steps with top-$k{=}10$ and either 10 or 60 draft tokens. DFlash uses block size 10. The baseline row is absolute throughput in tokens/s. The other rows are speedup over the baseline at each concurrency level.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| LLaMA-3.1-8B-Instruct | not stated | Baseline (TPS) | 245 | 906 | 1745 | 3237 | 5434 | – |
| LLaMA-3.1-8B-Instruct | not stated | EAGLE-3 (10) | 1.5× | 1.4× | 1.4× | 1.1× | 0.9× | 3.11 |
| LLaMA-3.1-8B-Instruct | not stated | EAGLE-3 (60) | 1.8× | 1.5× | 1.2× | 0.8× | 0.5× | 4.07 |
| LLaMA-3.1-8B-Instruct | not stated | DFlash (10) | 2.2× | 2.0× | 1.8× | 1.5× | 1.4× | 3.73 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): accepted length (Table 1)

Accepted length $\tau$ per decoding round, including the bonus token. Standard speculative decoding with chain-based drafting. All three drafters are retrained in the same framework on the same data, with block size 7 for DFlash and DSpark and TTT horizon 7 for Eagle3. Eagle3 has 1 draft layer, DSpark and DFlash have 5. The confidence scheduler is disabled. No speedup is reported for this table.[^chengDSparkConfidenceScheduledSpeculative2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Qwen3-4B | 1.0 | Eagle3 | 2.26 |
| Qwen3-4B | 1.0 | DFlash | 2.96 |
| Qwen3-4B | 1.0 | DSpark | 3.54 |
| Qwen3-8B | 1.0 | Eagle3 | 2.54 |
| Qwen3-8B | 1.0 | DFlash | 2.98 |
| Qwen3-8B | 1.0 | DSpark | 3.58 |
| Qwen3-14B | 1.0 | Eagle3 | 2.47 |
| Qwen3-14B | 1.0 | DFlash | 2.94 |
| Qwen3-14B | 1.0 | DSpark | 3.58 |
| Gemma4-12B | 1.0 | Eagle3 | 3.06 |
| Gemma4-12B | 1.0 | DFlash | 2.84 |
| Gemma4-12B | 1.0 | DSpark | 3.35 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): Tables 1 and 3

Batch size 1, up to 512 new tokens, draft length 7, speedup over AR. Temperature 0 rows are greedy decoding (Table 1). Temperature 1.0 rows use temperature 1.0 for both the target and the drafter (Table 3). SSD-E3 uses the EAGLE3 weight of the target as draft model. SSD, SD, and PEARL on Qwen3-14B use Qwen3-0.6B as draft model. The parallel methods (PEARL, SSD, DPara) use one additional GPU for drafting.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-8B | 0 | SSD-E3 | 1.29× | 2.17 |
| Qwen3-8B | 0 | EAGLE3 | 1.18× | 2.45 |
| Qwen3-8B | 0 | DFlash | 1.81× | 3.28 |
| Qwen3-8B | 0 | DSpark | 2.00× | 3.72 |
| Qwen3-8B | 0 | DPara | 2.10× | 2.92 |
| Qwen3-14B | 0 | SSD | 1.39× | 3.17 |
| Qwen3-14B | 0 | SSD-E3 | 1.48× | 2.17 |
| Qwen3-14B | 0 | PEARL | 1.84× | 1.98 |
| Qwen3-14B | 0 | SD | 1.31× | 3.17 |
| Qwen3-14B | 0 | EAGLE3 | 1.42× | 2.42 |
| Qwen3-14B | 0 | DFlash | 2.07× | 3.24 |
| Qwen3-14B | 0 | DSpark | 2.32× | 3.71 |
| Qwen3-14B | 0 | DPara | 2.32× | 2.91 |
| Qwen3-8B | 1.0 | DFlash | 1.56× | 2.98 |
| Qwen3-8B | 1.0 | DSpark | 1.80× | 3.54 |
| Qwen3-8B | 1.0 | DPara | 1.89× | 2.81 |
| Qwen3-14B | 1.0 | DFlash | 1.85× | 2.96 |
| Qwen3-14B | 1.0 | DSpark | 2.16× | 3.54 |
| Qwen3-14B | 1.0 | DPara | 2.18× | 2.79 |

All rows: [^liuWhenParallelDrafter2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): backbone finetuning ablation

DPara with the same frozen AR head, comparing the original DSpark checkpoint with the finetuned M-DFlash backbone.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | $\tau$ with original DSpark checkpoint | $\tau$ with M-DFlash | Relative gain |
|---|---|---|---|---|---|
| Qwen3-8B | not stated | DPara | 2.55 | 2.92 | 14.4% |

All rows: [^liuWhenParallelDrafter2026]

### [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md): Tables 1 and 5

Temperature 0 rows are Table 1 and temperature 1 rows are the per-task part of Table 5. Policies are trained only at greedy decoding. Speedup relative to vanilla auto-regressive decoding. L31 8B = Llama-3.1-8B-Instruct, V 13B = Vicuna-13B-v1.3, Dpsk 8B = DeepSeek-R1-Distill-LLaMA 8B. Default Eagle3 uses verification size 60 and 50 for the 8B and 13B LLMs, draft depth 8, and 10 nodes selected during expansion. GS is grid search over draft depth and verification size on HumanEval. LTD is the paper's learned policy.[^zhangLearningDraftAdaptive2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| L31 8B | 0 | Eagle3 | 4.26 | 6.93 |
| L31 8B | 0 | Eagle3+DDD | 3.97 | 5.58 |
| L31 8B | 0 | Eagle3+Svip | 4.04 | 6.73 |
| L31 8B | 0 | Eagle3+GT | 4.37 | 6.49 |
| L31 8B | 0 | Eagle3+C2T | 4.19 | 6.93 |
| L31 8B | 0 | Eagle3+Disco | 4.14 | 6.51 |
| L31 8B | 0 | Eagle3+Spec++ | 4.29 | 6.70 |
| L31 8B | 0 | Eagle3+GS | 4.38 | 7.42 |
| L31 8B | 0 | Eagle3+LTD | 4.53 | 7.31 |
| V 13B | 0 | Eagle3 | 4.16 | 6.47 |
| V 13B | 0 | Eagle3+DDD | 3.98 | 5.50 |
| V 13B | 0 | Eagle3+Svip | 3.77 | 6.53 |
| V 13B | 0 | Eagle3+GT | 3.94 | 6.09 |
| V 13B | 0 | Eagle3+C2T | 3.93 | 6.47 |
| V 13B | 0 | Eagle3+Disco | 4.02 | 6.29 |
| V 13B | 0 | Eagle3+Spec++ | 4.00 | 6.27 |
| V 13B | 0 | Eagle3+GS | 4.38 | 7.16 |
| V 13B | 0 | Eagle3+LTD | 4.40 | 7.01 |
| Dpsk 8B | 0 | Eagle3 | 3.65 | 5.63 |
| Dpsk 8B | 0 | Eagle3+GS | 3.54 | 6.24 |
| Dpsk 8B | 0 | Eagle3+LTD | 3.98 | 6.00 |
| Qwen3 14B | 0 | Eagle3+GS | 2.15 | 2.90 |
| Qwen3 14B | 0 | Eagle3+LTD | 2.24 | 2.87 |
| Qwen3 32B | 0 | Eagle3+GS | 1.75 | 2.96 |
| Qwen3 32B | 0 | Eagle3+LTD | 2.38 | 2.85 |
| L31 8B | 1 | Eagle3 | 3.38 | 5.47 |
| L31 8B | 1 | Eagle3+DDD | 3.38 | 4.59 |
| L31 8B | 1 | Eagle3+Svip | 3.19 | 4.95 |
| L31 8B | 1 | Eagle3+GT | 3.51 | 5.12 |
| L31 8B | 1 | Eagle3+C2T | 3.24 | 5.47 |
| L31 8B | 1 | Eagle3+Disco | 3.30 | 5.18 |
| L31 8B | 1 | Eagle3+Spec++ | 3.42 | 5.51 |
| L31 8B | 1 | Eagle3+GS | 3.46 | 5.79 |
| L31 8B | 1 | Eagle3+LTD | 3.43 | 5.68 |
| V 13B | 1 | Eagle3 | 3.40 | 5.49 |
| V 13B | 1 | Eagle3+DDD | 3.43 | 5.00 |
| V 13B | 1 | Eagle3+Svip | 3.21 | 5.39 |
| V 13B | 1 | Eagle3+GT | 3.39 | 4.95 |
| V 13B | 1 | Eagle3+C2T | 3.27 | 5.54 |
| V 13B | 1 | Eagle3+Disco | 3.36 | 5.51 |
| V 13B | 1 | Eagle3+Spec++ | 3.34 | 5.39 |
| V 13B | 1 | Eagle3+GS | 3.61 | 6.01 |
| V 13B | 1 | Eagle3+LTD | 3.65 | 6.20 |
| Dpsk 8B | 1 | Eagle3 | 2.79 | 4.53 |
| Dpsk 8B | 1 | Eagle3+GS | 2.76 | 4.83 |
| Dpsk 8B | 1 | Eagle3+LTD | 2.83 | 4.76 |
| Qwen3 14B | 1 | Eagle3+GS | 2.04 | 2.78 |
| Qwen3 14B | 1 | Eagle3+LTD | 2.11 | 2.76 |
| Qwen3 32B | 1 | Eagle3+GS | 1.63 | 2.73 |
| Qwen3 32B | 1 | Eagle3+LTD | 2.16 | 2.59 |

All rows: [^zhangLearningDraftAdaptive2026]

### [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md): end-to-end decoding speed (Appendix B.3)

The paper's own AR, SD, and SSD implementations. Batch size 1, greedy decoding, target on 4×H100, SSD draft on a separate H100. 128 prompts from the dataset, 512 decoding tokens each, decoding throughput excluding prefill. Temperature 0 is the paper's stated default of greedy decoding. Its appendix also says it uses vanilla sampling (not top-p or top-k). The Model column is target/draft.[^kumarSpeculativeSpeculativeDecoding2026]

| Model | Temp. | Method | Decode tok/s | Speedup over SD | Speedup over AR |
|---|---|---|---|---|---|
| Llama-3.1-Instruct 70B/1B | 0 | AR | 54.7 | – | – |
| Llama-3.1-Instruct 70B/1B | 0 | SD | 145 | – | – |
| Llama-3.1-Instruct 70B/1B | 0 | SSD | 224 | 1.55× | 4.10× |
| Qwen-3 32B/0.6B | 0 | AR | 88.8 | – | – |
| Qwen-3 32B/0.6B | 0 | SD | 127 | – | – |
| Qwen-3 32B/0.6B | 0 | SSD | 185 | 1.47× | 2.08× |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]

### [CoSine](../papers/gaoCollaborativeSpeculativeInference.md): drafter specialization (Table 2)

The table caption calls the values "acceptance ratio". Drafters #1 to #6 are fine-tuned on different domains. The table does not state which model pair or decoding temperature it uses. The paper's general setting is greedy sampling.[^gaoCollaborativeSpeculativeInference]

| Model | Temp. | Method | Acceptance ratio |
|---|---|---|---|
| not stated | not stated | Drafter #1 | 1.83 |
| not stated | not stated | Drafter #2 | 1.95 |
| not stated | not stated | Drafter #3 | 2.04 |
| not stated | not stated | Drafter #4 | 2.86 |
| not stated | not stated | Drafter #5 | 2.13 |
| not stated | not stated | Drafter #6 | 1.82 |

All rows: [^gaoCollaborativeSpeculativeInference]


## Known issues

- The papers do not cite the same source for "Alpaca". DSpark, DPara, DFlash, and Learning to Draft cite Taori et al. (2023).[^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026][^chenDFlashBlockDiffusion2026][^zhangLearningDraftAdaptive2026] The Speculative Speculative Decoding paper cites Dubois et al. (2023), whose reference entry is AlpacaFarm.[^kumarSpeculativeSpeculativeDecoding2026]
- Acceptance length on Alpaca is lower than on the math and code sets in the DSpark and DPara tables.[^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026]
- On the DPara paper's Qwen3-14B greedy table, DPara ties with DSpark on Alpaca, the only model-dataset pair where DPara does not have the strictly highest speedup.[^liuWhenParallelDrafter2026]

# Contradictions

### Same drafter, target, and temperature in different papers

More than one paper reports the same drafter on the same Qwen3 target and temperature with this dataset. The values are side by side below, and most of them differ.

| Target | Temp. | Method | DSpark paper[^chengDSparkConfidenceScheduledSpeculative2026] ($\tau$) | DPara paper[^liuWhenParallelDrafter2026] (speedup / $\tau$) |
|---|---|---|---|---|
| Qwen3-8B | 1 | DFlash | 2.98 | 1.56× / 2.98 |
| Qwen3-8B | 1 | DSpark | 3.58 | 1.80× / 3.54 |
| Qwen3-14B | 1 | DFlash | 2.94 | 1.85× / 2.96 |
| Qwen3-14B | 1 | DSpark | 3.58 | 2.16× / 3.54 |

The settings differ in ways that the papers state. The DSpark paper retrains all three drafters in one framework on the same data, uses chain-based drafting with block size 7 (TTT horizon 7 for Eagle3), and reports only $\tau$.[^chengDSparkConfidenceScheduledSpeculative2026] The DPara paper uses batch size 1, draft length 7, and up to 512 new tokens on an H800 node.[^liuWhenParallelDrafter2026]

### EAGLE-3 public checkpoints in different papers

Each cell is speedup / $\tau$ for EAGLE-3 on the same target. L31 8B = LLaMA-Instruct 3.1 8B, L33 70B = LLaMA-Instruct 3.3 70B, V 13B = Vicuna 13B, DSL 8B = DeepSeek-R1-Distill-LLaMA 8B.[^liEAGLE3ScalingInference2025]

| Target | Temp. | EAGLE-3 paper[^liEAGLE3ScalingInference2025] | Learning to Draft paper[^zhangLearningDraftAdaptive2026] | DFlash paper, Table 5[^chenDFlashBlockDiffusion2026] |
|---|---|---|---|---|
| DSL 8B | 0 | 3.65x / 5.37 | 3.65 / 5.63 | – |
| L31 8B | 0 | 4.82x / 6.70 | 4.26 / 6.93 | 1.5× / 3.11 (EAGLE-3 (10); temperature not stated); 1.8× / 4.07 (EAGLE-3 (60); temperature not stated) |
| V 13B | 0 | 5.16x / 6.17 | 4.16 / 6.47 | – |
| DSL 8B | 1 | 3.16x / 4.30 | 2.79 / 4.53 | – |
| L31 8B | 1 | 3.90x / 5.56 | 3.38 / 5.47 | – |
| V 13B | 1 | 4.49x / 5.39 | 3.40 / 5.49 | – |

The EAGLE-3 paper measures against Huggingface.transformers and does not state the hardware for its Table 1.[^liEAGLE3ScalingInference2025] The Learning to Draft paper runs the official Eagle3 releases with verification size 60 (50 for the 13B model), draft depth 8, and 10 nodes selected during expansion.[^zhangLearningDraftAdaptive2026] The DFlash paper runs the official EAGLE-3 checkpoint in SGLang with 10 or 60 draft tokens and reports speedup at concurrency 1.[^chenDFlashBlockDiffusion2026]


## Related

- Methods measured on it: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-2](../methods/eagle-2.md), [PEARL](../methods/pearl.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [SpecInfer](../methods/specinfer.md)
- Serving engines used for the measurements: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets evaluated alongside it: [MT-Bench](mt-bench.md), [GSM8K](gsm8k.md), [HumanEval](humaneval.md), [MATH-500](math-500.md), [MBPP](mbpp.md), [CNN/Daily Mail](cnn-dailymail.md)
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
