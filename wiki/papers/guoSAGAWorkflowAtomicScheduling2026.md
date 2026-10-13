---
type: Paper
title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
description: Distributed scheduler that treats a whole agent workflow as the schedulable unit, with workflow-aware KV cache eviction, session-affinity batching, and task-level fairness.
tags: [llm-serving, agent-serving, kv-cache, scheduling, fairness, gpu-cluster, ai899]
collections: [ai899]
authors: [Dongxin Guo, Jikun Wu, Siu-Ming Yiu]
year: 2026
doi: 10.48550/arXiv.2605.00528
arxiv: "2605.00528"
arxiv_version: 2605.00528v2
sources:
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
---

# SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters

Text source: arXiv HTML, version `2605.00528v2`.

## Summary

AI agents run tens to hundreds of chained LLM calls per task, interleaved with tool calls. GPU schedulers treat each call as an independent request and discard the KV cache between steps.[^guoSAGAWorkflowAtomicScheduling2026] On a 32-GPU cluster serving SWE-bench coding agents with vLLM v0.6.0, the authors measure that agents spend 38% of total time regenerating KV cache discarded during tool calls, GPU memory utilization averages only 42%, and end-to-end task completion has $6.0\times$ higher latency than the sum of individual inference times.[^guoSAGAWorkflowAtomicScheduling2026]

SAGA is a distributed scheduler that treats the whole agent workflow as the first-class schedulable unit (*program-level* scheduling).[^guoSAGAWorkflowAtomicScheduling2026] It has three mechanisms: Agent Execution Graphs that predict KV cache reuse across tool-call boundaries, session-affinity batching with work stealing, and Agent Fair Share, a fairness metric based on task completion time.[^guoSAGAWorkflowAtomicScheduling2026]

On a 64-GPU cluster, SAGA reduces task completion time by $1.64\times$ (geometric mean, $p<0.001$) over vLLM v0.15.1 with prefix caching and affinity routing, improves GPU memory utilization by $1.22\times$, and reaches 99.2% SLO attainment under multi-tenant interference. The cost is approximately 30% lower peak throughput than throughput-optimal batch scheduling.[^guoSAGAWorkflowAtomicScheduling2026]

## Contributions

- **Workflow-aware KV cache management.** Agent Execution Graphs (AEGs) capture multi-step reasoning structure and enable predictive cache retention with configurable TTL policies. The WA-LRU eviction policy is within $1.31\times$ of the offline-optimal policy.[^guoSAGAWorkflowAtomicScheduling2026]
- **Session-affinity batching with work stealing.** Local schedulers maximize cache reuse through session routing, and a global coordinator performs randomized work stealing.[^guoSAGAWorkflowAtomicScheduling2026]
- **Agent-level fair scheduling.** Agent Fair Share (AFS) with a theorem that bounds completion time deviation under bounded demand heterogeneity, using Lyapunov drift analysis.[^guoSAGAWorkflowAtomicScheduling2026]
- **Theoretical analysis.** A competitive ratio analysis of WA-LRU against Bélády's optimal offline policy, which the authors state is, to their knowledge, the first such empirical bound for workflow-aware KV cache eviction.[^guoSAGAWorkflowAtomicScheduling2026]
- **Empirical evaluation.** $1.73\times\pm 0.11$ and $1.55\times\pm 0.09$ task completion time reduction on SWE-bench and WebArena against vLLM+APC, and $1.22\times\pm 0.05$ memory utilization improvement. Against systems without workflow awareness, improvements reach $3.01\times$.[^guoSAGAWorkflowAtomicScheduling2026]

## Method

### Architecture

Three layers.[^guoSAGAWorkflowAtomicScheduling2026]

- **Agent interface layer.** Receives requests from agent frameworks (LangChain, AutoGen) and constructs AEGs. A pattern inference module is used when framework hints are unavailable.[^guoSAGAWorkflowAtomicScheduling2026]
- **Global scheduler.** Holds session-to-worker mappings, load information, and fairness metrics. Routes by session affinity and coordinates work stealing.[^guoSAGAWorkflowAtomicScheduling2026]
- **Worker pool.** Each worker runs an extended vLLM instance with workflow-aware KV cache management.[^guoSAGAWorkflowAtomicScheduling2026]

