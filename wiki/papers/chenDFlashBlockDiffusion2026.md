---
type: Paper
title: "DFlash: Block Diffusion for Flash Speculative Decoding"
description: Speculative decoding framework whose drafter is a lightweight block diffusion model, conditioned on target hidden features through KV injection, that drafts a whole token block in one forward pass.
tags: [speculative-decoding, block-diffusion, diffusion-llm, parallel-drafting, kv-injection, llm-inference, mobile-specedge]
collections: ["mobile-specedge"]
authors: [Jian Chen, Yesheng Liang, Zhijian Liu]
doi: 10.48550/arXiv.2602.06036
arxiv: "2602.06036"
arxiv_version: 2602.06036v2
code: https://github.com/z-lab/dflash
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
---

# DFlash: Block Diffusion for Flash Speculative Decoding

Text source: arXiv HTML, version `2602.06036v2`.

## Summary

[Speculative decoding](../methods/speculative-decoding.md) uses a fast draft model whose tokens the target LLM verifies in parallel, but state-of-the-art methods such as [EAGLE-3](../methods/eagle-3.md) still draft autoregressively, which the paper says caps achievable speedups at approximately 2-3×.[^chenDFlashBlockDiffusion2026] Diffusion LLMs generate in parallel but underperform autoregressive models in quality, and earlier diffusion drafters (DiffuSpec, SpecDiff-2) use massive drafters (e.g., 7B parameters) whose drafting latency limits practical speedups to 3-4×.[^chenDFlashBlockDiffusion2026]

[DFlash](../methods/dflash.md) is a speculative decoding framework that drafts with a lightweight [block diffusion](../methods/block-diffusion.md) model. It generates all draft tokens of a block in a single forward pass and conditions the drafter on context features extracted from the target model.[^chenDFlashBlockDiffusion2026] The paper reports over 6× lossless acceleration across a range of models and tasks, and up to 2.5× higher speedup than EAGLE-3.[^chenDFlashBlockDiffusion2026]

## Contributions

- A speculative decoding framework that uses a small block diffusion model as the drafter, so drafting cost is one parallel pass instead of one pass per draft token.[^chenDFlashBlockDiffusion2026]
- [KV injection](../methods/kv-injection.md): fused target hidden features are injected into the Key and Value projections of every draft layer, which lets acceptance length scale with drafter depth.[^chenDFlashBlockDiffusion2026]
- A training recipe tailored to speculative decoding: randomly sampled anchor tokens that define masked blocks, a sparse attention mask that trains many blocks in one pass, position-dependent loss decay, and a frozen embedding layer and LM head shared with the target.[^chenDFlashBlockDiffusion2026]
- Evaluation on Qwen3 and LLaMA-3.1 targets with the Transformers backend and under serving with [SGLang](../methods/sglang.md) and [vLLM](../methods/vllm.md).[^chenDFlashBlockDiffusion2026]

## Method

### Speedup model

Per-token latency is $L=\frac{T_{\text{draft}}+T_{\text{verify}}}{\tau}$ (Eq. 1), where $\tau\in[1,\gamma+1]$ is the expected number of accepted tokens per cycle including the bonus token, and speedup is $\eta=L_{\text{target}}/L$.[^chenDFlashBlockDiffusion2026] An autoregressive drafter pays $T_{\text{draft}}=\gamma\cdot t_{\text{step}}$ (Eq. 2). A diffusion drafter pays $T_{\text{draft}}=t_{\text{parallel}}$ (Eq. 3), which is largely insensitive to $\gamma$ for moderate block sizes.[^chenDFlashBlockDiffusion2026] Because cost no longer scales with the number of draft tokens, the drafter can be deeper: a five-layer DFlash drafter generating 16 tokens has lower latency and higher acceptance length than EAGLE-3 generating 8 tokens.[^chenDFlashBlockDiffusion2026]

### Inference

