---
type: Paper
title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
description: Speculative sampling draft model that drops EAGLE's feature prediction for direct token prediction with training-time test and fuses low-, mid-, and high-level target features.
tags: [speculative-decoding, draft-model, training-time-test, feature-fusion, llm-inference, mobile-specedge]
collections: ["mobile-specedge"]
authors: [Yuhui Li, Fangyun Wei, Chao Zhang, Hongyang Zhang]
doi: 10.48550/arXiv.2503.01840
arxiv: "2503.01840"
arxiv_version: 2503.01840v3
code: https://github.com/SafeAILab/EAGLE
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
---

# EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test

Text source: arXiv HTML, version `2503.01840v3`.

## Summary

[EAGLE](../methods/eagle.md) performs autoregression at the feature level: it reuses the top-layer features of the target model, predicts the next feature, and obtains the draft token from the target model's LM head.[^liEAGLE3ScalingInference2025] The authors observe that scaling up training data gives limited improvement for EAGLE and attribute this to its feature prediction constraint.[^liEAGLE3ScalingInference2025]

[EAGLE-3](../methods/eagle-3.md) abandons feature prediction for direct token prediction, and replaces reliance on top-layer features with multi-layer feature fusion, through a technique named [training-time test](../methods/training-time-test.md).[^liEAGLE3ScalingInference2025] The paper reports a speedup ratio up to 6.5x, about 1.4x improvement over [EAGLE-2](../methods/eagle-2.md), and a 1.38x throughput improvement at a batch size of 64 in the [SGLang](../methods/sglang.md) framework.[^liEAGLE3ScalingInference2025]

## Contributions

- A training-time test architecture for the draft model: the feature prediction constraint is removed, tokens are predicted directly, and multi-step generation is simulated during training. The draft model's input integrates low-, mid-, and high-level features from the target model.[^liEAGLE3ScalingInference2025]
- A scaling law for inference acceleration: with the new architecture, increasing the amount of draft-model training data leads to a proportional increase in the speedup ratio. This was not observed for the original EAGLE architecture.[^liEAGLE3ScalingInference2025]
- Improved acceleration: EAGLE-3, trained with approximately 8x more data than EAGLE, achieves a 1.4x latency speedup over EAGLE-2 at batch size 1.[^liEAGLE3ScalingInference2025]

## Method

### Why EAGLE does not scale with data

- EAGLE's loss has a feature prediction loss $l_{fea}$ and a token prediction loss $l_{token}$. The feature prediction loss lets a draft model trained only at Step 1 adapt to Step 2. With token prediction as the goal, feature prediction acts as an additional constraint that limits the expressiveness of the draft model.[^liEAGLE3ScalingInference2025]
- Removing the feature constraint and expanding the training data improves the acceptance rate $0$-$\alpha$ of the first draft token significantly. But the Step 1 output $\hat{a}_{t+1}$ is far from the ground truth $f_{t+1}$, so the Step 2 input deviates from the training distribution and the acceptance rate $1$-$\alpha$ of the second draft token is very low.[^liEAGLE3ScalingInference2025]
- Incorporating Step 1 into the training process fixes this. The authors name the technique training-time test.[^liEAGLE3ScalingInference2025]

### Inference pipeline

- EAGLE-3 alternates between drafting and verification like other speculative sampling methods ([speculative decoding](../methods/speculative-decoding.md)). It differs from EAGLE in the drafting stage.[^liEAGLE3ScalingInference2025]
- From the target model's forward pass, the low, middle, and high-level feature sequences $l$, $m$, $h$ are recorded. The three $k$-dimensional vectors are concatenated into a $3k$-dimensional vector and passed through a fully connected (FC) layer that reduces it to $k$ dimensions, giving the fused feature $g$. $k$ is the hidden size of the target model.[^liEAGLE3ScalingInference2025]
- $g$ is concatenated with the embedding $e$ of the sampled token, reduced to $k$ dimensions by an FC layer, and fed into a single layer decoder that outputs $a$. $a$ goes into the LM head, and sampling gives the draft token.[^liEAGLE3ScalingInference2025]
- For later steps, $g$ of an unverified token is not available, so the draft model's own output $a$ from the previous step replaces it and is concatenated with the embedding of the sampled token.[^liEAGLE3ScalingInference2025]
- EAGLE-3 adopts the context-aware dynamic draft tree of EAGLE-2.[^liEAGLE3ScalingInference2025]

