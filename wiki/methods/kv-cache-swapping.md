---
type: Method
title: KV cache swapping
description: Moving a paused request's KV cache from GPU memory to CPU memory and back, so that the context is neither recomputed nor left idle on the GPU.
tags: [llm-serving, kv-cache, memory-management, scheduling, agentic-inference]
sources:
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
---

# KV cache swapping

## Overview

Swap is one of three ways to handle a request whose decoding is paused by a tool call, another model, or a human. The system swaps the request's context from GPU to CPU memory when the interception happens and swaps it back when the interception ends.[^abhyankarInferCeptEfficientIntercept2024] The other two are Discard (drop the context and recompute it on resume) and Preserve (keep the context in GPU memory during the interception).[^abhyankarInferCeptEfficientIntercept2024] Swap avoids the recomputation of Discard and the idle GPU memory of Preserve, but the GPU-CPU link bandwidth is limited, so foreground model forwarding can be bottlenecked by waiting for swapping to finish.[^abhyankarInferCeptEfficientIntercept2024]

Symphony uses the same term for multi-turn sessions: systems swap K,V caches between GPU memory and host memory and migrate them back to the GPU when the next request of the session arrives.[^agarwalSYMPHONYImprovingMemory2024] Autellix uses it for preemptive scheduling, where [KV cache](../methods/kv-cache.md) blocks are repeatedly swapped between GPU and CPU to serve different requests.[^luoAutellixEfficientServing]

The same GPU-to-host movement is called [KV cache offloading](../methods/kv-cache-offloading.md) in later papers.

## How it works

- **Straightforward implementation.** Swapping runs synchronously: CUDA kernels are launched to move data out and in. One kernel is needed per discontinuous physical memory region, and with [PagedAttention](../methods/paged-attention.md) the context of an intercepted request can scatter across many regions, which causes high kernel launch overhead.[^abhyankarInferCeptEfficientIntercept2024]
- **Waste model.** With $C_i^j$ the context tokens of request $i$ at interception $j$, $M$ the per-token KV memory, and $T_{swap}$ the mapping from swapped tokens to swap latency, the GPU memory waste of Swap is $\text{WasteSwap}_{i}^{j}=2\times T_{swap}(C_{i}^{j})\times C_{batch}\times M$ (Eq. 3). The waste has two sources (the memory being swapped, and all running requests waiting for the swap), and the factor of 2 accounts for swapping in and out.[^abhyankarInferCeptEfficientIntercept2024]
- **In vLLM.** Each KV block is transferred individually via cudaMemcpyAsync, which creates small fragmented transfers that underutilize PCIe bandwidth and incur overhead such as repeated DMA setups.[^luoAutellixEfficientServing]

## Variants

| Variant | Paper | What it changes |
|---|---|---|
| Swap pipelining | InferCept | Each model layer's swapping is one pipeline stage. Kernel launching, data movement, and foreground model forwarding are pipelined and run in the background. |
| Swap chunking with a swap budget | InferCept | Swap-out and swap-in are split across iterations. At iteration $i$ with batch size $B_i$, the swap limit $N_i$ is set from $T_{swap}(N_i)=T_{fwd}(B_i)$, the number of tokens that can be swapped for free behind model forwarding. Swap-in plus swap-out tokens must be at most $N_i$. |
| Bulk-transfer swap kernel | Autellix | A host buffer is allocated and all KV blocks are consolidated into a single contiguous chunk for one bulk transfer. |
| Multi-step scheduling | Autellix | The scheduler runs once every $N$ decoding steps, which reduces the total number of swaps. |

Rows 1 and 2: [^abhyankarInferCeptEfficientIntercept2024]. Rows 3 and 4: [^luoAutellixEfficientServing]

## Papers using it

- **[InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md)** studies Swap as a baseline and as one of the three actions of its min-waste scheduler. On its mixed workload, plain Swap wastes 26% GPU resources, and over 25% of the total workload time is spent waiting for swapping. Intercepted requests are sorted by potential memory waste and swapped out in that order until the swap-out budget runs out. Resumed requests in the swap queue are swapped in FCFS order until the swap-in budget is reached. On the GPT-J 6B model, InferCept eliminates 96% of GPU waste for swapping compared to the Swap baseline, and adding budgeted swapping gives an added improvement of 12.7% in normalized latency in the technique breakdown.[^abhyankarInferCeptEfficientIntercept2024]
- **[Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md)** measures Swap against Recompute. Serving 1000 [ShareGPT](../datasets/sharegpt.md) samples on one A100 with LLaMa-7B, Swap reduces total pre-fill time by a factor of 4.9 and decode time by a factor of 1.68. On 8 A100 GPUs with session-sticky routing and InferCept as the swapping baseline, the swapping baseline takes 1.7 times longer than the Recompute baseline. Symphony reports up to $2.5\times$ speedup over InferCept and over $4.2\times$ the requests handled at high load (1024 users).[^agarwalSYMPHONYImprovingMemory2024]
- **[Autellix](../papers/luoAutellixEfficientServing.md)** modifies vLLM's memory swapping kernels. Its kernel reduces swaps by up to 18x and swap times by 3-7x, and achieves 1.3x higher throughput than vLLM's implemented kernel. In its offline batch ablation, MLFQ at 4000 programs fails with Out-Of-Memory errors despite a swap space >1.2TB, because of memory contention and frequent GPU-CPU swapping.[^luoAutellixEfficientServing]
- **[SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md)** discusses CPU swap as an alternative architecture and chooses HBM retention with predictive eviction instead. It treats the two as complementary.[^guoSAGAWorkflowAtomicScheduling2026]
- **[ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md)** states that in high-frequency agentic workflows the overhead of frequent swap-in and swap-out cycles often negates the benefits of multi-tier caching.[^kangThunderAgentSimpleFast2026]

