---
type: Paper
title: "MemGPT: Towards LLMs as Operating Systems"
description: OS-inspired LLM system that uses function calls to page information between the context window and external storage, giving a fixed-context LLM the illusion of extended context.
tags: [agent-memory, virtual-context-management, long-context, function-calling, retrieval-augmented-generation, conversational-agents, ai899]
collections: [ai899]
authors: [Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez]
doi: 10.48550/arXiv.2310.08560
arxiv: "2310.08560"
arxiv_version: 2310.08560v2
code: https://research.memgpt.ai
sources:
  - id: packerMemGPTLLMsOperating2024
    resource: zotero://select/items/@packerMemGPTLLMsOperating2024
    title: "MemGPT: Towards LLMs as Operating Systems"
---

# MemGPT: Towards LLMs as Operating Systems

Text source: arXiv HTML, version `2310.08560v2`.

## Summary

LLMs are constrained by limited fixed-length context windows, which hinders long conversations and reasoning about long documents.[^packerMemGPTLLMsOperating2024] Extending the context length directly incurs a quadratic increase in computational time and memory cost because of self-attention, and the paper cites research showing that long-context models struggle to use additional context effectively.[^packerMemGPTLLMsOperating2024]

The paper proposes *virtual context management*, a technique inspired by hierarchical memory in traditional operating systems, which give the illusion of extended virtual memory by paging between physical memory and disk.[^packerMemGPTLLMsOperating2024] MemGPT (MemoryGPT) applies it: the LLM uses function calls to read and write external data sources, modify its own context, and choose when to return a response to the user.[^packerMemGPTLLMsOperating2024] The context window is treated as a constrained memory resource, analogous to main memory, and external storage is analogous to disk.[^packerMemGPTLLMsOperating2024]

MemGPT is evaluated in two domains: document analysis, and multi-session chat.[^packerMemGPTLLMsOperating2024] On the deep memory retrieval task, MemGPT with GPT-4 Turbo reaches 93.4% accuracy, against 35.3% for GPT-4 Turbo alone.[^packerMemGPTLLMsOperating2024]

## Contributions

- Virtual context management, and the MemGPT system that implements it with a memory hierarchy, OS-style functions, and event-based control flow.[^packerMemGPTLLMsOperating2024]
- A hierarchical tiered memory that uses a long-context LLM as the implementation of main memory, which the paper names as its main contribution relative to long-context LLM work.[^packerMemGPTLLMsOperating2024]
- Two new dialogue tasks on an expanded Multi-Session Chat dataset: deep memory retrieval (DMR) and conversation opener.[^packerMemGPTLLMsOperating2024]
- A new nested key-value retrieval task that requires multi-hop lookups.[^packerMemGPTLLMsOperating2024]
- Public release of the augmented MSC dataset, the nested KV retrieval dataset, and a dataset of embeddings for 20M Wikipedia articles.[^packerMemGPTLLMsOperating2024]

## Method

### Memory hierarchy

| Tier | OS analogy | Contents |
|---|---|---|
| Main context | main memory / physical memory / RAM | The LLM prompt tokens. Anything here is in-context and accessible to the LLM processor during inference. |
| External context | disk memory / disk storage | Information held outside the fixed context window. It must be explicitly moved into main context before the LLM can use it. |

All rows: [^packerMemGPTLLMsOperating2024]

Main context is split into three contiguous sections:[^packerMemGPTLLMsOperating2024]

- **System instructions.** Read-only (static). They describe the MemGPT control flow, the intended usage of the memory levels, and how to use the MemGPT functions.[^packerMemGPTLLMsOperating2024]
- **Working context.** A fixed-size read/write block of unstructured text, writeable only via MemGPT function calls. In conversational settings it stores key facts, preferences, and other important information about the user and the agent's persona.[^packerMemGPTLLMsOperating2024]
- **FIFO queue.** A rolling history of messages: agent and user messages, system messages (for example memory warnings), and function call inputs and outputs. The first index holds a system message with a recursive summary of evicted messages.[^packerMemGPTLLMsOperating2024]

External context has two stores:[^packerMemGPTLLMsOperating2024]

- **Recall storage.** The MemGPT message database. The queue manager writes every incoming message and every generated LLM output to it.[^packerMemGPTLLMsOperating2024]
- **Archival storage.** A read/write database storing arbitrary length text objects.[^packerMemGPTLLMsOperating2024]

### Queue manager

