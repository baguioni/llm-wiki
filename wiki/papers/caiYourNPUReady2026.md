---
type: Paper
title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
description: Cross-layer measurement study of mobile LLM inference across five frameworks and CPU, GPU, and NPU backends, with a backend-level energy profiler (PowerBench) and an energy-oriented NPU configuration.
tags: [mobile-llm, on-device-inference, npu, energy-efficiency, measurement-study, dvfs, quantization, mobile-specedge]
collections: [mobile-specedge]
authors: [Guanyu Cai, Ruiming Tian, Lang Yang, Zhouhong Ren, Jinliang Yuan, Lingkun Li, Jiliang Wang]
year: 2026
doi: 10.48550/arXiv.2607.05475
arxiv: "2607.05475"
arxiv_version: 2607.05475v1
sources:
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
---

# Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference

Text source: arXiv HTML, version `2607.05475v1`.

## Summary

The paper is a measurement study of LLM inference on smartphones. It covers five frameworks ([llama.cpp](../methods/llama-cpp.md), [MNN](../methods/mnn.md), [GENIE](../methods/genie.md), [MLLM](../methods/mllm.md), [MLC-LLM](../methods/mlc-llm.md)), three backends (CPU, GPU, NPU), and resource scheduling policies such as [DVFS](../methods/dvfs.md).[^caiYourNPUReady2026] The authors build [PowerBench](../methods/powerbench.md), an instrumentation library that attributes energy to the SoC, CPU, GPU, and NPU separately.[^caiYourNPUReady2026] The benchmark spans more than 400 configurations across models, devices, frameworks, backends, and inference stages.[^caiYourNPUReady2026]

It reports three findings. Framework gaps are amplified on NPUs. NPUs are best for prefill while CPUs are usually best for decode (a "phase split"). Default scheduling settings (thread configuration, NPU sleep latency, CPU polling interval, DVFS) waste energy.[^caiYourNPUReady2026] A tuned NPU configuration is estimated to reduce energy consumption by up to 54.8% across three datasets.[^caiYourNPUReady2026]

## Contributions

- A measurement study across five frameworks and three hardware backends that includes NPU-based deployment, which the paper says prior measurement studies do not cover.[^caiYourNPUReady2026]
- A lightweight, framework-agnostic instrumentation suite for power and throughput measurement at the compute-unit level (CPU, GPU, NPU).[^caiYourNPUReady2026]
- Findings on kernel scalability, activation quantization, and backend coordination, and a proposed phase-aware co-design of scheduling and backend selection.[^caiYourNPUReady2026]

## Method

### Testbed

| Device | Year | SoC | CPU | GPU | NPU | DRAM |
|---|---|---|---|---|---|---|
| Xiaomi 17 | 2025 | SM8850 | 2×4.6 GHz + 6×3.62 GHz | 1.20 GHz | V81 | 16 GB |
| OnePlus 15 | 2025 | SM8850 | 2×4.6 GHz + 6×3.62 GHz | 1.20 GHz | V81 | 16 GB |
| Xiaomi 15 | 2024 | SM8750 | 2×4.32 GHz + 6×3.53 GHz | 1.10 GHz | V79 | 16 GB |
| Xiaomi 14 | 2023 | SM8650 | 1×3.3 GHz + 3×3.15 GHz + 2×2.96 GHz + 2×2.27 GHz | 1.00 GHz | V75 | 16 GB |

All rows: [^caiYourNPUReady2026]

- Models: Llama 3.2-1B, Llama 3.2-3B, Qwen 2.5-1.5B, Qwen 2.5-7B, and Phi 3.5-3.8B in quantized formats.[^caiYourNPUReady2026]
- Quantization: 4-bit weight-only (w4) unless otherwise specified. All MLLM deployments use 4-bit weight and 16-bit activation quantization (w4a16). Within GENIE only Qwen 2.5-7B uses w4a16.[^caiYourNPUReady2026]

### Frameworks (Table 3)

| Framework | Maintainer | CPU | GPU | NPU | Version |
|---|---|---|---|---|---|
| llama.cpp | Community | targeted | targeted | targeted, custom kernel (open source) | eadc418 |
| MNN | Alibaba | targeted | targeted | targeted, QNN kernel (closed source) | 510ac8f |
| MLC-LLM | Community | supported | targeted | unsupported | 8f49ea6 |
| MLLM | Community | supported | supported | targeted, QNN kernel (closed source) | 10d3d6a |
| GENIE | Qualcomm | supported | unsupported | targeted, QNN kernel (closed source) | 2.39.0 |

All rows: [^caiYourNPUReady2026]

GENIE, MNN, and MLLM delegate NPU execution to Qualcomm's [QNN](../methods/qnn.md) stack and inherit the same vendor kernels, while llama.cpp implements its own operators.[^caiYourNPUReady2026]

