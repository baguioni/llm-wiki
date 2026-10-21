---
type: Paper
title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
description: Extends the PARD parallel drafter with Confidence-Adaptive Token (CAT) loss weighting from the target's cumulative prefix confidence, target hidden features, and knowledge distillation, with stochastic gating so one drafter runs in target-dependent or target-independent mode.
tags: [speculative-decoding, parallel-drafting, draft-model, training-objective, knowledge-distillation, target-independent-drafter, vllm, speculative-drafter]
collections: ["speculative drafter"]
authors: [Zihao An, Taichi Liu, Ziqiong Liu, Dong Li, Ruofeng Liu, Emad Barsoum]
doi: 10.48550/arXiv.2605.08632
arxiv: "2605.08632"
arxiv_version: 2605.08632v1
code: https://github.com/AMD-AGI/PARD
sources:
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
---

# PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding

Text source: arXiv HTML, version `2605.08632v1`.

## Summary

[PARD](anPARDAcceleratingLLM2025.md) is a parallel drafter for [speculative decoding](../methods/speculative-decoding.md) that keeps an auto-regressive backbone and predicts $K$ future tokens in one forward pass from the prefix plus mask placeholders. It does not depend on the target, so one drafter can serve a family of target models.[^anPARD2TargetAlignedParallel2026] The authors observe that later draft positions have lower acceptance rates, and that training PARD with a longer draft length gives little improvement or even degrades performance on several benchmarks.[^anPARD2TargetAlignedParallel2026] They argue that the cause is a training objective that weights all positions equally, while a token only counts if every earlier token in the block is accepted.[^anPARD2TargetAlignedParallel2026]

[PARD-2](../methods/pard.md) changes the training in three ways. [Confidence-Adaptive Token (CAT) optimization](../methods/pard.md) weights each token's loss by the cumulative product of the target model's confidence on the preceding ground-truth tokens. Target hidden features are added to the draft input embeddings. A [knowledge distillation](../methods/knowledge-distillation.md) term is added to the cross-entropy loss.[^anPARD2TargetAlignedParallel2026] The target features are injected through a stochastic gate during training, so the same drafter runs with target features (target-dependent mode) or without them (target-independent mode).[^anPARD2TargetAlignedParallel2026]

In target-dependent mode at temperature 0 on [vLLM](../methods/vllm.md), PARD-2 reaches an average speedup of 5.81$\times$ on Qwen3-8B (PARD 4.39$\times$, [DFlash](../methods/dflash.md) 4.61$\times$, [EAGLE-3](../methods/eagle-3.md) 1.93$\times$), 5.81$\times$ on Qwen3-14B, and 5.19$\times$ on Llama3.1-8B. The highest single result is 6.94$\times$ on HumanEval with Llama3.1-8B.[^anPARD2TargetAlignedParallel2026] The abstract summarizes this as up to 6.94$\times$ lossless acceleration, surpassing EAGLE-3 by 1.9$\times$ and PARD by 1.3$\times$ on Llama3.1-8B.[^anPARD2TargetAlignedParallel2026]

## Contributions

- A dual-mode speculative decoding framework that supports target-dependent and target-independent settings with a single draft model. The authors state that, to their knowledge, it is the first work to unify the two paradigms in one draft model.[^anPARD2TargetAlignedParallel2026]
- CAT, a token-level loss reweighting that uses the target model's context-dependent confidence, aimed at maximizing the acceptance of consecutive token spans.[^anPARD2TargetAlignedParallel2026]
- Experiments across models and benchmarks, including validation in vLLM, with an average speedup of 1.3$\times$ over PARD and up to 6.94$\times$ over auto-regressive decoding. The authors also report the highest throughput under high concurrency.[^anPARD2TargetAlignedParallel2026]

## Method

### Background: PARD

