---
type: Method
title: vLLM
description: LLM inference engine that the wiki's papers use as a baseline, as the system they extend, or as the serving host for their experiments.
tags: [llm-serving, inference-engine, kv-cache, baseline]
sources:
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: gaoAgentScopeFlexibleRobust2024
    resource: zotero://select/items/@gaoAgentScopeFlexibleRobust2024
    title: "AgentScope: A Flexible yet Robust Multi-Agent Platform"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: maLeylineKVCache2026
    resource: zotero://select/items/@maLeylineKVCache2026
    title: "Leyline: KV Cache Directives for Agentic Inference"
  - id: wangAgentDropoutDynamicAgent2025
    resource: zotero://select/items/@wangAgentDropoutDynamicAgent2025
    title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
---

# vLLM

## Overview

vLLM is an LLM inference engine. None of the wiki's papers is the vLLM paper itself, so this page records how other papers describe and use it.

- Autellix describes it as a high-throughput LLM serving system that integrates [continuous batching](continuous-batching.md) and [PagedAttention](paged-attention.md) to reduce [KV cache](kv-cache.md) fragmentation, with FCFS as its default scheduling policy.[^luoAutellixEfficientServing]
- InferCept attributes the concept of paged attention to vLLM: the KV cache is treated as virtual memory that can map to non-contiguous physical GPU memory.[^abhyankarInferCeptEfficientIntercept2024]
- CoSine describes it as an LLM inference framework that implements continuous batching with distributed execution across GPUs.[^gaoCollaborativeSpeculativeInference]
- ThunderAgent describes it as a widely adopted, request-aware inference engine that serves as a stateless baseline, with no agent- or program-specific awareness.[^kangThunderAgentSimpleFast2026]
- SGLang groups it with TGI and TensorRT-LLM as state-of-the-art inference engines that are optimized without direct knowledge of the workload.[^zhengSGLangEfficientExecution2024]

## Variants

Versions and configurations that the wiki's papers name:

| Version / configuration | What the paper says about it | Paper |
|---|---|---|
| v0.2.5, default API server | Used as the baseline because RadixAttention had been partially integrated into the latest vLLM as an optional experimental feature | SGLang[^zhengSGLangEfficientExecution2024] |
| v0.4.2 | Prefix caching is available since this version | SAGA[^guoSAGAWorkflowAtomicScheduling2026] |
| v0.5 | Listed as "LRU + Prefix" in the eviction-policy comparison | SAGA[^guoSAGAWorkflowAtomicScheduling2026] |
| v0.6.0 (V1 engine) | PagedAttention with FCFS scheduling. SAGA extends this version | SAGA[^guoSAGAWorkflowAtomicScheduling2026] |
| v0.6.1 | FCFS baseline. Autellix builds on this version | Autellix[^luoAutellixEfficientServing] |
| vLLM-opt (v0.6.1) | Chunk-prefill, prefix-caching, and multi-step scheduling enabled | Autellix[^luoAutellixEfficientServing] |
| v0.11.0 + patch | Patch enables proper rejection sampling at non-zero temperatures. Equivalent support was integrated upstream starting from v0.18.0 | LK Losses[^samarinLKLossesDirect2026] |
| v0.14.0 | Serving host, one H100 per instance | KAIROS[^yuanKAIROSStatefulContextAware2026] |
| vLLM+APC (v0.15.1) | Automatic Prefix Caching and PrefixCacheAffinityRouter enabled | SAGA[^guoSAGAWorkflowAtomicScheduling2026] |
| v0.16.0 | Baseline with autoregressive decoding, standalone speculative decoding, and EAGLE-3 | SSD[^kumarSpeculativeSpeculativeDecoding2026] |
| vLLM KV-aware router | Sends all requests from the same agentic workflow to the same node | ThunderAgent[^kangThunderAgentSimpleFast2026] |
| vLLM + LMCache | KV cache offloading configuration | ThunderAgent[^kangThunderAgentSimpleFast2026] |

## Papers using it

Role is one of: *baseline* (the paper compares against vLLM), *built on* (the paper's system extends or reuses vLLM code), *deployment target* (the paper's method is integrated into vLLM and measured there), *host* (vLLM only serves the models).

