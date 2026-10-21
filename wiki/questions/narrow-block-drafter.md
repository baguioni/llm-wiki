---
type: Open Question
title: Can a block drafter be narrower than its target?
description: DFlash and DSpark drafters run at the target's hidden size because they share its frozen embedding and LM head, which makes them expensive on a phone NPU, and no paper tests a narrower drafter body or how it trains.
tags: [speculative-decoding, dflash, dspark, draft-model, mobile-npu, mobile-specedge, structured-pruning, speculative-drafter]
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
---

# Can a block drafter be narrower than its target?

## Question

Can a [DFlash](../methods/dflash.md)-style block drafter run its layers at a hidden size (width) much smaller than the target's, and keep enough acceptance to be worth it on a phone? If so, does the narrow drafter also train more cheaply, and under what initialization?

Width here means the hidden size $d$, the length of the vector that represents each token inside the model. Depth is the number of layers.

## Why it matters

The research question behind mobile SpecEdge is how to build a mobile-efficient drafter for an arbitrary target at low cost. A block drafter whose width follows the target gets more expensive on the phone as the target gets wider. On my phone NPU, draft latency follows the weight bytes read per token, and per-layer cost grows steeply with width (see [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)):

| Width | Head + overhead | Per layer | 5-layer drafter, from the fit |
|---|---|---|---|
| 5120 | 8.34 ms | 3.624 ms | about 26.5 ms |
| 1024 | 1.95 ms | 0.226 ms | about 3.1 ms |

The last column is my arithmetic from the Q4_0 fit (single token, context depth 0), not a measurement. The width-5120 head alone (151,936 × 5120, 438 MB) costs 8.3 ms per token at Q4_0.

## Evidence so far

### Where the width coupling comes from

- The DFlash drafter shares the target's token embedding layer and LM head and keeps them frozen. Only the draft transformer layers are updated. The stated reasons are training efficiency and keeping the drafter "tightly aligned with the target model's representation space".[^chenDFlashBlockDiffusion2026] Both shared matrices have the target's hidden size, so the draft layers run at that size too.
- The target features themselves do not force the width. They are concatenated from selected target layers and projected once into the draft hidden dimension by a learned matrix, $W_{c}\in\mathbb{R}^{D\times 5D}$.[^chenDFlashBlockDiffusion2026] They then enter every draft layer only as extra keys and values, bypassing the draft model's $Q$ projection, output projection, and FFN.[^chenDFlashBlockDiffusion2026]
- DSpark keeps the DFlash backbone and shares the target's frozen embedding and LM head in the same way.[^chengDSparkConfidenceScheduledSpeculative2026] Its default Markov head adds a low-rank $V\times V$ transition matrix $B=W_{1}W_{2}$ with $r{=}256$.[^chengDSparkConfidenceScheduledSpeculative2026]
- The DFlash ablations vary training data, number of draft layers, number of target hidden features, block size, and KV injection against input fusion.[^chenDFlashBlockDiffusion2026] None varies the drafter's width.

### Evidence that favors a narrower drafter

- Minitron recommends width pruning over depth pruning for the model scales it considers ($\leq$ 15B).[^muralidharanCompactLanguageModels2024] This is a finding about the accuracy of a general language model after pruning and retraining, not about drafter acceptance or latency. Its largest width cut takes the hidden size from 6144 to 3072 (Minitron 4B, 32 layers kept).[^muralidharanCompactLanguageModels2024]
- Minitron distills a narrow student from a wide teacher with "a shared linear transformation during distillation to upscale the student hidden state to the teacher hidden state dimension".[^muralidharanCompactLanguageModels2024]
- Its importance estimate for heads, MLP neurons, and embedding channels uses a calibration set of 1024 samples and only forward passes.[^muralidharanCompactLanguageModels2024]

### Osprey: a narrower autoregressive drafter that beats a full-width one

- The Osprey drafter for Qwen3-8B runs at hidden size 2560, the width of its Qwen3-4B source, with its own embedding and LM head resized to the target vocabulary. The EAGLE-3 drafters for the same target run at 4096.[^bieOspreyTargetagnosticPretraining2026]
- Body parameters, excluding embedding and LM head: Osprey 265 M (2 layers), 1-layer EAGLE-3 269 M, 2-layer EAGLE-3 487 M.[^bieOspreyTargetagnosticPretraining2026]
- Osprey still reaches a higher mean AL than both EAGLE-3 drafters. The authors credit the pretrained language prior, not capacity.[^bieOspreyTargetagnosticPretraining2026]
- The target features still enter at full size: the EAGLE-3 low, mid, and high features go through zero-initialized QKV columns added to the narrow drafter.[^bieOspreyTargetagnosticPretraining2026]

