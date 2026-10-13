---
type: Open Question
title: What is the GSM8K score of Sheared-LLaMA 2.7B?
description: Two papers report GSM8K scores for Sheared-LLaMA 2.7B that differ widely (2.7 and 23.96).
tags: [pruning, evaluation, gsm8k]
sources:
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
---

# What is the GSM8K score of Sheared-LLaMA 2.7B?

## Question

Which GSM8K score for Sheared-LLaMA 2.7B is correct, and what causes the gap?

## Why it matters

The Minitron paper uses the Sheared-LLaMA row as a baseline for its pruned models. The other values in that row agree with the Sheared-LLaMA paper; this one does not.

## Conflicting claims

| Reported by | GSM8K | Setting |
|---|---|---|
| [Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) | 2.7 | 8-shot, EM[^xiaShearedLLaMAAccelerating2024] |
| [Minitron](../papers/muralidharanCompactLanguageModels2024.md) | 23.96 | 5-shot[^muralidharanCompactLanguageModels2024] |

The Sheared-LLaMA paper reports 13.7 for the unpruned LLaMA2-7B in the same table,[^xiaShearedLLaMAAccelerating2024] so 23.96 for the pruned model is above the source model.

## What would resolve it

A statement of how the Minitron paper obtained the Sheared-LLaMA GSM8K value, or a re-run of both settings on the released checkpoint.

## Related

- [Sheared-LLaMA](../methods/sheared-llama.md), [Structured pruning](../methods/structured-pruning.md)
- [GSM8K](../datasets/gsm8k.md)

[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