| Paper | Role | vLLM version / configuration | Headline number against vLLM | Setting |
|---|---|---|---|---|
| InferCept[^abhyankarInferCeptEfficientIntercept2024] | built on, baseline | Unmodified vLLM, which performs Discard on an interception | 1.6×-2× higher serving load at similar latency per token. Per model: up to 1.6× higher request arrival rate and 1.9×-5.7× lower normalized latency (GPT-J 6B, 1 GPU); up to 1.8× and 1.6×-10× (Vicuna 13B, 2 GPUs); 2× and 1.3×-12× (Llama3 70B, 4 GPUs) | A100 GPUs, mixed workload of six augmentation types |
| InferCept[^abhyankarInferCeptEfficientIntercept2024] | baseline | Same | Up to 2.3× (QA) and 1.9× (Chatbot) on normalized latency | Single-augment workloads |
| Symphony[^agarwalSYMPHONYImprovingMemory2024] | built on, baseline | vLLM recomputes the K,V cache for every request. Symphony integrates with vLLM's scheduler for block management | Normalized end-to-end latency reduced by 1.4× to 1.9× (LLaMa-3.1 8B) and 1.31× to 1.9× (LLaMa-2-13B); time to first token reduced by up to 2.4×; up to 8× the users at similar time per output token (vLLM 64 users at 18ms, Symphony 512 users at 20.5ms) | Multi-turn chatbot workload, varying concurrent users. The introduction of the same paper gives 2.4× average latency reduction and 4× the requests |
| Symphony[^agarwalSYMPHONYImprovingMemory2024] | baseline | Same | Total time reduced by 2.8× | [MetaGPT](metagpt.md) agent workload, LLaMa-3.1-8b across 8 GPUs |
| DFlash[^chenDFlashBlockDiffusion2026] | deployment target | vLLM with autoregressive decoding as the 1× reference | Speedup of 4.0× / 4.6× / 3.0× at concurrency 1 and 1.9× / 2.1× / 1.3× at concurrency 32 (Math500 / HumanEval / MT-Bench) | Qwen3.5-9B |
| CoSine[^gaoCollaborativeSpeculativeInference] | baseline | vLLM as the server-side baseline. "Vanilla" speculative inference is an extension of vLLM with a single draft model | Normalized throughput 3.15× to 4.71× (LLaMA pair) and 2.84× to 3.79× (Qwen pair) | Offline serving, batch sizes 1 to 16, throughput normalized to vLLM at each batch size |
| ThunderAgent[^kangThunderAgentSimpleFast2026] | built on, baseline | vLLM is ThunderAgent's inference engine and the request-aware baseline | 1.48–3.58× throughput at high concurrency (e.g., 96 parallel programs). The Figure 4 caption of the same paper gives "up to 2.43-3.56×" | Agent serving on 8×H100 nodes |
| ThunderAgent[^kangThunderAgentSimpleFast2026] | baseline | vLLM + SGLang Gateway | 375.4 → 671.8 steps/min (1.79×) for mini-SWEAgent; 69.1 → 270.8 steps/min (3.92×) for OpenHands | GLM-4.6 RL rollout on two H100 nodes |
| ThunderAgent[^kangThunderAgentSimpleFast2026] | baseline | vLLM | 1.71–2.08× on mini-SWEAgent and 1.16–1.62× on OpenHands. At concurrency 24 ThunderAgent matches vLLM within noise | 8×A100, concurrency 48 and 72 |
| AgentScope[^gaoAgentScopeFlexibleRobust2024] | host | Listed as one of the supported ways to host local models, with FastChat and Flask | none | not applicable |
| SSD / Saguaro[^kumarSpeculativeSpeculativeDecoding2026] | baseline | v0.16.0 | vLLM's best configurations reach 197.6 tok/s (EAGLE-3, K=6) and 136.0 tok/s (standalone SD, K=2). The paper's SSD averages 255.8 tok/s over four datasets and is reported as on average 30% faster than the strongest speculative decoding baselines | Llama-3.1-70B target with Llama-3.2-1B draft, 4×H100 tensor parallelism, greedy decoding, radix caching disabled, single concurrent request |
| Parrot[^linParrotEfficientServing2024] | built on, baseline | Parrot's engine is built on kernels from vLLM, xFormers, and the authors' own. Baseline is FastChat with vLLM as the engine | End-to-end latency reduced by as much as 1.38×; 1.2× with variable chunk sizes; 2.38× with background requests; 1.68× average with concurrent applications | Chain summary, one engine (A100, LLaMA 13B) |
| Parrot[^linParrotEfficientServing2024] | baseline | vLLM with paged attention sharing a static prompt prefix | 1.1×∼1.7× speedup in request latency; 1.58× and 1.84× in latency per output token | Bing Copilot workload, A100, LLaMA 7B |
| Parrot[^linParrotEfficientServing2024] | baseline (kernel) | Parrot using vLLM's PagedAttention kernel | 2.4× higher request rate with Parrot's own kernel; a further 1.2× speedup with 16 files in the multi-agent workload | Four A6000 with four LLaMA 7B engines; MetaGPT workload |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | built on, baseline | SAGA extends v0.6.0. Baselines: v0.6.0 and vLLM+APC v0.15.1 | Task completion time: 612.3±32.1 s (v0.6.0) and 352.1±21.4 s (vLLM+APC) against 203.4±12.8 s for SAGA on SWE-bench, speedups of 3.01× and 1.73×; 2.17× and 1.55× on WebArena; geometric mean 1.64× over vLLM+APC | 64-GPU cluster, Llama-3-70B-Instruct, [SWE-bench](../benchmarks/swe-bench.md) and [WebArena](../benchmarks/webarena.md) agents |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | baseline | vLLM | SLO attainment 67.3% overall for vLLM against 99.2% for SAGA | Multi-tenant interference |
| Autellix[^luoAutellixEfficientServing] | built on, baseline | Built on v0.6.1 with only the scheduler modified. Baselines: vLLM (FCFS) and vLLM-opt | Throughput at the same latency: up to 8× vLLM and twice vLLM-opt (ShareGPT, BFCL); up to 5× and 2× (LATS); up to 15× and 4× (Mixed). The paper summarizes this as 4-15x | LLaMA-3.1-8B, 70B and Falcon-180B on A100 GPUs |
| Autellix[^luoAutellixEfficientServing] | baseline (kernel) | vLLM's swap kernel, which transfers each KV block individually | 1.3x higher throughput with Autellix's bulk-transfer swap kernel | Ablation |
| EAGLE-3[^liEAGLE3ScalingInference2025] | deployment target | vLLM without speculative sampling as the 1.00x reference | EAGLE-3: 1.75x at batch size 2, falling to 1.01x at batch size 56. EAGLE: 1.30x at batch size 2, 0.71x at batch size 56 | LLaMA-Instruct 3.1 8B, MT-Bench, chain draft with maximum length 2. The body text gives the GPU as RTX3090 and the table caption gives it as A100 |
| SuffixDecoding[^oliaroSuffixDecodingExtremeSpeculative2024] | deployment target, baseline | SuffixDecoding is implemented in vLLM. Baseline is vLLM's native PLD. Prefix caching enabled | 1.3–3× over PLD and 1.8–4.5× speculative speedup over vanilla decoding | [OpenHands](openhands.md) run live on SWE-Bench Verified, 4 H100 GPUs with 4-way tensor parallelism |
| Leyline[^maLeylineKVCache2026] | related system only | Leyline is implemented on SGLang, not vLLM | none | The paper says LMCache is the production storage and movement layer for vLLM and SGLang, and that four open vLLM RFCs each request a slice of cache control with no maintainer-accepted abstraction |
| AgentDropout[^wangAgentDropoutDynamicAgent2025] | host | Llama3 and Qwen2.5 inference runs on vLLM | none | Nvidia A800 GPUs |
| LK Losses[^samarinLKLossesDirect2026] | host | v0.11.0 with a rejection-sampling patch | none | Draft-model evaluation. The paper states that the unpatched implementation samples draft tokens greedily while using temperature-scaled target logits in the acceptance criterion |
| KAIROS[^yuanKAIROSStatefulContextAware2026] | host | v0.14.0, one H100 per instance, context caching enabled | none against vLLM itself. In the paper's thrashing experiment on a vLLM server, recomputation and LMCache-based offloading reduce average agent completion throughput by 44.2% and 42.1% | Qwen3-Coder-30B, mini-swe-agent |
| SGLang[^zhengSGLangEfficientExecution2024] | baseline | v0.2.5 with its default API server | Up to 6.4× higher throughput and up to 3.7× lower latency against Guidance, vLLM, and LMQL together | Llama-7B on A10G, LM-program benchmarks. Per-benchmark values are only in figures |

