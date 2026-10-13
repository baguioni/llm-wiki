---
type: Paper
title: Compact Language Models via Pruning and Knowledge Distillation
description: Empirical study of structured pruning (depth, width, attention, MLP) plus distillation-based retraining that yields a list of compression best practices and the Minitron 8B and 4B models derived from Nemotron-4 15B.
tags: [model-compression, structured-pruning, knowledge-distillation, neural-architecture-search, small-language-models, speculative-drafter]
collections: [speculative drafter]
authors: [Saurav Muralidharan, Sharath Turuvekere Sreenivas, Raviraj Joshi, Marcin Chochowski, Mostofa Patwary, Mohammad Shoeybi, Bryan Catanzaro, Jan Kautz, Pavlo Molchanov]
doi: 10.48550/arXiv.2407.14679
arxiv: "2407.14679"
arxiv_version: 2407.14679v2
code: https://github.com/NVlabs/Minitron
sources:
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
---

# Compact Language Models via Pruning and Knowledge Distillation

Text source: arXiv HTML, version `2407.14679v2`.

## Summary

Model families that target different deployment sizes are produced by training each variant from scratch, which is extremely compute-intensive.[^muralidharanCompactLanguageModels2024] The paper asks whether pruning an existing LLM and re-training it with a fraction (<3%) of the original training data is a suitable alternative.[^muralidharanCompactLanguageModels2024] It explores structured pruning along four axes (neurons in feed-forward layers, attention heads, embedding channels, and model depth), how to combine the axes, distillation-based retraining, and a search over compressed architectures, and it condenses the findings into a list of compression best practices.[^muralidharanCompactLanguageModels2024]

Applying the practices to Nemotron-4 15B produces the Minitron 8B and 4B models. Deriving them requires up to 40$\times$ fewer training tokens per model than training from scratch, which gives compute cost savings of 1.8$\times$ for training the full model family (15B, 8B, and 4B).[^muralidharanCompactLanguageModels2024] Minitron models show up to a 16% improvement in MMLU scores compared to training from scratch and perform comparably to community models such as Mistral 7B, Gemma 7B and Llama-3 8B.[^muralidharanCompactLanguageModels2024]

## Contributions

- The first thorough empirical exploration of structured pruning and retraining in LLMs across multiple axes, with insights on metrics and hyper-parameters for pruning, order of pruning, effects of combining axes, and data-efficient retraining.[^muralidharanCompactLanguageModels2024]
- A list of practical LLM compression and retraining best practices grounded in empirical evidence.[^muralidharanCompactLanguageModels2024]
- The Minitron family of LLMs, obtained through direct pruning of the Nemotron-4 15B model.[^muralidharanCompactLanguageModels2024]

## Method

### Importance estimation

The paper proposes a purely activation-based importance estimation strategy that computes sensitivity for all axes (depth, neuron, head, embedding channel) with a small calibration dataset of 1024 samples and only forward propagation passes.[^muralidharanCompactLanguageModels2024]

- **Width.** Importance of each head, neuron, and embedding channel is computed from the activations of the MHA, MLP, and LayerNorm layers, respectively:[^muralidharanCompactLanguageModels2024]

$$
F_{\text{head}}^{(i)}=\sum_{\mathbf{B,S}}\|\operatorname{Attn}(\mathbf{X}\boldsymbol{W}^{Q,i},\mathbf{X}\boldsymbol{W}^{K,i},\mathbf{X}\boldsymbol{W}^{V,i})\|_{2},\quad
F_{\text{neuron}}^{(i)}=\sum_{\mathbf{B,S}}\mathbf{X}\big(\boldsymbol{W}_{1}^{i}\big)^{T},\quad
F_{\text{emb}}^{(i)}=\sum_{\mathbf{B,S}}LN(\mathbf{X})_{i}
$$

  $\sum_{\mathbf{B,S}}$ is an aggregation along the batch and sequence dimensions. Three aggregation functions are tried for each dimension: mean(abs), L2 norm, and variance.[^muralidharanCompactLanguageModels2024]