### Measurement

- **Throughput.** Prefill throughput is the prompt length divided by the time from inference start to the first output token. Decode throughput is the number of generated tokens divided by the time between the first and the last output token. Each framework is instrumented to control prompt token injection and end-of-sequence token replacement so that prompt and generation lengths are the same.[^caiYourNPUReady2026]
- **Energy.** Four per-token metrics in µJ/token: SoC, CPU, GPU, and NPU. PowerBench is a header-only C++ library on top of the Qualcomm Power Telemetry (QPT) driver stack, which exposes cumulative energy counters through the Linux powercap sysfs interface. It records energy deltas through start()/stop() calls, and a background thread samples power traces.[^caiYourNPUReady2026]
- **Protocol.** Devices are cooled to below 28∘C before each experiment, run in airplane mode with the screen off, and background services are disabled. Each configuration has one warm-up run and at least three recorded trials, and the mean is reported.[^caiYourNPUReady2026]

### Background numbers (Table 2)

| Vendor | SoC | CPU FP32 (TFLOPS) | GPU FP32 (TFLOPS) | NPU INT8 (TOPS) |
|---|---|---|---|---|
| Qualcomm | 8 Elite Gen 5 | 0.49 | 3.68 | $>34$ |
| MediaTek | Dimensity 9500 | 0.40 | 5.27 | $>50$ |
| Apple | A19 Pro | 0.30 | 2.48 | $>35$ |

All rows: [^caiYourNPUReady2026]

## Experiments & Results

### Benchmark (Table 5, Qwen2.5-1.5B, 256 tokens)

Throughput in tokens/s on Xiaomi 17 / OnePlus 15 / Xiaomi 15 / Xiaomi 14. Energy in µJ/token on Xiaomi 17 / OnePlus 15. `–` means no value in the source. The other models (Qwen2.5-7B, Llama3.2-1B, Llama3.2-3B, and Phi-3.5-mini in Table 9) are in the raw file.[^caiYourNPUReady2026]

| Backend | Framework | Quant. | Prefill throughput | Prefill energy | Decode throughput | Decode energy |
|---|---|---|---|---|---|---|
| CPU | llama.cpp | w4 | 417.3 / 299.9 / 329.2 / 157.2 | 3.3e4 / 1.5e4 | 51.6 / 55.7 / 53.9 / 34.5 | 1.2e5 / 9.7e4 |
| CPU | MNN | w4 | 349.5 / 228.3 / 259.4 / 259.5 | 2.3e4 / 1.5e4 | 19.0 / 47.5 / 49.5 / 45.7 | 1.3e5 / 9.2e4 |
| GPU | llama.cpp | w4 | 569.7 / 754.8 / 680.9 / 365.7 | 1.0e4 / 1.1e4 | 38.8 / 50.3 / 48.6 / 31.8 | 1.1e5 / 1.4e5 |
| GPU | MNN | w4 | 392.2 / 434.1 / 406.1 / 272.5 | 8.6e3 / 1.7e4 | 39.1 / 12.3 / 45.8 / 26.2 | 9.4e4 / 9.9e4 |
| GPU | MLC-LLM | w4 | 24.3 / 42.4 / 45.9 / 141.8 | 5.7e4 / 5.0e4 | 24.6 / 19.6 / 29.9 / 16.8 | 1.3e5 / 1.3e5 |
| NPU | GENIE | w4 | 1213.0 / 1463.7 / 1219.2 / – | 6.8e3 / 5.6e3 | 23.1 / 23.0 / 20.7 / – | 4.3e5 / 3.2e5 |
| NPU | llama.cpp | w4 | 107.6 / 115.1 / 82.3 / 51.4 | 8.2e4 / 7.6e4 | 31.9 / 33.3 / 18.3 / 13.8 | 2.0e5 / 1.6e5 |
| NPU | MNN | w4 | 814.3 / 700.9 / 694.4 / 593.8 | 8.3e3 / 8.1e3 | 9.9 / 10.3 / 16.9 / 14.8 | 2.1e5 / 2.5e5 |
| NPU | MLLM | w4a16 | 904.5 / 966.8 / 814.6 / – | 3.2e3 / 4.1e3 | 34.0 / 34.3 / 32.7 / – | 7.5e4 / 8.7e4 |

All rows: [^caiYourNPUReady2026]

The paper states that GENIE's NPU decode energy can be roughly 2–4× higher than CPU/GPU alternatives.[^caiYourNPUReady2026]

### RQ1: framework gaps on NPU

