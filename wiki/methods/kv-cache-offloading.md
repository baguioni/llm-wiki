---
type: Method
title: KV cache offloading
description: Moving KV cache that is not immediately needed from GPU HBM to CPU DRAM or lower storage tiers and reloading it on demand, to extend the effective KV cache capacity of a serving node.
tags: [llm-serving, kv-cache, memory-management, agentic-inference, scheduling]
sources:
  - id: xiaIdlenessRelativeExploiting2026
    resource: zotero://select/items/@xiaIdlenessRelativeExploiting2026
    title: "Idleness Is Relative: Exploiting Tool-Call Idle Windows for Offloading in Agentic Systems with MORI"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: agarwalSYMPHONYImprovingMemory2024
    resource: zotero://select/items/@agarwalSYMPHONYImprovingMemory2024
    title: "SYMPHONY: Improving Memory Management for LLM Inference Workloads"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
---

# KV cache offloading

## Overview

When GPU memory is insufficient, [KV cache](../methods/kv-cache.md) tensors that are not immediately needed are offloaded to host memory or lower tiers of the memory hierarchy and reloaded on demand.[^xiaIdlenessRelativeExploiting2026] The motivation is that GPU HBM is the scarcest resource in a serving node: a typical H100 server pairs 80 GB of HBM per GPU for 8 GPUs with 1 TB of host DRAM, a roughly 2$\times$ capacity gap between the two tiers.[^xiaIdlenessRelativeExploiting2026] Without offloading, context that does not fit in HBM is evicted entirely and later recomputed from scratch.[^xiaIdlenessRelativeExploiting2026]

Earlier papers in this wiki call the same GPU-to-host movement [KV cache swapping](../methods/kv-cache-swapping.md).

## How it works

- **Tiers.** Offloading introduces a two-tier hierarchy of GPU HBM and CPU DRAM. A program in the GPU tier runs inference normally. A program whose context is in the CPU tier stays paused, even after its tool call completes, until the context is promoted back to GPU HBM.[^xiaIdlenessRelativeExploiting2026] Other systems extend the hierarchy to NVMe SSD.[^kangThunderAgentSimpleFast2026]
- **Transfer cost.** Offloading and reloading a program's KV cache incurs a transfer cost linear to its size. For a short tool-call gap this cost can exceed the gap itself. For a long tool call it is negligible relative to the gap.[^xiaIdlenessRelativeExploiting2026]
- **Scheduling dimension.** The system must decide which entries stay on the GPU, which to offload, and when to reload them.[^xiaIdlenessRelativeExploiting2026]
- **Target workload.** Online-serving offloading methods mainly target chatbots, where inter-turn gaps are dominated by human typing latency (typically tens of seconds), which leaves time to offload after each turn and reload before the next.[^xiaIdlenessRelativeExploiting2026] In agent serving, tool-call durations vary by orders of magnitude and are not known until the calls complete.[^xiaIdlenessRelativeExploiting2026]

## Variants

| Variant | Description | Source |
|---|---|---|
| Engine-managed LRU offloading | SGLang's HiCache manages CPU DRAM with its own LRU policy, without coordination from the scheduler (the TA+O baseline). | [^xiaIdlenessRelativeExploiting2026] |
| Idleness-ranked placement (MORI) | Programs are ranked by a continuous idleness metric. The busiest go to GPU HBM and the most idle to CPU DRAM, with admission control at both tiers. | [^xiaIdlenessRelativeExploiting2026] |
| Storage-layer offloading ([LMCache](../methods/lmcache.md)) | Offloads context to CPU memory or lower-tier storage. | [^yuanKAIROSStatefulContextAware2026] |
| Advisory-request prefetching (Symphony) | K,V caches are moved between memory tiers and nodes ahead of the request, off the critical serving path, with one copy always kept on disk. | [^agarwalSYMPHONYImprovingMemory2024] |
| Tiered caching with prefetch | Systems such as Pensieve, Continuum, Strata, and ShadowKV offload inactive KV states to lower-tier storage and prefetch them back on request resumption. | [^kangThunderAgentSimpleFast2026] |

## Papers using it

