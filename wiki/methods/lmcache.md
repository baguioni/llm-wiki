---
type: Method
title: LMCache
description: KV cache storage and movement layer for vLLM and SGLang that operates on cache blocks in physical storage tiers, used by papers in this wiki as an offloading baseline and as the layer below semantic cache edits.
tags: [llm-serving, kv-cache, kv-cache-offloading, storage, system]
sources:
  - id: maLeylineKVCache2026
    resource: zotero://select/items/@maLeylineKVCache2026
    title: "Leyline: KV Cache Directives for Agentic Inference"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# LMCache

## Overview

LMCache is not the subject of any paper in this wiki. The description below is what three papers that cite it state. All three cite the same reference, "LMCache: An Efficient KV Cache Layer for Enterprise-Scale LLM Inference" (arXiv 2510.09665).[^maLeylineKVCache2026][^kangThunderAgentSimpleFast2026][^yuanKAIROSStatefulContextAware2026]

Leyline describes LMCache as the production storage and movement layer for [vLLM](../methods/vllm.md) and [SGLang](../methods/sglang.md).[^maLeylineKVCache2026] KAIROS describes it as a framework for offloading context to CPU memory or lower-tier storage.[^yuanKAIROSStatefulContextAware2026] ThunderAgent uses it for [KV cache offloading](../methods/kv-cache-offloading.md) to CPU or SSD storage and names it as a system that enables KV cache transfer across data-parallel (DP) nodes.[^kangThunderAgentSimpleFast2026]

## How it works

- **Control API.** LMCache ships a control API with the verbs Pin, Clear, Move, Compress, and Lookup. The verbs act on KV cache *blocks* in physical storage tiers.[^maLeylineKVCache2026]
- **Position in the cache design space.** In Leyline's design-space table, LMCache targets storage, its reuse is prefix reuse, and its granularity is a 256-tok block. The correctness-after-edit column is n/a.[^maLeylineKVCache2026]
- **Integration.** It is integrated with vLLM and SGLang.[^maLeylineKVCache2026]

## Papers using it

- **[Leyline](../papers/maLeylineKVCache2026.md)** positions itself one layer above LMCache. LMCache's verbs act on blocks, while Leyline's directive acts on semantic spans of the prompt. The paper describes one pipeline: agent intent, then a semantic directive (Leyline), then block operations (LMCache), then physical tier movement. A directive such as "replace this stale tool-output span with a stub" decomposes into block-level operations (free, allocate, $K_{\mathrm{pe}}$ rotate, re-index) that LMCache schedules across tiers. Leyline states that it supplies what LMCache does not: position-encoding correctness across a semantic edit, and a span-level interface for the policy.[^maLeylineKVCache2026] Leyline also presents the block-level Pin in LMCache as the storage-side enforcement of its proposed semantic PIN directive, and notes that a proposed scratchpad KV extension goes beyond LMCache's block-level Compress.[^maLeylineKVCache2026]
- **[ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md)** runs vLLM + LMCache as a KV cache offloading ablation, serving GLM-4.6 with the mini-SWEAgent framework. It reports that PCIe bandwidth is insufficient for the context switching and data transfers of agentic workloads, and that the latency penalty from frequent swap-in and swap-out operations negates the memory capacity benefits, resulting in severe throughput degradation under heavy agentic workloads. The result is given as a KV cache hit rate plot (Figure 7(a)); the text states no number.[^kangThunderAgentSimpleFast2026]
- **[KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md)** uses LMCache-based offloading as one of two thrashing-regime baselines. In a controlled experiment that replays a replicated 18-turn mini-swe-agent request from SWE-bench Verified at 0.5 (non-thrashing) and 0.6 (thrashing) requests/second, offloading reduces average agent completion throughput by 42.1% (recomputation: 44.2%), and the average time spent in LLM calls increases by 3$\times$ for both. KAIROS attributes the offloading loss to starvation of GPU compute resources due to CPU-GPU data transfers.[^yuanKAIROSStatefulContextAware2026]

## Strengths & Limitations

- It consolidates the block-level lifecycle half of the agentic cache problem in production, in Leyline's words.[^maLeylineKVCache2026]
- It operates below the semantic-edit level.[^maLeylineKVCache2026]
- Two papers report that LMCache-based offloading performs poorly for agentic workloads under memory pressure. ThunderAgent attributes this to PCIe bandwidth.[^kangThunderAgentSimpleFast2026] KAIROS measures a throughput loss close to that of recomputation (42.1% vs 44.2%).[^yuanKAIROSStatefulContextAware2026]
- Its cross-node KV cache transfer is constrained by limited interconnect bandwidth in large-batch agentic serving and rollout.[^kangThunderAgentSimpleFast2026]
- Neither negative result compares LMCache with another offloading backend in the same setting. The conflicting conclusions about offloading in general are on the [KV cache offloading](../methods/kv-cache-offloading.md) page.

## Related

- [KV cache](../methods/kv-cache.md), [KV cache offloading](../methods/kv-cache-offloading.md), [KV cache swapping](../methods/kv-cache-swapping.md), [Prefix caching](../methods/prefix-caching.md)
- Systems: [vLLM](../methods/vllm.md), [SGLang](../methods/sglang.md), [ThunderAgent](../methods/thunderagent.md)

[^maLeylineKVCache2026]: Ma et al. 2026
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
