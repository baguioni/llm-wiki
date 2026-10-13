---
type: Dataset
title: MMLU
description: Multiple-choice benchmark with 57 subtasks, used in the wiki's papers as an accuracy test for compressed, agentic, and fine-tuned LLMs and as a prompt source for speed measurements.
tags: [dataset, evaluation, general-reasoning, pruning, speculative-decoding, multi-agent]
sources:
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: wangAgentDropoutDynamicAgent2025
    resource: zotero://select/items/@wangAgentDropoutDynamicAgent2025
    title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
---

# MMLU

## Overview

The wiki's papers use MMLU in two ways. Four papers report task accuracy on it: as a world-knowledge task among the Open LLM Leaderboard tasks,[^xiaShearedLLaMAAccelerating2024] as a downstream task for compressed models,[^muralidharanCompactLanguageModels2024] as the general reasoning task for multi-agent systems,[^wangAgentDropoutDynamicAgent2025] and as an out-of-domain check after domain-specific training.[^weiSWERLAdvancingLLM2025] Three papers use its questions only as prompts or as a workload for speed measurements, and report no accuracy.[^yanDecodingSpeculativeDecoding2025][^zhangLearningDraftAdaptive2026][^zhengSGLangEfficientExecution2024]

## Composition

- 57 subtasks across diverse domains, ranging from elementary mathematics and US history to computer science and law.[^zhangLearningDraftAdaptive2026]
- The questions are multiple-choice.[^wangAgentDropoutDynamicAgent2025]
- Sizes and splits are not stated in the wiki's papers.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Muralidharan et al. 2024](../papers/muralidharanCompactLanguageModels2024.md) | Accuracy of pruned and distilled Minitron models against baselines | 5-shot | See the accuracy table[^muralidharanCompactLanguageModels2024] |
| [Xia et al. 2024](../papers/xiaShearedLLaMAAccelerating2024.md) | Accuracy of [Sheared-LLaMA](../methods/sheared-llama.md) against similarly sized models | 5-shot, lm-evaluation-harness | See the accuracy table[^xiaShearedLLaMAAccelerating2024] |
| [Wang et al. 2025](../papers/wangAgentDropoutDynamicAgent2025.md) | General reasoning task for multi-agent systems | Llama3-8B-Instruct, Qwen2.5-72B-Instruct, Deepseek-V3-671B-Instruct | See the accuracy and token tables[^wangAgentDropoutDynamicAgent2025] |
| [Wei et al. 2025](../papers/weiSWERLAdvancingLLM2025.md) | Out-of-domain generalization | 70B Llama models, zero-shot greedy decoding | See the accuracy table[^weiSWERLAdvancingLLM2025] |
| [Yan et al. 2025](../papers/yanDecodingSpeculativeDecoding2025.md) | Prompts for [speculative decoding](../methods/speculative-decoding.md) throughput | Standard 5-shot, open-ended generation | See the speed table[^yanDecodingSpeculativeDecoding2025] |
| [Zhang et al. 2026](../papers/zhangLearningDraftAdaptive2026.md) | Cross-domain generalization of speedup | Llama-3.1-8B-Instruct, 80 sampled examples per subtask | See the speed table[^zhangLearningDraftAdaptive2026] |
| [Zheng et al. 2024](../papers/zhengSGLangEfficientExecution2024.md) | Serving workload for [SGLang](../methods/sglang.md) | 5-shot, one decoded token | Only normalized bar charts[^zhengSGLangEfficientExecution2024] |

### Protocols