| Finding | Evidence |
|---|---|
| 1. Offloading overhead | GENIE runs the full graph on the NPU. MNN keeps self-attention on the CPU and offloads the rest. GENIE achieves nearly 2× the throughput of MNN. Qwen2.5-1.5B breakdown: GENIE NPU Attention 44.79% and NPU others 55.21% of compute cycles; MNN CPU Attention 1.06% and NPU Plugins 98.94% of end-to-end latency |
| 2. Operator scaling | OnePlus 15, Qwen2.5-1.5B: GENIE 1463.7 tokens/s vs llama.cpp 115.1 tokens/s in NPU prefill, a 15× gap. MatMul sweep over output width $N$: comparable at $N\leq 4$; at $N=256$ QNN reduces MatMul cycles by $26.9\times$–$30.7\times$; at $N=1024$ the gap remains $28.9\times$–$48.0\times$ |
| 3. [Activation quantization](../methods/activation-quantization.md) | GENIE, W4 vs W4A16, Llama-3.2-1B and Llama-3.2-3B: throughput improves by $2.16\times$ and $2.58\times$ in prefill and by $2.63\times$ and $2.34\times$ in decode, and energy per token falls by $53.5\%$–$66.9\%$ |

All rows: [^caiYourNPUReady2026]

In Llama-3.2-3B, Conv2d, Eltwise\_Binary, and Softmax account for 86.6% of W4 cycles in prefill, and Conv2d and Eltwise\_Binary account for 82.2% of cycles in decode.[^caiYourNPUReady2026]

Perplexity on [WikiText-2](../datasets/wikitext-2.md), lower is better (Table 7):[^caiYourNPUReady2026]

| Model | PPL (W4) | PPL (W4A16) | Relative Δ PPL (%) |
|---|---|---|---|
| Llama-3.2-1B | 16.73 | 21.81 | +30.36% |
| Llama-3.2-3B | 11.50 | 11.62 | +1.04% |

### RQ2: backend and phase

- NPU decode throughput depends on context size, not on the number of generated tokens. As context grows from 16 to 4096 tokens, throughput drops from 61.6 to 47.0 tokens/s for Llama-3.2-1B and from 43.9 to 35.1 tokens/s for Qwen2.5-1.5B, i.e. by 23.8% and 20.0%. At a fixed context size, the curves for 15, 63, and 255 generated tokens nearly overlap.[^caiYourNPUReady2026]
- The paper attributes this to static-graph NPU execution: the NPU runs decode with shape-specialized static graphs and typically sets a large context size (e.g. 4096), so each step costs more.[^caiYourNPUReady2026]
- Across the four devices, CPU backends generally deliver the highest decode throughput, and GPU wins only in a few isolated cases. GPU is often a near-equivalent substitute for decode.[^caiYourNPUReady2026]

### RQ3: scheduling

| Knob | Sweep and default | Result |
|---|---|---|
| RPC polling interval | 5 to 65535 µs; default 9999 µs in GENIE and MLLM | Short intervals (5–20 µs) reduce total energy per token by $30.9\%$–$37.8\%$. Throughput changes by $-7.2\%$ to $+0.1\%$. The NPU energy component drops by $49.8\%$–$70.8\%$ |
| NPU sleep latency | 5 to 65535 µs; default 40 µs in GENIE and MLLM | Energy-optimal points are between 1280 and 65535 µs and reduce total energy per token by $44.6\%$–$50.9\%$. Throughput ranges from a $0.9\%$ drop to a $16.2\%$ increase. The NPU energy component falls by $66.7\%$–$100.0\%$ |
| CPU DVFS, CPU backend (llama.cpp, Llama 3.2 1B decode, 256 tokens) | 21 valid CPU frequency-level combinations | Frequency levels 8–9 reduce energy by roughly 50% relative to the default with about a 13% drop in throughput. Level 20 to 14: 20% throughput loss and 14% more energy. Level 20 to 8: 20% lower throughput and 42% less energy |
| GPU DVFS, GPU backend | 15 GPU frequency levels | At level 16 throughput is 27% lower than the default with a modest energy reduction. Level 16 to 13 costs an additional 30% throughput |
| CPU frequency while running the GPU backend | same CPU levels | At CPU frequency level 9, throughput increases by 13% relative to the default and energy decreases by 51% |
| CPU frequency while running the NPU backend (Qwen 1.5B, Xiaomi 17 and OnePlus 15) | fixed CPU levels vs default DVFS | Largest energy reduction 23.7% in prefill and 39.7% in decode |

All rows: [^caiYourNPUReady2026]

NPU voltage-corner sweep (core vcorner × bus vcorner), energy-optimal point relative to (max, max):[^caiYourNPUReady2026]

| Case | Energy-optimal (core, bus) | Energy | Throughput |
|---|---|---|---|
| Qwen prefill | (turbo\_l2, turbo\_l3) | lower by 2.0% | reduced by 6.5% |
| Qwen decode | (turbo\_plus, nom) | saves 22.1% | drops by 25.5% |
| Llama prefill | (nom, turbo\_l2) | saves 23.7% | 31.3% reduction |
| Llama decode | (turbo\_plus, turbo\_l3) | saves 19.1% | 11.7% drop |