- **Depth.** Layer importance uses perplexity (PPL), which removes a single layer and measures the effect on perplexity, and Block Importance (BI), which uses the cosine distance between the input and output of a layer: $\operatorname{BI}_{i}=1-\mathbb{E}_{X,t}\frac{\mathbf{X}^{T}_{i,t}\mathbf{X}_{i+1,t}}{\|\mathbf{X}_{i,t}\|_{2}\|\mathbf{X}_{i+1,t}\|_{2}}$. BI of all layers is computed in a single forward pass.[^muralidharanCompactLanguageModels2024]
- **Iterative importance.** Alternates pruning and importance estimation over $T$ iterations.[^muralidharanCompactLanguageModels2024]

### Obtaining a pruned model

- Elements of each axis are ranked by importance and the corresponding weight matrices are trimmed directly. Embedding-channel pruning trims the embedding dimension of the weight matrices in MLP, MHA, and LayerNorm layers.[^muralidharanCompactLanguageModels2024]
- When pruning attention heads from $L$ to $K$ heads, residual information from pruned heads is added back into the remaining heads: $head_{i}+(head_{i}-head_{2K-i+1})$ for $i\in[K-(L-K),K]$. With grouped query attention this is applied only to the query heads.[^muralidharanCompactLanguageModels2024]
- **Lightweight neural architecture search.** All feasible architectures that meet the parameter budget are enumerated, then each candidate undergoes lightweight retraining ($\sim$1.8B tokens), which stabilizes relative rankings.[^muralidharanCompactLanguageModels2024]

### Retraining with knowledge distillation

The uncompressed model is the teacher and the pruned model is the student.[^muralidharanCompactLanguageModels2024] The total loss is $L=L_{\text{CLM}}+L_{logits}+\alpha\times L_{is}$, where $L_{CLM}$ is the student cross-entropy loss against ground truth labels, $L_{logits}$ is the logit-based KD loss, $L_{is}$ is the intermediate-state KD loss, and $\alpha$ is computed dynamically as $\frac{L_{logits}}{L_{is}}$.[^muralidharanCompactLanguageModels2024] A shared linear transformation upscales the student hidden state to the teacher hidden state dimension, and the hidden states used are always post LayerNorm.[^muralidharanCompactLanguageModels2024]

### Best practices

1. To train a family of LLMs, train the largest one and prune+distill iteratively to smaller LLMs.[^muralidharanCompactLanguageModels2024]
2. Use (batch=L2, seq=mean) importance estimation for width axes and PPL/BI for depth.[^muralidharanCompactLanguageModels2024]
3. Use single-shot importance estimation; iterative provides no benefit.[^muralidharanCompactLanguageModels2024]
4. Prefer width pruning over depth for the model scales considered ($\leq$ 15B).[^muralidharanCompactLanguageModels2024]
5. Retrain exclusively with distillation loss using KLD instead of conventional training.[^muralidharanCompactLanguageModels2024]
6. Use (logit+intermediate state+embedding) distillation when depth is reduced significantly.[^muralidharanCompactLanguageModels2024]
7. Use logit-only distillation when depth isn't reduced significantly.[^muralidharanCompactLanguageModels2024]
8. Prune a model closest to the target size.[^muralidharanCompactLanguageModels2024]
9. Perform lightweight retraining to stabilize the rankings of searched pruned candidates.[^muralidharanCompactLanguageModels2024]
10. If the largest model is trained with a multi-phase training strategy, prune and retrain the model obtained from the final stage of training.[^muralidharanCompactLanguageModels2024]

## Experiments & Results

### Setup

