---
type: Paper
title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
description: AdaSPEC distills a draft model only on the tokens where a DistillSpec-trained reference drafter shows the draft can still catch up, and raises acceptance rate over DistillSpec on every task and model pair tested (by up to 15 points).
tags: [speculative-decoding, knowledge-distillation, draft-model, token-selection, acceptance-rate, speculative-drafter]
collections: [speculative drafter]
authors: [Yuezhou Hu, Jiaxin Guo, Xinyu Feng, Tuo Zhao]
doi: 10.48550/arXiv.2510.19779
arxiv: "2510.19779"
arxiv_version: 2510.19779v1
sources:
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: agarwalOnPolicyDistillationLanguage2024
    resource: zotero://select/items/@agarwalOnPolicyDistillationLanguage2024
    title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
---

# AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders

Text source: arXiv HTML, version `2510.19779v1`.

## Summary

The speedup of [speculative decoding](../methods/speculative-decoding.md) (SD) depends on how well the draft model aligns with the target, and this alignment is usually improved with [knowledge distillation](../methods/knowledge-distillation.md) (KD).[^huAdaSPECSelectiveKnowledge2025] The paper argues that minimizing KL divergence over all tokens is misaligned with SD's goal of maximizing acceptance rate: a small draft cannot absorb the whole target distribution, and spending its capacity on hard tokens that are unlikely to be accepted anyway is wasteful.[^huAdaSPECSelectiveKnowledge2025]

[AdaSPEC](../methods/adaspec.md) adds token filtering to KD. A reference model, a copy of the draft distilled from the target with [DistillSpec](../methods/distillspec.md), is used to score each token; the draft is then distilled only on the selected tokens.[^huAdaSPECSelectiveKnowledge2025] With Pythia-31M → Pythia-1.4B and CodeGen-350M → Phi-2 on GSM8K, Alpaca, MBPP, CNN/Daily Mail, and XSUM, AdaSPEC has a higher acceptance rate than DistillSpec in every task and setting, by up to 15%.[^huAdaSPECSelectiveKnowledge2025]

## Contributions

- AdaSPEC, a two-phase KD method for SD drafts: reference model distillation with token filtering, then selective draft distillation on the filtered tokens.[^huAdaSPECSelectiveKnowledge2025]
- A comparison against DistillSpec over five tasks, two model pairs, and two training budgets (3-Epoch and Optimal-Epoch).[^huAdaSPECSelectiveKnowledge2025]
- Ablations of the selection rule, training method, divergence, and selection ratio, plus wall-clock tests in vLLM and an integration with EAGLE.[^huAdaSPECSelectiveKnowledge2025]

## Method

### Preliminaries

- Greedy SD: the draft $M_q$ proposes $\gamma$ tokens by argmax; the target $M_p$ checks them in parallel and accepts them until the first mismatch (Algorithm 1).[^huAdaSPECSelectiveKnowledge2025]
- Acceptance rate $\alpha=\mathrm{accept}/(\mathrm{accept}+\mathrm{reject})$, counting tokens accepted and rejected by $M_p$.[^huAdaSPECSelectiveKnowledge2025]
- Block efficiency $\tau(x)=(1-\alpha^{\gamma+1})/(1-\alpha)$ and wall-time speed-up $\tau(x)/(\gamma c+1)$, with $c$ the ratio of one draft execution's time to one target execution's time.[^huAdaSPECSelectiveKnowledge2025]

### Algorithm (Algorithm 2)

