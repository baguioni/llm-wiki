---
type: Open Question
title: Do PARD-2's CAT and KD losses help a drafter trained without target features?
description: PARD-2's confidence-adaptive weighting and distillation term need only target probabilities, not hidden states, but every PARD-2 ablation adds them on top of target features, so their effect on a drafter trained fully feature-free (PARD-1 architecture) is untested.
tags: [speculative-decoding, parallel-drafting, draft-model, knowledge-distillation, speculative-drafter, mobile-specedge, pard]
sources:
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
---

# Do PARD-2's CAT and KD losses help a drafter trained without target features?

## Question

If a PARD drafter is trained with PARD-2's loss, $\mathcal{L}_{k}=\sum_{n}\hat{s}_{n,k}(\beta\mathcal{L}^{\mathrm{CE}}_{n,k}+\mathcal{L}^{\mathrm{KD}}_{n,k})$ with $K=16$, but never receives target hidden states in training or inference, how much of PARD-2's gain over PARD does it keep?

## Why it matters

A feature-free drafter deploys like PARD-1: no target hidden states have to reach the drafter. That suits a phone drafter with a server verifier. CAT needs only the target's probability of each ground-truth token, and the KD term needs the target distribution,[^anPARD2TargetAlignedParallel2026] so the training signal is available from a target forward pass without hidden-state extraction.

## Evidence so far

- PARD-1 trains with uniform cross-entropy over the $K$ positions and no target model.[^anPARDAcceleratingLLM2025]
- PARD-2's component breakdown (Table 5) adds CAT only on top of target features. It has no row with CAT and no target features, and no row without the KD term.[^anPARD2TargetAlignedParallel2026]
- In Table 5, training with $k_{train}=16$ instead of 8 without CAT lowers average $\tau$ from 4.96 to 4.83 at $k_{infer}=8$; adding CAT gives 4.98 at $k_{infer}=8$ and 5.79 at $k_{infer}=16$.[^anPARD2TargetAlignedParallel2026] All of these rows use target features.
- In target-independent mode (no features at inference), PARD-2 reaches average 4.79× / $\tau$ 6.03 on Qwen3-14B against PARD's 4.51× / 5.14.[^anPARD2TargetAlignedParallel2026] The authors conclude that CAT stays effective without target features.[^anPARD2TargetAlignedParallel2026] That drafter is trained with features present with probability $1-\rho$, so it is not a feature-free-trained drafter.
- The text does not give the exact form of $\mathcal{L}^{\mathrm{KD}}$.[^anPARD2TargetAlignedParallel2026]

## Conflicting claims

None. The question is untested.

## What would resolve it

On one backbone and dataset, train three feature-free arms at $K=16$: PARD-1 cross-entropy; CAT-weighted cross-entropy; CAT with $\beta\mathcal{L}^{\mathrm{CE}}+\mathcal{L}^{\mathrm{KD}}$, $\beta=0.1$. Compare $\tau$ and per-position acceptance against the same target.

## Related

- [Was PARD-2's Qwen3-14B drafter trained to run without target features?](pard-2-qwen3-14b-feature-gating.md)
- [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md)
- [Where Osprey's ideas fit a pruned-target PARD pipeline](../analyses/osprey-ideas-for-pruned-target-pard-pipeline.md)
- [What the target must supply to train a drafter](../analyses/target-signals-for-drafter-training.md)
- [PARD](../methods/pard.md), [Knowledge distillation](../methods/knowledge-distillation.md)

[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
