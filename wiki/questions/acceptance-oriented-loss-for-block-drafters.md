---
type: Open Question
title: Does an acceptance-oriented loss help a block diffusion drafter?
description: LK losses raise acceptance for autoregressive and MTP drafters, but no paper isolates their effect on a block diffusion drafter, and the gains at temperature 0 are small.
tags: [speculative-decoding, dflash, draft-model, training-objective, mobile-specedge]
sources:
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
---

# Does an acceptance-oriented loss help a block diffusion drafter?

## Question

Does training a DFlash-style drafter with a loss that targets acceptance rate (a total variation term, or an LK loss) raise its acceptance length over position-weighted cross-entropy, in particular at temperature 0?

## Why it matters

A loss change adds no inference cost, so any gain is free on the phone. The late block positions are where a parallel drafter loses acceptance, and a better objective is one of the few ways to improve them without adding parameters.

## Evidence so far

- DFlash trains with cross-entropy weighted by $w_{k}=\exp\!\left(-\frac{k-1}{\gamma}\right)$ at position $k$ in a block.[^chenDFlashBlockDiffusion2026]
- The acceptance rate is $\alpha=\sum_{x\in\mathcal{V}}\min(q(x),p(x))$ and equals $1-\operatorname{TV}(p,q)$, so maximizing acceptance is equivalent to minimizing total variation distance.[^samarinLKLossesDirect2026]
- LK losses come in two forms: a hybrid $\lambda\cdot\operatorname{KL}(p\|q)+(1-\lambda)\cdot\operatorname{TV}(p,q)$ with an adaptive $\lambda$, and a likelihood form $-\log\alpha$.[^samarinLKLossesDirect2026]
- When $p$ is a point mass, the likelihood form reduces to the standard negative log-likelihood.[^samarinLKLossesDirect2026] **Inference.** On hard token labels it is therefore the same as cross-entropy, and an LK loss only differs when the drafter is trained against the target's full output distribution.
- With stochastic sampling, MEDUSA and MLP speculators improve by 7.8% and 8.3% on average and EAGLE-3 by 3.8%, which the authors read as low-capacity drafts benefiting more.[^samarinLKLossesDirect2026]
- At $T=0$ the mean gains of the hybrid loss over KL for EAGLE-3 are small (+1.6 on LLaMA 3.1 8B, +0.5 on LLaMA 3.3 70B, +0.9 on GPT-OSS 20B), and KL is ahead in two cells (4.01 vs 4.00 on LLaMA 3.3 70B MT-Bench and on GPT-OSS 20B GSM8K).[^samarinLKLossesDirect2026]
- LK losses were tested on EAGLE-3, MEDUSA, MLP speculator, and DeepSeek MTP drafters.[^samarinLKLossesDirect2026]
- DSpark, which builds on DFlash, trains with $\mathcal{L}=\alpha_{\text{ce}}\,\mathcal{L}_{\text{ce}}+\alpha_{\text{tv}}\,\mathcal{L}_{\text{tv}}+\alpha_{\text{conf}}\,\mathcal{L}_{\text{conf}}$ with defaults $\alpha_{\text{ce}}=0.1$ and $\alpha_{\text{tv}}=0.9$.[^chengDSparkConfidenceScheduledSpeculative2026] So a fixed-weight total variation term is already used on a block drafter, together with a sequential head.

### PARD-2: acceptance-weighted loss on a parallel drafter

[PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) changes the loss weights of a mask-token parallel drafter, not the divergence. It writes the expected acceptance length as $\sum_{k}s_{k}a_{k}$, with $s_{k}$ the probability of reaching position $k$, and weights each position by a proxy $\hat{s}_{k}$: the cumulative product of the target's probability of the ground-truth tokens before position $k$. This is Confidence-Adaptive Token (CAT) optimization. The per-position loss is $\hat{s}_{n,k}(\beta\mathcal{L}^{\mathrm{CE}}+\mathcal{L}^{\mathrm{KD}})$ with $\beta=0.1$.[^anPARD2TargetAlignedParallel2026]

Weighting ablation at temperature 0 (speedup / $\tau$). The fixed decay $\gamma^{t-1}$ is the position-wise heuristic the paper attributes to DFlash and DART:[^anPARD2TargetAlignedParallel2026]

| Weighting | HumanEval | GSM8K | MT-Bench | Average |
|---|---|---|---|---|
| $\gamma=1.0$ (uniform) | 5.52 / 7.45 | 4.22 / 5.58 | 2.67 / 3.54 | 4.14 / 5.52 |
| $\gamma=0.8$ | 5.61 / 7.56 | 4.33 / 5.67 | 2.74 / 3.60 | 4.23 / 5.61 |
| $\gamma=0.6$ | 4.89 / 6.58 | 3.99 / 5.21 | 2.72 / 3.58 | 3.87 / 5.12 |
| CAT | 5.86 / 7.90 | 4.43 / 5.79 | 2.79 / 3.67 | 4.36 / 5.79 |

All rows: [^anPARD2TargetAlignedParallel2026]

- At a fixed inference draft length of 8, adding CAT to a drafter trained at length 16 raises average $\tau$ from 4.83 to 4.98.[^anPARD2TargetAlignedParallel2026]
- The paper does not state which target model the ablations use, and reports no result above temperature 0. The drafter is a mask-token autoregressive backbone with target features added to its inputs, not a block diffusion drafter with KV injection.[^anPARD2TargetAlignedParallel2026]

**Inference.** CAT reaches 5.79 against 5.61 for the best fixed decay, a gain of about 3% in $\tau$, at temperature 0, which is the case this question cares most about. It is the first evidence in the wiki that acceptance-aware weighting helps a one-pass drafter at $T=0$.

## Conflicting claims

None. The DSpark comparison against DFlash changes the head and the loss together, so it does not show what the loss alone contributes. PARD-2 isolates the weighting, but on a different drafter architecture.

## What would resolve it

Three training runs of the same DFlash drafter on the same data, evaluated at temperature 0 and at temperature 1:

1. Position-weighted cross-entropy only.
2. Cross-entropy plus the total variation term with DSpark's weights, with no sequential head.
3. An LK loss with the adaptive $\lambda$.
4. Cross-entropy weighted by PARD-2's CAT weights instead of DFlash's fixed decay.

## Related

- [DFlash research directions for mobile SpecEdge](../analyses/dflash-research-directions-for-mobile-specedge.md)
- [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [PARD](../methods/pard.md), [Knowledge distillation](../methods/knowledge-distillation.md), [DistillSpec](../methods/distillspec.md)
- [Does starting a block drafter from the target's own layers cut its training cost?](target-layer-initialization-for-block-drafters.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)

[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
