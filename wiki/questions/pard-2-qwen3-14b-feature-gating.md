---
type: Open Question
title: Was PARD-2's Qwen3-14B drafter trained to run without target features?
description: PARD-2's hyperparameter table gives a stochastic gating ratio of 0.0 for Qwen3-14B while its implementation details give 0.1, so it is unclear whether its Qwen3-14B drafter ever trained without target features and whether it can run feature-free.
tags: [speculative-decoding, pard, parallel-drafting, target-independent-drafting, mobile-specedge, speculative-drafter]
sources:
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
---

# Was PARD-2's Qwen3-14B drafter trained to run without target features?

## Question

[PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) trains one drafter to run either with or without target hidden features. To do this, it drops the features during training with probability $\rho$. Was its Qwen3-14B drafter trained with $\rho>0$, so that it can run in the feature-free (target-independent) mode?

## Why it matters

- In mobile SpecEdge, a feature-free drafter needs nothing from the server except verified token ids. A feature drafter needs target hidden states sent to the phone.
- The same drafter run with and without features would be the cleanest controlled comparison of what target features are worth on the phone, since architecture, data, and weights are all held fixed. That comparison only works if the drafter was trained to run both ways.
- The target in my project is Qwen3-14B, the one size for which the paper's settings disagree.

## Evidence so far

- **The gating mechanism.** The drafter input is $e^{d^{\prime}}=e^{d}+\xi\cdot t$ with $\xi\sim\mathrm{Bernoulli}(1-\rho)$, where $t$ is the fused target feature. With probability $\rho$ the features are left out. The paper presents this as reducing dependence on the target, so that one drafter serves the whole model family.[^anPARD2TargetAlignedParallel2026]
- **Implementation details:** "We set $\rho=0.1$", with no per-model exception.[^anPARD2TargetAlignedParallel2026]
- **Hyperparameter table (Table 6):** stochastic gating ratio 0.1 for Llama3.1-8B, 0.1 for Qwen3-8B, and **0.0 for Qwen3-14B**.[^anPARD2TargetAlignedParallel2026] At $\rho=0.0$ the features are always added, so the drafter never trains without them.
- **Target-independent results (Table 2)** include Qwen3-14B as a target, at an average 4.79× and $\tau$ 6.03, against 5.81× and 6.91 in target-dependent mode (Table 1).[^anPARD2TargetAlignedParallel2026] The caption says "All experiments are evaluated on the same draft model". It does not say which drafter that is, so this need not be the Qwen3-14B-trained drafter.
- **Gating ablation (Table 4):** no gating reaches an average $\tau$ of 6.10, and $\rho=0.1$ reaches 6.06.[^anPARD2TargetAlignedParallel2026] Gating costs little in target-dependent mode. The paper reports no feature-free numbers for a drafter trained without gating.

### My drafter evaluation

- In [my drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md), the released `amd/PARD2-Qwen3-14B` drafter (Q4_0) was scored offline in target-independent mode. The acceptance oracle on 10-15 gave it 2.0 tok/round as a chain, and the mode was dropped before the live runs.[^drafter-evaluation]
- For comparison, the same oracle gives PARD-1 (`amd/PARD-Qwen3-0.6B`) 2.78 tok/round as a chain, and live chain7 runs give PARD-2 in target-dependent mode 3.34.[^drafter-evaluation]

**Inference.** Feature-free, the Qwen3-14B drafter accepts less than the target-independent PARD-1, which fits a drafter trained at $\rho=0.0$. The report does not say whether the 2.0 figure used the same chain depth and requests as the 2.78 one, so this is suggestive, not a resolution.

## Conflicting claims

The paper itself disagrees: $\rho=0.1$ in the implementation details, and $\rho=0.0$ for Qwen3-14B in Table 6.[^anPARD2TargetAlignedParallel2026] The [PARD-2 paper page](../papers/anPARD2TargetAlignedParallel2026.md) records the same inconsistency.

## What would resolve it

- Measure the released Qwen3-14B drafter's acceptance on a GPU with the features switched off, against PARD and against the same drafter with features. A collapse without features would mean it was trained at $\rho=0.0$.
- Check the released training configuration, or ask the authors which drafter Table 2 uses.
- If the Qwen3-14B drafter cannot run feature-free, use a drafter trained with $\rho=0.1$ (Qwen3-8B, per Table 6) for the with-and-without comparison.

## Related

- [Do PARD-2's CAT and KD losses help a drafter trained without target features?](feature-free-pard-2-losses.md)
- [PARD](../methods/pard.md), [PARD-2 paper](../papers/anPARD2TargetAlignedParallel2026.md)
- [What the target must supply to train a drafter](../analyses/target-signals-for-drafter-training.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)
- [Does speculative decoding help on a mobile NPU?](speculative-decoding-on-mobile-npu.md)
- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)

[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
