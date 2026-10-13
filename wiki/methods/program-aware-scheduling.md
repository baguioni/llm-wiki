---
type: Method
title: Program-aware scheduling
description: Scheduling LLM serving at the level of the agentic program (all model invocations and tool calls of one agent workflow) instead of the individual request.
tags: [llm-serving, agentic-inference, scheduling, kv-cache, load-balancing]
sources:
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
---

# Program-aware scheduling

## Overview

An inference engine sees only individual requests. A program-aware scheduler recognizes requests as parts of the same program, with prefix dependencies across requests and a persistent memory working set.[^xiaIdlenessRelativeExploiting2026] An *agentic program* is the complete sequence of model invocations of one agent session together with the interleaved tool calls.[^xiaIdlenessRelativeExploiting2026] Autellix defines it as a dynamic execution workflow, represented by a DAG, of LLM calls from one or more agents and external interrupts.[^luoAutellixEfficientServing]

The motivation differs by paper:

- **Queueing.** Engines that optimize individual LLM calls cause head-of-line blocking at both the call level and the program level.[^luoAutellixEfficientServing]
- **Memory.** Systems that schedule per request, without end-to-end knowledge of the workflow, manage [KV cache](../methods/kv-cache.md) and tool environments sub-optimally. Request-aware schedulers cannot distinguish temporary tool waits from termination.[^kangThunderAgentSimpleFast2026] Without program-level awareness, concurrent programs evict each other's KV caches during tool-call gaps, which causes thrashing, so the program must be the unit of memory management.[^xiaIdlenessRelativeExploiting2026]

## How it works

Common elements across the systems:

- **Program identity on each request.** ThunderAgent and MORI require a `program_id` on requests.[^kangThunderAgentSimpleFast2026][^xiaIdlenessRelativeExploiting2026] Autellix has the program establish a session and annotates LLM calls with session, program, and thread IDs.[^luoAutellixEfficientServing]
- **Per-program state.** Autellix keeps a global process table with service time, waiting time, engine IDs, and thread metadata per program.[^luoAutellixEfficientServing] ThunderAgent tracks context tokens, tool environments, backend placement, execution phase (Reasoning or Acting), and scheduling status.[^kangThunderAgentSimpleFast2026] MORI tracks a Reasoning or Acting status and the time spent in each over the last $k$ cycles.[^xiaIdlenessRelativeExploiting2026]
- **A program-level decision rule.** See Variants.
- **Program-level routing across replicas.** Autellix pins calls longer than 2048 tokens to the engine already assigned to the program.[^luoAutellixEfficientServing] ThunderAgent shares one global waiting queue across replicas so a paused program can resume on any replica.[^kangThunderAgentSimpleFast2026] MORI keeps per-replica GPU and CPU queues plus one global Waiting queue, and prefers the replica that holds a program's offloaded cache.[^xiaIdlenessRelativeExploiting2026]

## Variants

| System | What the scheduler decides | Decision signal | Needs workflow structure in advance |
|---|---|---|---|
| Autellix (PLAS, ATLAS) | Priority and preemption of LLM calls | Total execution time of the program's previously completed calls (PLAS); longest observed critical path (ATLAS) | No (non-clairvoyant) |
| [ThunderAgent](../methods/thunderagent.md) | Which programs to pause and restore, and on which node | Execution phase first, then context length (shortest first), with time decay on acting programs | No |
| MORI | Which memory tier (GPU HBM, CPU DRAM, or discarded) holds each program's KV cache | Continuous idleness $\iota$ over the last $k{=}5$ cycles, ranked across programs | No |
| SAGA | Dispatch of a whole Agent Execution Graph as one schedulable unit, with workflow-aware eviction, tool-aware TTL, and fairness | Workflow DAG from framework hints or pattern inference | Best with hints; falls back to pattern inference |

Row 1: [^luoAutellixEfficientServing]. Row 2: [^kangThunderAgentSimpleFast2026]. Row 3: [^xiaIdlenessRelativeExploiting2026]. Row 4: [^guoSAGAWorkflowAtomicScheduling2026]

SAGA's own comparison of "directly related program-aware LLM serving systems" (its Table 11):[^guoSAGAWorkflowAtomicScheduling2026]

| System | Venue | Distributed scheduling | Tool TTL policies | Fairness guarantee | Competitive ratio |
|---|---|---|---|---|---|
| Parrot | OSDI'24 | $\times$ | $\times$ | $\times$ | $\times$ |
| Autellix | arXiv'25 | ✓ | $\times$ | $\times$ | $\times$ |
| Pie | SOSP'25 | $\times$ | ✓ | $\times$ | $\times$ |
| KVFlow | NeurIPS'25 | $\times$ | ✓ | $\times$ | $\times$ |
| SAGA | This work | ✓ | ✓ | ✓ | ✓ |

## Papers using it