- Muralidharan et al. and Xia et al. both report 5-shot MMLU.[^muralidharanCompactLanguageModels2024][^xiaShearedLLaMAAccelerating2024] Muralidharan et al. state that they ran all evaluations of Table 2 themselves; in Table 3 the columns marked `*` are reported from the corresponding papers.[^muralidharanCompactLanguageModels2024]
- Wei et al. use zero-shot greedy decoding and report the macro average over category accuracy.[^weiSWERLAdvancingLLM2025]
- Yan et al. use the standard 5-shot setup, feed the question and choices, and do not instruct the model to emit a single-letter answer; generation is open-ended.[^yanDecodingSpeculativeDecoding2025]
- Zheng et al. run 5-shot MMLU and decode one token. SGLang reuses the [KV cache](../methods/kv-cache.md) of the 5-shot examples with [RadixAttention](../methods/radix-attention.md).[^zhengSGLangEfficientExecution2024]

### Task quality: accuracy

Compression papers, 5-shot:

| Model | Setting | MMLU acc | Reported by |
|---|---|---|---|
| Llama-3 (8B) | 5-shot, base model | 65.3 | [^muralidharanCompactLanguageModels2024] |
| Llama-2 (6.7B) | 5-shot, base model | 46 | [^muralidharanCompactLanguageModels2024] |
| Mistral (7.3B) | 5-shot, base model | 64.1 | [^muralidharanCompactLanguageModels2024] |
| Gemma (8.5B) | 5-shot, base model | 64 | [^muralidharanCompactLanguageModels2024] |
| Nemotron-4 (15.6B) | 5-shot, base model | 66.6 | [^muralidharanCompactLanguageModels2024] |
| Nemotron-3 (8.5B) | 5-shot, base model | 54.7 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B (8.3B) | 5-shot, 94B training tokens | 63.8 | [^muralidharanCompactLanguageModels2024] |
| Phi-2 (2.7B) | 5-shot, base model | 57.5 | [^muralidharanCompactLanguageModels2024] |
| Gemma (2.5B) | 5-shot, base model | 42 | [^muralidharanCompactLanguageModels2024] |
| Gemma2 (2.6B) | 5-shot, value taken from the model's own paper | 51.3 | [^muralidharanCompactLanguageModels2024] |
| Qwen2 (1.5B) | 5-shot, value taken from the model's own paper | 56.5 | [^muralidharanCompactLanguageModels2024] |
| MiniCPM (2.7B) | 5-shot, value taken from the model's own paper | 53.5 | [^muralidharanCompactLanguageModels2024] |
| Minitron 4B (4.2B) | 5-shot, 94B training tokens | 58.6 | [^muralidharanCompactLanguageModels2024] |
| LLMPruner (9.8B) | 5-shot, 8 Billion target, pruning baseline | 25.2 | [^muralidharanCompactLanguageModels2024] |
| SliceGPT (9.9B) | 5-shot, 8 Billion target, pruning baseline | 37.1 | [^muralidharanCompactLanguageModels2024] |
| LaCo (9.8B) | 5-shot, 8 Billion target, pruning baseline | 45.9 | [^muralidharanCompactLanguageModels2024] |
| ShortGPT (9.8B) | 5-shot, 8 Billion target, pruning baseline | 54.7 | [^muralidharanCompactLanguageModels2024] |
| LLMPruner (4.8B) | 5-shot, 4 Billion target, pruning baseline | 23.33 | [^muralidharanCompactLanguageModels2024] |
| SliceGPT (4.9B) | 5-shot, 4 Billion target, pruning baseline | 28.92 | [^muralidharanCompactLanguageModels2024] |
| LaCo (4.9B) | 5-shot, 4 Billion target, pruning baseline | 26.45 | [^muralidharanCompactLanguageModels2024] |
| ShortGPT (4.9B) | 5-shot, 4 Billion target, pruning baseline | 43.96 | [^muralidharanCompactLanguageModels2024] |
| Sheared LLaMa (2.7B) | 5-shot, 4 Billion target, pruning baseline | 26.4 | [^muralidharanCompactLanguageModels2024] |
| LLaMA2-7B | 5-shot, 2T training tokens | 46.6 | [^xiaShearedLLaMAAccelerating2024] |
| OPT-1.3B | 5-shot, 300B training tokens | 24.7 | [^xiaShearedLLaMAAccelerating2024] |
| Pythia-1.4B | 5-shot, 300B training tokens | 25.7 | [^xiaShearedLLaMAAccelerating2024] |
| TinyLlama-1.1B | 5-shot, 3T training tokens | 25.5 | [^xiaShearedLLaMAAccelerating2024] |
| Sheared-LLaMA-1.3B | 5-shot, 50B training tokens | 25.7 | [^xiaShearedLLaMAAccelerating2024] |
| OPT-2.7B | 5-shot, 300B training tokens | 25.9 | [^xiaShearedLLaMAAccelerating2024] |
| Pythia-2.8B | 5-shot, 300B training tokens | 26.9 | [^xiaShearedLLaMAAccelerating2024] |
| INCITE-Base-3B | 5-shot, 800B training tokens | 27.0 | [^xiaShearedLLaMAAccelerating2024] |
| Open-LLaMA-3B-v1 | 5-shot, 1T training tokens | 27.0 | [^xiaShearedLLaMAAccelerating2024] |
| Open-LLaMA-3B-v2 | 5-shot, 1T training tokens | 26.9 | [^xiaShearedLLaMAAccelerating2024] |
| Sheared-LLaMA-2.7B | 5-shot, 50B training tokens | 26.4 | [^xiaShearedLLaMAAccelerating2024] |

