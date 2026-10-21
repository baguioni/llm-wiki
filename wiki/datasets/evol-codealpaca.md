---
type: Dataset
title: Evol-CodeAlpaca
description: Code instruction dataset that the PARD papers combine with Magpie to train parallel draft models.
tags: [training-data, code, speculative-decoding, draft-model]
sources:
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Evol-CodeAlpaca

## Overview

Evol-CodeAlpaca is the code part of the training data for [PARD](../methods/pard.md) draft models, cited in the PARD paper to Luo et al., 2023.[^anPARDAcceleratingLLM2025] No paper in the wiki evaluates on it.

## Usage across papers

| Paper | Use |
|---|---|
| [PARD](../papers/anPARDAcceleratingLLM2025.md) | Combined with Magpie-Llama-3.1-Pro-1M for the LLaMA3 drafter and with Magpie-Qwen2-Pro-1M for the Qwen2.5 drafter, with regenerated answers.[^anPARDAcceleratingLLM2025] |
| [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) | Kept from the PARD training set.[^anPARD2TargetAlignedParallel2026] |
| My experiment: [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) | 5,000 `instruction` prompts from `theblackcat102/evol-codealpaca-v1` (seed 0); the 128 over 1,024 tokens are dropped, leaving 4,872. Combined with 45,000 Magpie prompts and answered by Qwen3-14B.[^minitron-pard-qwen3-14b] |

## Related

- [Magpie](magpie.md), [HumanEval](humaneval.md)
- [PARD](../methods/pard.md)
- [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
