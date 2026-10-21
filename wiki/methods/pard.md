---
type: Method
title: PARD
description: Parallel drafter that fine-tunes a small autoregressive language model with mask tokens to predict K draft tokens in one forward pass, target-independent in PARD and dual-mode with confidence-adaptive loss weighting in PARD-2.
tags: [speculative-decoding, parallel-drafting, target-independent-drafting, mask-prediction, draft-model-training, speculative-drafter]
sources:
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# PARD

## Overview

PARD (PARallel Draft) is a [speculative decoding](speculative-decoding.md) drafter built from a small language model of the target's own series, fine-tuned so that mask placeholder tokens let it predict $K$ future tokens in a single forward pass.[^anPARDAcceleratingLLM2025] The original PARD uses no target hidden states, so one drafter serves a whole family of target models.[^anPARDAcceleratingLLM2025] PARD-2 adds target features with a stochastic gate, knowledge distillation, and a confidence-adaptive token loss, and one PARD-2 drafter runs either with or without target features.[^anPARD2TargetAlignedParallel2026]

Both papers come from the same AMD group, and both evaluate on [vLLM](vllm.md) on A100-40GB GPUs.[^anPARDAcceleratingLLM2025][^anPARD2TargetAlignedParallel2026]

## How it works

### Drafting

- With $T_{D}$ the time of one draft forward pass and $T_{T}$ the time of one target pass, vanilla SD predicting $K$ tokens costs $K*T_{D}+T_{T}$ per iteration and PARD costs $T_{D}+T_{T}$.[^anPARDAcceleratingLLM2025]
- PARD replaces the tokens that would create dependencies between draft positions with mask tokens $m_{k}$, so the $K$ predictions are made independently in one pass (Mask-Predict).[^anPARDAcceleratingLLM2025]
- One shared mask token ID for all positions performs better than distinct IDs and lets inference use a larger $K$ than training. With $K_{\text{train}}=8$, decode speed is highest at $K_{\text{infer}}=12$ (231 tokens/s).[^anPARDAcceleratingLLM2025]
- Draft bandwidth consumption stays at 2.48 GB for PARD at $k=4$, 6, and 8, against 5.94, 8.90, and 11.88 GB for EAGLE and EAGLE-3.[^anPARDAcceleratingLLM2025]

### Training (PARD)

- Training is split into $K$ subtasks, one per offset, with an attention mask that matches inference. This raises the training tokens from $N$ to $K\times N$.[^anPARDAcceleratingLLM2025]
- **Conditional Drop-token (COD).** Subtask $i$ keeps $N*\max(r^{i-1},r_{\text{min}})$ tokens, and a token is kept only if all its prefix tokens are kept, so every kept token has complete key and value states. The paper states this cuts training cost from $\mathcal{O}(N\cdot K)$ to $\mathcal{O}(N)$ and improves training efficiency by up to 3$\times$.[^anPARDAcceleratingLLM2025]
- The paper's FLOPs estimate for a 70B target is 20.22 Pflops per 1M tokens for PARD against 149.20 for EAGLE and 204.4 for EAGLE-3. PARD's count includes no target forward pass, because PARD trains without the target.[^anPARDAcceleratingLLM2025]

### Training (PARD-2)

- The expected acceptance length is $\sum_{k}s_{k}a_{k}$, where $s_{k}=\prod_{j<k}a_{j}$ is the chance of reaching position $k$. PARD-2 weights each position's loss by a proxy for $s_{k}$.[^anPARD2TargetAlignedParallel2026]
- **Confidence-Adaptive Token (CAT) optimization.** The proxy is $\hat{s}_{k}=\prod_{j<k}\hat{c}_{j}$, the cumulative product of the target's probability of the ground-truth tokens before position $k$, used as a stop-gradient weight.[^anPARD2TargetAlignedParallel2026] The paper contrasts this with the fixed, position-only decaying weights of DFlash and DART.[^anPARD2TargetAlignedParallel2026]
- The per-position loss is $\hat{s}_{n,k}(\beta\mathcal{L}^{\mathrm{CE}}+\mathcal{L}^{\mathrm{KD}})$ with $\beta=0.1$.[^anPARD2TargetAlignedParallel2026]
- **Stochastic gating.** Features from 4 target layers are fused by a lightweight projection and added to the draft input embeddings with probability $1-\rho$ ($\rho=0.1$), so the drafter also learns to run without them.[^anPARD2TargetAlignedParallel2026]

