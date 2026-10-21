---
type: Analysis
title: DFlash research directions for mobile SpecEdge
description: Which changes to a DFlash-style block drafter look worth testing for mobile-server speculative decoding, read from the drafter papers and my phone NPU profiling.
tags: [speculative-decoding, dflash, draft-model, mobile-npu, mobile-specedge, speculative-drafter]
question: For the DFlash direction of mobile SpecEdge, which experiments are worth running beyond the released drafter?
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
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
---

# DFlash research directions for mobile SpecEdge

## Question

For the DFlash direction of mobile SpecEdge, which experiments are worth running beyond the released drafter?

## Answer

Statements marked **Inference** combine sourced facts with my own measurements in [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md). They are not results from any paper.

**Inference.** In the live runs the draft takes about 30 ms of a round whose server forward takes about 98 ms, so raising acceptance is worth more than cutting draft time. Six switches follow, ordered by expected value for the effort.

| # | Direction | What the papers say | Expected effect on the phone (inference) |
|---|---|---|---|
| 1 | Add a sequential head (DSpark) | DSpark couples the parallel backbone with a lightweight sequential head. On Qwen3-14B it improves macro-average accepted length over DFlash by 18.3%.[^chengDSparkConfidenceScheduledSpeculative2026] Checkpoints and a training repository (DeepSpec, which includes Eagle3, DFlash, and DSpark) are released.[^chengDSparkConfidenceScheduledSpeculative2026] | The largest sourced gain, and it needs no training. The cost of the serial sampling loop on the phone is unmeasured. |
| 2 | Larger block | Block 16 against block 8 with 8 layers: $\tau$ 6.33 against 5.21 on Math500, 3.50 against 3.29 on MT-Bench.[^chenDFlashBlockDiffusion2026] DSpark's gain over DFlash widens with proposal length: 18% on chat at $\gamma=7$ and 22% at $\gamma=15$.[^chengDSparkConfidenceScheduledSpeculative2026] | Free on the NPU, where 16 rows cost the same as 8. A small gain on chat, more on math and code. My depth sweep already shows shrinking gains: 4.07, 4.38, 4.51 at depths 5, 6, 7. |
| 3 | Acceptance-oriented loss | LK losses optimize acceptance rate directly and reach gains of up to 8-10% in average acceptance length.[^samarinLKLossesDirect2026] DFlash trains with position-weighted cross-entropy.[^chenDFlashBlockDiffusion2026] DSpark already mixes a total variation term into its loss ($\alpha_{\text{ce}}=0.1$, $\alpha_{\text{tv}}=0.9$).[^chengDSparkConfidenceScheduledSpeculative2026] | Small at temperature 0, which is how my server verifies. See [the open question](../questions/acceptance-oriented-loss-for-block-drafters.md). |
| 4 | Start the draft layers from target layers | Deriving a small model from a pretrained one is far cheaper than training from scratch: Sheared LLaMA uses $3\%$ of the compute,[^xiaShearedLLaMAAccelerating2024] and Minitron needs up to 40$\times$ fewer training tokens.[^muralidharanCompactLanguageModels2024] SDFP builds a draft from the target's own layers with no training.[^weiSDFPSpeculativeDecoding2026] No paper does this for a block drafter. | Faster convergence and better acceptance with little training data. Probably the same final acceptance with full data. See [the open question](../questions/target-layer-initialization-for-block-drafters.md). |
| 5 | Fewer layers with a sequential head | A 2-layer DSpark outperforms the 5-layer DFlash baseline across all domains on Qwen3-4B.[^chengDSparkConfidenceScheduledSpeculative2026] | About half the weight bytes for the same acceptance, so lower energy and less throttling. See [the open question](../questions/minimum-drafter-depth-with-sequential-head.md). |
| 6 | Deeper drafter | 5 to 8 layers: $\tau$ 5.99 to 6.33 on Math500 and 3.37 to 3.50 on MT-Bench.[^chenDFlashBlockDiffusion2026] The paper notes that the best depth depends on the deployment setting.[^chenDFlashBlockDiffusion2026] | Likely no net gain. The block costs about 30 ms at 5 layers and 45.0 ms at 8 x 5120, which offsets a 4 to 6% gain in $\tau$. |

A seventh idea has no paper behind it: use the time the phone waits for verification to draft the next block. It is blocked by the fact that DFlash conditions on target context features,[^chenDFlashBlockDiffusion2026] which arrive with the verify response. See [Can a block drafter pre-draft with stale target features?](../questions/pre-drafting-with-stale-target-features.md)

### How the switches combine

**Inference.** Head (none or sequential), block size, loss, and initialization are independent settings of one training run. Testing each against the released baseline on the same training subset is cheaper than testing combinations. The DFlash paper's own ablations use 100K samples,[^chenDFlashBlockDiffusion2026] which is a comparable budget.

## Evidence

Paper numbers are copied from the Paper pages of the six cited papers. Phone numbers are from the Experiment page linked above.

DSpark training setup, for reference: prompts from Open-PerfectBlend, 1.3 million samples, responses regenerated by each target model, each drafter trained for 10 epochs, non-thinking mode. DFlash and DSpark have 5 draft layers and block size 7.[^chengDSparkConfidenceScheduledSpeculative2026]

## Caveats

- Every "expected effect" cell is an inference. None is measured.
- The paper numbers are from server GPUs. The DSpark depth result is for Qwen3-4B, not Qwen3-14B.
- LK losses were tested on EAGLE-3, MEDUSA, MLP speculator, and MTP drafters, not on a block diffusion drafter.[^samarinLKLossesDirect2026]
- Sheared LLaMA and Minitron build general small language models, not drafters, so their cost savings may not transfer.
- The phone measurements are from one device and mostly random-weight models, so they give cost, not acceptance.

## Related

- [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [KV injection](../methods/kv-injection.md), [Speculative decoding](../methods/speculative-decoding.md), [Structured pruning](../methods/structured-pruning.md)
- [DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B](dflash-dspark-eagle-3-drafting-comparison.md)
- [Applying the speculative drafter papers to a mobile phone NPU](speculative-drafter-papers-on-mobile-npu.md)
- [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
