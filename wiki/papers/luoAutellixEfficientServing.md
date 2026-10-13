---
type: Paper
title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
description: LLM serving system that schedules LLM calls by the attained service of their parent agentic program (PLAS, ATLAS) and routes calls across engines by program data locality.
tags: [llm-serving, agentic-programs, scheduling, head-of-line-blocking, load-balancing, kv-cache, ai899]
collections: [ai899]
authors: [Michael Luo, Xiaoxiang Shi, Colin Cai, Tianjun Zhang, Justin Wong, Yichuan Wang, Chi Wang, Yanping Huang, Zhifeng Chen, Joseph E. Gonzalez, Ion Stoica]
arxiv: "2502.13965"
arxiv_version: 2502.13965v1
sources:
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
---

# Autellix: An Efficient Serving Engine for LLM Agents as General Programs

Text source: arXiv HTML, version `2502.13965v1`.

## Summary

An *agentic program* is a dynamic execution workflow, represented by a directed acyclic graph (DAG), that consists of LLM calls from one or more agents and external interrupts (tool calls, generic code execution, or human inputs).[^luoAutellixEfficientServing] Existing LLM serving engines such as vLLM optimize individual LLM calls and ignore program-level context, so programs suffer head-of-line (HoL) blocking at both the LLM-call level and the program level.[^luoAutellixEfficientServing]

Autellix is an LLM serving system that treats programs as first-class citizens. It intercepts the LLM calls submitted by programs, records program-level statistics in a global process table, and prioritizes each call by the total execution time of its program's previously completed calls.[^luoAutellixEfficientServing] It proposes two non-clairvoyant scheduling algorithms, PLAS for single-threaded programs and ATLAS for multi-threaded programs, plus a data locality-aware load balancer across engines.[^luoAutellixEfficientServing] The paper reports that Autellix improves throughput of programs by 4-15× at the same latency compared to state-of-the-art systems such as vLLM, and by up to 1.5x over standard load-balancers across engines.[^luoAutellixEfficientServing]

## Contributions

- The first formalization of agentic programs as dynamic, non-deterministic DAGs of LLM calls and interrupts.[^luoAutellixEfficientServing]
- A non-clairvoyant scheduler informed by program-level statistics that requires only the cumulative service times of LLM calls within the same program.[^luoAutellixEfficientServing]
- A simple load-balancing policy across multiple engines that balances data locality and KV-cache recomputation.[^luoAutellixEfficientServing]
- An easily deployable system that integrates a stateful API with existing programming and agent frameworks.[^luoAutellixEfficientServing]

## Method

### Motivation

- A single-threaded program's end-to-end latency has three components: waiting time (total queuing time of its LLM calls on the engine), execution time (cumulative feedforward time of LLM calls), and interceptions (time waiting for external interrupts).[^luoAutellixEfficientServing]
- Across chatbot, ReAct, and MCTS workloads, the majority of a program's time is spent waiting as load increases.[^luoAutellixEfficientServing]
- **Call-level blocking.** LLM calls with long decodes delay shorter ones. vLLM waits for ongoing calls to finish decoding before scheduling new ones.[^luoAutellixEfficientServing]
- **Program-level blocking.** Longer programs with many LLM requests delay shorter programs. MLFQ places every new LLM call in the highest priority queue, so new calls of long programs starve short programs, and MLFQ may perform close to, or even worse, than FCFS.[^luoAutellixEfficientServing]
- **Data locality.** Within a single program, prefix cache-hit rates remain above 90% across all input lengths. Across different programs, the cache-hit rate decays exponentially with input length, which suggests that programs only share the system prompt.[^luoAutellixEfficientServing]
- In the paper's illustrative example (four programs, max batch size 2), FCFS and MLFQ both incur a total waiting time of 18 units and PLAS reduces it to 12 units.[^luoAutellixEfficientServing]

### Process table