### Draft model training

- The draft-model input may be target features $g_1,\cdots,g_t$ or draft outputs $a_{t+1},\cdots,a_{t+j}$. During training, test steps generate $a$ and feed it back into the draft model for further training.[^liEAGLE3ScalingInference2025]
- The core of the draft model is a Transformer decoder layer. Only the self-attention needs modification: the attention mask is adjusted in the simulated steps to respect the tree-like contextual relationship. All attention masks are diagonal except when the original training data is used as the key, so attention scores are computed with vector dot products only for the corresponding positions.[^liEAGLE3ScalingInference2025]
- Difference from [HASS](../methods/hass.md): HASS makes similar attention modifications to simulate testing during training, but it still performs feature prediction, includes the feature prediction loss $l_{fea}$, and requires the draft input to be the top-layer features.[^liEAGLE3ScalingInference2025]

### Implementation

| Item | Value |
|---|---|
| Optimizer | AdamW, $(\beta_1,\beta_2)$ = (0.9, 0.95), gradient clipping of 0.5 |
| Learning rate | 5e-5 |
| Training data | [ShareGPT](../datasets/sharegpt.md) (approximately 68K entries) and UltraChat-200K (approximately 464K entries); responses are generated by calling the target model |
| Extra data for DeepSeek-R1-Distill-LLaMA 8B | OpenThoughts-114k-math |
| Draft tree | Depth increased from 6 (EAGLE-2) to 8, with the same number of nodes as EAGLE-2 |
| EAGLE-2 settings | Total draft tokens 60, 50, and 48 for the 7B (8B), 13B, and 70B LLMs; tree depth 6; 10 nodes selected during the expansion phase |

All rows: [^liEAGLE3ScalingInference2025]

## Experiments & Results

### Setup

- Target models: Vicuna 13B, LLaMA-Instruct 3.1 8B, LLaMA-Instruct 3.3 70B, DeepSeek-R1-Distill-LLaMA 8B.[^liEAGLE3ScalingInference2025]
- Tasks, following EAGLE and [Spec-Bench](../benchmarks/spec-bench.md), with the same weights for all tasks: multi-turn conversation ([MT-bench](../datasets/mt-bench.md)), code generation ([HumanEval](../datasets/humaneval.md)), mathematical reasoning ([GSM8K](../datasets/gsm8k.md)), instruction following ([Alpaca](../datasets/alpaca.md)), summarization ([CNN/Daily Mail](../datasets/cnn-dailymail.md)).[^liEAGLE3ScalingInference2025]
- Metrics: speedup ratio relative to vanilla autoregressive decoding, average acceptance length $\tau$ (average number of tokens generated per drafting-verification cycle), and acceptance rate $n$-$\alpha$ (with $n$ self-predicted inputs, measured with a chain-like draft).[^liEAGLE3ScalingInference2025]
- Generation quality is not evaluated, because EAGLE-3 does not modify the target model's weights and uses strict speculative sampling acceptance conditions.[^liEAGLE3ScalingInference2025]
- Baseline (1.00x): Huggingface.transformers models with the PyTorch backend and pre-allocated KV cache.[^liEAGLE3ScalingInference2025]
- Hardware for Table 1 is not stated.

### Speedup ratio and average acceptance length (Table 1)