Minitron retraining ablations (the shot count is not restated for these tables):

| Model | Setting | MMLU | Reported by |
|---|---|---|---|
| 4B-Random-Init | 150B tokens (iso-compute) | 24.36 | [^muralidharanCompactLanguageModels2024] |
| 4B-Random-Init | 400B tokens | 26.24 | [^muralidharanCompactLanguageModels2024] |
| 4B-Pruned (prune Nemotron-4 15B) | 150B tokens (iso-compute) | 24.57 | [^muralidharanCompactLanguageModels2024] |
| 4B-Pruned-Distill (prune Nemotron-4 15B) | 100B tokens (iso-compute) | 37.81 | [^muralidharanCompactLanguageModels2024] |
| 4B-Pruned-Distill (prune Minitron 8B) | 100B tokens (iso-compute) | 42.45 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B | $L_{logits}+L_{is}$, 18.9B tokens | 58.0 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B | $L_{logits}$, 18.9B tokens | 58.3 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B | $L_{logits}$, 94B tokens | 62.8 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B-Width-pruned | Phase1 + Phase2, 113B tokens | 54.7 | [^muralidharanCompactLanguageModels2024] |
| Minitron 8B-Width-pruned | Phase2 only, 94B tokens | 61.9 | [^muralidharanCompactLanguageModels2024] |

- Pruning the 15B model with distillation gains 13.5% on MMLU compared to training from scratch with equivalent compute, and pruning an 8B model instead of the 15B model gains an additional 4.6%.[^muralidharanCompactLanguageModels2024]
- The two-step route (15B to 8B, then 8B to 4B) achieves a 12% improvement in MMLU scores compared to the one-shot strategy.[^muralidharanCompactLanguageModels2024]
- With iterative depth pruning, the MMLU score is retained up to 26 layers, with a sharp drop at 20 layers.[^muralidharanCompactLanguageModels2024]

Out-of-domain generalization of SWE-RL (zero-shot greedy decoding, macro average over category accuracy):

| Model | Setting | MMLU | Reported by |
|---|---|---|---|
| Llama-3.3-70B-Instruct | zero-shot, greedy | 86.49 | [^weiSWERLAdvancingLLM2025] |
| Llama3-SWE-SFT-70B | zero-shot, greedy | 85.26 | [^weiSWERLAdvancingLLM2025] |
| Llama3-SWE-RL-70B | zero-shot, greedy | 86.82 | [^weiSWERLAdvancingLLM2025] |

Using Eval Arena, Wei et al. state that improvements of > 0.8 percentage points on MMLU are significant on their own.[^weiSWERLAdvancingLLM2025]

