---
type: Method
title: PagedAttention
description: Memory management technique from vLLM that stores the KV cache in non-contiguous blocks tracked by a per-request page table, as the wiki's papers describe and reuse it.
tags: [kv-cache, memory-management, llm-serving, vllm]
sources:
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
---

# PagedAttention

## Overview

PagedAttention (also written "paged attention") is the memory management technique that the wiki's papers attribute to [vLLM](vllm.md). None of the wiki's papers is the PagedAttention paper itself, so this page records how other papers describe and use it.

- InferCept: the [KV cache](kv-cache.md) is treated as virtual memory that can map to non-contiguous physical GPU memory, which gives better utilization of GPU memory.[^abhyankarInferCeptEfficientIntercept2024]
- Parrot: the KV cache is stored in disparate memory segments, and a page table per request tracks block status and placement.[^linParrotEfficientServing2024]
- MORI: it reduces fragmentation by managing the cache in non-contiguous blocks.[^xiaIdlenessRelativeExploiting2026]
- Autellix: vLLM integrates PagedAttention to reduce KV cache fragmentation.[^luoAutellixEfficientServing]

## Variants

- **One-token pages in SGLang.** SGLang stores KV cache tensors in a non-contiguous, paged layout where each page is one token, and states that RadixAttention is compatible with paged attention.[^zhengSGLangEfficientExecution2024]
- **Parrot's shared-prefix kernel.** Parrot combines PagedAttention with FlashAttention in a new attention kernel. It keeps the per-request page table, and loads the KV cache tiles of a shared prefix to shared memory only once.[^linParrotEfficientServing2024]
- **Two page tables for speculative decoding.** In the SSD engine the target host keeps page-table bookkeeping for both the target and the draft model. After verification both page tables are reconciled: completed pages are finalized, and pages allocated beyond the accepted suffix are deallocated.[^kumarSpeculativeSpeculativeDecoding2026]

## Papers using it

| Paper | How it uses PagedAttention | Numbers |
|---|---|---|
| InferCept[^abhyankarInferCeptEfficientIntercept2024] | Builds on vLLM to reuse PagedAttention for regular memory management, and adds the choice to preserve, discard, or swap the KV cache of intercepted requests | none specific to PagedAttention |
| Parrot[^linParrotEfficientServing2024] | Uses vLLM's paged memory management to share the KV cache of a prompt prefix, and compares its own kernel against vLLM's PagedAttention kernel | 1.1×∼1.7× over vLLM with paged attention sharing a static prefix (Bing Copilot, A100, LLaMA 7B); 1.58× and 1.84× in latency per output token; 2.4× higher request rate than Parrot with vLLM's PagedAttention (four A6000, LLaMA 7B); a further 1.2× with 16 files in the MetaGPT workload |
| Autellix[^luoAutellixEfficientServing] | Inherits it from vLLM v0.6.1. Replaces vLLM's swap of individual KV blocks with one bulk transfer of all blocks | Swaps reduced by up to 18x and swap times by 3-7x |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | Its KV Cache Manager extends vLLM's PagedAttention with WA-LRU eviction, TTL tracking, and speculative prefetching. The vLLM v0.6.0 baseline is described as PagedAttention with FCFS scheduling | SAGA is 3.01× faster than vLLM v0.6.0 in SWE-bench task completion time |
| SSD / Saguaro[^kumarSpeculativeSpeculativeDecoding2026] | The custom inference engine incorporates PagedAttention together with continuous batching and tensor parallelism | none specific to PagedAttention |
| MORI[^xiaIdlenessRelativeExploiting2026] | Cited as background on GPU memory optimization for serving | none |
| SGLang[^zhengSGLangEfficientExecution2024] | Stores the radix tree's KV cache tensors in a paged layout | none specific to PagedAttention |

## Strengths & Limitations

- Because both systems use paged memory management, Parrot and vLLM can hold the same number of tokens in an engine. Parrot states that vLLM's kernel still reloads the shared-prefix tokens repeatedly, and that this redundant memory loading slows inference because token generation is bound by memory bandwidth.[^linParrotEfficientServing2024]
- vLLM's static prefix sharing through paged attention does not work when the shared content is generated dynamically.[^linParrotEfficientServing2024]
- vLLM is agnostic to interceptions, so paged memory management alone does not decide what happens to the KV cache of a paused request.[^abhyankarInferCeptEfficientIntercept2024]
- Each KV block is transferred individually in vLLM's swap path, which creates small fragmented transfers that underutilize PCIe bandwidth.[^luoAutellixEfficientServing]
- With speculative decoding, allocations for rejected tokens that wrote into pre-allocated pages must be undone after each verification.[^kumarSpeculativeSpeculativeDecoding2026]

## Related

- [vLLM](vllm.md), [KV cache](kv-cache.md), [RadixAttention](radix-attention.md), [Prefix caching](prefix-caching.md), [Continuous batching](continuous-batching.md), [KV cache swapping](kv-cache-swapping.md)
- Papers: [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md), [Parrot](../papers/linParrotEfficientServing2024.md), [Autellix](../papers/luoAutellixEfficientServing.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [SSD](../papers/kumarSpeculativeSpeculativeDecoding2026.md), [MORI](../papers/xiaIdlenessRelativeExploiting2026.md), [SGLang](../papers/zhengSGLangEfficientExecution2024.md)

[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^linParrotEfficientServing2024]: Lin et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
