---
type: Paper
title: Decoding Speculative Decoding
description: Empirical study showing that speculative decoding throughput is bottlenecked by draft model latency and depth, and that wide, shallow pruned draft models give up to 111% higher throughput.
tags: [speculative-decoding, draft-model, structured-pruning, llm-inference, benchmarking-study, speculative-drafter]
collections: [speculative drafter]
authors: [Minghao Yan, Saurabh Agarwal, Shivaram Venkataraman]
year: 2025
doi: 10.48550/arXiv.2402.01528
arxiv: "2402.01528"
arxiv_version: 2402.01528v4
sources:
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
---

# Decoding Speculative Decoding

Text source: arXiv HTML, version `2402.01528v4`.

## Summary

In [speculative decoding](../methods/speculative-decoding.md), a smaller *draft* model generates speculative tokens and the *target* LLM verifies them. The speedup depends heavily on the choice of draft model.[^yanDecodingSpeculativeDecoding2025] The paper runs over 350 experiments with LLaMa-65B and OPT-66B as targets to find the factors that determine the gain.[^yanDecodingSpeculativeDecoding2025]

Two findings come out of the study. The performance of speculative decoding depends heavily on the latency of the draft model, and that latency is bottlenecked by model depth. The draft model's capability in language modeling does not correlate strongly with its performance in speculative decoding.[^yanDecodingSpeculativeDecoding2025] Based on these, the paper designs draft models that trade depth for width, built by pruning with [Sheared-LLaMA](../methods/sheared-llama.md) and skipping its fine-tuning step. The new draft model provides up to 111% higher throughput than existing draft models, and the approach generalizes to all LLaMa models (1/2/3.1) and supervised fine-tuned models.[^yanDecodingSpeculativeDecoding2025]

## Contributions

- Comprehensive experiments (more than 352) on serving the open source LLaMa-65B and OPT-66B models with speculative decoding, to identify what to consider when selecting and designing a draft model.[^yanDecodingSpeculativeDecoding2025]
- Evidence that choosing a draft model by its accuracy on language modeling tasks is suboptimal, and a redesign of draft models that improves speculative decoding throughput by up to 111%.[^yanDecodingSpeculativeDecoding2025]
- The design leads to a $37\%$ reduction in KV-Caches, which enables larger batch sizes, and it outperforms [self-speculative decoding](../methods/self-speculative-decoding.md) in several setups.[^yanDecodingSpeculativeDecoding2025]

## Method

### Benchmarking setup

- Implementation: speculative decoding in the Microsoft Deepspeed library, with the same setup as [SpecInfer](../methods/specinfer.md): the draft model generates draft tokens, then the target model verifies them. Batch size 1, greedy decoding.[^yanDecodingSpeculativeDecoding2025]
- Hardware: 4 Nvidia 80GB A100 GPUs.[^yanDecodingSpeculativeDecoding2025]
- Targets: OPT-66B and LLaMa-65B. Drafts: OPT-125M, 350M, 1.3B, 2.7B, and 6.7B for the OPT series, and LLaMa-7B and 13B for the LLaMa series. Draft models range from $\approx 5\times$ to $528\times$ fewer parameters than the target models.[^yanDecodingSpeculativeDecoding2025]
- Prompts: [MMLU](../datasets/mmlu.md) (standard 5-shot), [Hellaswag](../datasets/hellaswag.md), and [Chatbot Arena](../datasets/chatbot-arena.md) (both zero-shot). Generation is open-ended: the model is not instructed to emit a single-letter answer.[^yanDecodingSpeculativeDecoding2025]
- Metrics: throughput (tokens generated per second) and TAR, the tokens accepted per iteration.[^yanDecodingSpeculativeDecoding2025]

### Findings

- **Draft latency is the bottleneck.** The draft model's time per token generation step grows from 6.23 ms for OPT-125M to 18.56 ms for OPT-6.7B. The target runs one prefill over the whole candidate sequence, while the draft runs multi-step autoregressive decoding sequentially. Look ahead values in this breakdown are 6 to 8.[^yanDecodingSpeculativeDecoding2025]
- **Latency scales with depth, not width.** With parameters fixed at around 350M, autoregressive decoding latency scales linearly with layer depth. Reducing the layers of OPT-350M (24 layers) reduces latency linearly. Scaling attention heads from 16 to 36 leaves decoding latency almost constant.[^yanDecodingSpeculativeDecoding2025]
- **TAR correlates little with task accuracy.** The authors attribute this to the majority of tokens in a sentence not being content words.[^yanDecodingSpeculativeDecoding2025]
- As draft model size increases, throughput decreases because of higher inference latency, despite consistent increases in TAR.[^yanDecodingSpeculativeDecoding2025]

