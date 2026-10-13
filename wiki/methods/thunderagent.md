---
type: Method
title: ThunderAgent
description: Agentic inference system that schedules whole agent workflows as programs, pausing and restoring them by execution phase and context length to avoid KV cache thrashing, with a global waiting queue across GPU nodes and lifecycle-aware tool resource management.
tags: [llm-serving, agentic-inference, kv-cache, scheduling, program-aware-scheduling, system]
sources:
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# ThunderAgent

## Overview

ThunderAgent is an agentic inference system that abstracts an agentic workflow as an *agentic program*, a scheduling unit that persists across model invocations and tool executions. On top of this abstraction it adds a [program-aware scheduler](../methods/program-aware-scheduling.md) and a tool resource manager.[^kangThunderAgentSimpleFast2026] It targets three problems that the paper measures in a [vLLM](../methods/vllm.md) + Kubernetes baseline: KV cache thrashing (end-to-end latency of each request increases by up to 7.14$\times$ compared to a non-thrashing setting), cross-node memory imbalance, and tool lifecycle obliviousness.[^kangThunderAgentSimpleFast2026]

It is a runtime layer between agent control flow and backend inference engines. It wraps existing engines and tool orchestrators through OpenAI-style endpoints, and adoption requires attaching `program_id` to requests and sending an explicit release signal when a program ends.[^kangThunderAgentSimpleFast2026]

## How it works

- **Program.** $P=\langle\mathit{ID},c,\mathcal{T},\mathcal{L},\tau,s\rangle$: a global identifier, the number of tokens in the context, the tool environments, the backend placement, the execution phase (Reasoning **R** or Acting **A**), and the scheduling status (Active, Paused, Terminated).[^kangThunderAgentSimpleFast2026]
- **Cost model.** The Space-Time Product integrates [KV cache](../methods/kv-cache.md) memory (in tokens) over time. Total cost is decomposed into decode, prefill, recompute, unused, and caching terms. Recompute comes from thrashing, unused from memory imbalance across replicas, and caching from holding memory during tool execution.[^kangThunderAgentSimpleFast2026]
- **Pause and Restore.** Pause unbinds an Active program from its backend and releases its KV cache for preemption. Restore assigns a Paused program to a backend with available capacity.[^kangThunderAgentSimpleFast2026]
- **Periodic thrashing detection.** A backend is thrashing when its KV cache token capacity is below the sum of its programs' context tokens. A monitor checks this every $\Delta t$, which catches context growth mid-execution.[^kangThunderAgentSimpleFast2026]
- **Time decay.** Tokens of acting programs are discounted by $f(t_q)$, where $t_q$ is the tool execution time in the current step, so long-idle caches become eviction candidates.[^kangThunderAgentSimpleFast2026]
- **Shortest-first eviction.** Recomputation cost scales quadratically with context length, so the scheduler greedily pauses the programs with the shortest contexts. $S_{\mathrm{pause}}(P)=\frac{1}{c_{P}}+\mathbb{I}(\tau=\textbf{A})$ and $S_{\mathrm{restore}}(P)=\frac{1}{c_{P}}+\mathbb{I}(\tau=\textbf{R})$: acting programs are paused first and reasoning programs are restored first.[^kangThunderAgentSimpleFast2026]
- **Global waiting queue.** The waiting queues of all backend replicas are unified. A paused program's KV cache is assumed evicted, so it can resume on any replica with free memory.[^kangThunderAgentSimpleFast2026]
- **Tool resource management.** A hook-based garbage collector reclaims sandboxes, network sockets, and compute slots when a program terminates, and environments are prepared asynchronously before GPU memory is allocated.[^kangThunderAgentSimpleFast2026]

The evaluated configuration is $\Delta t=5$, $f(t)=2^{-t}$, with vLLM as the inference engine.[^kangThunderAgentSimpleFast2026]

## Variants

