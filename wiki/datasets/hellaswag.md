---
type: Dataset
title: HellaSwag
description: Commonsense completion dataset, used in the wiki's papers as an accuracy test for compressed and on-device models and as a prompt source for speed measurements.
tags: [dataset, evaluation, commonsense, pruning, speculative-decoding, on-device]
sources:
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: wangEfficientOnDeviceDiffusion2026
    resource: zotero://select/items/@wangEfficientOnDeviceDiffusion2026
    title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
---

# HellaSwag

## Overview

HellaSwag is described in the wiki's papers as a commonsense completion dataset[^wangEfficientOnDeviceDiffusion2026] and as a question-answering dataset for common-sense reasoning.[^muralidharanCompactLanguageModels2024] Three papers report accuracy on it.[^muralidharanCompactLanguageModels2024][^xiaShearedLLaMAAccelerating2024][^wangEfficientOnDeviceDiffusion2026] Two papers use it only as prompts or as a workload for speed measurements.[^yanDecodingSpeculativeDecoding2025][^zhengSGLangEfficientExecution2024]

## Composition

- Each item has an incomplete sentence and a set of choices: Yan et al. feed the model the incomplete sentences without the choices,[^yanDecodingSpeculativeDecoding2025] and Zheng et al. select the answer with the highest probability among multiple choices that share a common question prefix.[^zhengSGLangEfficientExecution2024]
- Sizes and splits are not stated in the wiki's papers.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Muralidharan et al. 2024](../papers/muralidharanCompactLanguageModels2024.md) | Accuracy of pruned and distilled Minitron models against baselines | 10-shot, acc_norm | See the accuracy table[^muralidharanCompactLanguageModels2024] |
| [Xia et al. 2024](../papers/xiaShearedLLaMAAccelerating2024.md) | Accuracy of [Sheared-LLaMA](../methods/sheared-llama.md) against similarly sized models | 10-shot, lm-evaluation-harness | See the accuracy table[^xiaShearedLLaMAAccelerating2024] |
| [Wang et al. 2026](../papers/wangEfficientOnDeviceDiffusion2026.md) | Generation quality of on-device diffusion LLM inference | 200-sample subset, Q4\_0 models, temperature 0 | See the accuracy table[^wangEfficientOnDeviceDiffusion2026] |
| [Yan et al. 2025](../papers/yanDecodingSpeculativeDecoding2025.md) | Prompts for [speculative decoding](../methods/speculative-decoding.md) throughput | Zero-shot, open-ended generation | See the speed table[^yanDecodingSpeculativeDecoding2025] |
| [Zheng et al. 2024](../papers/zhengSGLangEfficientExecution2024.md) | Serving workload for [SGLang](../methods/sglang.md) | 20-shot, `select` primitive | Only normalized bar charts[^zhengSGLangEfficientExecution2024] |

### Protocols

- Muralidharan et al. and Xia et al. both report 10-shot HellaSwag.[^muralidharanCompactLanguageModels2024][^xiaShearedLLaMAAccelerating2024] Xia et al. list it among the tasks used by the Open LLM Leaderboard.[^xiaShearedLLaMAAccelerating2024]
- Wang et al. evaluate 200-sample subsets with all models in Q4\_0 low-bit weight quantization and temperature 0.[^wangEfficientOnDeviceDiffusion2026]
- Yan et al. evaluate zero-shot and do not instruct the model to emit a single-letter answer; generation is open-ended.[^yanDecodingSpeculativeDecoding2025]
- Zheng et al. run 20-shot HellaSwag and use the `select` primitive to pick the answer with the highest probability. SGLang reuses the [KV cache](../methods/kv-cache.md) of both the few-shot examples and the common question prefix for multiple choices, which the paper calls two-level sharing.[^zhengSGLangEfficientExecution2024]

### Task quality: accuracy

Compression papers, 10-shot:

| Model | Setting | HellaSwag | Reported by |
|---|---|---|---|
| Llama-3 (8B) | 10-shot, acc_norm, base model | 82.1 | [^muralidharanCompactLanguageModels2024] |
| Llama-2 (6.7B) | 10-shot, acc_norm, base model | 79 | [^muralidharanCompactLanguageModels2024] |
| Mistral (7.3B) | 10-shot, acc_norm, base model | 83.2 | [^muralidharanCompactLanguageModels2024] |
| Gemma (8.5B) | 10-shot, acc_norm, base model | 82 | [^muralidharanCompactLanguageModels2024] |
| Nemotron-4 (15.6B) | 10-shot, acc_norm, base model | 84.6 | [^muralidharanCompactLanguageModels2024] |
| Nemotron-3 (8.5B) | 10-shot, acc_norm, base model | 78.5 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B (8.3B) | 10-shot, acc_norm, 94B training tokens | 80.7 | [^muralidharanCompactLanguageModels2024] |
| Phi-2 (2.7B) | 10-shot, acc_norm, base model | 75.2 | [^muralidharanCompactLanguageModels2024] |
| Gemma (2.5B) | 10-shot, acc_norm, base model | 72 | [^muralidharanCompactLanguageModels2024] |
| Gemma2 (2.6B) | 10-shot, acc_norm, value taken from the model's own paper | 73.0 | [^muralidharanCompactLanguageModels2024] |
| Qwen2 (1.5B) | 10-shot, acc_norm, value taken from the model's own paper | 66.6 | [^muralidharanCompactLanguageModels2024] |
| MiniCPM (2.7B) | 10-shot, acc_norm, value taken from the model's own paper | 68.3 | [^muralidharanCompactLanguageModels2024] |
| Minitron 4B (4.2B) | 10-shot, acc_norm, 94B training tokens | 75.0 | [^muralidharanCompactLanguageModels2024] |
| LLMPruner (9.8B) | 10-shot, acc_norm, 8 Billion target, pruning baseline | 67.8 | [^muralidharanCompactLanguageModels2024] |
| SliceGPT (9.9B) | 10-shot, acc_norm, 8 Billion target, pruning baseline | 55.7 | [^muralidharanCompactLanguageModels2024] |
| LaCo (9.8B) | 10-shot, acc_norm, 8 Billion target, pruning baseline | 64.4 | [^muralidharanCompactLanguageModels2024] |
| ShortGPT (9.8B) | 10-shot, acc_norm, 8 Billion target, pruning baseline | 66.6 | [^muralidharanCompactLanguageModels2024] |
| LLMPruner (4.8B) | 10-shot, acc_norm, 4 Billion target, pruning baseline | 56.46 | [^muralidharanCompactLanguageModels2024] |
| SliceGPT (4.9B) | 10-shot, acc_norm, 4 Billion target, pruning baseline | 50.27 | [^muralidharanCompactLanguageModels2024] |
| LaCo (4.9B) | 10-shot, acc_norm, 4 Billion target, pruning baseline | 55.69 | [^muralidharanCompactLanguageModels2024] |
| ShortGPT (4.9B) | 10-shot, acc_norm, 4 Billion target, pruning baseline | 53.02 | [^muralidharanCompactLanguageModels2024] |
| Sheared LLaMa (2.7B) | 10-shot, acc_norm, 4 Billion target, pruning baseline | 70.8 | [^muralidharanCompactLanguageModels2024] |
| LLaMA2-7B | 10-shot, 2T training tokens | 78.6 | [^xiaShearedLLaMAAccelerating2024] |
| OPT-1.3B | 10-shot, 300B training tokens | 54.5 | [^xiaShearedLLaMAAccelerating2024] |
| Pythia-1.4B | 10-shot, 300B training tokens | 53.0 | [^xiaShearedLLaMAAccelerating2024] |
| TinyLlama-1.1B | 10-shot, 3T training tokens | 60.3 | [^xiaShearedLLaMAAccelerating2024] |
| Sheared-LLaMA-1.3B | 10-shot, 50B training tokens | 60.7 | [^xiaShearedLLaMAAccelerating2024] |
| OPT-2.7B | 10-shot, 300B training tokens | 61.5 | [^xiaShearedLLaMAAccelerating2024] |
| Pythia-2.8B | 10-shot, 300B training tokens | 60.8 | [^xiaShearedLLaMAAccelerating2024] |
| INCITE-Base-3B | 10-shot, 800B training tokens | 64.8 | [^xiaShearedLLaMAAccelerating2024] |
| Open-LLaMA-3B-v1 | 10-shot, 1T training tokens | 62.6 | [^xiaShearedLLaMAAccelerating2024] |
| Open-LLaMA-3B-v2 | 10-shot, 1T training tokens | 67.6 | [^xiaShearedLLaMAAccelerating2024] |
| Sheared-LLaMA-2.7B | 10-shot, 50B training tokens | 70.8 | [^xiaShearedLLaMAAccelerating2024] |