- On a new message, the queue manager appends it to the FIFO queue, concatenates the prompt tokens, and triggers LLM inference.[^packerMemGPTLLMsOperating2024]
- Messages retrieved from recall storage by a function call are appended to the back of the queue.[^packerMemGPTLLMsOperating2024]
- **Memory pressure warning.** When the prompt tokens exceed the "warning token count" (e.g. 70% of the context window), a system message warns the LLM of an impending eviction, so that it can store important information to working context or archival storage.[^packerMemGPTLLMsOperating2024]
- **Queue flush.** When the prompt tokens exceed the "flush token count" (e.g. 100% of the context window), the queue manager evicts a specific count of messages (e.g. 50% of the context window) and generates a new recursive summary from the existing summary and the evicted messages. Evicted messages stay in recall storage indefinitely and remain readable via function calls.[^packerMemGPTLLMsOperating2024]

### Function executor

- The LLM's completion tokens are interpreted as function calls. Memory edits and retrieval are entirely self-directed.[^packerMemGPTLLMsOperating2024]
- The system instructions hold a description of the memory hierarchy and a function schema with natural language descriptions.[^packerMemGPTLLMsOperating2024]
- In each inference cycle MemGPT parses the output string, and executes the function if the parser validates the arguments. Results, including runtime errors, are fed back to the processor.[^packerMemGPTLLMsOperating2024]
- Retrieval functions implement pagination so that retrieval calls do not overflow the context window.[^packerMemGPTLLMsOperating2024]

### Control flow and function chaining

- *Events* trigger LLM inference: user messages, system messages (for example main context capacity warnings), user interactions (for example a login alert or a finished document upload), and timed events run on a regular schedule.[^packerMemGPTLLMsOperating2024]
- A function can be called with a special flag (the keyword argument `request_heartbeat=true`) that requests control be returned to the processor right after the function completes. This chains function calls and enables multi-step retrieval.[^packerMemGPTLLMsOperating2024]
- Without the flag (a *yield*), MemGPT does not run the LLM processor until the next external event trigger.[^packerMemGPTLLMsOperating2024]

### Context windows of common models (Table 1, data collected 1/2024)

Message counts are approximate, assuming a preprompt of 1k tokens and an average message size of ∼50 tokens (∼250 characters).[^packerMemGPTLLMsOperating2024]

| Model / API name | Open? | Tokens | Messages |
|---|---|---|---|
| Llama (1) | ✓ | 2k | 20 |
| Llama 2 | ✓ | 4k | 60 |
| GPT-3.5 Turbo (release) | ✗ | 4k | 60 |
| Mistral 7B | ✓ | 8k | 140 |
| GPT-4 (release) | ✗ | 8k | 140 |
| GPT-3.5 Turbo | ✗ | 16k | 300 |
| GPT-4 | ✗ | 32k | ∼600 |
| Claude 2 | ✗ | 100k | ∼2000 |
| GPT-4 Turbo | ✗ | 128k | ∼2600 |
| Yi-34B-200k | ✓ | 200k | ∼4000 |

All rows: [^packerMemGPTLLMsOperating2024]

## Experiments & Results

### Setup

- Models: "GPT-4 Turbo" is gpt-4-1106-preview (context window of 128,000), "GPT-4" is gpt-4-0613 (context window of 8,192), and "GPT-3.5 Turbo" is gpt-3.5-turbo-1106 (context window of 16,385). MemGPT is run with all three.[^packerMemGPTLLMsOperating2024]
- Conversational dataset: [Multi-Session Chat (MSC)](../datasets/multi-session-chat.md), where each chat has five sessions of roughly a dozen messages each. The authors add a session 6 with a single question-answer pair between the same two personas.[^packerMemGPTLLMsOperating2024]

### Deep memory retrieval (Table 2)

In [DMR](../benchmarks/deep-memory-retrieval.md), the user asks a question that refers back to a prior conversation (sessions 1-5) and has a very narrow expected answer range. The QA pairs were generated by a separate LLM.[^packerMemGPTLLMsOperating2024] Accuracy comes from an LLM judge. ROUGE-L recall (R) is used because generated replies are more verbose than the gold answers.[^packerMemGPTLLMsOperating2024] The baselines see a lossy summarization of the past five conversations. MemGPT has the full conversation history but must reach it through paginated search queries.[^packerMemGPTLLMsOperating2024]

| Model | Accuracy ⇑ | ROUGE-L (R) ⇑ |
|---|---|---|
| GPT-3.5 Turbo | 38.7% | 0.394 |
| + MemGPT | 66.9% | 0.629 |
| GPT-4 | 32.1% | 0.296 |
| + MemGPT | 92.5% | 0.814 |
| GPT-4 Turbo | 35.3% | 0.359 |
| + MemGPT | 93.4% | 0.827 |

All rows: [^packerMemGPTLLMsOperating2024]

### Conversation opener (Table 3)

The agent's opener is scored by similarity to the gold persona labels (SIM-1/3) and to the human-created opener (SIM-H). The model rows are MemGPT with different underlying models.[^packerMemGPTLLMsOperating2024]

