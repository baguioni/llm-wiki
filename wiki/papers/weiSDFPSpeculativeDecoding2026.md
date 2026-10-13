---
type: Paper
title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
description: Training-free speculative decoding that builds the draft model by pruning the target LLM's least sensitive layers, ranked by Fisher Information Trace computed on WikiText2.
tags: [speculative-decoding, draft-model, layer-pruning, fisher-information, training-free, llm-inference, speculative-drafter]
collections: [speculative drafter]
authors: [Hanyu Wei, Zunhai Su, Peng Lu, Chao Li, Spandan Tiwari, Ashish Sirasao, Yuhan Dong]
year: 2026
doi: 10.48550/arXiv.2602.05499
arxiv: "2602.05499"
arxiv_version: 2602.05499v1
sources:
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
---

# SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration

Text source: arXiv HTML, version `2602.05499v1`.

## Summary

[Speculative decoding](../methods/speculative-decoding.md) (SD) lets a lightweight draft model propose several tokens that the target LLM verifies in parallel, which preserves the target's output distribution.[^weiSDFPSpeculativeDecoding2026] The paper argues that acquiring, tuning, and maintaining the draft model, not the decoding algorithm, is the primary barrier to practical deployment.[^weiSDFPSpeculativeDecoding2026]

[SDFP](../methods/sdfp.md) builds the draft by pruning layers of the target LLM itself. It ranks layers by [Fisher Information Trace](../methods/fisher-information-trace.md) (FIT) and removes the least sensitive ones, with no training, hyperparameter tuning, or separately maintained draft.[^weiSDFPSpeculativeDecoding2026] On LLaMA-2 models the paper reports overall speedups of $1.31\times$ to $1.46\times$ over vanilla autoregressive decoding, which is comparable to [SWIFT](../methods/swift.md) ($1.34\times$ to $1.48\times$).[^weiSDFPSpeculativeDecoding2026] The abstract states the range as 1.32×–1.5×.[^weiSDFPSpeculativeDecoding2026]

## Contributions

- The paper claims to be the first to use FIT as a sensitivity criterion for draft model construction in speculative decoding.[^weiSDFPSpeculativeDecoding2026]
- A fully training-free, plug-and-play framework that builds the draft by FIT-based [layer pruning](../methods/layer-pruning.md). FIT is estimated with a single forward–backward pass per minibatch over a small calibration set, without second-order derivatives, architecture search, or task-specific fine-tuning.[^weiSDFPSpeculativeDecoding2026]
- An evaluation on three LLaMA-2 models and three tasks against training-free baselines.[^weiSDFPSpeculativeDecoding2026]

## Method

### FIT as layer sensitivity

- The KL divergence between the original and perturbed output distributions is approximated as $D_{\mathrm{KL}}(p_{\theta}\|p_{\theta+\delta\theta})=\frac{1}{2}\,\delta\theta^{\top}I(\theta)\,\delta\theta$, where $I(\theta)$ is the Fisher Information Matrix.[^weiSDFPSpeculativeDecoding2026]
- Assuming zero-mean uncorrelated pruning or quantization noise, the expected degradation in layer-wise form is $\Omega=\sum_{l=1}^{L}\operatorname{Tr}\!\left(I(\theta_{l})\right)\,\mathbb{E}[\delta\theta_{l}^{2}]$.[^weiSDFPSpeculativeDecoding2026]
- The trace uses the empirical Fisher approximation: $T_{l}=\operatorname{Tr}\!\left[\widehat{I}(\theta_{l})\right]=\frac{1}{N}\sum_{i=1}^{N}\|\nabla_{\theta_{l}}f(z_{i},\theta)\|_{2}^{2}$, where $f(z_{i},\theta)$ is the per-sample loss.[^weiSDFPSpeculativeDecoding2026]
- For pruning, the perturbation variance is assumed approximately layer-wise constant, so FIT is proportional to the empirical Fisher trace, which is the practical layer score.[^weiSDFPSpeculativeDecoding2026]
- The paper states that the variance of this estimator is orders of magnitude smaller than that of Hutchinson-based Hessian trace estimators.[^weiSDFPSpeculativeDecoding2026]

### Stage A: FIT-based pruning

1. Compute $T_{\ell}$ for every layer by accumulating squared gradient norms over minibatches of the calibration set, here the general-purpose [WikiText2](../datasets/wikitext-2.md) dataset.[^weiSDFPSpeculativeDecoding2026]
2. Sort layers by ascending $T_{\ell}$ and select a prune set $\mathcal{P}$ with $|\mathcal{P}|=\lfloor rL\rfloor$ for pruning ratio $r$.[^weiSDFPSpeculativeDecoding2026]
3. Remove the layers in $\mathcal{P}$ to form the draft model.[^weiSDFPSpeculativeDecoding2026]