Autellix is stateful: a program runs on the user's local machine, establishes a session, and issues LLM calls with a session ID.[^luoAutellixEfficientServing] A global process table holds one entry per running program with: service time, waiting time, engine ID(s), threads metadata (active LLM calls with their arrival, waiting, and service times), most recent call arrival, and most recent call completion.[^luoAutellixEfficientServing] Autellix is non-clairvoyant: it assumes no knowledge of program arrivals, workflow structure, or workload distributions, and builds an internal representation of the DAG as the program runs.[^luoAutellixEfficientServing]

### PLAS (Program-Level Attained Service)

PLAS extends Least-Attained-Service (LAS) to programs. The priority of the $j$th LLM call $c_j$ is the sum of the runtimes $t_k$ of all prior LLM calls of the same program:[^luoAutellixEfficientServing]

$$
p(c_{j})=\sum_{k<j,\ c_{k}.id=c_{j}.id}t_{k}
$$

A larger value means lower priority.[^luoAutellixEfficientServing]

### ATLAS (Adaptive Thread-Level Attained Service)

A multi-threaded program's completion time is dictated by the DAG's critical path, the longest sequence of dependent calls from start to finish.[^luoAutellixEfficientServing] ATLAS generalizes PLAS by prioritizing a call from the priorities and completed service times of its parents $\mathcal{P}(c_j)$:[^luoAutellixEfficientServing]

$$
p(c_{j})=\begin{cases}0&\text{if }c_{j}\text{ is root}\\ \max_{c_{k}\in\mathcal{P}(c_{j})}\{p(c_{k})+t_{k}\}&\text{otherwise}\end{cases}
$$

In practice ATLAS keeps a single scalar per program in the process table, the longest observed critical path. Each active call inherits it as its initial priority, and a completing call updates it only if its own critical path is longer. This avoids tracking dependencies between LLM calls.[^luoAutellixEfficientServing] Because all calls of a program derive priority from the same entry, the scheduler groups a program's parallel calls.[^luoAutellixEfficientServing]

### Preemptive scheduling

- **Discretized priorities.** Priorities are binned into K queues $Q_1,\dots,Q_K$, where queue $Q_i$ covers $[Q_i^{lo},Q_i^{hi})$ with $Q_1^{lo}=0$ and $Q_K^{hi}=\infty$. Unlike traditional MLFQ, an arriving call is placed in the queue that matches its program's priority, not in $Q_1$. Calls receive the queue's time quantum, run in FCFS order within a queue, and are demoted to a lower queue when the quantum is exhausted.[^luoAutellixEfficientServing]
- **Anti-starvation.** A call $c$ of program $p$ is promoted to $Q_1$ if $W_{\text{total}}/T_{\text{total}}\geq\beta$, where $W_{\text{total}}=W_p+W_c$ is total waiting time and $T_{\text{total}}=T_p+T_c$ is service time. After promotion only $W_c$ and $T_c$ are set to zero.[^luoAutellixEfficientServing]
- **Multi-step scheduling.** The scheduler runs once every $N$ decoding steps and overprovisions queued requests already on the GPU, so new requests are added immediately when others finish before $N$ steps.[^luoAutellixEfficientServing]
- **Swap kernel.** vLLM transfers each KV block individually via cudaMemcpyAsync. Autellix allocates a host buffer and consolidates all KV blocks into a single contiguous chunk for one bulk transfer.[^luoAutellixEfficientServing]

### Load balancer

Short requests below 2048 tokens achieve high cache hit rates ($\geq 75\%$) across any engine because of common system prompts.[^luoAutellixEfficientServing] The load balancer therefore routes a call with at most 2048 tokens to the least-used engine, and pins a longer call to the engine already assigned to its program (or assigns the least-used engine if the program has none).[^luoAutellixEfficientServing]

### Implementation