| Method | SIM-1 ⇑ | SIM-3 | SIM-H |
|---|---|---|---|
| Human | 0.800 | 0.800 | 1.000 |
| GPT-3.5 Turbo | 0.830 | 0.812 | 0.817 |
| GPT-4 | 0.868 | 0.843 | 0.773 |
| GPT-4 Turbo | 0.857 | 0.828 | 0.767 |

All rows: [^packerMemGPTLLMsOperating2024]

MemGPT's openers tend to be more verbose and cover more aspects of the persona information than the human baseline.[^packerMemGPTLLMsOperating2024]

### Multi-document question answering (Figure 5)

- Task: the retriever-reader document QA task from Liu et al. (2023a), with questions from [NaturalQuestions-Open](../datasets/natural-questions-open.md) and Wikipedia documents from a late 2018 dump. Reader accuracy is measured as the number of retrieved documents $K$ increases.[^packerMemGPTLLMsOperating2024]
- A subset of 50 questions is sampled. Answers are scored by an LLM judge.[^packerMemGPTLLMsOperating2024]
- Retriever: top-$K$ by cosine distance on OpenAI text-embedding-ada-002 embeddings. MemGPT loads the whole embedded document set into archival storage (PostgreSQL with the pgvector extension and an HNSW index) and retrieves through archival storage search.[^packerMemGPTLLMsOperating2024]
- The fixed-context baselines are capped roughly at the performance of the retriever. To run them past their default context lengths, the retrieved document segments are truncated, which reduces accuracy.[^packerMemGPTLLMsOperating2024]
- MemGPT's performance is unaffected by increased context length. MemGPT with GPT-4 and with GPT-4 Turbo have equivalent results on this task.[^packerMemGPTLLMsOperating2024]
- MemGPT has significantly degraded performance using GPT-3.5, due to its limited function calling capabilities, and performs best using GPT-4.[^packerMemGPTLLMsOperating2024]
- Accuracy values are shown only in Figure 5. The text states no numbers.

### Nested key-value retrieval (Figure 7)

- Task: keys and values are 128-bit UUIDs, and a value may itself be a key, so the agent must do a multi-hop lookup. The total number of UUID pairs is fixed to 140, roughly 8k tokens. Nesting levels vary from 0 to 4, with 30 ordering configurations sampled.[^packerMemGPTLLMsOperating2024]
- GPT-3.5 hits 0 percent accuracy at 1 nesting level. Its primary failure mode is to return the original value.[^packerMemGPTLLMsOperating2024]
- GPT-4 and GPT-4 Turbo hit 0 percent accuracy by 3 nesting levels.[^packerMemGPTLLMsOperating2024]
- MemGPT with GPT-4 is unaffected by the number of nesting levels.[^packerMemGPTLLMsOperating2024]
- MemGPT with GPT-4 Turbo and GPT-3.5 beat their baseline models but begin to drop off at 2 nesting levels because they fail to perform enough lookups. MemGPT with GPT-4 Turbo performs worse than MemGPT with GPT-4.[^packerMemGPTLLMsOperating2024]
- Other accuracy values are shown only in Figure 7.

## Limitations

- MemGPT depends on the function calling ability of the underlying model: performance degrades significantly with GPT-3.5 on document QA.[^packerMemGPTLLMsOperating2024]
- On document QA, MemGPT will often stop paging through retriever results before exhausting the retriever database, although in theory it is not limited by retriever ranking.[^packerMemGPTLLMsOperating2024]
- The document QA task is limited by embedding-based similarity search: the gold document often appears outside the first dozen retrieved results.[^packerMemGPTLLMsOperating2024]
- The document QA evaluation uses a sampled subset of 50 questions.[^packerMemGPTLLMsOperating2024]
- DMR questions are LLM-generated and scored by an LLM judge that is told to be generous in grading.[^packerMemGPTLLMsOperating2024]
- Future work named by the paper: other domains with massive or unbounded contexts, different memory tier technologies such as databases or caches, and better control flow and memory management policies.[^packerMemGPTLLMsOperating2024]
- The paper has no dedicated limitations section, and reports no latency or token cost for MemGPT's extra LLM calls.

## Related

- Methods: [MemGPT](../methods/memgpt.md), [Virtual context management](../methods/virtual-context-management.md), [Function calling](../methods/function-calling.md), [Recursive summarization](../methods/recursive-summarization.md), [Retrieval-augmented generation](../methods/retrieval-augmented-generation.md)
- Benchmarks: [Deep memory retrieval](../benchmarks/deep-memory-retrieval.md), [Nested key-value retrieval](../benchmarks/nested-kv-retrieval.md)
- Datasets: [Multi-Session Chat](../datasets/multi-session-chat.md), [NaturalQuestions-Open](../datasets/natural-questions-open.md)

[^packerMemGPTLLMsOperating2024]: Packer et al. 2024