The pruning ratio follows the layer-sparsity proportions derived from prior Bayesian learning-based pruning methods.[^weiSDFPSpeculativeDecoding2026] For LLaMA-2-13B, 50% of attention layers and 35% of FFN layers are pruned.[^weiSDFPSpeculativeDecoding2026]

### Stage B: speculative decoding with the pruned draft

- The pruned model is the draft and the original full LLaMA-2 model is the target.[^weiSDFPSpeculativeDecoding2026]
- The draft proposes a $k$-token block. Each token is accepted with probability $\alpha_{i}=\min\!\left(1,\frac{p_{\theta}}{q_{\phi}}\right)$, and on the first rejection the next token is sampled from the corrected distribution $r(y)\propto p_{\theta}(y)-\alpha_{j}q_{\phi}(y)$.[^weiSDFPSpeculativeDecoding2026]
- Because the draft comes from the same pretrained LLM by structured layer pruning, it stays architecture-compatible with the target, which enables KV reuse during verification.[^weiSDFPSpeculativeDecoding2026]

## Experiments & Results

### Setup

- Models: LLaMA-2-13B, LLaMA-2-13B-Chat, LLaMA-2-70B.[^weiSDFPSpeculativeDecoding2026]
- Tasks: [CNN/Daily Mail](../datasets/cnn-dailymail.md) (summarization), [GSM8K](../datasets/gsm8k.md) (reasoning), [TinyStories](../datasets/tinystories.md) (narrative generation).[^weiSDFPSpeculativeDecoding2026]
- Maximum output length is 64 for CNN/DM and GSM8K, and 128 for TinyStories. CNN/DM and TinyStories are 1-shot and GSM8K is 5-shot.[^weiSDFPSpeculativeDecoding2026]
- 1,000 randomly sampled test instances per dataset, batch size 1, greedy decoding.[^weiSDFPSpeculativeDecoding2026]
- Baselines: [Parallel Decoding](../methods/parallel-decoding.md), [Lookahead Decoding](../methods/lookahead-decoding.md), and SWIFT.[^weiSDFPSpeculativeDecoding2026] Methods that need auxiliary networks or fine-tuning, such as [EAGLE](../methods/eagle.md) and [Medusa](../methods/medusa.md), are excluded.[^weiSDFPSpeculativeDecoding2026]
- Metrics: token acceptance rate $\alpha$, decoding throughput (tokens/s), and wall-time speedup over vanilla autoregressive decoding.[^weiSDFPSpeculativeDecoding2026] Generation quality is not evaluated.[^weiSDFPSpeculativeDecoding2026]
- Evaluation hardware for Table I: not stated.

### Main results (Table I)

$\alpha$ is the acceptance rate. Speed is the average decoding speed in tokens/s.[^weiSDFPSpeculativeDecoding2026]

| Model | Method | CNN/DM $\alpha$ | CNN/DM Speedup | GSM8K $\alpha$ | GSM8K Speedup | TinyStories $\alpha$ | TinyStories Speedup | Speed (tokens/s) | Overall Speedup |
|---|---|---|---|---|---|---|---|---|---|
| LLaMA-2-13B | VANILLA | N/A | $1.00\times$ | N/A | $1.00\times$ | N/A | $1.00\times$ | 20.10 | $1.00\times$ |
| LLaMA-2-13B | PARALLEL | N/A | $0.95\times$ | N/A | $0.99\times$ | N/A | $0.97\times$ | 19.49 | $0.97\times$ |
| LLaMA-2-13B | LOOKAHEAD | N/A | $1.16\times$ | N/A | $1.29\times$ | N/A | $1.35\times$ | 25.46 | $1.27\times$ |
| LLaMA-2-13B | SWIFT | 0.99 | $1.37\times$ | 0.98 | $1.31\times$ | 1.00 | $1.53\times$ | 28.26 | $1.41\times$ |
| LLaMA-2-13B | SDFP | 0.95 | $1.32\times$ | 0.95 | $1.36\times$ | 0.98 | $1.49\times$ | 28.05 | $1.40\times$ |
| LLaMA-2-13B-Chat | VANILLA | N/A | $1.00\times$ | N/A | $1.00\times$ | N/A | $1.00\times$ | 19.96 | $1.00\times$ |
| LLaMA-2-13B-Chat | PARALLEL | N/A | $0.96\times$ | N/A | $0.97\times$ | N/A | $0.98\times$ | 19.26 | $0.97\times$ |
| LLaMA-2-13B-Chat | LOOKAHEAD | N/A | $1.15\times$ | N/A | $1.31\times$ | N/A | $1.40\times$ | 25.69 | $1.29\times$ |
| LLaMA-2-13B-Chat | SWIFT | 0.90 | $1.28\times$ | 0.92 | $1.25\times$ | 0.99 | $1.50\times$ | 26.80 | $1.34\times$ |
| LLaMA-2-13B-Chat | SDFP | 0.92 | $1.23\times$ | 0.92 | $1.27\times$ | 0.95 | $1.44\times$ | 26.21 | $1.31\times$ |
| LLaMA-2-70B | VANILLA | N/A | $1.00\times$ | N/A | $1.00\times$ | N/A | $1.00\times$ | 4.32 | $1.00\times$ |
| LLaMA-2-70B | PARALLEL | N/A | $0.95\times$ | N/A | $0.97\times$ | N/A | $0.96\times$ | 4.14 | $0.96\times$ |
| LLaMA-2-70B | LOOKAHEAD | N/A | $1.15\times$ | N/A | $1.35\times$ | N/A | $1.35\times$ | 5.45 | $1.26\times$ |
| LLaMA-2-70B | SWIFT | 0.99 | $1.43\times$ | 0.98 | $1.39\times$ | 0.99 | $1.62\times$ | 6.41 | $1.48\times$ |
| LLaMA-2-70B | SDFP | 0.96 | $1.45\times$ | 0.95 | $1.37\times$ | 0.95 | $1.55\times$ | 6.29 | $1.46\times$ |

