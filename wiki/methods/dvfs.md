---
type: Method
title: DVFS (Dynamic Voltage and Frequency Scaling)
description: Changing the operating frequency or voltage point of a CPU, GPU, or NPU to trade inference speed for power, studied in this wiki for mobile LLM inference and for agentic LLM serving on GPUs.
tags: [dvfs, power-efficiency, energy-efficiency, llm-serving, mobile-llm, scheduling]
sources:
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# DVFS (Dynamic Voltage and Frequency Scaling)

## Overview

DVFS stands for Dynamic Voltage and Frequency Scaling.[^caiYourNPUReady2026] Reducing GPU core frequency is a common way to lower power, but it creates a trade-off with inference performance.[^yuanKAIROSStatefulContextAware2026] Two papers in this wiki study it, in different settings: Cai et al. sweep CPU, GPU, and NPU operating points on smartphones, and Yuan et al. control GPU frequency online in a datacenter serving system for agentic workloads.[^caiYourNPUReady2026][^yuanKAIROSStatefulContextAware2026]

## How it works

- **Datacenter GPU serving.** DVFS-based runtimes tune GPU frequency online using signals such as workload slack, phase behavior, or workload state.[^yuanKAIROSStatefulContextAware2026] Because lowering frequency slows inference down, any such approach must balance power savings against performance target SLOs.[^yuanKAIROSStatefulContextAware2026] Yuan et al. contrast DVFS with static power caps, and argue that static policies fit agentic workloads poorly because agent context evolves dynamically across turns.[^yuanKAIROSStatefulContextAware2026]
- **Mobile SoC.** On the phones Cai et al. measure, two CPU clusters expose different frequency ranges. The study uses 21 valid CPU frequency-level combinations and 15 GPU frequency levels. NPU frequency states are configured at the governor level and include disable, min, svs2, svs, svs\_plus, nom, nom\_plus, turbo, turbo\_plus, turbo\_l2, turbo\_l3, and max.[^caiYourNPUReady2026]
- **NPU scaling is two-dimensional.** DVFS on CPU and GPU can be analyzed along a single frequency axis, while NPU scaling depends on the joint configuration of NPU core and bus voltage corners.[^caiYourNPUReady2026]

## Variants

- **Backend-local DVFS.** Scaling the frequency of the processor that runs the model (CPU backend, GPU backend, or NPU).[^caiYourNPUReady2026]
- **Cross-backend DVFS.** Scaling the host CPU frequency while the GPU or NPU backend runs the model.[^caiYourNPUReady2026]
- **Fixed frequency.** A fixed GPU frequency of 810 MHz is one of the baselines in Yuan et al.[^yuanKAIROSStatefulContextAware2026]
- **Context-aware frequency control (KAIROS).** The controller picks a GPU frequency level from the aggregate context usage $U_k$ of ongoing agents against the instance's token capacity $U_{\max}$, with $\alpha=0.75$ in practice, and overrides it with the maximum level when an agent's throughput falls below the SLO target.[^yuanKAIROSStatefulContextAware2026]

## Papers using it

### Is Your NPU Ready for LLMs? (mobile measurement)

[Cai et al.](../papers/caiYourNPUReady2026.md) report DVFS as "Finding 8: Energy-Unfriendly DVFS": across CPU, GPU, and NPU sweeps, the default settings are often not energy-optimal.[^caiYourNPUReady2026] The CPU and GPU sweeps run in [llama.cpp](../methods/llama-cpp.md) for Llama 3.2 1B decode with 256 tokens.[^caiYourNPUReady2026]

| Setting | Result |
|---|---|
| CPU DVFS, CPU backend | Frequency levels 8–9 reduce energy by roughly 50% relative to the default, with about a 13% drop in throughput. Level 20 to 14: 20% throughput loss and 14% more energy. Level 20 to 8: 20% lower throughput and 42% less energy |
| GPU DVFS, GPU backend | At level 16, throughput is 27% lower than the default with a modest energy reduction. Level 16 to 13: an additional 30% throughput drop with limited further energy savings |
| CPU frequency while running the GPU backend | At CPU frequency level 9, throughput increases by 13% relative to the default and energy decreases by 51%. Mid-range CPU levels (5–10) can outperform higher levels (20–26) in both throughput and energy |
| CPU frequency while running the NPU backend | Fixed lower CPU levels vs default DVFS: largest energy reduction 23.7% in prefill and 39.7% in decode |

All rows: [^caiYourNPUReady2026]

NPU voltage-corner sweep, energy-optimal point relative to (max, max):[^caiYourNPUReady2026]

