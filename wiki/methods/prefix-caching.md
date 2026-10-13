---
type: Method
title: Prefix caching
description: Reuse of the KV cache of a shared prompt prefix across LLM requests, so that the prefill of the prefix is not recomputed.
tags: [kv-cache, prefix-caching, llm-serving, agentic-inference]
sources:
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: maLeylineKVCache2026
    resource: zotero://select/items/@maLeylineKVCache2026
    title: "Leyline: KV Cache Directives for Agentic Inference"
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# Prefix caching

## Overview

Prefix caching stores and reuses relevant key-value (KV) cache entries, such as those of the system prompt, across LLM requests, which removes significant portions of prefill computation.[^luoAutellixEfficientServing] It works because the [KV cache](kv-cache.md) of a token depends only on the tokens before it, so sequences with the same prefix can reuse the KV cache of the prefix tokens.[^zhengSGLangEfficientExecution2024]

## How it works

- **Cache-hit rate.** Autellix defines it as the percentage of precomputed input tokens in the LLM engine's KV cache for an incoming LLM call.[^luoAutellixEfficientServing] SGLang defines it as the number of cached prompt tokens divided by the number of prompt tokens.[^zhengSGLangEfficientExecution2024]
- **Where the sharing comes from.** Within a single agentic program the cache-hit rate stays above 90% across all input lengths. Across different programs it decays exponentially with input length, which suggests that programs share only the system prompt.[^luoAutellixEfficientServing]
- **Append-only assumption.** Leyline states that prefix caching is correct by construction when the cache grows append-only, as in a chatbot workload.[^maLeylineKVCache2026]

## Variants

| Variant | Description | Paper |
|---|---|---|
| Static prefix sharing in vLLM | vLLM's paged attention can share a prompt with a static prefix. SGLang describes this as basic prefix sharing that covers simple cases such as system prompt sharing | Parrot[^linParrotEfficientServing2024], SGLang[^zhengSGLangEfficientExecution2024] |
| [RadixAttention](radix-attention.md) | The KV cache of all requests is kept in a radix tree with LRU eviction, which handles multi-level and tree-structured sharing | SGLang[^zhengSGLangEfficientExecution2024] |
| Hashed-prefix sharing in Parrot | A key-value store maps each hashed prefix of tokens to a list of requests, so sharing is detected online for static and dynamically generated prompts | Parrot[^linParrotEfficientServing2024] |
| vLLM Automatic Prefix Caching (APC) with PrefixCacheAffinityRouter | Prefix reuse plus routing of requests with similar prefixes to the same workers. The router works at the prefix level, not the session level. Prefix caching is available in vLLM since v0.4.2 | SAGA[^guoSAGAWorkflowAtomicScheduling2026] |
| Prefix/context cache | KAIROS's name for the cache in which systems such as vLLM retain previously processed tokens, so later turns resume from accumulated history | KAIROS[^yuanKAIROSStatefulContextAware2026] |
| Provider prompt caching | Leyline's positioning table lists Anthropic prompt caching, OpenAI prompt caching, and Google context caching as read-side reuse | Leyline[^maLeylineKVCache2026] |

## Papers using it

| Paper | How it uses or compares against prefix caching | Numbers |
|---|---|---|
| Autellix[^luoAutellixEfficientServing] | Enables prefix-caching in the vLLM-opt baseline. Its load balancer pins long calls to the engine that holds their program's prefix and load-balances short calls | vLLM without prefix caching performs worst. Autellix reaches up to 8× the throughput of vLLM and twice that of vLLM-opt on ShareGPT and BFCL; up to 15× and 4× on the mixed workload. Requests below 2048 tokens reach cache hit rates ≥75% on any engine |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | Compares against vLLM+APC v0.15.1 as the state-of-the-art configuration, and against "LRU + Prefix (vLLM v0.5)" as an eviction policy | Task completion time on SWE-bench: 612.3±32.1 s (vLLM v0.6.0), 352.1±21.4 s (vLLM+APC), 203.4±12.8 s (SAGA). Time spent regenerating KV cache: 38%, 22%, 8%. Competitive ratio against Bélády's optimal: LRU + Prefix 1.97 (SWE-bench), 1.74 (WebArena), 1.86 (mean); WA-LRU 1.31, 1.28, 1.30 |
| Leyline[^maLeylineKVCache2026] | Targets the case that prefix caching does not cover: a policy edits earlier context. Its splice keeps the unedited prefix matched by the radix cache and avoids re-prefilling the content after the edit | Replay cache hit 49.6% (vanilla SGLang radix cache) → 60.8% (splice) on a message-edit microbenchmark |
| SGLang[^zhengSGLangEfficientExecution2024] | Generalizes prefix reuse with RadixAttention and cache-aware scheduling | Up to 6.4× higher throughput on LM-program benchmarks |
| Parrot[^linParrotEfficientServing2024] | Shares common prompt prefixes detected from prompt structure, and co-locates requests that share a long prefix | 1.8×∼2.4× over a baseline without prompt sharing (Bing Copilot workload, batch sizes 8 and 16); 12× higher request rates than a baseline without sharing for multiple GPTs applications, and 3× with affinity scheduling turned off |
| SuffixDecoding[^oliaroSuffixDecodingExtremeSpeculative2024] | Runs its end-to-end vLLM experiment with prefix caching enabled | none specific to prefix caching |
| KAIROS[^yuanKAIROSStatefulContextAware2026] | Runs vLLM with context caching enabled and studies how the retained context grows across agent turns | none specific to prefix caching |

## Strengths & Limitations

- vLLM's prefix caching does not retain session-specific cache across tool-call boundaries; vLLM+APC still evicts session-specific cache during long tool calls.[^guoSAGAWorkflowAtomicScheduling2026]
- Identical content that moves to a new absolute position between turns invalidates exact-prefix caches.[^maLeylineKVCache2026]
- When an agent harness edits the message list, the cost is the full prefix recomputation that prefix caching was meant to amortize.[^maLeylineKVCache2026]
- Static prefix sharing cannot identify dynamically generated content that could also be shared at runtime.[^linParrotEfficientServing2024]
- Enforcing data locality for short requests offers negligible gains and risks skewing engine utilization.[^luoAutellixEfficientServing]

# Contradictions

SAGA's text and table disagree on one value. Section 7.1 gives prefix-caching a competitive ratio of 1.86× on SWE-bench, and Table 2 gives 1.97 on SWE-bench with 1.86 as the mean of SWE-bench and WebArena.[^guoSAGAWorkflowAtomicScheduling2026] Both come from the same paper, so the difference is an inconsistency in the source, not a difference in setting.

## Related

- [KV cache](kv-cache.md), [RadixAttention](radix-attention.md), [PagedAttention](paged-attention.md), [vLLM](vllm.md), [SGLang](sglang.md), [Chunked prefill](chunked-prefill.md), [LMCache](lmcache.md), [Program-aware scheduling](program-aware-scheduling.md)
- Papers: [Autellix](../papers/luoAutellixEfficientServing.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [Leyline](../papers/maLeylineKVCache2026.md), [SGLang](../papers/zhengSGLangEfficientExecution2024.md), [Parrot](../papers/linParrotEfficientServing2024.md), [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md), [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md)

[^luoAutellixEfficientServing]: Luo et al.
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^maLeylineKVCache2026]: Ma et al. 2026
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
[^linParrotEfficientServing2024]: Lin et al. 2024
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
