---
type: Method
title: EAGLE-3
description: Speculative sampling draft model that predicts tokens directly from fused low-, mid-, and high-level target features and is trained with training-time test; the most re-measured baseline among the wiki's speculative decoding papers.
tags: [speculative-decoding, draft-model, training-time-test, feature-fusion, llm-inference, baseline]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
---

# EAGLE-3

## Overview

EAGLE-3 is a draft model for [speculative decoding](../methods/speculative-decoding.md) (the paper says "speculative sampling"). It abandons the feature prediction of [EAGLE](../methods/eagle.md) for direct token prediction, and replaces reliance on top-layer target features with a fusion of low-, mid-, and high-level features, through a technique named [training-time test](../methods/training-time-test.md).[^liEAGLE3ScalingInference2025] It keeps the context-aware dynamic draft tree of [EAGLE-2](../methods/eagle-2.md).[^liEAGLE3ScalingInference2025]

The original paper reports a speedup ratio up to 6.5x, about 1.4x over EAGLE-2, and a 1.38x throughput improvement at a batch size of 64 in [SGLang](../methods/sglang.md).[^liEAGLE3ScalingInference2025]

Ten papers in this wiki use EAGLE-3. Seven of them measure it again as a baseline or building block, with settings that differ from the original paper. The section "Re-measured baseline numbers" lists each set of numbers, and "Contradictions" lists where they disagree.

## How it works

### Drafting

- From the target model's forward pass, the low, middle, and high-level feature sequences $l$, $m$, $h$ are recorded. The three $k$-dimensional vectors are concatenated into a $3k$-dimensional vector and reduced to $k$ dimensions by a fully connected (FC) layer, which gives the fused feature $g$. $k$ is the hidden size of the target model.[^liEAGLE3ScalingInference2025]
- $g$ is concatenated with the embedding $e$ of the sampled token, reduced to $k$ dimensions by an FC layer, and fed into a single layer decoder that outputs $a$. $a$ goes into the LM head, and sampling gives the draft token.[^liEAGLE3ScalingInference2025]
- For later draft steps, $g$ of an unverified token is not available. The draft model's own output $a$ from the previous step replaces it.[^liEAGLE3ScalingInference2025]
- Verification follows other speculative sampling methods: EAGLE-3 differs from EAGLE only in the drafting stage.[^liEAGLE3ScalingInference2025]

### Training

- The draft-model input may be target features $g_1,\cdots,g_t$ or the draft model's own outputs $a_{t+1},\cdots,a_{t+j}$. During training, test steps generate $a$ and feed it back into the draft model. This is [training-time test](../methods/training-time-test.md).[^liEAGLE3ScalingInference2025]
- Only the self-attention of the Transformer decoder layer changes: the attention mask is adjusted in the simulated steps to respect the tree-like contextual relationship.[^liEAGLE3ScalingInference2025]
- Optimizer AdamW with $(\beta_1,\beta_2)$ = (0.9, 0.95), gradient clipping of 0.5, learning rate 5e-5. Training data is [ShareGPT](../datasets/sharegpt.md) (approximately 68K entries) and UltraChat-200K (approximately 464K entries), with responses generated by calling the target model.[^liEAGLE3ScalingInference2025]
- EAGLE-3 is trained with approximately 8x more data than EAGLE. The paper reports that the speedup ratio increases proportionally with the amount of draft-model training data, which it did not observe for the original EAGLE architecture.[^liEAGLE3ScalingInference2025]

### Default draft tree

The draft tree depth is 8, increased from 6 in EAGLE-2, with the same number of nodes as EAGLE-2 (total draft tokens 60, 50, and 48 for the 7B (8B), 13B, and 70B LLMs).[^liEAGLE3ScalingInference2025]

## Variants

| Variant | Where | What differs |
|---|---|---|
| Tree draft (default) | Original paper Table 1, LTD, DFlash, SuffixDecoding | Dynamic draft tree, depth 8, 48 to 60 draft tokens.[^liEAGLE3ScalingInference2025] |
| Chain draft | Original paper's SGLang and [vLLM](../methods/vllm.md) experiments, LK losses, DSpark | No tree structure. Chain length 3 in SGLang and maximum chain length 2 in vLLM in the original paper.[^liEAGLE3ScalingInference2025] $K=7$ in LK losses.[^samarinLKLossesDirect2026] Block size 7 in DSpark.[^chengDSparkConfidenceScheduledSpeculative2026] |
| Truncated draft vocabulary | LK losses, Aurora | LK losses states that EAGLE-3 uses a truncated vocabulary for its LM head, as proposed in FR-Spec.[^samarinLKLossesDirect2026] Aurora gives draft vocabulary sizes of 32K vs 128K for Llama3 models and 32K vs 152K for Qwen3 models.[^wangWhenRLMeets2026] |
| Dense head for MoE targets | LK losses | For MoE target models (gpt-oss-20b, gpt-oss-120b, Qwen3-235B) the draft is a single dense transformer block, not an MoE block.[^samarinLKLossesDirect2026] SpecForge finds that a dense draft model outperforms all MoE draft variants.[^liSpecForgeFlexibleEfficient2026] |
| EAGLE-3-5L | DFlash Table 9 | A 5-layer autoregressive EAGLE-3 drafter with input fusion, used as an ablation.[^chenDFlashBlockDiffusion2026] |
| SSD-E3 | DPara Table 1 | Speculative speculative decoding with the EAGLE3 weight of the target as draft model.[^liuWhenParallelDrafter2026] |
| Third-party checkpoints | DFlash, LTD, LK losses, SpecForge | AngelSlim checkpoints for Qwen3.[^chenDFlashBlockDiffusion2026][^zhangLearningDraftAdaptive2026] RedHatAI (RH), yuhuili (YH), and zhuyksir (ZK) HuggingFace checkpoints.[^samarinLKLossesDirect2026] SpecBundle checkpoints trained with SpecForge.[^liSpecForgeFlexibleEfficient2026] |