Cross-layer state is updated with bounded staleness of one scheduling epoch (100 ms).[^guoSAGAWorkflowAtomicScheduling2026]

### Agent Execution Graphs

An AEG is $G=(V,E,P,\phi)$: $V$ are LLM inference steps, $E$ are execution dependencies, $P:E\rightarrow[0,1]$ are transition probabilities, and $\phi$ maps each step to a tool type.[^guoSAGAWorkflowAtomicScheduling2026] For ReAct agents the AEG is typically a linear chain. For tree-of-thought agents it is a tree.[^guoSAGAWorkflowAtomicScheduling2026]

Three observability tiers:[^guoSAGAWorkflowAtomicScheduling2026]

| Tier | Source of the AEG | Cost |
|---|---|---|
| Explicit hints | LangChain callbacks, AutoGen message logs, delivered at task admission | none |
| Implicit traces | Inferred from tool-type patterns, keeping edges above $\theta_{\text{conf}}=0.7$ | 87% accuracy, 15.6% TCT degradation versus explicit hints |
| Cold-start | Served as a request-level workload until 30 tasks complete | at most 8% TCT added to the first 30 tasks |

### Workflow-aware KV cache management

- **WA-LRU eviction.** The eviction score is $P_{evict}(s)=\alpha\cdot\hat{R}(s)+\beta\cdot(1-P_{reuse}(s))+\gamma\cdot\hat{S}(s)$, where $\hat{R}$ is normalized idle time and $\hat{S}$ is normalized cache size. Defaults are $\alpha=0.3$, $\beta=0.5$, $\gamma=0.2$.[^guoSAGAWorkflowAtomicScheduling2026]
- **Reuse probability.** $P_{reuse}(s)=\sum_{u\in succ(v_{s})}P(v_{s}\rightarrow u)\cdot overlap(s,u)$. For linear ReAct chains the overlap is estimated as $n_{current}/(n_{current}+\hat{n}_{obs})$, where $\hat{n}_{obs}$ is the expected observation length for the tool type.[^guoSAGAWorkflowAtomicScheduling2026]
- **Tool-call-aware TTL.** Per-tool-type latency distributions are fitted as log-normal. The base TTL is the $p$-th percentile of expected duration (default 95%), scaled by $1-0.5\cdot m$ under memory pressure $m$, and capped at $TTL_{max}=300s$.[^guoSAGAWorkflowAtomicScheduling2026]
- **Memory pressure.** $m=\max\left(0,\frac{used_{kv}-threshold_{low}}{threshold_{high}-threshold_{low}}\right)$ with $threshold_{low}=0.7$ and $threshold_{high}=0.9$ of total GPU memory.[^guoSAGAWorkflowAtomicScheduling2026]
- **Speculative prefetching.** When a node finishes inference and starts its tool call, SAGA prefetches the prefix KV cache of the most likely successor, using spare GPU memory and separate CUDA streams.[^guoSAGAWorkflowAtomicScheduling2026]

### Session-affinity batching

- **Routing.** A request from session $s$ goes to the worker $w^{*}_{s}$ that caches the session if $load(w^{*}_{s})<\theta$ and the cache is still held. Otherwise it goes to the least-loaded worker. $\theta=0.8$.[^guoSAGAWorkflowAtomicScheduling2026]
- **Work stealing.** Triggered when a worker's queue is empty for $T_{idle}=100$ms, or when the load ratio between the most-loaded and least-loaded workers exceeds $R_{max}=2.0\times$. The victim migrates the oldest pending session's KV cache with [Llumnix](../methods/llumnix.md), and session affinity moves to the thief.[^guoSAGAWorkflowAtomicScheduling2026]
- **Contention mitigation.** Thread-local update buffering with 10 ms / 100-update batched flush ($12\times$ overhead reduction vs. per-update synchronization), lock-free session tables, and 64-byte cache-line alignment of per-worker counters.[^guoSAGAWorkflowAtomicScheduling2026]

### Agent Fair Share

