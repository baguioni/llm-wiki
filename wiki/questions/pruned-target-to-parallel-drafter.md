---
type: Open Question
title: Can a pruned target be turned into a parallel drafter?
description: PARD converts a small same-series autoregressive model into a parallel drafter and Minitron-style pruning can produce such a model from the target; no paper chains the two, my first run of the chain on Qwen3-14B reaches offline MAT 1.96 at K=8 against 2.66 for a same-recipe Qwen3-0.6B drafter, and DFlash and PARD-2 disagree on how far a PARD drafter can go.
tags: [speculative-decoding, parallel-drafting, draft-model, structured-pruning, mobile-specedge, speculative-drafter, pard, dflash]
sources:
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Can a pruned target be turned into a parallel drafter?

## Question

If the target is width-pruned and distilled into a small autoregressive model, and that model is then trained into a parallel drafter with PARD's mask tokens (and optionally PARD-2's target features), does the result match a drafter built from a same-series small model, and at what construction cost?

## Why it matters

Parallel drafters are the fastest drafters on my phone,[^drafter-evaluation] but DFlash and DSpark run at the target's width and cannot be cut from the target. PARD needs a small model of the target's own series, and not every target has one. A pruned target would supply that model for any target. See [Building a parallel drafter for on-device use](../analyses/building-parallel-drafters-for-on-device-use.md).

## Evidence so far

- PARD adapts a standard autoregressive draft model into a parallel one with mask-token training, and COD cuts that cost by up to 3×.[^anPARDAcceleratingLLM2025] Its drafters start from existing small models, for example DeepSeek-R1-Qwen-1.5B for a DeepSeek-R1-Qwen-7B target in the ablations.[^anPARDAcceleratingLLM2025]
- Minitron derives 8B and 4B models from Nemotron-4 15B with up to 40× fewer training tokens than from scratch, using an importance estimate from 1024 calibration samples and forward passes only.[^muralidharanCompactLanguageModels2024]
- PARD-2 adds features from 4 target layers to the drafter's input embeddings.[^anPARD2TargetAlignedParallel2026] On my phone the 409 MB PARD-2 drafter for Qwen3-14B matches the 1741 MB DFlash (30.0 against 28.8 tok/s own-best).[^drafter-evaluation]
- Osprey shows that a pruned pretrained body is a useful warm start when target features enter through zero-initialized QKV columns,[^bieOspreyTargetagnosticPretraining2026] and nearly useless under DFlash's KV injection (at most 0.07 accepted tokens).[^bieOspreyTargetagnosticPretraining2026]
- No paper in the wiki starts a parallel drafter from a pruned target. My own experiment does (below).

### Points specific to PARD-2

- PARD-2 fuses low-, middle-, and high-level target hidden states into $t=\mathrm{Proj}([l;m;h])$ with "a lightweight projection module" and adds it to the draft input embeddings, $e^{d^{\prime}}=e^{d}+\xi\cdot t$ with $\xi\sim\mathrm{Bernoulli}(1-\rho)$.[^anPARD2TargetAlignedParallel2026] The paper does not say how $\mathrm{Proj}$ is initialized.
- Nothing in that recipe names a particular backbone. PARD-2 describes PARD as adapting "auto-regressive models to parallel masked prediction".[^anPARD2TargetAlignedParallel2026]
- Minitron retrains its pruned models by distillation from the unpruned model,[^muralidharanCompactLanguageModels2024] and PARD-2's loss also has a distillation term toward the target.[^anPARD2TargetAlignedParallel2026] With a pruned target, the teacher is the same model in both stages.
- Tested compression ratios are far below a phone-sized drafter. Minitron's largest cut, Nemotron-4 15B to Minitron 4B, removes 73.3% of the weights, and the two-step route (15B to 8B to 4B) scores 12% higher on MMLU than one-shot.[^muralidharanCompactLanguageModels2024] Sheared LLaMA goes from 7B to 1.3B.[^xiaShearedLLaMAAccelerating2024] Qwen3-14B to a 0.6B shape is about 23× (my arithmetic). My run kept 5.1% of the target's parameters: 0.75B, because the pruned model keeps untied input and output embeddings.[^minitron-pard-qwen3-14b]
- A drafter may not need full language-model recovery after pruning. Yan et al. skip Sheared LLaMA's continued pre-training, and their NoFT-Wide-796M draft reaches 97.7% to 111.8% higher throughput than Sheared-LLaMA-1.3B with 0.8% of its training tokens.[^yanDecodingSpeculativeDecoding2025] Their drafts are pruned from LLaMa-7B and LLaMa-3.2-1B, not from the target.[^yanDecodingSpeculativeDecoding2025] Osprey's 10k-step pretraining checkpoint adapts to AL 3.552 against 3.578 for 55k steps.[^bieOspreyTargetagnosticPretraining2026]

### My experiment: [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)