V = Vicuna, L31 = LLaMA-Instruct 3.1, L33 = LLaMA-Instruct 3.3, DSL = DeepSeek-R1-Distill-LLaMA. SpS is standard speculative sampling with Vicuna-68M as draft model. Each cell is speedup / $\tau$.[^liEAGLE3ScalingInference2025]

Temperature=0:

| Model | Method | MT-bench | HumanEval | GSM8K | Alpaca | CNN/DM | Mean |
|---|---|---|---|---|---|---|---|
| V 13B | SpS | 1.93x / 2.27 | 2.23x / 2.57 | 1.77x / 2.01 | 1.76x / 2.03 | 1.93x / 2.33 | 1.92x / 2.24 |
| V 13B | PLD | 1.58x / 1.63 | 1.85x / 1.93 | 1.68x / 1.73 | 1.16x / 1.19 | 2.42x / 2.50 | 1.74x / 1.80 |
| V 13B | Medusa | 2.07x / 2.59 | 2.50x / 2.78 | 2.23x / 2.64 | 2.08x / 2.45 | 1.71x / 2.09 | 2.12x / 2.51 |
| V 13B | Lookahead | 1.65x / 1.69 | 1.71x / 1.75 | 1.81x / 1.90 | 1.46x / 1.51 | 1.46x / 1.50 | 1.62x / 1.67 |
| V 13B | Hydra | 2.88x / 3.65 | 3.28x / 3.87 | 2.93x / 3.66 | 2.86x / 3.53 | 2.05x / 2.81 | 2.80x / 3.50 |
| V 13B | EAGLE | 3.07x / 3.98 | 3.58x / 4.39 | 3.08x / 3.97 | 3.03x / 3.95 | 2.49x / 3.52 | 3.05x / 3.96 |
| V 13B | EAGLE-2 | 4.26x / 4.83 | 4.96x / 5.41 | 4.22x / 4.79 | 4.25x / 4.89 | 3.40x / 4.21 | 4.22x / 4.83 |
| V 13B | EAGLE-3 | 5.58x / 6.65 | 6.47x / 7.54 | 5.32x / 6.29 | 5.16x / 6.17 | 5.01x / 6.47 | 5.51x / 6.62 |
| L31 8B | EAGLE-2 | 3.16x / 4.05 | 3.66x / 4.71 | 3.39x / 4.24 | 3.28x / 4.12 | 2.65x / 3.45 | 3.23x / 4.11 |
| L31 8B | EAGLE-3 | 4.40x / 6.13 | 4.85x / 6.74 | 4.48x / 6.23 | 4.82x / 6.70 | 3.65x / 5.34 | 4.44x / 6.23 |
| L33 70B | EAGLE-2 | 2.83x / 3.67 | 3.12x / 4.09 | 2.83x / 3.69 | 3.03x / 3.92 | 2.44x / 3.55 | 2.85x / 3.78 |
| L33 70B | EAGLE-3 | 4.11x / 5.63 | 4.79x / 6.52 | 4.34x / 6.15 | 4.30x / 6.09 | 3.27x / 5.02 | 4.12x / 5.88 |
| DSL 8B | EAGLE-2 | 2.92x / 3.80 | 3.42x / 4.29 | 3.40x / 4.40 | 3.01x / 3.80 | 3.53x / 3.33 | 3.26x / 3.92 |
| DSL 8B | EAGLE-3 | 4.05x / 5.58 | 4.59x / 6.38 | 5.01x / 6.93 | 3.65x / 5.37 | 3.52x / 4.92 | 4.16x / 5.84 |

Temperature=1 (methods such as Medusa relax acceptance conditions under non-greedy settings and are not compared):

