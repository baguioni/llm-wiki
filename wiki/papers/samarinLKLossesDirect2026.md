---
type: Paper
title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
description: Training objectives for speculative decoding draft models that optimize the acceptance rate directly, as a negative log-acceptance loss or an adaptively blended KL and total variation loss.
tags: [speculative-decoding, draft-model-training, acceptance-rate, total-variation-distance, llm-inference, speculative-drafter]
collections: [speculative drafter]
authors: [Alexander Samarin, Sergei Krutikov, Anton Shevtsov, Sergei Skvortsov, Filipp Fisin, Alexander Golubev]
arxiv: "2602.23881"
arxiv_version: 2602.23881v2
sources:
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
---

# LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding

Text source: arXiv HTML, version `2602.23881v2`.

## Summary

In [speculative decoding](../methods/speculative-decoding.md), the speedup is largely determined by the acceptance rate, but draft models are usually trained by minimizing Kullback-Leibler (KL) divergence as a proxy objective.[^samarinLKLossesDirect2026] KL divergence and acceptance rate share the same global optimum, but draft models typically have 1-5% of the target model parameters and converge to suboptimal solutions, where minimizing KL does not guarantee maximizing acceptance rate.[^samarinLKLossesDirect2026]

[LK losses](../methods/lk-losses.md) are training objectives that target the acceptance rate directly.[^samarinLKLossesDirect2026] Across four draft architectures and six target models from 8B to 685B parameters, the paper reports consistent improvements in acceptance metrics over KL-based training, with gains of up to 8-10% in average acceptance length.[^samarinLKLossesDirect2026] The authors state that the losses introduce no computational overhead and can be integrated into any existing speculator training framework.[^samarinLKLossesDirect2026]

## Contributions

- Two loss variants for direct acceptance rate optimization in speculative decoding.[^samarinLKLossesDirect2026]
- Consistent improvements in acceptance metrics across target models and draft architectures, which the authors take as evidence that LK losses are model- and architecture-agnostic.[^samarinLKLossesDirect2026]
- Released training datasets (HuggingFace `nebius/infinity-instruct-completions`) and draft model weights (HuggingFace `nebius/lk-speculators`).[^samarinLKLossesDirect2026]

## Method

### Background

A draft model $q$ proposes tokens $x_1,\dots,x_K$ that the target model $p$ verifies in parallel. Each draft token is accepted with probability $\min(1, p(x_i)/q(x_i))$, and the first rejected token discards all later drafts.[^samarinLKLossesDirect2026] The acceptance rate is $\alpha=\sum_{x\in\mathcal{V}}\min(q(x),p(x))$, and it relates to the Total Variation (TV) distance by $\alpha=1-\operatorname{TV}(p,q)$.[^samarinLKLossesDirect2026] Maximizing acceptance is therefore strictly equivalent to minimizing TV, and other divergences are proxy objectives.[^samarinLKLossesDirect2026]

Motivating example: fitting a single Gaussian to a Gaussian mixture gives $\alpha=50.2\%$ with KL divergence, $\alpha=50.8\%$ with reverse KL, and $\alpha=60.2\%$ with TV.[^samarinLKLossesDirect2026]

### Gradient analysis

| Loss | Gradient w.r.t. draft logits $z_q$ | Magnitude for a randomly initialized draft |
|---|---|---|
| Forward KL | $q-p$ | $\mathcal{O}(1/\sqrt{k})$ when $p$ is concentrated on $k$ tokens |
| TV | $\frac{1}{2}q\odot(s-\mathbb{E}_{q}[s])$, with $s_i=\mathrm{sign}(q_i-p_i)$ | $\mathcal{O}(\sqrt{k}/V)$ for vocabulary size $V$ |
| $\mathcal{L}_{\text{LK}}^{\alpha}$ | $\frac{1}{\alpha}\nabla_{z_{q}}\operatorname{TV}(p,q)$ | $1/\sqrt{k}$ in the diffuse-$q$ regime |

All rows: [^samarinLKLossesDirect2026]

The TV gradient depends only on the sign of the error, and the TV loss landscape has non-differentiable points where $q_i=p_i$. With vocabulary sizes exceeding 100k, the TV gradient at initialization is extremely small. The authors conclude that pure TV optimization is impractical for training from random initialization.[^samarinLKLossesDirect2026]

### Hybrid objective $\mathcal{L}_{\text{LK}}^{\lambda}$

