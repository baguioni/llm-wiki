---
type: Paper
title: "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding"
description: LayerSkip trains Llama models with depth-increasing layer dropout and a shared-LM-head early exit loss, so that early layers can draft tokens that the remaining layers of the same model verify, reaching 1.34× to 2.16× speedups with one shared KV cache.
tags: [speculative-decoding, self-speculative-decoding, early-exit, layer-dropout, llm-inference, speculative-drafter]
collections: [speculative drafter]
authors: [Mostafa Elhoushi, Akshat Shrivastava, Diana Liskovich, Basil Hosmer, Bram Wasti, Liangzhen Lai, Anas Mahmoud, Bilge Acun, Saurabh Agrawal, Ahmed Roman, Ahmed A Aly, Beidi Chen, Carole Jean-Wu]
doi: 10.18653/v1/2024.acl-long.681
arxiv: "2404.16710"
arxiv_version: 2404.16710v4
sources:
  - id: elhoushiLayerSkipEnablingEarly2024
    resource: zotero://select/items/@elhoushiLayerSkipEnablingEarly2024
    title: "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding"
---

# LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding

Text source: arXiv HTML, version `2404.16710v4` (the Zotero entry is the ACL 2024 long paper).

## Summary

[LayerSkip](../methods/layerskip.md) is an end-to-end recipe to speed up LLM inference by using fewer layers per token.[^elhoushiLayerSkipEnablingEarly2024] Training applies layer dropout with low rates for early layers and high rates for later layers, plus an early exit loss in which all layers share the model's single LM head.[^elhoushiLayerSkipEnablingEarly2024] This makes [early exit](../methods/early-exit.md) at early layers more accurate without auxiliary layers or modules.[^elhoushiLayerSkipEnablingEarly2024] At inference a [self-speculative decoding](../methods/self-speculative-decoding.md) algorithm drafts with the first $E$ layers and verifies and corrects with the remaining layers. Draft and verification share the same model, KV cache, and activations, so memory footprint is lower than with a separate draft model.[^elhoushiLayerSkipEnablingEarly2024]

Experiments cover Llama models in four regimes: pretraining from scratch, continual pretraining, finetuning on code, and finetuning on a task. Reported speedups are up to 2.16× on CNN/DM summarization, 1.82× on coding, and 2.0× on TOPv2 semantic parsing.[^elhoushiLayerSkipEnablingEarly2024]

## Contributions

- A training recipe that combines layer dropout and early exit loss.[^elhoushiLayerSkipEnablingEarly2024]
- Inference that is more robust to exiting at earlier layers, which in effect creates sub-models of different sizes within one model.[^elhoushiLayerSkipEnablingEarly2024]
- A self-speculative decoding solution that decodes with earlier layers and verifies and corrects with later layers, with speedups between 1.34× and 2.16× depending on the task.[^elhoushiLayerSkipEnablingEarly2024]

## Method

### Motivation

- Probing each layer of a pretrained Llama1 7B on the first HumanEval prompt by projecting its output through the LM head shows that a token needs on average 23.45 of the 32 layers, so a perfect zero-overhead exit predictor could save at most 26% of computation.[^elhoushiLayerSkipEnablingEarly2024]
- Intermediate layers sometimes "change their minds", and easy tokens (for example "for" at the start of a loop) can still need all 32 layers.[^elhoushiLayerSkipEnablingEarly2024]

### Training: layer dropout

- Layer $l$ at iteration $t$ computes $x_{l+1,t}=x_{l,t}+M(p_{l,t})f_{l}(x_{l,t})$, where $M(p)$ is a Bernoulli function returning 0 with probability $p$. Dropout is per sample; dropped samples are removed from the batch for that layer, and every GPU uses the same seed so each layer drops the same number of samples.[^elhoushiLayerSkipEnablingEarly2024]
- Rate $p_{l,t}=S(t)D(l)p_{max}$. The per-layer scale rises exponentially from 0.0 at layer 0 to 1.0 at layer $L-1$: $D(l)=e^{\frac{l\ln 2}{L-1}}-1$.[^elhoushiLayerSkipEnablingEarly2024]
- Time scale: $S(t)=1$ for continual pretraining and finetuning; an exponential curriculum $S_{exp}(t)=e^{\frac{t\ln 2}{T-1}}-1$ for pretraining from scratch.[^elhoushiLayerSkipEnablingEarly2024]
- With equal average dropout, the exponential per-layer configuration (0 at the first layer to 0.2 at the last) gives lower training loss than a constant 0.0889 on all layers.[^elhoushiLayerSkipEnablingEarly2024]