- Base model: Nemotron-4 15B with 15.6 billion parameters, compressed to two target ranges, 8 billion and 4 billion.[^muralidharanCompactLanguageModels2024]
- Framework: NVIDIA Megatron-LM.[^muralidharanCompactLanguageModels2024]
- Data: the Nemotron-4 curated 8 trillion token (8T) base pretraining dataset and the continued training dataset (CT). The 8T blend is used for all ablations and a combination of both for the final models.[^muralidharanCompactLanguageModels2024]
- Lightweight retraining uses 1.8 billion tokens (400 steps) unless otherwise specified.[^muralidharanCompactLanguageModels2024]
- Evaluation: 5-shot MMLU, 5-shot Winogrande, 25-shot ARC-Challenge, 10-shot HellaSwag, 0-shot on 20% of XL-Sum, and pass@1 for HumanEval and MBPP with temperature 0.2 and top-p $=$ 0.95.[^muralidharanCompactLanguageModels2024]
- Compute: 16$\times$ NVIDIA DGX A100 nodes (8$\times$ A100 80GB).[^muralidharanCompactLanguageModels2024]

### Architectures (Table 5)

Vocabulary size is 256k for all models.[^muralidharanCompactLanguageModels2024]

| Model | Layers | Hidden Size | Att. Heads | Query Groups | MLP Hidden | Parameters |
|---|---|---|---|---|---|---|
| Nemotron-4 15B | 32 | 6144 | 48 | 8 | 24576 | 15.6B |
| Nemotron-3 8B | 32 | 4096 | 32 | 32 | 16384 | 8.5B |
| Minitron 8B | 32 | 4096 | 48 | 8 | 16384 | 8.27B |
| Minitron 4B | 32 | 3072 | 24 | 8 | 9216 | 4.19B |

All rows: [^muralidharanCompactLanguageModels2024]

### Minitron 8B vs baselines (Table 2)

The paper states that all evaluations were run by the authors.[^muralidharanCompactLanguageModels2024]

| Benchmark (shots) | Metric | Llama-3 | Llama-2 | Mistral | Gemma | Nemotron-4 | Nemotron-3 | Minitron |
|---|---|---|---|---|---|---|---|---|
| # Parameters | | 8B | 6.7B | 7.3B | 8.5B | 15.6B | 8.5B | 8.3B |
| # Non-Emb. Params | | 5.9B | 6.4B | 7B | 7.7B | 12.5B | 6.4B | 6.2B |
| # Training Tokens | | >15T | 2T | 8T | 6T | 8T | 3.8T | 94B |
| winogrande (5) | acc | 77.6 | 74 | 78.5 | 78 | 83.6 | 75.9 | 79.0 |
| arc_challenge (25) | acc_norm | 57.8 | 53 | 60.3 | 61 | 58.8 | 52.8 | 52.6 |
| MMLU (5) | acc | 65.3 | 46 | 64.1 | 64 | 66.6 | 54.7 | 63.8 |
| hellaswag (10) | acc_norm | 82.1 | 79 | 83.2 | 82 | 84.6 | 78.5 | 80.7 |
| gsm8k (5) | acc | 50.3 | 14 | 37 | 50 | 48.5 | 24.0 | 51.3 |
| truthfulqa (0) | mc2 | 43.9 | 39 | 42.6 | 45 | 40.7 | 36.5 | 42.6 |
| XLSum en (20) (3) | rougeL | 30.9 | 31 | 4.80 | 17 | 32 | 30.9 | 31.2 |
| MBPP (0) | pass@1 | 42.4 | 20 | 38.8 | 39 | 38 | 27.04 | 35.2 |
| humaneval (n=20) (0) | pass@1 | 28.1 | 12 | 28.7 | 32 | 35.4 | 20.7 | 31.6 |

All rows: [^muralidharanCompactLanguageModels2024]

Minitron 8B uses 40$\times$ fewer tokens than Nemotron-3 8B.[^muralidharanCompactLanguageModels2024]

### Minitron 4B vs similarly-sized models (Table 3)

Columns marked `*` are reported from the corresponding papers. Only base models without SFT and DPO are compared.[^muralidharanCompactLanguageModels2024]

