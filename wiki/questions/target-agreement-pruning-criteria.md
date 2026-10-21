---
type: Open Question
title: Does choosing what to prune by target agreement beat LM-loss importance?
description: Pruned drafters in the wiki choose what to remove by LM-loss or perplexity change, a Fisher trace on WikiText2, an unstated Bayesian-optimization objective, or layer position, and none scores candidate removals by acceptance or TV distance to the target; Minitron's candidate rankings shift during retraining, so it is also open whether any prune-time score predicts acceptance after recovery.
tags: [speculative-decoding, draft-model, structured-pruning, speculative-drafter, mobile-specedge]
sources:
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Does choosing what to prune by target agreement beat LM-loss importance?

## Question

When a drafter is made by pruning, does it reach a higher acceptance rate if the layers, heads, and channels to remove are chosen by how much each removal hurts agreement with the target (for example the TV distance or top-1 agreement on the target's own outputs), instead of by how much it hurts language-modeling loss? And does a score taken at pruning time still predict acceptance after recovery training?

## Why it matters

Yan et al. find that a draft model's capability in language modeling does not correlate strongly with its performance in speculative decoding.[^yanDecodingSpeculativeDecoding2025] The importance scores used to prune drafters are language-modeling scores, so they may keep parts that matter for general text and drop parts that matter for agreeing with the target. For a single draft token, acceptance rate relates directly to TV distance through $\alpha=1-\operatorname{TV}(p,q)$,[^samarinLKLossesDirect2026] so an agreement score is cheap to define.

## Evidence so far

How the pruned drafters in the wiki choose what to remove:

| Work | What is removed | Selection criterion | Data for the score |
|---|---|---|---|
| Minitron | layers, heads, neurons, embedding channels | depth: perplexity change from removing one layer, or Block Importance (cosine distance between a layer's input and output); width: activation magnitudes | 1024 calibration samples from the training data[^muralidharanCompactLanguageModels2024] |
| Sheared-LLaMA | layers, heads, hidden and intermediate dimensions | learned masks under the masked language modeling loss, constrained to a target shape | RedPajama, 0.4B tokens[^xiaShearedLLaMAAccelerating2024] |
| SDFP | layers of the target | Fisher Information Trace, from squared gradient norms of the per-sample loss | WikiText2[^weiSDFPSpeculativeDecoding2026] |
| SWIFT, SELF-SD | layers skipped at inference | Bayesian optimization (objective not stated in the wiki's sources) | not stated[^weiSDFPSpeculativeDecoding2026] |
| Yan et al. | depth traded for width | shape chosen for speculative decoding throughput; parts chosen by the Sheared-LLaMA scheme | RedPajama, 0.4B tokens[^yanDecodingSpeculativeDecoding2025] |
| Osprey | all but the first $N$ blocks of a small LM | position, $N\in\{1,2,3,4\}$, kept small for drafter latency | none[^bieOspreyTargetagnosticPretraining2026] |
| HAT | the target's middle layers | position (first $m$ layers and the head stay on the device) | none[^xieNovelHatShapedDeviceCloud2025] |
| My Qwen3-14B run | layers, heads, FFN neurons, hidden channels | depth: LM-loss increase when a layer is replaced by the identity; width: activation magnitudes | SlimPajama-6B, 32 sequences for depth and 256 for width[^minitron-pard-qwen3-14b] |

- **SDFP is the closest to an agreement criterion.** It starts from the KL divergence between the original and perturbed output distributions, $D_{\mathrm{KL}}(p_{\theta}\|p_{\theta+\delta\theta})\approx\frac{1}{2}\delta\theta^{\top}I(\theta)\delta\theta$, and claims that FIT models how pruning perturbations affect the acceptance behavior of speculative decoding.[^weiSDFPSpeculativeDecoding2026] Since SDFP's draft is the pruned target, the unperturbed model is the target. The practical score, though, is the empirical Fisher trace of the loss on WikiText2, and the paper does not compare FIT with any other layer-selection criterion.[^weiSDFPSpeculativeDecoding2026]
- **Yan et al. optimize for speculative utility, but at the level of shape.** They choose depth and width by throughput, because draft latency is bottlenecked by depth, and they find that below 5 layers the draft's alignment capability drops dramatically.[^yanDecodingSpeculativeDecoding2025] Which heads and neurons survive is still decided by the Sheared-LLaMA scheme.[^yanDecodingSpeculativeDecoding2025]
- **Prune-time scores can mislead.** In Minitron, the depth+width variant has a lower loss right after pruning, and the ranking flips around 200 steps of retraining (0.8B tokens). The relative rankings of searched 8B candidates change significantly up to $\sim$300 steps of retraining and then stabilize.[^muralidharanCompactLanguageModels2024]
- **My run shows the problem at an extreme cut.** Pruned zero-shot to 5.1% of Qwen3-14B's parameters, the draft has top-1 0.038 and MAT 1.04 on Spec-Bench. After forward-KL recovery on 57M tokens of the target's answers, it has top-1 0.572 and MAT 2.17 at γ=5.[^minitron-pard-qwen3-14b] At zero shot almost nothing agrees with the target, so a prune-time agreement score would have to rank candidates near the floor.

## Conflicting claims

None. No paper in the wiki compares selection criteria by acceptance.

## What would resolve it

My Qwen3-14B run already fixes the shape (the Qwen3-0.6B shape: 28 of 40 layers, hidden 1024 of 5120, 2 of 5 query heads in each of the 8 KV groups, FFN 3,072 of 17,408),[^minitron-pard-qwen3-14b] so only the choice of what to keep inside that shape varies. The depth choice is a near-tie under LM loss: the 12 dropped layers cost 0.022–0.033 nats each,[^minitron-pard-qwen3-14b] so a different score could easily pick a different set. Eight of the 12 dropped layers form the middle block 15–23 (dropped: 2, 4, 10, 15, 16, 18, 19, 20, 21, 22, 23, 26), and each was scored by removing it alone from the full model,[^minitron-pard-qwen3-14b] so the scores do not capture what removing neighbouring layers together costs. Minitron computes importance for all axes on the unpruned model and describes its strategy as targeting width and depth simultaneously, with no depth-first or width-first order.[^muralidharanCompactLanguageModels2024]

1. On that target and shape, compute depth importance two ways on the same calibration set of the target's own answers: (a) LM-loss increase, as in my run, and (b) the increase in TV distance (or the drop in top-1 agreement) between the target and the model with one layer removed. Compare the two rankings.
2. If the rankings differ, prune with each, recover each with the same recipe and token budget, and measure acceptance length on Spec-Bench.
3. Measure acceptance after a short recovery (a few hundred steps, as in Minitron's lightweight retraining) as well as at the end, to see whether the ranking from a short run predicts the ranking at the end.
4. Optionally, replace Sheared-LLaMA's mask objective (masked LM loss) with an acceptance-oriented loss, so that the masks are learned against the target.

## Related

- [Does recovering a pruned drafter against the target beat recovering it against its parent?](target-aware-recovery-of-pruned-drafters.md)
- [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)
- [Papers that train drafters for target agreement](../analyses/drafter-training-for-target-agreement.md)
- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- Methods: [Structured pruning](../methods/structured-pruning.md), [Sheared-LLaMA](../methods/sheared-llama.md), [SDFP](../methods/sdfp.md), [Self-speculative decoding](../methods/self-speculative-decoding.md)

[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
