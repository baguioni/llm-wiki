---
type: Method
title: KV cache
description: The per-token key and value tensors that an LLM keeps from earlier tokens so that later tokens do not recompute them, and the object that most serving papers in the wiki manage, share, move, or shrink.
tags: [kv-cache, llm-serving, inference, memory-management]
sources:
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: maLeylineKVCache2026
    resource: zotero://select/items/@maLeylineKVCache2026
    title: "Leyline: KV Cache Directives for Agentic Inference"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: wuDualPathBreakingStorage2026
    resource: zotero://select/items/@wuDualPathBreakingStorage2026
    title: "DualPath: Breaking the Storage Bandwidth Bottleneck in Agentic LLM Inference"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
  - id: wangEfficientOnDeviceDiffusion2026
    resource: zotero://select/items/@wangEfficientOnDeviceDiffusion2026
    title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
---

# KV cache

## Overview

During inference, each token generates intermediate tensors that are used for decoding further tokens. These tensors are called the KV cache, named for the key-value pairs in the self-attention mechanism.[^zhengSGLangEfficientExecution2024] Self-attention needs the current query vector and all keys and values of prior tokens, so inference-serving systems store them to avoid recomputation.[^agarwalSYMPHONYImprovingMemory2024]

## How it works

- **Prefill and decode.** The model first processes the input tokens in one forward pass (prefill), then decodes output tokens one at a time, each depending on prior tokens.[^zhengSGLangEfficientExecution2024] Prefill generates the KV cache and is compute-bound; decode fetches the entire KV cache for each generated token and is memory-bound.[^caiYourNPUReady2026]
- **Prefix property.** The KV cache of a token depends only on the tokens before it, so different sequences with the same prefix can reuse the KV cache of the prefix tokens.[^zhengSGLangEfficientExecution2024] This is the basis of [prefix caching](prefix-caching.md) and [RadixAttention](radix-attention.md).
- **Position dependence.** Under Multi-head Latent Attention, the cached K splits into a part with no position and a part rotated by RoPE according to absolute position, so content that moves to a new position needs a correction to the rotated part.[^maLeylineKVCache2026]

### Size

| Model and context | KV cache size | Paper |
|---|---|---|
| LLama-3.1-70B, 32K context | approximately 10GB | Symphony[^agarwalSYMPHONYImprovingMemory2024] |
| LLaMa-70B, full 128K context | 40 GB maximum | Symphony[^agarwalSYMPHONYImprovingMemory2024] |
| LLaMa-3.1 8B, per token | approximately 1.1 MB | Symphony[^agarwalSYMPHONYImprovingMemory2024] |
| Llama-3-70B with GQA, 32K context, FP16, per session | ∼10.7GB | SAGA[^guoSAGAWorkflowAtomicScheduling2026] |
| DeepSeek-V2-Lite MLA pool, per token | 31,104 bytes | Leyline[^maLeylineKVCache2026] |
| Sheared-LLaMa-1.3B draft model, context 256 / 512 / 1024 | 48MB / 96MB / 192MB | Yan et al.[^yanDecodingSpeculativeDecoding2025] |
| Wide 1.3B draft model, context 256 / 512 / 1024 | 30MB / 60MB / 120MB | Yan et al.[^yanDecodingSpeculativeDecoding2025] |
| DS 660B online serving working set under DualPath | 69 GB at APS 0.1 to 681 GB at APS 0.45 | DualPath[^wuDualPathBreakingStorage2026] |

### What to do with the cache of a paused request

InferCept names three options when a request pauses for an external call, and measures their cost on a mixed workload:[^abhyankarInferCeptEfficientIntercept2024]

| Strategy | Action | Measured cost |
|---|---|---|
| Discard | Drop the context and recompute on resume | 37-40% of total model forwarding time spent on recomputation |
| Preserve | Keep the context in GPU memory | Nearly half of the GPU memory is occupied by interrupted requests more than 60% of the time |
| Swap | Move the context to CPU memory and back | Over 25% of total workload time spent waiting for swapping |

See [KV cache swapping](kv-cache-swapping.md) and [KV cache offloading](kv-cache-offloading.md).

## Papers using it