PARD introduces a mask token $m$ and predicts each future token from the prefix and the preceding mask placeholders: $P(\tilde{Y}\mid X;\boldsymbol{\theta}_{\mathrm{PARD}})=\prod_{k=0}^{K-1}P\!\left(\tilde{y}_{n+k}\mid x_{0},\ldots,x_{n-1},m_{n},\ldots,m_{n+k-1};\boldsymbol{\theta}_{\mathrm{PARD}}\right)$ (Eq. 4). All $K$ predictions come from a single forward pass. PARD is trained with a uniform cross-entropy over the $K$ positions (Eq. 5).[^anPARD2TargetAlignedParallel2026]

### Acceptance-length decomposition

With per-token acceptance probability $a_{k}=\min\!\left(1,\,\frac{p_{k}(\tilde{y}_{n+k})}{q_{k}(\tilde{y}_{n+k})}\right)$ (Eq. 2), and ignoring the bonus token, the expected acceptance length is $\mathbb{E}[L\mid X,\tilde{Y}]=\sum_{k=0}^{K-1}\prod_{j=0}^{k}a_{j}$ (Eq. 3).[^anPARD2TargetAlignedParallel2026] Defining $s_{k}:=\prod_{j=0}^{k-1}a_{j}$ with $s_{0}:=1$ (Eq. 7) gives $\mathbb{E}[L\mid X,\tilde{Y}]=\sum_{k=0}^{K-1}s_{k}a_{k}$ (Eq. 8). The paper reads $s_{k}$ as the importance of position $k$ for acceleration, and $a_{k}$ as the local quality of the draft prediction, which the token-level training loss already targets. This motivates reweighting the per-token loss by $s_{k}$.[^anPARD2TargetAlignedParallel2026]

### Confidence-Adaptive Token (CAT) optimization

- The true $a_{k}$ is intractable during training because it depends on the interaction between draft and target at verification.[^anPARD2TargetAlignedParallel2026]
- Following EAGLE-2 and CAPE, the authors measure the relation between target-model confidence and token acceptance rate on HumanEval, GSM8K, and Math-500 (Figure 2(b), Llama3.1-8B), and report a strong positive correlation. They use target confidence as a proxy for acceptance.[^anPARD2TargetAlignedParallel2026]
- The proxy is the target's probability of the ground-truth token given its prefix, $\hat{c}_{k}:=P\!\left(y_{n+k}\mid x_{0},\ldots,x_{n-1},y_{n},\ldots,y_{n+k-1};\boldsymbol{\theta}_{\mathrm{target}}\right)$ (Eq. 9), and the weight is its cumulative product $\hat{s}_{k}:=\prod_{j=0}^{k-1}\hat{c}_{j}$, $\hat{s}_{0}:=1$ (Eq. 10). $\hat{s}_{k}$ approximates the probability that position $k$ is reached during verification.[^anPARD2TargetAlignedParallel2026]
- $\hat{s}_{k}$ is used as a stop-gradient weight: $\mathcal{L}_{\mathrm{PARD\text{-}2}}=-\frac{1}{K}\sum_{k=0}^{K-1}\hat{s}_{k}\log P\!\left(y_{n+k}\mid x_{0},\ldots,x_{n-1},m_{n},\ldots,m_{n+k-1};\boldsymbol{\theta}_{\mathrm{PARD\text{-}2}}\right)$ (Eq. 11). Tokens likely to be in the accepted prefix get more weight, and distant positions that are rarely reached get less.[^anPARD2TargetAlignedParallel2026]
- The paper contrasts CAT with the fixed, position-dependent decaying weights of DFlash and DART: CAT's weight depends on both the position and the prefix content.[^anPARD2TargetAlignedParallel2026]

### Target features with stochastic gating