- **Definition.** $AFS_{i}=\sum_{t\in\mathcal{T}_{i}}\frac{work_{remain}(t)}{deadline(t)-t_{now}}$ for tenant $i$ with active tasks $\mathcal{T}_{i}$. $work_{remain}(t)$ is the sum of estimated prefill and decode time over the unexecuted AEG nodes of task $t$.[^guoSAGAWorkflowAtomicScheduling2026]
- **Scheduling.** Every epoch (100ms) the coordinator recomputes AFS, allocates worker capacity in proportion to AFS, and triggers preemption if low-AFS tasks block high-AFS tasks for $>500$ms. A preempted task's KV cache is migrated, not discarded.[^guoSAGAWorkflowAtomicScheduling2026]
- **Theorem 2.** With $N$ tenants, capacity $C$, workloads $W_{i}$, and $\rho=\max_{i}W_{i}/\min_{i}W_{i}$: if $\sum_{i}W_{i}\leq C$ and $\rho\leq\rho_{max}$, then for any tenant with $W_{i}\leq C/N$, $Pr\left[TCT_{i}\leq(1+\epsilon)\cdot\mathbb{E}[TCT_{i}]\right]\geq 1-\delta$ with $\epsilon=O\left(\rho\cdot\sqrt{\frac{\log(N/\delta)}{n}}\right)$ over $n$ scheduling epochs. Only a proof sketch is given.[^guoSAGAWorkflowAtomicScheduling2026]

### Competitive ratio

- **Observation 1.** With $k$ steps each producing $c$ tokens of KV cache, complete eviction after each tool call costs $O(k^{2}\cdot c)$ regenerated tokens. A workflow-aware scheduler with perfect prediction costs $O(c)$.[^guoSAGAWorkflowAtomicScheduling2026]
- **Theorem 3.** If AEG predictions are correct with probability $1-\epsilon$ and tool-call durations have bounded variance, $CR_{empirical}(WA\text{-}LRU)\leq 1+\epsilon\cdot k_{max}+O\left(\frac{\sigma_{tool}}{TTL_{adaptive}}\right)$. The authors state this is an expected-case ratio under those assumptions, not a worst-case adversarial bound.[^guoSAGAWorkflowAtomicScheduling2026]

### Implementation

SAGA extends vLLM v0.6.0 (V1 engine) with approximately 8.5K lines of Python plus 1.2K lines of C++/CUDA. The distributed scheduler is built on Ray with gRPC. No modifications to agent code are required.[^guoSAGAWorkflowAtomicScheduling2026]

## Experiments & Results

### Setup