In the 4 Billion block of the pruning comparison, the Minitron 4B value is printed as 75.[^muralidharanCompactLanguageModels2024]

Minitron retraining ablations (the shot count is not restated for these tables):

| Model | Setting | HellaSwag | Reported by |
|---|---|---|---|
| 4B-Random-Init | 150B tokens (iso-compute) | 46.22 | [^muralidharanCompactLanguageModels2024] |
| 4B-Random-Init | 400B tokens | 48.23 | [^muralidharanCompactLanguageModels2024] |
| 4B-Pruned (prune Nemotron-4 15B) | 150B tokens (iso-compute) | 50.85 | [^muralidharanCompactLanguageModels2024] |
| 4B-Pruned-Distill (prune Nemotron-4 15B) | 100B tokens (iso-compute) | 51.04 | [^muralidharanCompactLanguageModels2024] |
| 4B-Pruned-Distill (prune Minitron 8B) | 100B tokens (iso-compute) | 52.04 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B | $L_{logits}+L_{is}$, 18.9B tokens | 73.6 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B | $L_{logits}$, 18.9B tokens | 73.8 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B | $L_{logits}$, 94B tokens | 79.7 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B-Width-pruned | Phase1 + Phase2, 113B tokens | 80.3 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B-Width-pruned | Phase2 only, 94B tokens | 80.1 | [^muralidharanCompactLanguageModels2024] |

- Pruning the 15B model with distillation gains 4.8% on Hellaswag compared to training from scratch with equivalent compute, and pruning an 8B model instead of the 15B model gains an additional 1%.[^muralidharanCompactLanguageModels2024]
- With iterative depth pruning, Hellaswag accuracy is retained up to 31 layers, with a sharper drop at 25 layers.[^muralidharanCompactLanguageModels2024]

On-device inference, 200-sample subset, Q4\_0 weights, temperature 0:

| Model | Setting | HellaSwag accuracy | Reported by |
|---|---|---|---|
| LLaDA-8B-Instruct | CPU, vanilla dLLM decoding | 51.0 | [^wangEfficientOnDeviceDiffusion2026] |
| LLaDA-8B-Instruct | llada.cpp | 49.5 | [^wangEfficientOnDeviceDiffusion2026] |
| Llama-3-8B-Instruct | CPU | 67.0 | [^wangEfficientOnDeviceDiffusion2026] |
| Llama-3-8B-Instruct | NPU | 60.0 | [^wangEfficientOnDeviceDiffusion2026] |
| LLaDA-8B-Instruct | Ablation: NPU | 50.0 | [^wangEfficientOnDeviceDiffusion2026] |
| LLaDA-8B-Instruct | Ablation: NPU + MBSD | 46.0 | [^wangEfficientOnDeviceDiffusion2026] |
| LLaDA-8B-Instruct | Ablation: NPU + MBSD + DPPR | 49.5 | [^wangEfficientOnDeviceDiffusion2026] |

MBSD is multi-block speculative decoding and DPPR is dual-path progressive revision.[^wangEfficientOnDeviceDiffusion2026] In a separate table on block-wise decoding with prefix KV cache reuse, vanilla dLLM decoding scores 102 / 200 (51.0%) and block-wise decoding 93 / 200 (46.5%), a change of -4.5.[^wangEfficientOnDeviceDiffusion2026]

### Speed: speculative decoding throughput on HellaSwag prompts

