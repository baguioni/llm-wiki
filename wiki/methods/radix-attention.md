---
type: Method
title: RadixAttention
description: SGLang's technique for automatic KV cache reuse, which keeps the cache of all requests as an LRU cache in a radix tree and schedules requests by matched prefix length.
tags: [kv-cache, prefix-caching, llm-serving, scheduling, sglang]
sources:
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: maLeylineKVCache2026
    resource: zotero://select/items/@maLeylineKVCache2026
    title: "Leyline: KV Cache Directives for Agentic Inference"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
---

# RadixAttention

## Overview

RadixAttention is the technique that [SGLang](sglang.md) introduces for automatic [KV cache](kv-cache.md) reuse at runtime.[^zhengSGLangEfficientExecution2024] Existing systems discard the KV cache after a generation request finishes. SGLang instead retains the cache for prompts and generation results in a radix tree, which supports prefix search, reuse, insertion, and eviction.[^zhengSGLangEfficientExecution2024] The paper states that it is the first solution that supports multi-level sharing, cache-aware scheduling, frontend-runtime co-scheduling, and distributed cases.[^zhengSGLangEfficientExecution2024]

## How it works

All items in this section are from the SGLang paper.[^zhengSGLangEfficientExecution2024]

- **Data structure.** A radix tree maps sequences of tokens to their KV cache tensors. The tensors are stored in a non-contiguous, paged layout where each page is one token. The tree structure is stored on the CPU.
- **Eviction.** An LRU policy evicts the least recently used leaf first, so common ancestors stay reusable until they become leaves. Each node has a reference counter of running requests that use it, and a node is evictable when the counter is zero.
- **Memory.** No fixed-size cache pool is preallocated. Cached tokens and running requests share one memory pool, and when enough waiting requests run, the system evicts all cached tokens in favor of a larger batch size.
- **Cache-aware scheduling.** Waiting requests are sorted by matched prefix length, and requests with longer matched prefixes run first (longest-shared-prefix-first), instead of first-come, first-served.
- **Theorem 3.1.** For a batch of requests, an optimal cache hit rate is achieved by visiting the radix tree of the requests in depth-first search order, with a cache size ≥ the maximum request length. Longest-shared-prefix-first order is equivalent to a depth-first search order.
- **Frontend hint.** On `fork`, the SGLang frontend sends the prefix first so that it is inserted into the tree, then sends the remaining prompts.
- **Multi-modal inputs.** The hash of an input image is the key in the radix tree, so the KV cache of image tokens from the same image is reused.
- **Compatibility.** RadixAttention is compatible with [continuous batching](continuous-batching.md), [paged attention](paged-attention.md), and tensor parallelism.

Cache hit rate is defined as the number of cached prompt tokens divided by the number of prompt tokens.[^zhengSGLangEfficientExecution2024]

## Variants

- **Tensor parallelism.** Each GPU keeps a sharded KV cache, and no extra synchronization is needed.[^zhengSGLangEfficientExecution2024]
- **Data parallelism.** Each worker keeps its own sub-tree and a router keeps a meta-tree, dispatching by the length of the shared prefix. Evictions at a worker are committed to a queue that the router processes during periods of low activity.[^zhengSGLangEfficientExecution2024]
- **Typed nodes (MORI).** MORI's scheduler propagates a type label (busy, idle, inactive) to each program's KV cache tree nodes. When the engine inserts KV blocks into the radix tree it stamps them with the program's type, and eviction uses the label as a higher-priority sort key before LRU.[^xiaIdlenessRelativeExploiting2026]
- **Spliced ranges (Leyline).** A ∼200-LOC SGLang RadixCache patch adds a content-hash side index. Leyline inserts a spliced range into the radix trie and re-runs the unwrapped `match_prefix`, so spliced KV is discoverable by later requests without a hook at lookup time.[^maLeylineKVCache2026]

## Papers using it

