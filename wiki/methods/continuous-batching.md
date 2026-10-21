---
type: Method
title: Continuous batching
description: Batching scheme for LLM serving in which requests join and leave the running batch between forward passes, as the wiki's papers describe and rely on it.
tags: [llm-serving, batching, scheduling]
sources:
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
---

# Continuous batching

## Overview

None of the wiki's papers introduces continuous batching, and most name it without defining it. The descriptions they do give:

- CoSine: continuous batching allows concurrent processing of multiple inference requests and eliminates stalls between request completions.[^gaoCollaborativeSpeculativeInference]
- InferCept does not use the term. It describes Orca's *iteration-level scheduling*: at the end of each model forward pass the scheduler is invoked to form a new batch for the next forward pass, which improves GPU utilization and gives higher inference throughput.[^abhyankarInferCeptEfficientIntercept2024] MORI credits the same system, Orca, with introducing continuous batching.[^xiaIdlenessRelativeExploiting2026] No paper in the wiki states that the two terms name the same technique.

## Papers using it

| Paper | How it uses continuous batching | Numbers |
|---|---|---|
| SGLang[^zhengSGLangEfficientExecution2024] | [RadixAttention](radix-attention.md) is compatible with continuous batching. Nodes used by the running batch cannot be evicted, so each radix-tree node keeps a reference counter of running requests. The cache-aware scheduling algorithm is written for RadixAttention with continuous batching | none specific to continuous batching |
| Symphony[^agarwalSYMPHONYImprovingMemory2024] | Symphony employs continuous batching, like vLLM. The paper uses it to explain an indirect gain: a faster prefill lets more requests reach the decode phase sooner, which raises throughput | Swap against recompute on 1000 ShareGPT samples, one A100, LLaMa-7B: total pre-fill time reduced by a factor of 4.9 and decode time by a factor of 1.68, with the decode reduction attributed to continuous batching |
| Parrot[^linParrotEfficientServing2024] | Parrot's engine supports continuous batching, and its vLLM baseline runs with continuous batching enabled | vLLM's latency per output token rises notably beyond a batch capacity of 6144 |
| CoSine[^gaoCollaborativeSpeculativeInference] | The verification server integrates continuous batching. The vLLM baseline is described as a framework that implements continuous batching | Normalized throughput 3.15× to 4.71× (LLaMA pair) and 2.84× to 3.79× (Qwen pair) over vLLM |
| InferCept[^abhyankarInferCeptEfficientIntercept2024] | Adopts iteration-level scheduling with its own policy: at each iteration it makes the decision that minimizes GPU memory waste for requests intercepted or resumed in that iteration | 1.6×-2× higher serving load than vLLM at similar latency per token |
| Autellix[^luoAutellixEfficientServing] | Describes vLLM as integrating continuous batching and PagedAttention | none specific to continuous batching |
| SSD / Saguaro[^kumarSpeculativeSpeculativeDecoding2026] | The custom inference engine incorporates continuous batching | none specific to continuous batching |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | Cited as background on LLM serving systems | none |
| MORI[^xiaIdlenessRelativeExploiting2026] | Cited as background on LLM serving | none |
| I-DLM[^yuIntrospectiveDiffusionLanguage2026] | Continuous batching works unmodified because every ISD step yields at least one token per request, so all requests advance uniformly. In block diffusion, tokens in a block converge at different rates and requests must synchronize at the slowest block, which the paper says breaks continuous batching | At batch size 8, throughput grows with tokens per forward at a slope of 549 for I-DLM against 84 for SDAR |

## Strengths & Limitations

- vLLM does not benefit from continuous batching during the pre-fill phase, because prefill throughput stays constant as batch size increases.[^agarwalSYMPHONYImprovingMemory2024]
- SAGA states that batching decisions in existing serving systems ignore session affinity.[^guoSAGAWorkflowAtomicScheduling2026]
- Diffusion LLMs that denoise a block for a variable number of steps do not fit it: I-DLM argues that block diffusion requests must wait for the slowest block in the batch.[^yuIntrospectiveDiffusionLanguage2026]

# Contradictions

The papers attribute the origin of continuous batching differently. MORI states that Orca introduced continuous batching.[^xiaIdlenessRelativeExploiting2026] SSD cites Yu et al., 2022 for it, which is the reference InferCept gives for Orca.[^kumarSpeculativeSpeculativeDecoding2026][^abhyankarInferCeptEfficientIntercept2024] SAGA states that vLLM, SGLang, Orca, and TensorRT-LLM "pioneered continuous batching and efficient memory management".[^guoSAGAWorkflowAtomicScheduling2026] SAGA's sentence credits a group of systems for two techniques together, so it does not single out one origin. This is a difference in attribution, not in a measured value.

## Related

- [vLLM](vllm.md), [SGLang](sglang.md), [PagedAttention](paged-attention.md), [Chunked prefill](chunked-prefill.md), [RadixAttention](radix-attention.md), [KV cache](kv-cache.md)
- Papers: [SGLang](../papers/zhengSGLangEfficientExecution2024.md), [Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md), [Parrot](../papers/linParrotEfficientServing2024.md), [CoSine](../papers/gaoCollaborativeSpeculativeInference.md), [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md), [Autellix](../papers/luoAutellixEfficientServing.md), [SSD](../papers/kumarSpeculativeSpeculativeDecoding2026.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [MORI](../papers/xiaIdlenessRelativeExploiting2026.md), [I-DLM](../papers/yuIntrospectiveDiffusionLanguage2026.md)

[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
[^linParrotEfficientServing2024]: Lin et al. 2024
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