## Strengths & Limitations

Limitations that the wiki's papers attribute to vLLM:

- It discards all K,V cache state at the end of each request and recomputes it for the next request of a session.[^agarwalSYMPHONYImprovingMemory2024]
- It treats an interception as the end of a request (Discard), which gives it high recomputation waste, and it schedules resumed requests at the end of the waiting queue.[^abhyankarInferCeptEfficientIntercept2024]
- Its FCFS scheduling is application-unaware and suffers from call-level and program-level head-of-line blocking.[^luoAutellixEfficientServing]
- Its request-aware scheduler lacks reserved memory for programs that are executing a tool, which forces frequent recomputation.[^kangThunderAgentSimpleFast2026]
- Its affinity router works at the prefix level, not the session level, and does not retain session-specific KV cache across tool-call boundaries.[^guoSAGAWorkflowAtomicScheduling2026]
- Its GPU kernel reloads shared-prefix tokens repeatedly, and its static prefix sharing does not work when the shared content is generated dynamically.[^linParrotEfficientServing2024]
- It covers simple KV cache reuse cases such as system prompt sharing but not multi-level tree-structured sharing or LRU caching.[^zhengSGLangEfficientExecution2024]
- Its latency per output token rises notably when the batch capacity goes beyond 6144.[^linParrotEfficientServing2024]
- Tree verification codepaths for speculative decoding are described as known to be incomplete in v0.16.0.[^kumarSpeculativeSpeculativeDecoding2026]