### Training: early exit loss

- Total loss $J(X,Y,t)=\sum_{l=0}^{L-1}\tilde{e}(t,l)J_{\text{CE}}(g(x_{l+1}),Y)$, where $g$ is the shared LM head and $\tilde{e}(t,l)$ are normalized per-layer scales that sum to 1.[^elhoushiLayerSkipEnablingEarly2024]
- The unnormalized scale grows with depth, $e(l)=e_{scale}\sum_{i=0}^{l}i$ for $l<L-1$ and $e(L-1)=L-1+e_{scale}\sum_{i=0}^{L-2}i$, so later layers get quadratically higher weight. $0\leq e_{scale}\leq 1$.[^elhoushiLayerSkipEnablingEarly2024]
- No extra LM heads are added; every layer exits through the same head.[^elhoushiLayerSkipEnablingEarly2024]
- **Curriculum $C(t,l)$.** Enabling all early exit losses at all iterations slows training and lowers last-layer accuracy. The rotational curriculum $C_{\text{rot},R}$ enables exits every $R$ layers and rotates each iteration, so only $\lceil L/R\rceil$ unembeddings run per iteration. The gradual curriculum $C_{\text{grad}}$ enables exits from layer $L-1$ down to 0, one layer every $T/2L$ iterations.[^elhoushiLayerSkipEnablingEarly2024]

### Inference

- **Early exit:** run the first $E$ layers and go straight to the LM head, output $g(x_E)$.[^elhoushiLayerSkipEnablingEarly2024]
- **Self-drafting:** generate $d$ draft tokens autoregressively by exiting at layer $E$.[^elhoushiLayerSkipEnablingEarly2024]
- **Self-verification:** run the full model on the draft in one forward pass; accept draft tokens up to the first disagreement and append the next verified token. Only the remaining $L-E$ layers need computing.[^elhoushiLayerSkipEnablingEarly2024]
- **Cache reuse.** Because draft and verification run the same first $E$ layers in the same order, a single KV cache serves both. An exit query cache stores the query vector of exit layer $E-1$ so verification continues from layer $E$. The union is called the KVQ cache.[^elhoushiLayerSkipEnablingEarly2024]

### Training configurations

| Regime | Model | Data | $p_{max}$ | $e_{scale}$ | Curriculum |
|---|---|---|---|---|---|
| Continual pretraining | Llama2 7B (32 layers) | 52B tokens | 0.1 | 0.2 | $C_{\text{rot},R=8}$ |
| Continual pretraining | Llama2 13B (40 layers) | 52B tokens | 0.1 | 0.1 | $C_{\text{rot},R=39}$ |
| Continual pretraining | Llama3 8B | 419B tokens | 0.1 | 0.1 | $C_{\text{rot},R=8}$ |
| Continual pretraining | Llama3.2 1B | 839B tokens | 0.1 | 0.1 | $C_{\text{rot},R=8}$ |
| Pretraining from scratch | Llama2 1.5B (24 layers) | 26B tokens | 0.1 | 0.2 | $C_{\text{rot},R=23}$ |
| Pretraining from scratch | Llama2 7B (32 layers) | 26B tokens | 0.2 | 0.2 | $C_{\text{rot},R=31}$ |
| Finetuning on code | Llama1 7B | 5.2B tokens of CodeLlama data mix | 0.1 | 1.0 | $C_{\text{rot},R=16}$ |
| Finetuning on a task | Llama 1.5B (24 layers) | [TOPv2](../datasets/topv2.md) | 0.2 | 1.0 | $C_{\text{grad}}$ |

All rows: [^elhoushiLayerSkipEnablingEarly2024]