## Original results

Speedup over vanilla autoregressive decoding / average acceptance length $\tau$. The baseline (1.00x) is Huggingface.transformers with the PyTorch backend and pre-allocated KV cache. V = Vicuna, L31 = LLaMA-Instruct 3.1, L33 = LLaMA-Instruct 3.3, DSL = DeepSeek-R1-Distill-LLaMA. Tasks: [MT-bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md).[^liEAGLE3ScalingInference2025]

| Model | Temp. | MT-bench | HumanEval | GSM8K | Alpaca | CNN/DM | Mean |
|---|---|---|---|---|---|---|---|
| V 13B | 0 | 5.58x / 6.65 | 6.47x / 7.54 | 5.32x / 6.29 | 5.16x / 6.17 | 5.01x / 6.47 | 5.51x / 6.62 |
| L31 8B | 0 | 4.40x / 6.13 | 4.85x / 6.74 | 4.48x / 6.23 | 4.82x / 6.70 | 3.65x / 5.34 | 4.44x / 6.23 |
| L33 70B | 0 | 4.11x / 5.63 | 4.79x / 6.52 | 4.34x / 6.15 | 4.30x / 6.09 | 3.27x / 5.02 | 4.12x / 5.88 |
| DSL 8B | 0 | 4.05x / 5.58 | 4.59x / 6.38 | 5.01x / 6.93 | 3.65x / 5.37 | 3.52x / 4.92 | 4.16x / 5.84 |
| V 13B | 1 | 4.57x / 5.42 | 5.15x / 6.22 | 4.71x / 5.58 | 4.49x / 5.39 | 4.33x / 5.72 | 4.65x / 5.67 |
| L31 8B | 1 | 3.07x / 4.24 | 4.13x / 5.82 | 3.32x / 4.59 | 3.90x / 5.56 | 2.99x / 4.39 | 3.45x / 4.92 |
| L33 70B | 1 | 3.96x / 5.45 | 4.36x / 6.16 | 4.17x / 5.95 | 4.14x / 5.87 | 3.11x / 4.88 | 3.95x / 5.66 |
| DSL 8B | 1 | 3.20x / 4.49 | 3.77x / 5.28 | 4.38x / 6.10 | 3.16x / 4.30 | 3.08x / 4.27 | 3.52x / 4.89 |

All rows: [^liEAGLE3ScalingInference2025]

- The hardware for this table is not stated in the paper.[^liEAGLE3ScalingInference2025]
- Ablation on L31 8B: EAGLE-2 gives 3.16x / 4.05 on MT-bench and 3.39x / 4.24 on GSM8K. Removing the feature prediction constraint gives 3.82x / 5.37 and 3.77x / 5.22. Adding fused features gives 4.40x / 6.13 and 4.48x / 6.23.[^liEAGLE3ScalingInference2025]
- In SGLang v0.4.4 on a single H100 with L31 8B on MT-Bench (chain length 3, no tree), the throughput improvement is 1.81x at batch size 2 and 1.38x at batch size 64. At batch size 1 the throughput is 373.25 tokens/s against 158.34 tokens/s without speculation and 244.10 tokens/s with EAGLE-2.[^liEAGLE3ScalingInference2025]
- In vLLM (maximum chain length 2, no tree) the improvement is 1.75x at batch size 2 and 1.01x at batch size 56.[^liEAGLE3ScalingInference2025]

## Re-measured baseline numbers

Each subsection gives one paper's EAGLE-3 numbers and the settings that produced them. Paper names are plain text when the method has no page in this wiki.

### DFlash (Chen et al. 2026)

Qwen3 targets, Transformers backend, NVIDIA H200, thinking mode disabled, maximum of 2048 generated tokens. EAGLE-3 checkpoints are those released by AngelSlim. EAGLE-3 uses 7 draft steps and top-$k$ 10. The number in parentheses is the draft tree size. Each cell is speedup / $\tau$.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | EAGLE-3 | GSM8K | HumanEval | MT-Bench | Avg. (7 tasks) |
|---|---|---|---|---|---|---|
| Q3-4B | 0 | (16) | 1.99× / 3.30 | 1.84× / 3.05 | 1.74× / 3.02 | 1.81× / 3.05 |
| Q3-4B | 0 | (60) | 2.27× / 3.77 | 2.12× / 3.47 | 2.04× / 3.49 | 2.08× / 3.48 |
| Q3-8B | 0 | (16) | 1.94× / 3.23 | 1.89× / 3.17 | 1.63× / 2.83 | 1.76× / 2.96 |
| Q3-8B | 0 | (60) | 2.23× / 3.71 | 2.17× / 3.65 | 1.90× / 3.26 | 2.02× / 3.40 |
| Q3-4B | 1 | (16) | 1.89× / 3.22 | 1.74× / 3.01 | 1.70× / 2.95 | 1.72× / 2.95 |
| Q3-4B | 1 | (60) | 2.12× / 3.68 | 1.94× / 3.39 | 1.91× / 3.36 | 1.93× / 3.36 |
| Q3-8B | 1 | (16) | 1.87× / 3.12 | 1.75× / 3.05 | 1.58× / 2.70 | 1.68× / 2.83 |
| Q3-8B | 1 | (60) | 2.07× / 3.59 | 2.05× / 3.54 | 1.70× / 3.05 | 1.88× / 3.26 |

