---
type: Method
title: SGLang
description: Language and serving runtime for LLM programs that reuses the KV cache through RadixAttention, and that later papers use as a baseline, a host engine, or a deployment target.
tags: [llm-serving, inference-engine, kv-cache, lm-programs, baseline]
sources:
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: maLeylineKVCache2026
    resource: zotero://select/items/@maLeylineKVCache2026
    title: "Leyline: KV Cache Directives for Agentic Inference"
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: wuDualPathBreakingStorage2026
    resource: zotero://select/items/@wuDualPathBreakingStorage2026
    title: "DualPath: Breaking the Storage Bandwidth Bottleneck in Agentic LLM Inference"
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
---

# SGLang

## Overview

SGLang (Structured Generation Language) is a system for executing language model programs: programs with multiple LLM calls, control flow, and structured inputs and outputs.[^zhengSGLangEfficientExecution2024] It has a front-end language embedded in Python and a back-end runtime, the SGLang Runtime (SRT).[^zhengSGLangEfficientExecution2024] The original paper reports up to 6.4× higher throughput than existing programming and inference systems, including Guidance, [vLLM](vllm.md), and LMQL.[^zhengSGLangEfficientExecution2024]

Later papers in the wiki use SGLang mostly as an inference engine: as a baseline, as the engine they extend, or as the place where a speculative decoding method is deployed and measured. The table under "Papers using it" lists each one.

## How it works

As described in the original paper:[^zhengSGLangEfficientExecution2024]

- **Front end.** Primitives for generation (`extend`, `gen`, `select`) and parallelism control (`fork`, `join`), run by an interpreter (default) or a compiler that traces a program into a computational graph.
- **[RadixAttention](radix-attention.md).** The [KV cache](kv-cache.md) of all requests is kept as an LRU cache in a radix tree, with a cache-aware scheduling policy.
- **Compressed finite state machine.** Decodes multiple tokens in one forward pass under a regular-expression constraint.
- **API speculative execution.** Reduces the latency and input-token cost of multi-call programs on API-only models.
- **Implementation.** PyTorch with custom CUDA kernels from FlashInfer and Triton.

Results reported in the original paper:[^zhengSGLangEfficientExecution2024]

| Setting | Result |
|---|---|
| Llama-7B on A10G, LM-program benchmarks | throughput up to 6.4× higher and latency up to 3.7× lower than Guidance v0.1.8, vLLM v0.2.5, and LMQL v0.7.3 |
| Multi-modal benchmarks (LLaVA-v1.5-7B, LLaVA-NeXT-34B) | throughput up to 6× higher than the model authors' Hugging Face Transformers implementation |
| Chatbot Arena deployment, Vicuna-33B | 74.1% RadixAttention cache hit rate after one month; first-token latency reduced by an average of 1.7× |
| Chatbot Arena deployment, LLaVA-Next-34B | 52.4% RadixAttention cache hit rate after one month |
| JSON decoding | compressed FSM increases throughput by 1.6× |

## Variants

Versions and components that the wiki's papers name:

| Version / component | What the paper says about it | Paper |
|---|---|---|
| v0.4.4 | Engine for the EAGLE-3 throughput experiments, run by the SGLang team | EAGLE-3[^liEAGLE3ScalingInference2025] |
| 0.5.2 + Leyline patch | A ∼200-LOC RadixCache patch adds a content-hash side index | Leyline[^maLeylineKVCache2026] |
| v0.5.8 | Baseline with RadixAttention, zero-overhead batch scheduler, and cache-aware load balancing | SAGA[^guoSAGAWorkflowAtomicScheduling2026] |
| 0.5.9 | Baseline with autoregressive decoding, standalone speculative decoding, and EAGLE-3 | SSD[^kumarSpeculativeSpeculativeDecoding2026] |
| v0.5.10 | Engine for all MORI experiments | MORI[^xiaIdlenessRelativeExploiting2026] |
| commit 19089aa, "SGL(MC)" | SGLang with HiCache, Mooncake Store, 3FS as the storage backend, and Mooncake Transfer Engine for prefill-decode disaggregation | DualPath[^wuDualPathBreakingStorage2026] |
| HiCache | SGLang's offloading backend for CPU DRAM | MORI[^xiaIdlenessRelativeExploiting2026], ThunderAgent[^kangThunderAgentSimpleFast2026] |
| SGLang Model Gateway (SMG) | A prefix-aware request scheduler. With one replica it forwards requests directly to the engine | MORI[^xiaIdlenessRelativeExploiting2026] |
| Spec-v1 / Spec-v2 | Spec-v2 enables scheduling overlap and does not support tree-based drafting for EAGLE-3 | DFlash[^chenDFlashBlockDiffusion2026] |

## Papers using it

Role is one of: *baseline* (the paper compares against SGLang), *built on* (the paper's system extends or reuses SGLang), *deployment target* (the paper's method is integrated into SGLang and measured there, with plain SGLang as the reference).

