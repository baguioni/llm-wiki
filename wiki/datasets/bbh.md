---
type: Dataset
title: BIG-Bench Hard (BBH)
description: Suite of 23 BIG-Bench tasks on which PaLM 540B scores below average human raters, used in the wiki's papers as a held-out test for task-agnostic distillation and for the transfer of a distilled draft model.
tags: [dataset, reasoning, knowledge-distillation, speculative-decoding, evaluation]
sources:
  - id: agarwalOnPolicyDistillationLanguage2024
    resource: zotero://select/items/@agarwalOnPolicyDistillationLanguage2024
    title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
---

# BIG-Bench Hard (BBH)

## Overview

BBH includes 23 tasks from BIG-Bench for which PaLM 540B performs below average human raters.[^agarwalOnPolicyDistillationLanguage2024]

## Composition

- 23 tasks.[^agarwalOnPolicyDistillationLanguage2024][^zhouDistillSpecImprovingSpeculative2024]
- Per-task sizes are not stated in the wiki's papers.

## Usage across papers

| Paper | Use | Setting | Reported numbers |
|---|---|---|---|
| [Agarwal et al. 2024](../papers/agarwalOnPolicyDistillationLanguage2024.md) | Held-out test of task-agnostic [GKD](../methods/gkd.md) on FLAN2021 | FLAN T5-XL teacher, few-shot exact match averaged over tasks | Teacher 41%; student 31.25% (the caption calls it T5-large, the setup T5-Base); on-policy GKD gives 2% absolute improvement[^agarwalOnPolicyDistillationLanguage2024] |
| [Zhou et al. 2024](../papers/zhouDistillSpecImprovingSpeculative2024.md) | Transfer of a [DistillSpec](../methods/distillspec.md) draft distilled on GSM8K | T5-XL target, T5-Small draft, zero-shot CoT, average over 23 tasks | Speedup 1.93× → 2.21× (greedy) and 1.78× → 2.02× (non-greedy)[^zhouDistillSpecImprovingSpeculative2024] |

## Related

- [MMLU](mmlu.md) (the other held-out suite in GKD's task-agnostic test)
- [GKD](../methods/gkd.md), [DistillSpec](../methods/distillspec.md)

[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