Hardware (Table 8): continual pretraining of Llama2 7B and 13B used batch size 4, $50\times10^{3}$ steps, 64 A100 80 GB; pretraining from scratch 32 A100; code finetuning $10\times10^{3}$ steps on 32 A100 80 GB; TOPv2 finetuning batch size 32, $5.8\times10^{3}$ steps on 8 A100 80 GB.[^elhoushiLayerSkipEnablingEarly2024] Pretraining from scratch with layer dropout uses a higher learning rate ($8\times10^{-4}$ instead of $4\times10^{-4}$ for Llama 1.5B and $3\times10^{-4}$ for Llama2 7B).[^elhoushiLayerSkipEnablingEarly2024]

## Experiments & Results

### Early exit accuracy, continual pretraining (Tables 1 and 2)

Last layer and middle layer, baseline vs LayerSkip, selected rows:

| Task | Llama2 7B last (L32) base / LS | Llama2 7B middle (L16) base / LS | Llama2 13B last (L40) base / LS | Llama2 13B middle (L20) base / LS |
|---|---|---|---|---|
| Wikipedia perplexity ↓ | 4.32 / 4.3 | 1900 / 8.12 | 3.97 / 3.98 | 507 / 10.5 |
| [HellaSwag](../datasets/hellaswag.md) | 57.0 / 56.6 | 31.5 / 43.8 | 60.1 / 60.3 | 35.6 / 46.8 |
| [MMLU](../datasets/mmlu.md) | 46.0 / 43.1 | 38.9 / 40.2 | 55.2 / 53.7 | 49.2 / 52.9 |
| NaturalQuestions | 25.1 / 23.2 | 0.0554 / 4.07 | 31.5 / 31.8 | 0.609 / 4.43 |
| [GSM8K](../datasets/gsm8k.md) | 14.3 / 12.2 | 0 / 2.05 | 29.3 / 27.4 | 0.0758 / 1.74 |
| [HumanEval](../datasets/humaneval.md) | 13.4 / 15.9 | 0 / 4.88 | 18.9 / 18.3 | 0 / 3.05 |
| [MBPP](../datasets/mbpp.md) | 21.0 / 22.4 | 0 / 7.20 | 26.4 / 29.0 | 0 / 3.40 |

All rows: [^elhoushiLayerSkipEnablingEarly2024]

| Task | Llama3 8B last (L32) base / LS | Llama3 8B middle (L16) base / LS | Llama3.2 1B last (L16) base / LS | Llama3.2 1B middle (L8) base / LS |
|---|---|---|---|---|
| Wikipedia perplexity ↓ | 5.63 / 5.38 | $1.10\times10^{05}$ / 12.2 | 8.52 / 8.38 | $2.18\times10^{05}$ / 22.1 |
| MMLU | 66.5 / 60.5 | 27.6 / 38.1 | 31.2 / 24.8 | 25.8 / 25.9 |
| GSM8K | 54.2 / 45.0 | 0.00 / 2.27 | 5.84 / 3.79 | 0.00 / 2.05 |
| HumanEval | 37.8 / 28.7 | 0.00 / 7.32 | 17.7 / 9.15 | 0.00 / 1.22 |
| MBPP | 49.0 / 40.0 | 0.00 / 13.6 | 25.8 / 13.2 | 0.00 / 0.00 |

All rows: [^elhoushiLayerSkipEnablingEarly2024]

