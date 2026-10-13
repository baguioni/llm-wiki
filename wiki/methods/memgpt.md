---
type: Method
title: MemGPT
description: OS-inspired LLM system that uses function calls to page information between a fixed context window and external storage, a technique its authors call virtual context management.
tags: [agent-memory, context-management, function-calling, llm-agents, long-context]
sources:
  - id: packerMemGPTLLMsOperating2024
    resource: zotero://select/items/@packerMemGPTLLMsOperating2024
    title: "MemGPT: Towards LLMs as Operating Systems"
  - id: rasmussenZepTemporalKnowledge2025
    resource: zotero://select/items/@rasmussenZepTemporalKnowledge2025
    title: "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
---

# MemGPT

## Overview

MemGPT (MemoryGPT) is an OS-inspired LLM system for *virtual context management*: it gives the illusion of a longer context while using fixed-context models, in the way an operating system gives the illusion of more memory by paging between main memory and disk.[^packerMemGPTLLMsOperating2024] The LLM uses function calls to read and write external data sources, modify its own context, and choose when to return a response to the user.[^packerMemGPTLLMsOperating2024] It is introduced in [Packer et al. 2024](../papers/packerMemGPTLLMsOperating2024.md). The Zep paper calls MemGPT the current state-of-the-art system for agent memory and uses it as its point of comparison.[^rasmussenZepTemporalKnowledge2025]

## How it works

### Memory hierarchy

| Tier | OS analogy | Contents |
|---|---|---|
| Main context | main memory | The LLM prompt tokens. Anything here is in-context. |
| External context | disk | Information outside the fixed context window. It must be explicitly moved into main context before the LLM can use it. |

All rows: [^packerMemGPTLLMsOperating2024]

Main context has three contiguous sections:[^packerMemGPTLLMsOperating2024]

- **System instructions.** Read-only. They describe the control flow, the intended usage of the memory levels, and how to use the MemGPT functions.
- **Working context.** A fixed-size read/write block of unstructured text, writeable only through MemGPT function calls.
- **FIFO queue.** A rolling history of messages, including system messages and function call inputs and outputs.

External context has two stores:[^packerMemGPTLLMsOperating2024]

- **Recall storage.** The message database. The queue manager writes every incoming message and every generated LLM output to it.
- **Archival storage.** A read/write database storing arbitrary length text objects.

### Queue manager

- When the prompt tokens exceed the "warning token count" (e.g. 70% of the context window), a system message warns the LLM of an impending eviction (a memory pressure warning), so that it can store important information to working context or archival storage.[^packerMemGPTLLMsOperating2024]
- When the prompt tokens exceed the "flush token count" (e.g. 100% of the context window), the queue manager flushes the queue: it evicts messages and generates a new recursive summary. Evicted messages remain in recall storage.[^packerMemGPTLLMsOperating2024]
- Messages retrieved from recall storage by a function call are appended to the back of the queue.[^packerMemGPTLLMsOperating2024]

### Function executor and control flow

- Memory edits and retrieval are entirely self-directed: MemGPT updates and searches its own memory based on the current context.[^packerMemGPTLLMsOperating2024]
- Retrieval mechanisms implement pagination so that retrieval calls do not overflow the context window.[^packerMemGPTLLMsOperating2024]
- The LLM can request an immediate follow-up inference with the keyword argument `request_heartbeat=true`. This function chaining is what allows multi-step retrieval.[^packerMemGPTLLMsOperating2024]

## Papers using it

### Packer et al. 2024 (the original paper)

Models: "GPT-4 Turbo" is gpt-4-1106-preview (context window of 128,000), "GPT-4" is gpt-4-0613 (8,192), and "GPT-3.5 Turbo" is gpt-3.5-turbo-1106 (16,385).[^packerMemGPTLLMsOperating2024]

**[Deep memory retrieval](../benchmarks/deep-memory-retrieval.md)** on the [Multi-Session Chat](../datasets/multi-session-chat.md) dataset (Table 2 of the paper). Accuracy comes from an LLM judge. The baselines see a lossy summarization of the past five conversations, while MemGPT has the full conversation history but must reach it through paginated search queries.[^packerMemGPTLLMsOperating2024]

| Model | Accuracy | ROUGE-L (R) |
|---|---|---|
| GPT-3.5 Turbo | 38.7% | 0.394 |
| + MemGPT | 66.9% | 0.629 |
| GPT-4 | 32.1% | 0.296 |
| + MemGPT | 92.5% | 0.814 |
| GPT-4 Turbo | 35.3% | 0.359 |
| + MemGPT | 93.4% | 0.827 |

All rows: [^packerMemGPTLLMsOperating2024]

**Conversation opener** (Table 3 of the paper). MemGPT's opener is scored by similarity to the gold persona labels (SIM-1/3) and to the human-created opener (SIM-H).[^packerMemGPTLLMsOperating2024]

| Method | SIM-1 | SIM-3 | SIM-H |
|---|---|---|---|
| Human | 0.800 | 0.800 | 1.000 |
| MemGPT with GPT-3.5 Turbo | 0.830 | 0.812 | 0.817 |
| MemGPT with GPT-4 | 0.868 | 0.843 | 0.773 |
| MemGPT with GPT-4 Turbo | 0.857 | 0.828 | 0.767 |

All rows: [^packerMemGPTLLMsOperating2024]

**Multi-document question answering.** MemGPT loads the whole embedded document set into archival storage and retrieves through archival storage search, while the fixed-context baselines receive the retriever's top-$K$ documents. MemGPT's performance is unaffected by increased context length, and MemGPT with GPT-4 and with GPT-4 Turbo have equivalent results. Accuracy values are shown only in a figure of the paper.[^packerMemGPTLLMsOperating2024]