| Variant | Description | Source |
|---|---|---|
| ThunderAgent on vLLM | The configuration of the paper's main results. | [^kangThunderAgentSimpleFast2026] |
| ThunderAgent on SGLang HiCache | ThunderAgent integrated into [SGLang](../methods/sglang.md) HiCache with host-memory ratio 2.0, to show compatibility with [KV cache offloading](../methods/kv-cache-offloading.md). | [^kangThunderAgentSimpleFast2026] |
| TA | MORI's baseline: ThunderAgent on SGLang v0.5.10 without CPU offloading. | [^xiaIdlenessRelativeExploiting2026] |
| TA+O | MORI's baseline: ThunderAgent with CPU offloading enabled via HiCache. The scheduler is unaware of the CPU tier, and HiCache manages CPU DRAM with its own LRU policy. | [^xiaIdlenessRelativeExploiting2026] |

## Papers using it

### ThunderAgent's own results

Models are GLM-4.6 (355B) and Qwen-3 (235B) at FP8 with TP8 on 8$\times$H100 nodes. Throughput is in steps per minute.[^kangThunderAgentSimpleFast2026]

| Result | Setting | Value |
|---|---|---|
| Serving throughput vs vLLM | high concurrency (e.g., 96 parallel programs) | 1.48–3.58$\times$ |
| Serving throughput vs Continuum | high concurrency (e.g., 96 parallel programs) | 1.17–3.31$\times$ |
| RL rollout, mini-SWEAgent, vs vLLM + Gateway | GLM-4.6, $N=144$, 2$\times$H100 nodes | 671.8 vs 375.4 (1.79$\times$) |
| RL rollout, [OpenHands](../methods/openhands.md), vs vLLM + Gateway | GLM-4.6, $N=144$, 2$\times$H100 nodes | 270.8 vs 69.1 (3.92$\times$) |
| Disk memory savings from tool resource management | OpenHands rollouts | 4.2$\times$ |
| + local program-aware scheduling over vLLM | 2$\times$H100, GLM-4.5-fp8, mini-SWEAgent, 144 concurrent programs | 375 to 602 (1.61$\times$) |
| + global waiting queue | same | 602 to 672 (a further 1.12$\times$) |
| Scaling vs Cache-Aware Routing Policy in SGLang Model Gateway | GLM-4.6 + mini-SWEAgent, 72 programs per node | 1.79$\times$ at 2 nodes to 2.39$\times$ at 8 nodes |
| Global scheduler per-tick communication delay | same | 13.5 ms at 2 nodes to 22.7 ms at 8 nodes |
| vs vLLM on 8$\times$A100 | concurrency 48 and 72 | 1.71–2.08$\times$ on mini-SWEAgent, 1.16–1.62$\times$ on OpenHands |
| With SGLang HiCache | MiniMax M2.5, [R2E-Gym](../datasets/r2e-gym.md), 8$\times$H100, batch 64 to 192 | P50 held at $\sim$10 s and P90 at $\sim$20 s; the baseline without ThunderAgent reaches $\sim$70 s P50 at batch 192 |
| SkyRL recipe | Qwen3-32B on R2EGym | 3.01$\times$ wall-clock speedup over the baseline |

All rows: [^kangThunderAgentSimpleFast2026]

Serving workloads are OpenHands and mini-SWEAgent on [SWE-bench Lite](../benchmarks/swe-bench-lite.md), ToolOrchestra on [HLE](../benchmarks/hle.md), and OpenHands on ScienceAgentBench. ThunderAgent keeps a KV cache hit rate of $\approx$100% for the mini-SWEAgent and OpenHands workloads, while Continuum's drops from $>$90% to $\approx$60% under high concurrency.[^kangThunderAgentSimpleFast2026] The paper reports that ThunderAgent is being integrated into NVIDIA Dynamo.[^kangThunderAgentSimpleFast2026]

### ThunderAgent as measured by MORI