- For Llama2, LayerSkip is clearly better than the baseline at earlier layers with a minimal last-layer drop.[^elhoushiLayerSkipEnablingEarly2024]
- For Llama3 8B and Llama3.2 1B the last-layer drop is larger despite more training tokens. Early-layer perplexity of the baseline Llama3 models is 2 or 3 orders of magnitude higher than for Llama2, which the authors link to the larger pretraining budget (8T tokens for Llama3 against 2T for Llama2).[^elhoushiLayerSkipEnablingEarly2024]
- Multiple-choice "classification" tasks keep decent accuracy at middle layers even on the baseline (Llama2 13B MMLU drops only from 55.2% to 49.2%), while open-ended generation tasks collapse.[^elhoushiLayerSkipEnablingEarly2024]
- **Pretraining from scratch** (Llama2 1.5B and 7B, 26B tokens): layer dropout and/or early exit loss give higher accuracy than the baseline at earlier layers; at the last layer some tasks drop slightly and others improve.[^elhoushiLayerSkipEnablingEarly2024]
- **Code finetuning** (Llama1 7B): LayerSkip is clearly better at earlier layers, and with both layer dropout and early exit loss the last layer is almost as accurate as the baseline.[^elhoushiLayerSkipEnablingEarly2024]
- **TOPv2 finetuning** (Llama 1.5B): the baseline gets 0 EM when layers are removed; LayerSkip reaches 77% at layer 12, with a 3% regression at the final layer.[^elhoushiLayerSkipEnablingEarly2024]
- **Scaling with pretraining tokens** (Llama 1.5B, 50,000 steps, 32/64/128 GPUs): last-layer perplexity on The Stack falls with more tokens, but middle-layer (layer 12) perplexity rises drastically unless early exit loss is applied; layer dropout reduces the rise as well.[^elhoushiLayerSkipEnablingEarly2024]

### Self-speculative decoding

Greedy decoding, up to 512 generated tokens per sample, HuggingFace implementation. Speedup is the reduction of average time per token against an "Autoregressive" baseline model trained without LayerSkip.[^elhoushiLayerSkipEnablingEarly2024]

**Continual pretraining, H100 (Table 3).** $E$ is the exit layer and $d$ the number of speculations.

| Task | Llama2 7B: $E$, $d$ | ROUGE-2 AR / self-spec | Token acc. | Tok/s AR / self-spec | Speedup | Llama2 13B: $E$, $d$ | ROUGE-2 AR / self-spec | Token acc. | Tok/s AR / self-spec | Speedup |
|---|---|---|---|---|---|---|---|---|---|---|
| [CNN/DM](../datasets/cnn-dailymail.md) (1-shot) | 8, 12 | 0.079 / 0.078 | 68.9% | 62.7 / 127.9 | 1.86× | 15, 12 | 0.098 / 0.098 | 74.5% | 37.2 / 70.2 | 1.81× |
| [XSUM](../datasets/xsum.md) (0-shot) | 8, 12 | 0.073 / 0.073 | 54.6% | 63.4 / 104.7 | 1.54× | 15, 4 | 0.124 / 0.124 | 67.7% | 43.8 / 60.5 | 1.34× |
| HumanEval | 8, 6 | 0.041 / 0.042 | 67.1% | 62.9 / 122.8 | 1.83× | 7, 4 | 0.055 / 0.055 | 57.0% | 48.9 / 84.2 | 1.66× |

All rows: [^elhoushiLayerSkipEnablingEarly2024]

- Early exit alone at the same $E$ is much faster but loses most quality (for example CNN/DM Llama2 7B: 232.4 tok/s at ROUGE-2 0.012).[^elhoushiLayerSkipEnablingEarly2024]
- Draft & Verify (Zhang et al. 2023), on Llama2 13B: 1.56× on CNN/DM and 1.48× on XSUM in Table 3. The text compares LayerSkip as "1.81× vs. 1.5×" on CNN/DM and "1.34× vs. 1.48×" on XSUM.[^elhoushiLayerSkipEnablingEarly2024]
- Speedups are generally higher for Llama2 7B than for 13B in continual pretraining.[^elhoushiLayerSkipEnablingEarly2024]

**Pretraining from scratch on 26B tokens, H100 (Table 4),** CNN/DM 1-shot, $E=8$: Llama2 1.5B 91.6 → 167.4 tok/s, token acceptance 77.4%, 1.76×; Llama2 7B 64.5 → 145.6 tok/s, 77.8%, 2.16×, ROUGE-2 0.060 → 0.067. Here the bigger model has the bigger speedup.[^elhoushiLayerSkipEnablingEarly2024]

**Code finetuning, A100 (Table 5),** Llama1 7B on HumanEval, $E=6$, 12 speculations: ROUGE-2 0.0513 for both, 34 → 62 tok/s, token acceptance 45%, 1.82×.[^elhoushiLayerSkipEnablingEarly2024]