| Paper | Role | SGLang version / configuration | Headline number against SGLang | Setting |
|---|---|---|---|---|
| DFlash[^chenDFlashBlockDiffusion2026] | deployment target | FlashAttention-4 backend, Spec-v2 scheduling overlap | Up to 5.1× at concurrency 1 (Qwen3-8B, Math500: 230 → 1175 tok/s). At concurrency 32 the speedups are 2.2× to 3.1× | Single B200 GPU; Qwen3-4B, Qwen3-8B, Qwen3-Coder-30B-A3B |
| DFlash[^chenDFlashBlockDiffusion2026] | deployment target | Spec-v1, Flashinfer backend | DFlash 2.2×-2.8× at concurrency 1 and 1.4×-1.8× at concurrency 32. [EAGLE-3](eagle-3.md) with 10 draft tokens: 1.5×-2.0× and 0.9×-1.2×. EAGLE-3 with 60 draft tokens: 1.8×-2.0× and 0.5×-0.6× | LLaMA-3.1-8B-Instruct, single B200; GSM8K, HumanEval, Alpaca |
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | baseline | v0.5.8 | Task completion time 387.2±24.3 s for SGLang against 203.4±12.8 s for SAGA on SWE-bench (1.90×), and 138.7±11.3 s against 82.1±6.8 s on WebArena (1.69×). SLO attainment 73.4% overall against 99.2% | 64-GPU cluster, Llama-3-70B-Instruct, [SWE-bench](../benchmarks/swe-bench.md) and [WebArena](../benchmarks/webarena.md) agents |
| SSD / Saguaro[^kumarSpeculativeSpeculativeDecoding2026] | baseline (main) | 0.5.9 | SGLang's best configurations reach 201.9 tok/s (standalone SD, steps 10, topk 3) and 192.8 tok/s (EAGLE-3, steps 8, topk 3). The paper's SSD averages 255.8 tok/s over four datasets and is reported as on average 30% faster than the strongest speculative decoding baselines | Llama-3.1-70B target with Llama-3.2-1B draft, 4×H100 tensor parallelism, greedy decoding, radix caching disabled, single concurrent request |
| ThunderAgent[^kangThunderAgentSimpleFast2026] | baseline | vLLM + SGLang Gateway | 375.4 → 671.8 steps/min (1.79×) for mini-SWEAgent; 69.1 → 270.8 steps/min (3.92×) for OpenHands | GLM-4.6 RL rollout on two H100 nodes |
| ThunderAgent[^kangThunderAgentSimpleFast2026] | baseline | Cache-Aware Routing Policy in SGLang Model Gateway | Speedup widens from 1.79× at 2 nodes to 2.39× at 8 nodes | GLM-4.6 + mini-SWEAgent, 72 programs per node, up to 64×H100 |
| ThunderAgent[^kangThunderAgentSimpleFast2026] | built on | ThunderAgent integrated into SGLang HiCache, host-memory ratio 2.0 | Shown in a figure; the baseline is the same SGLang + HiCache stack without ThunderAgent | MiniMax M2.5 on R2E-Gym, 8×H100, batch size 64 to 192 |
| SpecForge[^liSpecForgeFlexibleEfficient2026] | built on | SGLang's model runner executes the frozen target model during draft training | SGLang backend up to 6.8× over the Hugging Face and custom backends | Training experiments on the Table 1 models |
| SpecForge[^liSpecForgeFlexibleEfficient2026] | deployment target | SGLang as the inference engine for SpecBundle draft models | Up to 4.48× end-to-end inference speedup over the target model alone | NVIDIA H200 GPUs; concurrency 8 for LLaMA-3.1-8B and 16 for larger models |
| EAGLE-3[^liEAGLE3ScalingInference2025] | deployment target | v0.4.4, SGLang without speculative sampling as the 1.00x reference | EAGLE-3: 1.81x at batch size 2 and 1.38x at batch size 64. EAGLE: 1.40x at batch size 2 and 0.99x at batch size 64. At batch size 1: 158.34 tokens/s without speculation, 373.25 tokens/s with EAGLE-3 | Single H100, LLaMA-Instruct 3.1 8B, MT-Bench, chain length 3, no tree |
| Leyline[^maLeylineKVCache2026] | built on, baseline | 0.5.2 with the Leyline patch. Baseline arms: vanilla SGLang (radix) and SGLang with `--disable-radix-cache` | Replay cache hit 49.6% (radix) → 60.8% (splice). Replay p50 end-to-end −51 ms at C=1, −85 ms at C=4, −241 ms (−4.4%) at C=8, +45 ms (noise) at C=16 | DeepSeek-V2-Lite on one H100, three-arm message-edit microbenchmark |
| Leyline[^maLeylineKVCache2026] | baseline | Vanilla SGLang RadixCache | Sum end-to-end 52.65 s → 49.85 s (5.3%). On a second trajectory with a 91.6% RadixCache hit rate the splice is 0.6% slower | 50-step debug-gym trajectory, C=1 |
| Aurora[^wangWhenRLMeets2026] | built on | An SGLang speculative decoding engine is Aurora's inference server, and SGLang replicas are the actors of its training loop | 1.5× day-0 speedup; 1.57× to 1.25× across batch sizes for MiniMax M2.1, relative to serving without speculation | MiniMax M2.1 229B and Qwen3-Coder-Next 80B on H200 GPUs |
| DualPath[^wuDualPathBreakingStorage2026] | baseline | SGL(MC), commit 19089aa | No headline number. The paper states that comparing DualPath with SGL(MC) is unfair because of implementation differences | SGL(MC) uses 1.5TB DRAM on every node and failed to complete some large configurations |
| MORI[^xiaIdlenessRelativeExploiting2026] | built on, baseline | v0.5.10. MORI adds 500 lines to SGLang's cache subsystem via HiCache. Baseline: SGLang Model Gateway (SMG) | 1.6–2.1× higher output throughput than SMG and ThunderAgent at 80 programs. Example: 853 tokens/s for MORI against 447 tokens/s for SMG on H200 (80 GB) with a 7B model; 189 against 96 tokens/s on B200 with a 70B model | Replayed Claude Code traces, single replica |

## Strengths & Limitations