- **[MORI](../papers/xiaIdlenessRelativeExploiting2026.md)** is built around offloading. It uses SGLang v0.5.10 with HiCache as the offloading backend and compares against [ThunderAgent](../methods/thunderagent.md) with and without offloading (TA+O, TA) and SGLang Model Gateway (SMG). At 80 concurrent programs it reports 20–71% higher output throughput and 18–43% lower average TTFT than TA+O, and 1.6–2.1$\times$ higher throughput than SMG and TA.[^xiaIdlenessRelativeExploiting2026]
- **[ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md)** tests offloading twice. With [vLLM](../methods/vllm.md) + LMCache, serving GLM-4.6 with mini-SWEAgent, it reports that PCIe bandwidth is insufficient and that offloading results in severe throughput degradation under heavy agentic workloads (Figure 7(a), no number in the text). With SGLang HiCache (host-memory ratio 2.0, MiniMax M2.5 on [R2E-Gym](../datasets/r2e-gym.md), 8$\times$H100), the offloading-only baseline keeps high throughput up to batch size 96, then its P50 latency jumps from $\sim$10 s to $\sim$30 s at batch 160 and $\sim$70 s at batch 192. With ThunderAgent added, P50 stays at $\sim$10 s and P90 at $\sim$20 s across the sweep.[^kangThunderAgentSimpleFast2026]
- **[Symphony](../papers/agarwalSYMPHONYImprovingMemory2024.md)** argues that offloading makes the workload sticky and uses advisory requests to enable K,V cache offloading together with request-level load balancing.[^agarwalSYMPHONYImprovingMemory2024]
- **[KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md)** measures LMCache-based offloading as one of two fallbacks in the thrashing regime (the other is recomputation).[^yuanKAIROSStatefulContextAware2026]
- **[SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md)** considers offloading idle KV caches to host DRAM via PCIe during tool-call gaps and chooses HBM retention with predictive eviction instead.[^guoSAGAWorkflowAtomicScheduling2026]

### Numbers reported for offloading systems

| System with offloading | Compared to | Result | Setting | Reported by |
|---|---|---|---|---|
| TA+O (ThunderAgent + HiCache) | TA (no offloading) | 667 vs 557 tokens/s | H200 (80 GB), Qwen-2.5 7B, DP=1, 80 programs, Claude Code trace replay | [^xiaIdlenessRelativeExploiting2026] |
| TA+O | TA, SMG | average TTFT 56 s vs 73 s and 108 s | B200, Llama-3.1 70B, 80 programs, 1$\times$ CPU memory | [^xiaIdlenessRelativeExploiting2026] |
| TA+O | itself at lower load | 147, 181, then 146 tokens/s at 20, 50, 80 programs | B200, Llama-3.1 70B, 1$\times$ CPU memory | [^xiaIdlenessRelativeExploiting2026] |
| MORI | TA+O | 853 vs 667 tokens/s (+28%) | H200 (80 GB), Qwen-2.5 7B, 80 programs | [^xiaIdlenessRelativeExploiting2026] |
| MORI | TA+O | 213 vs 124 tokens/s (71%) | B200, Llama-3.1 70B, 80 programs, 2$\times$ CPU memory | [^xiaIdlenessRelativeExploiting2026] |
| MORI | TA+O | 136 vs 147 tokens/s (TA+O is higher) | B200, Llama-3.1 70B, 20 programs, 1$\times$ CPU memory | [^xiaIdlenessRelativeExploiting2026] |
| SGLang + HiCache | SGLang + HiCache + ThunderAgent | P50 latency $\sim$70 s vs $\sim$10 s | MiniMax M2.5, R2E-Gym, 8$\times$H100, batch 192, host-memory ratio 2.0 | [^kangThunderAgentSimpleFast2026] |
| LMCache-based offloading in the thrashing regime (0.6 requests/second) | non-thrashing vLLM baseline (0.5 requests/second) | average agent completion throughput reduced by 42.1%; average time in LLM calls increases by 3$\times$ | replicated 18-turn mini-swe-agent request from SWE-bench Verified | [^yuanKAIROSStatefulContextAware2026] |
| Recomputation in the thrashing regime (0.6 requests/second) | same baseline | throughput reduced by 44.2%; average time in LLM calls increases by 3$\times$ | same | [^yuanKAIROSStatefulContextAware2026] |

## Strengths & Limitations

Strengths:

- Expands the effective memory available for KV cache.[^xiaIdlenessRelativeExploiting2026]
- At low concurrency (20 programs), where the working set fits in the CPU tier, offloading systems reach 87–96% cache hit rates.[^xiaIdlenessRelativeExploiting2026]