- Frontend, scheduler, and load balancer total 5k lines of Python and CUDA/C++ code.[^luoAutellixEfficientServing]
- The frontend extends OpenAI's Chat Completion and vLLM's Python APIs. It issues `start_session` on program initialization, annotates later LLM calls with session, program, and thread IDs, and calls `end_session` on completion or error.[^luoAutellixEfficientServing]
- Built on vLLM v0.6.1. Only the scheduler is modified (PLAS, ATLAS, and MLFQ policies, plus the memory swapping kernels).[^luoAutellixEfficientServing]
- Multi-engine support is an `AsyncMultiLLMEngine` built on `AsyncLLMEngine`. Each replica runs in a dedicated Python process and a meta-engine coordinates them over IPC.[^luoAutellixEfficientServing]

## Experiments & Results

### Setup

- Models and testbed: LLaMA-3.1-8B, 70B and Falcon-180B, running on 1, 4, and 8 GPUs, respectively, on a GCP a2-ultragpu-8g instance with eight A100-SXM4-80GB GPUs connected via NVLink, 1360 GB host memory, PCIe-4.0×16, and 2 TB of disk space.[^luoAutellixEfficientServing]
- Metric: program-level token latency, the total program response time divided by the number of tokens generated. For multi-threaded programs it is the critical path response time divided by the total tokens across all threads.[^luoAutellixEfficientServing]
- Baselines (all with the same max batch size): vLLM v0.6.1 (FCFS); vLLM-opt (chunk-prefill, prefix-caching, and multi-step scheduling enabled); MLFQ (preemption on top of vLLM-opt).[^luoAutellixEfficientServing]
- Trace: programs (not LLM calls) are sampled randomly from the workloads, with arrivals generated by a Poisson process.[^luoAutellixEfficientServing]

### Workloads

| Workload | Program type | LLM calls per program | Prefill tokens per call (mean) | Decode tokens per call (mean) |
|---|---|---|---|---|
| [ShareGPT](../datasets/sharegpt.md) | Chatbot agent (entire conversations replayed) | mean of 6.66, max of 80 | 256 | 277 |
| [BFCL](../benchmarks/bfcl.md) (BFCLv3) | ReAct agent | mean of 10.75, maximum of 70 | 735.06 | 34.14 |
| [LATS](../methods/lats.md) (MCTS on [HotpotQA](../datasets/hotpotqa.md)) | Monte Carlo Tree Search | on average 159.7 | 467.2 | 72.6 |
| Mixed | Equal sampling from the three workloads | not stated | not stated | not stated |

All rows: [^luoAutellixEfficientServing]

### Single-engine throughput at the same latency (Figure 12)

The paper gives these as "up to" factors in the text. The underlying curves are in a figure.[^luoAutellixEfficientServing]

| Workload | Autellix vs vLLM | Autellix vs vLLM-opt | Autellix vs MLFQ |
|---|---|---|---|
| ShareGPT and BFCL (single-threaded, PLAS) | up to 8× | twice | 1.5× under heavy load |
| LATS (multi-threaded, ATLAS) | up to 5× | up to 2× | up to 2.5× |
| Mixed | up to 15× | 4× | 5.5× |

All rows: [^luoAutellixEfficientServing]

- On the single-threaded workloads, MLFQ improves throughput by 1.5× over vLLM-opt.[^luoAutellixEfficientServing]
- vLLM performs worst because it lacks prefix caching.[^luoAutellixEfficientServing]
- On LATS, MLFQ is worse than vLLM-opt (Autellix beats MLFQ by up to 2.5× and vLLM-opt by up to 2×). The paper attributes this to MLFQ disrupting threads of the same program.[^luoAutellixEfficientServing]
- Tail latency (LLaMA-3.1-8B): in 7 of 8 scenarios Autellix has lower P95/P99 latencies than MLFQ and vLLM-opt, and it improves throughput by up to 1.7× for P95/99 tail latencies.[^luoAutellixEfficientServing]
- Steady state over a one-hour trace (LLaMA-3.1-8B, single A100-80GB, chatbot conversations): Autellix consistently handles 10 additional concurrent LLM calls compared to vLLM's FCFS policy.[^luoAutellixEfficientServing]
- A single LLM engine handles only 0.2 programs per second for MCTS.[^luoAutellixEfficientServing]

