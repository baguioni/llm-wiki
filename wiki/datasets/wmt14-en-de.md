---
type: Dataset
title: WMT14 en-de
description: WMT 2014 English-to-German machine translation task, scored with BLEU, used in the wiki's papers to test knowledge distillation of T5 students and draft models.
tags: [dataset, machine-translation, knowledge-distillation, speculative-decoding, evaluation]
sources:
  - id: agarwalOnPolicyDistillationLanguage2024
    resource: zotero://select/items/@agarwalOnPolicyDistillationLanguage2024
    title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
---

# WMT14 en-de

## Overview

WMT14 EnDe is a standard machine translation benchmark: translate English text to German while preserving content, semantics, and style. It is scored with BLEU against high-quality reference translations.[^zhouDistillSpecImprovingSpeculative2024] Both papers that use it in the wiki distill T5 models.[^agarwalOnPolicyDistillationLanguage2024][^zhouDistillSpecImprovingSpeculative2024]

## Composition

- Split sizes are not stated in the wiki's papers.
- GKD uses the seqio task `wmt_t2t_ende_v003` with tokenized input and output length 80.[^agarwalOnPolicyDistillationLanguage2024]

## Usage across papers

| Paper | Use | Split | Setting | Reported numbers |
|---|---|---|---|---|
| [Agarwal et al. 2024](../papers/agarwalOnPolicyDistillationLanguage2024.md) | Task-specific [GKD](../methods/gkd.md) | validation | T5-XL teacher (BLEU 28), T5-small (25.58) and T5-base (26.98) students, beam search, 3 seeds | On-policy GKD with JSD (0.1) gives 53% higher BLEU improvement than ImitKD and 162% higher than f-distill, averaged over small and base[^agarwalOnPolicyDistillationLanguage2024] |
| [Zhou et al. 2024](../papers/zhouDistillSpecImprovingSpeculative2024.md) | [DistillSpec](../methods/distillspec.md) draft distillation | test | T5-XL target, T5-Small draft, max input and output length 80 | Speedup gains of +0.05× to +0.12× from distillation[^zhouDistillSpecImprovingSpeculative2024] |

- In GKD's ablations on WMT, generalized JSD divergences beat forward and reverse KL, with a smaller gap for the larger student, and on-policy or mixed data beats a fixed supervised dataset.[^agarwalOnPolicyDistillationLanguage2024]

## Known issues

- The two papers evaluate on different splits (validation in GKD, test in DistillSpec).[^agarwalOnPolicyDistillationLanguage2024][^zhouDistillSpecImprovingSpeculative2024]

## Related

- [GKD](../methods/gkd.md), [DistillSpec](../methods/distillspec.md), [Knowledge distillation](../methods/knowledge-distillation.md)

[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
