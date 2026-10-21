---
type: Paper
title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
description: Target-independent speculative decoding method that fine-tunes a small autoregressive language model into a parallel drafter predicting K tokens in one forward pass via mask tokens, with a conditional drop-token scheme that cuts adaptation training cost by 3x.
tags: [speculative-decoding, parallel-drafting, target-independent-drafting, mask-prediction, draft-model-training, vllm, speculative-drafter]
collections: ["speculative drafter"]
authors: [Zihao An, Huajun Bai, Ziqiong Liu, Dong Li, Emad Barsoum]
doi: 10.48550/arXiv.2504.18583
arxiv: "2504.18583"
arxiv_version: 2504.18583v4
code: https://github.com/AMD-AIG-AIMA/PARD
sources:
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
---

# PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation

Text source: arXiv HTML, version `2504.18583v4`.

## Summary

The paper divides [speculative decoding](../methods/speculative-decoding.md) drafters into *target-dependent* ones, which use information from the target model (Medusa and EAGLE feed target features into the drafter; LayerSkip and Kangaroo reuse target layers), and *target-independent* ones such as vanilla SD, where one draft model serves a whole family of target models. Target-dependent drafters need a separately trained draft model for every target, which raises adaptation and deployment cost.[^anPARDAcceleratingLLM2025]

With LLaMA3.1-8B as target, a LLaMA3.2-1B draft model has a higher first-token acceptance rate than the EAGLE head, but its autoregressive drafting cost can make vanilla SD slower overall than EAGLE.[^anPARDAcceleratingLLM2025] [PARD](../methods/pard.md) (PARallel Draft) keeps the target-independent small-model drafter and fine-tunes it with mask tokens so that it predicts $K$ future tokens in a single forward pass. A COnditional Drop-token (COD) mechanism reduces the cost of this adaptation training.[^anPARDAcceleratingLLM2025]

All comparisons run on [vLLM](../methods/vllm.md) on an A100-40GB GPU. On LLaMA3.1-8B, PARD reaches 264.88 tokens per second on HumanEval, which the paper reports as a 3.67$\times$ speedup over autoregressive decoding, 1.72$\times$ faster than vanilla SD, and 1.15$\times$ faster than EAGLE-3 (Table 1 lists the speedup for this cell as 3.63).[^anPARDAcceleratingLLM2025]

The authors are at Advanced Micro Devices, Inc. (one also at Tsinghua University).[^anPARDAcceleratingLLM2025]

## Contributions

- PARD, a speculative decoding method with target-independence and parallel token prediction. A single draft model accelerates an entire family of target models, unlike target-dependent methods such as Medusa and EAGLE. Mask tokens let it predict multiple future tokens in one draft forward pass.[^anPARDAcceleratingLLM2025]
- COnditional Drop-token (COD), a training strategy based on the integrity of prefix key-value states that adapts autoregressive draft models into parallel ones and improves training efficiency by up to 3$\times$ while maintaining accuracy.[^anPARDAcceleratingLLM2025]
- Integration of PARD into vLLM, with 264.88 tokens per second on LLaMA3.1-8B on an A100-40GB GPU.[^anPARDAcceleratingLLM2025]

## Method

### Draft cost model

With $T_{D}$ the time for one draft forward pass and $T_{T}$ the time for one target forward pass, one iteration of vanilla SD predicting $K$ tokens costs $T_{\mathrm{AR_{draft}}}=K*T_{D}+T_{T}$ (Eq. 3), and PARD costs $T_{\mathrm{PARD}}=T_{D}+T_{T}$ (Eq. 4). The paper assumes the change in forward time with input length is negligible when the input length is not significantly large.[^anPARDAcceleratingLLM2025]

Figure 1(b) (draft LLaMA3.2-1B, target LLaMA3.1-8B) shows one VSD iteration as six autoregressive draft steps of 4.1 ms plus a 14.3 ms target pass (38.9 ms), against one PARD draft pass of 4.1 ms plus 14.3 ms (18.4 ms), labeled "2.1x faster".[^anPARDAcceleratingLLM2025]

### Parallel drafting with mask tokens (inference)

PARD adopts Mask-Predict. Vanilla SD factorizes the draft distribution autoregressively, $\prod_{k=0}^{K-1}P(x_{n+k}|x_{0},\dots,x_{n+k-1};\bm{\theta}_{\mathrm{AR_{draft}}})$ (Eq. 6). PARD replaces the tokens that would create dependencies with placeholder mask tokens $m_{k}$:[^anPARDAcceleratingLLM2025]