| Paper | How it uses RadixAttention | Numbers |
|---|---|---|
| SGLang[^zhengSGLangEfficientExecution2024] | Proposes it | Cache hit rate after one month in Chatbot Arena: 52.4% for LLaVA-Next-34B and 74.1% for Vicuna-33B, with first-token latency reduced by an average of 1.7× for Vicuna-33B |
| SGLang[^zhengSGLangEfficientExecution2024] | Overhead test on [ShareGPT](../datasets/sharegpt.md), a benchmark with no KV cache reuse opportunities | 100 requests take 74.3 seconds, of which managing the RadixAttention data structures takes 0.2 seconds, an overhead of less than 0.3% |
| SGLang[^zhengSGLangEfficientExecution2024] | Data-parallel RadixAttention with four workers on MMLU | Linear scaling and an optimal cache hit rate |
| MORI[^xiaIdlenessRelativeExploiting2026] | Extends the radix tree's nodes with program type labels for two-tier eviction. Cites RadixAttention as reusing cached prefixes across requests via a radix tree | 20–71% higher output throughput than ThunderAgent with uncoordinated offloading at 80 concurrent programs |
| Leyline[^maLeylineKVCache2026] | Patches SGLang's RadixCache so that edited prompts keep their cache. Vanilla RadixCache is the baseline arm, and `--disable-radix-cache` is the lower-bound arm | Replay cache hit 0.0% (cache-off), 49.6% (radix), 60.8% (splice). Replay p50 end-to-end at concurrency 8: 7120 ms, 5533 ms, 5292 ms |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | Baseline: SGLang v0.5.8 with RadixAttention, zero-overhead batch scheduler, and cache-aware load balancing | SAGA is 1.90× faster on SWE-bench and 1.69× on WebArena in task completion time |
| SSD / Saguaro[^kumarSpeculativeSpeculativeDecoding2026] | Disables radix caching in its vLLM and SGLang baselines | none |

## Strengths & Limitations

- The paper's ablation tests No Cache, No Tree-Structure, FCFS Schedule, Random Schedule, No Frontend Parallelism, and No Frontend Hint variants and reports that each component is required for the best performance. The numbers are given only in a figure.[^zhengSGLangEfficientExecution2024]
- Greedy cache-aware scheduling can lead to starvation.[^zhengSGLangEfficientExecution2024]
- In practice the unpredictable number of output tokens can cause recomputation of the KV cache, so the computation differs from the one in the proof of Theorem 3.1.[^zhengSGLangEfficientExecution2024]
- In the data-parallel setting there is a trade-off between data locality and parallel processing efficiency.[^zhengSGLangEfficientExecution2024]
- The paper lists RadixAttention across multiple levels of the memory hierarchy (e.g., DRAM, Disk) and fuzzy semantic matching as future directions.[^zhengSGLangEfficientExecution2024]
- SAGA states that the KV cache in existing serving systems is evicted with LRU policies that are unaware of agent workflow structure.[^guoSAGAWorkflowAtomicScheduling2026]
- Leyline states that an exact-prefix cache is invalidated when identical content moves to a new position between turns, and that when RadixCache already covers the workload there is no headroom for its splice.[^maLeylineKVCache2026]

## Related

- [SGLang](sglang.md), [KV cache](kv-cache.md), [Prefix caching](prefix-caching.md), [PagedAttention](paged-attention.md), [Continuous batching](continuous-batching.md), [KV cache offloading](kv-cache-offloading.md), [Program-aware scheduling](program-aware-scheduling.md)
- Papers: [SGLang](../papers/zhengSGLangEfficientExecution2024.md), [MORI](../papers/xiaIdlenessRelativeExploiting2026.md), [Leyline](../papers/maLeylineKVCache2026.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [SSD](../papers/kumarSpeculativeSpeculativeDecoding2026.md)

[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^maLeylineKVCache2026]: Ma et al. 2026
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