Limitations:

- **Bandwidth.** Efficiency is constrained by the inter-tier bandwidth between device and host memory.[^kangThunderAgentSimpleFast2026] A 10.7 GB cache (Llama-3-70B, 32K context) takes $\approx$430 ms one-way over PCIe Gen4 $\times$16 at 25 GB/s.[^guoSAGAWorkflowAtomicScheduling2026] KAIROS attributes the offloading baseline's loss to starvation of GPU compute resources due to CPU-GPU data transfers.[^yuanKAIROSStatefulContextAware2026]
- **Capacity is still finite.** Offloading too many idle programs to DRAM makes them evict one another, so CPU memory needs admission control as well.[^xiaIdlenessRelativeExploiting2026] Once combined host and device capacity is exhausted, throughput decreases despite a larger batch.[^kangThunderAgentSimpleFast2026]
- **Phase-oblivious eviction.** LRU can evict a busy-phase program in a short tool-call gap while keeping an idle-phase program that just entered a long tool call.[^xiaIdlenessRelativeExploiting2026]
- **Statefulness.** Offloading from GPU HBM requires future requests of a session to be handled by the same machine, which leads to load imbalance, and on-demand migration adds high overhead.[^agarwalSYMPHONYImprovingMemory2024]
- **Cross-node transfer.** KV cache transfer across DP nodes is constrained by limited interconnect bandwidth in large-batch agentic serving and rollout.[^kangThunderAgentSimpleFast2026]

# Contradictions

**Does offloading help agentic workloads?** The papers disagree in their conclusions. No two of them use the same setting, so both sides are kept.

| Position | Evidence | Setting | Source |
|---|---|---|---|
| Offloading hurts | "severe throughput degradation under heavy agentic workloads" | vLLM + LMCache, GLM-4.6, mini-SWEAgent (figure only) | [^kangThunderAgentSimpleFast2026] |
| Offloading is no better than recomputation under thrashing | throughput reduced by 42.1% (offloading) vs 44.2% (recomputation) | LMCache, replicated 18-turn mini-swe-agent request, 0.6 requests/second | [^yuanKAIROSStatefulContextAware2026] |
| Swap is pure overhead for the modal request | $\approx$860 ms round trip vs tool P50 of 45 to 180 ms | analytical estimate, Llama-3-70B on A100-class PCIe Gen4 | [^guoSAGAWorkflowAtomicScheduling2026] |
| Offloading helps | TA+O 667 vs TA 557 tokens/s; TTFT 56 s vs 73 s | SGLang v0.5.10 + HiCache, Claude Code traces, 80 programs | [^xiaIdlenessRelativeExploiting2026] |
| Offloading helps until combined capacity is exhausted | high throughput up to batch size 96, collapse at 160 and 192 | SGLang HiCache, MiniMax M2.5, 8$\times$H100 | [^kangThunderAgentSimpleFast2026] |

Likely setting differences: the offloading backend (LMCache with vLLM in the negative results, HiCache with SGLang in the positive ones), the model size, the tool-call duration distribution of the workload, and the load level relative to combined GPU and CPU capacity. MORI's own data show both outcomes for one system: TA+O rises from 147 to 181 tokens/s and falls back to 146 tokens/s as load grows.[^xiaIdlenessRelativeExploiting2026] SAGA states that swap remains complementary for over-subscribed regimes ($>$95% utilization), which are outside its evaluation.[^guoSAGAWorkflowAtomicScheduling2026]

## Related

- [KV cache](../methods/kv-cache.md), [KV cache swapping](../methods/kv-cache-swapping.md), [Prefix caching](../methods/prefix-caching.md), [RadixAttention](../methods/radix-attention.md), [PagedAttention](../methods/paged-attention.md)
- Systems: [LMCache](../methods/lmcache.md), [ThunderAgent](../methods/thunderagent.md), [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Scheduling: [Program-aware scheduling](../methods/program-aware-scheduling.md)

## Open questions and results

- [Does offloading the KV cache to CPU memory help agentic workloads?](../questions/kv-cache-offloading-for-agent-workloads.md)

[^xiaIdlenessRelativeExploiting2026]: Xia et al. 2026
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^agarwalSYMPHONYImprovingMemory2024]: Agarwal et al. 2024
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
