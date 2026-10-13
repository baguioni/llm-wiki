---
type: Paper
title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
description: Cluster-level LLM serving system that uses advisory requests from multi-turn workloads to prefetch and migrate K,V caches off the critical path, enabling request-level load balancing.
tags: [llm-serving, kv-cache, multi-turn, scheduling, load-balancing, memory-management, ai899]
collections: [ai899]
authors: [Saurabh Agarwal, Anyong Mao, Aditya Akella, Shivaram Venkataraman]
year: 2024
doi: 10.48550/arXiv.2412.16434
arxiv: "2412.16434"
arxiv_version: 2412.16434v1
sources:
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
---

# SYMPHONY: Improving Memory Management for LLM Inference Workloads

Text source: arXiv HTML, version `2412.16434v1`.

## Summary

LLM workloads such as chatbots, code editors, and agents are multi-turn: each new request in a session depends on the K,V caches of all earlier requests in that session.[^agarwalSYMPHONYImprovingMemory2024] Existing serving engines either discard and recompute the K,V cache ([vLLM](../methods/vllm.md), TensorRT-LLM) or offload it to host memory or disk and load it back.[^agarwalSYMPHONYImprovingMemory2024] The paper reports that recomputation makes more than 99% of processed tokens redundant in a real-world multi-turn chatbot dataset, and that offloading makes the workload *sticky* (all requests of a session must go to the node that holds the cache), which forces session-granularity load balancing and causes load imbalance.[^agarwalSYMPHONYImprovingMemory2024]

Symphony is built on the observation that multi-turn workloads give hints about future requests, which the paper calls [advisory requests](../methods/advisory-requests.md). Symphony uses them to migrate K,V caches off the critical serving path and to schedule at request granularity.[^agarwalSYMPHONYImprovingMemory2024] The abstract reports that Symphony can handle over 8× the number of requests compared to state-of-the-art baselines with a similar latency profile.[^agarwalSYMPHONYImprovingMemory2024]

## Contributions

The paper has no explicit contribution list. The items below are the components it presents.

- The advisory-request abstraction: a signal that a request for a given session will arrive soon, sent when a chatbot user starts typing or by an upstream agent while it processes its prompt.[^agarwalSYMPHONYImprovingMemory2024]
- A two-component system: a cluster-level scheduler that does request-level scheduling, and a per-node manager that runs a hierarchical memory system for K,V caches.[^agarwalSYMPHONYImprovingMemory2024]
- Three techniques that make prefetching work with partial information: layer-wise asynchronous reads and writes, a priority-based K,V cache scheme, and cooperative memory management with the serving framework's scheduler.[^agarwalSYMPHONYImprovingMemory2024]
- A request prioritization policy built on the same request-level scheduling, as an example of a policy beyond load balancing.[^agarwalSYMPHONYImprovingMemory2024]

## Method

### Motivation measurements

| Observation | Value |
|---|---|
| K,V cache size, LLama-3.1-70B at 32K context length | approximately 10GB |
| Maximum K,V cache size, LLaMa-70B at full 128K context length | 40 GB |
| Multi-turn share of ShareGPT conversations | 73.4% (some sessions extend beyond 400 turns) |
| Redundant pre-filled tokens under recompute on ShareGPT | more than 50% once conversation turns exceed 3 |
| Retain: requests that saturate GPU HBM when serving LLaMa-8b on ShareGPT | 36 |
| Swap vs Recompute, 1000 ShareGPT samples on one A100, LLaMa-7B | total pre-fill time reduced by a factor of 4.9, decode time by a factor of 1.68 |
| Swap baseline (InferCept) vs Recompute on 8 A100 GPUs with session-sticky routing | swapping takes 1.7 times longer |
| Load imbalance with stateful serving (1024 concurrent users, 8 GPUs, InferCept) | one node can serve $3.1\times$ the median load; most and least loaded GPU can differ by 300 requests |
| K,V cache per token, LLaMa-3.1 8B | approximately 1.1 MB |
| Host-memory capacity, 256 GB of main memory | about 238K tokens; at an average ShareGPT session of around 2.2K tokens, a maximum of 108 concurrent sessions |
| Advisory request lead time, chatbot (shareGPT) | 11.3 seconds earlier on average |
| Advisory request lead time, MetaGPT served with 4 A100s | 5.8 seconds earlier on average |

All rows: [^agarwalSYMPHONYImprovingMemory2024]

Migrating K,V caches on demand to fix the imbalance of the swap baseline increases the time to serve requests further, because requests must wait for the cache to be migrated.[^agarwalSYMPHONYImprovingMemory2024]

### Advisory requests

