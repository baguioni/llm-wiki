---
type: Method
title: Chunked prefill
description: Technique that splits a prompt's prefill into chunks so that each chunk shares a batch with decoding requests, as the wiki's papers describe and use it.
tags: [llm-serving, prefill, batching, scheduling]
sources:
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: wuDualPathBreakingStorage2026
    resource: zotero://select/items/@wuDualPathBreakingStorage2026
    title: "DualPath: Breaking the Storage Bandwidth Bottleneck in Agentic LLM Inference"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models
---

# Chunked prefill

## Overview

None of the wiki's papers introduces chunked prefill. InferCept attributes it to Sarathi and describes it as a technique that splits prompt tokens into chunks, each merged with other decoding requests to form one iteration's batch.[^abhyankarInferCeptEfficientIntercept2024] InferCept places it among systems that address the imbalanced computation needs of the prefill and decoding stages.[^abhyankarInferCeptEfficientIntercept2024]

## Variants

- **Recomputation chunking (InferCept).** InferCept applies chunking to the recomputation of a discarded context and to swapping, not to ordinary prompts. The recomputation chunk size is the GPU saturation point (the number of query tokens that all GPU cores can process in parallel, from offline profiling) minus the running group size.[^abhyankarInferCeptEfficientIntercept2024]
- **Quota-bounded chunking (DualPath).** On a prefill engine, requests are added to a forward batch in FIFO order while the predicted attention-layer time stays under a compute quota. If adding a request would exceed the bound, a binary search finds a smaller batch size that fits the remaining quota, and the request is prefilled in chunks.[^wuDualPathBreakingStorage2026]

## Papers using it

| Paper | How it uses chunked prefill | Numbers |
|---|---|---|
| InferCept[^abhyankarInferCeptEfficientIntercept2024] | Adapts the idea to recomputation and swapping of intercepted requests | Adding recomputation chunking to ImprovedDiscard reduces normalized latency by 7.8% more (GPT-J 6B, mixed workload, 2 requests per second) |
| Autellix[^luoAutellixEfficientServing] | Enables it in the vLLM-opt baseline, together with prefix-caching and multi-step scheduling | Autellix reaches twice the throughput of vLLM-opt on ShareGPT and BFCL, up to 2× on LATS, and 4× on the mixed workload. The paper does not isolate the effect of chunked prefill |
| DualPath[^wuDualPathBreakingStorage2026] | Uses it in the intra-engine scheduler of prefill engines when a request does not fit the compute quota. Also lists it among recent inference acceleration techniques | none specific to chunked prefill |
| SpecForge[^liSpecForgeFlexibleEfficient2026] | Lists it among the system-level optimizations of SGLang that its SGLang backend reuses for target-model inference during draft training | SGLang backend up to 6.8× over the Hugging Face and custom backends. The paper does not isolate the effect of chunked prefill |
| HAT[^xieNovelHatShapedDeviceCloud2025] | Splits long prompts on the device so that the upload of one chunk overlaps with cloud computation of the previous one, with the chunk size set per device. The U-Sarathi baseline chunks prompts on the server without that overlap | Prompt chunking lowers SpecBench TTFT from 655.3 to 384.3 ms in the ablation |

## Related

- [Continuous batching](continuous-batching.md), [vLLM](vllm.md), [SGLang](sglang.md), [Prefix caching](prefix-caching.md), [KV cache](kv-cache.md), [KV cache swapping](kv-cache-swapping.md)
- Papers: [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md), [Autellix](../papers/luoAutellixEfficientServing.md), [DualPath](../papers/wuDualPathBreakingStorage2026.md), [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md)

[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^wuDualPathBreakingStorage2026]: Wu et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
