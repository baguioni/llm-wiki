---
type: Open Question
title: Is Deep Memory Retrieval an adequate benchmark for agent memory?
description: MemGPT presents Deep Memory Retrieval as evidence that a memory system is needed, while Zep shows a full-conversation baseline that matches it.
tags: [agent-memory, evaluation]
sources:
  - id: packerMemGPTLLMsOperating2024
    resource: zotero://select/items/@packerMemGPTLLMsOperating2024
    title: "MemGPT: Towards LLMs as Operating Systems"
  - id: rasmussenZepTemporalKnowledge2025
    resource: zotero://select/items/@rasmussenZepTemporalKnowledge2025
    title: "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
---

# Is Deep Memory Retrieval an adequate benchmark for agent memory?

## Question

Does a high score on Deep Memory Retrieval (DMR) show that a memory system works?

## Why it matters

DMR is the only benchmark on which the two memory systems in this wiki, [MemGPT](../methods/memgpt.md) and Zep, are directly compared.

## Evidence so far

| System | Model | Score | Reported by |
|---|---|---|---|
| MemGPT | GPT-4 Turbo | 93.4% | [MemGPT](../papers/packerMemGPTLLMsOperating2024.md)[^packerMemGPTLLMsOperating2024] |
| Fixed-context baseline (summary) | GPT-4 Turbo | 35.3% | [MemGPT](../papers/packerMemGPTLLMsOperating2024.md)[^packerMemGPTLLMsOperating2024] |
| Full-conversation baseline | gpt-4-turbo | 94.4% | [Zep](../papers/rasmussenZepTemporalKnowledge2025.md)[^rasmussenZepTemporalKnowledge2025] |
| Zep | gpt-4-turbo | 94.8% | [Zep](../papers/rasmussenZepTemporalKnowledge2025.md)[^rasmussenZepTemporalKnowledge2025] |
| Zep | gpt-4o-mini | 98.2% | [Zep](../papers/rasmussenZepTemporalKnowledge2025.md)[^rasmussenZepTemporalKnowledge2025] |

## Conflicting claims

- MemGPT reports a large gain over its fixed-context baseline (93.4% against 35.3%).[^packerMemGPTLLMsOperating2024]
- Zep reports that giving the model the full conversation scores 94.4%, above MemGPT, and evaluates on LongMemEval as well, where Zep scores 71.2% against 60.2% for full context with gpt-4o.[^rasmussenZepTemporalKnowledge2025]

The baselines differ: MemGPT's baseline sees a summary, Zep's sees the full conversation.

## What would resolve it

Results for both systems on a benchmark where the conversation does not fit in the context window, with the same model version.

## Related

- [Deep Memory Retrieval](../benchmarks/deep-memory-retrieval.md), [Multi-Session Chat](../datasets/multi-session-chat.md)
- [MemGPT](../methods/memgpt.md), [Retrieval-augmented generation](../methods/retrieval-augmented-generation.md)

[^packerMemGPTLLMsOperating2024]: Packer et al. 2024
[^rasmussenZepTemporalKnowledge2025]: Rasmussen et al. 2025