Multi-agent systems (Table 1 of Wang et al.; fully connected initial graph, temperature 1; the source does not name the metric unit and the text calls the gains "accuracy"):

| Base model | Method | MMLU | Reported by |
|---|---|---|---|
| Llama3-8B-Instruct | Vanilla | 53.59 | [^wangAgentDropoutDynamicAgent2025] |
| Llama3-8B-Instruct | [CoT](../methods/chain-of-thought.md) | 56.86 | [^wangAgentDropoutDynamicAgent2025] |
| Llama3-8B-Instruct | $\text{MAS}_{round=1}$ | 56.21 | [^wangAgentDropoutDynamicAgent2025] |
| Llama3-8B-Instruct | $\text{MAS}_{round=T}$ | 60.13 | [^wangAgentDropoutDynamicAgent2025] |
| Llama3-8B-Instruct | AgentPrune | 60.78 | [^wangAgentDropoutDynamicAgent2025] |
| Llama3-8B-Instruct | AgentDropout | 62.75 | [^wangAgentDropoutDynamicAgent2025] |
| Qwen2.5-72B-Instruct | Vanilla | 82.35 | [^wangAgentDropoutDynamicAgent2025] |
| Qwen2.5-72B-Instruct | CoT | 83.66 | [^wangAgentDropoutDynamicAgent2025] |
| Qwen2.5-72B-Instruct | $\text{MAS}_{round=1}$ | 82.35 | [^wangAgentDropoutDynamicAgent2025] |
| Qwen2.5-72B-Instruct | $\text{MAS}_{round=T}$ | 84.31 | [^wangAgentDropoutDynamicAgent2025] |
| Qwen2.5-72B-Instruct | AgentPrune | 83.66 | [^wangAgentDropoutDynamicAgent2025] |
| Qwen2.5-72B-Instruct | AgentDropout | 84.97 | [^wangAgentDropoutDynamicAgent2025] |
| Deepseek-V3-671B-Instruct | Vanilla | 84.97 | [^wangAgentDropoutDynamicAgent2025] |
| Deepseek-V3-671B-Instruct | CoT | 84.31 | [^wangAgentDropoutDynamicAgent2025] |
| Deepseek-V3-671B-Instruct | $\text{MAS}_{round=1}$ | 89.98 | [^wangAgentDropoutDynamicAgent2025] |
| Deepseek-V3-671B-Instruct | $\text{MAS}_{round=T}$ | 89.54 | [^wangAgentDropoutDynamicAgent2025] |
| Deepseek-V3-671B-Instruct | AgentPrune | 90.20 | [^wangAgentDropoutDynamicAgent2025] |
| Deepseek-V3-671B-Instruct | AgentDropout | 90.85 | [^wangAgentDropoutDynamicAgent2025] |

AgentDropout ablations, all on Llama3-8B-Instruct. The last five rows copy the Edge DR. and Node DR. marks of the dropout strategy table; for Random Dropout, ✓ marks the step where the random strategy is applied while the other step stays as in AgentDropout.[^wangAgentDropoutDynamicAgent2025]