- Hidden states from multiple target layers ($l$, $m$, $h$ for low-, middle-, and high-level features) are fused as $t=\mathrm{Proj}([l;m;h])$, where $\mathrm{Proj}(\cdot)$ is a lightweight projection module, and added to the draft input embeddings $e^{d}$.[^anPARD2TargetAlignedParallel2026] The implementation extracts features from 4 target layers.[^anPARD2TargetAlignedParallel2026]
- The draft input is also processed with Conditional Drop Token (COD) from PARD, which selectively drops conditional tokens during training to improve training efficiency.[^anPARD2TargetAlignedParallel2026]
- Stochastic gating: $e^{d^{\prime}}=e^{d}+\xi\cdot t$, $\xi\sim\mathrm{Bernoulli}(1-\rho)$. So $e^{d^{\prime}}=e^{d}$ with probability $\rho$, and $e^{d}+t$ otherwise. This reduces dependence on the target so one drafter can serve the whole model family.[^anPARD2TargetAlignedParallel2026]
- The paper contrasts PARD-2's standalone architecture with EAGLE-3 and DFlash, which it describes as requiring grafted layers.[^anPARD2TargetAlignedParallel2026]

### Training loss

For the $k$-th future position the loss is $\mathcal{L}_{k}=\sum_{n=1}^{N-k}\hat{s}_{n,k}\left(\beta\mathcal{L}^{\mathrm{CE}}_{n,k}+\mathcal{L}^{\mathrm{KD}}_{n,k}\right)$ (Eq. 12), where $\hat{s}_{n,k}$ is the confidence-adaptive weight of token $x_{n+k}$ given prefix $x_{\leq n}$, and $\beta$ balances the supervised and distillation terms.[^anPARD2TargetAlignedParallel2026] The text does not give the exact form of $\mathcal{L}^{\mathrm{KD}}$.

### Dual-mode inference

- During prefill, hidden states are extracted from multiple target layers. The hidden state at the last prompt token position is fused with the mask token, to keep the conditioning consistent with training.[^anPARD2TargetAlignedParallel2026]
- Target-dependent mode uses the target hidden features for maximum acceleration. Target-independent mode runs without them and works across the target model family without retraining. Both modes use the same draft model, with no architectural change or additional fine-tuning.[^anPARD2TargetAlignedParallel2026]

## Experiments & Results

### Setup

- Target-dependent mode: PARD-2 is trained and evaluated on Llama-3.1-8B, Qwen3-8B, and Qwen3-14B. Target-independent mode is evaluated mainly on the Qwen3 family.[^anPARD2TargetAlignedParallel2026]
- Training data: an expanded version of the PARD dataset. It keeps [Magpie](../datasets/magpie.md) and [Evol-CodeAlpaca](../datasets/evol-codealpaca.md) and adds samples from Nemotron-v2 and Nemotron-v3.[^anPARD2TargetAlignedParallel2026]
- Evaluation benchmarks: [HumanEval](../datasets/humaneval.md) (code), [MATH-500](../datasets/math-500.md) and [GSM8K](../datasets/gsm8k.md) (math), and [MT-Bench](../datasets/mt-bench.md) (multi-turn dialogue).[^anPARD2TargetAlignedParallel2026]
- Metrics: speedup over vanilla auto-regressive decoding, acceptance length $\tau$ (the average number of draft tokens accepted in each verification), and tokens per second.[^anPARD2TargetAlignedParallel2026]
- Training: AMD MI300X GPUs, batch size 64, draft length $K=16$, $\rho=0.1$, $\beta=0.1$.[^anPARD2TargetAlignedParallel2026]
- Inference: all throughput evaluations run on vLLM. [Tree-based decoding](../methods/tree-based-speculation.md) is disabled for all methods. Unless stated otherwise, evaluation runs on NVIDIA A100-40GB GPUs, with TP=2 for Qwen3-32B and TP=1 for all other models.[^anPARD2TargetAlignedParallel2026]
- Qwen3 and Llama3 run with thinking mode disabled. Main results use greedy decoding (temperature 0).[^anPARD2TargetAlignedParallel2026]
- Baselines: EAGLE-3, DFlash, and PARD. For Qwen3, EAGLE-3 uses third-party trained weights (Tencent AngelSlim). All other baselines and PARD-2 use official weights. EAGLE-3 uses an inference draft length of $K=8$, which the authors call its optimal open-source configuration. All other methods use $K=16$.[^anPARD2TargetAlignedParallel2026]