# Contradictions

- **vLLM against SGLang.** SSD states that SGLang usually outperforms vLLM and uses SGLang as its main baseline.[^kumarSpeculativeSpeculativeDecoding2026] SAGA's Table 3 has vLLM+APC v0.15.1 ahead of SGLang v0.5.8 (352.1±21.4 s against 387.2±24.3 s task completion time on SWE-bench), while vLLM v0.6.0 is behind both (612.3±32.1 s).[^guoSAGAWorkflowAtomicScheduling2026] Autellix states, citing a vLLM blog post, that vLLM-opt closely matches SGLang and TensorRT.[^luoAutellixEfficientServing] The settings differ: SSD measures single-request decode throughput with speculative decoding and radix caching disabled, SAGA measures agent task completion time on a 64-GPU cluster with prefix caching and affinity routing, and the versions differ in each paper. Within SSD's own sweeps, vLLM's EAGLE-3 result (197.6 tok/s) is above SGLang's (192.8 tok/s), and SGLang leads for standalone speculative decoding (201.9 against 136.0 tok/s).[^kumarSpeculativeSpeculativeDecoding2026]
- **Does vLLM keep the KV cache across requests?** Symphony states that vLLM discards all K,V cache state at the end of each request.[^agarwalSYMPHONYImprovingMemory2024] Autellix states that vLLM v0.6.1 performs worst because it lacks prefix caching.[^luoAutellixEfficientServing] KAIROS states that in systems such as vLLM previously processed tokens are retained in the prefix/context cache.[^yuanKAIROSStatefulContextAware2026] SAGA states that vLLM's prefix caching is available since v0.4.2.[^guoSAGAWorkflowAtomicScheduling2026] The papers use different versions and configurations: Autellix enables prefix caching only in its vLLM-opt baseline, and KAIROS and SuffixDecoding run with caching enabled.[^luoAutellixEfficientServing][^yuanKAIROSStatefulContextAware2026][^oliaroSuffixDecodingExtremeSpeculative2024]

## Related

- Mechanisms the papers attribute to vLLM: [PagedAttention](paged-attention.md), [Continuous batching](continuous-batching.md), [Prefix caching](prefix-caching.md), [Chunked prefill](chunked-prefill.md), [KV cache](kv-cache.md)
- Other engines: [SGLang](sglang.md)
- Systems built on vLLM: [ThunderAgent](thunderagent.md)
- Related storage layer: [LMCache](lmcache.md), [KV cache offloading](kv-cache-offloading.md), [KV cache swapping](kv-cache-swapping.md)
- Papers: [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md), [Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md), [DFlash](../papers/chenDFlashBlockDiffusion2026.md), [CoSine](../papers/gaoCollaborativeSpeculativeInference.md), [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md), [AgentScope](../papers/gaoAgentScopeFlexibleRobust2024.md), [SSD](../papers/kumarSpeculativeSpeculativeDecoding2026.md), [Parrot](../papers/linParrotEfficientServing2024.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [Autellix](../papers/luoAutellixEfficientServing.md), [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md), [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md), [Leyline](../papers/maLeylineKVCache2026.md), [AgentDropout](../papers/wangAgentDropoutDynamicAgent2025.md), [LK Losses](../papers/samarinLKLossesDirect2026.md), [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md), [SGLang](../papers/zhengSGLangEfficientExecution2024.md)

[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^gaoAgentScopeFlexibleRobust2024]: Gao et al. 2024
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^linParrotEfficientServing2024]: Lin et al. 2024
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^luoAutellixEfficientServing]: Luo et al.
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^maLeylineKVCache2026]: Ma et al. 2026
[^wangAgentDropoutDynamicAgent2025]: Wang et al. 2025
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
