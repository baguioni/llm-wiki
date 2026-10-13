---
type: Paper
title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
description: Agentic inference system that schedules whole agent workflows as programs, pausing and migrating them to avoid KV cache thrashing and cross-node memory imbalance, and manages tool environments by program lifecycle.
tags: [llm-serving, agentic-inference, kv-cache, scheduling, rl-rollout, tool-resource-management, ai899]
collections: [ai899]
authors: [Hao Kang, Ziyang Li, Weili Xu, Xinyu Yang, Yinfang Chen, Junxiong Wang, Beidi Chen, Tushar Krishna, Chenfeng Xu, Simran Arora]
year: 2026
doi: 10.48550/arXiv.2602.13692
arxiv: "2602.13692"
arxiv_version: 2602.13692v3
code: https://github.com/ThunderAgent-org/ThunderAgent
sources:
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
---

# ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System

Text source: arXiv HTML, version `2602.13692v3`.

## Summary

Existing systems run agentic inference by loosely combining an LLM inference engine (for example vLLM or SGLang) with a tool orchestrator (for example Kubernetes). These components schedule and allocate resources per request, with no end-to-end knowledge of the workflow.[^kangThunderAgentSimpleFast2026] The paper identifies three resulting problems: KV cache thrashing, cross-node memory imbalance, and tool lifecycle obliviousness.[^kangThunderAgentSimpleFast2026]

ThunderAgent abstracts an agentic workflow as an *agentic program*, a scheduling unit that persists across model invocations and tool executions. On top of this abstraction it adds a program-aware scheduler and a tool resource manager.[^kangThunderAgentSimpleFast2026] Across coding, routing, and scientific discovery agents, the paper reports 1.48–3.58× throughput improvements in serving, 1.79–3.92× in RL rollout, and up to 4.2× disk memory savings compared to state-of-the-art inference systems.[^kangThunderAgentSimpleFast2026]

## Contributions

- **Program abstraction.** A program tracks the workflow's identifier, execution phase (reasoning or acting), scheduling status, total tokens, and tool resources. The abstraction decouples scheduling from execution backends such as vLLM, SGLang, and TensorRT-LLM.[^kangThunderAgentSimpleFast2026]
- **Program-aware scheduler.** Scheduling is cast as a constrained optimization problem, with two mechanisms: state-aware pausing of workflows in the acting state under memory pressure, and dynamic migration of programs across data-parallel (DP) GPU nodes through a shared global waiting queue.[^kangThunderAgentSimpleFast2026]
- **Program-aware tool resource management.** Environment initialization overlaps with LLM reasoning, and a lifecycle-aware garbage collector reclaims tool resources such as Docker sandboxes and network ports when programs terminate.[^kangThunderAgentSimpleFast2026]

## Method

### Problems in existing systems

The profiled baseline is vLLM combined with Kubernetes, running OpenHands RL rollout with GLM 4.6 on two 8×H100 GPU nodes.[^kangThunderAgentSimpleFast2026]

| Problem | Cause | Measured effect |
|---|---|---|
| [KV cache thrashing](../methods/kv-cache-thrashing.md) | Under high concurrency, the KV cache of a program in tool execution is evicted to admit other requests, so the prefix is re-prefilled when the tool returns. | End-to-end latency of each request increases by up to 7.14× compared to a non-thrashing setting |
| Cross-node memory imbalance | KV-aware routers send all requests of a workflow to the same node, while workflows have heterogeneous KV footprints and lifetimes. | In a 90 minute snapshot, memory usage between two DP nodes diverges by more than 20% for over 37 minutes, with a peak imbalance of 51% |
| Tool lifecycle obliviousness | The tool orchestrator's lifecycle is not synchronized with the inference engine. | Disk usage grows linearly with processed workflows until it exceeds system capacity; environment preparation time grows with the number of parallel workflows |

All rows: [^kangThunderAgentSimpleFast2026]

The paper also notes that rollout accounts for over 70% of the total wall-clock time in reinforcement learning.[^kangThunderAgentSimpleFast2026]

### Program abstraction

An agentic program is the tuple $P=\langle\mathit{ID},c,\mathcal{T},\mathcal{L},\tau,s\rangle$ (Eq. 1): a unique global identifier, the number of tokens in the context, the set of tool environments, the backend placement, the execution phase (Reasoning **R** or Acting **A**), and the scheduling status (Active, Paused, Terminated).[^kangThunderAgentSimpleFast2026] ThunderAgent wraps existing LLM engines and tool orchestrators through OpenAI-style endpoints. Adoption requires attaching `program_id` to requests (for LLM inference and tool execution) and sending an explicit release signal when a program ends.[^kangThunderAgentSimpleFast2026]