| Benchmark (shots) | Metric | Phi-2 | Gemma | Gemma2* | Qwen2* | MiniCPM* | Minitron |
|---|---|---|---|---|---|---|---|
| # Parameters | | 2.7B | 2.5B | 2.6B | 1.5B | 2.7B | 4.2B |
| # Non-Emb. Params | | 2.5B | 2B | 2B | 1.3B | 2.4B | 2.6B |
| # Training Tokens | | 1.4T | 3T | 2T | 7T | 1.1T | 94B |
| winogrande (5) | acc | 74 | 67 | 70.9 | 66.2 | - | 74.0 |
| arc_challenge (25) | acc_norm | 61 | 48 | 55.4 | 43.9 | - | 50.9 |
| MMLU (5) | acc | 57.5 | 42 | 51.3 | 56.5 | 53.5 | 58.6 |
| hellaswag (10) | acc_norm | 75.2 | 72 | 73.0 | 66.6 | 68.3 | 75.0 |
| gsm8k (5) | acc | 55 | 18 | 23.9 | 58.5 | 53.8 | 24.1 |
| truthfulqa (0) | mc2 | 44 | 33 | - | 45.9 | - | 42.9 |
| XLSum en (20) (3) | rougeL | 1 | 11 | - | - | - | 29.5 |
| MBPP (0) | pass@1 | 47 | 29 | 29.6 | 37.4 | - | 28.2 |
| humaneval (n=20) (0) | pass@1 | 50 | 24 | 17.7 | 31.1 | - | 23.3 |

All rows: [^muralidharanCompactLanguageModels2024]

### Minitron vs other pruning methods (Table 4)

| Target | Benchmark | Metric | LLMPruner | SliceGPT | LaCo | ShortGPT | Sheared LLaMa | Minitron |
|---|---|---|---|---|---|---|---|---|
| 8 Billion | # Parameters | | 9.8B | 9.9B | 9.8B | 9.8B | - | 8.3B |
| 8 Billion | # Non-Emb. Params | | 9.5B | 9.5B | 9.5B | 9.5B | - | 6.2B |
| 8 Billion | MMLU (5) | acc | 25.2 | 37.1 | 45.9 | 54.7 | - | 63.8 |
| 8 Billion | hellaswag (10) | acc_norm | 67.8 | 55.7 | 64.4 | 66.6 | - | 80.7 |
| 4 Billion | # Parameters | | 4.8B | 4.9B | 4.9B | 4.9B | 2.7B | 4.2B |
| 4 Billion | # Non-Emb. Params | | 4.5B | 4.6B | 4.6B | 4.6B | 2.5B | 2.6B |
| 4 Billion | winogrande (5) | acc | - | - | - | - | 64.2 | 74 |
| 4 Billion | arc_challenge (25) | acc_norm | - | - | - | - | 41.2 | 50.9 |
| 4 Billion | MMLU (5) | acc | 23.33 | 28.92 | 26.45 | 43.96 | 26.4 | 58.6 |
| 4 Billion | hellaswag (10) | acc_norm | 56.46 | 50.27 | 55.69 | 53.02 | 70.8 | 75 |
| 4 Billion | gsm8k (5) | acc | - | - | - | - | 23.96 | 24.1 |

All rows: [^muralidharanCompactLanguageModels2024]

### Minitron 4B-instruct (Tables 6-9)

Minitron 4B-instruct is Minitron 4B after SFT with the instruction-tuning data used for Nemotron-4 340B.[^muralidharanCompactLanguageModels2024]

| Model | Non-Emb. Params | Tokens | MT-Bench Total |
|---|---|---|---|
| Minitron 4B-instruct | 2.6B | 90B | 6.46 |
| Phi-2 | 2.5B | 1.4T | 4.29 |
| Qwen-1.5 Chat | 1.2B | N/A | 5.29 |
| Gemma-2B-IT | 2B | 6T | 5.19 |
| StableLM 2 Chat | 1.6B | 2T | 5.42 |
| TinyLlama v1.0 Chat | 1.1B | 3T | 3.46 |