$$
P(x_{n},\dots,x_{n+K-1}|x_{0},\dots,x_{n-1},\bm{\theta}_{\mathrm{PARD}})=\prod_{k=0}^{K-1}P(x_{n+k}|x_{0},\dots,x_{n-1},m_{0},\dots,m_{k-1};\bm{\theta}_{\mathrm{PARD}})
$$

(Eq. 7). The predictions do not depend on each other, so the draft model needs one forward pass instead of $K$.[^anPARDAcceleratingLLM2025] Unlike PaSS, BiTA, and ParallelSpec, which also use mask tokens for parallel drafting but rely on target model information, PARD stays target-independent.[^anPARDAcceleratingLLM2025]

### Mask-token training

Training is split into $K$ subtasks, one per offset, trained simultaneously from lightly preprocessed data, with an attention mask designed so training matches inference. The loss for predicting the $k$-th next token is $\mathcal{L}_{k}=-\frac{1}{N-k+1}\sum_{i=k}^{N}\log P(x_{i}|x_{0},x_{1},\ldots,x_{i-k},m_{0},\ldots,m_{k-2};\bm{\theta}_{\mathrm{PARD}})$ (Eq. 8), where $N$ is the sample length.[^anPARDAcceleratingLLM2025]

This raises the number of training tokens from $N$ to $K\times N$.[^anPARDAcceleratingLLM2025]

### Conditional Drop-token (COD)

- Tokens in earlier subtasks are treated as more important; tokens in later subtasks are selectively dropped.[^anPARDAcceleratingLLM2025]
- Dropping is conditional: a token is retained only if all its prefix tokens are retained, so every retained token has complete key and value states during attention. A naive random drop would break this.[^anPARDAcceleratingLLM2025]
- Subtask $i$ keeps $N_{i}=N*r^{i-1}$ tokens (Eq. 9), so the total is $N_{\mathrm{COD}}=N\frac{1-r^{K}}{1-r}<\frac{N}{1-r}$ (Eq. 10). With $r=0.5$, training tokens drop from $K\times N$ to $2N$. A floor $r_{\text{min}}$ gives $N_{i}^{\prime}=N*\max(r^{i-1},r_{\text{min}})$ (Eq. 11).[^anPARDAcceleratingLLM2025]
- The paper states that COD reduces PARD training cost from $\mathcal{O}(N\cdot K)$ to $\mathcal{O}(N)$.[^anPARDAcceleratingLLM2025]
- After dropping, the sparse data is reorganized into a compact format (Figure 4(d)); Algorithm 1 updates input ids, labels, position ids, and attention masks per subtask and merges them.[^anPARDAcceleratingLLM2025]

### Shared mask token

Using one mask token ID for all positions ($m_{0}=m_{1}=\dots=m_{K-1}$) performs better than distinct IDs and gives what the paper calls *extrapolation capability*: inference with a larger $K$ than used in training.[^anPARDAcceleratingLLM2025]

## Experiments & Results

### Setup