All rows: [^weiSDFPSpeculativeDecoding2026]

SDFP is below SWIFT on overall speedup for all three models ($1.40\times$ vs $1.41\times$, $1.31\times$ vs $1.34\times$, $1.46\times$ vs $1.48\times$), and above it on GSM8K for the two 13B models and on CNN/DM for LLaMA-2-70B.[^weiSDFPSpeculativeDecoding2026]

### Draft construction overhead for LLaMA-2-13B (Table II)

Training cost is reported from the original papers. Optimization latency is measured on a single A6000 GPU.[^weiSDFPSpeculativeDecoding2026]

| Method | Training Cost | Optimization Latency |
|---|---|---|
| [LayerSkip](../methods/layerskip.md)-SD | $50\times 10^{3}$ training steps with 64 A100 (80GB) | N/A |
| SELF-SD | 1000 Bayesian Optimization Iterations Before inference | $\sim$7.5 hours |
| SWIFT | N/A | $\sim$A few minutes each time |
| SDFP | N/A | N/A |

All rows: [^weiSDFPSpeculativeDecoding2026]

## Limitations

- The paper has no limitations section.
- SDFP does not exceed SWIFT on overall speedup for any of the three models. The paper describes the result as "comparable" to prior state-of-the-art methods.[^weiSDFPSpeculativeDecoding2026]
- The abstract and conclusion state a 1.32×–1.5× speedup, but SDFP's values in Table I range from $1.23\times$ (LLaMA-2-13B-Chat, CNN/DM) to $1.55\times$ (LLaMA-2-70B, TinyStories).[^weiSDFPSpeculativeDecoding2026]
- The pruning ratio is not derived by SDFP. It follows layer-sparsity proportions from prior Bayesian learning-based pruning methods, and the LLaMA-2-13B configuration is described as identified through extensive empirical evaluation.[^weiSDFPSpeculativeDecoding2026]
- Only the LLaMA-2-13B pruning ratio is given. The ratios for the other models, the speculation depth $k$, and the calibration set size are not stated.[^weiSDFPSpeculativeDecoding2026]
- No comparison with trained-draft methods (EAGLE, Medusa), and no ablation of FIT against other layer-selection criteria.[^weiSDFPSpeculativeDecoding2026]
- Table II reports SDFP's optimization latency as N/A, and the time of the FIT pass itself is not reported.[^weiSDFPSpeculativeDecoding2026]
- SELF-SD appears in Table II but is not described or cited in the text.[^weiSDFPSpeculativeDecoding2026]

## Related

- Methods proposed: [SDFP](../methods/sdfp.md)
- Methods built on: [Speculative decoding](../methods/speculative-decoding.md), [Fisher Information Trace](../methods/fisher-information-trace.md), [Layer pruning](../methods/layer-pruning.md)
- Methods compared against: [SWIFT](../methods/swift.md), [Lookahead Decoding](../methods/lookahead-decoding.md), [Parallel Decoding](../methods/parallel-decoding.md), [LayerSkip](../methods/layerskip.md)
- Methods excluded from comparison: [EAGLE](../methods/eagle.md), [Medusa](../methods/medusa.md)
- Datasets: [CNN/Daily Mail](../datasets/cnn-dailymail.md), [GSM8K](../datasets/gsm8k.md), [TinyStories](../datasets/tinystories.md), [WikiText2](../datasets/wikitext-2.md)
- Papers in this wiki cited by this paper: [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md)

[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