All rows: [^muralidharanCompactLanguageModels2024]

| Model | IFEval Prompt-level Acc. (strict) | IFEval Prompt-level Acc. (loose) | IFEval Instruction-level Acc. (loose) | ChatRAG-Bench Avg | BFCL v2 Avg. |
|---|---|---|---|---|---|
| Minitron 4B-instruct | 68.76 | 73.01 | 81.29 | 41.11 | 53.09 |
| Gemma-2B-IT | - | 28.70 | 40.50 | 33.31 | 41.63 |
| Qwen2-1.5B-Instruct | 29 | - | - | not stated | not stated |
| Llama-3-8B-instruct | not stated | not stated | not stated | not stated | 50.51 |

All rows: [^muralidharanCompactLanguageModels2024]

### Pruning-strategy ablations

Pruning Nemotron-4 15B to the size of Nemotron-3 8B, then lightweight retraining with $\sim$1.8B tokens (Table 1). Distillation loss is KL divergence on logits, before $\rightarrow$ after retraining.[^muralidharanCompactLanguageModels2024]

| DEP | MLP | ATT | EMB | Distillation Loss | LM Val Loss |
|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | 5.35 $\rightarrow$ 0.38 | 2.062 |
| × | ✓ | ✓ | ✓ | 6.33 $\rightarrow$ 0.37 | 2.049 |
| × | ✓ | ✓ | × | 5.07 $\rightarrow$ 0.42 | 2.101 |
| ✓ | × | × | × | 8.35 $\rightarrow$ 0.49 | 2.155 |
| Train from scratch (random init) | | | | 12.27 $\rightarrow$ 2.34 | 3.953 |

All rows: [^muralidharanCompactLanguageModels2024]

Depth vs width after retraining with 1.8B tokens (Table 10).[^muralidharanCompactLanguageModels2024]

| Model | Parameters | LM Loss |
|---|---|---|
| Minitron 8B Depth (PPL) | 9.39B | 2.155 |
| Minitron 8B Depth (BI) | 9.39B | 2.177 |
| Minitron 8B Width | 7.74B | 2.049 |
| Minitron 8B Depth + Width | 7.91B | 2.062 |

All rows: [^muralidharanCompactLanguageModels2024]

The depth+width variant has a lower loss right after pruning, and the ranking flips around 200 steps of retraining (0.8B tokens).[^muralidharanCompactLanguageModels2024]

Aggregation metric, zero-shot after pruning Nemotron-4 15B to the Nemotron-3 8B architecture (Table 13).[^muralidharanCompactLanguageModels2024]

| Batch | Sequence | 8T LM Loss | WikiText2 LM Loss |
|---|---|---|---|
| L2 | L2 | 8.73 | 8.37 |
| L2 | mean | 7.18 | 7.23 |
| L2 | var | 8.18 | 8.61 |
| mean | L2 | 8.41 | 7.84 |
| mean | mean | 7.21 | 6.89 |
| mean | var | 7.94 | 8.29 |
| var | L2 | 9.01 | 9.30 |
| var | mean | 8.34 | 8.72 |
| var | var | 10.55 | 11.14 |

All rows: [^muralidharanCompactLanguageModels2024]

Iterative importance estimation when pruning the embedding dimension to 4096 (Table 14).[^muralidharanCompactLanguageModels2024]

| Iterations | Initial (Zero-Shot) Validation Loss | Final Validation Loss |
|---|---|---|
| T=1 | 5.43 | 1.92 |
| T=2 | 5.55 | 1.92 |
| T=4 | 5.24 | 1.92 |

All rows: [^muralidharanCompactLanguageModels2024]

### Retraining ablations

Strategies to train a 4B model (Table 11). `∗` marks iso-compute settings.[^muralidharanCompactLanguageModels2024]