All rows: [^chenDFlashBlockDiffusion2026]

LLaMA-3.1-8B-Instruct with the official EAGLE-3 checkpoint, on SGLang with Spec-v1 (without scheduling overlap), Flashinfer backend, single B200 GPU. EAGLE-3 uses 7 draft steps with top-$k{=}10$ and either 10 or 60 draft tokens. Cells are speedup over the SGLang baseline at each concurrency.[^chenDFlashBlockDiffusion2026]

| Task | EAGLE-3 | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|
| GSM8K | (10) | 1.6× | 1.5× | 1.4× | 1.2× | 1.0× | 3.49 |
| GSM8K | (60) | 1.9× | 1.6× | 1.3× | 0.9× | 0.6× | 4.55 |
| HumanEval | (10) | 2.0× | 1.9× | 1.8× | 1.5× | 1.2× | 3.62 |
| HumanEval | (60) | 2.0× | 1.7× | 1.3× | 0.9× | 0.6× | 4.65 |
| Alpaca | (10) | 1.5× | 1.4× | 1.4× | 1.1× | 0.9× | 3.11 |
| Alpaca | (60) | 1.8× | 1.5× | 1.2× | 0.8× | 0.5× | 4.07 |

All rows: [^chenDFlashBlockDiffusion2026]

A 5-layer EAGLE-3 with input fusion on Qwen3-4B (draft block size 8) gets $\tau$ / speedup of 4.2 / 2.1× on GSM8K, 4.3 / 2.2× on HumanEval, and 3.1 / 1.4× on MT-Bench.[^chenDFlashBlockDiffusion2026]

### DSpark (Cheng et al. 2026)

Eagle3 is retrained in the authors' framework on 1.3 million Open-PerfectBlend samples with responses regenerated by each target, for 10 epochs. It has 1 draft layer and a TTT horizon of 7. Evaluation uses standard speculative decoding at sampling temperature $1.0$ with chain-based drafting. The metric is accepted length $\tau$ per decoding round, including the bonus token. No wall-clock speedup is reported.[^chengDSparkConfidenceScheduledSpeculative2026]

| Target | GSM8K | MATH | AIME25 | MBPP | HumanEval | LCB | MT-Bench | Alpaca | Arena-Hard |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3-4B | 5.14 | 4.62 | 3.92 | 3.69 | 4.16 | 3.77 | 2.39 | 2.26 | 2.55 |
| Qwen3-8B | 5.30 | 4.77 | 3.91 | 3.96 | 4.33 | 4.17 | 2.66 | 2.54 | 2.54 |
| Qwen3-14B | 5.24 | 4.60 | 3.71 | 3.81 | 4.14 | 4.01 | 2.62 | 2.47 | 2.48 |
| Gemma4-12B | 5.87 | 5.46 | 4.83 | 4.72 | 5.37 | 4.16 | 3.19 | 3.06 | 2.72 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

On Qwen3-4B the conditional acceptance at draft position 1 is 0.81 on Math and 0.53 on Chat for Eagle3, and along the block it goes from 0.53 to 0.74 on Chat.[^chengDSparkConfidenceScheduledSpeculative2026]

### LK losses (Samarin et al. 2026)

Chain sampling with $K=7$, vLLM v0.11.0 with a patch for proper rejection sampling at non-zero temperatures, batch size 1. Each cell is $\tau$ / end-to-end speedup. "Ours KL" is an EAGLE-3 head trained from scratch by the authors with KL on 660K Infinity-Instruct prompts for 10 epochs. "HF" rows are public HuggingFace checkpoints run through the same pipeline (RH = RedHatAI, YH = yuhuili, ZK = zhuyksir).[^samarinLKLossesDirect2026]

| Target | EAGLE-3 draft | T=0 MT-Bench | T=0 HumanEval | T=0 GSM8K | T=1 MT-Bench | T=1 HumanEval | T=1 GSM8K |
|---|---|---|---|---|---|---|---|
| LLaMA 3.1 8B Instruct | Ours KL | 3.75 / 2.60 | 4.82 / 3.30 | 4.50 / 3.05 | 3.39 / 2.29 | 4.31 / 3.00 | 3.88 / 2.63 |
| LLaMA 3.1 8B Instruct | HF RH-8B | 3.08 / 2.09 | 3.90 / 2.65 | 3.57 / 2.37 | 2.67 / 1.83 | 3.36 / 2.31 | 3.08 / 2.05 |
| LLaMA 3.1 8B Instruct | HF YH-8B | 3.44 / 2.42 | 4.37 / 3.07 | 3.84 / 2.65 | 2.97 / 2.22 | 3.75 / 2.50 | 3.21 / 2.14 |
| LLaMA 3.1 8B Instruct | HF ZK-8B | 3.54 / 2.45 | 4.49 / 3.08 | 3.97 / 2.71 | 3.06 / 2.68 | 3.96 / 2.82 | 3.36 / 2.28 |
| LLaMA 3.3 70B Instruct | Ours KL | 4.01 / 3.01 | 5.18 / 3.87 | 5.16 / 3.78 | 3.76 / 2.82 | 4.86 / 3.66 | 4.89 / 3.61 |
| LLaMA 3.3 70B Instruct | HF RH-70B | 3.11 / 2.35 | 3.99 / 2.99 | 3.62 / 2.68 | 2.88 / 2.10 | 3.62 / 2.69 | 3.29 / 2.44 |
| LLaMA 3.3 70B Instruct | HF YH-70B | 3.13 / 2.50 | 3.96 / 3.12 | 3.76 / 2.90 | 2.77 / 2.07 | 3.49 / 2.63 | 3.34 / 2.50 |
| GPT-OSS 20B | Ours KL | 3.31 / 1.41 | 3.08 / 1.32 | 4.01 / 1.63 | 3.12 / 1.30 | 2.89 / 1.20 | 3.51 / 1.44 |
| GPT-OSS 120B | Ours KL | 2.81 / 1.57 | 2.47 / 1.54 | 3.00 / 1.77 | 2.53 / 1.20 | 2.27 / 1.19 | 2.57 / 1.32 |
| Qwen 3 235B A22B Instruct | Ours KL | 3.33 / 2.09 | 4.65 / 2.73 | 4.76 / 2.88 | 2.96 / 1.84 | 4.09 / 2.37 | 4.27 / 2.50 |
| Qwen 3 235B A22B Instruct | HF RH-235B | 2.92 / 1.85 | 4.06 / 2.42 | 4.31 / 2.63 | 2.56 / 1.61 | 3.52 / 2.06 | 3.78 / 2.22 |