Per-step draft latency (Table 11):[^yanDecodingSpeculativeDecoding2025]

| Model | Latency (ms) |
|---|---|
| OPT-125M | 6.23 |
| OPT-350M | 11.74 |
| OPT-1.3B | 12.64 |
| OPT-2.7B | 16.35 |
| OPT-6.7B | 18.56 |

### Performance model

The prior model of Leviathan et al. is $\frac{1-\alpha^{\gamma+1}}{(1-\alpha)(\gamma c+1)}$, which assumes the tokens generated in a sentence are mutually independent. The paper simplifies it to:[^yanDecodingSpeculativeDecoding2025]

$$
\text{Throughput}=\begin{cases}\displaystyle\frac{TAR}{(t^{d}_{target}+t^{d}_{draft})}&\text{if }TAR>1,\\ \displaystyle\frac{1}{(t^{d}_{target}+t^{d}_{draft})}&\text{if }TAR\leq 1.\end{cases}
$$

$t^{d}_{draft}$ is the time the draft model takes to generate $d$ draft tokens, and $t^{d}_{target}$ is the time the target takes to verify them.[^yanDecodingSpeculativeDecoding2025] The maximum deviation between this model and measured throughput is $3.5\%$ (LLaMa 7B and 13B, OPT 125M to 6.7B, on MMLU, 100 iterations).[^yanDecodingSpeculativeDecoding2025]

### Draft model design

- Models are pruned from LLaMa-7B with Sheared-LLaMa, using 0.4B tokens sampled from [RedPajama](../datasets/redpajama.md), and the fine-tuning step on 50B more tokens is skipped (hence the name NoFT).[^yanDecodingSpeculativeDecoding2025]
- NoFT-1.3B uses the configuration provided by the Sheared-LLaMa authors. NoFT-Wide-1.3B halves the layers from 24 to 12 and keeps the parameter count roughly the same by widening.[^yanDecodingSpeculativeDecoding2025]
- NoFT-Wide-796M, 543M, and 290M keep the attention heads, intermediate size, and model dimension of LLaMa-7B and reduce the layers to 5, 3, and 1. This is the widest configuration possible with the Sheared-LLaMa pruning scheme.[^yanDecodingSpeculativeDecoding2025]

Configurations (Table 1), where l is the number of layers, h the number of attention heads, $d_{\text{inter}}$ the intermediate size, and $d_{\text{model}}$ the model dimension:[^yanDecodingSpeculativeDecoding2025]

| Model | l | h | $d_{\text{inter}}$ | $d_{\text{model}}$ |
|---|---|---|---|---|
| NoFT-1.3B | 24 | 16 | 5504 | 2048 |
| NoFT-Wide-1.3B | 12 | 20 | 9280 | 2560 |
| NoFT-Wide-796M | 5 | 32 | 11008 | 4096 |
| NoFT-Wide-543M | 3 | 32 | 11008 | 4096 |
| NoFT-Wide-290M | 1 | 32 | 11008 | 4096 |

## Experiments & Results

### Deep vs wide draft at 1.3B (Table 3, MMLU)

| Draft Model | TAR | Latency (ms) | Throughput (tokens/s) |
|---|---|---|---|
| NoFT-1.3B | 3.81 | 13.13 | 23.10 |
| NoFT-Wide-1.3B | 3.70 | 6.69 | 32.59 |

All rows: [^yanDecodingSpeculativeDecoding2025]

The deep variant has $3\%$ higher TAR. The wide variant reduces draft latency by $49\%$ and improves overall throughput by $41\%$.[^yanDecodingSpeculativeDecoding2025]

### Draft model scaling (greedy decoding, from figures)

- NoFT-Wide-1.3B achieves up to $30\%$ higher speculative decoding throughput than Sheared-LLaMa-1.3B, using only $0.8\%$ of the tokens used to train Sheared-LLaMa-1.3B.[^yanDecodingSpeculativeDecoding2025]
- NoFT-Wide-796M provides another $20\%$ improvement over NoFT-Wide-1.3B and up to 60$\%$ over Sheared-LLaMa-1.3B.[^yanDecodingSpeculativeDecoding2025]
- NoFT-Wide-543M provides up to $40\%$ improvement over Sheared-LLaMa-1.3B, and has lower throughput than NoFT-Wide-796M.[^yanDecodingSpeculativeDecoding2025]
- Below 5 layers the model's alignment capability drops dramatically. At 5 layers, target model latency takes more than 80$\%$ of the time in a decoding cycle, so further latency reduction gives only a marginal gain.[^yanDecodingSpeculativeDecoding2025]

