---
type: Method
title: AutoGen
description: Multi-agent conversation framework that papers in this wiki cite as a source of agent workflows and as an example of a dynamic multi-agent workload for LLM serving.
tags: [multi-agent, agent-framework, llm-serving, workload]
sources:
  - id: gaoAgentScopeFlexibleRobust2024
    resource: zotero://select/items/@gaoAgentScopeFlexibleRobust2024
    title: "AgentScope: A Flexible yet Robust Multi-Agent Platform"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: wangAgentDropoutDynamicAgent2025
    resource: zotero://select/items/@wangAgentDropoutDynamicAgent2025
    title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
---

# AutoGen

## Overview

AutoGen is not the subject of any paper in this wiki. The papers here describe it as follows.

- A generic infrastructure that lets developers program interaction patterns using both natural language and code. It facilitates conversation among agents that are customizable and can use various combinations of LLMs, human inputs, and tools.[^gaoAgentScopeFlexibleRobust2024]
- An agentic orchestration framework that gives developers primitives to manage a program's control flow.[^luoAutellixEfficientServing]
- A multi-agent application in which roles such as product manager, architect, engineer, and QA tester communicate with each other on a software project.[^linParrotEfficientServing2024]
- A method that implicitly incorporates graph structures to model simultaneous conversations.[^wangAgentDropoutDynamicAgent2025]
- One of the agent frameworks that adopted the [ReAct](../methods/react.md) loop.[^guoSAGAWorkflowAtomicScheduling2026]

## How it works

The papers state two properties.

- AutoGen recurrently incorporates conversation history into the prompt over several rounds of LLM requests.[^linParrotEfficientServing2024]
- AutoGen exposes message logs, which a scheduler can read as explicit hints about the workflow.[^guoSAGAWorkflowAtomicScheduling2026] SAGA also names AutoGen, with CrewAI, as a dynamic multi-agent framework where structure is generated on the fly through agent-to-agent debate.[^guoSAGAWorkflowAtomicScheduling2026]

## Papers using it

| Paper | How it uses AutoGen | Reported numbers |
|---|---|---|
| [Parrot](../papers/linParrotEfficientServing2024.md) | Workload statistics (Table 1). Parrot's multi-agent evaluation uses [MetaGPT](../methods/metagpt.md), not AutoGen. | 17 LLM calls, 57k tokens, 99% repeated (a paragraph counts as repeated if it appears in at least two LLM requests) |
| [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md) | Workflow source: the agent interface layer receives requests from [LangChain](../methods/langchain.md) and AutoGen and builds Agent Execution Graphs. AutoGen message logs are an explicit-hint source. | Without hints SAGA falls back to pattern inference with 12 to 18% TCT degradation, and it degrades further on dynamic multi-agent frameworks (AutoGen, CrewAI); no AutoGen-specific number is given |
| [AgentScope](../papers/gaoAgentScopeFlexibleRobust2024.md) | Related work on multi-agent frameworks. | none |
| [Autellix](../papers/luoAutellixEfficientServing.md) | Example of an agentic orchestration framework. | none |
| [AgentDropout](../papers/wangAgentDropoutDynamicAgent2025.md) | Related work on communication structures. | none |
| [SGLang](../papers/zhengSGLangEfficientExecution2024.md) | Listed among LLM programming and agent frameworks; SGLang states it is compatible with other frameworks and can accelerate them. | none |

Row 1: [^linParrotEfficientServing2024]. Row 2: [^guoSAGAWorkflowAtomicScheduling2026]. Row 3: [^gaoAgentScopeFlexibleRobust2024]. Row 4: [^luoAutellixEfficientServing]. Row 5: [^wangAgentDropoutDynamicAgent2025]. Row 6: [^zhengSGLangEfficientExecution2024]

## Strengths & Limitations

- From a serving point of view, 99% of its paragraphs are repeated across LLM requests, the highest redundancy in Parrot's table (MetaGPT 72%, chat search 94%, long document analytics 3%).[^linParrotEfficientServing2024]
- Workflow-aware schedulers have difficulty with it: its structure is generated on the fly, which requires re-inference of the execution graph per epoch in SAGA.[^guoSAGAWorkflowAtomicScheduling2026]
- Like other agent frameworks, it delegates inference scheduling entirely to the underlying serving system.[^guoSAGAWorkflowAtomicScheduling2026]

# Contradictions

**How much workflow structure AutoGen gives a scheduler.** Within SAGA, AutoGen message logs are listed as explicit hints that deliver the Agent Execution Graph at task admission, and AutoGen is also named as a framework where structure is generated on the fly, requiring re-inference per epoch.[^guoSAGAWorkflowAtomicScheduling2026] Both statements are in the same paper. The paper does not report a measurement on AutoGen that would show which case dominates.

## Related

- Other agent frameworks: [MetaGPT](../methods/metagpt.md), [LangChain](../methods/langchain.md)
- Concepts: [ReAct](../methods/react.md), [Program-aware scheduling](../methods/program-aware-scheduling.md), [Prefix caching](../methods/prefix-caching.md), [SGLang](../methods/sglang.md)

[^gaoAgentScopeFlexibleRobust2024]: Gao et al. 2024
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^linParrotEfficientServing2024]: Lin et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^wangAgentDropoutDynamicAgent2025]: Wang et al. 2025
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
