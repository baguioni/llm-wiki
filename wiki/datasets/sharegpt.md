---
type: Dataset
title: ShareGPT
description: Dataset of real user conversations with ChatGPT, used in the wiki's papers as a chatbot serving trace and as training data for draft models and instruction tuning.
tags: [chat, conversations, serving-workload, training-data]
sources:
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
---

# ShareGPT

## Overview

ShareGPT consists of real conversations collected from ChatGPT.[^agarwalSYMPHONYImprovingMemory2024] InferCept describes it as crowd-sourced real-user ChatGPT conversations,[^abhyankarInferCeptEfficientIntercept2024] and Autellix as user-generated conversational inputs and outputs, typical for chatbot applications.[^luoAutellixEfficientServing] The papers in this wiki use it in two ways. LLM serving papers replay it as a multi-turn chatbot workload.[^agarwalSYMPHONYImprovingMemory2024][^abhyankarInferCeptEfficientIntercept2024][^luoAutellixEfficientServing][^linParrotEfficientServing2024][^zhengSGLangEfficientExecution2024] Other papers use it as training data, for speculative-decoding draft models[^liEAGLE3ScalingInference2025][^chenDFlashBlockDiffusion2026][^liSpecForgeFlexibleEfficient2026] and for instruction tuning.[^xiaShearedLLaMAAccelerating2024]

No paper in the wiki uses it as a prompt set for speculative-decoding speedup or reports task accuracy on it.

## Composition

Only what the papers state. They sample or filter the dataset differently, so these statistics do not describe one fixed version.

| Statistic | Value | Source |
|---|---|---|
| Share of conversations that are multi-turn | 73.4%, with some sessions extending beyond 400 turns | Symphony[^agarwalSYMPHONYImprovingMemory2024] |
| Average session length | around 2.2K tokens | Symphony[^agarwalSYMPHONYImprovingMemory2024] |
| LLM calls per conversation (program) | mean of 6.66, max of 80, long-tailed | Autellix[^luoAutellixEfficientServing] |
| Tokens per LLM call | averaging 256 prefill tokens and 277 decode tokens | Autellix[^luoAutellixEfficientServing] |
| Chatbot interceptions per request (mean, variance) | (4.45, 1.96) | InferCept[^abhyankarInferCeptEfficientIntercept2024] |
| Chatbot context length (mean, variance) | (753, 703) | InferCept[^abhyankarInferCeptEfficientIntercept2024] |
| Size as draft-model training data | approximately 68K data entries | EAGLE-3[^liEAGLE3ScalingInference2025] |
| Size as draft-model training data | 120K conversations | SpecForge[^liSpecForgeFlexibleEfficient2026] |

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md) | Multi-turn chatbot trace, 1000 samples unless stated, with arrival times generated from human reading and typing speed | LLaMa-3.1 8B and LLaMa-2-13B on A100 GPUs | Swap instead of recompute cuts total pre-fill time by a factor of 4.9 and decode time by a factor of 1.68 (1000 samples, one A100, LLaMa-7B). Advisory requests can be sent 11.3 seconds earlier on average.[^agarwalSYMPHONYImprovingMemory2024] |
| [InferCept](../papers/abhyankarInferCeptEfficientIntercept2024.md) | Chatbot augmentation workload, one of six interception types | GPT-J 6B, Vicuna 13B, Llama3 70B | On the single Chatbot workload InferCept outperforms vLLM by up to 1.9× on normalized latency[^abhyankarInferCeptEfficientIntercept2024] |
| [Autellix](../papers/luoAutellixEfficientServing.md) | Chatbot agent workload with entire conversations replayed as programs | LLaMA3.1-8B and LLaMA3.1-70B | On ShareGPT and BFCL, throughput at the same latency is up to 8× that of vLLM[^luoAutellixEfficientServing] |
| [Parrot](../papers/linParrotEfficientServing2024.md) | Source of chat service workloads; requests sampled from it with Poisson arrivals for the vLLM capacity study | LLaMA 13B and LLaMA 7B engines | In the mixed workload, $5.5\times$ and $1.23\times$ better normalized latency for chat applications than the latency-focused and throughput-focused baselines[^linParrotEfficientServing2024] |
| [SGLang](../papers/zhengSGLangEfficientExecution2024.md) | Benchmark with no KV cache reuse opportunities, to measure RadixAttention overhead | not stated | 100 requests take 74.3 seconds, of which 0.2 seconds is RadixAttention bookkeeping, less than 0.3%[^zhengSGLangEfficientExecution2024] |
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) | Training data for EAGLE-3 draft models, together with UltraChat-200K; also the unit of the data-scale axis in the scaling-law figures | Target model generates the responses | approximately 68K entries (ShareGPT) and 464K entries (UltraChat-200K)[^liEAGLE3ScalingInference2025] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Training data for a DFlash drafter, with UltraChat, to match EAGLE-3's training data | LLaMA-3.1-8B-Instruct on SGLang | DFlash (10) reaches 2.4× on GSM8K, 2.8× on HumanEval, and 2.2× on Alpaca at concurrency 1[^chenDFlashBlockDiffusion2026] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | Training data for a reproduced EAGLE-3 draft, with UltraChat, as the baseline against Perfect-Blend | LLaMA-3.1-Instruct | Acceptance length 2.82 on Math500, against 3.48 when trained on Perfect-Blend[^liSpecForgeFlexibleEfficient2026] |
| [Sheared-LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) | Instruction tuning: 10,000 instruction-response pairs for fine-tuning and another 1,000 instructions for evaluation, first round of each chat only | Sheared-LLaMA and baselines, GPT-4 as the evaluator | Win rates are given only in a figure[^xiaShearedLLaMAAccelerating2024] |