### Temperature sampling (Table 2)

Throughput of speculative decoding in tokens/s. The Speedup row is NoFT-Wide-796M over Sheared-LLaMA-1.3B.[^yanDecodingSpeculativeDecoding2025]

| Draft Model | MMLU (T=1.0) | Hellaswag (T=1.0) | Chatbot Arena (T=1.0) | MMLU (T=0.5) | Hellaswag (T=0.5) | Chatbot Arena (T=0.5) |
|---|---|---|---|---|---|---|
| NoFT-Wide-543M | 20.54 | 24.08 | 23.77 | 26.08 | 25.77 | 25.31 |
| NoFT-Wide-796M | 24.32 | 24.32 | 24.18 | 29.64 | 26.91 | 25.76 |
| NoFT-Wide-1.3B | 22.99 | 24.08 | 24.22 | 28.43 | 26.39 | 25.85 |
| Sheared-LLaMA-1.3B | 12.06 | 12.30 | 11.45 | 14.60 | 13.45 | 12.66 |
| Speedup | 101.6% | 97.7% | 111.8% | 103.0% | 100.0% | 103.5% |

NoFT-Wide-796M achieves $97.7\%$ to $111.8\%$ higher throughput than Sheared-LLaMA-1.3B while using only $0.8\%$ of its training tokens.[^yanDecodingSpeculativeDecoding2025]

### Memory and batch size (Tables 4 and 5)

| Context Length | KV cache, Sheared | KV cache, Wide | Activations, Sheared | Activations, Wide |
|---|---|---|---|---|
| 256 | 48MB | 30MB | 1MB | 1.25MB |
| 512 | 96MB | 60MB | 2MB | 2.5MB |
| 1024 | 192MB | 120MB | 4MB | 5MB |

All rows: [^yanDecodingSpeculativeDecoding2025]

The wide 1.3B design reduces [KV cache](../methods/kv-cache.md) by more than $37\%$ compared to Sheared-LLaMa-1.3B.[^yanDecodingSpeculativeDecoding2025]

| Batch size | LLaMA-65B prefill (s) | LLaMA-NoFT-Wide-1.3B autoregressive decoding (s) | Sheared-LLaMA-1.3B autoregressive decoding (s) |
|---|---|---|---|
| 1 | 0.060 | 0.0097 | 0.018 |
| 4 | 0.061 | 0.0097 | 0.019 |
| 16 | 0.063 | 0.0099 | 0.019 |
| 32 | 0.065 | 0.0101 | 0.019 |

All rows: [^yanDecodingSpeculativeDecoding2025]

### LLaMa-3 (Table 6)

Target model LLaMa-3.1-8B. The Wide-829M draft is pruned from LLaMa-3.2-1B, and its TAR is recovered by distilling over 1 million tokens, which finishes within 10 minutes.[^yanDecodingSpeculativeDecoding2025]

| Draft Model | Chat (tokens/s) | MMLU (tokens/s) | Hellaswag (tokens/s) |
|---|---|---|---|
| Wide-829M | 53.35 | 61.77 | 60.44 |
| LLaMA-3.2-1B | 37.41 | 44.89 | 39.03 |
| Self-Speculative | 35.14 | 40.41 | 40.02 |

All rows: [^yanDecodingSpeculativeDecoding2025]

Wide-829M achieves $42.6\%$ higher throughput than LLaMa-3.2-1B and $51.8\%$ higher than self-speculative decoding.[^yanDecodingSpeculativeDecoding2025]

### Ablations

Tokens accepted per iteration with NoFT-Wide-796M as the draft (Table 7):[^yanDecodingSpeculativeDecoding2025]

| Target Model | MMLU | Hellaswag | Chatbot Arena |
|---|---|---|---|
| LLaMa-65B | 2.66 | 2.74 | 2.61 |
| LLaMa-2-70B | 2.55 | 2.68 | 2.64 |

Throughput in tokens/s with Vicuna 33B as the target (Table 8):[^yanDecodingSpeculativeDecoding2025]

