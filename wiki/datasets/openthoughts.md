---
type: Dataset
title: OpenThoughts-114k
description: Reasoning dataset that PARD and EAGLE-3 use to train draft models for DeepSeek-R1-distilled reasoning targets.
tags: [reasoning, math, training-data, speculative-decoding, draft-model]
sources:
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
---

# OpenThoughts-114k

## Overview

PARD cites OpenThoughts-114k as Team 2025, "Open Thoughts", https://open-thoughts.ai.[^anPARDAcceleratingLLM2025] Two papers in this wiki use it as training data for [speculative decoding](../methods/speculative-decoding.md) draft models whose targets are DeepSeek-R1-distilled reasoning models: PARD for its DeepSeek-R1-Qwen drafter,[^anPARDAcceleratingLLM2025] and EAGLE-3, which uses a math portion named OpenThoughts-114k-math, for its DeepSeek-R1-Distill-LLaMA 8B drafter.[^liEAGLE3ScalingInference2025] Neither paper evaluates on it, and neither states its size beyond the name.

## Usage across papers

| Paper | Use | Setting | Numbers |
|---|---|---|---|
| [PARD](../papers/anPARDAcceleratingLLM2025.md) | Training data for the DeepSeek-R1-Qwen draft model, together with OpenR1-Math-220k and Chinese-DeepSeek-R1-Distill-Data-110k. The original answers are used, not regenerated ones | Smallest model of the series trained in the PARD framework; 4 epochs, learning rate 3e-5, max sequence length 1024, 8xMI250X; evaluated in vLLM on A100-40GB | Average speedup over HumanEval, GSM8K, and Math500 of 2.51 on DS 7B and 3.01 on DS 14B (Table 6)[^anPARDAcceleratingLLM2025] |
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | Extra training data (OpenThoughts-114k-math) for the DeepSeek-R1-Distill-LLaMA 8B draft model, on top of ShareGPT and UltraChat-200K | DeepSeek-R1-Distill-LLaMA 8B target | At temperature 0, EAGLE-3 reaches 5.01x speedup and $\tau$ 6.93 on GSM8K, its highest speedup across the five tasks for this target; mean 4.16x, $\tau$ 5.84[^liEAGLE3ScalingInference2025] |

## Known issues

- EAGLE-3 attributes the DeepSeek-R1-Distill-LLaMA 8B drafter's highest speedup being on GSM8K, rather than HumanEval as for the other targets, to training on OpenThoughts-114k-math, and hedges it: "This may be because".[^liEAGLE3ScalingInference2025] The paper reports no ablation without this data.
- PARD trains the DeepSeek-R1-Qwen drafter on a mixture of three datasets, so its results cannot be attributed to OpenThoughts-114k alone. PARD's ablations use a 93K subset of OpenR1-Math-220K, not OpenThoughts-114k.[^anPARDAcceleratingLLM2025]
- The two papers handle answers differently. PARD uses the original answers for DeepSeek-R1-Qwen.[^anPARDAcceleratingLLM2025] EAGLE-3 states that it calls the target model to generate responses rather than using a fixed dataset, but does not say whether this also applies to OpenThoughts-114k-math.[^liEAGLE3ScalingInference2025]

## Related

- Papers: [PARD](../papers/anPARDAcceleratingLLM2025.md), [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md)
- Methods trained on it: [PARD](../methods/pard.md), [EAGLE-3](../methods/eagle-3.md)
- Datasets used alongside it: [UltraChat](ultrachat.md), [ShareGPT](sharegpt.md) (EAGLE-3), [Magpie](magpie.md), [Evol-CodeAlpaca](evol-codealpaca.md) (PARD's data for its other targets)
- Evaluated on: [GSM8K](gsm8k.md), [MATH-500](math-500.md), [HumanEval](humaneval.md)
- [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
[^liEAGLE3ScalingInference2025]: Li et al. 2025