All rows: [^samarinLKLossesDirect2026]

Training the same EAGLE-3 head with the hybrid LK loss ($\eta=3$) instead of KL raises the mean $\tau$ on LLaMA 3.1 8B from 4.36 to 4.43 (+1.6) at $T=0$ and from 3.86 to 4.01 (+3.9) at $T=1$.[^samarinLKLossesDirect2026]

### SpecForge (Li et al. 2026)

SGLang on NVIDIA H200 GPUs. Concurrent requests are fixed to 8 for LLaMA-3.1-8B and 16 for larger models. The highest throughput among five (speculative steps, top-k, draft tokens) configurations is reported. "Existing" is an existing open-source EAGLE-3 draft model, from the EAGLE3 authors or the LMSYS team. Cells are speedup over the target model alone.[^liSpecForgeFlexibleEfficient2026]

| Target | Draft | MTBench | GPQA | FinanceQA | LiveCodeBench | HumanEval | GSM8K | Math500 |
|---|---|---|---|---|---|---|---|---|
| Llama-3.1-8B | Existing | 2.39 | 2.30 | 1.27 | 2.10 | 2.52 | 1.26 | 2.21 |
| Llama-3.1-8B | SpecBundle | 2.37 | 2.70 | 1.39 | 2.72 | 2.99 | 1.81 | 3.34 |
| Llama-3.3-70B | Existing | 2.35 | 1.82 | 1.92 | 2.32 | 2.29 | 1.15 | 1.98 |
| Llama-3.3-70B | SpecBundle | 2.31 | 2.44 | 2.00 | 2.60 | 2.68 | 1.59 | 2.69 |
| Qwen-235B-A22B | Existing | 1.21 | 1.27 | 1.28 | 1.34 | 1.61 | 1.49 | 1.39 |
| Qwen-235B-A22B | SpecBundle | 1.54 | 1.47 | 1.65 | 1.93 | 2.29 | 1.62 | 2.38 |

All rows: [^liSpecForgeFlexibleEfficient2026]

- The authors reproduced EAGLE-3 training for LLaMA-3.1-Instruct on ShareGPT (120K conversations) and UltraChat (200K conversations) and obtained an acceptance length of 2.82 on Math500. Training the same draft model on the Perfect-Blend dataset (1.4M conversations) raised it to 3.48.[^liSpecForgeFlexibleEfficient2026]
- A dense EAGLE-3 draft with 3 steps, top-k 1, and 4 draft tokens has values of 2.99 on MTBench, 3.48 on GSM8K, 3.34 on HumanEval, and 2.55 on Math500. The table is captioned "acceptance rate" and does not state the target model.[^liSpecForgeFlexibleEfficient2026]
- SpecForge cites EAGLE-3 as achieving up to 4.79× speedup on LLaMA-3.3-70B, which is the HumanEval cell at temperature 0 in the original table.[^liSpecForgeFlexibleEfficient2026][^liEAGLE3ScalingInference2025]

### Learning to Draft, LTD (Zhang et al. 2026)

Official Eagle3 releases for Llama-3.1-8B-Instruct, Vicuna-13B-v1.3, and DeepSeek-R1-Distill-LLaMA 8B. AngelSlim Eagle3 models for Qwen3. Default Eagle3: verification size 60 and 50 for the 8B and 13B LLMs, draft depth 8, 10 nodes selected during expansion. The Qwen3 Eagle3 models lack default settings, so only grid search (GS) over draft depths 4 to 12 and verification sizes 40 to 240 is given. All experiments were conducted on a single NVIDIA A100 GPU. Each cell is speedup / $\tau$. Qa is Natural Questions.[^zhangLearningDraftAdaptive2026]

