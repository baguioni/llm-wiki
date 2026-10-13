---
type: Paper
title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
description: Power management system for agentic LLM serving that uses aggregate agent context as the control signal for GPU frequency, per-instance concurrency, and multi-instance routing, cutting average GPU power by 27% while meeting a per-agent throughput SLO.
tags: [llm-serving, agentic-inference, power-efficiency, dvfs, kv-cache, scheduling, ai899]
collections: [ai899]
authors: [Yichao Yuan, Mosharaf Chowdhury, Nishil Talati]
doi: 10.48550/arXiv.2604.16682
arxiv: "2604.16682"
arxiv_version: 2604.16682v1
sources:
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving

Text source: arXiv HTML, version `2604.16682v1`.

## Summary

Prior power-management techniques for LLM inference, such as [DVFS](../methods/dvfs.md)-based runtimes and power-aware scheduling, are designed for stateless single-turn serving.[^yuanKAIROSStatefulContextAware2026] The paper characterizes [ReAct](../methods/react.md)-style agentic workloads and finds that each agent keeps long-lived state in the serving system's context cache ([KV cache](../methods/kv-cache.md)), which grows across tool-interleaved turns and varies widely across agents.[^yuanKAIROSStatefulContextAware2026] Lowering GPU frequency beyond a certain value pushes the system into a *thrashing regime*: slower execution lets accumulated context exceed GPU memory capacity, cached context is evicted, and previously processed tokens must be recomputed or loaded from slower memory tiers.[^yuanKAIROSStatefulContextAware2026]

[KAIROS](../methods/kairos.md) is a context-aware power management system that tracks requests at agent granularity, adapts GPU frequency and admission per serving instance to context growth and agent progress, and routes agents across instances.[^yuanKAIROSStatefulContextAware2026] It reduces average GPU power by 27% (up to 39.8%) for a single serving instance and by 46.3% for multi-instance serving while maintaining a per-agent SLO of P5 throughput 20 tokens/s.[^yuanKAIROSStatefulContextAware2026] The authors state that KAIROS is the first work to optimize power for agentic inference serving.[^yuanKAIROSStatefulContextAware2026]

## Contributions

- A characterization of agentic inference serving that shows why power optimization is different from, and harder than, single-turn LLM serving.[^yuanKAIROSStatefulContextAware2026]
- A context-aware control mechanism that jointly manages GPU frequency and concurrency using context growth, memory pressure, and agent progress, to reduce power while avoiding thrashing and preserving SLO attainment.[^yuanKAIROSStatefulContextAware2026]
- KAIROS, an end-to-end system for agentic AI serving that reduces power by 27% while maintaining performance targets.[^yuanKAIROSStatefulContextAware2026]
- A throughput-based, per-agent SLO for agentic serving, argued to be more actionable than TTFT, TBT, or TTLT.[^yuanKAIROSStatefulContextAware2026]

## Method

### Characterization