$$
\mathcal{L}_{\mathrm{LK}}^{\lambda}(p,q)=\lambda\cdot\operatorname{KL}(p\|q)+(1-\lambda)\cdot\operatorname{TV}(p,q)
$$

- $\lambda=1$ recovers standard KL training and $\lambda=0$ gives pure TV optimization.[^samarinLKLossesDirect2026]
- Adaptive schedule: $\lambda=\exp(-\eta\cdot\mathrm{sg}[\alpha])$ with $\eta>0$, where $\mathrm{sg}[\cdot]$ is the stop-gradient operation. $\lambda$ is computed independently for each draft token position from $\alpha$ aggregated across sequence and batch dimensions.[^samarinLKLossesDirect2026]
- $\lambda\to 1$ when $\alpha\to 0$, and $\lambda$ converges to a small value when $\alpha\to 1$, so training moves from KL-dominated to TV-dominated optimization.[^samarinLKLossesDirect2026]
- The authors interpret it as a trust-region approach: minimize $\operatorname{TV}(p,q)$ subject to $\operatorname{KL}(p\|q)\leq\delta$.[^samarinLKLossesDirect2026]

### Likelihood-based objective $\mathcal{L}_{\text{LK}}^{\alpha}$

$$
\mathcal{L}_{\text{LK}}^{\alpha}(p,q)=-\log\alpha=-\log\sum_{x\in\mathcal{V}}\min(p(x),q(x))
$$

- It performs TV optimization with adaptive gradient scaling. The $1/\alpha$ factor amplifies the gradient when acceptance is low.[^samarinLKLossesDirect2026]
- When $p$ is a point mass, it reduces to the standard negative log-likelihood.[^samarinLKLossesDirect2026]

### Vocabulary truncation

[EAGLE-3](../methods/eagle-3.md) uses a truncated vocabulary for its LM head, as proposed in [FR-Spec](../methods/fr-spec.md). KL divergence is infinite for tokens outside the draft vocabulary, so KL training masks the target logits and optimizes $\mathrm{KL}(\tilde{p}\|q)$ instead of $\mathrm{KL}(p\|q)$.[^samarinLKLossesDirect2026] Tokens outside the draft vocabulary contribute $\min(p_i,0)=0$ to the acceptance rate, so $\mathcal{L}_{\text{LK}}^{\alpha}$ and the TV component of $\mathcal{L}_{\text{LK}}^{\lambda}$ need no modification of $p$.[^samarinLKLossesDirect2026]

## Experiments & Results

### Setup