### Training hyperparameters (Table 6)

| Hyperparameter | Llama3.1-8B | Qwen3-8B | Qwen3-14B |
|---|---|---|---|
| Optimizer | AdamW | AdamW | AdamW |
| Learning rate | 1e-5 | 3e-5 | 3e-5 |
| Per-device train batch size | 8 | 4 | 4 |
| Gradient accumulation steps | 1 | 2 | 2 |
| Num processes | 8 | 8 | 8 |
| Num train epochs | 4 | 2 | 2 |
| Training draft length K | 16 | 16 | 16 |
| Stochastic gating ratio $\rho$ | 0.1 | 0.1 | 0.0 |
| CE loss coefficient $\beta$ | 0.1 | 0.1 | 0.1 |
| Max seq length | 512 | 1024 | 1024 |

All rows: [^anPARD2TargetAlignedParallel2026]

### Target-dependent mode (Table 1, temperature 0)

Speedup over AR / acceptance length $\tau$. The inference draft length is in parentheses. AR is 1.00 / 1.00 everywhere.

| Target | Method | HumanEval | GSM8K | Math-500 | MT-Bench | Average |
|---|---|---|---|---|---|---|
| Qwen3-8B | EAGLE-3 (8) | 2.11 / 2.68 | 1.98 / 2.44 | 1.90 / 2.32 | 1.71 / 2.05 | 1.93 / 2.37 |
| Qwen3-8B | DFlash (16) | 5.66 / 6.94 | 4.64 / 5.39 | 5.59 / 6.88 | 2.57 / 3.10 | 4.61 / 5.58 |
| Qwen3-8B | PARD (16) | 5.02 / 6.33 | 4.91 / 6.01 | 4.96 / 6.12 | 2.68 / 3.79 | 4.39 / 5.56 |
| Qwen3-8B | PARD-2 (16) | 6.75 / 8.09 | 6.44 / 7.68 | 6.87 / 8.27 | 3.16 / 3.89 | 5.81 / 6.98 |
| Qwen3-14B | EAGLE-3 (8) | 2.32 / 2.86 | 2.10 / 2.50 | 2.09 / 2.49 | 1.72 / 1.97 | 2.06 / 2.46 |
| Qwen3-14B | PARD (16) | 5.16 / 5.25 | 5.10 / 6.09 | 4.98 / 5.95 | 2.78 / 3.26 | 4.51 / 5.14 |
| Qwen3-14B | PARD-2 (16) | 6.74 / 7.95 | 6.40 / 7.65 | 6.73 / 8.07 | 3.37 / 3.96 | 5.81 / 6.91 |
| Llama3.1-8B | EAGLE-3 (8) | 3.34 / 4.55 | 2.80 / 3.97 | 2.37 / 3.42 | 2.54 / 3.60 | 2.76 / 3.89 |
| Llama3.1-8B | PARD (16) | 5.09 / 6.71 | 4.20 / 5.43 | 3.84 / 5.08 | 2.85 / 3.57 | 4.00 / 5.20 |
| Llama3.1-8B | PARD-2 (16) | 6.94 / 9.19 | 5.21 / 6.98 | 5.36 / 7.40 | 3.25 / 4.22 | 5.19 / 6.95 |

All rows: [^anPARD2TargetAlignedParallel2026]

- PARD-2 has the highest speedup and $\tau$ in every cell of Table 1.[^anPARD2TargetAlignedParallel2026]
- DFlash is reported only for Qwen3-8B.[^anPARD2TargetAlignedParallel2026]
- The authors note that PARD-2 keeps strong performance on MT-Bench, and read this as a sign that its benefits extend beyond structured reasoning and coding.[^anPARD2TargetAlignedParallel2026]

### Target-independent mode (Table 2, temperature 0)

One drafter for all three Qwen3 targets. Speedup / $\tau$, inference draft length 16. AR is 1.00 / 1.00 everywhere.