- The original paper states that greedy cache-aware scheduling can lead to starvation, and leaves fair scheduling to future work.[^zhengSGLangEfficientExecution2024]
- In multi-turn chat with long outputs SGLang shows almost no speedup, because there is little sharing between chat sessions and decoding time dominates.[^zhengSGLangEfficientExecution2024]
- SAGA states that SGLang, like other serving systems, treats each inference call independently, evicts the KV cache with LRU policies that are unaware of agent workflow structure, and ignores session affinity in batching.[^guoSAGAWorkflowAtomicScheduling2026]
- ThunderAgent states that the Cache-Aware Routing Policy in SGLang Model Gateway falls behind as the cluster grows, because a locality-only router cannot rebalance memory across nodes.[^kangThunderAgentSimpleFast2026]
- MORI states that HiCache manages CPU DRAM with its own LRU policy, without coordination from the scheduler.[^xiaIdlenessRelativeExploiting2026]
- SpecForge attributes a 2.01× training speedup on LLaMA-3.1-8B to SGLang's optimized prefill execution.[^liSpecForgeFlexibleEfficient2026]
- DualPath notes that SGLang lacks support for its downscaled DS 27B model and for DP attention on Qwen 32B.[^wuDualPathBreakingStorage2026]
- Leyline reports no headroom over RadixCache when RadixCache already covers the workload.[^maLeylineKVCache2026]

# Contradictions

- **EAGLE-3 at high batch size in SGLang.** The EAGLE-3 paper reports that EAGLE-3 keeps a 1.38x throughput gain at batch size 64 (SGLang v0.4.4, single H100, LLaMA-Instruct 3.1 8B, MT-Bench, chain length 3, no tree).[^liEAGLE3ScalingInference2025] DFlash reports that the official EAGLE-3 checkpoints for the same target model give 0.9× to 1.2× at concurrency 32 with 10 draft tokens and 0.5× to 0.6× with 60 draft tokens (single B200, Spec-v1, 7 draft steps with top-k 10, on GSM8K, HumanEval, and Alpaca).[^chenDFlashBlockDiffusion2026] The two differ in GPU, datasets, draft configuration (chain against tree), SGLang version, and batch size against concurrency.
- **SGLang against vLLM.** SSD states that SGLang usually outperforms vLLM.[^kumarSpeculativeSpeculativeDecoding2026] SAGA's Table 3 has vLLM+APC v0.15.1 ahead of SGLang v0.5.8 on both workloads (352.1±21.4 s against 387.2±24.3 s on SWE-bench).[^guoSAGAWorkflowAtomicScheduling2026] SSD measures single-request decode throughput with radix caching disabled, and SAGA measures agent task completion time on a 64-GPU cluster. Details are on the [vLLM](vllm.md) page.
- **Within the EAGLE-3 paper**, the SGLang gain at batch size 64 is given as 1.38x in Table 3, as 38% in Section 4.3, and as 40% in the contributions list.[^liEAGLE3ScalingInference2025]

## Related

- Mechanisms: [RadixAttention](radix-attention.md), [KV cache](kv-cache.md), [Prefix caching](prefix-caching.md), [Continuous batching](continuous-batching.md), [PagedAttention](paged-attention.md), [KV cache offloading](kv-cache-offloading.md)
- Other engines and systems: [vLLM](vllm.md), [ThunderAgent](thunderagent.md), [LMCache](lmcache.md)
- Speculative decoding methods deployed on it: [EAGLE-3](eagle-3.md), [DFlash](dflash.md), [Speculative decoding](speculative-decoding.md)
- Papers: [SGLang](../papers/zhengSGLangEfficientExecution2024.md), [DFlash](../papers/chenDFlashBlockDiffusion2026.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [SSD](../papers/kumarSpeculativeSpeculativeDecoding2026.md), [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md), [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md), [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md), [Leyline](../papers/maLeylineKVCache2026.md), [Aurora](../papers/wangWhenRLMeets2026.md), [DualPath](../papers/wuDualPathBreakingStorage2026.md), [MORI](../papers/xiaIdlenessRelativeExploiting2026.md)

[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^maLeylineKVCache2026]: Ma et al. 2026
[^wangWhenRLMeets2026]: Wang et al. 2026
[^wuDualPathBreakingStorage2026]: Wu et al. 2026
[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
