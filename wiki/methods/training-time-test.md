---
type: Method
title: Training-Time Test
description: Draft-model training technique from EAGLE-3 that simulates multi-step drafting during training by feeding the draft model's own outputs back as inputs, so the draft adapts to self-generated inputs.
tags: [speculative-decoding, draft-model-training, eagle-3, training-technique]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
---

# Training-Time Test

## Overview

Training-time test (TTT) is the training technique introduced with [EAGLE-3](../methods/eagle-3.md). During training, the draft model performs test steps: it generates its output $a$ and feeds it back into itself for further training, so that it adapts to inputs that come from its own earlier steps.[^liEAGLE3ScalingInference2025] SpecForge summarizes the core idea as simulating multiple steps of autoregressive token generation during training.[^liSpecForgeFlexibleEfficient2026]

## How it works

### Motivation

- [EAGLE](../methods/eagle.md) has a feature prediction loss that lets a draft model trained only at Step 1 adapt to Step 2. Removing that loss and expanding the training data improves the acceptance rate $0$-$\alpha$ of the first draft token significantly.[^liEAGLE3ScalingInference2025]
- Without the loss, the Step 1 output $\hat{a}_{t+1}$ is far away from the ground-truth feature $f_{t+1}$. The Step 2 input then deviates from the training distribution, and the acceptance rate $1$-$\alpha$ of the second draft token is very low.[^liEAGLE3ScalingInference2025]
- Incorporating Step 1 into the training process fixes this. The authors name the technique training-time test.[^liEAGLE3ScalingInference2025]
- Because the feature prediction loss is gone, the draft model's input no longer has to be the top-layer features, which is what allows EAGLE-3 to use features from intermediate layers.[^liEAGLE3ScalingInference2025]

### Mechanism

- The draft-model input may be target features $g_1,\cdots,g_t$ or the draft model's outputs $a_{t+1},\cdots,a_{t+j}$.[^liEAGLE3ScalingInference2025]
- Only the self-attention needs modification. In the native training step the attention mask is a standard lower triangular matrix. In a simulated step the outputs have a tree-like contextual relationship with the training tokens, and the mask is adjusted accordingly. All attention masks are diagonal except when the original training data is used as the key, so attention scores are computed with vector dot products only for the corresponding positions.[^liEAGLE3ScalingInference2025]
- At each TTT step, the model attends to a growing context: the original training sequence as prefix, plus the tokens generated in previous steps.[^liSpecForgeFlexibleEfficient2026]

## Variants

| Setting | TTT length | Source |
|---|---|---|
| Original EAGLE3 implementation | fixed at 7 | SpecForge[^liSpecForgeFlexibleEfficient2026] |
| SpecForge sweep on Llama3.1-8B, perfect-blend dataset | 1 to 17 | SpecForge[^liSpecForgeFlexibleEfficient2026] |
| DSpark's retrained Eagle3 baseline | 7, aligned with the block size of DFlash and DSpark | DSpark[^chengDSparkConfidenceScheduledSpeculative2026] |
| Aurora online training | 5 | Aurora[^wangWhenRLMeets2026] |

- HASS makes similar attention modifications to simulate testing during training. It still performs feature prediction, includes the feature prediction loss $l_{fea}$, and requires the draft input to be the top-layer features.[^liEAGLE3ScalingInference2025]
- Names differ across papers. The EAGLE-3 paper writes "training-time test".[^liEAGLE3ScalingInference2025] SpecForge writes both "Training-Time Test" and "Training-Time Testing".[^liSpecForgeFlexibleEfficient2026] Aurora's hyperparameter description expands TTT as "test-time training", in a table whose "TTT Length" is 5.[^wangWhenRLMeets2026]

## Papers using it

- [EAGLE-3 paper](../papers/liEAGLE3ScalingInference2025.md): proposes it. With training-time test, the paper reports that increasing the draft model's training data gives a proportional increase in the speedup ratio. EAGLE-3's acceptance rate stays almost unchanged as more of the input comes from the draft model itself, whereas EAGLE's drops significantly (figure only).[^liEAGLE3ScalingInference2025]
- [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md): optimizes the computation of TTT and studies its length.[^liSpecForgeFlexibleEfficient2026]
  - TTT with a step length of 7 incurs substantial GPU memory consumption. Stored attention logits account for 80% of the total activation memory in the naive implementation.[^liSpecForgeFlexibleEfficient2026]
  - Sparse tree attention with FlexAttention and a BlockMask: at TTT length 7, final TTT step, sequence length 4096, on a single NVIDIA H200 GPU, execution time falls by 62.1% and peak memory usage by 93.5% against a native SDPA-based implementation.[^liSpecForgeFlexibleEfficient2026]
  - A custom Triton kernel for the backward pass of the masked softmax loss reduces memory by 30–40%.[^liSpecForgeFlexibleEfficient2026]
  - Length study: acceptance length gains sharply as the TTT length increases from 1 to 3. For MT-Bench a TTT length of 3 already achieves strong performance, whereas for Math500, GSM8K, and HumanEval a TTT length of approximately 13 yields the best results. The numbers are in a figure only.[^liSpecForgeFlexibleEfficient2026]
- [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): describes Eagle3 as an autoregressive drafter based on TTT and sets its TTT horizon to 7 for the baseline.[^chengDSparkConfidenceScheduledSpeculative2026]
- [Aurora](../papers/wangWhenRLMeets2026.md): uses a TTT length of 5 with a maximum sequence length of 2,048 for online speculator training.[^wangWhenRLMeets2026]
- [DFlash](../papers/chenDFlashBlockDiffusion2026.md): names the costly training-time test as the reason long-context training is challenging for methods such as EAGLE-3, and avoids it with a fixed number of masked blocks per sequence.[^chenDFlashBlockDiffusion2026]

## Strengths & Limitations

- Strength: it closes the gap between training inputs and the self-generated inputs seen at inference, which removes the need for the feature prediction loss.[^liEAGLE3ScalingInference2025]
- Limitation: increasing the TTT length proportionally increases training time and memory consumption for the draft model. SpecForge advises reducing TTT to 3 or 5 under memory constraints.[^liSpecForgeFlexibleEfficient2026]
- Limitation: the best TTT length is task-dependent.[^liSpecForgeFlexibleEfficient2026]
- Limitation: it makes long-context training costly.[^chenDFlashBlockDiffusion2026]

## Related

- Method it belongs to: [EAGLE-3](../methods/eagle-3.md)
- Predecessors: [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md)
- Parent concept: [Speculative decoding](../methods/speculative-decoding.md)
- Drafters trained without it: [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md)
- Datasets: [Open-PerfectBlend](../datasets/perfectblend.md), [MT-Bench](../datasets/mt-bench.md), [GSM8K](../datasets/gsm8k.md), [HumanEval](../datasets/humaneval.md), [MATH-500](../datasets/math-500.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^wangWhenRLMeets2026]: Wang et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