**TOPv2 finetuning, H100 (Table 6),** Llama 1.5B, 1000 sampled test examples for latency, 8 speculations, 80 generated tokens:

| Generation | $E$ | EM | Token acc. | Time per token (ms) | Speedup |
|---|---|---|---|---|---|
| Autoregressive | - | 85.9% | - | 36 | 1.00× |
| Early exit | 18 | 83.3% | - | 28 | - |
| Early exit | 12 | 79.4% | - | 19 | - |
| Early exit | 6 | 62.9% | - | 10 | - |
| Self speculative | 18 | 82.9% | 98.9% | 29 | 1.24× |
| Self speculative | 12 | 82.9% | 97.6% | 22 | 1.64× |
| Self speculative | 6 | 82.9% | 76.0% | 18 | 2.0× |

All rows: [^elhoushiLayerSkipEnablingEarly2024]

**CPU (Table 11),** TOPv2, first 100 test samples, 7 speculations, 50 tokens: autoregressive 165 ms/token at 85.39 EM; self speculation 134 ms ($E=18$, acceptance 99), 104 ms ($E=12$, 97), 87 ms ($E=6$, 76), all at 82.9 EM.[^elhoushiLayerSkipEnablingEarly2024]

**KVQ cache reuse on CPU (Table 7):**

| Generation | TOPv2 ms/token | CNN/DM ms/token |
|---|---|---|
| Self speculation ($E=18$) | 134 | 166 |
| without KVQ reuse | 143 | 182 |
| Self speculation ($E=12$) | 104 | 165 |
| without KVQ reuse | 110 | 185 |

All rows: [^elhoushiLayerSkipEnablingEarly2024]

The text says cache reuse saves 9-20 ms per token; the TOPv2 $E=12$ row differs by 6 ms.[^elhoushiLayerSkipEnablingEarly2024]

## Limitations

- Self-speculation needs a model finetuned or pretrained with the LayerSkip recipe, while the self-speculative approach of Zhang et al. (2023) does not change model weights.[^elhoushiLayerSkipEnablingEarly2024]
- $p_{max}$, $e_{scale}$, and $R$ need tuning to avoid a drop in last-layer accuracy.[^elhoushiLayerSkipEnablingEarly2024]
- Pretraining from scratch with layer dropout needs a higher learning rate, and tuning it can be tricky and time-consuming.[^elhoushiLayerSkipEnablingEarly2024]
- Continual pretraining of Llama3 8B and Llama3.2 1B costs more last-layer accuracy than for Llama2 (for example MMLU 66.5 → 60.5 and HumanEval 37.8 → 28.7 on Llama3 8B).[^elhoushiLayerSkipEnablingEarly2024]
- Inconsistencies in the text: the abstract states speedups up to 2.16× while the conclusion states up to 1.86×; the TOPv2 text gives 97.2% acceptance at $E=12$ while Table 6 gives 97.6%; the text cites "Table 6" for the code results that are in Table 5.[^elhoushiLayerSkipEnablingEarly2024]
- All verification is greedy (exact match of draft and full-model tokens); no sampling-based acceptance is evaluated.[^elhoushiLayerSkipEnablingEarly2024]

## Related

- Methods proposed: [LayerSkip](../methods/layerskip.md)
- Methods: [Self-speculative decoding](../methods/self-speculative-decoding.md), [Early exit](../methods/early-exit.md), [Speculative decoding](../methods/speculative-decoding.md), [KV cache](../methods/kv-cache.md)
- Datasets: [CNN/DM](../datasets/cnn-dailymail.md), [XSum](../datasets/xsum.md), [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [TOPv2](../datasets/topv2.md), [GSM8K](../datasets/gsm8k.md), [MMLU](../datasets/mmlu.md), [HellaSwag](../datasets/hellaswag.md)
- Later use: [Osprey](bieOspreyTargetagnosticPretraining2026.md) prunes a LayerSkip-Llama3.2-1B checkpoint into a drafter body; [SDFP](weiSDFPSpeculativeDecoding2026.md) lists LayerSkip-SD's training cost.

[^elhoushiLayerSkipEnablingEarly2024]: Elhoushi et al. 2024
