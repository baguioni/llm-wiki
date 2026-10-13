---
type: Dataset
title: Chatbot Instruction Prompts
description: Huggingface dataset of general assistant-style prompts that two of the wiki's papers use as an input stream for speculative-decoding serving experiments.
tags: [chat, prompts, speculative-decoding, serving-workload]
sources:
  - id: suSynergySpeculativeDecoding2023
    resource: zotero://select/items/@suSynergySpeculativeDecoding2023
    title: The Synergy of Speculative Decoding and Batching in Serving Large Language Models
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
---

# Chatbot Instruction Prompts

## Overview

Chatbot Instruction Prompts (`chatbot_instruction_prompts`) is a Huggingface dataset.[^suSynergySpeculativeDecoding2023] It contains general assistant-style prompts for open-ended dialog.[^wangWhenRLMeets2026] Two papers in this wiki use its prompts as the input stream for [speculative decoding](../methods/speculative-decoding.md) serving experiments.[^suSynergySpeculativeDecoding2023][^wangWhenRLMeets2026] Neither reports task accuracy on it.

## Composition

- Aurora describes it as open-ended assistant conversations with more diverse and less constrained language than its other sources, and groups it with the long-form natural language response regime.[^wangWhenRLMeets2026]
- The papers do not state the dataset's size or splits. Aurora samples 10k prompts from it.[^wangWhenRLMeets2026] The Synergy paper uses only the prompt field.[^suSynergySpeculativeDecoding2023]

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Synergy of Speculative Decoding and Batching](../papers/suSynergySpeculativeDecoding2023.md) | The only evaluation dataset. Prompts are batched (1000 prompts, 128 new tokens each) or sent as a request stream | OPT-6.7B as the LLM and OPT-125M as the small speculative model, RTX 3090 | See the speed table below[^suSynergySpeculativeDecoding2023] |
| [Aurora](../papers/wangWhenRLMeets2026.md) | Source of the conversational-instruction prompts, 10k of a 44k mixed-domain request stream | Online draft training with EAGLE-3; Qwen3-8B target in the day-0 study | No per-dataset number. On the whole mixed stream the acceptance length reaches 3.08 and throughput stabilizes at 302.3 tokens/s[^wangWhenRLMeets2026] |

## Speed metrics

These are speculative-decoding speedups measured with this dataset's prompts. They say nothing about task accuracy.

### [Synergy of Speculative Decoding and Batching](../papers/suSynergySpeculativeDecoding2023.md)

Speedup of adaptive speculative decoding (speculation length chosen per batch size) over serving without speculative decoding. The paper's Algorithm 1 is speculative decoding with argmax sampling, and it does not state a sampling temperature for these runs.[^suSynergySpeculativeDecoding2023]

| Model | Temp. | Method | Setting | Speedup |
|---|---|---|---|---|
| OPT-6.7B / OPT-125M | not stated | Adaptive speculative decoding | fixed batch size 1 | 2.73$\times$ (63% latency reduction) |
| OPT-6.7B / OPT-125M | not stated | Adaptive speculative decoding | fixed batch size 32 | 1.31$\times$ |
| OPT-6.7B / OPT-125M | not stated | Adaptive speculative decoding | average across all fixed batch sizes | 1.94$\times$ |
| OPT-6.7B / OPT-125M | not stated | Adaptive speculative decoding | dynamic traffic, on average | 2.3$\times$ |

All rows: [^suSynergySpeculativeDecoding2023]

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md)
- Datasets in the same request stream: [GSM8K](gsm8k.md), [Spider](spider.md)

[^suSynergySpeculativeDecoding2023]: Su et al. 2023
[^wangWhenRLMeets2026]: Wang et al. 2026
