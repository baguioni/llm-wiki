---
type: Method
title: llama.cpp
description: An open-source, community-maintained LLM inference framework in C/C++ that the wiki's papers measure on mobile CPU, GPU, and NPU backends and extend for on-device diffusion LLM inference.
tags: [inference-framework, on-device-inference, mobile-llm, npu]
sources:
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
  - id: wangEfficientOnDeviceDiffusion2026
    resource: zotero://select/items/@wangEfficientOnDeviceDiffusion2026
    title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
---

# llama.cpp

## Overview

Wang et al. cite llama.cpp as "llama.cpp: llm inference in c/c++" by ggml-org.[^wangEfficientOnDeviceDiffusion2026] Cai et al. list it as a community-maintained mobile inference framework that targets the CPU, GPU, and NPU backends, and say that it has the most active open-source community among the five frameworks they study.[^caiYourNPUReady2026]

## How it works

The wiki's papers describe only its NPU path:

- For NPU execution, llama.cpp follows a custom-kernel path: it implements operators at a lower level in open source. GENIE, MNN, and MLLM instead delegate execution to Qualcomm's QNN-based stack and inherit the same vendor-provided kernels.[^caiYourNPUReady2026]
- The custom-kernel approach provides greater flexibility and control but demands substantially higher engineering effort.[^caiYourNPUReady2026]

## Variants

- **llada.cpp.** An end-to-end framework for block-wise diffusion LLM inference built on llama.cpp, extending it with over 12K lines of code and targeting Qualcomm Hexagon NPUs. Its model converter extends the GGUF pipeline, and its Android host runtime adds a GGML Hexagon backend.[^wangEfficientOnDeviceDiffusion2026]
- **llama.cpp-npu.** Wang et al. describe it as a system that reverse-engineers Hexagon HMX execution and builds a mobile-NPU path for test-time scaling with hardware-aware tile quantization and LUT-based vector kernels.[^wangEfficientOnDeviceDiffusion2026]

## Papers using it

### Is Your NPU Ready for LLMs? (measured framework)

[Cai et al.](../papers/caiYourNPUReady2026.md) measure llama.cpp at version eadc418 on four smartphones.[^caiYourNPUReady2026]

Qwen2.5-1.5B, w4 quantization, 256 tokens (Table 5). Throughput in tokens/s on Xiaomi 17 / OnePlus 15 / Xiaomi 15 / Xiaomi 14. Energy in µJ/token on Xiaomi 17 / OnePlus 15:[^caiYourNPUReady2026]

| Backend | Prefill throughput | Prefill energy | Decode throughput | Decode energy |
|---|---|---|---|---|
| CPU | 417.3 / 299.9 / 329.2 / 157.2 | 3.3e4 / 1.5e4 | 51.6 / 55.7 / 53.9 / 34.5 | 1.2e5 / 9.7e4 |
| GPU | 569.7 / 754.8 / 680.9 / 365.7 | 1.0e4 / 1.1e4 | 38.8 / 50.3 / 48.6 / 31.8 | 1.1e5 / 1.4e5 |
| NPU | 107.6 / 115.1 / 82.3 / 51.4 | 8.2e4 / 7.6e4 | 31.9 / 33.3 / 18.3 / 13.8 | 2.0e5 / 1.6e5 |

- **NPU prefill gap.** On OnePlus 15 with Qwen2.5-1.5B, GENIE reaches 1463.7 tokens/s in NPU prefill and llama.cpp reaches 115.1 tokens/s, a 15$\times$ gap.[^caiYourNPUReady2026]
- **MatMul scaling.** In a sweep over the MatMul output width $N$, llama.cpp is comparable to QNN at decode-like sizes ($N\leq 4$). At $N=256$ QNN reduces MatMul cycles by $26.9\times$–$30.7\times$, and at $N=1024$ the gap remains $28.9\times$–$48.0\times$.[^caiYourNPUReady2026] The paper concludes that large-$N$ operator optimization is the bottleneck in open-source NPU paths.[^caiYourNPUReady2026]
- **CPU decode.** On OnePlus 15 with Qwen2.5-1.5B decode, llama.cpp on CPU reaches 55.7 tokens/s, compared with 23.0 tokens/s for GENIE on NPU.[^caiYourNPUReady2026]
- **Frequency scaling.** The paper's [DVFS](../methods/dvfs.md) sweeps run in llama.cpp for Llama 3.2 1B decode with 256 tokens.[^caiYourNPUReady2026]
- **Tuned configuration.** Tuning thread-core affinity, removing one mid core from the thread placement, and lowering the CPU frequency to Level 17 improves llama.cpp CPU decode throughput by 1.5% and reduces energy consumption by 20.0%.[^caiYourNPUReady2026]

### Efficient On-Device Diffusion LLM Inference with Mobile NPU (base framework)

[Wang et al.](../papers/wangEfficientOnDeviceDiffusion2026.md) implement llada.cpp on top of llama.cpp.[^wangEfficientOnDeviceDiffusion2026]

## Strengths & Limitations

- Its NPU operators are open source and give flexibility and control.[^caiYourNPUReady2026]
- Its NPU MatMul does not scale to large token-parallel widths as QNN's does, so NPU prefill is far slower than in QNN-based frameworks, while decode stays competitive.[^caiYourNPUReady2026]

# Contradictions

**llama.cpp NPU decode throughput on OnePlus 15, Qwen2.5-1.5B, within Cai et al.** Section 5.2 says GENIE and llama.cpp have nearly identical decode throughput (23.0 vs. 22.8 tokens/s), and the introduction says both are at $\sim$ 23 tokens/s. Table 5 lists llama.cpp NPU decode on OnePlus 15 as 33.3 tokens/s and GENIE as 23.0 tokens/s.[^caiYourNPUReady2026] The paper does not explain the difference.

## Related

- [DVFS](../methods/dvfs.md)
- [KV cache](../methods/kv-cache.md)

[^caiYourNPUReady2026]: Cai et al. 2026
[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
