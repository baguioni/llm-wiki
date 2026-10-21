---
type: Experiment
title: Pruning Qwen3-14B into a PARD-1 drafter
description: My pipeline that one-shot Minitron-prunes Qwen3-14B to the Qwen3-0.6B shape (0.75B with untied embeddings), recovers it by chat-KD on 57M tokens of the target's own answers, and PARD-1-trains it; offline on Spec-Bench it reaches MAT 1.96 at K=8 against 2.66 for a Qwen3-0.6B control with the same data and recipe and 3.07 for the released amd/PARD-Qwen3-0.6B.
tags: [speculative-decoding, parallel-drafting, draft-model, structured-pruning, knowledge-distillation, pard, mobile-specedge, speculative-drafter]
date: 2026-10-19
data_sources:
  - raw/experiments/minitron-pard-qwen3-14b.md
sources:
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# Pruning Qwen3-14B into a PARD-1 drafter

This page records my own experiment. Every number without a paper footnote comes from the report `raw/experiments/minitron-pard-qwen3-14b.md`.[^minitron-pard-qwen3-14b] The prune ran on 2026-10-17 on spark2 (DGX Spark GB10), answer regeneration on 2026-10-17 on spark4 (GB10, vLLM 0.20), chat-KD recovery and PARD-1 on 2026-10-18 on nutella2 (one H100 PCIe 80 GB), and the K=7 re-evaluations on 2026-10-19 on spark2.[^minitron-pard-qwen3-14b]

The report takes the pruned model's numbers from the project README and the 10-19 daily log, because its recovery and PARD run folders on the lab NAS were not readable when the report was written.[^minitron-pard-qwen3-14b] An earlier version of the pipeline (10-17/10-18) recovered the same pruned model on SlimPajama text from a cached top-64 teacher. The report calls it superseded and gives no numbers for it.[^minitron-pard-qwen3-14b]

## Goal

Test the pipeline proposed in [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md): turn the target itself into a [PARD](../methods/pard.md)-1 parallel drafter in three stages.[^minitron-pard-qwen3-14b]

1. One [Minitron](../methods/minitron.md) pruning step takes Qwen3-14B to the shape of Qwen3-0.6B, with no retraining inside the step.
2. The pruned model is recovered by online logit distillation from Qwen3-14B on answers Qwen3-14B wrote itself ("chat-KD").
3. The recovered model is fine-tuned into a PARD-1 drafter with K=8 mask tokens.

Two references are scored with the same benchmark and evaluator: a PARD-1 drafter trained with the identical data and recipe on the off-the-shelf Qwen3-0.6B (the control), and AMD's released `amd/PARD-Qwen3-0.6B`.[^minitron-pard-qwen3-14b]

## Setup

### Models

| | Qwen3-14B (target, teacher) | Pruned / recovered backbone | Qwen3-0.6B (control backbone) |
|---|---|---|---|
| Parameters | 14,768,296,960 | 751,625,216 by the pruning budget; 751,632,384 counted by the evaluator | 596,049,920 |
| Layers | 40 | 28 | 28 |
| Hidden size | 5120 | 1024 | 1024 |
| Query heads / KV heads | 40 / 8 | 16 / 8 | 16 / 8 |
| Head dim | 128 | 128 | 128 |
| FFN (intermediate) | 17,408 | 3,072 (3.0 × hidden) | 3,072 |
| Embeddings | untied | untied | tied |
| Vocab rows | 151,936 | 151,936 | 151,936 |

All rows: [^minitron-pard-qwen3-14b]

The pruned model has the Qwen3-0.6B shape but keeps untied input and output embeddings, so it is 0.75B and not 0.6B. It is 5.1% of the target's parameters.[^minitron-pard-qwen3-14b] Minitron's largest tested cut, Nemotron-4 15B to Minitron 4B, removes 73.3% of the weights.[^muralidharanCompactLanguageModels2024]

### Stage 1: Minitron one-shot pruning

