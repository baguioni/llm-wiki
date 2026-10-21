---
type: Dataset
title: Magpie
description: Synthetic instruction dataset that the PARD papers use, with regenerated answers, to train parallel draft models.
tags: [training-data, speculative-decoding, draft-model]
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

# Magpie

## Overview

The PARD paper cites Magpie as "alignment data synthesis from scratch by prompting aligned llms with nothing".[^anPARDAcceleratingLLM2025] Two papers in the wiki use it as training data for [PARD](../methods/pard.md) draft models. Neither evaluates on it.[^anPARDAcceleratingLLM2025][^anPARD2TargetAlignedParallel2026]

## Usage across papers

| Paper | Subset and use |
|---|---|
| [PARD](../papers/anPARDAcceleratingLLM2025.md) | Magpie-Llama-3.1-Pro-1M with Evol-CodeAlpaca for the LLaMA3 drafter, and Magpie-Qwen2-Pro-1M with Evol-CodeAlpaca for the Qwen2.5 drafter. Answers are regenerated to improve training accuracy.[^anPARDAcceleratingLLM2025] |
| [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) | Kept from the PARD training set, which PARD-2 expands with samples from Nemotron-v2 and Nemotron-v3.[^anPARD2TargetAlignedParallel2026] |
| My experiment: [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) | 45,000 first-turn prompts from `Magpie-Align/Magpie-Qwen2-Pro-1M-v0.1` (seed 0), with 4,872 Evol-CodeAlpaca prompts. Qwen3-14B answers them greedily with thinking off, at most 512 new tokens; the answers train both the chat-KD recovery and PARD-1.[^minitron-pard-qwen3-14b] |

## Related

- [Evol-CodeAlpaca](evol-codealpaca.md), [Open-PerfectBlend](perfectblend.md), [ShareGPT](sharegpt.md)
- [PARD](../methods/pard.md)
- [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