| Draft Model | MMLU | Hellaswag | Chatbot Arena |
|---|---|---|---|
| Tiny-LLaMa-1.1B | 20.78 | 18.25 | 18.73 |
| NoFT-Wide-796M | 29.87 | 26.55 | 25.61 |

NoFT-Wide-796M outperforms Tiny-LLaMa-1.1B by up to $45\%$. Tiny-LLaMa-1.1B has a TAR $35\%$ and $32\%$ higher on MMLU and Hellaswag, and its latency is 4x higher because it has 22 layers against 5.[^yanDecodingSpeculativeDecoding2025]

Comparison against self-speculative decoding, in its best setting (LLaMa-2-70B target, greedy sampling), on [CNNDM](../datasets/cnn-dailymail.md) and [XSum](../datasets/xsum.md) (Tables 9 and 10):[^yanDecodingSpeculativeDecoding2025]

| Strategy | Speedup, CNNDM | Speedup, XSum | Attention layers | MLP layers |
|---|---|---|---|---|
| Self-Speculative (LLaMa-2-70B) | 99% | 60% | 33 | 43 |
| NoFT-Wide-796M | 131% | 145% | 5 | 5 |

All rows: [^yanDecodingSpeculativeDecoding2025]

Self-speculative decoding on LLaMa-2-13B uses 16 attention layers and 30 MLP layers.[^yanDecodingSpeculativeDecoding2025] LLaMa-NoFT-Wide-796M outperforms self-speculative decoding by up to $53\%$, and its autoregressive decoding latency is only $7\%$ of the 70B target's prefill latency.[^yanDecodingSpeculativeDecoding2025]

### Latency reduction for parity with OPT-125M (Table 12, MMLU)

| Model | Latency (ms) | Parity Latency | Reduction ($\%$) |
|---|---|---|---|
| 125M | 43.7 | 43.7 | 0 |
| 350M | 79.8 | 50.6 | 36.6 |
| 1.3B | 87.1 | 58.7 | 32.6 |
| 2.7B | 114.3 | 49.8 | 56.4 |
| 6.7B | 139.5 | 68.2 | 51.1 |

All rows: [^yanDecodingSpeculativeDecoding2025]

- The table gives 32.6 for OPT-1.3B, while the body text says its latency needs to be reduced by 32.9%.[^yanDecodingSpeculativeDecoding2025]
- A 1.3B model would be preferred over OPT-125M only with a TAR advantage greater than 2. With TAR capped at 8 by the draft length, OPT-2.7B and OPT-6.7B cannot surpass OPT-125M.[^yanDecodingSpeculativeDecoding2025]

## Limitations

- The work studies only lossless speculative decoding, where the target LLM's output distribution is preserved. Approximate efficient inference algorithms are left for future work.[^yanDecodingSpeculativeDecoding2025]
- Conclusions drawn on specific hardware (e.g., A100) may not hold for newer or older hardware (e.g., H100 or V100).[^yanDecodingSpeculativeDecoding2025]
- The main benchmarks use batch size 1.[^yanDecodingSpeculativeDecoding2025]
- For LLaMa-3, pruning layers had a larger impact on TAR, and a distillation step was needed to recover it.[^yanDecodingSpeculativeDecoding2025]
- The greedy-decoding gains for the wide draft models (up to $30\%$, 60$\%$, and $40\%$) are reported from figures, not tables.[^yanDecodingSpeculativeDecoding2025]

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [KV cache](../methods/kv-cache.md)
- Methods built on or compared against: [Sheared-LLaMA](../methods/sheared-llama.md), [Self-speculative decoding](../methods/self-speculative-decoding.md), [SpecInfer](../methods/specinfer.md)
- Datasets: [MMLU](../datasets/mmlu.md), [Hellaswag](../datasets/hellaswag.md), [Chatbot Arena](../datasets/chatbot-arena.md), [CNN/DailyMail](../datasets/cnn-dailymail.md), [XSum](../datasets/xsum.md), [RedPajama](../datasets/redpajama.md)
- Papers in this wiki cited by this paper: [Sheared LLaMA](xiaShearedLLaMAAccelerating2024.md), [Compact Language Models via Pruning and Knowledge Distillation](muralidharanCompactLanguageModels2024.md), [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md)

## Open questions and results

- [Target-aware recovery of compressed drafters](../analyses/target-aware-recovery-of-compressed-drafters.md)
- [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