Thread–core affinity (Qwen2.5-1.5B decode on Xiaomi 17): CPU and NPU backends are fastest when the thread count roughly matches the number of active cores, the NPU backend is best with the smallest CPU thread count, and the GPU backend loses throughput with too few threads.[^caiYourNPUReady2026] The introduction states that suboptimal thread-core affinity causes up to 35% performance variance, and that the host CPU can account for up to 30% of total system energy during NPU-accelerated inference.[^caiYourNPUReady2026]

### Best-practice configuration

NPU (GENIE): QNN with full-graph offloading, a computation graph with a context length suited to the workload, RPC polling interval 20µs, NPU sleep latency 65535µs, and CPU frequency fixed at the lowest level. This cuts prefill energy by 53.6% with a throughput gain of 0.8%, and cuts decode energy by 54.8% with a 13.4% throughput loss.[^caiYourNPUReady2026]

Estimated end-to-end impact (Table 8):[^caiYourNPUReady2026]

| Dataset | Latency | Energy |
|---|---|---|
| [MathQA](../datasets/mathqa.md) | 174187.8 → 201244.4 s (+15.5%) | 127774.4 → 57754.2 J (-54.8%) |
| [RoleBench](../datasets/rolebench.md) | 407485.2 → 469985.6 s (+15.3%) | 335279.9 → 152037.8 J (-54.7%) |
| [LongBench](../benchmarks/longbench.md) | 89531.2 → 88848.8 s (-0.8%) | 733648.2 → 340622.2 J (-53.6%) |

- llama.cpp CPU decode: tuning thread-core affinity, removing one mid core from the thread placement, and lowering the CPU frequency to Level 17 improves throughput by 1.5% and reduces energy consumption by 20.0%.[^caiYourNPUReady2026]
- GPU decode: setting the CPU frequency to Level 10 with thread-core affinity optimization improves throughput by 10.8% and reduces energy by 36.4%.[^caiYourNPUReady2026]

### Inconsistencies inside the paper

- The NPU framework gap is "up to $10\times$" in the abstract, "over $15\times$" in the introduction, and "a 15× gap" in Section 5.2.[^caiYourNPUReady2026]
- Section 5.2 gives OnePlus 15 Qwen2.5-1.5B NPU decode as 23.0 vs. 22.8 tokens/s for GENIE vs llama.cpp, while Table 5 lists llama.cpp NPU decode on OnePlus 15 as 33.3 tokens/s.[^caiYourNPUReady2026]
- The introduction compares GENIE at 1219.2 tokens/s with MNN at 700.9 tokens/s. In Table 5 these are the Xiaomi 15 value for GENIE and the OnePlus 15 value for MNN.[^caiYourNPUReady2026]
- The model is called Phi 3.5-3.8B in Section 3 and Phi-3.5-mini in Table 9.[^caiYourNPUReady2026]

## Limitations

- All four devices use Qualcomm Snapdragon SoCs (SM8650, SM8750, SM8850). No MediaTek or Apple device is measured.[^caiYourNPUReady2026]
- The dataset-level results in Table 8 are estimates, not measured end-to-end runs.[^caiYourNPUReady2026]
- The energy-oriented NPU configuration raises end-to-end latency by 15.1%–15.5% on MathQA and RoleBench.[^caiYourNPUReady2026]
- Activation quantization raises perplexity by 30.36% on Llama-3.2-1B, so its gains hold only when the model tolerates it.[^caiYourNPUReady2026]
- Some frequency points cannot be fixed or maintained because of vendor-enforced DVFS behavior.[^caiYourNPUReady2026]
- Table 5 and Table 9 have missing cells for several framework, device, and model combinations.[^caiYourNPUReady2026]
- Multi-graph switching on NPU, phase-aware pipelines (prefill on NPU, decode on CPU), and phase- and model-aware NPU frequency scaling are proposed as future directions and are not built or evaluated.[^caiYourNPUReady2026]
- The paper has no dedicated limitations section.

## Related

- Proposed: [PowerBench](../methods/powerbench.md)
- Frameworks measured: [llama.cpp](../methods/llama-cpp.md), [MNN](../methods/mnn.md), [MLC-LLM](../methods/mlc-llm.md), [MLLM](../methods/mllm.md), [GENIE](../methods/genie.md), [QNN](../methods/qnn.md)
- Techniques studied: [Activation quantization](../methods/activation-quantization.md), [DVFS](../methods/dvfs.md), [KV cache](../methods/kv-cache.md)
- Datasets and benchmarks: [WikiText-2](../datasets/wikitext-2.md), [MathQA](../datasets/mathqa.md), [RoleBench](../datasets/rolebench.md), [LongBench](../benchmarks/longbench.md)

[^caiYourNPUReady2026]: Cai et al. 2026
