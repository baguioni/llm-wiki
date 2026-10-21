---
type: Analysis
title: Training budgets for pruning recovery and drafter distillation
description: How long the papers train to recover a pruned model or to distill a drafter; general-LM recovery runs for 50B to 94B tokens with no epoch count, drafter recoveries range from 1M tokens to about 462B, DistillSpec and GKD give 40K to 300K steps, and AdaSPEC trains 3 epochs as standard and 6 to 30 at its tuned optimum.
tags: [structured-pruning, knowledge-distillation, draft-model, training-budget, speculative-decoding, speculative-drafter]
question: How many epochs or tokens do Minitron and the drafter distillation papers (DistillSpec, AdaSPEC, and others) train for when recovering or fine-tuning a model?
sources:
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
  - id: agarwalOnPolicyDistillationLanguage2024
    resource: zotero://select/items/@agarwalOnPolicyDistillationLanguage2024
    title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Training budgets for pruning recovery and drafter distillation

## Question

How long do the papers train to recover a pruned model, or to distill or fine-tune a draft model? Minitron gives tokens rather than epochs. Do DistillSpec, AdaSPEC, and the other papers report epochs, steps, or tokens? This sizes the recovery stage of [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md).

## Answer

Only the fine-tuning-style papers count epochs. The pruning papers report tokens, and DistillSpec and GKD report optimizer steps.

- **Recovering a pruned general LM** takes tens of billions of tokens and less than one pass over a pretraining corpus. Minitron uses 94B tokens, which it describes as less than 3% of the original training data.[^muralidharanCompactLanguageModels2024] Sheared LLaMA uses 50B tokens of continued pre-training.[^xiaShearedLLaMAAccelerating2024]
- **Recovering a pruned drafter** has the widest spread. Yan et al. use 1 million tokens.[^yanDecodingSpeculativeDecoding2025] Osprey runs five epochs over a 100B-token sample, about 462B to 500B tokens, but a 10k-step checkpoint (84B tokens) adapts almost as well.[^bieOspreyTargetagnosticPretraining2026]
- **Distilling a task drafter:** DistillSpec trains for 300,000 steps at batch 32.[^zhouDistillSpecImprovingSpeculative2024] GKD trains for 40,000 to 100,000 steps.[^agarwalOnPolicyDistillationLanguage2024] AdaSPEC uses 3 epochs as its standard setting. When epochs are tuned on validation data, its draft settles at 6 to 30 epochs.[^huAdaSPECSelectiveKnowledge2025]
- **Fine-tuning a drafter that already exists** takes 1 to 4 epochs: 1 for DPara and the DeepSeek MTP module in LK Losses, and 4 for PARD.[^liuWhenParallelDrafter2026][^samarinLKLossesDirect2026][^anPARDAcceleratingLLM2025]

## Evidence

### Recovery after structured pruning

| Paper | Pruned model | Recovery budget | Schedule details |
|---|---|---|---|
| [Minitron](../papers/muralidharanCompactLanguageModels2024.md) | Nemotron-4 15B to 8B and 4B | 94B tokens per final model; 1.8B tokens (400 steps) for lightweight retraining | Cosine LR decay from $2^{-4}$ to $4.5^{-7}$, same optimizer settings as Nemotron-4; candidate rankings stabilize after $\sim$300 steps[^muralidharanCompactLanguageModels2024] |
| [Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) | LLaMA2-7B to 1.3B and 2.7B | 0.4B tokens for pruning, 50B for continued pre-training | Pruning 3,200 steps at 131K tokens per batch; continued pre-training 51,200 steps at 1M tokens per batch, LR 0.0001, warmup 3%[^xiaShearedLLaMAAccelerating2024] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Qwen3-4B to 2 blocks | Five epochs over a 100B-token FineWeb sample, "approximately 500B" tokens; 55k steps, about 462B tokens, elsewhere | Then adaptation to the target: 97.5k optimizer steps (3 epochs), about 0.8B tokens[^bieOspreyTargetagnosticPretraining2026] |
| [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) | LLaMa-3.2-1B to Wide-829M | Distillation over 1 million tokens, within 10 minutes | Not stated[^yanDecodingSpeculativeDecoding2025] |
| [My experiment](../experiments/minitron-pard-qwen3-14b.md) | Qwen3-14B to the Qwen3-0.6B shape | 3 epochs, about 18.9M target tokens per epoch, 57M in all | About 1,543 steps per epoch, 32 sequences per step, lr 3e-5 cosine[^minitron-pard-qwen3-14b] |

What the budget buys:

- Minitron: the ranking of width against depth+width pruning flips around 200 steps (0.8B tokens).[^muralidharanCompactLanguageModels2024] Removing 16 layers at once and distilling on 30.2B tokens beats iterative removal, even when the iterative budget is raised to 86.4B tokens.[^muralidharanCompactLanguageModels2024]
- Osprey: adapted the same way, the 10k-step checkpoint reaches an overall AL of 3.552 and the 55k-step checkpoint 3.578.[^bieOspreyTargetagnosticPretraining2026]
- My run: the held-out recovery curve had flattened by the third epoch, at +0.001 top-1 per 250 steps. The report concludes that more epochs over the same answers will not help.[^minitron-pard-qwen3-14b]

### Distilling a drafter from its target