- **[Autellix](../papers/luoAutellixEfficientServing.md)** presents a program-aware scheduler that reduces call-level and program-level blocking. It reports 4-15× higher program throughput at the same latency compared to systems such as [vLLM](../methods/vllm.md), and up to 1.5x over standard load balancers across engines.[^luoAutellixEfficientServing]
- **[ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md)** applies it to KV cache thrashing and cross-node memory imbalance. It reports 1.48–3.58$\times$ serving throughput over vLLM and 1.79–3.92$\times$ in RL rollout. In its component ablation (2$\times$H100, GLM-4.5-fp8, mini-SWEAgent, 144 concurrent programs), local program-aware scheduling raises throughput from 375 to 602 steps/min (1.61$\times$), and the global waiting queue adds a further 1.12$\times$ (602 to 672).[^kangThunderAgentSimpleFast2026]
- **[MORI](../papers/xiaIdlenessRelativeExploiting2026.md)** is a program-aware scheduler with explicit KV cache placement across GPU HBM and CPU DRAM ([KV cache offloading](../methods/kv-cache-offloading.md)). It measures the effect of program-aware scheduling alone through its ThunderAgent baseline (TA) against SGLang Model Gateway (SMG), a prefix-aware request scheduler: on H200 (80 GB) with Qwen-2.5 7B at 80 programs, TA reaches 557 tokens/s and SMG 447 tokens/s, and on B200 at 80 programs TA's average TTFT is 73 s and SMG's is 108 s. At 20 programs with DP=3, program-aware routing gives 9–10 running requests per engine and 99%+ GPU utilization, while SMG reaches 51%.[^xiaIdlenessRelativeExploiting2026]
- **[SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md)** treats agent programs as first-class schedulable units. It reports $1.73\times\pm 0.11$ and $1.55\times\pm 0.09$ task completion time reductions on [SWE-bench](../benchmarks/swe-bench.md) and [WebArena](../benchmarks/webarena.md) over vLLM v0.15.1 with Automatic Prefix Caching.[^guoSAGAWorkflowAtomicScheduling2026]

## Strengths & Limitations

Strengths:

- Works as a layer over existing engines. ThunderAgent decouples scheduling from backends such as vLLM, [SGLang](../methods/sglang.md), and TensorRT-LLM, and Autellix modifies only the scheduler of vLLM.[^kangThunderAgentSimpleFast2026][^luoAutellixEfficientServing]
- Within a single program, prefix cache-hit rates remain above 90% across all input lengths, so keeping a program's calls together preserves locality.[^luoAutellixEfficientServing]

Limitations:

- The client must tag requests with a program or session identifier.[^kangThunderAgentSimpleFast2026][^xiaIdlenessRelativeExploiting2026][^luoAutellixEfficientServing]
- Program-aware scheduling that keeps the working set in GPU HBM confines it to that capacity: the context of a program that does not fit is evicted entirely and later recomputed.[^xiaIdlenessRelativeExploiting2026]
- Choosing eviction candidates by static properties such as context length may keep a program blocked on a long tool call in GPU memory while evicting one that is about to resume.[^xiaIdlenessRelativeExploiting2026]
- Methods that take a fixed workflow structure into account are less effective when agent structures become more complex and dynamic.[^xiaIdlenessRelativeExploiting2026] SAGA reports 15.6% task completion time degradation with pattern inference compared to explicit hints (235.2$\pm$14.6 s vs 203.4$\pm$12.8 s), and further degradation on dynamic multi-agent frameworks.[^guoSAGAWorkflowAtomicScheduling2026]
- In simulation a noticeable gap remains between Autellix and the clairvoyant SRPT policy.[^luoAutellixEfficientServing]

# Contradictions

**How Autellix manages KV cache.** MORI lists Autellix (Luo et al., 2025) among recent program-aware systems "which pin a program's KV cache in GPU HBM across tool calls to prevent eviction during short gaps that would otherwise cause thrashing".[^xiaIdlenessRelativeExploiting2026] ThunderAgent states that Autellix models workflows as GPU-only programs and "ignores workflow locality, allowing concurrent workflows to aggressively evict other's KV cache, triggering KV cache thrashing under heavy workloads".[^kangThunderAgentSimpleFast2026] Autellix's own description is a scheduler that prioritizes calls by program-level attained service and swaps KV cache between GPU and CPU under preemption. The only pinning it describes is in its load balancer, which pins longer requests to their program's engine.[^luoAutellixEfficientServing] Neither MORI nor ThunderAgent runs Autellix as a baseline, so neither characterization comes with a measurement.

**Scope of the term.** SAGA's Table 11 calls Parrot, Autellix, Pie, and KVFlow program-aware systems.[^guoSAGAWorkflowAtomicScheduling2026] MORI groups Parrot with methods that take a fixed workflow structure into account, separately from the program-aware systems it names (ThunderAgent, Continuum, Autellix, Pie).[^xiaIdlenessRelativeExploiting2026]

**Autellix fairness.** SAGA's related-work text says Autellix "proposes program-level fairness", and its Table 11 marks Autellix with $\times$ under "Fairness Guarantee".[^guoSAGAWorkflowAtomicScheduling2026] Autellix includes an anti-starvation mechanism that promotes a call when its ratio of waiting time to service time reaches a threshold $\beta$.[^luoAutellixEfficientServing] The table column is about a formal guarantee, so the two statements can both hold.

## Related

- Systems: [ThunderAgent](../methods/thunderagent.md), [vLLM](../methods/vllm.md), [SGLang](../methods/sglang.md)
- Memory: [KV cache](../methods/kv-cache.md), [KV cache offloading](../methods/kv-cache-offloading.md), [KV cache swapping](../methods/kv-cache-swapping.md), [Prefix caching](../methods/prefix-caching.md)
- Agent frameworks that supply workflow structure: [LangChain](../methods/langchain.md), [AutoGen](../methods/autogen.md)
- Papers: [Autellix](../papers/luoAutellixEfficientServing.md), [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md), [MORI](../papers/xiaIdlenessRelativeExploiting2026.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [Parrot](../papers/linParrotEfficientServing2024.md)

[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^luoAutellixEfficientServing]: Luo et al.
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
