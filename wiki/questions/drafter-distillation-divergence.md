---
type: Open Question
title: Which divergence should a draft model be distilled with?
description: GKD and DistillSpec find the best divergence task-dependent and get good drafts from TVD and reverse KL, while AdaSPEC gets acceptance rates of 9-30% with TVD and reverse KL against 60% with forward KL, and LK Losses explains why pure TVD fails from random initialization.
tags: [speculative-decoding, knowledge-distillation, draft-model, training-objective]
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
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
---

# Which divergence should a draft model be distilled with?

## Question

When a draft model is distilled from its target, which token-level objective (forward KL, reverse KL, JSD, total variation distance) gives the highest acceptance, and does the answer depend on the task, the decoding temperature, the training budget, or how the draft is initialized?

## Why it matters

Acceptance rate equals one minus the total variation distance between target and draft,[^samarinLKLossesDirect2026] so the objective is the most direct lever on acceptance that adds no inference cost. The papers in the wiki give opposite recommendations for the same divergences.

## Evidence so far

| Paper | Setting | Finding |
|---|---|---|
| [GKD](../papers/agarwalOnPolicyDistillationLanguage2024.md) | T5-XL teacher, T5 students, task quality (not acceptance) | Best divergence is task-dependent: JSD (0.1) on WMT, forward KL on GSM8K and on XSum with greedy evaluation, reverse KL and JSD (0.9) on XSum with temperature sampling, reverse KL for FLAN instruction tuning.[^agarwalOnPolicyDistillationLanguage2024] |
| [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md) | T5-XL target, T5-Small draft initialized from a supervised fine-tuned model, 300,000 steps | f-Distill (TVD) is the best method in 30 of 36 rows of Table C.1 and GKD in 6; best recipe for block efficiency is JSD on XSum (greedy), forward KL with draft data on GSM8K (greedy), and reverse KL with target data on GSM8K ($T=1$). Directly optimizing TVD does not give the best performance in most settings explored, so the divergence is treated as a hyperparameter.[^zhouDistillSpecImprovingSpeculative2024] |
| [AdaSPEC](../papers/huAdaSPECSelectiveKnowledge2025.md) | Pythia-31M draft, Pythia-1.4B target, 3 epochs, greedy acceptance, token selection $k=0.4$ | Reference / draft acceptance on GSM8K: forward KL 59.77% / 63.22%, reverse KL 30.22% / 30.05%, TVD 9.32% / 9.09%. On MBPP: 42.22% / 48.22%, 13.17% / 15.61%, 3.86% / 6.76%. Concludes that RKL and TVD struggle to align draft and target in SD and uses forward KL.[^huAdaSPECSelectiveKnowledge2025] |
| [LK Losses](../papers/samarinLKLossesDirect2026.md) | Randomly initialized draft heads (EAGLE-3, MTP) | Forward KL is mode-covering and reverse KL mode-seeking, while TV maximizes overlap in a toy example. But the TV gradient has norm $\mathcal{O}(\sqrt{k}/V)$ for a randomly initialized draft, which with vocabularies over 100k makes pure TV optimization impractical from random initialization.[^samarinLKLossesDirect2026] It notes that DistillSpec's drafts start from pretrained LMs and states this distinction is critical.[^samarinLKLossesDirect2026] |

## Conflicting claims

- AdaSPEC: "RKL and TVD ... struggle to effectively align the draft and target models in the context of SD".[^huAdaSPECSelectiveKnowledge2025] DistillSpec: TVD-based f-Distill gives the best speedup in most of its Table C.1, and reverse KL is the best divergence for GSM8K at $T=1$.[^zhouDistillSpecImprovingSpeculative2024]
- AdaSPEC attributes DistillSpec's results to its long schedule (batch size 32, 300,000 steps), which it calls costly and prone to overfitting.[^huAdaSPECSelectiveKnowledge2025]

Setting differences that could explain the conflict:

- **Initialization.** DistillSpec's T5 drafts start from supervised fine-tuned checkpoints;[^zhouDistillSpecImprovingSpeculative2024] AdaSPEC's Pythia-31M draft is a pretrained model and the target is fine-tuned on the task first;[^huAdaSPECSelectiveKnowledge2025] LK Losses' argument against TV is specifically about random initialization.[^samarinLKLossesDirect2026] AdaSPEC's drafts are not randomly initialized, so the LK gradient argument does not directly cover them.
- **Budget.** 3 epochs (AdaSPEC) against 300,000 steps (DistillSpec).[^huAdaSPECSelectiveKnowledge2025][^zhouDistillSpecImprovingSpeculative2024]
- **Token selection.** AdaSPEC's divergence ablation keeps its top-40% token filter on, so the RKL and TVD rows also change which tokens are selected.[^huAdaSPECSelectiveKnowledge2025] Its reference model, distilled without selection, also collapses under RKL and TVD.[^huAdaSPECSelectiveKnowledge2025]
- **Data.** DistillSpec and GKD find on-policy (model-generated) data important;[^zhouDistillSpecImprovingSpeculative2024][^agarwalOnPolicyDistillationLanguage2024] AdaSPEC distills on the task dataset.[^huAdaSPECSelectiveKnowledge2025]

## What would resolve it

- One draft and target pair trained with forward KL, reverse KL, JSD, and TVD at matched budgets, from both a pretrained and a random initialization, without token selection, reporting acceptance rate under greedy and $T=1$ verification.
- AdaSPEC's RKL and TVD runs repeated without the token filter and with a longer schedule.
- For the wiki's drafters (DFlash, PARD, EAGLE-3 heads), the same sweep at block positions beyond the first, where most acceptance is lost.

## Related

- [Knowledge distillation](../methods/knowledge-distillation.md), [GKD](../methods/gkd.md), [DistillSpec](../methods/distillspec.md), [AdaSPEC](../methods/adaspec.md)
- [Does an acceptance-oriented loss help a block diffusion drafter?](acceptance-oriented-loss-for-block-drafters.md)
- [What the target must supply to train a drafter](../analyses/target-signals-for-drafter-training.md)
- [Papers that train drafters for target agreement](../analyses/drafter-training-for-target-agreement.md)

[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
[^samarinLKLossesDirect2026]: Samarin et al. 2026