- The repo's own reproduction of Minitron, run as one step with a single candidate (28 layers, hidden 1024, 16 heads, MLP 3.0 × hidden), budget 751,625,216 parameters, `hidden_min_frac` 0.2 so that 5120 → 1024 is allowed in one step. No lightweight retraining and no distillation inside the step.[^minitron-pard-qwen3-14b]
- Minitron's residual-head trick is off. The report states that it is absent from the official implementation and that the literal version made zero-shot LM loss worse in a Llama-3.1 reproduction.[^minitron-pard-qwen3-14b] The Minitron paper describes adding residual information from pruned heads back into the remaining heads.[^muralidharanCompactLanguageModels2024]
- Calibration on SlimPajama-6B tokenized with Qwen3, 4096-token sequences, with a domain mix of cc 0.67 / github 0.045 / book 0.045 / stackexchange 0.02 / wiki 0.045 / arxiv 0.025 / c4-rp 0.15. 256 sequences for width importance, 32 for depth importance.[^minitron-pard-qwen3-14b]
- Width importance comes from forward passes only: each head's output L2 norm, the FFN `down_proj` input, and RMSNorm outputs summed over the layers' norms for hidden channels. Depth importance is the increase in LM loss when one layer is replaced by the identity (base loss 2.326).[^minitron-pard-qwen3-14b]
- Kept layers: 0, 1, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 17, 24, 25, 27–39. The 12 dropped layers each cost 0.022–0.033 nats. Layer 0 is by far the most important (9.37 nats), then layer 6 (0.97), 39 (0.54), 38 (0.22), and 35 (0.099).[^minitron-pard-qwen3-14b]
- In every kept layer, 2 of the 5 query heads in each of the 8 KV groups are kept, all 8 KV heads, the top 3,072 of 17,408 FFN neurons, and the top 1,024 of 5,120 hidden channels.[^minitron-pard-qwen3-14b]
- Zero-shot, the pruned model's SlimPajama validation loss is 9.60 nats/token on average against 1.907 for Qwen3-14B.[^minitron-pard-qwen3-14b]
- The stage took 64 min on the GB10, 44 min of it depth importance.[^minitron-pard-qwen3-14b]

### Training data: the target's own answers

- 45,000 prompts from `Magpie-Align/Magpie-Qwen2-Pro-1M-v0.1` and 5,000 from `theblackcat102/evol-codealpaca-v1`. 128 CodeAlpaca prompts over 1,024 tokens were dropped, leaving 49,872 prompts. This follows the prompt sources of PARD's Qwen recipe.[^minitron-pard-qwen3-14b] See [Magpie](../datasets/magpie.md) and [Evol-CodeAlpaca](../datasets/evol-codealpaca.md).
- Answers: Qwen3-14B, greedy, thinking off, at most 512 new tokens, served by vLLM 0.20. 7.9 h at about 2 prompts/s and 700 output tokens/s.[^minitron-pard-qwen3-14b]
- 26,648 of the 49,872 answers (53%) hit the 512-token cap and are kept.[^minitron-pard-qwen3-14b]
- Recovery trains on 49,372 answers and holds out the last 500. PARD-1 trains on all 49,872, including those 500.[^minitron-pard-qwen3-14b]

### Stage 2: chat-KD recovery

| Setting | Value |
|---|---|
| Teacher | Qwen3-14B bf16, run live on the same GPU (no cache) |
| Loss | forward KL over the full vocabulary, temperature 1.0, answer tokens only |
| Schedule | 3 epochs, about 1,543 steps per epoch, about 18.9M target tokens per epoch, 57M in all |
| Batch | 32 sequences per step, about 14k target tokens |
| Optimizer | lr 3e-5, cosine with min 0.1 × peak, warmup 3%, bf16 |
| Memory | 48 GB in use (teacher bf16 about 28 GB, student fp32 + Adam about 12 GB, plus activations) |
| Time | 3 h 44 min on one H100 at 2.9 s/step; final train loss 1.85 |

All rows: [^minitron-pard-qwen3-14b]

### Stage 3: PARD-1

- AMD's `pard_train.py`. Hard-label cross-entropy on the target-written answers, no teacher logits.[^minitron-pard-qwen3-14b]
- K = 8, mask token id 151670 (the same id as `amd/PARD-Qwen3-0.6B`), COD subsampling (`down_sample_ration` 0.7, minimum 0.2).[^minitron-pard-qwen3-14b]
- 1 epoch = 779 steps of 64 sequences, `max_seq_length` 512, lr 3e-5 cosine with min 0.1, warmup 3%. Qwen3 non-thinking template. 88 min at 6.5 s/step, train loss 3.70.[^minitron-pard-qwen3-14b]
- The recovered checkpoint had to be converted for transformers 4.51.3, which otherwise reads a transformers-5 Qwen3 save with the wrong `rope_theta`.[^minitron-pard-qwen3-14b]
- Upstream `pard_train.py` sets pad to the end token, so `<|im_end|>` is never trained. This is the same for the control.[^minitron-pard-qwen3-14b]

