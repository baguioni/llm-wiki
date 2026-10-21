---
type: Method
title: Generalized Knowledge Distillation (GKD)
description: Knowledge distillation for autoregressive models that trains the student on a mix of fixed and self-generated (on-policy) sequences with teacher token probabilities as labels and a free choice of divergence; the on-policy variant is one of the recipes DistillSpec uses for draft models.
tags: [knowledge-distillation, on-policy-distillation, gkd, draft-model, imitation-learning]
sources:
  - id: agarwalOnPolicyDistillationLanguage2024
    resource: zotero://select/items/@agarwalOnPolicyDistillationLanguage2024
    title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
---

# Generalized Knowledge Distillation (GKD)

## Overview

GKD addresses the train-inference distribution mismatch of [knowledge distillation](knowledge-distillation.md) for autoregressive models: with a fixed set of output sequences, the partial sequences the student sees in training can differ from those it produces at inference.[^agarwalOnPolicyDistillationLanguage2024] Drawing on on-policy imitation learning, GKD trains the student on sequences it samples itself and uses the teacher's token-level probabilities on those sequences as labels. It also lets the divergence between teacher and student be chosen freely.[^agarwalOnPolicyDistillationLanguage2024]

## How it works

- **Objective.** $L_{\mathrm{GKD}}(\theta)=(1-\lambda)\mathbb{E}_{(x,y)\sim(X,Y)}[\mathcal{D}(p_{\text{T}}\|p_{\text{S}}^{\theta})(y|x)]+\lambda\mathbb{E}_{x\sim X}[\mathbb{E}_{y\sim p_{\text{S}}(\cdot|x)}[\mathcal{D}(p_{\text{T}}\|p_{\text{S}}^{\theta})(y|x)]]$, where $\mathcal{D}$ is a token-level divergence averaged over the output positions and $\lambda\in[0,1]$ is the fraction of student-generated sequences.[^agarwalOnPolicyDistillationLanguage2024]
- **No gradient through sampling.** The student's sampling distribution is not differentiated, which the paper says keeps training stable and efficient. Training samples are drawn at temperature 1.[^agarwalOnPolicyDistillationLanguage2024]
- **Divergences.** Forward KL, reverse KL, and generalized JSD($\beta$), which interpolates between them and is bounded. Forward KL makes a low-capacity student cover the teacher's whole support; reverse KL is mode-seeking and gives higher quality but less diversity.[^agarwalOnPolicyDistillationLanguage2024]
- **Starting point.** The student must already generate adequate sequences, so GKD starts from a supervised fine-tuned student, like SFT before online RL in RLHF.[^agarwalOnPolicyDistillationLanguage2024]
- **With RL.** On-policy GKD only needs student samples, so it can be added to RL fine-tuning as a regularizer toward the teacher, weighted by $\alpha$ against the reward.[^agarwalOnPolicyDistillationLanguage2024]

## Variants

| Variant | Divergence | $\lambda$ | Source |
|---|---|---|---|
| Supervised KD | forward KL | 0 | GKD paper[^agarwalOnPolicyDistillationLanguage2024] |
| On-policy KD | forward KL | 1 | GKD paper[^agarwalOnPolicyDistillationLanguage2024] |
| ImitKD | forward KL | 0.5 ("mixed") | GKD paper[^agarwalOnPolicyDistillationLanguage2024] |
| f-distill | total variation distance | 0.5 ("mixed") | GKD paper[^agarwalOnPolicyDistillationLanguage2024] |
| On-policy GKD (as listed in DistillSpec) | FKL / JSD | on-policy data from the student | DistillSpec[^zhouDistillSpecImprovingSpeculative2024] |

SeqKD, supervised fine-tuning on teacher-generated outputs, is the other common baseline; it uses no teacher probabilities.[^agarwalOnPolicyDistillationLanguage2024]

## Papers using it

- [Agarwal et al. 2024](../papers/agarwalOnPolicyDistillationLanguage2024.md) propose GKD and test it with a supervised fine-tuned T5-XL teacher and T5-small, base, and large students.[^agarwalOnPolicyDistillationLanguage2024]
  - Averaged over student sizes, on-policy GKD's gain over the initial student is 2.1× (summarization), 1.7× (translation), and 1.9× (arithmetic reasoning) the gain of baseline KD methods.[^agarwalOnPolicyDistillationLanguage2024]
  - On [XSum](../datasets/xsum.md), on-policy GKD on 5% of the training inputs, without ground-truth summaries, beats supervised KD and ImitKD on the full dataset.[^agarwalOnPolicyDistillationLanguage2024]
  - On [GSM8K](../datasets/gsm8k.md), performance rises with the on-policy fraction once at least 25% of the data is on-policy.[^agarwalOnPolicyDistillationLanguage2024]
  - Best divergence by task: JSD (0.1) on WMT, forward KL on XSum (greedy) and GSM8K, reverse KL for FLAN instruction tuning.[^agarwalOnPolicyDistillationLanguage2024]
- [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md) uses GKD as one of the distillation methods for draft models. In its Table C.1, GKD is the best method in 6 of 36 dataset/temperature/$\gamma$ rows (for example CNNDM, $T=0$, $\gamma=5$: 2.07× → 2.42×), and f-Distill in the rest.[^zhouDistillSpecImprovingSpeculative2024] f-Distill and GKD perform comparably and GKD gives the best wall-time improvement in DistillSpec's method comparison.[^zhouDistillSpecImprovingSpeculative2024]
- The GKD paper states that DistillSpec and online speculative decoding (Liu et al. 2023) apply GKD to align draft and target models.[^agarwalOnPolicyDistillationLanguage2024]
- [AdaSPEC](../papers/huAdaSPECSelectiveKnowledge2025.md) does not use on-policy data: its reference and draft models are distilled with forward KL in the DistillSpec framework on the task dataset.[^huAdaSPECSelectiveKnowledge2025]

## Strengths & Limitations

- Sampling from the student is cheaper than sampling from the teacher because of the size difference.[^agarwalOnPolicyDistillationLanguage2024]
- On GSM8K, on-policy sampling costs approximately $1.8\times$ to $2.2\times$ the compute of training on a fixed dataset.[^agarwalOnPolicyDistillationLanguage2024]
- The best divergence is task- and temperature-dependent.[^agarwalOnPolicyDistillationLanguage2024]
- It needs white-box access to the teacher's token probabilities.[^agarwalOnPolicyDistillationLanguage2024]

## Related

- [Knowledge distillation](knowledge-distillation.md), [DistillSpec](distillspec.md), [AdaSPEC](adaspec.md)
- [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md)

[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