### Cost model

The metric is the Space-Time Product (STP), the integral of memory footprint over processing time, with memory measured as KV cache token count: $\text{Cost}_{\text{x}}=\int_{0}^{t_{x}}M_{x}(t)\,dt$ (Eq. 2).[^kangThunderAgentSimpleFast2026] Total cost decomposes as $\text{Cost}_{\text{total}}\approx\text{Cost}_{\text{decode}}+\text{Cost}_{\text{prefill}}+\text{Cost}_{\text{recompute}}+\text{Cost}_{\text{unused}}+\text{Cost}_{\text{caching}}$ (Eq. 3). Decode and prefill are effective work. Recompute comes from thrashing, unused from memory imbalance across DP replicas, and caching from holding memory during tool execution.[^kangThunderAgentSimpleFast2026]

### Scheduling policy

- **Restore and Pause.** Restore assigns a Paused program to a backend with available capacity and marks it Active. Pause unbinds an Active program from its backend, releases its KV cache for preemption, and marks it Paused.[^kangThunderAgentSimpleFast2026]
- **Periodic thrashing detection.** A backend $\mathcal{L}$ is thrashing when $\text{C}_{\text{total}}<\sum_{p\in\mathcal{L}}c_{p}$ (Eq. 6), where $\text{C}_{\text{total}}$ is the fixed token capacity of its KV cache pool. A periodic monitor checks this every $\Delta t$, which catches pressure from context growth mid-execution, unlike schedulers that check only on arrival. Pause runs until usage falls below $\lambda_{\max}\cdot\text{C}_{\text{total}}$; Restore runs when usage is below $\lambda_{\min}\cdot C_{\text{total}}$. Both watermarks are set to 1 in practice.[^kangThunderAgentSimpleFast2026]
- **Time decay.** Tokens of acting programs are discounted by $f(t_q)$, where $t_q$ is the tool execution time in the current step: $\text{C}_{\text{total}}<\sum_{p\in\mathcal{L},\tau=\textbf{R}}c_{p}+\sum_{q\in\mathcal{L},\tau=\textbf{A}}c_{q}\times f(t_{q})$ (Eq. 7). This lets the scheduler evict long-idle caches. The paper proves that under memoryless tool latencies and the boundary conditions $f(0)=1$, $\lim_{t\to\infty}f(t)=0$, the admissible forms are $f(t)=e^{-\lambda t}$ with $\lambda>0$ or $f(k)=x^{-k}$ with $x>1$ (Theorem F.1).[^kangThunderAgentSimpleFast2026]
- **Shortest-first eviction.** Recomputation cost scales quadratically with context length, $\text{Cost}_{\text{recompute}}\propto c_{i}^{2}$ (Lemma 4.1). The eviction problem is $\min_{S}\sum_{i\in S}c_{i}^{2}$ subject to $\sum_{i\in S}c_{i}\geq\Delta C$ (Eq. 9), and the scheduler greedily pauses the programs with the shortest contexts.[^kangThunderAgentSimpleFast2026]
- **Scores.** $S_{\mathrm{restore}}(P)=\frac{1}{c_{P}}+\mathbb{I}(\tau=\textbf{R})$ (Eq. 10) and $S_{\mathrm{pause}}(P)=\frac{1}{c_{P}}+\mathbb{I}(\tau=\textbf{A})$ (Eq. 11). The indicator gives execution state strict priority over context length: acting programs are paused first and reasoning programs are restored first.[^kangThunderAgentSimpleFast2026]
- **Global program-aware waiting queue.** The waiting queues of all backend replicas are unified. A paused program's KV cache is assumed evicted, so its recomputation cost is node-agnostic and it can resume on any replica with free memory. This bounds the unused cost to $\text{C}_{\text{unused}}<c_{\mathrm{min}}\cdot\Delta t$ per node per period, where $c_{\mathrm{min}}$ is the minimum token length among paused programs.[^kangThunderAgentSimpleFast2026]

### Tool resource management

- **Hook-based garbage collection.** When a program is Terminated, the collector immediately reclaims sandboxes, network sockets, and compute slots.[^kangThunderAgentSimpleFast2026]
- **Asynchronous environment preparation.** When a program with high $S_{\text{restore}}$ approaches the restore threshold, its execution environment is restored asynchronously before GPU memory is allocated.[^kangThunderAgentSimpleFast2026]