| Case | Energy-optimal (core, bus) | Energy | Throughput |
|---|---|---|---|
| Qwen prefill | (turbo\_l2, turbo\_l3) | lower by 2.0% | reduced by 6.5% |
| Qwen decode | (turbo\_plus, nom) | saves 22.1% | drops by 25.5% |
| Llama prefill | (nom, turbo\_l2) | saves 23.7% | 31.3% reduction |
| Llama decode | (turbo\_plus, turbo\_l3) | saves 19.1% | 11.7% drop |

- None of the NPU energy-optimal points falls into min/svs/svs2. They cluster around nom to turbo\_plus for the core and nom to turbo\_l3 for the bus.[^caiYourNPUReady2026]
- The paper's best-practice NPU configuration fixes the CPU frequency at the lowest level, together with an RPC polling interval of 20µs and an NPU sleep latency of 65535µs. The combination cuts prefill energy by 53.6% with a throughput gain of 0.8%, and decode energy by 54.8% with a 13.4% throughput loss.[^caiYourNPUReady2026]
- The introduction states that fine-grained DVFS tuning can recover approximately 50% of wasted energy on certain backends.[^caiYourNPUReady2026]

### KAIROS (agentic serving on GPUs)

[KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md) states that prior DVFS-based runtimes are designed for stateless LLM serving, and that prior work studied the frequency-performance trade-off only in single-turn LLM serving.[^yuanKAIROSStatefulContextAware2026]

- **Characterization.** With a fixed arrival rate of 0.08 agents/s, reducing GPU frequency from 1680 MHz to 900 MHz lowers energy and power by about 30% with little impact on throughput or latency. Below 900 MHz the trend reverses, with sharply higher energy, lower throughput, and longer time per LLM request.[^yuanKAIROSStatefulContextAware2026]
- **Thrashing.** The reversal occurs because slower execution lets the total context footprint of concurrent agents grow until it exceeds GPU memory capacity. Cached context ([KV cache](../methods/kv-cache.md)) is then evicted and previously processed tokens must be recomputed. At 1185 MHz memory pressure stays stable; at 660 MHz the system enters the thrashing regime.[^yuanKAIROSStatefulContextAware2026]
- **Results.** KAIROS reduces average GPU power by 27% (up to 39.8%) for a single serving instance and by 46.3% for multi-instance serving, while maintaining a per-agent SLO of P5 throughput 20 tokens/s.[^yuanKAIROSStatefulContextAware2026]
- **Against fixed frequency.** The fixed 810 MHz baseline achieves slightly larger power savings than KAIROS at the cost of significantly degraded SLO attainment.[^yuanKAIROSStatefulContextAware2026]
- **Across models** (SWE-Bench Verified, 0.06 jobs/s): power falls from 367.9 W to 240.9 W on Qwen3-Coder-30B (34.5%) and from 370.8 W to 263.8 W on Ministral-3-14B (28.9%).[^yuanKAIROSStatefulContextAware2026]
- **SLO sensitivity.** As the SLO increases from 20 to 45 tokens/s, power savings drop from 32.9% to 6.3% relative to the baseline.[^yuanKAIROSStatefulContextAware2026]
- The serving system is [vLLM](../methods/vllm.md) on NVIDIA H100 GPUs, and frequency and power control and measurement use Zeus.[^yuanKAIROSStatefulContextAware2026]

## Strengths & Limitations

- Both papers find unused energy savings: roughly 50% against the default DVFS setting on a mobile CPU backend, and about 30% from lowering GPU frequency from 1680 MHz to 900 MHz in agentic serving.[^caiYourNPUReady2026][^yuanKAIROSStatefulContextAware2026]
- Lower is not always better. On the mobile CPU, going from level 20 to 14 loses 20% throughput and uses 14% more energy.[^caiYourNPUReady2026] On the NPU, aggressive under-clocking is not the right policy.[^caiYourNPUReady2026] In agentic serving, frequencies below 900 MHz raise energy because of context thrashing.[^yuanKAIROSStatefulContextAware2026]
- The effect depends on which processor is on the critical path. NPU- and GPU-bound workloads frequently tolerate substantial CPU downclocking, while GPU downclocking on the GPU backend significantly reduces throughput for a limited energy benefit.[^caiYourNPUReady2026]
- On phones, some frequency points cannot be fixed or maintained because of vendor-enforced DVFS behavior.[^caiYourNPUReady2026]
- In stateful serving, frequency control is coupled with memory: Yuan et al. pair it with concurrency control to avoid thrashing.[^yuanKAIROSStatefulContextAware2026]

## Related

- [llama.cpp](../methods/llama-cpp.md)
- [KV cache](../methods/kv-cache.md), [vLLM](../methods/vllm.md)

[^caiYourNPUReady2026]: Cai et al. 2026
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