Qwen3-14B was pruned in one Minitron step to the Qwen3-0.6B shape (28 layers, hidden 1024), recovered by forward-KL distillation from Qwen3-14B on 57M tokens of its own greedy answers ("chat-KD"), and fine-tuned into a PARD-1 drafter with K=8. A control ran the same data and PARD recipe on Qwen3-0.6B. All numbers are offline greedy MAT on the 480 Spec-Bench questions.[^minitron-pard-qwen3-14b]

| Drafter | Backbone AR top-1 | PARD MAT K=8 | First-offset top-1 |
|---|---|---|---|
| Pruned Qwen3-14B + chat-KD + PARD-1 | 0.572 | 1.96 | 0.570 |
| Qwen3-0.6B + PARD-1 (control, same data and recipe) | 0.747 | 2.66 | 0.751 |
| amd/PARD-Qwen3-0.6B (released) | 0.747 | 3.07 | 0.752 |

All rows: [^minitron-pard-qwen3-14b]

- **The chain works, but below the small-model route.** The pruned drafter reaches 74% of the control's MAT and 64% of the released drafter's.[^minitron-pard-qwen3-14b]
- **Recovery is essential.** Unrecovered, the pruned model has top-1 0.038 and MAT 1.04. Chat-KD lifts it to MAT 2.17 at γ=5 as an AR draft, against 3.12 for Qwen3-0.6B, and the recovery curve had flattened by the third epoch.[^minitron-pard-qwen3-14b]
- **The backbone sets the ceiling.** PARD training passes the backbone's first-token accuracy through unchanged (0.572 → 0.570), and the report attributes the gap to the control to that first offset. Its own computation adds that the later offsets also decay faster than the control's (ratio 0.76 at offset 0, about 0.60 at offsets 4–7).[^minitron-pard-qwen3-14b]
- **Construction time.** 64 min to prune on a GB10, 7.9 h to regenerate 49,872 answers on a GB10, 3 h 44 min of chat-KD recovery and 88 min of PARD-1 on one H100.[^minitron-pard-qwen3-14b]
- The pruned drafter has not been run live, so there is no tok/s figure for it.[^minitron-pard-qwen3-14b]

See [A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT](../results/pruned-target-pard-drafter-vs-small-model.md).

**Inference.** The question's first part now has a partial answer for Qwen3-14B: a pruned target does become a working PARD-1 drafter, but with 49,872 answers it stays well below a drafter built on the same-series small model. Since the gap follows the backbone's first-token accuracy, the open lever is a better-recovered backbone (more answers, or a longer cap, as the report suggests) rather than the PARD stage.

## Conflicting claims

- DFlash states that PARD's small models "lack the modeling capacity of the target LLMs, leading to limited acceptance lengths and a speedup ceiling of approximately 3×".[^chenDFlashBlockDiffusion2026]
- PARD-2 reports target-independent PARD at an average of 4.39× / τ 5.56 on Qwen3-8B and 4.51× / 5.14 on Qwen3-14B, on vLLM with A100-40GB at temperature 0 and draft length 16.[^anPARD2TargetAlignedParallel2026] PARD's own paper reports 3.00× average and 3.63× on HumanEval for LLaMA3.1-8B.[^anPARDAcceleratingLLM2025]
- The settings differ (targets, draft length, benchmarks), so the 3× figure may describe the original PARD on LLaMA targets rather than a limit. Both claims are kept on [PARD](../methods/pard.md).

## What would resolve it

1. For Qwen3-14B, width-prune the target to the Qwen3-0.6B shape and distill it, then PARD-train it on the same data as `amd/PARD-Qwen3-0.6B`. Compare τ and tok/s on the phone against PARD-1. *Partly done:* pruned (depth and width), distilled, and PARD-trained on 49,872 target-written answers with a same-data Qwen3-0.6B control, scored offline only ([Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)). Still open: the same with more data, and tok/s on the phone.
2. Repeat with PARD-2 features added at the input, and compare against `amd/PARD2-Qwen3-14B`.
3. Report the GPU-hours of pruning, distillation, and PARD training separately, so the cost can be set against Osprey's 48 H100-hours per target. *Done for the first run:* see the construction times above.[^minitron-pard-qwen3-14b]

## Related

- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md), [A pruned-target PARD-1 drafter reaches 74% of a same-recipe Qwen3-0.6B drafter's MAT](../results/pruned-target-pard-drafter-vs-small-model.md)
- [Where Osprey's ideas fit a pruned-target PARD pipeline](../analyses/osprey-ideas-for-pruned-target-pard-pipeline.md)
- [Target-aware recovery of compressed drafters](../analyses/target-aware-recovery-of-compressed-drafters.md)
- [Does recovering a pruned drafter against the target beat recovering it against its parent?](target-aware-recovery-of-pruned-drafters.md)
- [Building a parallel drafter for on-device use](../analyses/building-parallel-drafters-for-on-device-use.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)
- [Can a block drafter be narrower than its target?](narrow-block-drafter.md)
- [Does starting a block drafter from the target's own layers cut its training cost?](target-layer-initialization-for-block-drafters.md)
- [PARD](../methods/pard.md), [Structured pruning](../methods/structured-pruning.md), [Osprey](../methods/osprey.md), [DFlash](../methods/dflash.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