- **Target context features.** During the prefill pass the target model's hidden states are extracted from a fixed set of layers uniformly sampled from shallow to deep, concatenated, and passed through a lightweight projection layer into a compact target context feature.[^chenDFlashBlockDiffusion2026]
- **KV injection.** $\mathbf{H}_{t}=\mathrm{RMSNorm}\left(W_{c}[\mathbf{H}^{(l_{1})};\ldots;\mathbf{H}^{(l_{5})}]\right)$ is shared by all draft layers. At layer $i$ the draft tokens produce the queries, and both target features and draft tokens are projected into keys and values: $\mathbf{K}_{i}=[W_{i}^{K}\mathbf{H}_{t};\,W_{i}^{K}\mathbf{H}_{d}]_{\mathrm{seq}}$, $\mathbf{V}_{i}=[W_{i}^{V}\mathbf{H}_{t};\,W_{i}^{V}\mathbf{H}_{d}]_{\mathrm{seq}}$. The projected features are stored in the drafter's KV cache and reused across drafting iterations.[^chenDFlashBlockDiffusion2026]
- **Contrast with EAGLE-3.** EAGLE-3 fuses target features with the drafter's token embeddings and feeds them only as inputs, so the target information is diluted as drafter depth grows.[^chenDFlashBlockDiffusion2026]
- **Parallel diffusion drafting.** All masked positions within a block are decoded in parallel in a single forward pass.[^chenDFlashBlockDiffusion2026]
- **Memory overhead.** The only extra parameterized component is $W_{c}\in\mathbb{R}^{D\times 5D}$. For Qwen3.5-35B-A3B with $D=2048$ and BF16 weights this adds about 42 MB, against a roughly 70 GB target model. For batch size 1 and sequence length 2048, the projection input and output require about 40 MB and 8 MB. During decoding with block size 16, the temporary activation is below 400 KB.[^chenDFlashBlockDiffusion2026]

### Training

- **Random sampling of masked blocks.** Anchor tokens are sampled at random from the response. Each anchor is the first position of a block and the remaining positions are masked. The drafter predicts the next $\text{block\_size}-1$ tokens in parallel, which matches inference, where the drafter always conditions on the clean bonus token from the previous verification step.[^chenDFlashBlockDiffusion2026]
- **Sparse attention mask.** All blocks are concatenated into one sequence. Tokens attend bidirectionally within their block and to the corresponding injected target features, and attention across blocks is disallowed. Implemented with Flex Attention.[^chenDFlashBlockDiffusion2026]
- **Long-context training.** The number of masked blocks per sequence is fixed, and anchor positions are resampled for each sequence at every epoch.[^chenDFlashBlockDiffusion2026]
- **Loss weighting.** Cross-entropy at position $k$ within a block is weighted by $w_{k}=\exp\!\left(-\frac{k-1}{\gamma}\right)$ (Eq. 4). $\gamma$ is set to 7 for block size 16, 5 for block size 10, and 4 for block size 8.[^chenDFlashBlockDiffusion2026]
- **Shared embedding and LM head.** Both are shared with the target and frozen. Only the draft Transformer layers are updated.[^chenDFlashBlockDiffusion2026]
- **Hyperparameters.** 6 epochs, AdamW, learning rate $6\times 10^{-4}$, gradient clipping threshold 1.0, cosine schedule with warmup ratio 0.04, maximum sequence length 3072 tokens (4096 for Qwen3-Coder), 512 anchor positions sampled per sequence.[^chenDFlashBlockDiffusion2026]

## Experiments & Results

### Setup