### Multi-engine (Figure 14, Figure 15)

- Baselines: Round Robin and Least Used load balancing, both under the same scheduling policies (PLAS, ATLAS).[^luoAutellixEfficientServing]
- Configurations: four replicas of LLaMA3.1-8B and two replicas of LLaMA3.1-70B, with the ShareGPT and LATS workloads.[^luoAutellixEfficientServing]
- Autellix delivers up to 1.4× higher throughput compared to both baselines. The benefit is more pronounced on ShareGPT.[^luoAutellixEfficientServing]
- Scalability (ShareGPT, LLaMA3.1-8B): the max arrival rate at a fixed SLO scales linearly with the number of replicas.[^luoAutellixEfficientServing]

### Ablations (LLaMA3.1-8B, ShareGPT and LATS)

| Ablation | Result |
|---|---|
| Offline batch inference (all programs submitted at the start, ShareGPT) | Autellix decreases the average makespan by 10-40%. At 4000 programs, MLFQ fails to complete execution with Out-Of-Memory errors despite a swap space >1.2TB. |
| Timing breakdown | Autellix reduces wait and swap times. Autellix and MLFQ have higher scheduling times than vLLM-opt's FCFS, and Autellix has lower scheduling overhead than MLFQ. |
| Comparison to optimal scheduling (simulation) | Autellix outperforms FCFS, Round Robin, and MLFQ. A noticeable gap remains to SRPT, which has complete knowledge of each program's runtime. |
| Swap kernel | Reduces swaps by up to 18x and swap times by 3-7x, and achieves 1.3x higher throughput than vLLM's implemented kernel. |

All rows: [^luoAutellixEfficientServing]

## Limitations

- The frontend is a research prototype and lacks safeguards against user modification of the underlying package.[^luoAutellixEfficientServing]
- In simulation a noticeable gap remains between Autellix and the clairvoyant SRPT policy.[^luoAutellixEfficientServing]
- Autellix assumes no prior knowledge of the execution DAG. Optimizations that anticipate a program's next steps (branch prediction, speculative execution of future LLM calls) are deferred to future work.[^luoAutellixEfficientServing]
- Discrete prioritization starves long, low-priority programs, which the anti-starvation threshold $\beta$ trades off against average response time.[^luoAutellixEfficientServing]
- Most headline results appear only as latency curves in figures. The text gives "up to" factors, not per-arrival-rate numbers.[^luoAutellixEfficientServing]
- The caption of Figure 9 gives the best-case makespan as 14 units and the worst-case as 11 units, while the body text says the makespan increases from 11 to 14 units without considering critical paths.[^luoAutellixEfficientServing]
- The paper has no dedicated limitations section.

## Related

- Methods proposed: [PLAS](../methods/plas.md), [ATLAS](../methods/atlas.md)
- Methods built on or compared: [Least-Attained-Service](../methods/least-attained-service.md), [Multi-level feedback queue](../methods/mlfq.md), [Prefix caching](../methods/prefix-caching.md), [KV cache](../methods/kv-cache.md), [KV cache swapping](../methods/kv-cache-swapping.md), [Chunked prefill](../methods/chunked-prefill.md), [PagedAttention](../methods/paged-attention.md)
- Systems compared or built on: [vLLM](../methods/vllm.md)
- Workloads: [ShareGPT](../datasets/sharegpt.md), [BFCL](../benchmarks/bfcl.md), [LATS](../methods/lats.md), [HotpotQA](../datasets/hotpotqa.md)
- Papers in this wiki cited by this paper: [Parrot](linParrotEfficientServing2024.md), [SGLang](zhengSGLangEfficientExecution2024.md)

[^luoAutellixEfficientServing]: Luo et al.