## Variants

| Variant | Target features | Loss | Source |
|---|---|---|---|
| PARD | none (target-independent) | uniform cross-entropy over the $K$ positions, with COD | [^anPARDAcceleratingLLM2025] |
| PARD-2, target-dependent mode | fused features from 4 target layers added to input embeddings | CAT-weighted CE + KD | [^anPARD2TargetAlignedParallel2026] |
| PARD-2, target-independent mode | none, same drafter | same | [^anPARD2TargetAlignedParallel2026] |

## Papers using it

### PARD paper ([An et al. 2025](../papers/anPARDAcceleratingLLM2025.md))

vLLM, A100-40GB. Each cell is tokens/s / speedup over autoregressive decoding. EAGLE and EAGLE-3 use official checkpoints. The temperature is not stated.[^anPARDAcceleratingLLM2025]

| Target | Method | HumanEval | GSM8K | SpecBench | Avg |
|---|---|---|---|---|---|
| LLaMA3.1-8B | VSD | 155.47 / 2.13 | 140.93 / 1.92 | 106.44 / 1.46 | 134.28 / 1.84 |
| LLaMA3.1-8B | EAGLE | 136.05 / 1.86 | 110.81 / 1.51 | 100.11 / 1.38 | 115.66 / 1.58 |
| LLaMA3.1-8B | EAGLE-3 | 233.43 / 3.19 | 192.56 / 2.62 | 155.58 / 2.14 | 193.86 / 2.65 |
| LLaMA3.1-8B | PARD | 264.88 / 3.63 | 235.09 / 3.20 | 157.49 / 2.17 | 219.15 / 3.00 |
| LLaMA3.3-70B | VSD | 80.78 / 3.32 | 77.07 / 3.18 | 53.09 / 2.22 | 70.31 / 2.91 |
| LLaMA3.3-70B | EAGLE-3 | 95.17 / 3.91 | 75.34 / 3.10 | 63.14 / 2.64 | 77.88 / 3.22 |
| LLaMA3.3-70B | PARD | 99.88 / 4.11 | 95.58 / 3.94 | 57.41 / 2.40 | 84.29 / 3.49 |

All rows: [^anPARDAcceleratingLLM2025]

- The paper's text states a 3.67$\times$ speedup for the 264.88 tokens/s result, while its table lists 3.63 for the same cell.[^anPARDAcceleratingLLM2025]
- Acceptance rate at the first draft position on LLaMA3.1-8B: EAGLE 0.83 / 0.79, EAGLE-3 0.87 / 0.82, PARD 0.93 / 0.88 (HumanEval / GSM8K).[^anPARDAcceleratingLLM2025]
- Speedup by batch size on LLaMA3.1-8B HumanEval, batch sizes 1, 2, 4, 8, 16: PARD 3.63, 3.16, 2.59, 1.90, 1.33; VSD 2.13, 2.03, 1.88, 1.61, 1.41; EAGLE 1.86, 1.69, 1.69, 1.44, 1.19.[^anPARDAcceleratingLLM2025]

### PARD-2 paper ([An et al. 2026](../papers/anPARD2TargetAlignedParallel2026.md))

vLLM, A100-40GB, temperature 0, tree decoding disabled for all methods. EAGLE-3 uses draft length 8 and the parallel methods 16. Averages over HumanEval, GSM8K, Math-500, and MT-Bench, speedup / $\tau$.[^anPARD2TargetAlignedParallel2026]

| Target | EAGLE-3 | DFlash | PARD | PARD-2 (target-dependent) | PARD-2 (target-independent) |
|---|---|---|---|---|---|
| Qwen3-8B | 1.93 / 2.37 | 4.61 / 5.58 | 4.39 / 5.56 | 5.81 / 6.98 | 4.82 / 6.14 |
| Qwen3-14B | 2.06 / 2.46 | not reported | 4.51 / 5.14 | 5.81 / 6.91 | 4.79 / 6.03 |
| Llama3.1-8B | 2.76 / 3.89 | not reported | 4.00 / 5.20 | 5.19 / 6.95 | not reported |
| Qwen3-32B | not reported | not reported | 4.37 / 5.33 | not reported | 4.68 / 5.75 |

All rows: [^anPARD2TargetAlignedParallel2026]

