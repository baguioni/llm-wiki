---
type: Method
title: LangChain
description: LLM orchestration framework for composing LLM calls and tools into applications, which papers in this wiki use as the application layer above serving systems and as a baseline client.
tags: [agent-framework, llm-orchestration, llm-serving, workload]
sources:
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: gaoAgentScopeFlexibleRobust2024
    resource: zotero://select/items/@gaoAgentScopeFlexibleRobust2024
    title: "AgentScope: A Flexible yet Robust Multi-Agent Platform"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
---

# LangChain

## Overview

LangChain is not the subject of any paper in this wiki. The papers here describe it as follows.

- A Python framework that provides many workflow patterns, e.g., chain and map-reduce, so that developers can customize their own LLM applications. Parrot calls it the predominant framework for LLM application development.[^linParrotEfficientServing2024]
- A framework for building applications that are context-aware and capable of reasoning, with libraries and templates that integrate multiple components. LangServe and LangSmith extend it with deployment as a REST API and developer tools for debugging and monitoring chains.[^gaoAgentScopeFlexibleRobust2024]
- An agentic orchestration framework that gives developers primitives to manage a program's control flow: when to execute agents, invoke tools, or request human input.[^luoAutellixEfficientServing]
- A high-level programming system for LLMs (grouped with DSPy), as opposed to low-level systems such as LMQL, Guidance, and [SGLang](../methods/sglang.md).[^zhengSGLangEfficientExecution2024]
- One of the frameworks that provide programming models for users to write their own flows of augmented LLMs.[^abhyankarInferCeptEfficientIntercept2024]
- One of the agent frameworks that adopted the [ReAct](../methods/react.md) loop of Thought, Action, and Observation.[^guoSAGAWorkflowAtomicScheduling2026]

## How it works

Only two mechanisms are described by the papers.

- **Prompt templates.** LangChain allows placeholders in a prompt, and the placeholders are rendered with real data before submission. The LLM service therefore loses the information on the prompt structure.[^linParrotEfficientServing2024]
- **Callbacks.** LangChain exposes orchestration metadata through callbacks, which a scheduler can read as explicit hints about the workflow.[^guoSAGAWorkflowAtomicScheduling2026]

## Papers using it

| Paper | How it uses LangChain | Reported numbers |
|---|---|---|
| [Parrot](../papers/linParrotEfficientServing2024.md) | Baseline client: the majority of baseline applications are developed with LangChain and call OpenAI-style chat completion APIs served by FastChat. Parrot states that it is compatible with LangChain, that it supports most of LangChain's output parsing methods, and that integration needs the template and its variables to be wrapped as a SemanticFunction. | none specific to LangChain |
| [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md) | Workflow source: the agent interface layer receives requests from LangChain and [AutoGen](../methods/autogen.md) and builds Agent Execution Graphs. LangChain callbacks are an explicit-hint source that delivers the graph at task admission. | With hints: TCT 203.4$\pm$12.8 s, 100% AEG accuracy. Pattern inference without hints: 235.2$\pm$14.6 s, 87% accuracy, +15.6% |
| [AgentScope](../papers/gaoAgentScopeFlexibleRobust2024.md) | Compatibility target for its [RAG](../methods/retrieval-augmented-generation.md) module, alongside LlamaIndex, and a related-work entry. | none |
| [Autellix](../papers/luoAutellixEfficientServing.md) | Example of an agentic orchestration framework. | none |
| [SGLang](../papers/zhengSGLangEfficientExecution2024.md) | Example of a high-level LLM programming system in related work. | none |
| [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md) | Example of a framework for composing augmented LLM flows. | none |

Row 1: [^linParrotEfficientServing2024]. Row 2: [^guoSAGAWorkflowAtomicScheduling2026]. Row 3: [^gaoAgentScopeFlexibleRobust2024]. Row 4: [^luoAutellixEfficientServing]. Row 5: [^zhengSGLangEfficientExecution2024]. Row 6: [^abhyankarInferCeptEfficientIntercept2024]

SAGA's hint comparison (its Table 5) does not say which framework supplied the hints, so the numbers are for framework hints in general.[^guoSAGAWorkflowAtomicScheduling2026]

## Strengths & Limitations

- Because templates are rendered before submission, public LLM services cannot detect the prompt structure of LangChain applications.[^linParrotEfficientServing2024]
- Agent frameworks such as LangChain provide high-level orchestration but delegate inference scheduling entirely to the underlying serving system.[^guoSAGAWorkflowAtomicScheduling2026]

## Related

- Other agent frameworks: [AutoGen](../methods/autogen.md), [MetaGPT](../methods/metagpt.md)
- Concepts: [ReAct](../methods/react.md), [Retrieval-augmented generation](../methods/retrieval-augmented-generation.md), [Program-aware scheduling](../methods/program-aware-scheduling.md), [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)

[^linParrotEfficientServing2024]: Lin et al. 2024
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^gaoAgentScopeFlexibleRobust2024]: Gao et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