- Targets: LLaMA-3.1 Instruct (8B) and Qwen3 (4B, 8B, Coder-30B-A3B-Instruct).[^chenDFlashBlockDiffusion2026]
- Tasks. Math: [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md), AIME25. Code: [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [LiveCodeBench](../datasets/livecodebench.md) (LCB). Chat: [MT-Bench](../datasets/mt-bench.md), [Alpaca](../datasets/alpaca.md).[^chenDFlashBlockDiffusion2026]
- Metrics: average acceptance length $\tau$ and end-to-end decoding speedup over the autoregressive baseline.[^chenDFlashBlockDiffusion2026]
- Hardware: NVIDIA H200 GPUs unless otherwise specified. Serving experiments use a single B200 GPU.[^chenDFlashBlockDiffusion2026]
- Training data: a mixture of around 800K samples from NVIDIA Nemotron Post-Training Dataset V2 and CodeAlpaca, with responses regenerated by the target model.[^chenDFlashBlockDiffusion2026]
- Drafter: 5 layers (8 for Qwen3 Coder), block size 16 (10 for LLaMA 3.1), target features from 5 layers uniformly selected between the second layer and the third-to-last layer.[^chenDFlashBlockDiffusion2026]
- Baselines: vanilla autoregressive decoding and EAGLE-3. EAGLE-3 checkpoints for Qwen3 are those released by AngelSlim. For LLaMA-3.1-Instruct the official EAGLE-3 checkpoint is used. Other dLLM-based speculative decoding methods are not compared because they lack open-source implementations.[^chenDFlashBlockDiffusion2026]

### Instruct models, Transformers backend (Table 1)

Qwen3, thinking mode disabled, maximum of 2048 generated tokens. Each cell is speedup / $\tau$. The number in parentheses is the draft tree size for EAGLE-3 and the block size for DFlash. EAGLE-3 uses 7 draft steps and top-$k$ 10.[^chenDFlashBlockDiffusion2026]

Temperature = 0:

| Model | Method | GSM8K | MATH-500 | AIME25 | HumanEval | MBPP | LCB | MT-Bench | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| Q3-4B | EAGLE-3 (16) | 1.99× / 3.30 | 1.83× / 3.08 | 1.79× / 3.05 | 1.84× / 3.05 | 1.78× / 2.95 | 1.73× / 2.91 | 1.74× / 3.02 | 1.81× / 3.05 |
| Q3-4B | EAGLE-3 (60) | 2.27× / 3.77 | 2.10× / 3.52 | 2.13× / 3.51 | 2.12× / 3.47 | 2.02× / 3.38 | 1.90× / 3.22 | 2.04× / 3.49 | 2.08× / 3.48 |
| Q3-4B | DFlash (16) | 5.15× / 6.53 | 6.09× / 7.84 | 5.68× / 7.27 | 5.21× / 6.64 | 4.78× / 6.09 | 5.41× / 7.09 | 2.85× / 4.35 | 4.91× / 6.54 |
| Q3-8B | EAGLE-3 (16) | 1.94× / 3.23 | 1.81× / 3.02 | 1.79× / 3.00 | 1.89× / 3.17 | 1.69× / 2.82 | 1.57× / 2.65 | 1.63× / 2.83 | 1.76× / 2.96 |
| Q3-8B | EAGLE-3 (60) | 2.23× / 3.71 | 2.05× / 3.49 | 2.05× / 3.44 | 2.17× / 3.65 | 1.93× / 3.25 | 1.81× / 3.03 | 1.90× / 3.26 | 2.02× / 3.40 |
| Q3-8B | DFlash (16) | 5.15× / 6.54 | 6.08× / 7.87 | 5.62× / 7.08 | 5.14× / 6.50 | 4.65× / 5.95 | 5.51× / 7.27 | 2.75× / 4.24 | 4.86× / 6.49 |

Temperature = 1:

| Model | Method | GSM8K | MATH-500 | AIME25 | HumanEval | MBPP | LCB | MT-Bench | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| Q3-4B | EAGLE-3 (16) | 1.89× / 3.22 | 1.75× / 2.99 | 1.64× / 2.79 | 1.74× / 3.01 | 1.69× / 2.89 | 1.63× / 2.77 | 1.70× / 2.95 | 1.72× / 2.95 |
| Q3-4B | EAGLE-3 (60) | 2.12× / 3.68 | 1.97× / 3.44 | 1.83× / 3.20 | 1.94× / 3.39 | 1.92× / 3.33 | 1.82× / 3.14 | 1.91× / 3.36 | 1.93× / 3.36 |
| Q3-4B | DFlash (16) | 4.71× / 6.00 | 5.09× / 6.67 | 3.73× / 4.92 | 4.74× / 6.04 | 4.42× / 5.66 | 4.90× / 6.50 | 2.67× / 4.07 | 4.24× / 5.69 |
| Q3-8B | EAGLE-3 (16) | 1.87× / 3.12 | 1.73× / 2.91 | 1.63× / 2.74 | 1.75× / 3.05 | 1.64× / 2.74 | 1.56× / 2.57 | 1.58× / 2.70 | 1.68× / 2.83 |
| Q3-8B | EAGLE-3 (60) | 2.07× / 3.59 | 1.94× / 3.38 | 1.84× / 3.18 | 2.05× / 3.54 | 1.85× / 3.16 | 1.72× / 2.92 | 1.70× / 3.05 | 1.88× / 3.26 |
| Q3-8B | DFlash (16) | 4.67× / 5.98 | 4.84× / 6.40 | 3.57× / 4.73 | 4.32× / 5.52 | 4.04× / 5.21 | 4.93× / 6.69 | 2.47× / 3.80 | 4.03× / 5.48 |

All rows: [^chenDFlashBlockDiffusion2026]

The paper summarizes this as an average 4.9× speedup over the baseline under greedy decoding, a 2.4× improvement over EAGLE-3 (16), and at temperature 1 a 4.1× speedup over baseline and a 2.2× improvement over EAGLE-3.[^chenDFlashBlockDiffusion2026]

### Reasoning models (Table 2)

Qwen3 with thinking mode enabled, Transformers backend, drafters trained on target outputs with reasoning traces. Each cell is speedup / $\tau$.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | GPQA | MATH-500 | AIME25 |
|---|---|---|---|---|
| Q3-4B | 0 | 4.23× / 5.23 | 4.59× / 5.74 | 4.39× / 5.54 |
| Q3-4B | 1 | 3.67× / 4.55 | 3.93× / 4.89 | 3.64× / 4.68 |
| Q3-8B | 0 | 4.17× / 5.17 | 4.64× / 5.82 | 4.51× / 5.74 |
| Q3-8B | 1 | 3.75× / 4.65 | 4.03× / 5.06 | 3.70× / 4.69 |

All rows: [^chenDFlashBlockDiffusion2026]

### Serving on SGLang (Table 3)

Single B200 GPU, FlashAttention-4 (FA4) backend, Spec-v2 scheduling overlap enabled. Cells are throughput in tok/s, with DFlash speedup over baseline in parentheses.[^chenDFlashBlockDiffusion2026]

| Model | Task | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| Qwen3-4B | Math500 | Baseline | 316 | 1145 | 2201 | 4100 | 7136 | – |
| Qwen3-4B | Math500 | DFlash | 1531 (4.8×) | 4943 (4.3×) | 9066 (4.1×) | 14477 (3.5×) | 20417 (2.9×) | 8.01 |
| Qwen3-4B | HumanEval | Baseline | 312 | 1162 | 2217 | 4184 | 7143 | – |
| Qwen3-4B | HumanEval | DFlash | 1247 (4.0×) | 4147 (3.6×) | 6997 (3.2×) | 11234 (2.7×) | 15703 (2.2×) | 6.63 |
| Qwen3-8B | Math500 | Baseline | 230 | 861 | 1666 | 3133 | 5694 | – |
| Qwen3-8B | Math500 | DFlash | 1175 (5.1×) | 3884 (4.5×) | 7485 (4.5×) | 12268 (3.9×) | 16076 (2.8×) | 8.01 |
| Qwen3-8B | HumanEval | Baseline | 229 | 868 | 1649 | 3253 | 5462 | – |
| Qwen3-8B | HumanEval | DFlash | 955 (4.2×) | 3092 (3.6×) | 6010 (3.6×) | 9919 (3.0×) | 13116 (2.4×) | 6.50 |
| Qwen3-Coder-30B-A3B | HumanEval | Baseline | 229 | 686 | 1068 | 1681 | 2713 | – |
| Qwen3-Coder-30B-A3B | HumanEval | DFlash | 802 (3.5×) | 2078 (3.0×) | 3442 (3.2×) | 5429 (3.2×) | 8314 (3.1×) | 8.09 |
| Qwen3-Coder-30B-A3B | LCB | Baseline | 220 | 681 | 1112 | 1733 | 2823 | – |
| Qwen3-Coder-30B-A3B | LCB | DFlash | 569 (2.6×) | 1621 (2.4×) | 2554 (2.3×) | 4160 (2.4×) | 6401 (2.3×) | 6.42 |
| Qwen3-Coder-30B-A3B | MBPP | Baseline | 228 | 682 | 1057 | 1697 | 2735 | – |
| Qwen3-Coder-30B-A3B | MBPP | DFlash | 720 (3.2×) | 2052 (3.0×) | 3360 (3.2×) | 5522 (3.3×) | 8538 (3.1×) | 7.23 |

All rows: [^chenDFlashBlockDiffusion2026]

### Same training data as EAGLE-3: LLaMA-3.1-8B-Instruct on SGLang (Table 5)

DFlash is trained on UltraChat and [ShareGPT](../datasets/sharegpt.md), the same training data as EAGLE-3, and compared with the official EAGLE-3 checkpoints. SGLang with Spec-v1 (without scheduling overlap, because Spec-v2 does not support tree-based drafting for EAGLE-3), Flashinfer backend, single B200 GPU. EAGLE-3 uses 7 draft steps with top-$k{=}10$ and either 10 or 60 draft tokens. DFlash uses block size 10. Baseline rows are absolute throughput in tokens/s. Other rows are speedup over baseline.[^chenDFlashBlockDiffusion2026]

| Task | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|
| GSM8K | Baseline (TPS) | 249 | 923 | 1739 | 3245 | 5349 | – |
| GSM8K | EAGLE-3 (10) | 1.6× | 1.5× | 1.4× | 1.2× | 1.0× | 3.49 |
| GSM8K | EAGLE-3 (60) | 1.9× | 1.6× | 1.3× | 0.9× | 0.6× | 4.55 |
| GSM8K | DFlash (10) | 2.4× | 2.2× | 2.1× | 1.8× | 1.6× | 4.32 |
| HumanEval | Baseline (TPS) | 245 | 922 | 1778 | 3336 | 5854 | – |
| HumanEval | EAGLE-3 (10) | 2.0× | 1.9× | 1.8× | 1.5× | 1.2× | 3.62 |
| HumanEval | EAGLE-3 (60) | 2.0× | 1.7× | 1.3× | 0.9× | 0.6× | 4.65 |
| HumanEval | DFlash (10) | 2.8× | 2.6× | 2.5× | 2.1× | 1.8× | 4.91 |
| Alpaca | Baseline (TPS) | 245 | 906 | 1745 | 3237 | 5434 | – |
| Alpaca | EAGLE-3 (10) | 1.5× | 1.4× | 1.4× | 1.1× | 0.9× | 3.11 |
| Alpaca | EAGLE-3 (60) | 1.8× | 1.5× | 1.2× | 0.8× | 0.5× | 4.07 |
| Alpaca | DFlash (10) | 2.2× | 2.0× | 1.8× | 1.5× | 1.4× | 3.73 |

All rows: [^chenDFlashBlockDiffusion2026]

In this table EAGLE-3 (60) has a higher average $\tau$ than DFlash (10) on GSM8K (4.55 vs 4.32) and Alpaca (4.07 vs 3.73), while DFlash has the higher speedup at every concurrency level.[^chenDFlashBlockDiffusion2026]

### More models on SGLang (Table 11) and vLLM (Table 12)

SGLang, one B200, concurrency 8. Each cell is acceptance length / speedup over autoregressive decoding. MTP is the model's native MTP.[^chenDFlashBlockDiffusion2026]

| Model | Method | Math500 | HumanEval | MT-Bench |
|---|---|---|---|---|
| Qwen3.5-4B | MTP | 6.5 / 1.5× | 6.3 / 1.6× | 5.3 / 1.3× |
| Qwen3.5-4B | DFlash | 7.1 / 3.0× | 7.3 / 2.9× | 5.6 / 2.3× |
| Qwen3.5-9B | MTP | 6.7 / 1.7× | 6.6 / 1.7× | 5.3 / 1.3× |
| Qwen3.5-9B | DFlash | 7.3 / 3.5× | 7.9 / 3.4× | 5.5 / 2.5× |
| Qwen3.5-35B-A3B | MTP | 6.9 / 1.7× | 7.1 / 1.6× | 5.2 / 1.2× |
| Qwen3.5-35B-A3B | DFlash | 7.2 / 2.4× | 7.9 / 2.3× | 5.4 / 1.7× |
| Qwen3.5-27B | DFlash | 7.7 / 3.8× | 9.1 / 3.9× | 5.5 / 2.5× |
| Qwen3-Coder-Next | DFlash | 6.0 / 1.9× | 7.2 / 1.9× | 3.9 / 1.2× |
| GPT-OSS-20B | DFlash | 5.1 / 2.2× | 4.3 / 2.2× | 4.2 / 2.0× |
| GPT-OSS-120B | DFlash | 5.4 / 1.6× | 4.4 / 1.7× | 3.7 / 1.3× |

vLLM, Qwen3.5-9B. Each cell is DFlash throughput in tok/s, with speedup over autoregressive decoding in parentheses.[^chenDFlashBlockDiffusion2026]

| Concurrency | Math500 | HumanEval | MT-Bench |
|---|---|---|---|
| 1 | 849 (4.0×) | 969 (4.6×) | 627 (3.0×) |
| 8 | 5096 (3.2×) | 5434 (3.4×) | 3536 (2.2×) |
| 16 | 7669 (2.5×) | 8131 (2.7×) | 5297 (1.7×) |
| 32 | 9836 (1.9×) | 10258 (2.1×) | 6787 (1.3×) |

All rows of both tables: [^chenDFlashBlockDiffusion2026]

### Long-context adaptation (Table 4)

The base Qwen3.5-27B drafter, trained on 4K context, is fine-tuned with 1.6K samples from LongAlign-10K for 3 epochs and tested on LongBench. Values are acceptance length.[^chenDFlashBlockDiffusion2026]

| Context | hotpotqa Base | hotpotqa Long | qasper Base | qasper Long | gov_report Base | gov_report Long |
|---|---|---|---|---|---|---|
| 1K | 4.91 | 4.99 | 5.27 | 5.38 | 4.53 | 4.53 |
| 2K | 4.97 | 5.06 | 5.50 | 5.67 | 4.35 | 4.38 |
| 4K | 4.91 | 5.41 | 5.17 | 5.80 | 3.93 | 4.25 |
| 8K | 4.46 | 5.76 | 4.17 | 5.62 | 3.32 | 4.04 |
| 16K | 3.61 | 6.05 | 3.57 | 6.00 | 2.67 | 3.81 |
| 32K | – | – | – | – | 2.09 | 3.56 |

All rows: [^chenDFlashBlockDiffusion2026]

### Ablations

Ablation models are trained on 100K samples drawn from the full data mixture and run on a single H200 GPU with greedy decoding, unless stated. Cells are speedup / $\tau$ unless stated.[^chenDFlashBlockDiffusion2026]

| Ablation | Setting | Math500 | HumanEval | MT-Bench |
|---|---|---|---|---|
| Draft layers (block size 16, 5 target features; Table 6) | 3-L | 4.69× / 5.64 | 3.90× / 4.61 | 2.38× / 3.18 |
| | 5-L | 4.71× / 5.99 | 3.96× / 4.94 | 2.35× / 3.37 |
| | 8-L | 4.64× / 6.33 | 3.96× / 5.29 | 2.23× / 3.50 |
| Target hidden features (3 draft layers, block size 16; Table 7) | 3-H | 4.49× / 5.38 | 3.80× / 4.47 | 2.32× / 3.07 |
| | 5-H | 4.69× / 5.64 | 3.90× / 4.61 | 2.38× / 3.18 |
| Train BS → test BS (8 layers, 5 features; Table 8) | b16 → b16 | 4.64x / 6.33 | 3.96x / 5.29 | 2.23x / 3.50 |
| | b16 → b8 | 3.87x / 5.09 | 3.39x / 4.44 | 2.12x / 3.18 |
| | b8 → b16 | 3.78x / 5.02 | 3.24x / 4.28 | 2.09x / 3.09 |
| | b8 → b8 | 3.97x / 5.21 | 3.53x / 4.61 | 2.22x / 3.29 |
| Masked-block construction (3 layers, 5 features, block size 16; Table 13) | Standard | 4.13x / 4.94 | 3.29x / 3.86 | 2.13x / 2.80 |
| | Sample (random anchors) | 4.69x / 5.64 | 3.90x / 4.61 | 2.38x / 3.18 |

All rows: [^chenDFlashBlockDiffusion2026]

- On Math500 the block-8 model fully accepts entire blocks 35.7% of the time, which the paper reads as block size 8 being underutilized.[^chenDFlashBlockDiffusion2026]
- A model trained with block size 16 generalizes to block size 8 at inference, with acceptance lengths close to a model trained and evaluated at block size 8. The reverse does not hold.[^chenDFlashBlockDiffusion2026]

KV injection vs input fusion (Table 9), Qwen3-4B, 5-layer draft models, draft block size 8. Each cell is $\tau$ / speedup.[^chenDFlashBlockDiffusion2026]

| Drafting | Variant | Injection | GSM8K | HumanEval | MT-Bench |
|---|---|---|---|---|---|
| Autoregressive | EAGLE-3-5L | Input | 4.2 / 2.1× | 4.3 / 2.2× | 3.1 / 1.4× |
| Autoregressive | DFlash-AR | KV | 4.8 / 2.4× | 4.6 / 2.3× | 3.4 / 1.5× |
| Block diffusion | DFlash | Input | 3.5 / 2.9× | 3.5 / 2.9× | 2.6 / 2.0× |
| Block diffusion | DFlash | KV | 4.2 / 3.3× | 4.0 / 3.2× | 3.0 / 2.2× |

All rows: [^chenDFlashBlockDiffusion2026]

A 5-layer block diffusion drafter *without* target context features (Table 10). Each cell is speedup / $\tau$. The target model for this table is not stated.[^chenDFlashBlockDiffusion2026]

| Temp | GSM8K | Math500 | AIME24 | AIME25 |
|---|---|---|---|---|
| 0 | 2.83 / 3.38 | 3.73 / 4.61 | 3.43 / 4.12 | 3.35 / 4.07 |
| 1 | 2.76 / 3.29 | 3.31 / 4.12 | 2.66 / 3.23 | 2.65 / 3.24 |

All rows: [^chenDFlashBlockDiffusion2026]

Loss decay makes training converge faster and to a better result than uniform token weighting. This result is shown only as a figure (Figure 5), with no numbers in the text.[^chenDFlashBlockDiffusion2026]

## Limitations

- Large blocks can increase verification cost under compute-bound settings such as large batch sizes. Adaptive block-size scheduling is left to future work.[^chenDFlashBlockDiffusion2026]
- Speedup falls as concurrency rises: on SGLang, Qwen3-4B Math500 goes from 4.8× at concurrency 1 to 2.9× at concurrency 32.[^chenDFlashBlockDiffusion2026]
- Deeper drafters raise acceptance length but also drafting latency, so the best depth depends on the deployment setting.[^chenDFlashBlockDiffusion2026]
- Using more target hidden features raises training cost: in offline training the storage for cached target hidden states grows linearly with the number of extracted features.[^chenDFlashBlockDiffusion2026]
- The base drafter trained on 4K context degrades beyond 4K context and needs fine-tuning for long contexts.[^chenDFlashBlockDiffusion2026]
- No comparison with other diffusion-based speculative decoding methods (TiDAR, Samragh et al., DiffuSpec, SpecDiff-2), because they have no open-source implementation.[^chenDFlashBlockDiffusion2026]
- The paper has no dedicated limitations section.

## Related

- Methods: [DFlash](../methods/dflash.md), [Speculative decoding](../methods/speculative-decoding.md), [Block diffusion](../methods/block-diffusion.md), [KV injection](../methods/kv-injection.md)
- Systems compared or built on: [EAGLE-3](../methods/eagle-3.md), [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets: [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md), [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [LiveCodeBench](../datasets/livecodebench.md), [MT-Bench](../datasets/mt-bench.md), [Alpaca](../datasets/alpaca.md), [ShareGPT](../datasets/sharegpt.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [SGLang](zhengSGLangEfficientExecution2024.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