### Control and released reference

- **Control:** Qwen3-0.6B + PARD-1 with the same 49,872 answers, template, K, mask token, COD, learning-rate schedule, epoch count, and 64 sequences per step, on a GB10: 779 steps, 12.0 h, mean train loss 2.84. Only the batch split (8 × 8 against 16 × 4) and checkpoint retention differ.[^minitron-pard-qwen3-14b]
- **Released:** `amd/PARD-Qwen3-0.6B`, revision `f9f650fbab180c26498817718f0db5cae8f25136`. The report states that AMD trained it on about 1M prompts for 4 epochs.[^minitron-pard-qwen3-14b]

### Evaluation

- [Spec-Bench](../benchmarks/spec-bench.md), all 480 questions, against stored Qwen3-14B bf16 greedy non-thinking references: 154,651 response positions. The teacher's argmax equals the stored token at 98.0% of positions.[^minitron-pard-qwen3-14b]
- **MAT** (mean accepted tokens) is offline greedy τ: draft tokens accepted per verify plus the bonus token, so with γ draft tokens the maximum is γ + 1. **top-1** is the fraction of positions where the draft's argmax equals the target's. **Macro MAT** averages over the six tasks.[^minitron-pard-qwen3-14b]
- The PARD evaluator builds PARD's block attention mask, takes the argmax at every anchor × offset in one forward pass, and replays greedy chain acceptance. `--mode ar` scores the same PARD weights as an ordinary autoregressive draft.[^minitron-pard-qwen3-14b]

## Results

### Summary (Spec-Bench, 480 questions, temperature 0)

| Drafter | Params | Backbone AR top-1 | PARD MAT K=8 | Macro MAT K=8 | First-offset top-1 | Same weights as AR draft, MAT γ=8 |
|---|---|---|---|---|---|---|
| **Pruned Qwen3-14B + chat-KD + PARD-1** | 751,632,384 | 0.572 | **1.96** | 1.92 | 0.570 | 2.26 |
| Qwen3-0.6B + PARD-1 (control) | 596,049,920 | 0.747 | 2.66 | 2.73 | 0.751 | 3.55 |
| amd/PARD-Qwen3-0.6B (released) | 596,049,920 | 0.747 | 3.07 | 3.14 | 0.752 | 3.55 |

All rows: [^minitron-pard-qwen3-14b]

The pruned drafter reaches 74% of the control's MAT and 64% of the released drafter's.[^minitron-pard-qwen3-14b] See [A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT](../results/pruned-target-pard-drafter-vs-small-model.md).

### Recovery curve (500 held-out answers, AR τ at γ=5)

| Step | Target tokens | top-1 | Forward KL | τ |
|---|---|---|---|---|
| 0 | 0 | 0.023 | 9.78 | 1.02 |
| 250 | 3.2M | 0.379 | 3.41 | 1.59 |
| 500 | 6.4M | 0.460 | 2.67 | 1.80 |
| 1000 | 12.8M | 0.521 | 2.16 | 1.99 |
| 1543 (end of epoch 1) | 19M | 0.548 | 1.95 | 2.09 |
| 2250 | 28.8M | 0.580 | 1.73 | 2.21 |
| 3000 | 38M | 0.594 | 1.64 | 2.27 |
| 4500 | 57.6M | 0.605 | 1.57 | 2.31 |

All rows: [^minitron-pard-qwen3-14b]

The curve had flattened by the end: +0.001 top-1 per 250 steps in epoch 3. The report concludes that more epochs over the same answers will not help.[^minitron-pard-qwen3-14b]

### Recovered backbone as an autoregressive draft (Spec-Bench)

| Backbone | Recovery | top-1 | MAT γ=3 | MAT γ=5 | MAT γ=7 |
|---|---|---|---|---|---|
| Pruned, no recovery | none | 0.038 | 1.04 | 1.04 | 1.04 |
| **Pruned + chat-KD** | 57M tokens, 3 epochs | **0.572** | **2.00** | **2.17** | **2.24** |
| Qwen3-0.6B (off the shelf) | pretrained | 0.747 | 2.65 | 3.12 | 3.39 |

All rows: [^minitron-pard-qwen3-14b]