| Model | Method | MT-bench | HumanEval | GSM8K | Alpaca | CNN/DM | Mean |
|---|---|---|---|---|---|---|---|
| V 13B | SpS | 1.62x / 1.84 | 1.72x / 1.97 | 1.46x / 1.73 | 1.52x / 1.78 | 1.66x / 1.89 | 1.60x / 1.84 |
| V 13B | EAGLE | 2.32x / 3.20 | 2.65x / 3.63 | 2.57x / 3.60 | 2.45x / 3.57 | 2.23x / 3.26 | 2.44x / 3.45 |
| V 13B | EAGLE-2 | 3.80x / 4.40 | 4.22x / 4.89 | 3.77x / 4.41 | 3.78x / 4.37 | 3.25x / 3.97 | 3.76x / 4.41 |
| V 13B | EAGLE-3 | 4.57x / 5.42 | 5.15x / 6.22 | 4.71x / 5.58 | 4.49x / 5.39 | 4.33x / 5.72 | 4.65x / 5.67 |
| L31 8B | EAGLE-2 | 2.44x / 3.16 | 3.39x / 4.39 | 2.86x / 3.74 | 2.83x / 3.65 | 2.44x / 3.14 | 2.80x / 3.62 |
| L31 8B | EAGLE-3 | 3.07x / 4.24 | 4.13x / 5.82 | 3.32x / 4.59 | 3.90x / 5.56 | 2.99x / 4.39 | 3.45x / 4.92 |
| L33 70B | EAGLE-2 | 2.73x / 3.51 | 2.89x / 3.81 | 2.52x / 3.36 | 2.77x / 3.73 | 2.32x / 3.27 | 2.65x / 3.54 |
| L33 70B | EAGLE-3 | 3.96x / 5.45 | 4.36x / 6.16 | 4.17x / 5.95 | 4.14x / 5.87 | 3.11x / 4.88 | 3.95x / 5.66 |
| DSL 8B | EAGLE-2 | 2.69x / 3.41 | 3.01x / 3.82 | 3.16x / 4.05 | 2.64x / 3.29 | 2.35x / 3.13 | 2.77x / 3.54 |
| DSL 8B | EAGLE-3 | 3.20x / 4.49 | 3.77x / 5.28 | 4.38x / 6.10 | 3.16x / 4.30 | 3.08x / 4.27 | 3.52x / 4.89 |

All rows of both tables: [^liEAGLE3ScalingInference2025]

- The paper summarizes this as a speedup of approximately 3.0x-6.5x over vanilla autoregressive generation, with a 20%-40% improvement over EAGLE-2.[^liEAGLE3ScalingInference2025]
- EAGLE-3 performs best on HumanEval, which the authors attribute to the many fixed templates in code generation. DeepSeek-R1-Distill-LLaMA 8B is an exception, with its highest speedup on GSM8K. The authors suggest this may be due to training its draft model on OpenThoughts-114k-math.[^liEAGLE3ScalingInference2025]
- On MT-bench with LLaMA-Instruct 3.1 8B, EAGLE's acceptance rate drops significantly as more of the input comes from the draft model itself, whereas EAGLE-3's remains almost unchanged (Figure 7, no table).[^liEAGLE3ScalingInference2025]

### Ablation (Table 2, LLaMA-Instruct 3.1 8B)

| Method | MT-bench speedup | MT-bench $\tau$ | GSM8K speedup | GSM8K $\tau$ |
|---|---|---|---|---|
| EAGLE-2 | 3.16x | 4.05 | 3.39x | 4.24 |
| + remove fea con | 3.82x | 5.37 | 3.77x | 5.22 |
| + fused features (ours) | 4.40x | 6.13 | 4.48x | 6.23 |

"Remove fea con" removes the feature prediction constraint. "Fused features" replaces top-layer features with the fusion of low, middle, and high-level features.[^liEAGLE3ScalingInference2025]

### EAGLE-3 in SGLang (Table 3)

Throughput improvement on a single H100 GPU with LLaMA-Instruct 3.1 8B on MT-Bench, SGLang v0.4.4, baseline SGLang without speculative sampling (1.00x). No tree structure, chain length 3. The experiments were conducted by the SGLang team.[^liEAGLE3ScalingInference2025]