- Hardware: 8 nodes, each with 8 NVIDIA A100-80GB GPUs (64 GPUs total), 200Gbps InfiniBand HDR between nodes.[^guoSAGAWorkflowAtomicScheduling2026]
- Model: Llama-3-70B-Instruct with tensor parallelism across 4 GPUs per instance. With GQA and 32K context in FP16, each session needs ${\sim}10.7$GB of KV cache.[^guoSAGAWorkflowAtomicScheduling2026]
- Workloads: [SWE-bench](../benchmarks/swe-bench-verified.md) (500 "verified" subset tasks, mean 37 steps, max 150 steps), [WebArena](../benchmarks/webarena.md) (full 812 browser tasks, mean 18 steps), and a [BurstGPT](../datasets/burstgpt.md)-derived synthetic workload with 10 tenants (3 heavy, 4 medium, 3 light).[^guoSAGAWorkflowAtomicScheduling2026]
- Baselines: [vLLM](../methods/vllm.md) v0.6.0, vLLM+APC (v0.15.1 with Automatic Prefix Caching and PrefixCacheAffinityRouter), [SGLang](../methods/sglang.md) v0.5.8, [Llumnix](../methods/llumnix.md) v1.2, TRT-LLM+Scaffolding (TensorRT-LLM v1.1), and vLLM+[KVFlow](../methods/kvflow.md) (the authors' reimplementation on vLLM v0.6.0).[^guoSAGAWorkflowAtomicScheduling2026]
- Metrics: task completion time (TCT), GPU memory utilization, throughput, and SLO attainment (fraction of tasks meeting a deadline of $1.5\times$ expected time).[^guoSAGAWorkflowAtomicScheduling2026]
- Protocol: 10 repetitions with different random seeds, mean $\pm$ standard deviation, two-tailed Welch's t-test.[^guoSAGAWorkflowAtomicScheduling2026]

### Tool call latency (Table 1, from production traces)

| Tool Type | P50 (ms) | P95 (ms) | P99 (ms) |
|---|---|---|---|
| Code execution | 180 | 2,400 | 28,000 |
| File operations | 45 | 320 | 1,200 |
| Web/API calls | 850 | 4,500 | 45,000 |
| Database queries | 120 | 890 | 3,500 |

All rows: [^guoSAGAWorkflowAtomicScheduling2026]

### End-to-end performance (Table 3)

TCT in seconds, Mem = GPU memory utilization (%), mean $\pm$ std over 10 trials.[^guoSAGAWorkflowAtomicScheduling2026]

| System | SWE-bench TCT (s) | SWE-bench Mem% | WebArena TCT (s) | WebArena Mem% |
|---|---|---|---|---|
| vLLM v0.6.0 | 612.3$\pm$32.1 | 42.1$\pm$2.3 | 178.4$\pm$14.2 | 45.3$\pm$2.1 |
| vLLM+APC v0.15.1 | 352.1$\pm$21.4 | 58.7$\pm$2.8 | 127.3$\pm$10.1 | 61.2$\pm$2.5 |
| SGLang v0.5.8 | 387.2$\pm$24.3 | 56.2$\pm$2.6 | 138.7$\pm$11.3 | 58.9$\pm$2.4 |
| Llumnix v1.2 | 498.1$\pm$28.7 | 48.3$\pm$2.4 | 156.2$\pm$12.8 | 51.7$\pm$2.2 |
| TRT-LLM+Scaff. | 324.6$\pm$19.8 | 61.4$\pm$2.7 | 118.9$\pm$9.4 | 63.8$\pm$2.6 |
| vLLM+KVFlow | 298.4$\pm$18.2 | 64.1$\pm$2.9 | 108.2$\pm$8.7 | 66.4$\pm$2.7 |
| **SAGA** | 203.4$\pm$12.8 | 71.3$\pm$2.4 | 82.1$\pm$6.8 | 74.6$\pm$2.3 |

Speedup of SAGA (TCT ratio). `***` $p<0.001$, `**` $p<0.01$.[^guoSAGAWorkflowAtomicScheduling2026]

| Baseline | SWE-bench | WebArena |
|---|---|---|
| vs. vLLM v0.6.0 | 3.01$\times$\*\*\* | 2.17$\times$\*\*\* |
| vs. vLLM+APC | 1.73$\times$\*\*\* | 1.55$\times$\*\*\* |
| vs. SGLang | 1.90$\times$\*\*\* | 1.69$\times$\*\*\* |
| vs. Llumnix | 2.45$\times$\*\*\* | 1.90$\times$\*\*\* |
| vs. TRT-LLM | 1.60$\times$\*\*\* | 1.45$\times$\*\* |
| vs. KVFlow | 1.47$\times$\*\*\* | 1.32$\times$\*\* |

Geometric mean speedup vs. vLLM+APC: $1.64\times$.[^guoSAGAWorkflowAtomicScheduling2026]

Share of SWE-bench time spent regenerating KV cache after tool calls: 38% for vLLM v0.6.0, 22% for vLLM+APC, 8% for SAGA.[^guoSAGAWorkflowAtomicScheduling2026]

### Eviction policy vs. Bélády's optimal (Table 2)

Competitive ratio on production traces. Lower is better (1.0 = optimal).[^guoSAGAWorkflowAtomicScheduling2026]

| Policy | SWE-bench | WebArena | Mean |
|---|---|---|---|
| Standard LRU | 2.84 | 2.12 | 2.48 |
| LRU + Prefix (vLLM v0.5) | 1.97 | 1.74 | 1.86 |
| WA-LRU (ours) | 1.31 | 1.28 | 1.30 |

On SWE-bench the prediction error is $\epsilon=0.13$ and $k_{max}=150$, so the Theorem 3 bound is $1+\epsilon\cdot k_{max}\approx 20.5$, which the authors call far from tight.[^guoSAGAWorkflowAtomicScheduling2026]

### Ablation on SWE-bench (Table 4)

| Configuration | TCT (s) | vs. Full |
|---|---|---|
| Full SAGA | 203.4$\pm$12.8 | — |
| w/o Workflow-aware eviction | 312.8$\pm$18.3 | +54% |
| w/o Tool-call TTL | 289.1$\pm$16.7 | +42% |
| w/o Speculative prefetch | 241.6$\pm$14.2 | +19% |
| w/o Session affinity | 398.2$\pm$22.4 | +96% |
| w/o Work stealing | 267.3$\pm$15.9 | +31% |
| w/o AFS fairness | 218.7$\pm$13.1 | +8% |

All rows: [^guoSAGAWorkflowAtomicScheduling2026]

### Framework hints vs. pattern inference (Table 5)

| Mode | TCT (s) | AEG Accuracy | vs. Hints |
|---|---|---|---|
| With hints | 203.4$\pm$12.8 | 100% | — |
| Pattern inference | 235.2$\pm$14.6 | 87% | +15.6% |
| No AEG (baseline) | 398.2$\pm$22.4 | — | +95.8% |

Pattern inference still gives $2.60\times$ speedup over vLLM v0.6.0.[^guoSAGAWorkflowAtomicScheduling2026]

### Multi-tenant SLO attainment (Table 6)

Percent of tasks meeting the deadline, by tenant type, on the BurstGPT-derived workload.[^guoSAGAWorkflowAtomicScheduling2026]

| System | Heavy | Medium | Light | Overall |
|---|---|---|---|---|
| vLLM | 89.4 | 72.1 | 43.2 | 67.3 |
| SGLang | 91.2 | 78.6 | 51.4 | 73.4 |
| Llumnix | 92.8 | 81.3 | 58.9 | 77.2 |
| **SAGA** | 99.1 | 99.4 | 98.7 | 99.2 |

For light tenants, vLLM has P99 = $12.4\times$ expected TCT, and SAGA has P99 $<$ $1.8\times$ expected.[^guoSAGAWorkflowAtomicScheduling2026]

### Scalability, load balance, and overhead

- $6.4\times$ speedup scaling from 8 to 64 GPUs (80% efficiency) on fixed workloads, and near-linear weak scaling ($0.94\times$ per doubling) up to 512 concurrent agents.[^guoSAGAWorkflowAtomicScheduling2026]
- On a 32-GPU subset, worker utilization ranges narrow from 23 to 94% without work stealing to 68 to 79% with stealing.[^guoSAGAWorkflowAtomicScheduling2026]
- Migration occurs 2.3 times per task on average, with a maximum of 5 across all trials.[^guoSAGAWorkflowAtomicScheduling2026]

Overhead breakdown (Table 7, 64 GPUs, 32 tenants):[^guoSAGAWorkflowAtomicScheduling2026]

| Component | Mean (ms) | P95 (ms) | CPU (%) |
|---|---|---|---|
| Coordinator cycle | 12.3 | 28.7 | 4.2 |
| AFS computation | 3.1 | 8.4 | — |
| AEG construction | 45.2 | 112.8 | — |
| Work stealing (migration) | 230 | 890 | — |

### Execution strategy on SWE-bench, 32 GPUs (Table 8)

| Strategy | TCT (s) | Throughput | Evict Rate |
|---|---|---|---|
| Pure BFS | 487.2$\pm$28.4 | 12.4 t/m | 78% |
| Pure DFS | 623.1$\pm$34.2 | 4.2 t/m | 3% |
| **Hybrid (SAGA)** | 203.4$\pm$12.8 | 8.7 t/m | 12% |

All rows: [^guoSAGAWorkflowAtomicScheduling2026]

### Sensitivity

- Parameters (Table 9): no single-parameter perturbation within the tested ranges produces $>$8% TCT change. The most sensitive are $\beta$ ($<$8%) and $T_{idle}$ ($<$7%).[^guoSAGAWorkflowAtomicScheduling2026]
- Tool latency variance (Table 10), mean tool latency held constant at 1.2s:[^guoSAGAWorkflowAtomicScheduling2026]

| CV | TCT (s) | TTL Accuracy | Evict Rate | vs. CV=0.5 |
|---|---|---|---|---|
| 0.5 | 195.1$\pm$11.2 | 96% | 9% | — |
| 1.0 | 203.4$\pm$12.8 | 93% | 12% | +4% |
| 1.5 | 218.6$\pm$15.3 | 88% | 18% | +12% |
| 2.0 | 241.3$\pm$18.7 | 82% | 24% | +24% |
| 3.0 | 298.4$\pm$24.1 | 71% | 35% | +53% |

### CPU swap as an alternative

The authors chose retention in GPU memory over offloading idle KV caches to host DRAM. A 10.7 GB cache takes $\approx$430 ms one-way over PCIe Gen4 $\times$16 at 25 GB/s, so a round trip is $\approx$860 ms uncontested. Three of the four tool classes in Table 1 have a P50 below this round trip.[^guoSAGAWorkflowAtomicScheduling2026] The authors treat swap as complementary for over-subscribed regimes ($>$95% utilization).[^guoSAGAWorkflowAtomicScheduling2026]

## Limitations

The paper lists these in its Section 1.5.[^guoSAGAWorkflowAtomicScheduling2026]

- **Workflow observability.** Without framework hints, SAGA falls back to pattern inference with 12 to 18% TCT degradation, and degrades further on dynamic multi-agent frameworks (AutoGen, CrewAI) where structure is generated on the fly.[^guoSAGAWorkflowAtomicScheduling2026]
- **Tool-latency tail.** Black-swan events ($>5\times$ P99) still cause eviction.[^guoSAGAWorkflowAtomicScheduling2026]
- **Task-duration estimation.** AFS needs task-duration estimates that may be inaccurate for agent types absent from profiling.[^guoSAGAWorkflowAtomicScheduling2026]
- **Single-datacenter scope.** Geo-distributed deployment is future work.[^guoSAGAWorkflowAtomicScheduling2026]
- **Model-family coverage.** The evaluation uses Llama-3-70B-Instruct only. MoE architectures need routing-aware extensions.[^guoSAGAWorkflowAtomicScheduling2026]
- **Memory-pressure regime.** The evaluation reaches 71 to 75% peak utilization. Behavior under over-subscription ($>$95%) is not empirically validated.[^guoSAGAWorkflowAtomicScheduling2026]
- **Throughput tradeoff.** Approximately 30% throughput reduction relative to throughput-maximizing batch scheduling. SAGA suits latency-sensitive interactive deployments, not batch workloads.[^guoSAGAWorkflowAtomicScheduling2026]

Further caveats in the text:

- Multi-axis adversarial parameter perturbation was not characterized empirically.[^guoSAGAWorkflowAtomicScheduling2026]
- The work-stealing bound (Theorem 1) assumes zero-cost migration, and SAGA's migration costs a mean of 230 ms.[^guoSAGAWorkflowAtomicScheduling2026]
- The worst-case competitive ratio for online policies on KV-cache traces remains open.[^guoSAGAWorkflowAtomicScheduling2026]
- Source inconsistency: Section 7.1 gives prefix-caching a competitive ratio of $1.86\times$ on SWE-bench, and Table 2 gives 1.97 on SWE-bench with 1.86 as the mean.[^guoSAGAWorkflowAtomicScheduling2026]
- Source inconsistency: Section 9.1.1 calls 1.2s the median tool-call duration, and Table 10 calls 1.2s the mean tool latency.[^guoSAGAWorkflowAtomicScheduling2026]

## Related

- Proposed system: [SAGA](../methods/saga.md)
- Methods: [KV cache](../methods/kv-cache.md), [Prefix caching](../methods/prefix-caching.md), [Work stealing](../methods/work-stealing.md), [ReAct](../methods/react.md), [PagedAttention](../methods/paged-attention.md)
- Systems compared or built on: [vLLM](../methods/vllm.md), [SGLang](../methods/sglang.md), [Llumnix](../methods/llumnix.md), [KVFlow](../methods/kvflow.md), [TensorRT-LLM](../methods/tensorrt-llm.md)
- Benchmarks and datasets: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [WebArena](../benchmarks/webarena.md), [BurstGPT](../datasets/burstgpt.md)
- Papers in this wiki cited by this paper: [Parrot](linParrotEfficientServing2024.md), [Autellix](luoAutellixEfficientServing.md), [SGLang](zhengSGLangEfficientExecution2024.md), [WebArena](zhouWebArenaRealisticWeb2024.md)
- Agent frameworks it receives workflows from: [LangChain](../methods/langchain.md), [AutoGen](../methods/autogen.md)

[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