Per task at γ=5, the pruned backbone is 0.65–0.74 of Qwen3-0.6B on five tasks and 0.44 on translation (1.39 against 3.13).[^minitron-pard-qwen3-14b]

### PARD-1 drafters at K=8

Per-offset top-1:

| Offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Pruned + chat-KD + PARD-1 | .570 | .400 | .290 | .215 | .165 | .133 | .112 | .096 |
| Control | .751 | .560 | .432 | .338 | .274 | .225 | .189 | .159 |
| Released | .752 | .618 | .520 | .444 | .385 | .337 | .298 | .264 |

All rows: [^minitron-pard-qwen3-14b]

Per task, PARD mode:

| Task | Pruned (K=8) | Control (K=8) | Released (K=7) | Control, AR mode (γ=8) |
|---|---|---|---|---|
| math_reasoning | 2.91 | 4.30 | 5.26 | 6.24 |
| mt_bench | 2.00 | 2.71 | 3.12 | 3.65 |
| rag | 1.84 | 2.46 | 2.80 | 3.29 |
| qa | 1.79 | 2.31 | 2.58 | 2.95 |
| summarization | 1.63 | 2.24 | 2.46 | 2.92 |
| translation | 1.35 | 2.37 | 2.21 | 3.30 |

All rows: [^minitron-pard-qwen3-14b]

- PARD MAT at the PARD-1 checkpoints (steps 200 / 400 / 600 / 779): pruned 1.89 / 1.94 / 1.96 / 1.96, control 2.53 / 2.61 / 2.65 / 2.66.[^minitron-pard-qwen3-14b]
- The released drafter at K=16 scores 3.15 (macro 3.30). Its top-1 at offset 15 is 0.100 and survival to offset 15 is 0.017.[^minitron-pard-qwen3-14b]
- The released drafter's per-task numbers are at K=7, the only setting with a per-task file.[^minitron-pard-qwen3-14b]

### K=7 against K=8 (re-evaluation without retraining)

| Drafter | MAT K=7 | MAT K=8 | Worth of the eighth offset |
|---|---|---|---|
| Pruned + chat-KD + PARD-1 | 1.958 | 1.959 | 0.001 |
| Control | 2.655 | 2.663 | 0.008 |
| Released | 3.031 | 3.07 | 0.04 |

All rows: [^minitron-pard-qwen3-14b]

### Construction time

| Stage | Hardware | Time |
|---|---|---|
| Minitron one-shot prune | GB10 | 64 min |
| Answer regeneration, 49,872 answers | GB10, vLLM 0.20 | 7.9 h |
| Chat-KD recovery, 3 epochs | H100 PCIe 80 GB | 3 h 44 min |
| PARD-1 on the pruned backbone, 779 steps | H100 PCIe 80 GB | 88 min |
| PARD-1 on Qwen3-0.6B (control), 779 steps | GB10 | 12.0 h |

All rows: [^minitron-pard-qwen3-14b]

## Interpretation

The report's findings:[^minitron-pard-qwen3-14b]

1. **The backbone sets the ceiling.** Backbone top-1 0.572 → PARD first-offset top-1 0.570 → MAT 1.96. The PARD stage passes the first offset through unchanged, and the report attributes the gap to the control (1.96 against 2.66) to that first offset (0.570 against 0.751).
2. **But the later offsets also decay faster.** The report adds, as its own computation, that the pruned-to-control ratio of per-offset top-1 falls from 0.76 at offset 0 to about 0.60 at offsets 4–7, and that top-1 at offset 7 relative to offset 0 is 0.17 for the pruned drafter, 0.21 for the control, and 0.35 for the released drafter.
3. **Chat-KD recovery works but has saturated.** It took the pruned model from MAT 1.04 to 2.17 at γ=5 as an autoregressive draft (top-1 0.038 → 0.572), against 3.12 for Qwen3-0.6B. The next levers named are more answers (the Magpie pool has about 300K prompts) or a longer answer cap.
4. **The PARD fine-tune did not lift the backbone's AR MAT further** (2.24 at γ=7 before, 2.26 at γ=8 after), unlike the earlier chat-free recovery. The report reads this as: once the backbone has been distilled on these answers, a second pass over the same answers is not further recovery.
5. **The eighth offset adds almost nothing** for the pruned drafter (0.001) and the control (0.008); for the released drafter it is worth 0.04.
6. **Why chat answers worked**, as the report explains it: the teacher's greedy answers have lower entropy than web text and are easier to match, and Spec-Bench references are the same teacher's chat answers. The chat-KD learning rate (3e-5) was also 3× that of the SlimPajama recovery.

