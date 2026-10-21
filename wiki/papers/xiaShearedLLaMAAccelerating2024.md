---
type: Paper
title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
description: LLM-shearing prunes LLaMA2-7B to a pre-specified 1.3B or 2.7B architecture and continues pre-training with dynamic batch loading, using 50B tokens.
tags: [structured-pruning, model-compression, pre-training, small-language-models, speculative-drafter]
collections: [speculative drafter]
authors: [Mengzhou Xia, Tianyu Gao, Zhiyuan Zeng, Danqi Chen]
year: 2024
arxiv: "2310.06694"
arxiv_version: 2310.06694v2
code: https://github.com/princeton-nlp/LLM-Shearing
sources:
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
---

# Sheared LLaMA: Accelerating Language Model Pre-training via Structured Pruning

Text source: arXiv HTML, version `2310.06694v2`.

## Summary

Training moderate-sized LLMs from scratch on trillions of tokens is expensive. The paper studies [structured pruning](../methods/structured-pruning.md) as a way to build smaller LLMs from larger pre-trained models.[^xiaShearedLLaMAAccelerating2024] The approach, called LLM-shearing, has two components: *targeted structured pruning*, which prunes a source model to a specified target shape by removing layers, heads, and intermediate and hidden dimensions end to end, and [dynamic batch loading](../methods/dynamic-batch-loading.md), which updates the domain composition of each training batch based on per-domain losses.[^xiaShearedLLaMAAccelerating2024]

The resulting [Sheared-LLaMA](../methods/sheared-llama.md) models prune LLaMA2-7B down to 1.3B and 2.7B parameters. They outperform open-source models of equivalent sizes (Pythia, INCITE, OpenLLaMA, and the concurrent TinyLlama) on downstream and instruction tuning evaluations, while requiring only $3\%$ of the compute of training such models from scratch.[^xiaShearedLLaMAAccelerating2024]

## Contributions