| Paper | What it does with the KV cache | Key numbers |
|---|---|---|
| SGLang[^zhengSGLangEfficientExecution2024] | **Reuse.** Keeps the KV cache of all requests as an LRU cache in a radix tree ([RadixAttention](radix-attention.md)) and schedules requests to raise the cache hit rate | Up to 6.4× higher throughput on LM-program benchmarks; 74.1% cache hit rate for Vicuna-33B in a one-month Chatbot Arena deployment |
| Parrot[^linParrotEfficientServing2024] | **Share.** Detects common prompt prefixes across requests, shares the prefix's KV cache with paged memory management, and adds an attention kernel that loads the shared KV cache tiles only once | 1.8×∼2.4× over a baseline without prompt sharing at batch sizes 8 and 16; larger batches of that baseline run out of memory because of the KV cache of the shared system prompt (about 6000 tokens) |
| InferCept[^abhyankarInferCeptEfficientIntercept2024] | **Preserve, discard, or swap.** Chooses per intercepted request the option that minimizes GPU memory waste | 1.6×-2× higher serving load than vLLM at similar latency per token |
| Symphony[^agarwalSYMPHONYImprovingMemory2024] | **Migrate and prefetch.** Uses advisory requests to move a session's K,V cache across nodes and memory tiers before the request arrives, with layer-wise asynchronous loading and a disk copy of every cache | Reports that recomputation makes more than 99% of processed tokens redundant in a multi-turn chatbot dataset; up to 8× the users of vLLM at similar time per output token |
| Autellix[^luoAutellixEfficientServing] | **Route for locality, swap faster.** Routes long calls to the engine that holds their program's KV cache and load-balances short calls. Replaces vLLM's per-block KV transfer with one bulk transfer | Within one program the prefix cache-hit rate stays above 90%; requests below 2048 tokens reach ≥75% on any engine; the swap kernel reduces swaps by up to 18x and swap times by 3-7x |
| ThunderAgent[^kangThunderAgentSimpleFast2026] | **Protect from thrashing.** Pauses whole programs and releases their KV cache when a backend's KV cache pool is over capacity, instead of letting requests evict each other. A paused program's cache is assumed evicted, so it can resume on any replica | KV cache thrashing raises the end-to-end latency of each request by up to 7.14× in the profiled baseline; 1.48–3.58× throughput over vLLM at high concurrency |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | **Retain by predicted reuse.** WA-LRU eviction scores each session by idle time, predicted reuse, and size; a per-tool TTL keeps caches during tool calls; the successor's prefix cache is prefetched; preempted tasks have their cache migrated | Share of SWE-bench time spent regenerating KV cache: 38% (vLLM v0.6.0), 22% (vLLM+APC), 8% (SAGA). WA-LRU is within 1.31× of Bélády's offline-optimal policy on SWE-bench |
| MORI[^xiaIdlenessRelativeExploiting2026] | **Place across tiers.** Ranks programs by idleness and keeps their KV cache in GPU HBM (busy), CPU DRAM (idle), or discards it (waiting), with admission control at both tiers and type labels that steer the engine's eviction | 20–71% higher output throughput than uncoordinated offloading and 1.6–2.1× higher than non-offloading systems at 80 concurrent programs |
| DualPath[^wuDualPathBreakingStorage2026] | **Load from storage.** Loads the KV-Cache from external storage through decode engines as well as prefill engines, so the storage NIC bandwidth of all engines is used | Agent traces have a KV-Cache hit rate of 98.7%; the cache-compute ratio is approximately 22 GB/PFLOP for DeepSeek-V3.2; offline throughput up to 1.87× and online throughput 1.96× on average |
| Leyline[^maLeylineKVCache2026] | **Edit in place.** Lets a policy remove or replace a span of cached content. The replacement is prefilled fresh, and downstream slots keep their cache with only the position-dependent part of K rotated | Replay cache hit 49.6% → 60.8% against vanilla SGLang; replay p50 end-to-end −241 ms (−4.4%) at concurrency 8 |
| KAIROS[^yuanKAIROSStatefulContextAware2026] | **Treat as the constraint on power saving.** Lowering GPU frequency too far lets accumulated context exceed GPU memory, so cached context is evicted and recomputed or loaded from slower tiers (the thrashing regime). The paper calls the cache the context cache | In the thrashing regime, recomputation and LMCache-based offloading reduce average agent completion throughput by 44.2% and 42.1% |
| Yan et al.[^yanDecodingSpeculativeDecoding2025] | **Shrink.** A shallower, wider draft model needs a smaller KV cache, which allows larger batch sizes | More than 37% smaller KV cache than Sheared-LLaMa-1.3B at the same 1.3B size |
| Cai et al.[^caiYourNPUReady2026] | **Measure.** Explains the prefill/decode split on mobile hardware through the KV cache: decode repeatedly reads the growing KV cache and is memory-bound, so NPU peak compute is underused in decode | The paper lists KV-cache reuse and state migration as the challenge for switching between NPU graphs compiled for different context windows |
| llada.cpp[^wangEfficientOnDeviceDiffusion2026] | **Reuse in a diffusion LLM.** Block-wise decoding reuses the prefix KV cache of completed blocks. Tokens in the current block can still change, so a CPU-side path refreshes selected KV entries and merges them into the prefix KV cache only at step boundaries | Prefix KV cache reuse: 2996.2 s → 607.0 s on CPU (4.94×) and 341.2 s → 87.0 s on NPU (3.92×) for 128-token generation |

