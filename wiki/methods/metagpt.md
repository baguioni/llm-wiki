---
type: Method
title: MetaGPT
description: Multi-agent framework that assigns software-development roles to LLMs, used by LLM serving papers in this wiki as a multi-agent programming workload.
tags: [multi-agent, agent-framework, llm-serving, workload]
sources:
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
  - id: gaoAgentScopeFlexibleRobust2024
    resource: zotero://select/items/@gaoAgentScopeFlexibleRobust2024
    title: "AgentScope: A Flexible yet Robust Multi-Agent Platform"
---

# MetaGPT

## Overview

MetaGPT is not the subject of any paper in this wiki. The papers here describe it as follows.

- A multi-agent framework designed to simulate an AI software development company, in which different roles are defined for each LLM.[^agarwalSYMPHONYImprovingMemory2024]
- A framework that incorporates meta-programming to enhance multi-agent collaborations. It encodes Standardized Operating Procedures (SOP) into prompts.[^gaoAgentScopeFlexibleRobust2024]
- A multi-agent application in which roles such as product manager, architect, engineer, and QA tester communicate with each other on a software project, each role supported by one or multiple LLM requests.[^linParrotEfficientServing2024]

## How it works

The papers describe the workflow they run, not MetaGPT's internals.

| Paper | Roles and workflow |
|---|---|
| Symphony | Three main roles: an architect who defines the project, designs data structures and APIs, and writes multiple design documents; engineers who take over coding tasks, each focusing on specific files; and QA engineers who review the code, followed by engineers making revisions. The review and revision cycle occurs three times.[^agarwalSYMPHONYImprovingMemory2024] |
| Parrot | A workflow with three roles: the Architect outlines the project's file structures and specifies APIs within each file; multiple Coders each implement a specific file; several Reviewers each examine and comment on a single file, and the Coders revise their code based on the comments. The review-and-revision cycle is iterated three times.[^linParrotEfficientServing2024] |

MetaGPT recurrently incorporates conversation history into the prompt over several rounds of LLM requests.[^linParrotEfficientServing2024]

## Papers using it

| Paper | What it is used for | Setting | Reported numbers |
|---|---|---|---|
| [Parrot](../papers/linParrotEfficientServing2024.md) | Workload statistics (Table 1) | not stated | 14 LLM calls, 17k tokens, 72% repeated (a paragraph counts as repeated if it appears in at least two LLM requests) |
| [Parrot](../papers/linParrotEfficientServing2024.md) | Multi-agent programming evaluation, with a varying number of files to program | one A100 running LLaMA 13B | speedup of up to $11.7\times$ over the latency-centric baseline; faster by up to $2.45\times$ than the throughput-centric baseline; prompt structure analysis contributes a $2.35\times$ acceleration; Parrot's GPU kernel for the shared prefix gives a further $1.2\times$ speedup at 16 files compared to vLLM's PagedAttention |
| [Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md) | Advisory request lead time | MetaGPT served using 4 A100s | advisory requests can be issued on average 5.8 seconds earlier than the actual inference request |
| [Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md) | Agent workload evaluation vs [vLLM](../methods/vllm.md) | LLaMa-3.1-8b across 8 GPUs | overall time reduced by $2.8\times$ |
| [AgentScope](../papers/gaoAgentScopeFlexibleRobust2024.md) | Related work only | n/a | none |

Parrot rows: [^linParrotEfficientServing2024]. Symphony rows: [^agarwalSYMPHONYImprovingMemory2024]. AgentScope row: [^gaoAgentScopeFlexibleRobust2024]

Why the serving systems gain on this workload:

- Parrot identifies task groups within the parallel coding, reviewing, and revising steps, which allows larger batch sizes. The roles share considerable context, which Parrot shares as a prompt prefix. Without this sharing, Parrot would hit the GPU memory ceiling.[^linParrotEfficientServing2024]
- Symphony attributes its gain to advisory requests, which enable K,V cache offloading and request load balancing. It calls MetaGPT an interactive workload, with documents and reviews shared among engineers and QA.[^agarwalSYMPHONYImprovingMemory2024]

## Strengths & Limitations

- AgentScope's related work credits the SOP encoding with streamlined workflows and reduced errors, and calls it an example of effective task decomposition among agents.[^gaoAgentScopeFlexibleRobust2024]
- From a serving point of view, 72% of its paragraphs are repeated across LLM requests, so the redundant sections are computed multiple times unless the serving system shares them.[^linParrotEfficientServing2024]
- The two serving results are not comparable: Parrot and Symphony use different models, GPU counts, baselines, and metrics (see the table above).

## Related

- Other agent frameworks: [AutoGen](../methods/autogen.md), [LangChain](../methods/langchain.md)
- Serving concepts: [Prefix caching](../methods/prefix-caching.md), [KV cache](../methods/kv-cache.md), [KV cache offloading](../methods/kv-cache-offloading.md), [PagedAttention](../methods/paged-attention.md), [vLLM](../methods/vllm.md)
- Papers: [Parrot](../papers/linParrotEfficientServing2024.md), [Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md), [AgentScope](../papers/gaoAgentScopeFlexibleRobust2024.md)

[^linParrotEfficientServing2024]: Lin et al. 2024
[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
[^gaoAgentScopeFlexibleRobust2024]: Gao et al. 2024
