---
type: Paper
title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
description: Open-source framework for training EAGLE-3 draft models that decouples the target model (run on SGLang) from the draft model (trained with ZeRO Stage 2), released with the SpecBundle suite of draft models.
tags: [speculative-decoding, draft-model-training, eagle-3, training-framework, training-time-test, mobile-specedge]
collections: ["mobile-specedge"]
authors: [Shenggui Li, Chao Wang, Yikai Zhu, Yubo Wang, Fan Yin, Shuai Shi, Yefei Chen, Xiaomin Dong, Qiaoling Chen, Jin Pan, Ji Li, Laixin Xie, Yineng Zhang, Lei Yu, Yonggang Wen, Ivor Tsang, Tianwei Zhang]
doi: 10.48550/arXiv.2603.18567
arxiv: "2603.18567"
arxiv_version: 2603.18567v1
code: https://github.com/sgl-project/SpecForge
sources:
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
---

# SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding

Text source: arXiv HTML, version `2603.18567v1`.

## Summary

[Speculative decoding](../methods/speculative-decoding.md) uses a lightweight draft model to propose several tokens that the target model verifies in one forward pass.[^liSpecForgeFlexibleEfficient2026] The paper names three causes that keep it underused in practice, especially for [EAGLE-3](../methods/eagle-3.md): limited availability of draft models, poor performance of open-source draft models, and a lack of robust training tools.[^liSpecForgeFlexibleEfficient2026]

[SpecForge](../methods/specforge.md) is an open-source, production-oriented framework for training speculative decoding draft models with full support for EAGLE-3.[^liSpecForgeFlexibleEfficient2026] It combines target-draft decoupling, hybrid parallelism, optimized training kernels, and integration with the [SGLang](../methods/sglang.md) inference engine.[^liSpecForgeFlexibleEfficient2026] The abstract reports up to 9.9× faster EAGLE-3 training for Qwen3-235B-A22B; Table 1 lists the same case as 9.99×.[^liSpecForgeFlexibleEfficient2026]

The authors also release [SpecBundle](../methods/specbundle.md), a suite of EAGLE-3 draft models trained with SpecForge for mainstream open-source LLMs. The abstract reports up to 4.48× end-to-end inference speedup on SGLang.[^liSpecForgeFlexibleEfficient2026]

## Contributions

- SpecForge, a training framework for speculative decoding that implements hybrid parallelism through target-draft decoupling and training-time test attention optimization.[^liSpecForgeFlexibleEfficient2026]
- SpecBundle, a collection of draft models covering mainstream open-source LLM families, with up to 1.3× speedup over existing open checkpoints (contribution list; Section 6.1 states 1.35×).[^liSpecForgeFlexibleEfficient2026]
- A systematic study of training recipes and design choices: data regeneration, training-time test length, and draft model architecture.[^liSpecForgeFlexibleEfficient2026]

## Method

### Motivation

- Existing open-source EAGLE-3 training implementations treat the target and draft model as one unified model and wrap both in fully sharded data parallelism (FSDP).[^liSpecForgeFlexibleEfficient2026]
- The first training stage runs the target model over the whole input sequence to produce hidden states, which is equivalent to the prefill phase of LLM inference. Existing training frameworks use naive model implementations (self-written or imported from Hugging Face) that lack efficient attention kernels, optimized memory management, and CUDA Graph.[^liSpecForgeFlexibleEfficient2026]
- The authors reproduced EAGLE-3 training for LLaMA-3.1-Instruct on [ShareGPT](../datasets/sharegpt.md) (120K conversations) and [UltraChat](../datasets/ultrachat.md) (200K conversations) and obtained an acceptance length of 2.82 on Math500. Training the same draft model on the Perfect-Blend dataset (1.4M conversations) raised the acceptance length to 3.48, corresponding to an additional 1.17× inference speedup.[^liSpecForgeFlexibleEfficient2026]

### Target-draft decoupling and hybrid parallelism