## Experiments & Results

### Setup

- Coding agent serving: [OpenHands](../methods/openhands.md) and mini-SWEAgent on [SWE-bench Lite](../benchmarks/swe-bench-lite.md). OpenHands averages more than 10GB of disk per sandbox; mini-SWEAgent uses 2GB per sandbox.[^kangThunderAgentSimpleFast2026]
- General agent serving: ToolOrchestra on [HLE](../benchmarks/hle.md) and OpenHands on [ScienceAgentBench](../benchmarks/scienceagentbench.md).[^kangThunderAgentSimpleFast2026]
- RL rollout: the same models, workflows, and samples on two 8× H100 nodes.[^kangThunderAgentSimpleFast2026]
- Models: GLM-4.6 (355B) and Qwen-3 (235B), quantized to FP8 with Tensor Parallelism (TP8) on 8×H100 nodes. ToolOrchestra uses Qwen3-8B at FP16 on one RTX 5090. Agent Docker environments run on a separate CPU cluster.[^kangThunderAgentSimpleFast2026]
- ThunderAgent configuration: $\Delta t=5$, $f(t)=2^{-t}$, with [vLLM](../methods/vllm.md) as the inference engine.[^kangThunderAgentSimpleFast2026]
- Metric: steps per minute, where one step includes a reasoning and an acting period.[^kangThunderAgentSimpleFast2026]
- Baselines: vLLM (request-aware, stateless), [Continuum](../methods/continuum.md) (pins KV cache by predicted tool duration), and vLLM + SGLang Gateway for distributed rollout.[^kangThunderAgentSimpleFast2026]

### Serving

| Comparison | Throughput speedup of ThunderAgent |
|---|---|
| vs vLLM, at high concurrency (e.g., 96 parallel programs) | 1.48–3.58× |
| vs Continuum, at high concurrency (e.g., 96 parallel programs) | 1.17–3.31× |

All rows: [^kangThunderAgentSimpleFast2026]

- ThunderAgent keeps a KV cache hit rate of ≈100% for the mini-SWEAgent and OpenHands workloads, while Continuum's hit rate drops from >90% to ≈60% under high concurrency.[^kangThunderAgentSimpleFast2026]
- With stochastic tool execution times, ThunderAgent has a lower KV cache hit rate than Continuum but higher throughput.[^kangThunderAgentSimpleFast2026]
- ThunderAgent's throughput stays stable as the number of parallel workflows grows past the GPU memory limit, while the baselines collapse.[^kangThunderAgentSimpleFast2026]
- Per-configuration serving throughput is reported only in Figure 4 and is not transcribed here.

### RL rollout (Table 2)

GLM-4.6 rollout ($N=144$) on 2×H100 nodes. Throughput is in steps per minute.[^kangThunderAgentSimpleFast2026]

| Workflow | Serving system | Throughput |
|---|---|---|
| mini-SWEAgent | vLLM + Gateway | 375.4 |
| mini-SWEAgent | ThunderAgent | 671.8 (1.79×) |
| OpenHands | vLLM + Gateway | 69.1 |
| OpenHands | ThunderAgent | 270.8 (3.92×) |

### Ablations

- Latency breakdown for OpenHands rollouts: the gain comes mainly from lower prefill and decode latency. Tool resource management contributes approximately 10% of the latency improvement and gives 4.2× disk memory savings.[^kangThunderAgentSimpleFast2026]
- Sensitivity: throughput stays high across settings of $\Delta t$ and $f(t)=x^{-t}$. A larger $\Delta t$ might lower the KV cache hit rate, and a larger $x$ evicts acting programs with short tool calls prematurely.[^kangThunderAgentSimpleFast2026]

Component-wise ablation (Table 7), 2×H100 + GLM-4.5-fp8 + mini-SWEAgent at 144 concurrent programs:[^kangThunderAgentSimpleFast2026]

| Component | Throughput (steps/min) | Step gain |
|---|---|---|
| vLLM (baseline) | 375 | - |
| + local program-aware scheduling | 602 | 1.61× |
| + global waiting queue (ThunderAgent) | 672 | a further 1.12× |

Other ablations:[^kangThunderAgentSimpleFast2026]