| Model | Method | Temp. | MT-bench | Gsm8k | Alpaca | Qa | Mean |
|---|---|---|---|---|---|---|---|
| L31 8B | Eagle3 | 0 | 3.70 / 6.39 | 3.58 / 6.44 | 4.26 / 6.93 | 3.17 / 5.35 | 3.68 / 6.28 |
| L31 8B | Eagle3+GS | 0 | 3.83 / 6.75 | 3.78 / 6.91 | 4.38 / 7.42 | 3.33 / 5.67 | 3.83 / 6.69 |
| V 13B | Eagle3 | 0 | 4.48 / 7.22 | 4.36 / 6.58 | 4.16 / 6.47 | 3.43 / 5.12 | 4.11 / 6.35 |
| V 13B | Eagle3+GS | 0 | 4.53 / 7.99 | 4.47 / 7.27 | 4.38 / 7.16 | 3.51 / 5.48 | 4.22 / 6.98 |
| Dpsk 8B | Eagle3 | 0 | 3.67 / 5.82 | 4.73 / 7.39 | 3.65 / 5.63 | 3.14 / 5.02 | 3.80 / 5.53 |
| Dpsk 8B | Eagle3+GS | 0 | 3.69 / 6.42 | 4.83 / 8.37 | 3.54 / 6.24 | 3.20 / 5.55 | 3.82 / 6.08 |
| Qwen3 14B | Eagle3+GS | 0 | 2.34 / 3.40 | 2.75 / 3.95 | 2.15 / 2.90 | 1.86 / 2.65 | 2.28 / 3.23 |
| Qwen3 32B | Eagle3+GS | 0 | 1.76 / 3.30 | 2.26 / 4.10 | 1.75 / 2.96 | 1.45 / 2.67 | 1.81 / 3.26 |

All rows: [^zhangLearningDraftAdaptive2026]

At temperature 1, the mean over the four tasks for default Eagle3 is 2.98 / 4.47 on L31 8B, 3.44 / 5.33 on V 13B, and 3.07 / 4.66 on Dpsk 8B. Eagle3+GS gets 2.10 / 3.08 on Qwen3 14B and 1.66 / 3.01 on Qwen3 32B.[^zhangLearningDraftAdaptive2026]

### Speculative Speculative Decoding, SSD (Kumar et al. 2026)

Llama-3.1-70B target, tensor parallelism across 4×H100 80GB GPUs, greedy decoding, radix caching disabled, a single concurrent request. Values are decode throughput in tok/s, excluding prefill, best configuration from a sweep.[^kumarSpeculativeSpeculativeDecoding2026]

| Engine | Method | Best tok/s | Best configuration |
|---|---|---|---|
| SGLang 0.5.9 | EAGLE-3 | 192.8 | steps 8, topk 3 |
| SGLang 0.5.9 | Standalone SD (Llama-3.2-1B draft) | 201.9 | steps 10, topk 3 |
| vLLM 0.16.0 | EAGLE-3 | 197.6 | $K=6$ |
| vLLM 0.16.0 | Standalone SD (Llama-3.2-1B draft) | 136.0 | $K=2$ |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]

- The vLLM EAGLE-3 sweep over lookahead $K$ = 2, 4, 6, 8, 10, 12 gives 143.7, 181.4, 197.6, 197.0, 191.8, 187.9 tok/s.[^kumarSpeculativeSpeculativeDecoding2026]
- The authors' own autoregressive implementation decodes at 54.7 tok/s for this target. The paper gives no autoregressive throughput for SGLang or vLLM in these sweep tables, so no speedup ratio is stated for EAGLE-3.[^kumarSpeculativeSpeculativeDecoding2026]
- In the authors' experiments, Llama-3.2-1B outperforms EAGLE-3 as a draft model for Llama-3.1-70B in SGLang.[^kumarSpeculativeSpeculativeDecoding2026]

### SuffixDecoding (Oliaro et al. 2024)

Llama-3.1-8B-Instruct on a single H100 GPU with batch size 1, baselines run through the Spec-Bench codebase. Speedup is the ratio of wall-clock time-per-output-token relative to vanilla decoding.[^oliaroSuffixDecodingExtremeSpeculative2024]

| Workload | Speedup | Mean accepted tokens (tokens/step) | Speculation time per generated token (ms) | Mean acceptance rate |
|---|---|---|---|---|
| [Spec-Bench](../benchmarks/spec-bench.md) | 2.367 | 4.647 | 2.634 | 0.061 |
| AgenticSQL | 1.623 | 3.160 | 4.854 | 0.036 |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

- Spec-Bench per-category speedup for eagle3 ranges from 1.447 (translation) to 3.115 (coding).[^oliaroSuffixDecodingExtremeSpeculative2024]
- On AgenticSQL, eagle3 (1.623) is below eagle2 (1.864). On Spec-Bench, eagle3 (2.367) is above eagle2 (1.825).[^oliaroSuffixDecodingExtremeSpeculative2024]
- EAGLE-2/3 failed to run on several SWE-Bench tasks due to long context lengths (>8192 tokens).[^oliaroSuffixDecodingExtremeSpeculative2024]

### DPara (Liu et al. 2026)

Batch size 1, greedy decoding, up to 512 new tokens, draft length 7, NVIDIA H800. Each cell is speedup over autoregressive decoding / $\tau$. The paper does not state the source of the EAGLE3 weights.[^liuWhenParallelDrafter2026]

| Model | Method | GSM8K | MATH-500 | HumanEval | MBPP | CodeAlpaca | Alpaca | MT-Bench | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B | EAGLE3 | 1.44× / 2.83 | 1.46× / 2.84 | 1.67× / 3.26 | 1.51× / 2.98 | 1.58× / 3.18 | 1.18× / 2.45 | 1.27× / 2.57 | 1.44× / 2.87 |
| Qwen3-8B | SSD-E3 | 1.51× / 2.39 | 1.54× / 2.42 | 1.72× / 2.75 | 1.58× / 2.49 | 1.67× / 2.62 | 1.29× / 2.17 | 1.34× / 2.26 | 1.52× / 2.44 |
| Qwen3-14B | EAGLE3 | 1.76× / 2.94 | 1.74× / 2.93 | 2.01× / 3.35 | 1.80× / 3.04 | 1.86× / 3.24 | 1.42× / 2.42 | 1.51× / 2.57 | 1.73× / 2.93 |
| Qwen3-14B | SSD-E3 | 1.76× / 2.48 | 1.80× / 2.48 | 2.02× / 2.80 | 1.82× / 2.54 | 1.91× / 2.68 | 1.48× / 2.17 | 1.57× / 2.28 | 1.77× / 2.49 |