| Target | Method | HumanEval | GSM8K | Math-500 | MT-Bench | Average |
|---|---|---|---|---|---|---|
| Qwen3-8B | PARD | 5.02 / 6.33 | 4.91 / 6.01 | 4.96 / 6.12 | 2.68 / 3.79 | 4.39 / 5.56 |
| Qwen3-8B | PARD-2 | 5.71 / 7.38 | 5.20 / 6.56 | 5.63 / 7.23 | 2.74 / 3.39 | 4.82 / 6.14 |
| Qwen3-14B | PARD | 5.16 / 5.25 | 5.10 / 6.09 | 4.98 / 5.95 | 2.78 / 3.26 | 4.51 / 5.14 |
| Qwen3-14B | PARD-2 | 5.63 / 7.16 | 5.28 / 6.61 | 5.50 / 6.97 | 2.76 / 3.37 | 4.79 / 6.03 |
| Qwen3-32B | PARD | 5.18 / 6.46 | 4.90 / 5.99 | 4.76 / 5.83 | 2.64 / 3.05 | 4.37 / 5.33 |
| Qwen3-32B | PARD-2 | 5.71 / 7.12 | 5.10 / 6.24 | 5.25 / 6.47 | 2.67 / 3.15 | 4.68 / 5.75 |

All rows: [^anPARD2TargetAlignedParallel2026]

- In the text, the average speedup rises from 4.38$\times$ to 4.82$\times$ on Qwen3-8B, from 4.38$\times$ to 4.79$\times$ on Qwen3-14B, and from 4.37$\times$ to 4.68$\times$ on Qwen3-32B, and the average $\tau$ rises from 5.41 to 5.97.[^anPARD2TargetAlignedParallel2026] The PARD averages in Table 2 for Qwen3-8B and Qwen3-14B are 4.39 and 4.51, which differ from the text.[^anPARD2TargetAlignedParallel2026]
- In two cells PARD-2 is below PARD: MT-Bench $\tau$ on Qwen3-8B (3.39 vs. 3.79) and MT-Bench speedup on Qwen3-14B (2.76 vs. 2.78).[^anPARD2TargetAlignedParallel2026]
- The PARD rows for Qwen3-8B and Qwen3-14B are identical to the PARD rows in Table 1.[^anPARD2TargetAlignedParallel2026]
- The authors conclude that stochastic gating reduces over-reliance on target-specific hidden states and that CAT stays effective without target features.[^anPARD2TargetAlignedParallel2026]

### Large batch sizes (Figure 1, vLLM)

- Figure 1 plots TPS/GPU against TPS/User for batch sizes 1 to 64, for Baseline, EAGLE-3, PARD, and PARD-2 on Llama-3.1-8B, and additionally DFlash on Qwen3-8B. PARD-2's frontier lies above and to the right of the others at every plotted batch size.[^anPARD2TargetAlignedParallel2026]
- At batch size 64 the speedup gain is smaller because of higher GPU utilization, but PARD-2 still outperforms PARD on both Llama-3-8B and Qwen3-8B.[^anPARD2TargetAlignedParallel2026]
- The figure gives no numeric labels, so exact values are not recorded here.

### Position-wise acceptance (Figure 2(a), Llama3.1-8B, HumanEval)

PARD's per-position acceptance rate falls at later positions of the 16-token block, while PARD-2's stays roughly flat, and PARD-2's cumulative acceptance length keeps growing over the block where PARD's levels off. The paper describes this as PARD-2 mitigating distant-position degradation.[^anPARD2TargetAlignedParallel2026] The figure gives no numeric labels.

### Ablations

All ablation models are trained for 30k steps on MI300X GPUs.[^anPARD2TargetAlignedParallel2026] The text does not name the target model for the ablations.

**Fixed decay vs. CAT (Table 3).** The fixed decay weight is $\gamma_{t}=\gamma^{t-1}$, the position-wise heuristic of DFlash and DART.[^anPARD2TargetAlignedParallel2026]

