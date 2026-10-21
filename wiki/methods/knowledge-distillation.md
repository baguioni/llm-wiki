---
type: Method
title: Knowledge Distillation
description: Training a smaller student model under the supervision of a larger teacher model, used in this wiki to retrain pruned LLMs and to align speculative-decoding draft models with their targets.
tags: [knowledge-distillation, model-compression, speculative-decoding, draft-model, structured-pruning]
sources:
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models
  - id: agarwalOnPolicyDistillationLanguage2024
    resource: zotero://select/items/@agarwalOnPolicyDistillationLanguage2024
    title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Knowledge Distillation

## Overview

Knowledge distillation (KD) transfers knowledge from a larger or more complex model, the teacher, to a smaller or simpler model, the student. The student mimics the output and/or the intermediate states of the teacher.[^muralidharanCompactLanguageModels2024] DistillSpec describes it as training high-quality smaller student models with the supervision of larger teacher models, to reduce inference cost while maintaining model quality.[^zhouDistillSpecImprovingSpeculative2024]

The papers in this wiki use KD for two purposes:

- **Retraining a pruned model.** The uncompressed model is the teacher and the pruned model is the student.[^muralidharanCompactLanguageModels2024]
- **Training a draft model for [speculative decoding](../methods/speculative-decoding.md).** The draft model is the student and approximates the output distribution of the target model, the teacher.[^samarinLKLossesDirect2026] Here the goal is a higher acceptance rate, not better task performance for the student.[^zhouDistillSpecImprovingSpeculative2024]

## How it works

- **Divergence objective.** The student is trained to minimize a divergence $D$ between the teacher and student next-token distributions over a training set $\mathscr{G}$.[^zhouDistillSpecImprovingSpeculative2024] The commonly used divergences are forward KL, $\operatorname{KL}(p\|q)=\sum_{i}p_{i}\log(p_{i}/q_{i})$, reverse KL, $\text{KL}(q\|p)$, and Total Variation distance, $\operatorname{TV}(p,q)=\frac{1}{2}\sum_{i}|p_{i}-q_{i}|$.[^samarinLKLossesDirect2026]
- **Standard objective for draft models.** The standard training objective has been KL divergence, or equivalently cross-entropy, between the target and draft distributions.[^samarinLKLossesDirect2026]
- **Combined loss for pruned models.** Muralidharan et al. define the total loss as $L=L_{\text{CLM}}+L_{logits}+\alpha\times L_{is}$, where $L_{CLM}$ is the student cross-entropy loss against ground truth labels, $L_{logits}$ is the logit-based KD loss, $L_{is}$ is the intermediate-state KD loss, and $\alpha$ is computed dynamically as $\frac{L_{logits}}{L_{is}}$. A shared linear transformation upscales the student hidden state to the teacher hidden state dimension.[^muralidharanCompactLanguageModels2024]

## Variants

- **Black-box vs white-box.** In black-box KD only the teacher's output generations are accessible during student training. White-box KD uses access to the teacher's weights and logits.[^zhouDistillSpecImprovingSpeculative2024]
- **By divergence and training data** (Table 1 of DistillSpec):[^zhouDistillSpecImprovingSpeculative2024]

| Name | Divergence | Training Data ($\mathscr{G}$) |
|---|---|---|
| SeqKD (black-box KD) | FKL | Data generated by teacher $\mathscr{M}_p$ |
| Supervised KD | FKL | Fixed dataset of input-output pairs |
| ImitKD | FKL | Fixed dataset + data generated by $\mathscr{M}_q^\theta$ |
| f-Distill | TVD | Data generated by $\mathscr{M}_q^\theta$ and $\mathscr{M}_p$ |
| On-policy GKD | FKL / JSD | On-policy data from student $\mathscr{M}_q^\theta$ |