All rows: [^liuWhenParallelDrafter2026]

### Aurora (Wang et al. 2026)

Aurora uses EAGLE-3 as its speculative decoding framework in SGLang, with Qwen3-8B on H100 GPUs, 5 speculative steps, top-$k$ sampling 1, and 6 draft tokens per step. On mixed traffic the static baseline has an acceptance length of 2.63 and the pretrained-then-finetuned baseline 2.99. Under an ordered domain shift, the pretrained static speculator has an acceptance length of 2.57 and 288.8 tokens/s.[^wangWhenRLMeets2026]

## Papers using it

- [EAGLE-3 paper](../papers/liEAGLE3ScalingInference2025.md): proposes the method. See "Original results".[^liEAGLE3ScalingInference2025]
- [DFlash](../papers/chenDFlashBlockDiffusion2026.md) ([method page](../methods/dflash.md)): the main baseline. DFlash reports an average 4.9× speedup under greedy decoding on Qwen3, a 2.4× improvement over EAGLE-3 (16). It contrasts its [KV injection](../methods/kv-injection.md) with EAGLE-3's input fusion, where the target information is diluted as drafter depth grows.[^chenDFlashBlockDiffusion2026]
- [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) ([method page](../methods/dspark.md)): the autoregressive baseline. DSpark improves the macro-average accepted length over Eagle3 by 30.9%, 26.7%, and 30.0% on Qwen3-4B, 8B, and 14B.[^chengDSparkConfidenceScheduledSpeculative2026]
- [LK losses](../papers/samarinLKLossesDirect2026.md): trains EAGLE-3 heads for five target models with KL and LK objectives, and benchmarks public checkpoints.[^samarinLKLossesDirect2026]
- [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): a training framework with full support for EAGLE-3. It reports up to 9.99× faster EAGLE-3 training than the official implementation (Qwen3-235B-A22B) and releases SpecBundle draft models.[^liSpecForgeFlexibleEfficient2026]
- [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md): replaces Eagle3's fixed draft depth and verification size with two RL policies. Eagle3+LTD reaches a mean of 3.92 / 6.56 on L31 8B and 4.32 / 7.00 on V 13B (speedup / $\tau$, temperature 0).[^zhangLearningDraftAdaptive2026]
- [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md) ([method page](../methods/speculative-speculative-decoding.md)): an engine baseline. The paper also discusses combining SSD with EAGLE-3: the SSD draft does not yet have target activations from round $T$, so with lookahead $K$ it conditions on up to $2K$ self-generated tokens, which lowers acceptance on the latter $K$.[^kumarSpeculativeSpeculativeDecoding2026]
- [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md): a baseline, and the fallback speculator of the hybrid mode. The hybrid of SuffixDecoding and EAGLE-3 reaches 2.500 (linear) on Spec-Bench against 2.367 for standalone eagle3.[^oliaroSuffixDecodingExtremeSpeculative2024]
- [DPara](../papers/liuWhenParallelDrafter2026.md): a serial baseline (EAGLE3) and a parallel baseline (SSD-E3).[^liuWhenParallelDrafter2026]
- [Aurora](../papers/wangWhenRLMeets2026.md): trains an EAGLE-3 speculator online from live inference traces, starting from random weights, and hot-swaps it into an SGLang server.[^wangWhenRLMeets2026]

## Strengths & Limitations

Strengths:

- The acceptance rate stays almost unchanged as more of the input comes from the draft model itself, whereas EAGLE's drops significantly (MT-bench, LLaMA-Instruct 3.1 8B, figure only).[^liEAGLE3ScalingInference2025]
- It does not modify the target model's weights and uses strict speculative sampling acceptance conditions, so the original paper does not evaluate generation quality.[^liEAGLE3ScalingInference2025]
- DSpark observes that the autoregressive Eagle3 keeps or increases its conditional acceptance deeper into the block, while the parallel DFlash decays. On Gemma4-12B, Eagle3 has a higher accepted length than DFlash in every benchmark column.[^chengDSparkConfidenceScheduledSpeculative2026]

Limitations:

- Gains shrink as batch size or concurrency grows. In the original vLLM experiment the gain falls to 1.01x at batch size 56.[^liEAGLE3ScalingInference2025] In DFlash's SGLang experiment, EAGLE-3 with 60 draft tokens falls below the baseline (0.9× at concurrency 16 and 0.5× to 0.6× at concurrency 32).[^chenDFlashBlockDiffusion2026]
- Drafting is autoregressive, so drafting cost grows with the number of draft tokens. DFlash states that this caps achievable speedups at approximately 2-3×.[^chenDFlashBlockDiffusion2026] DSpark states that autoregressive drafters like Eagle3 are constrained to shallow networks by their $O(\gamma)$ latency.[^chengDSparkConfidenceScheduledSpeculative2026]
- Training is costly. DFlash describes EAGLE-3's training-time test as costly for long contexts.[^chenDFlashBlockDiffusion2026] SpecForge reports that training-time test with a step length of 7 incurs substantial GPU memory consumption.[^liSpecForgeFlexibleEfficient2026]
- Draft model availability and quality: SpecForge names limited availability of draft models, poor performance of open-source draft models, and a lack of robust training tools as the causes that keep EAGLE-3 underused.[^liSpecForgeFlexibleEfficient2026]
- The static draft tree size is manually tuned. LTD's grid search and learned policies both beat the default configuration.[^zhangLearningDraftAdaptive2026]
- Context length: EAGLE-2/3 failed on SWE-Bench tasks with contexts above 8192 tokens in the Spec-Bench codebase.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The original paper does not test the 405B and 671B models, due to the GPU constraint.[^liEAGLE3ScalingInference2025]