**Nested key-value retrieval.** GPT-3.5 hits 0 percent accuracy at 1 nesting level, and GPT-4 and GPT-4 Turbo hit 0 percent accuracy by 3 nesting levels. MemGPT with GPT-4 is unaffected by the number of nesting levels. MemGPT with GPT-4 Turbo and with GPT-3.5 beat their baseline models but begin to drop off at 2 nesting levels because they fail to perform enough lookups.[^packerMemGPTLLMsOperating2024]

### Zep (as the compared system)

[Zep](../papers/rasmussenZepTemporalKnowledge2025.md) evaluates on the DMR task from MemGPT. Its Table 1 takes the two rows marked `†` from the MemGPT paper and adds its own baselines and results.[^rasmussenZepTemporalKnowledge2025]

| Memory | Model | Score |
|---|---|---|
| Recursive Summarization† | gpt-4-turbo | 35.3% |
| Conversation Summaries | gpt-4-turbo | 78.6% |
| MemGPT† | gpt-4-turbo | 93.4% |
| Full-conversation | gpt-4-turbo | 94.4% |
| Zep | gpt-4-turbo | 94.8% |
| Conversation Summaries | gpt-4o-mini | 88.0% |
| Full-conversation | gpt-4o-mini | 98.0% |
| Zep | gpt-4o-mini | 98.2% |

All rows: [^rasmussenZepTemporalKnowledge2025]

- Zep's own gpt-4-turbo runs use gpt-4-turbo-2024-04-09, chosen for comparability with MemGPT's DMR results.[^rasmussenZepTemporalKnowledge2025]
- The authors could not reproduce MemGPT's results with gpt-4o-mini, which they attribute to insufficient methodological details in the published work.[^rasmussenZepTemporalKnowledge2025]
- The authors could not evaluate MemGPT on LongMemEval. They state that the MemGPT framework does not support direct ingestion of existing message histories, and that their workaround of adding the conversation messages to the archival history did not produce successful question responses.[^rasmussenZepTemporalKnowledge2025]

## Strengths & Limitations

- MemGPT clearly improves the underlying base LLM on DMR for all three models.[^packerMemGPTLLMsOperating2024]
- It depends on the function calling ability of the underlying model: on document QA it has significantly degraded performance with GPT-3.5, and it performs best with GPT-4.[^packerMemGPTLLMsOperating2024]
- In theory it is not limited by sub-optimal retriever ranking, but in practice it often stops paging through retriever results before exhausting the retriever database.[^packerMemGPTLLMsOperating2024]
- On nested KV retrieval, MemGPT with GPT-4 Turbo performs worse than MemGPT with GPT-4.[^packerMemGPTLLMsOperating2024]
- The DMR judge is instructed to be generous in its grading.[^packerMemGPTLLMsOperating2024]
- Per Zep, it does not support direct ingestion of an existing message history.[^rasmussenZepTemporalKnowledge2025]

# Contradictions

**Does DMR show that a memory system is needed?** MemGPT reports 93.4% on DMR with GPT-4 Turbo against 35.3% for the same model without MemGPT, and concludes that MemGPT clearly improves the base LLM.[^packerMemGPTLLMsOperating2024] Zep reports that a plain full-conversation baseline with gpt-4-turbo reaches 94.4%, slightly above MemGPT's reported 93.4%, and argues that DMR is inadequate for evaluating memory systems: each conversation has only 60 messages and fits in current context windows, the questions are single-turn fact retrieval, and many are ambiguously phrased.[^rasmussenZepTemporalKnowledge2025] Both numbers stand. The settings differ: MemGPT's baseline sees only a lossy summarization of the past sessions, not the full conversation, and it uses gpt-4-1106-preview, while Zep's baseline puts the full conversation in context and uses gpt-4-turbo-2024-04-09.[^packerMemGPTLLMsOperating2024][^rasmussenZepTemporalKnowledge2025]

**Summary baseline on DMR.** The summarization baseline scores 35.3% in the MemGPT paper (GPT-4 Turbo), and Zep's own "Conversation Summaries" (session summary) baseline scores 78.6% with gpt-4-turbo.[^packerMemGPTLLMsOperating2024][^rasmussenZepTemporalKnowledge2025] These are two different implementations of a summary baseline, run by different authors with different model versions, so they are not the same measurement. Zep lists them as separate rows.[^rasmussenZepTemporalKnowledge2025]

**MemGPT's 93.4% is not independently reproduced.** Zep copies the number from the MemGPT paper and states that it could not reproduce MemGPT's results with gpt-4o-mini.[^rasmussenZepTemporalKnowledge2025]

## Related

- Methods: [Retrieval-augmented generation](retrieval-augmented-generation.md), [LLM-as-a-judge](llm-as-a-judge.md)
- Benchmarks: [Deep Memory Retrieval](../benchmarks/deep-memory-retrieval.md)
- Datasets: [Multi-Session Chat](../datasets/multi-session-chat.md)
- Papers: [MemGPT](../papers/packerMemGPTLLMsOperating2024.md), [Zep](../papers/rasmussenZepTemporalKnowledge2025.md)

## Open questions and results

- [Is Deep Memory Retrieval an adequate benchmark for agent memory?](../questions/deep-memory-retrieval-adequacy.md)

[^packerMemGPTLLMsOperating2024]: Packer et al. 2024
[^rasmussenZepTemporalKnowledge2025]: Rasmussen et al. 2025