| Paper | Models | Budget | Schedule details |
|---|---|---|---|
| [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md) | T5-Small from T5-XL; 33M from 234M GPT-like on LM1B | 300,000 training steps, batch size 32 | LR 0.0003, 5,000 warmup steps, cosine cooldown from step 150,000 to 300,000, Adafactor; draft and target start from supervised fine-tuned checkpoints[^zhouDistillSpecImprovingSpeculative2024] |
| [GKD](../papers/agarwalOnPolicyDistillationLanguage2024.md) | T5 students from a T5-XL teacher | XSum and GSM8K 40,000 steps; WMT en-de 100,000 steps; FLAN instruction tuning 50,000 steps | Batch 32 (128 for FLAN), Adafactor; all students start from the same supervised fine-tuned student[^agarwalOnPolicyDistillationLanguage2024] |
| [AdaSPEC](../papers/huAdaSPECSelectiveKnowledge2025.md) | Pythia-31M from Pythia-1.4B; CodeGen-350M from Phi-2 | 3 epochs in the 3-Epoch setting; 1 to 30 epochs in the Optimal-Epoch setting | Batch 16 (8 for MBPP), LR 1e-5 to 3e-4[^huAdaSPECSelectiveKnowledge2025] |

AdaSPEC's Optimal-Epoch setting first fine-tunes the target. It then distills a reference drafter and the final draft, choosing each epoch count from 1, 3, 6, 10, 15, 20, and 30 (1, 3, 6, and 10 for XSUM and CNN/Daily Mail). The chosen epochs (Table 9) are:[^huAdaSPECSelectiveKnowledge2025]

| Task | Pair | Target | Reference | Draft |
|---|---|---|---|---|
| GSM8K | Pythia 31M→1.4B | 6 | 15 | 30 |
| GSM8K | Codegen-350M→Phi-2 | 3 | 30 | 30 |
| Alpaca | Pythia 31M→1.4B | 1 | 15 | 30 |
| Alpaca | Codegen-350M→Phi-2 | 1 | 20 | 15 |
| MBPP | Pythia 31M→1.4B | 1 | 30 | 6 |
| MBPP | Codegen-350M→Phi-2 | 1 | 10 | 6 |
| CNN/Daily Mail | both pairs | 1 | 10 | 10 |
| XSUM | both pairs | 1 | 10 | 10 |

All rows: [^huAdaSPECSelectiveKnowledge2025]

- DistillSpec reports that supervised KD shows declining acceptance rates after $\sim$40k training steps on XSum and CNNDM.[^zhouDistillSpecImprovingSpeculative2024]
- AdaSPEC says it trains for less time than DistillSpec because of compute constraints. It describes DistillSpec's 300,000-step TVD schedule as costly and prone to overfitting.[^huAdaSPECSelectiveKnowledge2025]
- AdaSPEC also uses 3 epochs when combined with EAGLE (Vicuna-7B-v1.3 on ShareGPT) and for the Qwen2.5-0.5B/32B pair on GSM8K.[^huAdaSPECSelectiveKnowledge2025]

### Fine-tuning an existing drafter

- DPara fine-tunes the official DSpark checkpoints for one epoch.[^liuWhenParallelDrafter2026]
- LK Losses trains draft models from scratch for 10 epochs and fine-tunes the DeepSeek MTP module for 1 epoch.[^samarinLKLossesDirect2026]
- PARD trains for 4 epochs, and its ablations use a single epoch on a 93K subset.[^anPARDAcceleratingLLM2025]

More drafter recipes, with dataset sizes, are in [Drafter training data across papers](drafter-training-data-across-papers.md).

## Caveats

- Units differ: tokens (Minitron, Sheared LLaMA, Osprey pretraining, Yan et al.), optimizer steps (DistillSpec, GKD), and epochs (AdaSPEC, PARD, DPara, LK Losses). The wiki does not record the training-set sizes for DistillSpec and GKD, so their step counts cannot be turned into epochs here.
- Osprey gives its pretraining budget as both about 500B and about 462B tokens. Its paper page tracks the inconsistency.[^bieOspreyTargetagnosticPretraining2026]
- The pruning papers recover general LMs on pretraining corpora. DistillSpec, GKD, and AdaSPEC distill small task-specific drafters on single task datasets. The budgets are not directly comparable.
- **Inference.** 94B tokens against an 8T-token blend is well under one epoch, which agrees with Minitron's "<3%" figure. The paper itself gives no epoch count.

## Related

- [Drafter training data across papers](drafter-training-data-across-papers.md)
- [Target-aware recovery of compressed drafters](target-aware-recovery-of-compressed-drafters.md)
- [Where Osprey's ideas fit a pruned-target PARD pipeline](osprey-ideas-for-pruned-target-pard-pipeline.md)
- [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md)
- Methods: [Structured pruning](../methods/structured-pruning.md), [Minitron](../methods/minitron.md), [Sheared LLaMA](../methods/sheared-llama.md), [Knowledge distillation](../methods/knowledge-distillation.md), [DistillSpec](../methods/distillspec.md), [AdaSPEC](../methods/adaspec.md), [GKD](../methods/gkd.md)

[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^minitron-pard-qwen3-14b]: My experiment, `raw/experiments/minitron-pard-qwen3-14b.md`
