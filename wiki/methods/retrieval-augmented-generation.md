---
type: Method
title: Retrieval-Augmented Generation
description: Approach that retrieves relevant external documents and inserts them into the LLM prompt before generation, used in this wiki's papers as a framework module, a non-interactive baseline, and the starting point for agent memory systems.
tags: [retrieval, rag, agent-memory, llm-agents, baseline]
sources:
  - id: gaoAgentScopeFlexibleRobust2024
    resource: zotero://select/items/@gaoAgentScopeFlexibleRobust2024
    title: "AgentScope: A Flexible yet Robust Multi-Agent Platform"
  - id: yangSWEagentAgentComputerInterfaces2024
    resource: zotero://select/items/@yangSWEagentAgentComputerInterfaces2024
    title: "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"
  - id: packerMemGPTLLMsOperating2024
    resource: zotero://select/items/@packerMemGPTLLMsOperating2024
    title: "MemGPT: Towards LLMs as Operating Systems"
  - id: rasmussenZepTemporalKnowledge2025
    resource: zotero://select/items/@rasmussenZepTemporalKnowledge2025
    title: "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
---

# Retrieval-Augmented Generation

## Overview

Retrieval-augmented generation (RAG) supplies an LLM with knowledge that is not in its training data, such as knowledge in highly professional domains or knowledge that is not publicly available, without fine-tuning or re-training the model.[^gaoAgentScopeFlexibleRobust2024] Zep describes it as using information retrieval techniques to supply necessary domain knowledge to LLMs.[^rasmussenZepTemporalKnowledge2025]

## How it works

AgentScope describes RAG as a pre-processing step inserted into the usual LLM pipeline: given a collection of documents, a similarity-based index is built, and the user input is combined with the most relevant pieces of information, converted into a prompt, and fed to the LLM.[^gaoAgentScopeFlexibleRobust2024] The phases it lists are:[^gaoAgentScopeFlexibleRobust2024]

1. Collection of the documents that contain the necessary information.
2. Segmentation of the documents.
3. Indexing of the segments (chunks or nodes).
4. Similarity-based index retrieval.
5. Fusion of the original query and the retrieved results.
6. Composition of the prompt.
7. Generation of the response by the LLM.

Retrievers that appear in the wiki's papers:

- BM25 over codebase files, with the issue text as the query (the SWE-bench RAG baseline).[^yangSWEagentAgentComputerInterfaces2024]
- Top-$K$ by cosine distance on OpenAI text-embedding-ada-002 embeddings (MemGPT's document QA baseline).[^packerMemGPTLLMsOperating2024]
- Cosine semantic similarity search, Okapi BM25 full-text search, and breadth-first search within $n$-hops over a knowledge graph (Zep).[^rasmussenZepTemporalKnowledge2025]

## Variants

- **Non-interactive RAG.** A retriever fetches files once and the model directly generates the output, with no further interaction with the environment.[^yangSWEagentAgentComputerInterfaces2024]
- **Retriever-reader.** A retriever selects documents for a question and a reader LLM answers from them. The top-$K$ documents are fetched independently from the LLM inference.[^packerMemGPTLLMsOperating2024]
- **Self-directed, paginated retrieval.** In [MemGPT](memgpt.md) the LLM issues retrieval calls itself through function calls and can page through results, so it can make multiple calls to the retriever.[^packerMemGPTLLMsOperating2024]
- **Knowledge banks shared across agents.** AgentScope groups RAG objects, each with a unique `knowledge_id`, an index, and a retriever, so that agents share knowledge without recomputing indexes.[^gaoAgentScopeFlexibleRobust2024]
- **Graph-based RAG.** Zep states that knowledge graphs have been employed to enhance RAG architectures and address shortcomings of traditional information retrieval techniques. Its community nodes build on GraphRAG.[^rasmussenZepTemporalKnowledge2025]

## Papers using it

### AgentScope: RAG as a platform module

[AgentScope](../papers/gaoAgentScopeFlexibleRobust2024.md) provides configurable and sharable knowledge processing modules for RAG, from data preprocessing to customizable retrieval.[^gaoAgentScopeFlexibleRobust2024]

- A single `.json` file groups all RAG-related configuration.[^gaoAgentScopeFlexibleRobust2024]
- A RAG agent can load several RAG objects, update knowledge (insert, delete, or replace pieces), and set weights for the results retrieved from different RAG objects.[^gaoAgentScopeFlexibleRobust2024]
- The design is meant to be compatible with RAG frameworks such as LlamaIndex and [LangChain](langchain.md).[^gaoAgentScopeFlexibleRobust2024]
- Application example: AgentScope Copilot, a multi-agent copilot built from LlamaIndex-based RAG agents, where a guide agent picks the most suitable agent when the user does not mention one.[^gaoAgentScopeFlexibleRobust2024]
- The paper reports no accuracy numbers for its RAG module.

### SWE-agent: RAG as the non-interactive baseline

[SWE-agent](../papers/yangSWEagentAgentComputerInterfaces2024.md) compares against the RAG baselines established in SWE-bench: a BM25 retrieval system retrieves the most relevant codebase files using the issue as the query, and the model directly generates a patch file.[^yangSWEagentAgentComputerInterfaces2024]

| Setting | [SWE-bench](../benchmarks/swe-bench.md) % Resolved | SWE-bench $ Avg. Cost | [SWE-bench Lite](../benchmarks/swe-bench-lite.md) % Resolved | SWE-bench Lite $ Avg. Cost |
|---|---|---|---|---|
| RAG w/ GPT-4 Turbo | 1.31 | 0.13 | 2.67 | 0.13 |
| RAG w/ Claude 3 Opus | 3.79 | 0.25 | 4.33 | 0.25 |
| [SWE-agent](swe-agent.md) w/ GPT-4 Turbo | 12.47 | 1.59 | 18.00 | 1.67 |
| SWE-agent w/ Claude 3 Opus | 10.46 | 2.59 | 13.00 | 2.18 |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

- The paper's introduction gives the previous best resolve rate, by a non-interactive, retrieval-augmented system, as 3.8%.[^yangSWEagentAgentComputerInterfaces2024]
- Compared to RAG on Lite, SWE-agent is 8-13x more costly but yields a 6.7-fold improved % Resolved rate.[^yangSWEagentAgentComputerInterfaces2024]
- File localization: SWE-agent w/ GPT-4 Turbo reaches an F1 score of 59.05% between the files it edits and the files of the gold patch, while BM25 w/ Claude 3 Opus reaches 45.47%.[^yangSWEagentAgentComputerInterfaces2024]
- Agent-generated patches tend to be larger than the gold solution, while the RAG baselines typically produce smaller edits on average.[^yangSWEagentAgentComputerInterfaces2024]
- SWE-agent resolves problems in repositories that the RAG baselines left nearly or completely unsolved, for example matplotlib and sympy.[^yangSWEagentAgentComputerInterfaces2024]

### MemGPT: retrieval under the LLM's control

[MemGPT](../papers/packerMemGPTLLMsOperating2024.md) states that the design of its external memory builds upon prior work that augments LLMs with relevant inputs from external retrievers.[^packerMemGPTLLMsOperating2024]

- On the multi-document QA task, the fixed-context baselines follow the retriever-reader setup and are capped roughly at the performance of the retriever: if the embedding search does not surface the gold article, the baseline never sees it.[^packerMemGPTLLMsOperating2024]
- MemGPT loads the whole embedded document set into archival storage and retrieves through archival storage search, so the number of documents available to it is not limited by what fits in the context window.[^packerMemGPTLLMsOperating2024]
- The gold document often appears outside the first dozen retrieved results.[^packerMemGPTLLMsOperating2024]
- MemGPT often stops paging through retriever results before exhausting the retriever database.[^packerMemGPTLLMsOperating2024]
- Accuracy for this task is shown only in a figure of the paper.

### Zep: RAG is too static for agent memory

[Zep](../papers/rasmussenZepTemporalKnowledge2025.md) argues that current RAG approaches have focused on broad domain knowledge and largely static corpora, and that they are unsuitable for agents that need a continuously evolving memory built from conversations and business data.[^rasmussenZepTemporalKnowledge2025] Its answer is a temporally-aware knowledge graph. The paper describes its bi-temporal model as what sets Zep apart from previous graph-based RAG proposals.[^rasmussenZepTemporalKnowledge2025]

- On LongMemEval, Zep's retrieved context averages 1.6k tokens against 115k for the full-context baseline. Accuracy is 63.8% against 55.4% with gpt-4o-mini and 71.2% against 60.2% with gpt-4o.[^rasmussenZepTemporalKnowledge2025]
- Zep's traditional RAG capabilities are not evaluated against established RAG benchmarks. The authors name this as future work.[^rasmussenZepTemporalKnowledge2025]

## Strengths & Limitations

- AgentScope states that RAG gives LLMs customized domain knowledge at low cost, and that with it hallucination could be avoided and factual accuracy significantly improved. The paper gives no measurement for this.[^gaoAgentScopeFlexibleRobust2024]
- Configuration of a RAG pipeline is complex, which is the reason AgentScope gives for its one-file configuration.[^gaoAgentScopeFlexibleRobust2024]
- A one-shot retrieval bounds the downstream model by the retriever: this is seen in MemGPT's fixed-context baselines and in the BM25 localization score in SWE-agent.[^packerMemGPTLLMsOperating2024][^yangSWEagentAgentComputerInterfaces2024]
- It is cheap compared with an interactive agent ($0.13 to $0.25 per SWE-bench instance against $1.59 to $2.59) but resolves far fewer issues.[^yangSWEagentAgentComputerInterfaces2024]
- Zep argues that RAG over static corpora does not cover continuously changing conversational and business data.[^rasmussenZepTemporalKnowledge2025]
- Zep notes that the literature on LLM memory and RAG systems insufficiently addresses cost and latency at production scale.[^rasmussenZepTemporalKnowledge2025]

## Related

- Methods: [MemGPT](memgpt.md), [SWE-agent](swe-agent.md), [LangChain](langchain.md)
- Benchmarks: [SWE-bench](../benchmarks/swe-bench.md), [SWE-bench Lite](../benchmarks/swe-bench-lite.md), [Deep Memory Retrieval](../benchmarks/deep-memory-retrieval.md)

[^gaoAgentScopeFlexibleRobust2024]: Gao et al. 2024
[^yangSWEagentAgentComputerInterfaces2024]: Yang et al. 2024
[^packerMemGPTLLMsOperating2024]: Packer et al. 2024
[^rasmussenZepTemporalKnowledge2025]: Rasmussen et al. 2025