- The target model is large, frozen, and inference-dominated; the draft model is lightweight and frequently updated. SpecForge gives each its own execution backend and parallelization strategy.[^liSpecForgeFlexibleEfficient2026]
- **Draft model.** The draft model is typically only 3–5% the size of the target model. SpecForge shards only the optimizer states and gradients, which is equivalent to ZeRO Stage 2 in DeepSpeed.[^liSpecForgeFlexibleEfficient2026]
- **Target model.** SpecForge uses the model runner of SGLang as the inference engine. This reuses SGLang's tensor parallelism, expert parallelism, and pipeline parallelism, and kernels such as FlashAttention and FlashInfer for the prefill phase. Piecewise CUDA Graph in SGLang fuses non-attention modules into a single kernel to reduce kernel launch time.[^liSpecForgeFlexibleEfficient2026]
- The two models can be co-located on the same GPU or disaggregated on distinct GPUs. The experiments use the co-located setting.[^liSpecForgeFlexibleEfficient2026]
- Three target-model backends are supported: Hugging Face, SGLang, and Custom (models implemented manually by the authors' team).[^liSpecForgeFlexibleEfficient2026]

### Computation optimization for training-time test

[Training-Time Test (TTT)](../methods/training-time-test.md) simulates multiple steps of autoregressive token generation during training. At each TTT step the model attends to the original training sequence as prefix plus the tokens generated in previous steps.[^liSpecForgeFlexibleEfficient2026] TTT with a step length of 7 incurs substantial GPU memory consumption.[^liSpecForgeFlexibleEfficient2026]

- **Sparse tree attention.** The naive implementation materializes the attention logits as intermediate activations. Profiling shows that stored attention logits account for 80% of the total activation memory. SpecForge computes attention with FlexAttention, which streams the computation in a FlashAttention style and uses a *BlockMask* that precomputes which blocks can be skipped, partially computed, or fully computed. At each TTT step SpecForge stores the newly generated keys and values in the KV cache and builds a BlockMask as the OR of a causal mask and a suffix mask (Algorithm 2).[^liSpecForgeFlexibleEfficient2026]
- **Memory-efficient gradient computation.** A custom Triton kernel implements the backward pass of the masked softmax loss and overwrites the logits tensor with the gradient with respect to the logits, so no separate gradient buffer is allocated. The memory reduction ranges from 30–40%, depending on the context length and the draft model's vocabulary size.[^liSpecForgeFlexibleEfficient2026]

### SpecBundle training recipe

- Dataset: [Open-PerfectBlend](../datasets/perfectblend.md), 1.4M conversations across the chat, math, coding, and instruction-following domains.[^liSpecForgeFlexibleEfficient2026]
- The assistant responses are regenerated with the target model at temperature 0.8, and the draft model is trained from scratch on the regenerated dataset.[^liSpecForgeFlexibleEfficient2026]
- Training runs for 2 epochs at learning rate 1e-4 with a cosine annealing scheduler.[^liSpecForgeFlexibleEfficient2026]

## Experiments & Results

### Training throughput (Table 1)

Setup: a cluster of eight NVIDIA H200 GPUs, sequence length 4096, batch size adjusted per method to maximize throughput under GPU memory constraints. The baseline ("EAGLE") is the official SafeAILab implementation released with the EAGLE3 paper. SpecForge enables tensor parallelism (TP), FlashAttention kernels, and CUDA Graphs.[^liSpecForgeFlexibleEfficient2026]

| Target model | Framework | Target model parallelism | Draft model parallelism | Max batch size | Step time (s) | Throughput (tokens/s) | Speedup |
|---|---|---|---|---|---|---|---|
| Llama3.1-8B | EAGLE | ZeRO 2 | ZeRO 2 | 16 | 1.04 | 63015.4 | 1 |
| Llama3.1-8B | SpecForge | TP=1 | ZeRO 2 | 64 | 2.07 | 126639.6 | 2.01 |
| Llama3.3-70B | EAGLE | ZeRO 2 | ZeRO 2 | 16 | OOM | - | - |
| Llama3.3-70B | EAGLE | ZeRO 3 | ZeRO 3 | 8 | 2.21 | 14827.1 | 1 |
| Llama3.3-70B | SpecForge | TP=4 | ZeRO 2 | 16 | 3.18 | 20608.8 | 1.39 |
| Qwen3-30B-A3B | EAGLE | ZeRO 2 | ZeRO 2 | 8 | 1.12 | 29257.1 | 1 |
| Qwen3-30B-A3B | EAGLE | ZeRO 3 | ZeRO 3 | 8 | 5.07 | 6463.1 | 0.2 |
| Qwen3-30B-A3B | SpecForge | TP=4 | ZeRO 2 | 16 | 0.52 | 126030.8 | 4.31 |
| Qwen3-235B-A22B | EAGLE | ZeRO 2 | ZeRO 2 | 8 | OOM | - | - |
| Qwen3-235B-A22B | EAGLE | ZeRO 3 | ZeRO 3 | 8 | 11.2 | 2025.7 | 1 |
| Qwen3-235B-A22B | SpecForge | TP=8 | ZeRO 2 | 8 | 1.62 | 20227.2 | 9.99 |

All rows: [^liSpecForgeFlexibleEfficient2026]

- The paper attributes the weak baseline to two factors: under ZeRO Stage 2 the frozen target parameters stay fully replicated on each device, and under ZeRO Stage 3 frequent all-gather operations during target-model inference add communication overhead.[^liSpecForgeFlexibleEfficient2026]
- On LLaMA-3.1-8B, where neither system parallelizes the target model, SpecForge still attains a 2.01× speedup, which the paper attributes to SGLang's optimized prefill execution.[^liSpecForgeFlexibleEfficient2026]
- Target model backends (Figure 3): the SGLang backend achieves speedups of up to 6.8× over the Hugging Face and custom backends. The Hugging Face implementation encounters runtime errors on large-scale MoE models.[^liSpecForgeFlexibleEfficient2026]
- Attention kernel micro-benchmark (Figure 4, TTT length 7, final TTT step, single NVIDIA H200 GPU, compared with a native SDPA-based implementation): at sequence length 4096 the optimized attention reduces execution time by 62.1% and peak memory usage by 93.5%. The gap widens as the sequence length increases.[^liSpecForgeFlexibleEfficient2026]

### SpecBundle inference (Tables 2 and 3)

Setup: SGLang as the inference engine on NVIDIA H200 GPUs. Concurrent requests are fixed to 8 for LLaMA-3.1-8B and 16 for larger models, with tensor parallelism set by target model scale. Configurations (number of speculative steps, top-k, number of draft tokens) tested: (3, 1, 4), (5, 1, 6), (5, 3, 6), (7, 1, 8), (7, 4, 8); the highest throughput among them is reported. "-" is the target model alone. "Existing" is an existing open-source draft model, from the EAGLE3 authors or the LMSYS team.[^liSpecForgeFlexibleEfficient2026] Evaluation sets: [MT-Bench](../datasets/mt-bench.md), [GPQA](../datasets/gpqa.md), [FinanceQA](../datasets/financeqa.md), [LiveCodeBench](../datasets/livecodebench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Math500](../datasets/math-500.md).[^liSpecForgeFlexibleEfficient2026] The tables do not state the unit of the Throughput columns.

Each cell is Throughput / Speedup. Table 2, general benchmarks:[^liSpecForgeFlexibleEfficient2026]

| Target model | Draft model | #GPUs | MTBench | GPQA | FinanceQA |
|---|---|---|---|---|---|
| Llama-3.1-8B | - | 1 | 190.0 / 1 | 190.5 / 1 | 185.7 / 1 |
| Llama-3.1-8B | Existing | 1 | 454.7 / 2.39 | 438.1 / 2.30 | 237.2 / 1.27 |
| Llama-3.1-8B | SpecBundle | 1 | 450.0 / 2.37 | 514.2 / 2.70 | 258.6 / 1.39 |
| Llama-3.3-70B | - | 4 | 540.5 / 1 | 575.7 / 1 | 512.6 / 1 |
| Llama-3.3-70B | Existing | 4 | 1272.7 / 2.35 | 1049.0 / 1.82 | 981.7 / 1.92 |
| Llama-3.3-70B | SpecBundle | 4 | 1253.0 / 2.31 | 1405.1 / 2.44 | 1022.7 / 2.00 |
| Llama-4-Scout | - | 8 | 502.1 / 1 | 541.0 / 1 | 288.9 / 1 |
| Llama-4-Scout | Existing | 8 | 1253.0 / 2.50 | 1405.1 / 2.60 | 1022.7 / 3.54 |
| Llama-4-Scout | SpecBundle | 8 | 1312.4 / 2.61 | 1502.2 / 2.78 | 1189.6 / 4.12 |
| Qwen-30B-A3B | - | 4 | 1341.3 / 1 | 1410.4 / 1 | 1320.1 / 1 |
| Qwen-30B-A3B | SpecBundle | 4 | 2086.1 / 1.55 | 2341.3 / 1.66 | 1779.0 / 1.35 |
| Qwen-235B-A22B | - | 8 | 529.9 / 1 | 563.2 / 1 | 539.5 / 1 |
| Qwen-235B-A22B | Existing | 8 | 642.7 / 1.21 | 716.7 / 1.27 | 689.4 / 1.28 |
| Qwen-235B-A22B | SpecBundle | 8 | 814.5 / 1.54 | 826.5 / 1.47 | 889.0 / 1.65 |
| Ling-Flash-V2 | - | 8 | 728.5 / 1 | 794.1 / 1 | 747.7 / 1 |
| Ling-Flash-V2 | SpecBundle | 8 | 1022.6 / 1.40 | 1185.7 / 1.49 | 863.9 / 1.16 |
| Kimi-K2 | - | 8 | 430.9 / 1 | 505.4 / 1 | 433.4 / 1 |
| Kimi-K2 | SpecBundle | 8 | 533.8 / 1.24 | 811.4 / 1.61 | 660.0 / 1.52 |

Table 3, math and coding benchmarks:[^liSpecForgeFlexibleEfficient2026]

| Target model | Draft model | #GPUs | LiveCodeBench | HumanEval | GSM8K | Math500 |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | - | 1 | 189.7 / 1 | 190.9 / 1 | 181.8 / 1 | 191.0 / 1 |
| Llama-3.1-8B | Existing | 1 | 398.4 / 2.10 | 480.3 / 2.52 | 228.6 / 1.26 | 422.4 / 2.21 |
| Llama-3.1-8B | SpecBundle | 1 | 516.9 / 2.72 | 571.5 / 2.99 | 329.7 / 1.81 | 638.0 / 3.34 |
| Llama-3.3-70B | - | 4 | 560.9 / 1 | 561.0 / 1 | 453.2 / 1 | 567.4 / 1 |
| Llama-3.3-70B | Existing | 4 | 1303.4 / 2.32 | 1282.8 / 2.29 | 521.5 / 1.15 | 1122.2 / 1.98 |
| Llama-3.3-70B | SpecBundle | 4 | 1459.4 / 2.60 | 1506.0 / 2.68 | 722.0 / 1.59 | 1524.9 / 2.69 |
| Llama-4-Scout | - | 8 | 484.3 / 1 | 631.9 / 1 | 455.9 / 1 | 561.8 / 1 |
| Llama-4-Scout | Existing | 8 | 1601.3 / 3.31 | 1556.5 / 2.46 | 816.6 / 1.79 | 1479.0 / 2.63 |
| Llama-4-Scout | SpecBundle | 8 | 2170.2 / 4.48 | 1944.8 / 3.08 | 971.9 / 2.13 | 2110.3 / 3.76 |
| Qwen-30B-A3B | - | 4 | 1492.6 / 1 | 1366.6 / 1 | 1071.3 / 1 | 1469.0 / 1 |
| Qwen-30B-A3B | SpecBundle | 4 | 3413.0 / 2.29 | 3070.0 / 2.25 | 1499.6 / 1.40 | 3636.1 / 1.48 |
| Qwen-235B-A22B | - | 8 | 598.2 / 1 | 553.1 / 1 | 469.1 / 1 | 587.4 / 1 |
| Qwen-235B-A22B | Existing | 8 | 803.8 / 1.34 | 889.9 / 1.61 | 697.0 / 1.49 | 821.8 / 1.39 |
| Qwen-235B-A22B | SpecBundle | 8 | 1155.7 / 1.93 | 1267.5 / 2.29 | 758.3 / 1.62 | 1399.2 / 2.38 |
| Ling-Flash-V2 | - | 8 | 770.4 / 1 | 740.2 / 1 | 674.3 / 1 | 762.7 / 1 |
| Ling-Flash-V2 | SpecBundle | 8 | 1366.4 / 1.77 | 1359.0 / 1.83 | 1323.0 / 1.96 | 1685.6 / 2.21 |
| Kimi-K2 | - | 8 | 500.1 / 1 | 466.1 / 1 | 337.9 / 1 | 492.1 / 1 |
| Kimi-K2 | SpecBundle | 8 | 904.4 / 1.81 | 897.9 / 1.93 | 544.2 / 1.61 | 1022.7 / 2.08 |

- The text states that the speedup reaches up to 4.48× compared to inference with no speculative decoding and 1.35× compared to inference with an existing draft model.[^liSpecForgeFlexibleEfficient2026]
- On the coding and mathematics benchmarks, the text states that SpecBundle speedups over baselines range from 1.61× to 4.48× (Table 3).[^liSpecForgeFlexibleEfficient2026]
- The existing draft model has slightly higher MT-Bench throughput than SpecBundle for the LLaMA-3 8B and 70B models, which the paper describes as a trade-off.[^liSpecForgeFlexibleEfficient2026]

### Training insights

- **Data regeneration (Figure 5, Llama3.1-8B, 1 H200 GPU, batch size 8).** Regenerating the responses increases the acceptance length on nearly all benchmarks, with FinanceQA the only exception, and yields an average throughput improvement of 5.3% across all benchmarks.[^liSpecForgeFlexibleEfficient2026]
- **TTT length (Figure 6, Llama3.1-8B, perfect-blend dataset).** The original EAGLE3 implementation fixes the TTT length at 7. The paper varies it from 1 to 17. Acceptance length gains sharply as the TTT length increases from 1 to 3. For MT-Bench a TTT length of 3 already achieves strong performance, whereas for Math500, GSM8K, and HumanEval a TTT length of approximately 13 yields the best results. The paper advises reducing TTT to 3 or 5 under memory constraints.[^liSpecForgeFlexibleEfficient2026]
- **MoE draft models (Table 4).** The dense draft model outperforms all MoE variants. The paper concludes that MoE architectures are not well suited as draft models for speculative decoding.[^liSpecForgeFlexibleEfficient2026]

Table 4 is captioned "Acceptance rate of MoE models with different settings" (configuration: MoE top-k = 1, EAGLE3 number of steps = 3, EAGLE3 top-k = 1, EAGLE3 number of draft tokens = 4). The target model for this table is not stated.[^liSpecForgeFlexibleEfficient2026]

| Configuration | #Experts | MTBench | GPQA | FinanceQA | Math500 | GSM8K | HumanEval | LiveCodeBench |
|---|---|---|---|---|---|---|---|---|
| Same Params | 2 | 1.16 | 1.05 | 1.07 | 1.17 | 1.05 | 1.2 | 1.14 |
| Same FLOPS | 2 | 1.61 | 1.56 | 1.34 | 1.67 | 1.59 | 1.64 | 1.46 |
| Same FLOPS | 3 | 1.62 | 1.69 | 1.35 | 1.77 | 1.7 | 1.67 | 1.57 |
| Same FLOPS | 4 | 1.63 | 1.7 | 1.36 | 1.79 | 1.72 | 1.69 | 1.59 |
| With Shared Experts | 2 | 1.52 | 1.69 | 1.5 | 1.75 | 1.61 | 1.53 | 1.52 |
| With Shared Experts | 3 | 1.52 | 1.7 | 1.46 | 1.75 | 1.61 | 1.53 | 1.52 |
| With Shared Experts | 4 | 1.53 | 1.69 | 1.47 | 1.81 | 1.67 | 1.64 | 1.54 |
| Dense Draft Model | - | 2.99 | 3.14 | 1.91 | 2.55 | 3.48 | 3.34 | 3.12 |

All rows: [^liSpecForgeFlexibleEfficient2026]

## Limitations

- The current SpecBundle release covers instruct models only. Support for reasoning models and vision-language models is planned for future iterations.[^liSpecForgeFlexibleEfficient2026]
- The gain from the larger training dataset is not uniform across domains: MT-Bench performance decreases slightly for the LLaMA-3 8B and 70B models.[^liSpecForgeFlexibleEfficient2026]
- Increasing the TTT length proportionally increases training time and memory consumption for the draft model. Dynamic TTT strategies are left to future work.[^liSpecForgeFlexibleEfficient2026]
- All experiments use the co-located setting; the disaggregated setting is not evaluated.[^liSpecForgeFlexibleEfficient2026]
- No existing draft model is compared for Qwen-30B-A3B, Ling-Flash-V2, and Kimi-K2, because many target models have no publicly accessible draft checkpoint.[^liSpecForgeFlexibleEfficient2026]
- The paper has no dedicated limitations section.

Inconsistencies inside the source, copied as printed:

- The introduction says SpecBundle delivers "up to 4.8x" speedup over inference without speculative decoding; the abstract, Section 6.1, and Table 3 say 4.48×.[^liSpecForgeFlexibleEfficient2026]
- In Table 2, the "Existing" row for Llama-4-Scout has the same three throughput values (1253.0, 1405.1, 1022.7) as the SpecBundle row for Llama-3.3-70B.[^liSpecForgeFlexibleEfficient2026]
- In Table 3, the Qwen-30B-A3B Math500 cell lists throughput 3636.1 against a baseline of 1469.0 with a printed speedup of 1.48.[^liSpecForgeFlexibleEfficient2026]
- Table 4 is captioned "acceptance rate" but its values exceed 1.[^liSpecForgeFlexibleEfficient2026]

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [Training-Time Test](../methods/training-time-test.md), [SpecForge](../methods/specforge.md), [SpecBundle](../methods/specbundle.md)
- Systems compared or built on: [SGLang](../methods/sglang.md)
- Datasets: [Open-PerfectBlend](../datasets/perfectblend.md), [ShareGPT](../datasets/sharegpt.md), [UltraChat](../datasets/ultrachat.md), [MT-Bench](../datasets/mt-bench.md), [GPQA](../datasets/gpqa.md), [FinanceQA](../datasets/financeqa.md), [LiveCodeBench](../datasets/livecodebench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Math500](../datasets/math-500.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [SGLang](zhengSGLangEfficientExecution2024.md)

[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