- The highest single result is 6.94$\times$ / 9.19 on HumanEval with Llama3.1-8B.[^anPARD2TargetAlignedParallel2026]
- Loss-weighting ablation, average $\tau$: uniform weights ($\gamma=1.0$) 5.52, fixed decay $\gamma=0.8$ 5.61, $\gamma=0.6$ 5.12, CAT 5.79.[^anPARD2TargetAlignedParallel2026]

### My experiment: [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)

Galaxy S25 NPU drafts with Q4_0 GGUFs, DGX Spark verifies Qwen3-14B-FP8, 60 Spec-Bench requests, temperature 0, 64 new tokens. PARD-1 is `amd/PARD-Qwen3-0.6B`. PARD-2 is `amd/PARD2-Qwen3-14B` in target-dependent mode, with the server projecting target layers 17, 25, and 33 plus the final post-norm from 20480 to 1024 wide.[^drafter-evaluation]

| Drafter | tok/s chain7 / tree16 / own-best | tok/round chain7 / tree16 / own-best | draft ms, tree16 | KB down / token, steady |
|---|---|---|---|---|
| PARD-2 | 24.9 / 29.3 / 30.0 | 3.34 / 4.21 / 4.58 | 29.3 | 2.0 |
| PARD-1 | 22.1 / 26.7 / 26.7 | 2.76 / 3.54 / 3.81 | 22.8 | 0.0 |

All rows: [^drafter-evaluation]

- PARD-2 is the fastest of the six drafters with a tree, and has the lowest TTFT. PARD-1 is the best drafter that needs nothing from the server.[^drafter-evaluation]
- PARD-1 is weak on translation: 2.07–2.81 tok/round against 3.2–4.1 for DFlash and DSpark.[^drafter-evaluation]
- PARD-2's target-independent mode was dropped before the live runs, because the offline oracle gave it 2.0 tok/round as a chain.[^drafter-evaluation] See [the feature-gating question](../questions/pard-2-qwen3-14b-feature-gating.md).

### My experiment: [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md)

The same two checkpoints re-implemented in PyTorch bf16 and drafting as chain7 on the DGX Spark GPU beside the target, with a CUDA graph for the PARD block.[^drafter-evaluation-server-only-chain]

| Drafter | tok/s | tok/round | draft ms | Phone chain7 tok/s |
|---|---|---|---|---|
| PARD-2 | 34.0 | 3.50 | 15.6 | 24.9 |
| PARD-1 | 28.0 | 2.86 | 13.0 | 22.1 |

All rows: [^drafter-evaluation-server-only-chain]

- PARD-2 ties DSpark (33.9) for the fastest server-only chain and has the cheapest draft of the four feature drafters.[^drafter-evaluation-server-only-chain]
- The PARD block graph cut replay draft time from 15.2 to 12.6 ms (PARD-1) and from 18.7 to 15.4 ms (PARD-2).[^drafter-evaluation-server-only-chain]

### My experiment: [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)

Two PARD-1 drafters trained on different backbones with the same 49,872 Qwen3-14B-written answers (K=8, COD, 1 epoch), plus the released drafter, all scored offline by greedy MAT on all 480 Spec-Bench questions against Qwen3-14B references.[^minitron-pard-qwen3-14b]

| Drafter | PARD MAT K=7 | PARD MAT K=8 | First-offset top-1 | Top-1 at offset 7 | Same weights in AR mode, MAT γ=8 |
|---|---|---|---|---|---|
| Pruned Qwen3-14B (0.75B) + chat-KD + PARD-1 | 1.958 | 1.959 | 0.570 | 0.096 | 2.26 |
| Qwen3-0.6B + PARD-1 (control) | 2.655 | 2.663 | 0.751 | 0.159 | 3.55 |
| amd/PARD-Qwen3-0.6B (released) | 3.031 | 3.07 | 0.752 | 0.264 | 3.55 |

All rows: [^minitron-pard-qwen3-14b]

- The PARD stage passes the backbone's first-token accuracy through: the pruned backbone's AR top-1 is 0.572 and the PARD drafter's first-offset top-1 0.570; for Qwen3-0.6B the numbers are 0.747 and 0.751–0.752.[^minitron-pard-qwen3-14b] See [A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT](../results/pruned-target-pard-drafter-vs-small-model.md).
- The eighth offset is worth 0.001 (pruned), 0.008 (control), and 0.04 (released) MAT. The released drafter at K=16 scores 3.15, with top-1 0.100 at offset 15.[^minitron-pard-qwen3-14b]
- Upstream `pard_train.py` sets pad to the end token, so `<|im_end|>` is never trained.[^minitron-pard-qwen3-14b]