| Method | Setting | MMLU | Reported by |
|---|---|---|---|
| MAS | Layered initial graph | 57.52 | [^wangAgentDropoutDynamicAgent2025] |
| AgentPrune | Layered initial graph | 59.48 | [^wangAgentDropoutDynamicAgent2025] |
| AgentDropout | Layered initial graph | 61.44 | [^wangAgentDropoutDynamicAgent2025] |
| MAS | Random initial graph | 62.75 | [^wangAgentDropoutDynamicAgent2025] |
| AgentPrune | Random initial graph | 63.40 | [^wangAgentDropoutDynamicAgent2025] |
| AgentDropout | Random initial graph | 64.71 | [^wangAgentDropoutDynamicAgent2025] |
| AgentDropout | Dropout rate 0.8 | 57.52 | [^wangAgentDropoutDynamicAgent2025] |
| AgentDropout | Dropout rate 0.6 | 60.78 | [^wangAgentDropoutDynamicAgent2025] |
| AgentDropout | Dropout rate 0.4 | 60.13 | [^wangAgentDropoutDynamicAgent2025] |
| AgentDropout | Dropout rate 0.2 | 62.75 | [^wangAgentDropoutDynamicAgent2025] |
| Random Dropout | Edge DR. ✗, Node DR. ✓ | 61.72 | [^wangAgentDropoutDynamicAgent2025] |
| Random Dropout | Edge DR. ✓, Node DR. ✗ | 60.13 | [^wangAgentDropoutDynamicAgent2025] |
| Learned Dropout | Edge DR. ✗, Node DR. ✓ | 63.76 | [^wangAgentDropoutDynamicAgent2025] |
| Learned Dropout | Edge DR. ✓, Node DR. ✗ | 61.87 | [^wangAgentDropoutDynamicAgent2025] |
| Single Learning | Edge DR. ✓, Node DR. ✓ | 60.78 | [^wangAgentDropoutDynamicAgent2025] |

### Token consumption on MMLU

Llama3-8B-Instruct. Ptok. is prompt tokens and Ctok. is completion tokens.[^wangAgentDropoutDynamicAgent2025]

| Method | Ptok. | Ctok. | Reported by |
|---|---|---|---|
| Vanilla | 99K | 44K | [^wangAgentDropoutDynamicAgent2025] |
| CoT | 129K | 70K | [^wangAgentDropoutDynamicAgent2025] |
| $\text{MAS}_{round=1}$ | 1.4M | 355K | [^wangAgentDropoutDynamicAgent2025] |
| $\text{MAS}_{round=T}$ | 1.6M | 387K | [^wangAgentDropoutDynamicAgent2025] |
| AgentPrune | 1.3M | 367K | [^wangAgentDropoutDynamicAgent2025] |
| AgentDropout | 1.1M | 333K | [^wangAgentDropoutDynamicAgent2025] |

### Speed: speculative decoding throughput on MMLU prompts

These rows measure decoding speed with MMLU questions as prompts. They are not accuracy results. Yan et al. run on 4 Nvidia 80GB A100 GPUs with batch size 1.[^yanDecodingSpeculativeDecoding2025] TAR is the tokens accepted per iteration.[^yanDecodingSpeculativeDecoding2025]

| Draft model | Target model | Setting | TAR | Throughput (tokens/s) | Reported by |
|---|---|---|---|---|---|
| NoFT-1.3B | LLaMa-65B | greedy | 3.81 | 23.10 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-1.3B | LLaMa-65B | greedy | 3.70 | 32.59 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-543M | LLaMa-65B | T=1.0 | not given | 20.54 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-65B | T=1.0 | not given | 24.32 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-1.3B | LLaMa-65B | T=1.0 | not given | 22.99 | [^yanDecodingSpeculativeDecoding2025] |
| Sheared-LLaMA-1.3B | LLaMa-65B | T=1.0 | not given | 12.06 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-543M | LLaMa-65B | T=0.5 | not given | 26.08 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-65B | T=0.5 | not given | 29.64 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-1.3B | LLaMa-65B | T=0.5 | not given | 28.43 | [^yanDecodingSpeculativeDecoding2025] |
| Sheared-LLaMA-1.3B | LLaMa-65B | T=0.5 | not given | 14.60 | [^yanDecodingSpeculativeDecoding2025] |
| Wide-829M | LLaMa-3.1-8B | Table 6 | not given | 61.77 | [^yanDecodingSpeculativeDecoding2025] |
| LLaMA-3.2-1B | LLaMa-3.1-8B | Table 6 | not given | 44.89 | [^yanDecodingSpeculativeDecoding2025] |
| Self-Speculative | LLaMa-3.1-8B | Table 6 | not given | 40.41 | [^yanDecodingSpeculativeDecoding2025] |
| Tiny-LLaMa-1.1B | Vicuna 33B | Table 8 | not given | 20.78 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | Vicuna 33B | Table 8 | not given | 29.87 | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-65B | Table 7 | 2.66 | not given | [^yanDecodingSpeculativeDecoding2025] |
| NoFT-Wide-796M | LLaMa-2-70B | Table 7 | 2.55 | not given | [^yanDecodingSpeculativeDecoding2025] |