## Strengths & Limitations

Strengths:

- Avoids recomputation and GPU memory wastage during an interception.[^abhyankarInferCeptEfficientIntercept2024]
- On a single GPU it shortens both pre-fill and decode time compared to recomputation (factors of 4.9 and 1.68). The decode gain comes from [continuous batching](../methods/continuous-batching.md): faster pre-fill lets more requests be processed at the same time.[^agarwalSYMPHONYImprovingMemory2024]
- As model size increases, Swap performs better than vanilla vLLM and ImprovedDiscard. The paper attributes this to grouped query attention, which compresses the attention KVs and moderates data movement for Swap.[^abhyankarInferCeptEfficientIntercept2024]

Limitations:

- Unpipelined swapping blocks foreground computation for the entire swapping time.[^abhyankarInferCeptEfficientIntercept2024]
- It makes the workload stateful: future requests of a session must be handled by the machine that holds the cache. This leads to load imbalance, where one node can serve $3.1\times$ the median load.[^agarwalSYMPHONYImprovingMemory2024]
- It only allows offloading to host memory, because moving caches to disk or remote storage incurs significant overhead when serving requests. Host memory is finite: with LLaMa-3.1 8B at approximately 1.1 MB of K,V cache per token, 256 GB of main memory holds about 238K tokens, a maximum of 108 concurrent ShareGPT sessions.[^agarwalSYMPHONYImprovingMemory2024]
- PCIe round trips can exceed the tool call. A 10.7 GB cache (Llama-3-70B, 32K context, GQA $n_{kv}=8$) takes $\approx$430 ms one-way over PCIe Gen4 $\times$16 at 25 GB/s, so a swap-out plus swap-in round trip is $\approx$860 ms uncontested. Three of four tool classes in that paper (file ops P50=45 ms, code execution P50=180 ms, database queries P50=120 ms) complete faster than this. Under multi-tenant PCIe contention the round trip doubles to $\approx$1.7 s.[^guoSAGAWorkflowAtomicScheduling2026]
- Preemptive scheduling increases the number of active LLM calls, which leads to frequent GPU-CPU swaps and significant swapping overheads at high request rates.[^luoAutellixEfficientServing]

# Contradictions

**Does swapping beat recomputation?** The papers reach different conclusions under different settings. Both claims are kept.

| Claim | Setting | Source |
|---|---|---|
| Swap reduces pre-fill time by a factor of 4.9 and decode time by a factor of 1.68 vs Recompute | 1000 ShareGPT samples, one A100, LLaMa-7B | [^agarwalSYMPHONYImprovingMemory2024] |
| The swapping baseline (InferCept) takes 1.7 times longer than Recompute | 8 A100 GPUs, each serving LLaMa-3.2 8B, requests of a session routed to the same GPU | [^agarwalSYMPHONYImprovingMemory2024] |
| The overall results for Swap are similar to ImprovedDiscard | GPT-J 6B, one A100, mixed augmentation workload | [^abhyankarInferCeptEfficientIntercept2024] |
| Swap is pure overhead for the modal request | Llama-3-70B, 32K context, tool calls with P50 of 45 to 180 ms; analytical PCIe estimate, not a measured run | [^guoSAGAWorkflowAtomicScheduling2026] |

The single-GPU results isolate compute savings. The 8-GPU result adds session-sticky routing, and Symphony attributes the slowdown to load imbalance, not to transfer cost.[^agarwalSYMPHONYImprovingMemory2024] SAGA's argument depends on tool calls shorter than the PCIe round trip and states that swap remains complementary for over-subscribed regimes ($>$95% utilization), which are outside its evaluation.[^guoSAGAWorkflowAtomicScheduling2026]

**How InferCept is classified.** Symphony describes InferCept as "a system that offloads K,V caches to the main memory of the host" and uses it as its swapping baseline.[^agarwalSYMPHONYImprovingMemory2024] MORI lists InferCept among systems that temporarily pin KV cache in GPU memory during short tool-call intervals.[^xiaIdlenessRelativeExploiting2026] InferCept itself adaptively combines preserve, its optimized discard, and its optimized swap per request.[^abhyankarInferCeptEfficientIntercept2024] Each later paper names one of the three actions.

**InferCept load imbalance as reported by Symphony.** Symphony gives the maximum load on one InferCept node as $3.1\times$ the median load in its introduction and Section 4.3, and as $2.8\times$ in Section 4.2.[^agarwalSYMPHONYImprovingMemory2024] Symphony states that InferCept does not perform request-level routing, so its authors built the top-level session-sticky scheduler used in these measurements themselves.[^agarwalSYMPHONYImprovingMemory2024]

## Related

- [KV cache](../methods/kv-cache.md), [KV cache offloading](../methods/kv-cache-offloading.md), [PagedAttention](../methods/paged-attention.md), [Chunked prefill](../methods/chunked-prefill.md), [Continuous batching](../methods/continuous-batching.md)
- Systems: [vLLM](../methods/vllm.md), [ThunderAgent](../methods/thunderagent.md), [LMCache](../methods/lmcache.md)
- Scheduling: [Program-aware scheduling](../methods/program-aware-scheduling.md)

## Open questions and results

- [Does offloading the KV cache to CPU memory help agentic workloads?](../questions/kv-cache-offloading-for-agent-workloads.md)
- [Recomputation share of forwarding time](../results/recomputation-share-of-forwarding-time.md)

[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