## Strengths & Limitations

- Keeping the cache across calls is not free: it needs additional storage and more complex memory management.[^zhengSGLangEfficientExecution2024]
- The cache makes multi-turn serving stateful. Offloading it makes the workload sticky, since all requests of a session must go to the node that holds the cache, which causes load imbalance.[^agarwalSYMPHONYImprovingMemory2024]
- With `k` agent steps that each add `c` tokens of KV cache, complete eviction after each tool call costs O(k²·c) regenerated tokens.[^guoSAGAWorkflowAtomicScheduling2026]
- Moving the cache between GPU and host memory is limited by PCIe: a 10.7 GB cache takes ≈430 ms one-way at 25 GB/s.[^guoSAGAWorkflowAtomicScheduling2026]
- Prefix reuse assumes the cache grows append-only. Agent policies that edit earlier context break this assumption.[^maLeylineKVCache2026]
- In a diffusion LLM, cached KV states go stale when token identities change across denoising steps.[^wangEfficientOnDeviceDiffusion2026]

## Related

- Reuse: [Prefix caching](prefix-caching.md), [RadixAttention](radix-attention.md)
- Memory layout: [PagedAttention](paged-attention.md)
- Movement between tiers: [KV cache swapping](kv-cache-swapping.md), [KV cache offloading](kv-cache-offloading.md), [LMCache](lmcache.md)
- Scheduling around it: [Program-aware scheduling](program-aware-scheduling.md), [ThunderAgent](thunderagent.md), [Continuous batching](continuous-batching.md), [Chunked prefill](chunked-prefill.md)
- Engines: [vLLM](vllm.md), [SGLang](sglang.md)
- Papers: [SGLang](../papers/zhengSGLangEfficientExecution2024.md), [Parrot](../papers/linParrotEfficientServing2024.md), [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md), [Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md), [Autellix](../papers/luoAutellixEfficientServing.md), [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [MORI](../papers/xiaIdlenessRelativeExploiting2026.md), [DualPath](../papers/wuDualPathBreakingStorage2026.md), [Leyline](../papers/maLeylineKVCache2026.md), [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md), [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md), [Is Your NPU Ready for LLMs?](../papers/caiYourNPUReady2026.md), [llada.cpp](../papers/wangEfficientOnDeviceDiffusion2026.md)

## Open questions and results

- [Recomputation share of forwarding time](../results/recomputation-share-of-forwarding-time.md)
- [Does offloading the KV cache to CPU memory help agentic workloads?](../questions/kv-cache-offloading-for-agent-workloads.md)

[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^linParrotEfficientServing2024]: Lin et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^maLeylineKVCache2026]: Ma et al. 2026
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^wuDualPathBreakingStorage2026]: Wu et al. 2026
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^caiYourNPUReady2026]: Cai et al. 2026
[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