1. **Fine-tune the target** $M_p$ on the task dataset $\mathcal{D}$ to get $M_p^{*}$.[^huAdaSPECSelectiveKnowledge2025]
2. **Reference model.** Initialize $M_{\mathrm{ref}}$ as a copy of the draft and distill it from $M_p^{*}$ on $\mathcal{D}$ with the DistillSpec framework, minimizing forward KL $\mathcal{K}(P\|R)$ (Eq. 6).[^huAdaSPECSelectiveKnowledge2025]
3. **Selective distillation of the draft.** For each token $w$, compute $\mathcal{L}_{\mathrm{ref}}(w)=\mathcal{K}(P(w|\cdot)\|R(w|\cdot))$ and $\mathcal{L}_{\mathrm{draft}}(w)=\mathcal{K}(P(w|\cdot)\|Q(w|\cdot))$, and their difference $\Delta_{\mathcal{L}}(w)=\mathcal{L}_{\mathrm{draft}}(w)-\mathcal{L}_{\mathrm{ref}}(w)$. Keep the set $\mathbb{S}$ of tokens whose $\Delta_{\mathcal{L}}$ is in the top $k\times100\%$, and train the draft on
   $\mathcal{L}_{\mathrm{distill}}=\frac{1}{k\cdot|y|}\sum_{i}\mathbb{I}[y_i\in\mathbb{S}]\cdot\mathcal{L}_{\mathrm{draft}}(y_i)$.[^huAdaSPECSelectiveKnowledge2025]

- A large $\Delta_{\mathcal{L}}$ means the draft is still far from the target on that token while the same-size reference is close, so the paper reads such tokens as "not yet well aligned" but "highly learnable".[^huAdaSPECSelectiveKnowledge2025] The introduction describes the same step as excluding "hard" tokens that the reference identifies as difficult for small models.[^huAdaSPECSelectiveKnowledge2025]
- In the PyTorch listing, the threshold is the per-batch $(1-k)$ quantile of $\Delta$ over tokens, and the KL terms are computed from target, reference, and draft logits on the same sequences.[^huAdaSPECSelectiveKnowledge2025] The core fits in about 100 lines of code.[^huAdaSPECSelectiveKnowledge2025]
- The learning rate is adjusted with the linear scaling rule when token selection is applied.[^huAdaSPECSelectiveKnowledge2025]
- On GSM8K the selected tokens are mostly mathematical, such as digits and operators.[^huAdaSPECSelectiveKnowledge2025]

## Experiments & Results

### Setup