- Targeted structured pruning, a pruning algorithm that prunes a source model to a specified target architecture taken from the configurations of existing pre-trained models.[^xiaShearedLLaMAAccelerating2024]
- Dynamic batch loading, which loads training data from each domain in proportion to its rate of loss reduction.[^xiaShearedLLaMAAccelerating2024]
- Sheared-LLaMA-1.3B and Sheared-LLaMA-2.7B, produced with only 50 billion additional tokens (5% of OpenLLaMA's pre-training budget), which outperform Pythia, INCITE, and OpenLLaMA models of similar scale on 11 downstream tasks and on instruction tuning.[^xiaShearedLLaMAAccelerating2024]

## Method

The process has two stages: (1) prune the source model $\mathcal{M}_{S}$ into the target model $\mathcal{M}_{T}$, and (2) continue pre-training $\mathcal{M}_{T}$ with a standard language modeling objective.[^xiaShearedLLaMAAccelerating2024]

### Targeted structured pruning

- The method learns pruning masks at four granularities: layers ($z^{\text{layer}}\in\mathbb{R}^{L_{\mathcal{S}}}$), hidden dimensions ($z^{\text{hidden}}\in\mathbb{R}^{d_{\mathcal{S}}}$), attention heads ($z^{\text{head}}\in\mathbb{R}^{H_{\mathcal{S}}}$ per layer), and FFN intermediate dimensions ($z^{\text{int}}\in\mathbb{R}^{m_{\mathcal{S}}}$ per layer).[^xiaShearedLLaMAAccelerating2024]
- Masks are parametrized as hard concrete distributions following the $\ell_{0}$ regularization approach, with $\beta=0.83$, $\zeta=1.1$, and $\gamma=-0.1$.[^xiaShearedLLaMAAccelerating2024]
- Prior work controls a target sparsity. This method uses a pair of Lagrange multipliers per substructure to constrain the pruned shape directly. For heads in one layer:[^xiaShearedLLaMAAccelerating2024]

$$
\tilde{\mathcal{L}}^{\mathrm{head}}(\lambda,\phi,z)=\lambda^{\mathrm{head}}\cdot\left(\sum{z^{\mathrm{head}}}-H_{\mathcal{T}}\right)+\phi^{\mathrm{head}}\cdot\left(\sum{z^{\mathrm{head}}}-H_{\mathcal{T}}\right)^{2}
$$

- Weights and masks are optimized jointly with the min-max objective $\min_{\theta,z}\max_{\lambda,\phi}\mathcal{L}_{\mathrm{prune}}(\theta,z,\lambda,\phi)$, where $\mathcal{L}_{\mathrm{prune}}$ is the language modeling loss with masked weights plus the head, intermediate, layer, and hidden constraints.[^xiaShearedLLaMAAccelerating2024]
- The pruning stage is roughly 5$\times$ slower than standard LM training and the masks converge fast, so only a limited budget goes to pruning. After pruning, the highest-scoring components of each substructure are kept.[^xiaShearedLLaMAAccelerating2024]
- The shearing algorithm inherits the head dimension of the source model. The target number of heads is the target hidden dimension divided by the source head dimension.[^xiaShearedLLaMAAccelerating2024]

### Dynamic batch loading

- Motivation: continued pre-training on RedPajama reduces loss at different rates across domains compared to training from scratch. The pruned model's loss on GitHub is better than the reference loss, and significantly worse on C4.[^xiaShearedLLaMAAccelerating2024]
- Every $m$ steps, the model is evaluated on a held-out validation set per domain. With $\Delta_{t}[i]=\max\{\ell_{t}[i]-\ell_{\mathrm{ref}}[i],0\}$, the domain weights are updated by exponential ascent:[^xiaShearedLLaMAAccelerating2024]

$$
\alpha_{t}=w_{t-m}\cdot\exp({\Delta_{t}});\quad w_{t}=\frac{\alpha_{t}}{\sum_{i}\alpha_{t}[i]}
$$

- It is applied in both stages. For pruning, $w_{0}$ is the original pre-training data's domain weights. For continued pre-training, $w_{0}$ is the final weights from the pruning stage.[^xiaShearedLLaMAAccelerating2024]
- Reference loss: by default the loss predicted by a scaling function fitted per domain on LLaMA2-7B, LLaMA2-13B, and LLaMA2-70B (*scaling reference*), $L(N,D)=E+\frac{A}{N^{\alpha}}+\frac{B}{D^{\beta}}$. The alternative is the source model's domain validation loss (*source reference*).[^xiaShearedLLaMAAccelerating2024]
- Unlike DoReMi, it needs no reference or proxy model to be trained.[^xiaShearedLLaMAAccelerating2024]

Estimated reference loss (Table 6):[^xiaShearedLLaMAAccelerating2024]

| | CC | GitHub | Book | StackExchange | Wiki | ArXiv | C4 |
|---|---|---|---|---|---|---|---|
| LLaMA2-1.3B | 1.964 | 0.746 | 2.139 | 1.612 | 1.759 | 1.445 | 2.125 |
| LLaMA2-2.7B | 1.871 | 0.688 | 2.033 | 1.535 | 1.630 | 1.356 | 2.033 |

### Training details (Table 7)

| | Pruning | Continued pre-training |
|---|---|---|
| Training budget | $0.4$B | $50$B |
| Learning rate of $z,\phi,\lambda$ | $1.0$ | - |
| Learning rate of $\theta$ | $0.0001$ | $0.0001$ |
| LR warmup ratio | $10\%$ | $3\%$ |
| Batch size (tokens) | $131$K | $1$M |
| Evaluation interval $m$ (steps) | $50$ | $400$ |
| Steps | $3,200$ | $51,200$ |
| # GPUs | $8$ | $16$ |
| Throughput (tokens/s) | $15$K | $145$K (1.3B) / $77$K (2.7B) |

All rows: [^xiaShearedLLaMAAccelerating2024]

## Experiments & Results

### Setup

- Source model: LLaMA2-7B. Target architectures: Pythia-1.4B for the 1.3B model and INCITE-Base-3B for the 2.7B model.[^xiaShearedLLaMAAccelerating2024]
- Data: [RedPajama](../datasets/redpajama.md), with seven domains (CommonCrawl, C4, Github, Wikipedia, Books, ArXiv, StackExchange). The held-out validation set has 2 million tokens per domain (500 sequences of 4,096 tokens). 0.4 billion tokens go to pruning and 50 billion tokens to continued pre-training. Sequence length is 4,096 tokens.[^xiaShearedLLaMAAccelerating2024]
- Evaluation uses lm-evaluation-harness: 0-shot ARC-E, LAMBADA, LogiQA, PIQA, SciQ, WinoGrande; 10-shot [HellaSwag](../datasets/hellaswag.md), 25-shot ARC-C, and 5-shot [MMLU](../datasets/mmlu.md); exact match on 32-shot Natural Questions.[^xiaShearedLLaMAAccelerating2024]
- Instruction tuning: fine-tune on 10,000 instruction-response pairs sampled from [ShareGPT](../datasets/sharegpt.md), evaluate on another 1,000 instructions with GPT-4 as the evaluator, and report the win rate averaged over both presentation orders.[^xiaShearedLLaMAAccelerating2024]

Model configurations (Table 8):[^xiaShearedLLaMAAccelerating2024]

| Model | #Param | #Layers | Hidden | Intermediate | #Heads | Head Dim |
|---|---|---|---|---|---|---|
| OPT-1.3B | 1.3B | 24 | 2048 | 8192 | 32 | 64 |
| Pythia-1.4B | 1.4B | 24 | 2048 | 8192 | 16 | 128 |
| TinyLlama-1.1B | 1.1B | 22 | 2048 | 5632 | 32 | 64 |
| Sheared-LLaMA-1.3B | 1.3B | 24 | 2048 | 5504 | 16 | 128 |
| OPT-2.7B | 2.7B | 32 | 2560 | 10240 | 32 | 80 |
| Pythia-2.8B | 2.8B | 32 | 2560 | 10240 | 32 | 80 |
| INCITE-Base-3B | 2.8B | 32 | 2560 | 10240 | 32 | 80 |
| OpenLLaMA-3B | 2.7B | 26 | 3200 | 8640 | 32 | 100 |
| Sheared-LLaMA-2.7B | 2.7B | 32 | 2560 | 6912 | 20 | 128 |
| LLaMA2-7B | 6.7B | 32 | 4096 | 11008 | 32 | 128 |

### Downstream tasks (Table 2)

The number in parentheses after a model is its training token count. † marks models trained on data other than RedPajama. Shot counts are in parentheses after the task, 0-shot if not given.[^xiaShearedLLaMAAccelerating2024]

| Model | SciQ | PIQA | WinoGrande | ARC-E | ARC-C (25) | HellaSwag (10) | LogiQA | BoolQ (32) | LAMBADA | NQ (32) | MMLU (5) | Average |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LLaMA2-7B (2T)† | 93.7 | 78.1 | 69.3 | 76.4 | 53.0 | 78.6 | 30.7 | 82.1 | 28.8 | 73.9 | 46.6 | 64.6 |
| OPT-1.3B (300B)† | 84.3 | 71.7 | 59.6 | 57.0 | 29.7 | 54.5 | 26.9 | 57.5 | 58.0 | 6.9 | 24.7 | 48.2 |
| Pythia-1.4B (300B)† | 86.4 | 70.9 | 57.4 | 60.7 | 31.2 | 53.0 | 27.3 | 57.4 | 61.6 | 6.2 | 25.7 | 48.9 |
| TinyLlama-1.1B (3T)† | 88.9 | 73.3 | 58.8 | 55.3 | 30.1 | 60.3 | 26.3 | 60.9 | 58.8 | 12.1 | 25.5 | 50.0 |
| Sheared-LLaMA-1.3B (50B) | 87.3 | 73.4 | 57.9 | 61.5 | 33.5 | 60.7 | 26.9 | 64.0 | 61.0 | 9.6 | 25.7 | 51.0 |
| OPT-2.7B (300B)† | 85.8 | 73.7 | 60.8 | 60.8 | 34.0 | 61.5 | 26.0 | 63.4 | 63.6 | 10.1 | 25.9 | 51.4 |
| Pythia-2.8B (300B)† | 88.3 | 74.0 | 59.7 | 64.4 | 36.4 | 60.8 | 28.0 | 66.0 | 64.7 | 9.0 | 26.9 | 52.5 |
| INCITE-Base-3B (800B) | 90.7 | 74.6 | 63.5 | 67.7 | 40.2 | 64.8 | 27.7 | 65.9 | 65.3 | 14.9 | 27.0 | 54.7 |
| Open-LLaMA-3B-v1 (1T) | 91.3 | 73.7 | 61.5 | 67.6 | 39.6 | 62.6 | 28.4 | 70.0 | 65.4 | 18.6 | 27.0 | 55.1 |
| Open-LLaMA-3B-v2 (1T)† | 91.8 | 76.2 | 63.5 | 66.5 | 39.0 | 67.6 | 28.1 | 69.6 | 66.5 | 17.1 | 26.9 | 55.7 |
| Sheared-LLaMA-2.7B (50B) | 90.8 | 75.8 | 64.2 | 67.0 | 41.2 | 70.8 | 28.9 | 73.7 | 68.4 | 16.5 | 26.4 | 56.7 |

The LLaMA2-7B row is copied as extracted: LAMBADA 28.8 and NQ 73.9.[^xiaShearedLLaMAAccelerating2024]

- Sheared-LLaMA-2.7B needs 1/32 (3%) of the budget to reach on-par performance with OpenLLaMA-3B-v2.[^xiaShearedLLaMAAccelerating2024]
- TinyLlama-1.1B was pre-trained on 3T tokens, more than the total used for pre-training LLaMA2-7B and the pruning process combined (2T for the source model, and 50.4B for pruning and continued training).[^xiaShearedLLaMAAccelerating2024]
- Instruction tuning: Sheared-LLaMA achieves higher win rates than Pythia-1.4B, INCITE-Base-3B, OpenLLaMA-3B-v1, and OpenLLaMA-3B-v2. The win rates are given only in Figure 3.[^xiaShearedLLaMAAccelerating2024]

### Dynamic batch loading: domain data usage (Table 3)

| | CC | GitHub | Book | StackExchange | Wiki | ArXiv | C4 |
|---|---|---|---|---|---|---|---|
| RedPajama (Original) | $67.0\%$ | $4.5\%$ | $4.5\%$ | $2.0\%$ | $4.5\%$ | $2.5\%$ | $15.0\%$ |
| Dynamic Batch Loading | $36.1\%$ | $0.8\%$ | $9.1\%$ | $1.0\%$ | $3.1\%$ | $0.7\%$ | $49.2\%$ |

All rows: [^xiaShearedLLaMAAccelerating2024]

Pruned models trained with dynamic batch loading achieve better downstream performance than those trained on the original RedPajama distribution (shown in a figure, Sheared-LLaMA-1.3B).[^xiaShearedLLaMAAccelerating2024] The domain weights stabilize after approximately 30% of the training.[^xiaShearedLLaMAAccelerating2024] The scaling reference gives slightly better downstream results than the source reference, especially on math and coding tasks.[^xiaShearedLLaMAAccelerating2024]

### Comparison to other pruning approaches

Targeted structured pruning vs [CoFiPruning](../methods/cofi-pruning.md) (Table 4), with a 0.4B pruning budget and the RedPajama data proportion. Speed is in tokens/second on an Nvidia A100 (80G) GPU, a single instance generating up to 512 tokens.[^xiaShearedLLaMAAccelerating2024]

| Size | Layer config | PPL ↓ | Speed ↑ |
|---|---|---|---|
| 1.3B | CoFiPruning | 9.1 | 51 |
| 1.3B | Targeted pruning | 10.3 | 58 |
| 2.7B | CoFiPruning | 7.0 | 37 |
| 2.7B | Targeted pruning | 7.7 | 43 |

All rows: [^xiaShearedLLaMAAccelerating2024]

Targeted structured pruning needs about 0.5B more tokens in continued pre-training to match CoFiPruning's perplexity.[^xiaShearedLLaMAAccelerating2024]

Sheared-LLaMA (1.3B) vs [LLM-Pruner](../methods/llm-pruner.md) (1.6B) (Table 12), with the same total token budget (around 6B tokens) and no dynamic batch loading.[^xiaShearedLLaMAAccelerating2024]

| | Generation Speed | Training Throughput | PPL |
|---|---|---|---|
| LLM-Pruner | 43 tokens/s | 83K tokens/s | 7.09 |
| Sheared-LLaMA | 58 tokens/s | 139K tokens/s | 6.85 |

All rows: [^xiaShearedLLaMAAccelerating2024]

The LLM-Pruner model has 32 layers, 7 heads, intermediate size 2201, and hidden size 4096, because that algorithm cannot prune the hidden dimension and layers.[^xiaShearedLLaMAAccelerating2024]

Inference speed in tokens/s (Table 16), on an A100 GPU, generating up to 2048 tokens with a batch size of 1.[^xiaShearedLLaMAAccelerating2024]

| Model | 7B | 1.3B | 2.7B |
|---|---|---|---|
| LLaMA-7B | 37 | n/a | n/a |
| LLM Pruner | n/a | 41 | 40 |
| Sheared-LLaMA | n/a | 62 | 47 |
| Wanda (2:4), 50% sparsity | n/a | - | 42 |
| Wanda (4:8), 50% sparsity | n/a | - | 42 |

All rows: [^xiaShearedLLaMAAccelerating2024]

### Budget allocation (Table 5)

Fixed budget of 5B tokens split between pruning and continued pre-training (CT).[^xiaShearedLLaMAAccelerating2024]

| Pruning tokens | CT tokens | PPL after pruning | PPL after CT |
|---|---|---|---|
| 0.2B | 4.6B | 12.99 | 7.46 |
| 0.4B | 4.4B | 10.29 | 7.32 |
| 0.8B | 4.0B | 9.01 | 7.23 |
| 1.6B | 3.2B | 8.04 | 7.08 |

All rows: [^xiaShearedLLaMAAccelerating2024]

### Coding and math (Table 13)

| Model | [GSM8K](../datasets/gsm8k.md) (8) EM | [HumanEval](../datasets/humaneval.md) Pass@1 | HumanEval Pass@5 |
|---|---|---|---|
| LLaMA2-7B | 13.7 | 12.8 | 23.8 |
| OPT-2.7B | 0.1 | 0.0 | 0.0 |
| Pythia-2.8B | 1.7 | 5.1 | 14.6 |
| INCITE-Base-3B | 1.8 | 4.3 | 4.9 |
| Open-LLaMA-3B-v1 | 2.5 | 0.0 | 1.2 |
| Open-LLaMA-3B-v2 | 2.7 | 10.4 | 20.1 |
| Sheared-LLaMA-2.7B (Source) | 2.7 | 3.7 | 5.5 |
| Sheared-LLaMA-2.7B (Scaling) | 2.4 | 4.9 | 9.2 |

All rows: [^xiaShearedLLaMAAccelerating2024]

### Pruning Pythia (Table 14)

A Pythia model is pruned down to 160M parameters with 0.4B tokens for pruning and 33B tokens (32,000 steps) for continued pre-training. The text names the source model as both Pythia-440M and Pythia-410M.[^xiaShearedLLaMAAccelerating2024]

| | Training tokens | Zero-shot performance |
|---|---|---|
| Pythia-160M | 300B | 43.56 |
| Sheared-Pythia | (300B) + 10B | 43.51 |
| Sheared-Pythia | (300B) + 33B | 45.78 |

All rows: [^xiaShearedLLaMAAccelerating2024]

### Other findings

- Pruning from LLaMA2 gives a consistent advantage over pruning from LLaMA1, and the difference is not very large.[^xiaShearedLLaMAAccelerating2024]
- A continually pre-trained INCITE-Base-3B starts with higher task accuracy but plateaus, while Sheared-LLaMA-2.7B improves rapidly and surpasses it.[^xiaShearedLLaMAAccelerating2024]
- Excluding GitHub, StackExchange, and ArXiv during pruning (LLaMA1-13B to 7B) does not resolve the loss imbalance. After continued pre-training on RedPajama, the difference from LLaMA1-7B is -0.0783 on GitHub and 0.1064 on C4.[^xiaShearedLLaMAAccelerating2024]

## Limitations

- The method depends on the availability of open-source pre-training datasets and models. If a domain is not covered in the pre-training data, the method may not recover performance well on it.[^xiaShearedLLaMAAccelerating2024]
- Only a 7B parameter model was used as the source model, due to computational constraints.[^xiaShearedLLaMAAccelerating2024]
- The math ability of 3B models including Sheared-LLaMA is far below that of larger models, and Sheared-LLaMA's coding ability lags behind models trained on more code data.[^xiaShearedLLaMAAccelerating2024]
- The scaling law is fitted on few data points, so the projected reference loss may be biased compared to the true value.[^xiaShearedLLaMAAccelerating2024]
- Dynamic batch loading relies on a fixed evaluation set, which may not fully represent performance on the entire dataset.[^xiaShearedLLaMAAccelerating2024]
- Targeted pruning has a slightly higher perplexity than CoFiPruning at the same sparsity.[^xiaShearedLLaMAAccelerating2024]
- The continued pre-training setup for the INCITE-Base-3B comparison may not be optimal, as the authors note in hindsight.[^xiaShearedLLaMAAccelerating2024]

## Related

- Proposed: [Sheared-LLaMA](../methods/sheared-llama.md), [Dynamic batch loading](../methods/dynamic-batch-loading.md)
- Methods: [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md)
- Methods compared against: [CoFiPruning](../methods/cofi-pruning.md), [LLM-Pruner](../methods/llm-pruner.md), [Wanda](../methods/wanda.md)
- Datasets: [RedPajama](../datasets/redpajama.md), [ShareGPT](../datasets/sharegpt.md), [MMLU](../datasets/mmlu.md), [HellaSwag](../datasets/hellaswag.md), [GSM8K](../datasets/gsm8k.md), [HumanEval](../datasets/humaneval.md)

## Open questions and results

- [Training budgets for pruning recovery and drafter distillation](../analyses/recovery-and-distillation-training-budgets.md)
- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