Against the papers and my other experiments:

- **Recipe classification.** The report classifies the pipeline as structured pruning of the target, white-box forward-KL logit distillation on fixed teacher-generated data (no on-policy samples, no RKL/JSD/TVD), then sequence-level distillation only in the PARD stage.[^minitron-pard-qwen3-14b] Minitron also retrains with logit distillation at temperature 1.0,[^muralidharanCompactLanguageModels2024] and PARD-1 trains with cross-entropy and no target model.[^anPARDAcceleratingLLM2025]
- **PARD paper.** The report notes that the PARD paper's Qwen3-14B K=16 τ of 5.14 is averaged over HumanEval, GSM8K, MATH-500, and MT-Bench, while Spec-Bench adds translation, summarization, QA, and RAG, so lower numbers here are expected.[^minitron-pard-qwen3-14b] The released drafter scores 3.15 at K=16 here.[^minitron-pard-qwen3-14b]
- **Osprey's recovery stage.** Osprey's separate recovery stage before target adaptation adds +0.185 overall AL.[^bieOspreyTargetagnosticPretraining2026] Here recovery is what makes the pruned target usable at all (MAT 1.04 unrecovered).[^minitron-pard-qwen3-14b] Osprey recovers with plain next-token prediction on web text;[^bieOspreyTargetagnosticPretraining2026] the report states that the web-text (SlimPajama) version of this pipeline was superseded by chat-KD, without numbers for it.[^minitron-pard-qwen3-14b]

## Limitations

- **Offline only.** Every number is greedy offline MAT on stored references. No live run of the pruned drafter was made, so there is no tok/s figure.[^minitron-pard-qwen3-14b]
- **Different γ.** The "no further lift" comparison is between the backbone at γ=7 (2.24) and the PARD weights in AR mode at γ=8 (2.26).[^minitron-pard-qwen3-14b]
- **Held-out set reused.** The 500 answers held out during recovery are in the PARD-1 training data. Only the recovery curve uses them.[^minitron-pard-qwen3-14b]
- **Numbers not from run folders.** The pruned model's numbers come from the README and the 10-19 log; survival for the pruned drafter is not recorded.[^minitron-pard-qwen3-14b]
- Batch split differs from the control (16 × 4 against 8 × 8, both 64 sequences per step). Optimizer state was not saved, but no run was resumed.[^minitron-pard-qwen3-14b]
- Seed 0 for every run, a single pruning candidate, and only forward KL in recovery, although the training code supports RKL, JSD, and TVD.[^minitron-pard-qwen3-14b]

## Next steps

- From the report: generate more Qwen3-14B answers (the Magpie pool has about 300K prompts) or lift the 512-token answer cap; more epochs on the current answers will not help.[^minitron-pard-qwen3-14b]
- Run the pruned drafter live on the phone, as in [Six phone drafters for a Qwen3-14B server verifier](drafter-evaluation-qwen3-14b.md), to get tok/s.
- Remaining arms of [the pruned-target question](../questions/pruned-target-to-parallel-drafter.md): PARD-2 features on the pruned backbone, and recovery losses other than forward KL ([the target-aware recovery question](../questions/target-aware-recovery-of-pruned-drafters.md)).

## Related

- [A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT](../results/pruned-target-pard-drafter-vs-small-model.md)
- [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md)
- [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- [Does choosing what to prune by target agreement beat LM-loss importance?](../questions/target-agreement-pruning-criteria.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](../questions/cost-efficient-drafter-construction.md)
- [Where Osprey's ideas fit a pruned-target PARD pipeline](../analyses/osprey-ideas-for-pruned-target-pard-pipeline.md)
- [Building a parallel drafter for on-device use without training it from scratch](../analyses/building-parallel-drafters-for-on-device-use.md)
- [Six phone drafters for a Qwen3-14B server verifier](drafter-evaluation-qwen3-14b.md)
- Methods: [PARD](../methods/pard.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Minitron](../methods/minitron.md)
- Data: [Magpie](../datasets/magpie.md), [Evol-CodeAlpaca](../datasets/evol-codealpaca.md). Benchmark: [Spec-Bench](../benchmarks/spec-bench.md)

[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