| Weighting | HumanEval | GSM8K | MT-Bench | Average |
|---|---|---|---|---|
| $\gamma=1.0$ | 5.52 / 7.45 | 4.22 / 5.58 | 2.67 / 3.54 | 4.14 / 5.52 |
| $\gamma=0.8$ | 5.61 / 7.56 | 4.33 / 5.67 | 2.74 / 3.60 | 4.23 / 5.61 |
| $\gamma=0.6$ | 4.89 / 6.58 | 3.99 / 5.21 | 2.72 / 3.58 | 3.87 / 5.12 |
| CAT (ours) | 5.86 / 7.90 | 4.43 / 5.79 | 2.79 / 3.67 | 4.36 / 5.79 |

Speedup / $\tau$. All rows: [^anPARD2TargetAlignedParallel2026]

The paper states that position-wise decay peaks at $\tau$ 5.61 at $\gamma=0.8$, is highly sensitive to the decay rate, and fails to generalize across tasks, while CAT weights by both the token and its prefix.[^anPARD2TargetAlignedParallel2026]

**Stochastic gating ratio (Table 4).**

| Gate ratio | HumanEval | GSM8K | MT-Bench | Average |
|---|---|---|---|---|
| w/o | 6.10 / 8.28 | 4.66 / 6.17 | 2.88 / 3.86 | 4.55 / 6.10 |
| $\rho$ = 0.5 | 5.96 / 8.15 | 4.55 / 6.01 | 2.85 / 3.80 | 4.45 / 5.99 |
| $\rho$ = 0.2 | 5.99 / 8.18 | 4.66 / 6.12 | 2.85 / 3.80 | 4.50 / 6.03 |
| $\rho$ = 0.1 | 6.02 / 8.19 | 4.68 / 6.13 | 2.88 / 3.85 | 4.53 / 6.06 |

Speedup / $\tau$. All rows: [^anPARD2TargetAlignedParallel2026]

The table caption calls $\rho$ = 0.1 optimal.[^anPARD2TargetAlignedParallel2026] The text says the fully injected baseline reaches $\tau=5.62$ and $\rho=0.1$ reaches $\tau=5.60$, and that $\rho=0.1$ raises MT-Bench from 3.79 to 3.84, reading mild gating as a regularizer. These numbers do not appear in Table 4, where the averages are 6.10 and 6.06 and MT-Bench $\tau$ is 3.86 and 3.85.[^anPARD2TargetAlignedParallel2026]

**Component breakdown (Table 5).**

| Method | $k_{train}$ | $k_{infer}$ | HumanEval | GSM8K | MT-Bench | Average |
|---|---|---|---|---|---|---|
| PARD | 8 | 8 | 4.71 / 5.90 | 3.89 / 4.78 | 2.75 / 3.42 | 3.78 / 4.70 |
| PARD + Target Feat | 8 | 8 | 4.92 / 6.18 | 4.18 / 5.12 | 2.88 / 3.57 | 3.99 / 4.96 |
| PARD + Target Feat | 16 | 8 | 4.76 / 6.00 | 4.11 / 5.02 | 2.80 / 3.46 | 3.89 / 4.83 |
| PARD + Target Feat + CAT | 16 | 8 | 4.94 / 6.19 | 4.24 / 5.15 | 2.93 / 3.60 | 4.04 / 4.98 |
| PARD + Target Feat + CAT | 16 | 16 | 5.86 / 7.90 | 4.41 / 5.79 | 2.79 / 3.67 | 4.35 / 5.79 |
| PARD + Multi-layer Target Feat + CAT | 16 | 16 | 5.89 / 7.93 | 4.41 / 5.80 | 2.86 / 3.79 | 4.37 / 5.84 |

Speedup / $\tau$. All rows: [^anPARD2TargetAlignedParallel2026]