## Known issues

- SpecForge states that existing draft checkpoints are primarily trained on ShareGPT and UltraChat, which contain limited coverage of math- and code-centric samples, and gives this as the reason those checkpoints trail SpecBundle on math and coding benchmarks.[^liSpecForgeFlexibleEfficient2026]
- The serving papers generate request timing synthetically. Symphony derives arrival times from human reading and typing speed.[^agarwalSYMPHONYImprovingMemory2024] InferCept estimates the human response time of chatbot interceptions.[^abhyankarInferCeptEfficientIntercept2024] Parrot uses Poisson arrivals.[^linParrotEfficientServing2024]
- Sheared-LLaMA uses only the first round of the multi-turn chat history.[^xiaShearedLLaMAAccelerating2024]

# Contradictions

### Size of the ShareGPT training set

EAGLE-3 states that its ShareGPT and UltraChat-200K training data contain approximately 68K and 464K data entries.[^liEAGLE3ScalingInference2025] SpecForge, describing its reproduction of the EAGLE-3 training procedure, gives ShareGPT as 120K conversations and UltraChat as 200K conversations.[^liSpecForgeFlexibleEfficient2026] The two papers count different units ("data entries" and "conversations") and neither says how the data was filtered, so the wiki cannot tell whether they describe the same data.

## Related

- Methods trained on it: [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [Sheared-LLaMA](../methods/sheared-llama.md)
- Serving systems evaluated on it: [vLLM](../methods/vllm.md), [SGLang](../methods/sglang.md), [Radix attention](../methods/radix-attention.md), [KV cache](../methods/kv-cache.md), [KV cache swapping](../methods/kv-cache-swapping.md), [Program-aware scheduling](../methods/program-aware-scheduling.md), [Continuous batching](../methods/continuous-batching.md)
- Datasets: [Open-PerfectBlend](perfectblend.md), [MT-Bench](mt-bench.md), [MATH-500](math-500.md), [HotpotQA](hotpotqa.md), [ALFWorld](alfworld.md)
- Benchmarks used alongside it as workloads: [BFCL](../benchmarks/bfcl.md)

[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
[^linParrotEfficientServing2024]: Lin et al. 2024
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
