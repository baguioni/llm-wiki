---
type: Result
title: A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT
description: Minitron-pruning Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery on 57M tokens, and PARD-1 training give offline MAT 1.96 at K=8 on Spec-Bench, against 2.66 for Qwen3-0.6B with the same data and recipe and 3.07 for the released amd/PARD-Qwen3-0.6B; the gap follows the backbone's first-token accuracy (0.570 against 0.751).
tags: [speculative-decoding, parallel-drafting, draft-model, structured-pruning, knowledge-distillation, pard, mobile-specedge]
sources:
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT

## Claim

A PARD-1 drafter built from Qwen3-14B itself by one-shot Minitron pruning and chat-KD recovery reaches MAT 1.96 at K=8 on Spec-Bench: 74% of a PARD-1 drafter trained the same way on Qwen3-0.6B (2.66), and 64% of the released `amd/PARD-Qwen3-0.6B` (3.07).[^minitron-pard-qwen3-14b]

## Conditions

- Pruned backbone: Qwen3-14B cut in one step to 28 layers, hidden 1024, 16 query / 8 KV heads, FFN 3,072, untied embeddings (751,632,384 parameters, 5.1% of the target), no retraining inside the prune.[^minitron-pard-qwen3-14b]
- Recovery: online forward-KL distillation from Qwen3-14B bf16 on 49,372 of its own greedy non-thinking answers to Magpie and Evol-CodeAlpaca prompts, 3 epochs, 57M target tokens, one H100.[^minitron-pard-qwen3-14b]
- PARD-1: K=8, COD, 1 epoch of 779 steps of 64 sequences on all 49,872 answers, hard labels only. The control uses the same data and recipe on `Qwen/Qwen3-0.6B`.[^minitron-pard-qwen3-14b]
- Evaluation: offline greedy MAT on all 480 Spec-Bench questions against stored Qwen3-14B greedy references, temperature 0. No live run.[^minitron-pard-qwen3-14b]
- Source: [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md).

## Numbers

| Drafter | Backbone AR top-1 | PARD MAT K=8 | Macro MAT K=8 | First-offset top-1 | Top-1 at offset 7 |
|---|---|---|---|---|---|
| Pruned Qwen3-14B + chat-KD + PARD-1 | 0.572 | 1.96 | 1.92 | 0.570 | 0.096 |
| Qwen3-0.6B + PARD-1 (control) | 0.747 | 2.66 | 2.73 | 0.751 | 0.159 |
| amd/PARD-Qwen3-0.6B (released) | 0.747 | 3.07 | 3.14 | 0.752 | 0.264 |

All rows: [^minitron-pard-qwen3-14b]

- Without recovery the pruned model is useless as a draft: top-1 0.038, MAT 1.04 at γ=3, 5, and 7. After chat-KD it reaches MAT 2.17 at γ=5, against 3.12 for Qwen3-0.6B.[^minitron-pard-qwen3-14b]
- Its weakest task is translation: 1.35 PARD MAT against 2.37 for the control.[^minitron-pard-qwen3-14b]

## Comparisons

- **Where the gap comes from.** The report attributes the gap to the control to the first offset (0.570 against 0.751), which the PARD stage inherits from the backbone (0.572). By its own computation the later offsets also decay faster: the pruned-to-control ratio falls from 0.76 at offset 0 to about 0.60 at offsets 4–7.[^minitron-pard-qwen3-14b]
- **Control against released.** The control (2.66) is below the released drafter (3.07) on the same evaluator. The report states that AMD trained the released drafter on about 1M prompts for 4 epochs, against 49,872 answers for 1 epoch here.[^minitron-pard-qwen3-14b]
- **Recovery had saturated.** On 500 held-out answers the recovery curve gained +0.001 top-1 per 250 steps in epoch 3, so more epochs over the same answers are not expected to close the gap. The report names more answers or a longer answer cap as the next levers.[^minitron-pard-qwen3-14b]

## Related

- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md)
- [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- [PARD](../methods/pard.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md)

[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