An advisory request carries `session_id`, `model_id`, `expected_arrival`, `ordered`, and `priority`.[^agarwalSYMPHONYImprovingMemory2024] For chatbots it is sent with no arrival time and no ordering. For agent workloads, offline profiling gives a lower bound on the current agent's runtime, so `expected_arrival` can be set (3.2 in the paper's example), but ordering is still unknown.[^agarwalSYMPHONYImprovingMemory2024]

### Scheduler and node manager

- **Scheduler.** It exposes one interface for inference requests and one for advisory requests. On an advisory request it does request-level scheduling, attaches the current K,V cache location, forwards the request to a node manager, and records the new cache location. The later inference request is routed to the node chosen for its advisory request.[^agarwalSYMPHONYImprovingMemory2024] The policy used in the paper is load balancing that distributes requests evenly across nodes.[^agarwalSYMPHONYImprovingMemory2024]
- **Node manager.** It handles advisory requests, inference requests, and K,V cache fetch requests from other node managers. If the cache is on another node it issues an RPC call to retrieve it. If the cache is local it moves it to the fastest memory tier that memory constraints allow.[^agarwalSYMPHONYImprovingMemory2024]

### Techniques

- **Layer-wise asynchronous reads and writes.** Inference needs the K,V cache only for the layer being computed, so caches are loaded and stored in parallel with inference execution. A background thread keeps writing new K,V caches to disk, and one copy of each K,V cache is always kept in the slowest tier (disk), so higher tiers can be evicted on demand without data loss.[^agarwalSYMPHONYImprovingMemory2024]
- **Priority-based K,V cache.** Advisory requests do not give the order of arrival across sessions. K,V cache blocks are prioritized by layer: blocks of lower layers get higher priority in GPU HBM because they are needed first, and the later layers are fetched while decoding has already started.[^agarwalSYMPHONYImprovingMemory2024]
- **Cooperative memory management.** The number of generated tokens is not known in advance, so free GPU memory cannot be estimated accurately. The node manager greedily fills free GPU memory with prefetched K,V cache, and the serving library can overwrite that memory under pressure. Blocks of later layers have the lowest priority, followed by the K,V caches with the smallest size. This is used only for GPU HBM.[^agarwalSYMPHONYImprovingMemory2024]

### Implementation

Symphony is around 2400 lines of Python, uses gRPC between scheduler and node managers, connects every node manager to all others for on-demand K,V cache migration, and integrates with vLLM's scheduler for block management.[^agarwalSYMPHONYImprovingMemory2024]

## Experiments & Results

### Setup