- **Logit-only vs intermediate-state distillation.** Muralidharan et al. recommend logit-only distillation when depth is not reduced significantly, and (logit + intermediate state + embedding) distillation when depth is reduced significantly.[^muralidharanCompactLanguageModels2024]
- **Combined objectives for draft heads.** LK Losses reports that [Medusa](../methods/medusa.md) mixes the KL loss with the LM objective for the target model, and that [EAGLE](../methods/eagle.md) extends KL with a regression loss on hidden states of the last layer.[^samarinLKLossesDirect2026]
- **[DistillSpec](../methods/distillspec.md).** White-box KD for draft models with on-policy data and a task-tuned divergence.[^zhouDistillSpecImprovingSpeculative2024]
- **On-policy distillation ([GKD](../methods/gkd.md)).** The student is trained on its own sampled sequences with the teacher's token probabilities as labels, mixed with a fixed dataset at a student data fraction $\lambda$, and with a free choice of divergence (forward KL, reverse KL, generalized JSD). Supervised KD and on-policy KD are the cases $\lambda=0$ and $\lambda=1$ with forward KL.[^agarwalOnPolicyDistillationLanguage2024]
- **Selective distillation ([AdaSPEC](../methods/adaspec.md)).** The draft is distilled with forward KL only on the top 40% of tokens ranked by how much its KL to the target exceeds that of a DistillSpec-distilled reference copy.[^huAdaSPECSelectiveKnowledge2025]

## Papers using it

- [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md) distills a T5-Small (77M) draft from a T5-XL (3B) target, and a 33M GPT-like draft from a 234M target, and reports a 10$-$45% speedup improvement over standard SD.[^zhouDistillSpecImprovingSpeculative2024] Supervised KD on a fixed ground-truth dataset ranks lowest in all settings, and f-Distill and GKD, which use only model-generated data, outperform the other variants.[^zhouDistillSpecImprovingSpeculative2024] In a model-garden setting, distilling the target as well reduces relative latency from 17.3 to 2.7 on [XSum](../datasets/xsum.md) and from 15.0 to 1.4 on [GSM8K](../datasets/gsm8k.md).[^zhouDistillSpecImprovingSpeculative2024]
- [GKD](../papers/agarwalOnPolicyDistillationLanguage2024.md) distills supervised fine-tuned T5-XL into T5-small, base, and large students on summarization, translation, and GSM8K, and FLAN T5-XL into FLAN T5-Base on FLAN2021. Averaged over student sizes, on-policy GKD's gain over the initial student is 2.1× (summarization), 1.7× (translation), and 1.9× (arithmetic reasoning) the gain of baseline KD methods.[^agarwalOnPolicyDistillationLanguage2024] On XSum, on-policy GKD on 5% of the inputs, without ground-truth summaries, beats supervised KD and ImitKD trained on the full dataset.[^agarwalOnPolicyDistillationLanguage2024]
- [AdaSPEC](../papers/huAdaSPECSelectiveKnowledge2025.md) argues that minimizing KL over all tokens is misaligned with acceptance rate because a small draft cannot absorb all of the target's knowledge.[^huAdaSPECSelectiveKnowledge2025] Filtering tokens raises acceptance over DistillSpec on every task and model pair tested, for example 46.88% → 47.73% and 49.88% → 65.12% on MBPP with Pythia-31M → 1.4B (3-Epoch and Optimal-Epoch).[^huAdaSPECSelectiveKnowledge2025]
- [Compact Language Models via Pruning and Knowledge Distillation](../papers/muralidharanCompactLanguageModels2024.md) retrains [structurally pruned](../methods/structured-pruning.md) models with KD from the unpruned Nemotron-4 15B teacher, and states that, to the best of the authors' knowledge, it is the first to employ distillation from an uncompressed teacher to improve the retraining of structurally-pruned student models.[^muralidharanCompactLanguageModels2024]
  - Strategies to train a 4B model (Table 11, `∗` marks iso-compute settings):[^muralidharanCompactLanguageModels2024]

    | Model | Tokens | Hellaswag | MMLU |
    |---|---|---|---|
    | 4B-Random-Init | 150B∗ | 46.22 | 24.36 |
    | 4B-Random-Init | 400B | 48.23 | 26.24 |
    | 4B-Pruned (prune Nemotron-4 15B) | 150B∗ | 50.85 | 24.57 |
    | 4B-Pruned-Distill (prune Nemotron-4 15B) | 100B∗ | 51.04 | 37.81 |
    | 4B-Pruned-Distill (prune Minitron 8B) | 100B∗ | 52.04 | 42.45 |

  - Loss ablation on Nemotron-3 8B (Table 15): $L_{logits}$(KLD) alone gives LM loss 2.107 and WikiText PPL 8.720, against 2.117 and 8.791 for $L_{CLM}$ + $L_{logits}$(KLD). MSE, RKLD, and cosine logit losses are worse.[^muralidharanCompactLanguageModels2024]
  - Softmax temperature $\tau$ was tried at 0.1, 0.5, 1.0, and 3.0, and $\tau$=1.0 was best.[^muralidharanCompactLanguageModels2024]
  - Minitron 8B with $L_{logits}$ at 18.9B tokens scores 58.3 on [MMLU](../datasets/mmlu.md) and 73.8 on [HellaSwag](../datasets/hellaswag.md), against 58.0 and 73.6 with $L_{logits}+L_{is}$ (Table 18).[^muralidharanCompactLanguageModels2024]
  - In the final retraining step for Minitron 4B, Nemotron-4 15B as the teacher gives better results than Minitron 8B as the teacher.[^muralidharanCompactLanguageModels2024]