| Ablation | Setting | Result |
|---|---|---|
| Global vs local waiting queue | GLM-4.5-fp8 + mini-SWEAgent, 72 concurrent programs per node | Gain of the global queue widens to 1.28× at 4 nodes |
| Decay function, exponential $f(t)=e^{-t}$ | speedup vs constant (no decay) | mini-SWE-Agent 1.08×; ScienceAgent 1.63×; OSWorld 1.14× |
| Decay function, linear $f(t)=\max(1-t,0)$ | speedup vs constant (no decay) | ScienceAgent 1.39×; OSWorld 1.21× |
| Eviction policy on OpenHands | single H100 node, 72 concurrent programs | Shortest-first is roughly 2.0× the throughput of longest-first; average prefill time 7.5 s vs. 15.1 s |

### Scaling and deployment (appendix)

| Setting | Result |
|---|---|
| Up to 8 nodes (64×H100), GLM-4.6 + mini-SWEAgent, 72 programs per node, vs Cache-Aware Routing Policy in SGLang Model Gateway | Speedup widens from 1.79× at 2 nodes to 2.39× at 8 nodes |
| Global scheduler per-tick communication delay | 13.5 ms at 2 nodes to 22.7 ms at 8 nodes (1.68× for a 4× increase in nodes) |
| With SGLang HiCache (host-memory ratio 2.0), MiniMax M2.5 on [R2E-Gym](../datasets/r2e-gym.md), 8×H100, batch size 64 to 192 | Baseline P50 latency jumps from ∼10 s to ∼30 s at batch 160 and ∼70 s at batch 192; ThunderAgent holds P50 at ∼10 s and P90 at ∼20 s across the sweep |
| 8×A100, concurrency 48 and 72, vs vLLM | 1.71–2.08× on mini-SWEAgent and 1.16–1.62× on OpenHands |
| SkyRL recipe, Qwen3-32B on R2EGym | 3.01× wall-clock speedup over the baseline |

All rows: [^kangThunderAgentSimpleFast2026]

- Compute-to-bandwidth ratio (Table 3): H100 989 TFLOPs, 3350 GB/s, ratio 295.2; A100 312 TFLOPs, 2039 GB/s, ratio 153.0.[^kangThunderAgentSimpleFast2026]
- KV cache offloading with vLLM + LMCache degrades throughput under heavy agentic workloads because PCIe bandwidth is insufficient, and prefill-decode disaggregation exacerbates thrashing.[^kangThunderAgentSimpleFast2026]
- ThunderAgent is being integrated into NVIDIA Dynamo as part of Dynamo 2.0.[^kangThunderAgentSimpleFast2026]

## Limitations

- Reserving memory for acting programs leaves GPU memory idle during long-running tool execution; the time-decay mechanism is the paper's answer to this tradeoff.[^kangThunderAgentSimpleFast2026]
- Exponential decay is not best everywhere: on OSWorld, where tool durations are near-deterministic, it trails linear decay by about 6% (1.14× vs. 1.21×).[^kangThunderAgentSimpleFast2026]
- At low concurrency (24) on 8×A100, ThunderAgent only matches vLLM within noise, because the working set fits in HBM and thrashing is rare.[^kangThunderAgentSimpleFast2026]
- The decay-function proof assumes that tool return time cannot be predicted (Hypothesis F.1).[^kangThunderAgentSimpleFast2026]
- The paper has no dedicated limitations section.

## Related

- Methods proposed: [ThunderAgent](../methods/thunderagent.md), [Program-aware scheduling](../methods/program-aware-scheduling.md)
- Concepts: [KV cache](../methods/kv-cache.md), [KV cache thrashing](../methods/kv-cache-thrashing.md), [KV cache offloading](../methods/kv-cache-offloading.md)
- Systems compared or built on: [vLLM](../methods/vllm.md), [Continuum](../methods/continuum.md), [SGLang](../methods/sglang.md), [Autellix](../methods/autellix.md), [OpenHands](../methods/openhands.md), [SWE-agent](../methods/swe-agent.md)
- Benchmarks: [SWE-bench Lite](../benchmarks/swe-bench-lite.md), [HLE](../benchmarks/hle.md), [ScienceAgentBench](../benchmarks/scienceagentbench.md)
- Datasets: [R2E-Gym](../datasets/r2e-gym.md)
- Papers in this wiki cited by this paper: [Autellix](luoAutellixEfficientServing.md), [SGLang](zhengSGLangEfficientExecution2024.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md)
- Other papers in this wiki: [R2E-Gym](jainR2EGymProceduralEnvironments2025.md)

[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
