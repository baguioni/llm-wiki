---
type: Dataset
title: UltraChat
description: Instructional conversation dataset (used as UltraChat-200K) that the wiki's papers pair with ShareGPT to train speculative-decoding draft models, including the official EAGLE-3 drafters.
tags: [chat, conversations, training-data, speculative-decoding, draft-model]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# UltraChat

## Overview

The papers in this wiki cite UltraChat as Ding et al. 2023, "Enhancing chat language models by scaling high-quality instructional conversations".[^liEAGLE3ScalingInference2025][^liSpecForgeFlexibleEfficient2026][^chenDFlashBlockDiffusion2026] EAGLE-3 names the version it uses UltraChat-200K.[^liEAGLE3ScalingInference2025]

Three papers use it as training data for [speculative decoding](../methods/speculative-decoding.md) draft models, always together with [ShareGPT](sharegpt.md). EAGLE-3 trains its draft models on it,[^liEAGLE3ScalingInference2025] SpecForge reproduces that EAGLE-3 training as a baseline,[^liSpecForgeFlexibleEfficient2026] and DFlash uses the same data to compare against the official EAGLE-3 checkpoints on LLaMA-3.1-8B-Instruct.[^chenDFlashBlockDiffusion2026] None of these papers evaluates on it. HyCo uses its test split as a validation set (UC-val) and its train split (UC-tr) for calibration, quantization-aware training, and vocabulary statistics.[^baeHyCoHybridDrafting2026]

## Composition

Only what the papers state. The two size statements use different units and are not reconciled (see Contradictions).

| Statistic | Value | Source |
|---|---|---|
| Size as draft-model training data (UltraChat-200K) | approximately 464K data entries | EAGLE-3[^liEAGLE3ScalingInference2025] |
| Size as draft-model training data | 200K conversations | SpecForge[^liSpecForgeFlexibleEfficient2026] |

## Usage across papers

| Paper | Use | Setting | Numbers |
|---|---|---|---|
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | Training data for the EAGLE-3 draft models, with ShareGPT. The target model generates the responses rather than using a fixed dataset | AdamW, $(\beta_{1},\beta_{2})$ = (0.9, 0.95), gradient clipping 0.5, learning rate 5e-5; targets Vicuna 13B, LLaMA-Instruct 3.1 8B, LLaMA-Instruct 3.3 70B, DeepSeek-R1-Distill-LLaMA 8B | approximately 68K (ShareGPT) and 464K (UltraChat-200K) data entries. For LLaMA-Instruct 3.1 8B at temperature 0, mean speedup 4.44x and $\tau$ 6.23[^liEAGLE3ScalingInference2025] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | Training data for a reproduction of the EAGLE-3 training procedure, with ShareGPT; the baseline against Perfect-Blend | LLaMA-3.1-Instruct | ShareGPT (120K conversations) and UltraChat (200K conversations) give an acceptance length of 2.82 on Math500; Perfect-Blend (1.4M conversations) gives 3.48, an additional 1.17× inference speedup[^liSpecForgeFlexibleEfficient2026] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Training data for a DFlash drafter, with ShareGPT, "using the exactly same training data as EAGLE-3", in the ablation against the official EAGLE-3 checkpoints | LLaMA-3.1-8B-Instruct, DFlash block size 10, SGLang Spec-v1, single B200 GPU | At concurrency 1, DFlash (10) reaches 2.4× on GSM8K, 2.8× on HumanEval, and 2.2× on Alpaca, with average $\tau$ 4.32, 4.91, and 3.73[^chenDFlashBlockDiffusion2026] |
| [HyCo](../papers/baeHyCoHybridDrafting2026.md) | UC-val: 60 prompts from the test\_sft split of UltraChat 200k, used to select HyCo's settings. UC-tr: the train\_sft split, used for 60 activation-calibration and MTP-head QAT prompts and for the token counts of the 86K output keep set | Gemma 4 26B-A4B verifier's greedy answers; UC-val prompts have about 100 tokens at the median and a 512-token output limit | Keep-set tokens are the most frequent in the assistant turns of 20,000 UC-tr conversations. Tokens outside the keep set are 3.0% of the verifier's bonus tokens on UC-val[^baeHyCoHybridDrafting2026] |

## Known issues

- SpecForge states that existing draft checkpoints are primarily trained on the ShareGPT and UltraChat datasets, which contain limited coverage of math- and code-centric samples, and gives this as the reason those checkpoints trail SpecBundle on coding and mathematics benchmarks.[^liSpecForgeFlexibleEfficient2026]
- EAGLE-3 regenerates the responses with the target model,[^liEAGLE3ScalingInference2025] and SpecForge describes its run as a reproduction of the EAGLE-3 training procedure.[^liSpecForgeFlexibleEfficient2026] SpecForge does not state whether its responses were regenerated.

# Contradictions

### Size of the UltraChat training set

EAGLE-3 states that UltraChat-200K contains approximately 464K data entries.[^liEAGLE3ScalingInference2025] SpecForge, reproducing the EAGLE-3 training procedure, gives UltraChat as 200K conversations.[^liSpecForgeFlexibleEfficient2026] The papers count different units ("data entries" and "conversations") and neither says how the data was split or filtered, so the wiki cannot tell whether they describe the same data. The ShareGPT figures in the same two sentences differ in the same way (approximately 68K entries against 120K conversations); see [ShareGPT](sharegpt.md).

## Related

- Papers: [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md), [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md), [DFlash](../papers/chenDFlashBlockDiffusion2026.md), [HyCo](../papers/baeHyCoHybridDrafting2026.md)
- Methods trained on it: [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [Training-time test](../methods/training-time-test.md)
- Datasets: [ShareGPT](sharegpt.md) (always used with it), [Open-PerfectBlend](perfectblend.md) (the larger mixture SpecForge compares it against), [OpenThoughts-114k](openthoughts.md) (EAGLE-3's extra data for its reasoning-model drafter), [Nemotron Post-Training Dataset](nemotron-post-training.md) (DFlash's main training data), [MATH-500](math-500.md)
- [How large are the standard drafter training sets?](../questions/drafter-training-set-sizes.md)
- [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