These rows measure decoding speed with HellaSwag sentences as prompts. They are not accuracy results. Yan et al. run on 4 Nvidia 80GB A100 GPUs with batch size 1.[^yanDecodingSpeculativeDecoding2025] TAR is the tokens accepted per iteration.[^yanDecodingSpeculativeDecoding2025]

| Draft model | Target model | Setting | TAR | Throughput (tokens/s) | Reported by |
|---|---|---|---|---|---|
| NoFT-Wide-543M | LLaMa-65B | T=1.0 | not given | 24.08 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-65B | T=1.0 | not given | 24.32 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-1.3B | LLaMa-65B | T=1.0 | not given | 24.08 | [^yanDecodingSpeculativeDecoding2025] |
| Sheared-LLaMA-1.3B | LLaMa-65B | T=1.0 | not given | 12.30 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-543M | LLaMa-65B | T=0.5 | not given | 25.77 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-65B | T=0.5 | not given | 26.91 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-1.3B | LLaMa-65B | T=0.5 | not given | 26.39 | [^yanDecodingSpeculativeDecoding2025] |
| Sheared-LLaMA-1.3B | LLaMa-65B | T=0.5 | not given | 13.45 | [^yanDecodingSpeculativeDecoding2025] |
| Wide-829M | LLaMa-3.1-8B | Table 6 | not given | 60.44 | [^yanDecodingSpeculativeDecoding2025] |
| LLaMA-3.2-1B | LLaMa-3.1-8B | Table 6 | not given | 39.03 | [^yanDecodingSpeculativeDecoding2025] |
| Self-Speculative | LLaMa-3.1-8B | Table 6 | not given | 40.02 | [^yanDecodingSpeculativeDecoding2025] |
| Tiny-LLaMa-1.1B | Vicuna 33B | Table 8 | not given | 18.25 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | Vicuna 33B | Table 8 | not given | 26.55 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-65B | Table 7 | 2.74 | not given | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-2-70B | Table 7 | 2.68 | not given | [^yanDecodingSpeculativeDecoding2025] |

- NoFT-Wide-796M over Sheared-LLaMA-1.3B on Hellaswag: 97.7% higher throughput at T=1.0 and 100.0% at T=0.5.[^yanDecodingSpeculativeDecoding2025]
- Tiny-LLaMa-1.1B has a TAR $32\%$ higher than NoFT-Wide-796M on Hellaswag, and its latency is 4x higher.[^yanDecodingSpeculativeDecoding2025]
- SGLang reports per-benchmark throughput and latency only as normalized bar charts.[^zhengSGLangEfficientExecution2024]

## Known issues

- Rows from different papers are not directly comparable. The compression papers evaluate base models 10-shot.[^muralidharanCompactLanguageModels2024][^xiaShearedLLaMAAccelerating2024] Wang et al. evaluate Q4\_0 quantized instruct models on a 200-sample subset.[^wangEfficientOnDeviceDiffusion2026]
- Yan et al. find that the tokens accepted per iteration correlate little with task accuracy, with accuracy numbers taken from the OpenLLM Leaderboard.[^yanDecodingSpeculativeDecoding2025] The speed table therefore says nothing about HellaSwag accuracy.

# Contradictions

- **LLaMA-2 7B, 10-shot HellaSwag.** Xia et al. report 78.6 for LLaMA2-7B.[^xiaShearedLLaMAAccelerating2024] Muralidharan et al. report 79 for Llama-2 (6.7B parameters), with the metric named acc_norm.[^muralidharanCompactLanguageModels2024] Both are 10-shot. Muralidharan et al. print this column without a decimal, so the difference may come from precision; neither paper explains it. Xia et al. use lm-evaluation-harness and do not name the metric variant.[^xiaShearedLLaMAAccelerating2024]
- For Sheared-LLaMA-2.7B the two papers agree: 70.8 in both.[^xiaShearedLLaMAAccelerating2024][^muralidharanCompactLanguageModels2024]

## Related

- Datasets: [MMLU](mmlu.md), [GSM8K](gsm8k.md)
- Methods: [Sheared-LLaMA](../methods/sheared-llama.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Speculative decoding](../methods/speculative-decoding.md), [SGLang](../methods/sglang.md), [RadixAttention](../methods/radix-attention.md)

[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