- [LK Losses](../papers/samarinLKLossesDirect2026.md) states that the training of speculators has been predominantly framed as KD, and argues that KL divergence is only a proxy for acceptance rate.[^samarinLKLossesDirect2026] KL divergence and acceptance rate share the same global optimum, but draft models typically have 1-5% of the target model parameters and converge to suboptimal solutions, where minimizing KL does not guarantee maximizing acceptance rate.[^samarinLKLossesDirect2026] Its LK losses target acceptance rate directly and are compared against the standard KL-based training, with reported gains of up to 8-10% in average acceptance length.[^samarinLKLossesDirect2026]
- [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) prunes a Wide-829M draft from LLaMa-3.2-1B and, following Muralidharan et al., recovers its token acceptance rate by distilling over 1 million tokens, which finishes within 10 minutes.[^yanDecodingSpeculativeDecoding2025] With LLaMa-3.1-8B as the target, Wide-829M achieves $42.6\%$ higher throughput than LLaMa-3.2-1B.[^yanDecodingSpeculativeDecoding2025] The paper lists draft model distillation (DistillSpec) among the prior ways to improve speculative decoding.[^yanDecodingSpeculativeDecoding2025]
- [Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) does not use KD. It discusses KD in related work and continues pre-training its pruned models with a standard language modeling objective.[^xiaShearedLLaMAAccelerating2024]
- [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) adds a KD term to the cross-entropy loss of its parallel drafter, $\hat{s}_{n,k}(\beta\mathcal{L}^{\mathrm{CE}}+\mathcal{L}^{\mathrm{KD}})$ with $\beta=0.1$, and weights both by the target's cumulative confidence. The paper does not give the form of the KD loss.[^anPARD2TargetAlignedParallel2026]
- [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) distills each target into a drafter that was first pretrained without any target, with a cross-entropy loss against the target's logits over the TTT steps.[^bieOspreyTargetagnosticPretraining2026]
- [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md) distills an adapter with the structure of one self-attention module to imitate the LLM's middle layers, so that the device's shallow layers, adapter, and head form a draft model.[^xieNovelHatShapedDeviceCloud2025]
- My experiment [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) recovers a pruned Qwen3-14B by online white-box distillation from Qwen3-14B: forward KL over the full vocabulary at temperature 1.0, on answer tokens of 49,372 of the target's own greedy answers, 3 epochs and 57M target tokens. The following PARD-1 stage uses hard labels on the same answers, with no teacher distribution.[^minitron-pard-qwen3-14b]
  - Recovery lifts top-1 on Spec-Bench from 0.038 to 0.572 and AR MAT at γ=5 from 1.04 to 2.17. On held-out answers, forward KL falls from 9.78 to 1.57 and the curve is flat by the third epoch.[^minitron-pard-qwen3-14b]

## Strengths & Limitations

