---
type: Open Question
title: Does offloading the KV cache to CPU memory help agentic workloads?
description: Agent-serving papers disagree on whether moving idle KV cache off the GPU during tool calls improves throughput.
tags: [kv-cache, agent-serving, llm-serving]
sources:
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
---

# Does offloading the KV cache to CPU memory help agentic workloads?

## Question

During a tool call an agent's KV cache sits idle. Should the system keep it on the GPU, drop it and recompute, or offload it to CPU memory?

## Why it matters

This choice is the main design difference between the agent-serving systems in this wiki: [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md), [ThunderAgent](../methods/thunderagent.md), SAGA, KAIROS, and MORI.

## Evidence so far

| Paper | Finding | Setting |
|---|---|---|
| [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md) | Plain swap wastes 26% GPU resources; its pipelined, chunked swap removes 96% of GPU waste for swapping | mixed augmented-LLM workload[^abhyankarInferCeptEfficientIntercept2024] |
| [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md) | LMCache offloading loses 42.1% throughput | mini-swe-agent workload[^yuanKAIROSStatefulContextAware2026] |
| [MORI](../papers/xiaIdlenessRelativeExploiting2026.md) | ThunderAgent with offloading reaches 124 tokens/s; MORI reaches 213 tokens/s | B200, 70B model, 80 programs[^xiaIdlenessRelativeExploiting2026] |

## Conflicting claims

- ThunderAgent reports that offloading degrades throughput for its workloads (figure only).[^kangThunderAgentSimpleFast2026]
- SAGA argues from transfer cost that offloading does not fit short tool calls.[^guoSAGAWorkflowAtomicScheduling2026]
- MORI reports that ranking programs by idleness and offloading the most idle ones gives 20–71% higher output throughput than ThunderAgent with offloading.[^xiaIdlenessRelativeExploiting2026]

No two papers share the backend, model, and load level. See the Contradictions section of [KV cache offloading](../methods/kv-cache-offloading.md).

## What would resolve it

One workload and one model on one GPU type, with the three policies (keep, recompute, offload) swept over tool-call duration and number of concurrent programs.

## Related

- [KV cache offloading](../methods/kv-cache-offloading.md), [KV cache swapping](../methods/kv-cache-swapping.md), [KV cache](../methods/kv-cache.md)
- [Program-aware scheduling](../methods/program-aware-scheduling.md), [ThunderAgent](../methods/thunderagent.md), [LMCache](../methods/lmcache.md)

[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