**Inference.** This is option D above (a new head at the drafter's own width) on an autoregressive drafter, and it works when the narrow body is pretrained. It says nothing yet about a block drafter with KV injection, where Osprey's own DFlash warm-start result was weak (see [the target-layer initialization question](target-layer-initialization-for-block-drafters.md)).

### PARD-2 on my phone: a narrow parallel drafter with projected target features

- In [my drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md), PARD-2 (`amd/PARD2-Qwen3-14B`) is one of the "0.6B-shaped" drafters (409 MB at Q4_0, about 885 MB of NPU DMA-BUF, the same as Qwen3-0.6B and PARD-1). DFlash and DSpark take 1741 MB and about 1.7 GB.[^drafter-evaluation]
- The server taps target layers 17, 25, and 33 plus the final post-norm and projects them from 20480 to 1024 wide with `target_proj` (40 MB, on the server). The phone adds the 1024-wide feature to the token embedding. So it downloads a 2 KB feature row per committed token, against 10 KB for DFlash and DSpark.[^drafter-evaluation]
- Against the full-width DFlash on the same 60 requests: 24.9 / 29.3 / 30.0 tok/s against 25.5 / 27.9 / 28.8 (chain7 / tree16 / own-best), and 3.34 / 4.21 / 4.58 tok/round against 3.45 / 4.15 / 4.37. Its NPU decode takes 21.6–22.0 ms against 29.6–29.7 ms for DFlash.[^drafter-evaluation]

**Inference.** This is the "apply $W_{c}$ on the server" option from the inference list below, on a narrow drafter, and it keeps acceptance level with the full-width DFlash on this phone. It is not a test of a narrow DFlash: PARD-2 adds the features to the input embedding, not through KV injection, and it is a different drafter family with different training.

### Ways to shrink the LM head

- FR-Spec observed that large vocabularies often make the latency of LM heads dominate the total latency of speculator heads, even in EAGLE, and truncates the draft vocabulary to a subset of high-frequency tokens.[^samarinLKLossesDirect2026] EAGLE-3 uses such a truncated vocabulary.[^samarinLKLossesDirect2026]
- Truncation complicates KL-based training, because KL divergence becomes infinite for tokens outside the draft vocabulary, so the target distribution has to be masked. LK losses handle truncation without that change, since excluded tokens contribute nothing to the acceptance rate.[^samarinLKLossesDirect2026]

### Evidence about training cost

- The fewer-token results for narrow models come from inheriting trained weights. Minitron derives its 8B and 4B models from a pretrained 15B model with up to 40$\times$ fewer training tokens than training from scratch.[^muralidharanCompactLanguageModels2024] Sheared LLaMA needs $3\%$ of the compute of training such models from scratch.[^xiaShearedLLaMAAccelerating2024]
- In EAGLE-3 training, the target model's prefill stage often becomes the dominant bottleneck.[^liSpecForgeFlexibleEfficient2026] SpecForge's loss-backward kernel cuts memory by 30–40%, depending on context length and the draft model's vocabulary size.[^liSpecForgeFlexibleEfficient2026]
- DFlash samples 512 anchor positions per training sequence,[^chenDFlashBlockDiffusion2026] and the storage for cached target hidden states grows linearly with the number of extracted features.[^chenDFlashBlockDiffusion2026]

### Inference

- **Design options.** From least to most invasive: (A) narrow draft layers between a down-projection after the embedding and an up-projection before the frozen head; (B) a frozen head restricted to a high-frequency subset of the vocabulary; (C) a low-rank head; (D) a new trained head at the narrow width. A keeps the target-aligned head but leaves its 8.3 ms. A with B removes most of both costs. D loses the frozen alignment and adds about $V\cdot d$ trainable parameters.
- **Training cost.** A narrow body cuts only the draft-layer part of each training step. The target forward pass, the full-vocabulary logits at every predicted position, and generating the training data are unchanged unless the head is also truncated or the target features are cached. A narrow body with random initialization has no known reason to need fewer tokens, and probably reaches a lower $\tau$. Any token saving would come from initializing the narrow layers from width-pruned target layers, which joins this question to [the target-layer initialization question](target-layer-initialization-for-block-drafters.md).
- **Network.** If the server applies $W_{c}$ before sending, the feature sent per accepted token shrinks from $5D$ to $d$ values, 25× less at $D=5120$ and $d=1024$.
- **KV injection under compression.** At $d=1024$ for a 5120-wide target, every draft layer sees the five target features compressed 25×. How much acceptance survives is the main unknown.

## Conflicting claims

On server GPUs, [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) finds that draft latency is bottlenecked by model depth, and trades depth for width at the same parameter count to raise throughput by over 60%.[^yanDecodingSpeculativeDecoding2025] On my phone NPU, cost follows weight bytes instead. This is a hardware difference, not a contradiction between sources, but the server guidance to keep drafters wide does not carry over to the phone.

## What would resolve it

1. Profile the live 5-layer DFlash draft on the S25 and split its time into the head and the body. This decides whether to start with the head (B) or the body (A).
2. Train option A at $d\in\{1024, 2048\}$ for Qwen3-14B on about 100K samples, with random initialization, and compare $\tau$ against the released full-width drafter.
3. Repeat 2 with the narrow layers initialized from width-pruned target layers, using Minitron's activation-based importance. Plot $\tau$ against training samples for both initializations. A token saving shows as the gap between the curves.
4. Add a truncated-vocabulary head with $K\in\{16\text{K}, 32\text{K}, 64\text{K}\}$. First measure the share of target tokens each $K$ covers on SpecBench, then $\tau$.
5. Measure tokens per second and joules per accepted token on the phone for each variant.

## Related

- [Building a parallel drafter for on-device use without training it from scratch](../analyses/building-parallel-drafters-for-on-device-use.md)
- [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md)
- [DFlash research directions for mobile SpecEdge](../analyses/dflash-research-directions-for-mobile-specedge.md)
- [Does starting a block drafter from the target's own layers cut its training cost?](target-layer-initialization-for-block-drafters.md)
- [What is the smallest block drafter that keeps acceptance with a sequential head?](minimum-drafter-depth-with-sequential-head.md)
- [Does an acceptance-oriented loss help a block diffusion drafter?](acceptance-oriented-loss-for-block-drafters.md)
- [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [KV injection](../methods/kv-injection.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md)
- Papers: [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md), [Minitron](../papers/muralidharanCompactLanguageModels2024.md), [Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md), [LK losses](../papers/samarinLKLossesDirect2026.md), [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)
- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