# Contradictions

Later papers report EAGLE-3 speedups well below the original paper. No two papers use exactly the same setting, so each item states what differs.

1. **Ceiling of autoregressive drafting.** The EAGLE-3 paper reports a speedup ratio up to 6.5x and means of 4.12x to 5.51x at temperature 0.[^liEAGLE3ScalingInference2025] DFlash states that autoregressive drafting, as in EAGLE-3, caps achievable speedups at approximately 2-3×, and measures 1.76× to 2.08× on average for EAGLE-3 on Qwen3 at temperature 0.[^chenDFlashBlockDiffusion2026] Setting differences: different target models (Vicuna, LLaMA, DeepSeek-R1-Distill-LLaMA vs Qwen3), different checkpoints (the authors' own vs AngelSlim), and the original hardware is not stated.

2. **LLaMA-3.1-8B-Instruct, temperature 0.** The same target and overlapping tasks give different values:

   | Paper | Setting | MT-Bench | HumanEval | GSM8K |
   |---|---|---|---|---|
   | EAGLE-3 paper | tree, 60 draft tokens, depth 8, Transformers baseline, hardware not stated | 4.40x / 6.13 | 4.85x / 6.74 | 4.48x / 6.23 |
   | LTD | official release, tree, verification size 60, depth 8, A100 | 3.70 / 6.39 | not measured | 3.58 / 6.44 |
   | LK losses | yuhuili checkpoint, chain $K=7$, vLLM v0.11.0, batch size 1 ($\tau$ / speedup) | 3.44 / 2.42 | 4.37 / 3.07 | 3.84 / 2.65 |
   | DFlash | official checkpoint, SGLang Spec-v1, B200, concurrency 1, 60 draft tokens | not measured | 2.0× / 4.65 | 1.9× / 4.55 |
   | SpecForge | existing open-source draft, SGLang, H200, concurrency 8 (speedup only) | 2.39 | 2.52 | 1.26 |

   Rows: [^liEAGLE3ScalingInference2025], [^zhangLearningDraftAdaptive2026], [^samarinLKLossesDirect2026], [^chenDFlashBlockDiffusion2026], [^liSpecForgeFlexibleEfficient2026]. Cells are speedup / $\tau$ unless the row says otherwise.

   LTD's $\tau$ (6.39, 6.44) is close to the original (6.13, 6.23), but its speedup is lower (3.70 vs 4.40x on MT-bench, 3.58 vs 4.48x on GSM8K). The likely cause is hardware and baseline implementation, since LTD uses the official weights and default tree. The engine-based numbers (LK losses, DFlash, SpecForge) have lower $\tau$ as well as lower speedup. Their settings use a chain or a smaller tree, a serving engine baseline that is already optimized, and for SpecForge a concurrency of 8. On Alpaca, LTD (4.26 / 6.93) and the original (4.82x / 6.70) also differ, and DFlash measures 1.8× / 4.07 with 60 draft tokens at concurrency 1.[^zhangLearningDraftAdaptive2026][^liEAGLE3ScalingInference2025][^chenDFlashBlockDiffusion2026]

3. **Spec-Bench style mean for LLaMA-3.1-8B.** SuffixDecoding measures an overall eagle3 speedup of 2.367 with 4.647 mean accepted tokens on Spec-Bench (H100, batch size 1, Spec-Bench codebase).[^oliaroSuffixDecodingExtremeSpeculative2024] The EAGLE-3 paper reports a mean of 4.44x with $\tau$ 6.23 over five tasks for the same target at temperature 0.[^liEAGLE3ScalingInference2025] The task sets differ (13 Spec-Bench categories vs five datasets), and SuffixDecoding does not state the draft tree configuration.

4. **Vicuna-13B and DeepSeek-R1-Distill-LLaMA 8B, temperature 0.** The EAGLE-3 paper reports 5.58x / 6.65 (MT-bench), 5.32x / 6.29 (GSM8K), and 5.16x / 6.17 (Alpaca) for Vicuna 13B.[^liEAGLE3ScalingInference2025] LTD reports 4.48 / 7.22, 4.36 / 6.58, and 4.16 / 6.47 for Vicuna-13B-v1.3 with the official release.[^zhangLearningDraftAdaptive2026] For DeepSeek-R1-Distill-LLaMA 8B the original has 4.05x / 5.58, 5.01x / 6.93, and 3.65x / 5.37 on the same three tasks, and LTD has 3.67 / 5.82, 4.73 / 7.39, and 3.65 / 5.63.[^liEAGLE3ScalingInference2025][^zhangLearningDraftAdaptive2026] LTD's $\tau$ is higher and its speedup is lower or equal. LTD runs on a single A100. The original hardware is not stated.

5. **LLaMA-3.3-70B, temperature 0.** The EAGLE-3 paper reports 4.11x / 5.63 (MT-bench), 4.79x / 6.52 (HumanEval), and 4.34x / 6.15 (GSM8K).[^liEAGLE3ScalingInference2025] LK losses measures the yuhuili checkpoint at $\tau$ / speedup of 3.13 / 2.50, 3.96 / 3.12, and 3.76 / 2.90 (chain $K=7$, vLLM).[^samarinLKLossesDirect2026] SpecForge measures the existing draft at speedups of 2.35, 2.29, and 1.15 (SGLang, 4 GPUs, concurrency 16).[^liSpecForgeFlexibleEfficient2026]

6. **Qwen3 accepted length.** Four papers measure EAGLE-3 on Qwen3 and their $\tau$ values on GSM8K differ by a wide margin:

   | Paper | Checkpoint and setting | Qwen3-8B GSM8K $\tau$ | Qwen3-14B GSM8K $\tau$ |
   |---|---|---|---|
   | DFlash | AngelSlim, tree size 16 / 60, temperature 0 | 3.23 / 3.71 | not measured |
   | DFlash | AngelSlim, tree size 16 / 60, temperature 1 | 3.12 / 3.59 | not measured |
   | DSpark | retrained on 1.3 million PerfectBlend samples, chain of 7, temperature 1.0 | 5.30 | 5.24 |
   | DPara | source of weights not stated, draft length 7, greedy | 2.83 | 2.94 |
   | LTD | AngelSlim, grid-searched tree, temperature 0 | not measured | 3.95 |

   Rows: [^chenDFlashBlockDiffusion2026], [^chenDFlashBlockDiffusion2026], [^chengDSparkConfidenceScheduledSpeculative2026], [^liuWhenParallelDrafter2026], [^zhangLearningDraftAdaptive2026].

   DSpark's retrained Eagle3 has a much higher $\tau$ with a chain at temperature 1.0 than the AngelSlim checkpoint has with a 60-node tree at temperature 0. The likely cause is the checkpoint: DSpark retrains for 10 epochs on 1.3 million samples with target-regenerated responses. The speedups also differ: Qwen3-8B GSM8K is 1.94× to 2.23× in DFlash and 1.44× in DPara, and Qwen3-14B GSM8K is 1.76× in DPara and 2.75 in LTD's grid search.[^chenDFlashBlockDiffusion2026][^liuWhenParallelDrafter2026][^zhangLearningDraftAdaptive2026]

7. **EAGLE-3 vs parallel drafters.** DFlash reports a higher $\tau$ than EAGLE-3 on every Qwen3 benchmark.[^chenDFlashBlockDiffusion2026] DSpark confirms this for Qwen3-4B, 8B, and 14B with all drafters retrained on the same data, but on Gemma4-12B its retrained Eagle3 is above DFlash in every column (for example 5.87 vs 5.45 on GSM8K).[^chengDSparkConfidenceScheduledSpeculative2026] In DFlash's own LLaMA-3.1-8B experiment, EAGLE-3 (60) has a higher average $\tau$ than DFlash (10) on GSM8K (4.55 vs 4.32) and Alpaca (4.07 vs 3.73), while DFlash has the higher speedup.[^chenDFlashBlockDiffusion2026]

8. **EAGLE-3 vs an independent small draft model.** The EAGLE-3 paper reports 5.51x mean speedup for EAGLE-3 against 1.92x for standard speculative sampling (SpS, Vicuna-68M draft) on Vicuna 13B.[^liEAGLE3ScalingInference2025] SSD finds that Llama-3.2-1B outperforms EAGLE-3 as a draft model for Llama-3.1-70B in SGLang (201.9 vs 192.8 tok/s), while in vLLM EAGLE-3 is faster (197.6 vs 136.0 tok/s).[^kumarSpeculativeSpeculativeDecoding2026] DPara measures standard SD with a Qwen3-0.6B draft at 1.83× on Qwen3-14B against 1.73× for EAGLE3.[^liuWhenParallelDrafter2026] The targets, draft models, engines, and hardware all differ.

9. **EAGLE-3 vs EAGLE-2.** The EAGLE-3 paper states that EAGLE-3 achieves the highest speedup on all tasks and target models, with a 20%-40% improvement over EAGLE-2.[^liEAGLE3ScalingInference2025] SuffixDecoding measures eagle3 below eagle2 on AgenticSQL (1.623 vs 1.864 overall).[^oliaroSuffixDecodingExtremeSpeculative2024] AgenticSQL is a proprietary agentic workload that is not in the EAGLE-3 paper's task set.

10. **Size of the training data.** The EAGLE-3 paper describes its training data as ShareGPT with approximately 68K entries and UltraChat-200K with approximately 464K entries.[^liEAGLE3ScalingInference2025] SpecForge describes its reproduction of EAGLE-3 training as using ShareGPT (120K conversations) and UltraChat (200K conversations).[^liSpecForgeFlexibleEfficient2026] The units differ (entries vs conversations), and neither paper explains the difference.

## Related

- Predecessors: [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md)
- Training technique: [Training-time test](../methods/training-time-test.md)
- Parent concept: [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Methods compared against it: [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [PEARL](../methods/pearl.md), [Medusa](../methods/medusa.md), [Multi-token prediction](../methods/multi-token-prediction.md)
- Serving engines: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Benchmarks and datasets: [Spec-Bench](../benchmarks/spec-bench.md), [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [ShareGPT](../datasets/sharegpt.md), [Open-PerfectBlend](../datasets/perfectblend.md)

## Open questions and results

- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)
- [Does speculative decoding still help at large batch sizes?](../questions/speculative-decoding-at-large-batch.md)
- [DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B](../analyses/dflash-dspark-eagle-3-drafting-comparison.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^wangWhenRLMeets2026]: Wang et al. 2026