- Distillation adds training overhead: an additional forward pass on the teacher model.[^muralidharanCompactLanguageModels2024]
- For draft models, improvements in SD and in downstream task performance are only weakly correlated: a high-quality distilled model is not necessarily an effective draft model.[^zhouDistillSpecImprovingSpeculative2024]
- No single divergence is best. DistillSpec finds that the divergence must be tuned per task and decoding strategy, and that directly optimizing TVD does not give the best performance in most settings explored.[^zhouDistillSpecImprovingSpeculative2024] GKD likewise finds the best divergence task-dependent, with mode-seeking divergences (reverse KL, JSD (0.9)) ahead under temperature sampling and little difference under greedy decoding on XSum.[^agarwalOnPolicyDistillationLanguage2024] AdaSPEC gets much lower draft acceptance with reverse KL or TVD than with forward KL (see Contradictions).[^huAdaSPECSelectiveKnowledge2025]
- Training on a fixed dataset leaves a train-inference mismatch for autoregressive students; on-policy data addresses it at roughly $1.8\times$ to $2.2\times$ the training compute on GSM8K.[^agarwalOnPolicyDistillationLanguage2024]
- LK Losses states that the gap between proxy objectives and direct optimization of acceptance becomes stark when model capacity is limited.[^samarinLKLossesDirect2026]

# Contradictions

**Is distillation cost-effective for retraining a pruned LLM?**

- Sheared LLaMA states that, for pre-training LLMs, distilling from a teacher model improves the quality of student models given the same number of training steps, but is less cost-effective than pruning and continued training because of the inference cost of the teacher model.[^xiaShearedLLaMAAccelerating2024]
- Muralidharan et al. compare the two under iso-compute settings, which account for the teacher's forward pass, and find distillation better: 4B-Pruned-Distill at 100B tokens scores 51.04 on Hellaswag and 37.81 on MMLU, against 50.85 and 24.57 for 4B-Pruned with conventional training at 150B tokens. Their best practice is to retrain exclusively with distillation loss using KLD.[^muralidharanCompactLanguageModels2024]

Setting differences: the Sheared LLaMA statement is in its related-work section and rests on cited prior work, not on an experiment in that paper, and it is about distillation as a pre-training approach compared with pruning plus continued pre-training.[^xiaShearedLLaMAAccelerating2024] The Muralidharan et al. result is a measurement where both arms start from the same pruned Nemotron-4 15B model and differ only in the retraining objective.[^muralidharanCompactLanguageModels2024]

**Which divergence works for distilling a draft model?**

- AdaSPEC's ablation on Pythia-31M → 1.4B reaches a reference acceptance rate of 59.77% on GSM8K with forward KL, against 30.22% with reverse KL and 9.32% with TVD, and concludes that RKL and TVD struggle to align draft and target in SD.[^huAdaSPECSelectiveKnowledge2025]
- DistillSpec reports f-Distill (TVD) as the best method in most rows of its speedup table and reverse KL with target-generated data as the best recipe for GSM8K at $T=1$.[^zhouDistillSpecImprovingSpeculative2024] GKD finds reverse KL best for task-agnostic instruction tuning.[^agarwalOnPolicyDistillationLanguage2024]

Setting differences: AdaSPEC trains for 3 epochs with its token filter on; DistillSpec trains T5 drafts for 300,000 steps from supervised fine-tuned checkpoints; GKD measures student task quality, not acceptance. See [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md).

## Related

- [GKD](../methods/gkd.md), [AdaSPEC](../methods/adaspec.md)
- [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md)
- [Target-aware recovery of compressed drafters](../analyses/target-aware-recovery-of-compressed-drafters.md)
- [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- [DistillSpec](../methods/distillspec.md)
- [Structured pruning](../methods/structured-pruning.md), [Sheared-LLaMA](../methods/sheared-llama.md)
- [Speculative decoding](../methods/speculative-decoding.md), [Medusa](../methods/medusa.md), [EAGLE](../methods/eagle.md)
- [What the target must supply to train a drafter](../analyses/target-signals-for-drafter-training.md)

[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