- Target features raise average $\tau$ from 4.70 to 4.96, with larger gains on reasoning and code generation.[^anPARD2TargetAlignedParallel2026]
- Training with $k_{train}=16$ instead of 8, without CAT, lowers average $\tau$ from 4.96 to 4.83 at $k_{infer}=8$. The authors use this to motivate CAT.[^anPARD2TargetAlignedParallel2026]
- With $k_{infer}=16$, CAT raises $\tau$ from 4.83 to 5.79 according to the text. That comparison also changes $k_{infer}$ from 8 to 16. At a fixed $k_{infer}=8$, adding CAT moves $\tau$ from 4.83 to 4.98.[^anPARD2TargetAlignedParallel2026]

## Limitations

The paper has no limitations section. The points below are stated in the text or follow directly from its setup.

- The speedup gain at batch size 64 is smaller than at small batch, which the authors attribute to higher GPU utilization.[^anPARD2TargetAlignedParallel2026]
- Tree-based decoding is disabled for all methods, and EAGLE-3 runs a chain of $K=8$ while the parallel methods use $K=16$. On Qwen3, EAGLE-3 uses third-party weights.[^anPARD2TargetAlignedParallel2026]
- All reported results use greedy decoding with thinking mode disabled. No results at temperature above 0 are given.[^anPARD2TargetAlignedParallel2026]
- DFlash is compared only on Qwen3-8B, and only in target-dependent mode.[^anPARD2TargetAlignedParallel2026]
- The text does not give the drafter's size or number of layers, the form of the KD loss, or the target model used in the ablations.[^anPARD2TargetAlignedParallel2026]
- Table 6 lists $\rho=0.0$ for Qwen3-14B, while the implementation details state $\rho=0.1$.[^anPARD2TargetAlignedParallel2026]
- Several numbers in the text disagree with the tables (target-independent PARD averages, the stochastic-gating $\tau$ values). Section 4.3 also cites Table 4 for the fixed-decay comparison, which is in Table 3.[^anPARD2TargetAlignedParallel2026]

## Related

- Methods: [PARD-2](../methods/pard.md), [PARD](../methods/pard.md), [Confidence-Adaptive Token optimization](../methods/pard.md), [Speculative decoding](../methods/speculative-decoding.md), [Knowledge distillation](../methods/knowledge-distillation.md)
- Systems compared or cited: [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [EAGLE-2](../methods/eagle-2.md), [Medusa](../methods/medusa.md), [DistillSpec](../methods/distillspec.md), [PEARL](../methods/pearl.md), [SpecInfer](../methods/specinfer.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md), [vLLM](../methods/vllm.md)
- Datasets: [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md), [MT-Bench](../datasets/mt-bench.md), [Magpie](../datasets/magpie.md), [Evol-CodeAlpaca](../datasets/evol-codealpaca.md), [Nemotron Post-Training Dataset](../datasets/nemotron-post-training.md)
- Papers in this wiki cited by this paper: [PARD](anPARDAcceleratingLLM2025.md), [DFlash](chenDFlashBlockDiffusion2026.md), [EAGLE-3](liEAGLE3ScalingInference2025.md), [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md), [Speculative Speculative Decoding](kumarSpeculativeSpeculativeDecoding2026.md)
- Other papers in this wiki on drafter training objectives: [LK Losses](samarinLKLossesDirect2026.md), [DSpark](chengDSparkConfidenceScheduledSpeculative2026.md)
- [Was PARD-2's Qwen3-14B drafter trained to run without target features?](../questions/pard-2-qwen3-14b-feature-gating.md)

## Open questions and results

- [Does an acceptance-oriented loss help a block diffusion drafter?](../questions/acceptance-oriented-loss-for-block-drafters.md)
- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)
- [Does speculative decoding still help at large batch sizes?](../questions/speculative-decoding-at-large-batch.md)
- [Why parallel drafters beat EAGLE-3](../analyses/why-parallel-drafters-beat-eagle-3.md)

[^anPARD2TargetAlignedParallel2026]: An et al. 2026