[MORI](../papers/xiaIdlenessRelativeExploiting2026.md) is implemented on top of ThunderAgent and SGLang (v0.5.10). It adds approximately 3,300 lines of Python to ThunderAgent's scheduler, and its control loop runs in the ThunderAgent router process.[^xiaIdlenessRelativeExploiting2026] It uses TA and TA+O as baselines on replayed Claude Code traces. Throughput is output tokens/s.[^xiaIdlenessRelativeExploiting2026]

| Metric | Setting | TA | TA+O | MORI | SMG |
|---|---|---|---|---|---|
| Output throughput (tokens/s) | H200 (80 GB), Qwen-2.5 7B, DP=1, 80 programs | 557 | 667 | 853 | 447 |
| Output throughput (tokens/s) | B200, Llama-3.1 70B, 1$\times$ CPU memory, 20 / 50 / 80 programs | not stated | 147 / 181 / 146 | 136 / 191 / 189 | not stated / not stated / 96 |
| Output throughput (tokens/s) | B200, Llama-3.1 70B, 2$\times$ CPU memory, 80 programs | not stated | 124 | 213 | not stated |
| Average TTFT (s) | B200, Llama-3.1 70B, 1$\times$ CPU memory, 80 programs | 73 | 56 | 38 | 108 |
| Throughput collapse (tokens/s), 50 to 80 programs per replica | H200, Qwen-3 30B-A3B, DP=3 | 1147 to 798 (1$\times$ CPU memory) | 1395 to 920 (2$\times$ CPU memory) | not stated | not stated |
| GPU utilization | DP=3, 80 programs per replica | 59–76% | 59–76% | 99%+ | not stated |
| Programs that switch backends | DP=3, 80 programs per replica, 2$\times$ CPU memory | 7.6% | 5.5% | 2.0% | not stated |
| Programs that switch backends | DP=3, 20 programs per replica | 14–15% | 14–15% | 0.3–2.9% | not stated |
| Average CPU scheduling latency | H200, 30B model, DP=1 | not stated | 21.5 ms | 23.8 ms | not stated |

All rows: [^xiaIdlenessRelativeExploiting2026]

At 20 programs per replica with 1$\times$ CPU memory, TA and MORI both reach 9–10 running requests per engine and 99%+ GPU utilization, while SMG reaches 51%.[^xiaIdlenessRelativeExploiting2026]

### Other mentions

- [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md) cites ThunderAgent as an example of a system that recomputes evicted tokens in the thrashing regime, and as a workflow-aware runtime. It does not run ThunderAgent. Its own recomputation baseline loses 44.2% of average agent completion throughput against a non-thrashing baseline.[^yuanKAIROSStatefulContextAware2026]

## Strengths & Limitations

Strengths:

- Throughput stays stable as the number of parallel workflows grows past the GPU memory limit, while the baselines collapse.[^kangThunderAgentSimpleFast2026]
- The abstraction decouples scheduling from execution backends such as vLLM, SGLang, and TensorRT-LLM.[^kangThunderAgentSimpleFast2026]
- Program-aware routing gives balanced per-engine loads at low concurrency.[^xiaIdlenessRelativeExploiting2026]

Limitations:

- Reserving memory for acting programs leaves GPU memory idle during long tool execution. The time decay is the paper's answer to this tradeoff.[^kangThunderAgentSimpleFast2026]
- At low concurrency (24) on 8$\times$A100, ThunderAgent only matches vLLM within noise.[^kangThunderAgentSimpleFast2026]
- Without a CPU memory tier, its throughput is bounded by GPU KV cache capacity.[^xiaIdlenessRelativeExploiting2026]
- Its scheduler is offloading-agnostic. When a program is evicted from GPU memory, it is treated as having no cached state and reassigned to the replica with the lightest load, even when the original replica still holds the KV cache in CPU memory.[^xiaIdlenessRelativeExploiting2026]
- MORI argues that choosing eviction candidates by static properties such as context length may keep a program blocked on a long tool call in GPU memory while evicting one that is about to resume.[^xiaIdlenessRelativeExploiting2026]