- Target models: Llama-3.1-8B-Instruct, Llama-3.3-70B-Instruct, gpt-oss-20b, gpt-oss-120b, Qwen3-235B-A22B-Instruct, and DeepSeek-V3.[^samarinLKLossesDirect2026]
- Draft models: for Llama-3.1-8B, [EAGLE-3](../methods/eagle-3.md), a multi-stage [MLP speculator](../methods/mlp-speculator.md), and [MEDUSA](../methods/medusa.md). For Llama-3.3-70B, gpt-oss, and Qwen3, only EAGLE-3. For DeepSeek-V3, the native [Multi-Token Prediction](../methods/multi-token-prediction.md) (MTP) module is fine-tuned.[^samarinLKLossesDirect2026]
- All draft architectures are trained with $K=6$ speculative heads. EAGLE-3 heads are a single transformer layer. For MoE target models the block is dense.[^samarinLKLossesDirect2026]
- Training data: 660K prompts from [Infinity-Instruct](../datasets/infinity-instruct.md)-0625 with responses generated by each target model. Input sequence length is 8K.[^samarinLKLossesDirect2026]
- Training: batch size 64, learning rate $4\times 10^{-4}$ with cosine scheduling and 100 warmup steps, AdamW with $(\beta_1,\beta_2)=(0.9,0.95)$, gradient clipping at 0.5, temperature $T=1$. Draft models are trained from scratch for 10 epochs, and the DeepSeek MTP module is fine-tuned for 1 epoch.[^samarinLKLossesDirect2026]
- Default $\eta=3$, with $\eta=10$ for MEDUSA. Losses are aggregated across draft heads with weight $\gamma^{n-1}$ for the $n$-th head, $\gamma=0.8$.[^samarinLKLossesDirect2026]
- Inference: [vLLM](../methods/vllm.md) v0.11.0 with a patch that enables proper rejection sampling at non-zero temperatures. In the original version, draft tokens are sampled greedily regardless of temperature.[^samarinLKLossesDirect2026]
- Evaluation data: full [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), and [GSM8K](../datasets/gsm8k.md), at $T=0$ and $T=1$, with chain sampling instead of tree-based drafting.[^samarinLKLossesDirect2026]
- Metric: average acceptance length $\tau=K\times\frac{\#\text{ accepted tokens}}{\#\text{ drafted tokens}}+1$, which includes the bonus token. EAGLE-3 and DeepSeek-MTP are evaluated with $K=7$, MEDUSA and the MLP speculator with $K=6$.[^samarinLKLossesDirect2026]

### Draft architectures on Llama-3.1-8B-Instruct (Table 1)

Average acceptance length $\tau$.[^samarinLKLossesDirect2026]

| Method | Loss | T=0 MT-Bench | T=0 HumanEval | T=0 GSM8K | T=1 MT-Bench | T=1 HumanEval | T=1 GSM8K |
|---|---|---|---|---|---|---|---|
| EAGLE-3 | KL | 3.75 | 4.82 | 4.50 | 3.39 | 4.31 | 3.88 |
| EAGLE-3 | TV | 2.81 | 3.42 | 3.34 | 2.67 | 3.25 | 3.12 |
| EAGLE-3 | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.77 | 4.82 | 4.55 | 3.50 | 4.48 | 3.98 |
| EAGLE-3 | $\mathcal{L}_{\text{LK}}^{\lambda},\lambda=0.5$ | 3.78 | 4.84 | 4.53 | 3.35 | 4.36 | 3.95 |
| EAGLE-3 | $\mathcal{L}_{\text{LK}}^{\lambda},\eta=0.7$ | 3.79 | 4.88 | 4.54 | 3.53 | 4.45 | 3.98 |
| EAGLE-3 | $\mathcal{L}_{\text{LK}}^{\lambda},\eta=1$ | 3.80 | 4.83 | 4.54 | 3.51 | 4.47 | 3.96 |
| EAGLE-3 | $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 3.84 | 4.89 | 4.57 | 3.48 | 4.52 | 4.02 |
| EAGLE-3 | $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 3.67 | 4.85 | 4.53 | 3.34 | 4.51 | 4.03 |
| MEDUSA | KL | 2.05 | 2.41 | 2.11 | 1.72 | 2.02 | 1.81 |
| MEDUSA | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.06 | 2.42 | 2.11 | 1.78 | 2.09 | 1.85 |
| MEDUSA | $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 2.07 | 2.44 | 2.13 | 1.85 | 2.22 | 1.92 |
| MLP | KL | 2.45 | 2.42 | 2.42 | 2.13 | 2.16 | 2.16 |
| MLP | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.48 | 2.46 | 2.46 | 2.17 | 2.19 | 2.19 |
| MLP | $\mathcal{L}_{\text{LK}}^{\lambda},\eta=3$ | 2.48 | 2.83 | 2.46 | 2.19 | 2.62 | 2.18 |

All rows: [^samarinLKLossesDirect2026]

- With stochastic sampling, MEDUSA and MLP speculators show average improvements of 7.8% and 8.3% respectively across domains, and EAGLE-3 sees 3.8% on average. The authors read this as low-capacity draft models benefiting more from direct optimization of acceptance rate.[^samarinLKLossesDirect2026]
- A constant weight ($\lambda=0.5$) is described as inferior to any other LK setting.[^samarinLKLossesDirect2026]
- Pure TV training performs substantially worse than all other objectives.[^samarinLKLossesDirect2026]

### Target model scale (Table 2)

Average acceptance length $\tau$ for KL against $\mathcal{L}_{\text{LK}}^{\lambda}$ with $\eta=3$. Values in parentheses are the relative improvement (%) over KL. MT: MT-Bench, HE: HumanEval, GSM: GSM8K.[^samarinLKLossesDirect2026]

| Model | Method/Loss | T=0 MT | T=0 HE | T=0 GSM | T=0 Mean | T=1 MT | T=1 HE | T=1 GSM | T=1 Mean |
|---|---|---|---|---|---|---|---|---|---|
| LLaMA 3.1 8B Instruct | EAGLE-3 KL | 3.75 | 4.82 | 4.50 | 4.36 | 3.39 | 4.31 | 3.88 | 3.86 |
| LLaMA 3.1 8B Instruct | EAGLE-3 $\mathcal{L}_{\text{LK}}^{\lambda}$ | 3.84 | 4.89 | 4.57 | 4.43 (+1.6) | 3.48 | 4.52 | 4.02 | 4.01 (+3.9) |
| LLaMA 3.3 70B Instruct | EAGLE-3 KL | 4.01 | 5.18 | 5.16 | 4.78 | 3.76 | 4.86 | 4.89 | 4.50 |
| LLaMA 3.3 70B Instruct | EAGLE-3 $\mathcal{L}_{\text{LK}}^{\lambda}$ | 4.00 | 5.21 | 5.21 | 4.81 (+0.5) | 3.89 | 5.08 | 5.01 | 4.66 (+3.5) |
| GPT-OSS 20B | EAGLE-3 KL | 3.31 | 3.07 | 4.01 | 3.46 | 3.12 | 2.89 | 3.51 | 3.17 |
| GPT-OSS 20B | EAGLE-3 $\mathcal{L}_{\text{LK}}^{\lambda}$ | 3.35 | 3.11 | 4.00 | 3.49 (+0.9) | 3.20 | 3.01 | 3.65 | 3.29 (+3.8) |
| GPT-OSS 120B | EAGLE-3 KL | 2.81 | 2.47 | 3.00 | 2.76 | 2.53 | 2.27 | 2.57 | 2.46 |
| GPT-OSS 120B | EAGLE-3 $\mathcal{L}_{\text{LK}}^{\lambda}$ | 2.86 | 2.51 | 3.06 | 2.81 (+1.8) | 2.69 | 2.44 | 2.81 | 2.65 (+7.7) |
| Qwen3-235B-A22B-Instruct-2507 | EAGLE-3 KL | 3.33 | 4.65 | 4.76 | 4.25 | 2.96 | 4.09 | 4.27 | 3.77 |
| Qwen3-235B-A22B-Instruct-2507 | EAGLE-3 $\mathcal{L}_{\text{LK}}^{\lambda}$ | 3.36 | 4.74 | 4.87 | 4.32 (+1.8) | 3.18 | 4.42 | 4.65 | 4.08 (+8.2) |
| DeepSeek-V3-0324 (685B) | MTP original | 2.90 | 3.28 | 3.41 | 3.20 | 2.82 | 3.17 | 3.27 | 3.09 |
| DeepSeek-V3-0324 (685B) | MTP KL | 3.96 | 4.74 | 5.67 | 4.79 | 3.66 | 4.39 | 5.23 | 4.43 |
| DeepSeek-V3-0324 (685B) | MTP $\mathcal{L}_{\text{LK}}^{\lambda}$ | 4.00 | 4.77 | 5.72 | 4.83 (+0.8) | 3.88 | 4.64 | 5.51 | 4.68 (+5.6) |

All rows: [^samarinLKLossesDirect2026]

- Target models range from 32 layers (Llama-3.1-8B) to 94 layers (Qwen3-235B), while every EAGLE-3 draft is a single dense transformer layer. The largest gains occur for large MoE targets with much smaller dense drafts.[^samarinLKLossesDirect2026]
- For DeepSeek-V3, the released MTP module was trained to predict the first token and is reused autoregressively for later ones. Fine-tuning it with KL improves it substantially, and the LK loss adds an extra 5.6% gain at $T=1$.[^samarinLKLossesDirect2026]

### Wall-clock speedup and public checkpoints (Table 4)

Each cell is $\tau$ / end-to-end speedup relative to decoding without speculative decoding, in a low-latency setting with batch size 1. "Ours" rows are trained from scratch with the given objective. "HF" rows are public HuggingFace checkpoints run through the same inference pipeline (RH = RedHatAI, YH = yuhuili, ZK = zhuyksir, DS = deepseek-ai).[^samarinLKLossesDirect2026]

| Model | Type | Setup | T=0 MT-Bench | T=0 HumanEval | T=0 GSM8K | T=1 MT-Bench | T=1 HumanEval | T=1 GSM8K |
|---|---|---|---|---|---|---|---|---|
| LLaMA 3.1 8B Instruct (EAGLE-3) | Ours | KL | 3.75 / 2.60 | 4.82 / 3.30 | 4.50 / 3.05 | 3.39 / 2.29 | 4.31 / 3.00 | 3.88 / 2.63 |
| | Ours | TV | 2.81 / 1.96 | 3.42 / 2.39 | 3.34 / 2.28 | 2.67 / 1.83 | 3.25 / 2.26 | 3.12 / 2.11 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.77 / 2.61 | 4.82 / 3.28 | 4.55 / 3.07 | 3.50 / 2.30 | 4.48 / 3.03 | 3.98 / 2.72 |
| | Ours | $\mathcal{L}_{\text{LK}}$, $\lambda=0.5$ | 3.78 / 2.63 | 4.84 / 3.32 | 4.53 / 3.07 | 3.35 / 2.36 | 4.36 / 3.03 | 3.95 / 2.68 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=0.7$ | 3.79 / 2.61 | 4.88 / 3.31 | 4.54 / 3.07 | 3.53 / 2.37 | 4.45 / 2.98 | 3.98 / 2.66 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=1$ | 3.80 / 2.64 | 4.83 / 3.33 | 4.54 / 3.08 | 3.51 / 2.30 | 4.47 / 3.01 | 3.96 / 2.70 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.84 / 2.62 | 4.89 / 3.35 | 4.57 / 3.10 | 3.48 / 2.39 | 4.52 / 3.08 | 4.02 / 2.72 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=10$ | 3.67 / 2.53 | 4.85 / 3.33 | 4.53 / 3.06 | 3.34 / 2.30 | 4.51 / 3.01 | 4.03 / 2.72 |
| | HF | RH-8B | 3.08 / 2.09 | 3.90 / 2.65 | 3.57 / 2.37 | 2.67 / 1.83 | 3.36 / 2.31 | 3.08 / 2.05 |
| | HF | YH-8B | 3.44 / 2.42 | 4.37 / 3.07 | 3.84 / 2.65 | 2.97 / 2.22 | 3.75 / 2.50 | 3.21 / 2.14 |
| | HF | ZK-8B | 3.54 / 2.45 | 4.49 / 3.08 | 3.97 / 2.71 | 3.06 / 2.68 | 3.96 / 2.82 | 3.36 / 2.28 |
| LLaMA 3.3 70B Instruct (EAGLE-3) | Ours | KL | 4.01 / 3.01 | 5.18 / 3.87 | 5.16 / 3.78 | 3.76 / 2.82 | 4.86 / 3.66 | 4.89 / 3.61 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.95 / 3.00 | 5.12 / 3.82 | 5.13 / 3.78 | 3.76 / 2.85 | 4.94 / 3.71 | 4.91 / 3.66 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 4.00 / 2.98 | 5.21 / 3.87 | 5.21 / 3.83 | 3.89 / 2.89 | 5.08 / 3.77 | 5.01 / 3.69 |
| | HF | RH-70B | 3.11 / 2.35 | 3.99 / 2.99 | 3.62 / 2.68 | 2.88 / 2.10 | 3.62 / 2.69 | 3.29 / 2.44 |
| | HF | YH-70B | 3.13 / 2.50 | 3.96 / 3.12 | 3.76 / 2.90 | 2.77 / 2.07 | 3.49 / 2.63 | 3.34 / 2.50 |
| GPT-OSS 20B (EAGLE-3) | Ours | KL | 3.31 / 1.41 | 3.08 / 1.32 | 4.01 / 1.63 | 3.12 / 1.30 | 2.89 / 1.20 | 3.51 / 1.44 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.27 / 1.41 | 3.07 / 1.32 | 4.03 / 1.63 | 3.28 / 1.35 | 2.97 / 1.25 | 3.65 / 1.49 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.35 / 1.42 | 3.11 / 1.34 | 4.00 / 1.63 | 3.20 / 1.35 | 3.01 / 1.26 | 3.65 / 1.49 |
| | HF | RH-20B† | 2.90 / 1.26 | 2.70 / 1.17 | 3.49 / 1.45 | 2.63 / 1.12 | 2.43 / 1.04 | 3.00 / 1.26 |
| GPT-OSS 120B (EAGLE-3) | Ours | KL | 2.81 / 1.57 | 2.47 / 1.54 | 3.00 / 1.77 | 2.53 / 1.20 | 2.27 / 1.19 | 2.57 / 1.32 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.80 / 1.59 | 2.51 / 1.57 | 3.08 / 1.82 | 2.67 / 1.49 | 2.39 / 1.45 | 2.78 / 1.63 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 2.86 / 1.62 | 2.51 / 1.60 | 3.06 / 1.82 | 2.69 / 1.48 | 2.44 / 1.48 | 2.81 / 1.66 |
| Qwen 3 235B A22B Instruct (EAGLE-3) | Ours | KL | 3.33 / 2.09 | 4.65 / 2.73 | 4.76 / 2.88 | 2.96 / 1.84 | 4.09 / 2.37 | 4.27 / 2.50 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\alpha}$ | 3.29 / 2.10 | 4.68 / 2.77 | 4.82 / 2.91 | 3.11 / 1.96 | 4.31 / 2.46 | 4.50 / 2.61 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$, $\eta=3$ | 3.36 / 2.13 | 4.74 / 2.78 | 4.87 / 2.93 | 3.18 / 1.98 | 4.42 / 2.52 | 4.65 / 2.68 |
| | HF | RH-235B | 2.92 / 1.85 | 4.06 / 2.42 | 4.31 / 2.63 | 2.56 / 1.61 | 3.52 / 2.06 | 3.78 / 2.22 |
| | HF | ZK-235B‡ | 3.06 / 1.94 | 4.54 / 2.70 | 4.90 / 2.94 | 2.64 / 1.63 | 4.03 / 2.36 | 4.43 / 2.57 |
| DeepSeek V3 0324 (MTP) | Ours | KL | 3.96 / 2.22 | 4.74 / 2.62 | 5.67 / 2.95 | 3.66 / 1.85 | 4.39 / 2.17 | 5.23 / 2.30 |
| | Ours | $\mathcal{L}_{\text{LK}}^{\lambda}$ | 4.00 / 2.22 | 4.77 / 2.64 | 5.72 / 2.97 | 3.88 / 2.14 | 4.64 / 2.42 | 5.51 / 2.71 |
| | HF | DS-685B | 2.90 / 1.66 | 3.28 / 1.84 | 3.41 / 1.82 | 2.82 / 1.54 | 3.17 / 1.59 | 3.27 / 1.47 |