Setup: the Harbor framework on a single NVIDIA H100 GPU with context caching enabled, a [vLLM](../methods/vllm.md) server with Qwen3-Coder-30B, [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [mini-swe-agent](../methods/mini-swe-agent.md), and a fixed Poisson arrival rate of 0.08 agent jobs per second.[^yuanKAIROSStatefulContextAware2026]

- **Dynamic context growth.** The setup serves an average of 17 agents in parallel. The number of conversation turns varies from 1 to 2518, with an average of 37 turns.[^yuanKAIROSStatefulContextAware2026] Turn counts, agent durations, and maximum context lengths are heavy-tailed: many agents peak at tens of thousands of tokens, while a non-trivial subset grows to hundreds of thousands of tokens.[^yuanKAIROSStatefulContextAware2026] When an agent completes, its entire context cache is released at once.[^yuanKAIROSStatefulContextAware2026]
- **Effect of GPU frequency scaling.** Reducing frequency from 1680 MHz to 900 MHz lowers energy and power by about 30% with little impact on throughput or latency. Below 900 MHz the trend reverses, with sharply higher energy, lower throughput, and longer time per LLM request.[^yuanKAIROSStatefulContextAware2026]
- **Thrashing.** At 1185 MHz memory pressure stays stable; at 660 MHz accumulated context grows faster than it can be drained and exceeds available memory.[^yuanKAIROSStatefulContextAware2026]
- **Cost of thrashing.** In a controlled experiment that replays an 18-turn mini-swe-agent request at 0.5 (non-thrashing) and 0.6 (thrashing) requests/second, recomputation and [LMCache](../methods/lmcache.md)-based offloading reduce average agent completion throughput by 44.2% and 42.1%, respectively; average time spent in LLM calls increases by 3× for both; useful decode throughput, excluding recomputation cycles, drops by 22.3%.[^yuanKAIROSStatefulContextAware2026]

The paper derives three challenges: C1, tension between power saving and performance; C2, highly dynamic context demand; C3, strong coupling between power and memory stability.[^yuanKAIROSStatefulContextAware2026]

### Problem formulation

An agent $a$ issues requests $r_i = (\Delta p_i, \Delta d_i)$, where $\Delta p_i$ is the number of newly appended prefill tokens and $\Delta d_i$ the number of generated decode tokens. The context size after step $i$ is $C_i = |H_i|$, the length of all prior tokens.[^yuanKAIROSStatefulContextAware2026] Per-agent throughput is $\text{Throughput}(a)=\frac{\sum_{i}\Delta d_{i}}{\sum_{i}t_{i}}$, with $t_i$ the end-to-end latency of request $i$; an agent satisfies the SLO with target $\tau$ (tokens/s) if $\text{Throughput}(a)\geq\tau$.[^yuanKAIROSStatefulContextAware2026] SLO attainment is the fraction of agents completing in $[0,T]$ that meet the target, and the quantity to reduce is average system power $\bar{P}(T)$ summed over serving instances.[^yuanKAIROSStatefulContextAware2026] The formal optimization objective appears only as a figure in the extracted text.

### Components

- **Agent ID tracker.** A lightweight wrapper launches each agent as a child process, assigns a unique ID, emits lifecycle signals (`agent_start`/`agent_end`), and encodes the ID into each request via the API key, without modifying agent programs. The tracking is purely identifier-based and carries no information about request content or relationships.[^yuanKAIROSStatefulContextAware2026]
- **Context-aware frequency control.** At startup the controller obtains the available GPU frequency levels $\mathcal{F}=\{f^{(1)},\dots,f^{(L)}\}$ in ascending order and the token capacity $U_{\max}$ of the instance. At epoch $k$ it observes the aggregate context usage $U_k$ of ongoing agents. If $U_{k}\geq\alpha U_{\max}$ it selects $f^{(L)}$; otherwise it selects level $\ell_{k}=\left\lfloor\frac{U_{k}}{\alpha U_{\max}}\cdot(L-1)\right\rfloor+1$. In practice $\alpha=0.75$.[^yuanKAIROSStatefulContextAware2026]
- **SLO-aware frequency boosting.** The controller tracks each agent's achieved throughput. If the minimum throughput across ongoing and pending agents falls below $\tau$, it overrides the context-aware policy and sets the frequency to the maximum level $f^{(L)}$.[^yuanKAIROSStatefulContextAware2026]
- **Thrashing avoidance via concurrency control.** The controller enforces $U_{k}\leq\beta U_{\max}$, with safety margin $\beta$ (e.g., $\beta=0.95$) reserving headroom for transient decode growth. An agent whose admission would violate the bound stays pending. A second threshold $\gamma<\beta$ (e.g., $\gamma=0.9$) governs admission: when pending agents exist and $U_{k}<\gamma U_{\max}$, agents are admitted in arrival order.[^yuanKAIROSStatefulContextAware2026]
- **Context-aware multi-instance router.** An idle NVIDIA H100 can sit at a very low power state (e.g., 50W), while a small amount of incoming work triggers a substantial increase (e.g., an additional 100W), so round robin is inefficient because it activates all instances.[^yuanKAIROSStatefulContextAware2026]
  - *Assignment:* while some instance has ongoing context usage below 50% of the maximum context capacity, new agents go to instances in increasing instance ID order (consolidation). Once all active instances exceed the threshold, each incoming agent goes to the instance with the lowest current context usage (load spreading).[^yuanKAIROSStatefulContextAware2026]
  - *Reassignment:* allowed only after an agent's step counter since its last (re)assignment reaches 8 conversation turns. The agent moves if its current instance's context usage is at least 2× that of the active instance with the lowest context usage.[^yuanKAIROSStatefulContextAware2026]

Idle instances keep the vLLM server running and consume power close to the GPU's idle level, so they can be brought back into service without a long restart delay.[^yuanKAIROSStatefulContextAware2026]

## Experiments & Results

### Setup

- Hardware: NVIDIA H100 NVL server, each GPU with a 400 W TDP and 80 GB of memory, Intel Xeon Platinum 8592+ CPU, 2 TB of DRAM.[^yuanKAIROSStatefulContextAware2026]
- Serving: vLLM v0.14.0, one H100 per instance, prefill-decode aggregated. Primary model Qwen3-Coder-30B, quantized to FP8; Ministral-3-14B is used for model diversity.[^yuanKAIROSStatefulContextAware2026]
- Workloads: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [DABStep](../benchmarks/dabstep.md), and [Terminal-Bench 2.0](../benchmarks/terminal-bench.md), with the agent scaffolds mini-swe-agent and [Terminus-2](../methods/terminus-2.md) as implemented in Harbor.[^yuanKAIROSStatefulContextAware2026]
- Power control and measurement: [Zeus](../methods/zeus.md).[^yuanKAIROSStatefulContextAware2026]
- Protocol: requests and timing are recorded from a real agent execution and replayed with the same token distribution, relative timing, and agent issuing order. Each evaluation runs over a 3-hour window.[^yuanKAIROSStatefulContextAware2026]
- Metric: P5 throughput, the throughput of the slowest 5% of agents.[^yuanKAIROSStatefulContextAware2026]
- Baselines: no frequency control, and a fixed GPU frequency of 810 MHz.[^yuanKAIROSStatefulContextAware2026]

### Single-instance serving

| Setting | Result |
|---|---|
| Across request rates, per-agent SLO target of 20 tokens/s | KAIROS: average power saving of 27% (up to 39.8%) while meeting the SLO target |
| Fixed 810 MHz baseline, same setting | Slightly larger power savings than KAIROS, at the cost of significantly degraded SLO attainment |

All rows: [^yuanKAIROSStatefulContextAware2026]

Per-request-rate values for throughput, SLO attainment, energy, and power are reported only in Figure 7 of the paper.

**SLO targets** (mini-swe-agent on DABStep, arrival rate 0.03 jobs/s):[^yuanKAIROSStatefulContextAware2026]

| SLO target (tokens/s) | Power savings relative to no frequency control |
|---|---|
| 20 | 32.9% |
| 35 | not stated |
| 45 | 6.3% |

All rows: [^yuanKAIROSStatefulContextAware2026]

The paper identifies 45 tokens/s as the maximum achievable per-agent SLO for this setup.[^yuanKAIROSStatefulContextAware2026]

**Thrashing avoidance** (mini-swe-agent on DABStep, request rate 0.05 jobs/s, SLO target 20 tokens/s):[^yuanKAIROSStatefulContextAware2026]

| Configuration | Per-agent P5 throughput | Overall throughput |
|---|---|---|
| KAIROS without thrashing avoidance | 2.3 tokens/s | 0.046 jobs/s |
| KAIROS with thrashing avoidance | close to the 20 tokens/s target | 0.05 jobs/s |

All rows: [^yuanKAIROSStatefulContextAware2026]

**Across models** (Table 1, SWE-Bench Verified, 0.06 jobs/s):[^yuanKAIROSStatefulContextAware2026]

| Model | No Freq. Control power (W) | KAIROS power (W) | Reduction |
|---|---|---|---|
| Qwen3-Coder-30B | 367.9 | 240.9 | 34.5% |
| Ministral-3-14B | 370.8 | 263.8 | 28.9% |

All rows: [^yuanKAIROSStatefulContextAware2026]

### Multi-instance serving

Four serving instances, input rate of 0.16 jobs/s, mini-swe-agent on SWE-Bench Verified.[^yuanKAIROSStatefulContextAware2026]

| Configuration | Average power | Per-agent P5 throughput |
|---|---|---|
| No frequency control | 1279.5 W | not stated |
| KAIROS with round-robin routing | 784.8 W | 25.4 tokens/s |
| KAIROS with context-aware routing | 686.5 W | 26.9 tokens/s |

All rows: [^yuanKAIROSStatefulContextAware2026]

The context-aware configuration is a total power reduction of 46.3% against no frequency control.[^yuanKAIROSStatefulContextAware2026]

## Limitations

- The design is instantiated on a prefill-decode aggregated architecture; exploration of PD-disaggregated settings, where additional coordination overheads may arise, is left to future work.[^yuanKAIROSStatefulContextAware2026]
- Arrival rates are chosen to match the capabilities of the experimental hardware; higher arrival rates would require proportionally more GPU resources.[^yuanKAIROSStatefulContextAware2026]
- Tighter SLO targets require higher GPU frequencies and shrink the savings: from 32.9% at 20 tokens/s to 6.3% at 45 tokens/s.[^yuanKAIROSStatefulContextAware2026]
- The work focuses on the GPU-side LLM serving path; CPU power for orchestration and tool interaction is outside its scope.[^yuanKAIROSStatefulContextAware2026]
- The authors note there is still no consensus on an appropriate SLO for agentic serving.[^yuanKAIROSStatefulContextAware2026]
- Workloads are replayed traces of recorded agent executions, not live agents.[^yuanKAIROSStatefulContextAware2026]
- The paper has no dedicated limitations section.

## Related

- Methods: [KAIROS](../methods/kairos.md), [DVFS](../methods/dvfs.md), [KV cache](../methods/kv-cache.md), [ReAct](../methods/react.md), [LMCache](../methods/lmcache.md), [Zeus](../methods/zeus.md)
- Systems built on or used: [vLLM](../methods/vllm.md), [mini-swe-agent](../methods/mini-swe-agent.md), [Terminus-2](../methods/terminus-2.md)
- Benchmarks: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [DABStep](../benchmarks/dabstep.md), [Terminal-Bench](../benchmarks/terminal-bench.md)
- Papers in this wiki cited by this paper: [ThunderAgent](kangThunderAgentSimpleFast2026.md), [Parrot](linParrotEfficientServing2024.md), [Autellix](luoAutellixEfficientServing.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md), [Reflexion](shinnReflexionLanguageAgents2023.md)

[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