| Model | Tokens | Hellaswag | MMLU |
|---|---|---|---|
| 4B-Random-Init | 150B∗ | 46.22 | 24.36 |
| 4B-Random-Init | 400B | 48.23 | 26.24 |
| 4B-Pruned (prune Nemotron-4 15B) | 150B∗ | 50.85 | 24.57 |
| 4B-Pruned-Distill (prune Nemotron-4 15B) | 100B∗ | 51.04 | 37.81 |
| 4B-Pruned-Distill (prune Minitron 8B) | 100B∗ | 52.04 | 42.45 |

All rows: [^muralidharanCompactLanguageModels2024]

- Pruning the 15B model with distillation gains 4.8% on Hellaswag and 13.5% on MMLU compared to training from scratch with equivalent compute. Pruning an 8B model instead of the 15B model gains an additional 1% and 4.6%.[^muralidharanCompactLanguageModels2024]
- Compressing Nemotron-4 15B to Minitron 4B is a 73.3% reduction of the original model weights. The two-step route (15B to 8B, $\sim$46% reduction, then 8B to 4B, $\sim$50% reduction) achieves a 12% improvement in MMLU scores compared to the one-shot strategy.[^muralidharanCompactLanguageModels2024]
- In the final retraining step, Nemotron-4 15B as the teacher gives better results than Minitron 8B as the teacher.[^muralidharanCompactLanguageModels2024]

Loss functions and components on Nemotron-3 8B (Table 15).[^muralidharanCompactLanguageModels2024]

| Loss | LM loss | WikiText PPL |
|---|---|---|
| $L_{CLM}$ + $L_{logits}$(MSE) | 2.144 | 9.007 |
| $L_{CLM}$ + $L_{logits}$(RKLD) | 2.140 | 9.008 |
| $L_{CLM}$ + $L_{logits}$(Cosine) | 2.134 | 8.965 |
| $L_{CLM}$ + $L_{logits}$(KLD) | 2.117 | 8.791 |
| $L_{logits}$(KLD) | 2.107 | 8.720 |

All rows: [^muralidharanCompactLanguageModels2024]

- On Minitron 8B-Depth-pruned (Table 16), LM loss is 2.665 with $L_{logits}$(RKLD) and 2.155 with $L_{logits}$(KLD).[^muralidharanCompactLanguageModels2024]
- Softmax temperature $\tau$ was tried at 0.1, 0.5, 1.0, 3.0, and $\tau$=1.0 was best. Top-K filtering of logits with a low value (<=100) caused a significant drop in accuracy and larger values were no better than no top-K.[^muralidharanCompactLanguageModels2024]
- Intermediate-state loss on Minitron 8B-Depth-pruned (Table 17): $L_{logits}$ alone gives LM loss 2.155, and $L_{logits}$ + $L_{o}$(29:13) + $L_{emb}$ gives 2.141, where (29:13) is the (teacher:student) layer mapping.[^muralidharanCompactLanguageModels2024]

Effect of $L_{is}$ and token count for Minitron 8B (Table 18).[^muralidharanCompactLanguageModels2024]

| Loss | Tokens | MMLU | HellaSwag | HumanEval |
|---|---|---|---|---|
| $L_{logits}+L_{is}$ | 18.9B | 58.0 | 73.6 | 26.8 |
| $L_{logits}$ | 18.9B | 58.3 | 73.8 | 26.2 |
| $L_{logits}$ | 94B | 62.8 | 79.7 | 30.4 |

All rows: [^muralidharanCompactLanguageModels2024]

Single vs multi-phase retraining with Minitron 8B-Width-pruned, which is not the searched 8B model of Table 2 (Table 20).[^muralidharanCompactLanguageModels2024]

| Strategy | Tokens | MMLU | HellaSwag | PIQA | HumanEval |
|---|---|---|---|---|---|
| Phase1 + Phase2 | 113B | 54.7 | 80.3 | 77.2 | 25.6 |
| Phase2 only | 94B | 61.9 | 80.1 | 76.7 | 30.5 |