| Batch size | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 | 64 |
|---|---|---|---|---|---|---|---|---|---|
| EAGLE | 1.40x | 1.38x | 1.23x | 1.02x | 0.93x | 0.94x | 0.88x | 0.99x | 0.99x |
| EAGLE-3 | 1.81x | 1.82x | 1.62x | 1.48x | 1.39x | 1.32x | 1.38x | 1.34x | 1.38x |

Throughput at batch size 1 on H100, same model and dataset (Table 4):[^liEAGLE3ScalingInference2025]

| Method | Throughput (bs=1) |
|---|---|
| SGLang (w/o speculative, 1x H100) | 158.34 tokens/s |
| SGLang + EAGLE-2 (1x H100) | 244.10 tokens/s |
| SGLang + EAGLE-3 (1x H100) | 373.25 tokens/s |

### EAGLE-3 in vLLM (Table 5)

Throughput improvement with LLaMA-Instruct 3.1 8B on MT-Bench, baseline [vLLM](../methods/vllm.md) without speculative sampling (1.00x). No tree structure, maximum chain length 2. The body text gives the GPU as RTX3090 and the table caption gives it as A100.[^liEAGLE3ScalingInference2025]

| Batch size | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 |
|---|---|---|---|---|---|---|---|---|
| EAGLE | 1.30x | 1.25x | 1.21x | 1.10x | 1.03x | 0.93x | 0.82x | 0.71x |
| EAGLE-3 | 1.75x | 1.68x | 1.58x | 1.49x | 1.42x | 1.36x | 1.21x | 1.01x |

## Limitations

- Due to the GPU constraint, EAGLE-3 is not tested on the 405B and 671B models.[^liEAGLE3ScalingInference2025]
- As batch sizes increase, the redundant computational power that speculative sampling exploits decreases, which reduces its effectiveness. In vLLM the EAGLE-3 gain falls to 1.01x at batch size 56.[^liEAGLE3ScalingInference2025]
- The SGLang and vLLM experiments use a chain draft (no tree structure), unlike the Table 1 experiments.[^liEAGLE3ScalingInference2025]
- The paper has no dedicated limitations section.

## Inconsistencies in the source

- The text says EAGLE-3 achieves the highest speedup ratio on all tasks and target models, but Table 1 at temperature=0 lists DSL 8B on CNN/DM as 3.53x for EAGLE-2 and 3.52x for EAGLE-3.[^liEAGLE3ScalingInference2025]
- The SGLang throughput gain at batch size 64 is given as 1.38x in the abstract and Table 3, as 38% in Section 4.3, and as 40% in the contributions list.[^liEAGLE3ScalingInference2025]
- The vLLM experiment hardware is RTX3090 in the body text and A100 in the Table 5 caption.[^liEAGLE3ScalingInference2025]
- The text says EAGLE shows its maximum vLLM throughput improvement at a batch size of 24 and EAGLE-3 at 56, while Table 5 has the largest values for both at batch size 2.[^liEAGLE3ScalingInference2025]

## Related

- Proposed: [EAGLE-3](../methods/eagle-3.md), [Training-time test](../methods/training-time-test.md)
- Builds on: [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md) (dynamic draft tree), [Speculative decoding](../methods/speculative-decoding.md)
- Compared against: [HASS](../methods/hass.md), EAGLE, EAGLE-2, standard speculative sampling, PLD, Medusa, Lookahead, Hydra
- Serving frameworks evaluated in: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets: [MT-bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md), [ShareGPT](../datasets/sharegpt.md) (training), [UltraChat](../datasets/ultrachat.md) (training), [OpenThoughts-114k](../datasets/openthoughts.md) (training)
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md) (task selection follows it)
- Papers in this wiki cited by this paper: [SGLang](zhengSGLangEfficientExecution2024.md), [SpecExec](svirschevskiSpecExecMassivelyParallel2024.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