# Contradictions

**1. Does ThunderAgent stay stable when offloading is enabled?** ThunderAgent reports that with SGLang HiCache it holds P50 latency at $\sim$10 s and P90 at $\sim$20 s across batch sizes 64 to 192, with throughput growing monotonically.[^kangThunderAgentSimpleFast2026] MORI reports that the same combination (TA+O) has non-monotonic throughput: 147, 181, then 146 tokens/s at 20, 50, and 80 programs on B200 with 1$\times$ CPU memory, and a drop from 1395 to 920 tokens/s between 50 and 80 programs per replica at DP=3 with 2$\times$ CPU memory.[^xiaIdlenessRelativeExploiting2026] Setting differences: ThunderAgent uses MiniMax M2.5 on R2E-Gym across 8$\times$H100; MORI uses Qwen and Llama models on H200 and B200, replayed Claude Code traces in which each tool call is simulated by sleeping for the recorded duration, and CPU memory capped at 1$\times$ or 2$\times$ GPU memory. The metrics also differ (P50 and P90 latency vs output tokens/s).

**2. What ThunderAgent's eviction depends on.** MORI describes ThunderAgent's GPU eviction as context-length-based and "uncorrelated with program phase".[^xiaIdlenessRelativeExploiting2026] ThunderAgent's pause score gives the execution phase strict priority over context length (acting programs are paused first), and its time decay discounts the tokens of programs that have been in a tool call for longer.[^kangThunderAgentSimpleFast2026] The two papers use "phase" differently: ThunderAgent's phase is Reasoning or Acting in the current step, and MORI's phase is busy or idle over the last $k{=}5$ inference and tool-call cycles.[^kangThunderAgentSimpleFast2026][^xiaIdlenessRelativeExploiting2026]

**3. Is ThunderAgent a pinning system?** MORI lists ThunderAgent among systems that temporarily pin KV cache in GPU memory during short tool-call intervals to avoid eviction.[^xiaIdlenessRelativeExploiting2026] ThunderAgent pauses acting programs before reasoning programs under memory pressure and contrasts itself with Continuum, which pins KV caches by a time-to-live.[^kangThunderAgentSimpleFast2026]

**4. Headline serving speedup inside the ThunderAgent paper.** The body text gives 1.48–3.58$\times$ over vLLM and 1.17–3.31$\times$ over Continuum. The Figure 4 caption says ThunderAgent outperforms vLLM and Continuum "up to 2.43-3.56$\times$" for workflows with predictable tool call times.[^kangThunderAgentSimpleFast2026]

**Not comparable.** ThunderAgent's self-reported throughput is in steps per minute on vLLM. MORI's numbers for TA are output tokens/s on SGLang. ThunderAgent's 13.5 ms to 22.7 ms is a per-tick communication delay of the global scheduler; MORI's 21.5 ms is the average CPU scheduling latency of TA+O.[^kangThunderAgentSimpleFast2026][^xiaIdlenessRelativeExploiting2026]

## Related

- [Program-aware scheduling](../methods/program-aware-scheduling.md), [KV cache](../methods/kv-cache.md), [KV cache offloading](../methods/kv-cache-offloading.md), [KV cache swapping](../methods/kv-cache-swapping.md), [LMCache](../methods/lmcache.md)
- Engines: [vLLM](../methods/vllm.md), [SGLang](../methods/sglang.md)
- Agents and workloads: [OpenHands](../methods/openhands.md), [SWE-agent](../methods/swe-agent.md), [SWE-bench Lite](../benchmarks/swe-bench-lite.md), [HLE](../benchmarks/hle.md), [R2E-Gym](../datasets/r2e-gym.md)
- Papers: [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md), [MORI](../papers/xiaIdlenessRelativeExploiting2026.md), [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md)

## Open questions and results

- [Does offloading the KV cache to CPU memory help agentic workloads?](../questions/kv-cache-offloading-for-agent-workloads.md)

[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