All rows: [^muralidharanCompactLanguageModels2024]

### Depth pruning: one-shot vs iterative

- Iteratively removing the least important layer and distilling with 1.8B tokens, repeated 16 times, is compared with removing 16 layers at once and distilling with 1.8B $\times$ 16 (30.2B) tokens. Raising the iterative budget to 86.4B tokens in total improves accuracy but still performs worse than the one-shot strategy that uses 30.2B tokens.[^muralidharanCompactLanguageModels2024]
- With the iterative strategy, Hellaswag and PIQA accuracy is retained up to 31 layers, with a sharper drop at 25 layers. MMLU is retained up to 26 layers, with a sharp drop at 20 layers.[^muralidharanCompactLanguageModels2024]

### Search

Search space (Table 12), with a target of 8 and 4 billion parameters and a tolerance of 5%.[^muralidharanCompactLanguageModels2024]

| Target | Layers | Heads | MLP Exp. Factor | Embedding |
|---|---|---|---|---|
| Minitron 8B | [29-32] | {32,48} | {2.5,3,3.5,4} | {4096,4680,5120,5632,6144} |
| Minitron 4B | [29-32] | {24,32,48} | {2.5,3,3.5,4} | {2560,3072,3584,4096,4608} |

All rows: [^muralidharanCompactLanguageModels2024]

The search yields 15 and 18 feasible candidates for the 8B and 4B targets. Relative rankings of the 8B candidates change significantly up to $\sim$ 300 steps of retraining and then stabilize.[^muralidharanCompactLanguageModels2024]

### Training cost

FLOPs per training step (batch size 1152) for the 15B, 8B, and 4B models are $4.4\text{e}17$, $2.5\text{e}17$ and $1.2\text{e}17$. From scratch the family costs $(4.4\text{e}17+2.5\text{e}17+1.2\text{e}17)\times\text{steps}$, and with this approach $(4.4\text{e}17+2.5\text{e}17/40+1.2\text{e}17/40)\times\text{steps}$, a saving of $1.8\times$.[^muralidharanCompactLanguageModels2024]

## Limitations

- The preference for width over depth pruning is stated for the model scales considered ($\leq$ 15B).[^muralidharanCompactLanguageModels2024]
- Parameter-efficient fine-tuning such as LoRA for the lightweight retraining stage is left to future work.[^muralidharanCompactLanguageModels2024]
- Attention-score losses could not be tested because of Flash Attention abstractions.[^muralidharanCompactLanguageModels2024]
- The loss-function study was done mostly on the previous generation of Nemotron models, and only a subset was repeated with the Section 4 setup.[^muralidharanCompactLanguageModels2024]
- Minitron 8B is below Nemotron-3 8B on arc_challenge (52.6 vs 52.8), and Minitron 4B is well below Phi-2 and Qwen2 on gsm8k (24.1 vs 55 and 58.5) and on the coding benchmarks.[^muralidharanCompactLanguageModels2024]
- The paper has no dedicated limitations section.

## Related

- Methods proposed or built on: [Minitron](../methods/minitron.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Neural architecture search](../methods/neural-architecture-search.md)
- Pruning methods compared: [Sheared LLaMA](../methods/sheared-llama.md), [LLM-Pruner](../methods/llm-pruner.md), [SliceGPT](../methods/slicegpt.md), [LaCo](../methods/laco.md), [ShortGPT](../methods/shortgpt.md)
- Benchmarks: [MMLU](../datasets/mmlu.md), [HellaSwag](../datasets/hellaswag.md), [GSM8K](../datasets/gsm8k.md), [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [MT-Bench](../datasets/mt-bench.md), [BFCL](../benchmarks/bfcl.md)
- Papers in this wiki cited by this paper: [Sheared LLaMA](xiaShearedLLaMAAccelerating2024.md)

[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