All rows: [^samarinLKLossesDirect2026]

`†` The RH-20B result uses the checkpoint revision available when the experiments were run, before a later weight update. `‡` The ZK-235B checkpoint uses a wider MLP (24,576 vs. 12,288) and a smaller vocabulary (32k vs. 64k), which gives a slightly larger parameter count.[^samarinLKLossesDirect2026]

## Limitations

- The study uses one specific adaptive scheduler for the hybrid objective and a fixed exponential aggregation scheme across draft heads. Other scheduler parameterizations, learnable or data-dependent per-head aggregation, and the sensitivity to the order of aggregation are left to future work.[^samarinLKLossesDirect2026]
- The evaluation uses chain sampling and standard sequential acceptance. Transfer to tree-based sampling and to other verification mechanisms such as block verification is expected by the authors but not verified.[^samarinLKLossesDirect2026]
- The trade-off between training-data diversity and epoch count is not studied.[^samarinLKLossesDirect2026]
- Direct optimization of the acceptance length $\tau$ is left as a future direction.[^samarinLKLossesDirect2026]
- The work covers draft modules integrated into the target model and trained from scratch (plus MTP fine-tuning), not separately pretrained external drafters.[^samarinLKLossesDirect2026]
- At $T=0$ some LK results do not beat KL: for Llama-3.3-70B on MT-Bench, KL gives 4.01 against 4.00 for $\mathcal{L}_{\text{LK}}^{\lambda}$, and for GPT-OSS 20B on GSM8K, KL gives 4.01 against 4.00.[^samarinLKLossesDirect2026]

## Related

- Proposed: [LK losses](../methods/lk-losses.md)
- Builds on: [Speculative decoding](../methods/speculative-decoding.md), [Knowledge distillation](../methods/knowledge-distillation.md), [FR-Spec](../methods/fr-spec.md)
- Draft architectures trained: [EAGLE-3](../methods/eagle-3.md), [MEDUSA](../methods/medusa.md), [MLP speculator](../methods/mlp-speculator.md), [Multi-Token Prediction](../methods/multi-token-prediction.md)
- Related training objectives: [DistillSpec](../methods/distillspec.md)
- Systems: [vLLM](../methods/vllm.md)
- Datasets: [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Infinity-Instruct](../datasets/infinity-instruct.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md)

## Open questions and results

- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^samarinLKLossesDirect2026]: Samarin et al. 2026