- NoFT-Wide-796M over Sheared-LLaMA-1.3B on MMLU: 101.6% higher throughput at T=1.0 and 103.0% at T=0.5.[^yanDecodingSpeculativeDecoding2025]
- The deep 1.3B draft (NoFT-1.3B) achieves $3\%$ higher TAR, while the wide one (NoFT-Wide-1.3B) reduces draft latency by $49\%$ and improves overall throughput by $41\%$.[^yanDecodingSpeculativeDecoding2025]
- Tiny-LLaMa-1.1B has a TAR $35\%$ higher than NoFT-Wide-796M on MMLU, and its latency is 4x higher.[^yanDecodingSpeculativeDecoding2025]
- Yan et al. also use MMLU to validate their analytical throughput model (maximum deviation $3.5\%$) and to compute the latency reduction that larger OPT drafts need to reach parity with OPT-125M.[^yanDecodingSpeculativeDecoding2025]
- Learning to Draft (LTD) against [EAGLE-3](../methods/eagle-3.md) on Llama-3.1-8B-Instruct, 80 sampled examples per subtask: LTD outperforms Eagle3 on 54 out of 57 subtasks, with an average speedup improvement of 5% and over $10\%$ in mathematics and logic-related tasks. Per-subtask values are given only in a figure.[^zhangLearningDraftAdaptive2026]
- SGLang: with four workers on the MMLU dataset, data-parallel RadixAttention achieves linear scaling and an optimal cache hit rate. Per-benchmark throughput and latency are given only as normalized bar charts.[^zhengSGLangEfficientExecution2024]

## Known issues

- Rows from different papers are not directly comparable. Wang et al. evaluate instruct models inside agent pipelines at temperature 1,[^wangAgentDropoutDynamicAgent2025] Wei et al. use zero-shot greedy decoding with a macro average over categories,[^weiSWERLAdvancingLLM2025] and the two compression papers use 5-shot evaluation of base models.[^muralidharanCompactLanguageModels2024][^xiaShearedLLaMAAccelerating2024]
- Yan et al. find that the tokens accepted per iteration correlate little with task accuracy, with accuracy numbers taken from the OpenLLM Leaderboard.[^yanDecodingSpeculativeDecoding2025] The speed table therefore says nothing about MMLU accuracy.

# Contradictions

- **LLaMA-2 7B, 5-shot MMLU.** Xia et al. report 46.6 for LLaMA2-7B.[^xiaShearedLLaMAAccelerating2024] Muralidharan et al. report 46 for Llama-2 (6.7B parameters).[^muralidharanCompactLanguageModels2024] Both are 5-shot. Muralidharan et al. print this column without a decimal, so the difference may come from precision; neither paper explains it. Xia et al. use lm-evaluation-harness,[^xiaShearedLLaMAAccelerating2024] and Muralidharan et al. state only that they ran the evaluations themselves.[^muralidharanCompactLanguageModels2024]
- For Sheared-LLaMA-2.7B the two papers agree: 26.4 in both.[^xiaShearedLLaMAAccelerating2024][^muralidharanCompactLanguageModels2024]

## Related

- Datasets: [HellaSwag](hellaswag.md), [GSM8K](gsm8k.md), [HumanEval](humaneval.md)
- Methods: [Sheared-LLaMA](../methods/sheared-llama.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [SGLang](../methods/sglang.md), [RadixAttention](../methods/radix-attention.md)

[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^wangAgentDropoutDynamicAgent2025]: Wang et al. 2025
[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
