---
type: Analysis
title: Why parallel drafters beat EAGLE-3
description: At equal depth an autoregressive drafter accepts more tokens, but one pass per block makes depth cheap and KV injection makes it useful, so a 5-layer DFlash beats a 1-layer EAGLE-3 on first-token acceptance and on wall-clock speedup.
tags: [speculative-decoding, dflash, dspark, eagle-3, kv-injection, parallel-drafting, draft-model]
question: Why does a parallel drafter like DFlash beat an autoregressive drafter like EAGLE-3, when autoregression is expected to draft better?
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
---

# Why parallel drafters beat EAGLE-3

## Question

Why does a parallel drafter like [DFlash](../methods/dflash.md) beat an autoregressive drafter like [EAGLE-3](../methods/eagle-3.md), when autoregression is expected to draft better? The DSpark paper calls its own version of this result counter-intuitive, because it contrasts with the standard expectation that step-by-step autoregression produces higher-quality sequences than parallel models.[^chengDSparkConfidenceScheduledSpeculative2026]

## Answer

Autoregression still drafts better token for token at the same depth. Parallel drafting wins on cost. One pass per block makes depth cheap, and [KV injection](../methods/kv-injection.md) makes that depth useful. In practice EAGLE-3 is kept at 1 layer to stay fast, so DFlash ends up deeper and better conditioned, and it wins both on first-token accuracy and on wall-clock time.

Each part of this summary rests on a sourced result:

1. **Same depth, autoregression accepts more.** With 5 draft layers and KV injection in both, the autoregressive DFlash-AR reaches $\tau$ 4.8 on GSM8K against 4.2 for parallel DFlash.[^chenDFlashBlockDiffusion2026]
2. **Parallel wins on cost.** An autoregressive drafter pays $T_{\text{draft}}=\gamma\cdot t_{\text{step}}$, while a diffusion drafter pays one parallel pass that is largely insensitive to $\gamma$ for moderate block sizes, so the drafter can be deeper.[^chenDFlashBlockDiffusion2026] In the same ablation, parallel DFlash has the higher speedup (3.3× against 2.4× on GSM8K) despite the lower $\tau$.[^chenDFlashBlockDiffusion2026]
3. **KV injection makes depth useful.** With input fusion, as in EAGLE-3, target information becomes more diluted as draft depth grows, so added layers give diminishing gains in acceptance length. Injecting the target features into every draft layer lets acceptance length scale with the number of draft layers.[^chenDFlashBlockDiffusion2026]
4. **EAGLE-3 stays at 1 layer.** Autoregressive drafters are constrained to very shallow architectures to keep latency manageable, for example a single transformer layer in EAGLE-3.[^chenDFlashBlockDiffusion2026] The DSpark paper's comparison uses 1 layer for Eagle3 and 5 for DFlash and DSpark.[^chengDSparkConfidenceScheduledSpeculative2026]
5. **The deeper drafter wins at position 1.** At the first draft position both architectures predict from the target context alone, so the gap comes from capacity. DFlash starts higher than Eagle3 (0.88 against 0.81 on Math, 0.72 against 0.53 on Chat). A rejection at position 1 invalidates the whole block, so this advantage disproportionately raises the final accepted length.[^chengDSparkConfidenceScheduledSpeculative2026]
6. **The deeper drafter wins on wall-clock time.** Under greedy decoding on Qwen3, DFlash averages a 4.9× speedup over autoregressive decoding, a 2.4× improvement over EAGLE-3 (16). At temperature 1 the improvement is 2.2×.[^chenDFlashBlockDiffusion2026]

**Inference.** Expected accepted draft tokens are $a_{1}+a_{1}a_{2}+a_{1}a_{2}a_{3}+\cdots$, where $a_{k}$ is the conditional acceptance at position $k$, so $a_{1}$ scales every term. On Chat, the move from 0.53 to 0.72 alone scales the sum by about 1.36×, before any later position is counted. This arithmetic is mine, not the paper's.

## Evidence

### Same depth, different drafting style and conditioning

Ablation on Qwen3-4B, 5-layer draft models, draft block size 8. Each cell is $\tau$ / speedup.[^chenDFlashBlockDiffusion2026]