- Model pairs: Pythia-31M draft with Pythia-1.4B target (same family and tokenizer), and CodeGen-350M draft with Phi-2 target (different families with an aligned tokenizer).[^huAdaSPECSelectiveKnowledge2025]
- Tasks: [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [MBPP](../datasets/mbpp.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md), [XSUM](../datasets/xsum.md).[^huAdaSPECSelectiveKnowledge2025]
- Draft and reference start from the same pretrained model; the target is first fine-tuned on each task.[^huAdaSPECSelectiveKnowledge2025]
- **3-Epoch setting:** reference and draft trained for exactly 3 epochs. **Optimal-Epoch setting:** epochs chosen from 1, 3, 6, 10, 15, 20, 30 (1, 3, 6, 10 for XSUM and CNN/Daily Mail) by validation accuracy (GSM8K target) or validation perplexity, and the reference with the highest validation $\alpha$ is used.[^huAdaSPECSelectiveKnowledge2025]
- Filter fraction $k=0.4$ everywhere; batch size 16 (8 for MBPP); learning rates from 1e-5 to 3e-4 depending on task and pair (Table 9).[^huAdaSPECSelectiveKnowledge2025]
- The paper states it uses a shorter training schedule than the DistillSpec paper because of compute constraints, capping Optimal-Epoch at 30 epochs.[^huAdaSPECSelectiveKnowledge2025]

Epochs chosen in the Optimal-Epoch setting (Table 9; the 3-Epoch setting uses 3 for target, reference, and draft):[^huAdaSPECSelectiveKnowledge2025]

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

### Main results (Table 1, acceptance rate $\alpha$)

| Task | 3-Epoch Pythia DistillSpec | 3-Epoch Pythia AdaSPEC | 3-Epoch CodeGen→Phi-2 DistillSpec | 3-Epoch CodeGen→Phi-2 AdaSPEC | Optimal Pythia DistillSpec | Optimal Pythia AdaSPEC | Optimal CodeGen→Phi-2 DistillSpec | Optimal CodeGen→Phi-2 AdaSPEC |
|---|---|---|---|---|---|---|---|---|
| GSM8K | 57.58% | 62.63% | 79.49% | 82.79% | 66.19% | 68.28% | 81.49% | 83.48% |
| Alpaca | 44.34% | 47.25% | 56.48% | 58.80% | 65.41% | 65.79% | 58.05% | 60.36% |
| MBPP | 46.88% | 47.73% | 87.36% | 88.76% | 49.88% | 65.12% | 86.60% | 87.70% |
| CNN/Daily Mail | 73.05% | 74.22% | 79.33% | 80.63% | 80.15% | 80.89% | 85.01% | 86.29% |
| XSUM | 47.24% | 49.11% | 58.88% | 59.93% | 56.11% | 57.80% | 66.78% | 68.19% |

All rows: [^huAdaSPECSelectiveKnowledge2025]

- The gain over DistillSpec is larger for the pair with the larger size gap (Pythia-31M → 1.4B) than for CodeGen-350M → Phi-2, in both settings.[^huAdaSPECSelectiveKnowledge2025]
- On Pythia-31M/1.4B for GSM8K (3-Epoch) and CNN/Daily Mail (Optimal-Epoch), AdaSPEC shifts the per-task acceptance-rate histogram right, has more and larger positive top-2 logit margins and fewer and smaller negative ones, and has lower token-level KL to the target (shown in figures only).[^huAdaSPECSelectiveKnowledge2025]
- In case studies AdaSPEC's prediction errors form nearly a subset of DistillSpec's errors.[^huAdaSPECSelectiveKnowledge2025]

### Ablations (Pythia-31M/1.4B, 3 epochs; Tables 2-4)

| Variant | GSM8K reference $\alpha$ | GSM8K draft $\alpha$ | MBPP reference $\alpha$ | MBPP draft $\alpha$ |
|---|---|---|---|---|
| Top 40% tokens (AdaSPEC) | 59.77% | 63.22% | 42.22% | 48.22% |
| Bottom 40% tokens | 59.77% | 49.03% | 42.22% | 39.75% |
| Fine-tuning instead of distillation | 59.64% | 63.13% | 41.42% | 45.61% |
| TVD as divergence | 9.32% | 9.09% | 3.86% | 6.76% |
| RKL as divergence | 30.22% | 30.05% | 13.17% | 15.61% |

All rows: [^huAdaSPECSelectiveKnowledge2025]

- Training on the bottom 40% does worse than the reference model itself.[^huAdaSPECSelectiveKnowledge2025]
- With RKL and TVD the acceptance rate degrades, which the paper attributes to the limits of RKL and TVD as distillation objectives for aligning draft and target in SD. It notes that DistillSpec used TVD with batch size 32 and 300,000 training steps, and says this long schedule is costly and leads to overfitting. AdaSPEC therefore uses forward KL.[^huAdaSPECSelectiveKnowledge2025]
- **Selection ratio $k$:** lower values (0.2-0.4) generally give a higher acceptance rate on GSM8K (Figure 4, values in the figure only); $k=0.4$ is chosen to balance training efficiency and performance.[^huAdaSPECSelectiveKnowledge2025]

### Wall-clock speed in vLLM (Table 5)

Pythia-31M → 1.4B, 3 epochs, greedy decoding, [vLLM](../methods/vllm.md) on one A100:

| Task | DistillSpec s/sentence | AdaSPEC s/sentence | DistillSpec tokens/s | AdaSPEC tokens/s |
|---|---|---|---|---|
| MBPP | 0.69 | 0.57 | 149.15 | 181.67 |
| GSM8K | 0.51 | 0.48 | 227.86 | 241.34 |
| CNN/DailyMail | 0.76 | 0.67 | 248.49 | 283.50 |

All rows: [^huAdaSPECSelectiveKnowledge2025]

The paper summarizes this as a 10-20% speed-up over DistillSpec.[^huAdaSPECSelectiveKnowledge2025]

### Further experiments

- **With [EAGLE](../methods/eagle.md)** (Table 6): Vicuna-7B-v1.3, 3-epoch training on [ShareGPT](../datasets/sharegpt.md) with the EAGLE recipe, evaluated on [MT-Bench](../datasets/mt-bench.md). Training first-token accuracy 75.3% → 76.3%, 8.85 → 8.06 s/sentence (-8.9%), 63.48 → 68.21 tokens/s (+7.45%).[^huAdaSPECSelectiveKnowledge2025]
- **Larger models** (Table 7): Qwen2.5-0.5B draft with Qwen2.5-32B target, GSM8K, 3 epochs: DistillSpec 84.43%, AdaSPEC 86.21%.[^huAdaSPECSelectiveKnowledge2025]
- **Mixed data** (Table 8): target, reference, and draft trained 3 epochs on MBPP then 3 on GSM8K: DistillSpec 69.63% / 72.75%, AdaSPEC 70.69% / 78.41% (MBPP / GSM8K).[^huAdaSPECSelectiveKnowledge2025]
- **Compute** (Table 10, A100 GPU hours): 3-Epoch 1 (Pythia) and 3 (CodeGen) for GSM8K, Alpaca, MBPP, and 60 and 200 for CNN/Daily Mail and XSUM; Optimal-Epoch up to 700.[^huAdaSPECSelectiveKnowledge2025]
- The discussion states that AdaSPEC bridges draft-target size gaps of up to 64 times in the experiments.[^huAdaSPECSelectiveKnowledge2025]

## Limitations

- The paper calls itself a preliminary study limited to a simple loss-based token filter, and lists more adaptive filters and integration with tree-based or multi-step verification as future work.[^huAdaSPECSelectiveKnowledge2025]
- The headline metric is acceptance rate under greedy verification; wall-clock results are given only for three tasks with Pythia-31M → 1.4B, and none against autoregressive decoding.[^huAdaSPECSelectiveKnowledge2025]
- Training is per task: the target is fine-tuned on the task and the reference and draft are distilled on the same task data.[^huAdaSPECSelectiveKnowledge2025]
- DistillSpec is run with a shorter schedule than in its own paper, and only with forward KL, while the DistillSpec paper tunes the divergence per task.[^huAdaSPECSelectiveKnowledge2025]
- The method needs an extra reference model trained to convergence before the draft, and logits from target, reference, and draft at every training step.[^huAdaSPECSelectiveKnowledge2025]
- The EAGLE results are cited as Table 7 in the text but appear in Table 6.[^huAdaSPECSelectiveKnowledge2025]

# Contradictions

**Is reverse KL or TVD a viable objective for distilling a drafter?** AdaSPEC's ablation gets acceptance rates of 9.32% (TVD) and 30.22% (RKL) for the reference model on GSM8K, against 59.77% with forward KL, and concludes that RKL and TVD struggle to align draft and target in SD.[^huAdaSPECSelectiveKnowledge2025] The DistillSpec paper reports f-Distill (TVD) as the best method in most rows of its Table C.1 and RKL with target data as best for GSM8K under temperature sampling,[^zhouDistillSpecImprovingSpeculative2024] and the GKD paper finds reverse KL best for task-agnostic instruction tuning.[^agarwalOnPolicyDistillationLanguage2024] Setting differences: AdaSPEC trains for 3 epochs with task-specific targets and greedy acceptance; DistillSpec trains for 300,000 steps with T5 models. See [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md).

## Related

- Methods proposed: [AdaSPEC](../methods/adaspec.md)
- Methods built on or compared: [DistillSpec](../methods/distillspec.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Speculative decoding](../methods/speculative-decoding.md), [EAGLE](../methods/eagle.md), [vLLM](../methods/vllm.md)
- Datasets: [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [MBPP](../datasets/mbpp.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md), [XSum](../datasets/xsum.md), [ShareGPT](../datasets/sharegpt.md), [MT-Bench](../datasets/mt-bench.md)

## Open questions and results

- [Training budgets for pruning recovery and drafter distillation](../analyses/recovery-and-distillation-training-budgets.md)
- [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md)

[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