## Strengths & Limitations

- One drafter serves a model family without retraining (PARD, and PARD-2 in target-independent mode).[^anPARDAcceleratingLLM2025][^anPARD2TargetAlignedParallel2026]
- Draft cost does not grow with the number of draft tokens, because all $K$ tokens come from one pass.[^anPARDAcceleratingLLM2025]
- An autoregressive small draft of the same size accepts slightly more at the first position: on LLaMA3.1-8B, VSD with LLaMA3.2-1B has first-token acceptance 0.944 / 0.895 against 0.936 / 0.889 for PARD (Figure 1(a)).[^anPARDAcceleratingLLM2025] In my offline Qwen3-14B evaluation, top-1 against stored greedy references is 0.747 for Qwen3-0.6B as an AR draft and 0.751–0.752 at the first offset of the PARD-1 drafters built on it.[^minitron-pard-qwen3-14b] The metric, target, and backbone differ.
- The gain shrinks with batch size, and at batch size 16 PARD (1.33) is below VSD (1.41) on LLaMA3.1-8B HumanEval.[^anPARDAcceleratingLLM2025] PARD-2 reports a smaller gain at batch size 64 that still beats PARD.[^anPARD2TargetAlignedParallel2026]
- On LLaMA3.3-70B SpecBench, EAGLE-3 (2.64) is above PARD (2.40).[^anPARDAcceleratingLLM2025]
- Training PARD with a longer draft length gives little improvement or degrades performance on several benchmarks, which motivates CAT.[^anPARD2TargetAlignedParallel2026]
- Neither paper reports results at a temperature above 0.

# Contradictions

**How far a PARD drafter can go.** DFlash states that PARD's small models "lack the modeling capacity of the target LLMs, leading to limited acceptance lengths and a speedup ceiling of approximately 3$\times$".[^chenDFlashBlockDiffusion2026] PARD itself reports up to 3.63 (3.00 average) on LLaMA3.1-8B,[^anPARDAcceleratingLLM2025] while PARD-2 measures PARD at an average of 4.39 / $\tau$ 5.56 on Qwen3-8B and 4.51 / 5.14 on Qwen3-14B with draft length 16.[^anPARD2TargetAlignedParallel2026] The settings differ (targets, draft length, benchmarks), so the 3$\times$ figure may describe the original PARD on LLaMA targets rather than a limit. See [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md)

## Related

- [Where Osprey's ideas fit a pruned-target PARD pipeline](../analyses/osprey-ideas-for-pruned-target-pard-pipeline.md)
- [Building a parallel drafter for on-device use without training it from scratch](../analyses/building-parallel-drafters-for-on-device-use.md)
- [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md)
- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md), [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md)
- Papers: [PARD](../papers/anPARDAcceleratingLLM2025.md), [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md)
- Other parallel drafters: [DFlash](dflash.md), [DSpark](dspark.md)
- Compared against: [EAGLE](eagle.md), [EAGLE-3](eagle-3.md), [Medusa](medusa.md)
- Training: [Knowledge distillation](knowledge-distillation.md)
- Serving engine: [vLLM](vllm.md)
- Data: [Magpie](../datasets/magpie.md), [Evol-CodeAlpaca](../datasets/evol-codealpaca.md)
- [Was PARD-2's Qwen3-14B drafter trained to run without target features?](../questions/pard-2-qwen3-14b-feature-gating.md)
- [What the target must supply to train a drafter](../analyses/target-signals-for-drafter-training.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](../questions/cost-efficient-drafter-construction.md)

## Open questions and results

- [Do PARD-2's CAT and KD losses help a drafter trained without target features?](../questions/feature-free-pard-2-losses.md)
- [A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT](../results/pruned-target-pard-drafter-vs-small-model.md)
- [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](../results/block-drafters-vs-ar-drafters-on-phone-npu.md)
- [Does an acceptance-oriented loss help a block diffusion drafter?](../questions/acceptance-oriented-loss-for-block-drafters.md)
- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)
- [Does speculative decoding still help at large batch sizes?](../questions/speculative-decoding-at-large-batch.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