| Drafting | Variant | Injection | GSM8K | HumanEval | MT-Bench |
|---|---|---|---|---|---|
| Autoregressive | EAGLE-3-5L | Input | 4.2 / 2.1× | 4.3 / 2.2× | 3.1 / 1.4× |
| Autoregressive | DFlash-AR | KV | 4.8 / 2.4× | 4.6 / 2.3× | 3.4 / 1.5× |
| Block diffusion | DFlash | Input | 3.5 / 2.9× | 3.5 / 2.9× | 2.6 / 2.0× |
| Block diffusion | DFlash | KV | 4.2 / 3.3× | 4.0 / 3.2× | 3.0 / 2.2× |

All rows: [^chenDFlashBlockDiffusion2026]

- At fixed drafting style, KV injection beats input fusion on every task.[^chenDFlashBlockDiffusion2026]
- At fixed conditioning (KV), autoregressive drafting has the higher $\tau$ and parallel drafting has the higher speedup on every task.[^chenDFlashBlockDiffusion2026]
- The authors summarize that DFlash achieves acceptance length comparable to EAGLE-3-5L but much higher speedup, because block diffusion drafts multiple tokens in parallel.[^chenDFlashBlockDiffusion2026]

### Position-wise conditional acceptance

The DSpark paper measures, for each draft position $k$, the share of accepted tokens among only the rounds in which positions 1 to $k-1$ were all accepted. Qwen3-4B target, 1-layer Eagle3, 5-layer DFlash and DSpark, block size 7.[^chengDSparkConfidenceScheduledSpeculative2026]

| Drafter | Position 1 | Later positions |
|---|---|---|
| Eagle3 (autoregressive) | 0.81 on Math, 0.53 on Chat | Stable or rising, for example from 0.53 to 0.74 on Chat |
| DFlash (parallel) | 0.88 on Math, 0.72 on Chat | Decaying: from 0.87 to 0.78 on Code, from 0.72 to 0.63 on Chat |
| DSpark (semi-autoregressive) | 0.93 on Math | High and stable |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

The later-position decay is the cost of independence. Each parallel position marginalizes over all possible prior tokens instead of conditioning on the sampled prefix, so the drafter can propose inconsistent suffixes, a failure called multi-modal collision.[^chengDSparkConfidenceScheduledSpeculative2026] [DSpark](../methods/dspark.md) keeps the deep parallel backbone for position 1 and adds a lightweight sequential head to reduce the decay. A 2-layer DSpark outperforms the 5-layer DFlash across all domains.[^chengDSparkConfidenceScheduledSpeculative2026]

## Caveats

- The same-depth ablation is one target (Qwen3-4B), one block size (8), and three tasks, with ablation models trained on 100K samples drawn from the full data mixture.[^chenDFlashBlockDiffusion2026]
- The position-wise measurements are for Qwen3-4B only.[^chengDSparkConfidenceScheduledSpeculative2026]
- The parallel drafter does not always win. In the DSpark paper, with all drafters retrained on the same data, Eagle3 has higher accepted length than DFlash on every benchmark for Gemma4-12B, for example 5.87 against 5.45 on GSM8K.[^chengDSparkConfidenceScheduledSpeculative2026]
- The size of the margin depends on the EAGLE-3 baseline. The 2.4× figure uses EAGLE-3 checkpoints released by AngelSlim with tree drafting,[^chenDFlashBlockDiffusion2026] while the DSpark paper's retrained Eagle3 is close to DFlash on Qwen3 (5.30 against 5.33 on Qwen3-8B GSM8K).[^chengDSparkConfidenceScheduledSpeculative2026] See [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)

## Related

- [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-3](../methods/eagle-3.md), [KV injection](../methods/kv-injection.md), [Speculative decoding](../methods/speculative-decoding.md)
- [DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B](dflash-dspark-eagle-3-drafting-comparison.md)
- [What is the smallest block drafter that keeps acceptance with a sequential head?](../questions/minimum-drafter-depth-with-sequential-head.md)
- Papers: [DFlash](../papers/chenDFlashBlockDiffusion2026.md), [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