- Baselines: [vLLM](../methods/vllm.md) (recomputes the K,V cache for every request) and [InferCept](../methods/infercept.md) (offloads K,V caches to host memory). The authors add a top-level scheduler to both: for vLLM it balances load as Symphony does, and for InferCept the first request of a session goes to the node with the fewest requests and later requests of the session go to the same node.[^agarwalSYMPHONYImprovingMemory2024]
- Testbed: 2 nodes, each with 4 Nvidia A100 GPUs with 80 GB of HBM, 256 GB of DRAM, and 4 TB of SSDs, connected by a 100Gbps Ethernet link.[^agarwalSYMPHONYImprovingMemory2024]
- Models: LLaMa-3.1 8B with 128K context length and LLaMa-2-13B with 32K context length.[^agarwalSYMPHONYImprovingMemory2024]
- Trace: 1000 samples of [ShareGPT](../datasets/sharegpt.md) unless otherwise stated. Request arrival times within a session are generated from human reading and typing speed, and the trace generator keeps a fixed number of active users.[^agarwalSYMPHONYImprovingMemory2024]
- Metrics: normalized latency (mean of each request's end-to-end latency divided by its output length), time to first token (TTFT), and number of requests served.[^agarwalSYMPHONYImprovingMemory2024]

### Comparison with vLLM and InferCept

| Metric | Setting | Result |
|---|---|---|
| Normalized end-to-end latency vs vLLM | LLaMa-3.1 8B, varying concurrent users | reduced by a factor of $1.4\times$ to $1.9\times$ |
| Normalized end-to-end latency vs vLLM | LLaMa-2-13B | reductions of $1.31\times$ to $1.9\times$ |
| Speedup vs InferCept | not stated | up to $2.5\times$ |
| Time to first token vs vLLM and InferCept | both models | reduced by up to $2.4\times$ |
| Users served at similar time per output token vs vLLM | same number of GPUs | up to $8\times$: vLLM at 64 users has 18ms average time per output token, Symphony at 512 users has 20.5ms |
| Requests handled vs InferCept | high load (1024 users) | over $4.2\times$ |
| Load imbalance of InferCept | LLaMa-3.1-8b, 256 concurrent users | maximum users on one instance is more than $3.1\times$ the median load across machines |
| Total time vs vLLM, [MetaGPT](../methods/metagpt.md) agent workload | LLaMa-3.1-8b across 8 GPUs | reduced by $2.8\times$ |

All rows: [^agarwalSYMPHONYImprovingMemory2024]

- The Figure 13 caption for LLaMa-2 13b reports up to $2.6\times$ speedup in TPOT and around $2.56\times$ in TTFT.[^agarwalSYMPHONYImprovingMemory2024]
- The introduction reports a $2.4\times$ reduction in end-to-end latency on average compared to vLLM, and $4\times$ the requests served by vLLM with $1.3\%$ inflation in average end-to-end latency.[^agarwalSYMPHONYImprovingMemory2024]
- The paper attributes the gain over vLLM to removing redundant computation, which also lets more requests move to the decode phase sooner under [continuous batching](../methods/continuous-batching.md). It attributes the gain over InferCept to load imbalance in InferCept's stateful serving, where one server can have as much as $2.8\times$ the median load across the cluster.[^agarwalSYMPHONYImprovingMemory2024]

### Ablations

| Experiment | Setting | Result |
|---|---|---|
| Prefill-heavy workload | all requests replaced by a 1024-token prompt and a 1-token response, original arrival times | InferCept does not reach high throughput because of load imbalance (Figure 16; no number stated in the text) |
| Missed advisory requests | 256 concurrent users, 10% miss rate | latency to produce one token rises from 21.3ms to 24.4ms |
| Prioritization policy | 10%, 30%, 50% high-priority requests, vs vLLM's priority scheduling | better for both prioritized and regular jobs (Figure 18; no number stated in the text) |

All rows: [^agarwalSYMPHONYImprovingMemory2024]

### Inconsistencies inside the paper

- Users served relative to vLLM: the abstract and Section 4.2 say $8\times$ (64 users at 18ms vs 512 users at 20.5ms), while the introduction and the Figure 12 caption say $4\times$ (64 for vLLM and 256 for Symphony, 18.5ms vs 20.5ms).[^agarwalSYMPHONYImprovingMemory2024]
- Latency vs vLLM: the introduction says $2.4\times$ reduction on average, while Section 4.2 gives $1.4\times$ to $1.9\times$ (LLaMa-3.1 8B) and $1.31\times$ to $1.9\times$ (LLaMa-2-13B).[^agarwalSYMPHONYImprovingMemory2024]
- Missing advisory requests at a 10% miss rate: the text gives 21.3ms to 24.4ms and calls it "approximately 6%", Section 3.5 says "only 6% loss in latency", and the Figure 17 caption says a degradation of 3.1 ms.[^agarwalSYMPHONYImprovingMemory2024]
- InferCept load imbalance is given as $3.1\times$ the median load in Sections 1 and 4.3 and as $2.8\times$ in Section 4.2.[^agarwalSYMPHONYImprovingMemory2024]
- Model names vary: "LLaMa-3.1 8B", "LLaMa-3.2 8B", "LLaMa-3 8B", and "LLaMa-7B" all appear.[^agarwalSYMPHONYImprovingMemory2024]

## Limitations

- Symphony assumes advisory requests arrive early enough to leave time for K,V cache migration. When the advisory request is late or missing, performance can be affected.[^agarwalSYMPHONYImprovingMemory2024]
- For chatbots and code editors, advisory requests give only the likely arrival of a request, not the prompt length, the number of generated tokens, or the order across sessions.[^agarwalSYMPHONYImprovingMemory2024]
- Chatbot request arrival times are generated from reading and typing speeds taken from prior studies, not measured from users.[^agarwalSYMPHONYImprovingMemory2024]
- The only cluster policy evaluated besides prioritization is even load balancing.[^agarwalSYMPHONYImprovingMemory2024]
- Several headline numbers disagree between sections (see above), and the prefill-heavy and prioritization results are given only as figures.[^agarwalSYMPHONYImprovingMemory2024]
- Symphony does not change the model or the data. The paper states it can be combined with K,V cache compression methods but does not evaluate this.[^agarwalSYMPHONYImprovingMemory2024]

## Related

- Proposed: [Symphony](../methods/symphony.md), [Advisory requests](../methods/advisory-requests.md)
- Builds on: [KV cache](../methods/kv-cache.md), [KV cache swapping](../methods/kv-cache-swapping.md), [Continuous batching](../methods/continuous-batching.md), [vLLM](../methods/vllm.md)
- Compared against: [vLLM](../methods/vllm.md), [InferCept](../methods/infercept.md)
- Workloads and datasets: [ShareGPT](../datasets/sharegpt.md), [MetaGPT](../methods/metagpt.md)
- Papers in this wiki cited by this paper: [InferCept](abhyankarInferCeptEfficientIntercept2024.md), [SGLang](zhengSGLangEfficientExecution2024.md)

[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
