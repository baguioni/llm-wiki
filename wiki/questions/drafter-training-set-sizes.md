---
type: Open Question
title: How large are the standard drafter training sets?
description: EAGLE-3, SpecForge, and DSpark give different sizes for ShareGPT, UltraChat, and Open-PerfectBlend, in different units and without versions or filtering steps, so the data budgets of published drafters cannot be compared exactly.
tags: [speculative-decoding, training-data, draft-model, speculative-drafter]
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
---

# How large are the standard drafter training sets?

## Question

How many samples are actually in ShareGPT, UltraChat, and Open-PerfectBlend as used for drafter training? The papers give different numbers for the same datasets.

## Why it matters

Data budget is one of the levers for building a drafter cheaply (see [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)). Matching a published recipe, or comparing a cheaper one against it, needs its sample count.

## Evidence so far

| Dataset | EAGLE-3 | SpecForge | DSpark |
|---|---|---|---|
| [ShareGPT](../datasets/sharegpt.md) | approximately 68K data entries[^liEAGLE3ScalingInference2025] | 120K conversations[^liSpecForgeFlexibleEfficient2026] | – |
| [UltraChat](../datasets/ultrachat.md) (UltraChat-200K) | approximately 464K data entries[^liEAGLE3ScalingInference2025] | 200K conversations[^liSpecForgeFlexibleEfficient2026] | – |
| [Open-PerfectBlend](../datasets/perfectblend.md) | – | 1.4M conversations[^liSpecForgeFlexibleEfficient2026] | 1.3 million samples[^chengDSparkConfidenceScheduledSpeculative2026] |

SpecForge's ShareGPT and UltraChat numbers come from its reproduction of the EAGLE-3 training procedure.[^liSpecForgeFlexibleEfficient2026]

## Conflicting claims

The same datasets are given different sizes. The units differ ("data entries", "conversations", "samples"), and no paper states a dataset version, split, or filtering step. One possible reading is that "data entries" count turns or examples while "conversations" count whole dialogues, but no paper says so. The contradictions are recorded on the [ShareGPT](../datasets/sharegpt.md), [UltraChat](../datasets/ultrachat.md), and [Open-PerfectBlend](../datasets/perfectblend.md) pages.

## What would resolve it

- Count the released training files of each recipe in the same unit (conversations and tokens).
- Papers stating the dataset version and any filtering applied.

## Related

- [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)
- [EAGLE-3](../methods/eagle-3.md), [DSpark](../methods/dspark.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