- Target families: LLaMA3, DeepSeek-R1-Qwen, and Qwen. For each series the smallest variant is trained as the PARD drafter.[^anPARDAcceleratingLLM2025] Figure 2 names the draft models as LLaMA3.2-1B and Qwen2.5-0.5B; the ablations use DeepSeek-R1-Qwen-1.5B.[^anPARDAcceleratingLLM2025]
- Training data, chosen per series to match the instruct model's training: LLaMA3 with [Magpie](../datasets/magpie.md)-Llama-3.1-Pro-1M and [Evol-CodeAlpaca](../datasets/evol-codealpaca.md); Qwen2.5 with Magpie-Qwen2-Pro-1M and Evol-CodeAlpaca; DeepSeek-R1-Qwen with OpenR1-Math-220k, OpenThoughts-114k, and Chinese-DeepSeek-R1-Distill-Data-110k. For LLaMA3 and Qwen the answers are regenerated.[^anPARDAcceleratingLLM2025]
- Training: 8xMI250X, TRL framework, 4 epochs, $k=8$, $r=0.7$, $r_{min}=0.2$.[^anPARDAcceleratingLLM2025]
- Benchmarks: [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [MATH500](../datasets/math-500.md), and [SpecBench](../benchmarks/spec-bench.md).[^anPARDAcceleratingLLM2025]
- Evaluation: vLLM on an A100-40GB GPU. Metrics are tokens per second (TPS) and speedup over standard autoregressive generation. EAGLE and EAGLE-3 use their official models.[^anPARDAcceleratingLLM2025]
- The paper does not state the sampling temperature. The Table 1 LLaMA3.1-8B HumanEval speedups (AR 1.00, EAGLE 1.86, VSD 2.13, PARD 3.63) equal the bs=1 column of Table 5.[^anPARDAcceleratingLLM2025]

### Training hyperparameters (Table 4)

| Hyperparameter | Llama3 | Deepseek-R1-Qwen | Qwen |
|---|---|---|---|
| Optimizers | AdamW | AdamW | AdamW |
| Learning Rate | 1e-5 | 3e-5 | 8e-5 |
| Per Device Train Batch Size | 4 | 4 | 8 |
| Gradient Accumulation Steps | 2 | 2 | 1 |
| Num Processes | 8 | 8 | 8 |
| Num Train Epochs | 4 | 4 | 4 |
| Training PARD K | 8 | 8 | 8 |
| Max Seq Length | 512 | 1024 | 512 |
| The Answer Of Training Data | Regenerate + Original | Original | Regenerate |

All rows: [^anPARDAcceleratingLLM2025]

### Main results, vLLM, A100-40GB (Table 1)

| Target | Method | HumanEval TPS | HumanEval SpeedUp | GSM8K TPS | GSM8K SpeedUp | SpecBench TPS | SpecBench SpeedUp | Average TPS | Average SpeedUp |
|---|---|---|---|---|---|---|---|---|---|
| Q2 7B | AR | 76.34 | 1.00 | 76.12 | 1.00 | 75.97 | 1.00 | 76.14 | 1.00 |
| Q2 7B | VSD | 181.18 | 2.37 | 201.15 | 2.64 | 112.00 | 1.47 | 164.78 | 2.16 |
| Q2 7B | PARD | 268.98 | 3.52 | 221.43 | 2.91 | 135.05 | 1.78 | 208.49 | 2.74 |
| Q2.5 3B | AR | 130.46 | 1.00 | 130.42 | 1.00 | 129.95 | 1.00 | 130.28 | 1.00 |
| Q2.5 3B | VSD | 231.65 | 1.78 | 238.71 | 1.83 | 136.26 | 1.05 | 202.21 | 1.55 |
| Q2.5 3B | PARD | 425.96 | 3.27 | 406.17 | 3.11 | 203.05 | 1.56 | 345.06 | 2.65 |
| Q2.5 7B | AR | 76.07 | 1.00 | 75.93 | 1.00 | 75.97 | 1.00 | 75.99 | 1.00 |
| Q2.5 7B | VSD | 178.97 | 2.35 | 162.85 | 2.14 | 107.38 | 1.41 | 149.73 | 1.97 |
| Q2.5 7B | PARD | 285.82 | 3.76 | 292.56 | 3.85 | 145.64 | 1.92 | 241.34 | 3.18 |
| Q2.5 14B | AR | 40.78 | 1.00 | 40.92 | 1.00 | 40.78 | 1.00 | 40.83 | 1.00 |
| Q2.5 14B | VSD | 135.88 | 3.33 | 146.69 | 3.58 | 80.59 | 1.98 | 121.05 | 2.97 |
| Q2.5 14B | PARD | 181.19 | 4.44 | 182.25 | 4.45 | 91.33 | 2.24 | 151.59 | 3.71 |
| L3 8B | AR | 73.68 | 1.00 | 73.57 | 1.00 | 72.80 | 1.00 | 73.35 | 1.00 |
| L3 8B | VSD | 144.59 | 1.96 | 123.76 | 1.68 | 102.76 | 1.41 | 123.70 | 1.69 |
| L3 8B | PARD | 235.84 | 3.20 | 200.45 | 2.72 | 147.80 | 2.03 | 194.70 | 2.65 |
| L3.1 8B | AR | 73.07 | 1.00 | 73.38 | 1.00 | 72.70 | 1.00 | 73.05 | 1.00 |
| L3.1 8B | VSD | 155.47 | 2.13 | 140.93 | 1.92 | 106.44 | 1.46 | 134.28 | 1.84 |
| L3.1 8B | EAGLE | 136.05 | 1.86 | 110.81 | 1.51 | 100.11 | 1.38 | 115.66 | 1.58 |
| L3.1 8B | EAGLE-3 | 233.43 | 3.19 | 192.56 | 2.62 | 155.58 | 2.14 | 193.86 | 2.65 |
| L3.1 8B | PARD | 264.88 | 3.63 | 235.09 | 3.20 | 157.49 | 2.17 | 219.15 | 3.00 |
| L3.3 70B | AR | 24.31 | 1.00 | 24.27 | 1.00 | 23.95 | 1.00 | 24.18 | 1.00 |
| L3.3 70B | VSD | 80.78 | 3.32 | 77.07 | 3.18 | 53.09 | 2.22 | 70.31 | 2.91 |
| L3.3 70B | EAGLE-3 | 95.17 | 3.91 | 75.34 | 3.10 | 63.14 | 2.64 | 77.88 | 3.22 |
| L3.3 70B | PARD | 99.88 | 4.11 | 95.58 | 3.94 | 57.41 | 2.40 | 84.29 | 3.49 |

All rows: [^anPARDAcceleratingLLM2025]

- PARD has the highest TPS in every cell except SpecBench on LLaMA3.3-70B, where EAGLE-3 (63.14, 2.64) is above PARD (57.41, 2.40).[^anPARDAcceleratingLLM2025]
- The paper states that on code tasks PARD achieves speedups from 3.20$\times$ to 4.44$\times$, with average speedups between 2.65$\times$ and 3.71$\times$, and that on LLaMA3.1-8B it runs 1.9$\times$ faster than EAGLE and 1.15$\times$ faster than EAGLE-3.[^anPARDAcceleratingLLM2025]
- Target-independence: one PARD model accelerates three LLaMA3-series targets and three Qwen targets without per-target training.[^anPARDAcceleratingLLM2025]

### DeepSeek-R1-Qwen series (Table 6)

| Target | Method | HumanEval TPS | HumanEval SpeedUp | GSM8K TPS | GSM8K SpeedUp | Math500 TPS | Math500 SpeedUp | Average TPS | Average SpeedUp |
|---|---|---|---|---|---|---|---|---|---|
| DS 7B | AR | 75.87 | 1.00 | 75.96 | 1.00 | 75.92 | 1.00 | 75.92 | 1.00 |
| DS 7B | VSD | 97.90 | 1.29 | 129.20 | 1.70 | 122.51 | 1.61 | 116.54 | 1.54 |
| DS 7B | PARD | 162.39 | 2.14 | 204.62 | 2.69 | 205.23 | 2.70 | 190.75 | 2.51 |
| DS 14B | AR | 40.74 | 1.00 | 40.78 | 1.00 | 40.72 | 1.00 | 40.75 | 1.00 |
| DS 14B | VSD | 75.80 | 1.86 | 102.88 | 2.52 | 95.35 | 2.34 | 91.34 | 2.24 |
| DS 14B | PARD | 103.34 | 2.54 | 130.17 | 3.19 | 133.98 | 3.29 | 122.50 | 3.01 |

All rows: [^anPARDAcceleratingLLM2025]

### Acceptance rate vs. EAGLE (LLaMA3.1-8B, Table 2)

$k$-$\alpha$ is the average acceptance rate when the draft length is $k$.[^anPARDAcceleratingLLM2025]

| Method | HumanEval 1-$\alpha$ | HumanEval 4-$\alpha$ | GSM8K 1-$\alpha$ | GSM8K 4-$\alpha$ |
|---|---|---|---|---|
| EAGLE | 0.83 | 0.72 | 0.79 | 0.66 |
| EAGLE-3 | 0.87 | 0.85 | 0.82 | 0.79 |
| PARD | 0.93 | 0.90 | 0.88 | 0.85 |

All rows: [^anPARDAcceleratingLLM2025]

Figure 1(a) (first-token acceptance rate, target LLaMA3.1-8B, VSD draft LLaMA3.2-1B) carries bar labels EAGLE 0.827 / 0.792, EAGLE3 0.875 / 0.839, VSD 0.944 / 0.895, PARD 0.936 / 0.889 for its two task groups. The task names are not legible in the extracted figure; the EAGLE, EAGLE-3, and PARD values match Table 2's HumanEval and GSM8K 1-$\alpha$ to two decimals. In both groups VSD has a slightly higher first-token acceptance than PARD.[^anPARDAcceleratingLLM2025]

### Draft memory bandwidth (LLaMA3.1-8B, bf16, Table 3)

| Method | $k=4$ | $k=6$ | $k=8$ |
|---|---|---|---|
| EAGLE | 5.94 GB | 8.90 GB | 11.88 GB |
| EAGLE-3 | 5.94 GB | 8.90 GB | 11.88 GB |
| PARD | 2.48 GB | 2.48 GB | 2.48 GB |

All rows: [^anPARDAcceleratingLLM2025]

PARD's draft-phase bandwidth stays constant as $k$ grows, because drafting is one forward pass. The paper concludes that PARD has a higher acceptance ratio than the EAGLE series while consuming less bandwidth.[^anPARDAcceleratingLLM2025]

### Batch size (LLaMA3.1-8B, HumanEval, vLLM, Table 5)

| Method | bs=1 | bs=2 | bs=4 | bs=8 | bs=16 |
|---|---|---|---|---|---|
| AR | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| EAGLE | 1.86 | 1.69 | 1.69 | 1.44 | 1.19 |
| VSD | 2.13 | 2.03 | 1.88 | 1.61 | 1.41 |
| PARD | 3.63 | 3.16 | 2.59 | 1.90 | 1.33 |

All rows: [^anPARDAcceleratingLLM2025]

As batch size grows the bottleneck shifts from memory-bound to compute-bound. PARD's speedup ranges from 1.33$\times$ to 3.63$\times$; at bs=16 VSD (1.41) is above PARD (1.33). EAGLE-3 is not in this table.[^anPARDAcceleratingLLM2025]

### Training cost (Appendix A)

Cost in Pflops per 1M tokens, target fixed to LLaMA3-70B (Section 3.2.3 says LLaMA3.3-70B).[^anPARDAcceleratingLLM2025]

| Method | Forward | Backward | Total |
|---|---|---|---|
| PARD | 6.74 | 13.48 | 20.22 |
| EAGLE | 143.74 | 5.46 | 149.20 |
| EAGLE-3 | 166.18 | 38.22 | 204.4 |

All rows: [^anPARDAcceleratingLLM2025]

- PARD's forward cost uses $2\times 10^{9}$ parameters $\times$ 3.37M effective input tokens after mask prediction with COD. EAGLE's forward includes the 70B target plus the draft (0.86B layer and 1.01B lm-head); the target needs no gradients in the backward pass. EAGLE-3 is counted with HASS-style training and seven times the EAGLE head's input tokens.[^anPARDAcceleratingLLM2025]
- The paper states PARD training efficiency is 7$\times$ higher than EAGLE and 10$\times$ higher than EAGLE-3. PARD's drafter is also reusable across a model series (e.g., LLaMA3-8B, 70B, 405B), while EAGLE-style drafters are trained per target.[^anPARDAcceleratingLLM2025]

### Ablations (target DeepSeek-R1-Qwen-7B, draft DeepSeek-R1-Qwen-1.5B, 93K subset of OpenR1-Math-220K, 1 epoch, MATH500)

COD retention (Figure 5(a), runs named PARD\_$r$\_$r_{\text{min}}$, decoding speed in tokens/s against training hours):[^anPARDAcceleratingLLM2025]

| Run | Tokens/s |
|---|---|
| PARD_1_1 (no drop) | 217.21 |
| PARD_0.7_0.2 | 218.93 |
| PARD_0.7_0 | 217.93 |
| PARD_0.5_0.2 | 214.73 |
| PARD_0.5_0 | 211.74 |
| PARD_0.2_0.2 | 214.39 |
| PARD_0.2_0 | 198.11 |

All rows: [^anPARDAcceleratingLLM2025]

Lower retention trains faster but too low a retention hurts accuracy. $r=0.7$, $r_{\text{min}}=0.2$ gives 3$\times$ faster training while maintaining the original accuracy, and all experiments use it.[^anPARDAcceleratingLLM2025]

Shared vs. distinct mask token IDs: 221.97 vs. 218.05 tokens/s.[^anPARDAcceleratingLLM2025]

$K_{\text{train}}$ × $K_{\text{infer}}$ (Figure 5(b), tokens/s, rows PARD\_$K_{\text{train}}$):[^anPARDAcceleratingLLM2025]

| $K_{\text{train}}$ | $K_{\text{infer}}=4$ | 8 | 12 | 16 |
|---|---|---|---|---|
| 4 | 184 | 213 | 216 | 199 |
| 8 | 184 | 219 | 231 | 212 |
| 12 | 183 | 221 | 232 | 217 |
| 16 | 183 | 220 | 232 | 217 |

All rows: [^anPARDAcceleratingLLM2025]

The best performance is at $K_{\text{infer}}=12$, results are stable for $K_{\text{train}}\geq 8$, and the paper selects $K_{\text{train}}=8$.[^anPARDAcceleratingLLM2025]

### Inference framework (LLaMA3.1-8B, Table 7)

| Framework | Method | HumanEval TPS | HumanEval Speedup | GSM8K TPS | GSM8K Speedup | Average TPS | Average Speedup |
|---|---|---|---|---|---|---|---|
| Transformers | AR | 34.36 | 1.00 | 35.90 | 1.00 | 35.13 | 1.00 |
| Transformers | VSD | 50.52 | 1.47 | 45.24 | 1.26 | 47.88 | 1.36 |
| Transformers | PARD | 145.47 | 4.23 | 114.65 | 3.19 | 130.06 | 3.70x |
| Transformers+ | AR | 76.34 | 1.00 | 76.50 | 1.00 | 76.42 | 1.00 |
| Transformers+ | VSD | 185.29 | 2.43 | 160.59 | 2.10 | 172.94 | 2.26 |
| Transformers+ | PARD | 336.97 | 4.41 | 275.03 | 3.60 | 306.00 | 4.00 |
| vLLM | AR | 73.07 | 1.00 | 73.38 | 1.00 | 73.22 | 1.00 |
| vLLM | VSD | 155.47 | 2.13 | 140.93 | 1.92 | 148.20 | 2.02 |
| vLLM | PARD | 264.88 | 3.63 | 235.09 | 3.20 | 249.98 | 3.41 |

All rows: [^anPARDAcceleratingLLM2025]

Transformers+ is Transformers optimized with torch.compile and a static key-value cache, following GPT-Fast. The paper uses it for development and testing, and reports all final results on vLLM because plain Transformers is inefficient and understates relative speedups for methods such as vanilla SD.[^anPARDAcceleratingLLM2025]

## Limitations

- The paper's headline speedup for LLaMA3.1-8B is 3.67$\times$ in the abstract and conclusion, while Table 1, Table 5, and Table 7 list 3.63 for the same 264.88 tokens/s configuration.[^anPARDAcceleratingLLM2025]
- EAGLE and EAGLE-3 are compared only on LLaMA3.1-8B (both) and LLaMA3.3-70B (EAGLE-3), using official checkpoints. On LLaMA3.3-70B SpecBench, EAGLE-3 is faster than PARD.[^anPARDAcceleratingLLM2025]
- PARD's advantage shrinks with batch size and falls below VSD at bs=16 (1.33 vs. 1.41). Batch sizes above 16 are not reported.[^anPARDAcceleratingLLM2025]
- The cost model treats draft and target forward time as independent of input length, which the paper states holds only when the input length is not significantly large.[^anPARDAcceleratingLLM2025]
- PARD builds on existing small language models: for each model series the smallest variant is trained as the drafter, on data selected for that series. Target-independence holds within a series, not across series.[^anPARDAcceleratingLLM2025]
- The paper does not report sampling temperature or mean accepted length per round; it reports TPS, speedup, and per-position acceptance rates.[^anPARDAcceleratingLLM2025]
- Ablations use one target (DeepSeek-R1-Qwen-7B) and one benchmark (MATH500).[^anPARDAcceleratingLLM2025]

## Related

- Methods: [PARD](../methods/pard.md), [Speculative decoding](../methods/speculative-decoding.md)
- Systems compared or built on: [EAGLE](../methods/eagle.md), [EAGLE-3](../methods/eagle-3.md), [Medusa](../methods/medusa.md), [vLLM](../methods/vllm.md), [EAGLE-2](../methods/eagle-2.md), [Sequoia](../methods/sequoia.md), [SpecInfer](../methods/specinfer.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Datasets and benchmarks: [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md), [Spec-Bench](../benchmarks/spec-bench.md), [Magpie](../datasets/magpie.md), [Evol-CodeAlpaca](../datasets/evol-codealpaca.md), [OpenThoughts-114k](../datasets/openthoughts.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [SuffixDecoding](oliaroSuffixDecodingExtremeSpeculative2024.md)
- Other parallel drafters in this wiki: [DFlash](chenDFlashBlockDiffusion2026.md), [DSpark](chengDSparkConfidenceScheduledSpeculative2026.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
