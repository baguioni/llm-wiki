---
type: Open Question
title: What is the smallest block drafter that keeps acceptance with a sequential head?
description: A 2-layer DSpark beats a 5-layer DFlash on Qwen3-4B on server GPUs, which suggests a much smaller phone drafter; on my phone the 5-layer DSpark's Markov head costs 8.48-23.68 ms per round on the host CPU and cancels its acceptance gain, while on the server GPU it costs 3.0 ms as a chain, and the head has not been tried on the NPU.
tags: [speculative-decoding, dflash, dspark, draft-model, mobile-npu, mobile-specedge, energy-efficiency]
sources:
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# What is the smallest block drafter that keeps acceptance with a sequential head?

## Question

How few backbone layers can a DSpark-style drafter have on a phone and still match the acceptance of the 5-layer DFlash drafter, once the cost of its sequential head on the phone is counted?

## Why it matters

On my phone the draft cost follows the weight bytes read per token, and a larger model throttles sooner and uses more energy per token (see [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)). Fewer layers at equal acceptance is a direct saving in energy and heat.

## Evidence so far

- With block size 7 and 1 to 5 DSpark layers on Qwen3-4B, accepted length improves monotonically with depth, with the steepest gain from one to two layers. A 2-layer DSpark outperforms the 5-layer DFlash baseline across all domains.[^chengDSparkConfidenceScheduledSpeculative2026]
- On Qwen3-14B, DSpark improves the macro-average accepted length over DFlash by 18.3%.[^chengDSparkConfidenceScheduledSpeculative2026]
- The default sequential head is a Markov head whose $V\times V$ transition matrix is approximated as $B=W_{1}W_{2}$ with $r{=}256$. Sampling runs left to right, so the design requires $T_{\text{sequential}}\ll T_{\text{parallel}}$.[^chengDSparkConfidenceScheduledSpeculative2026]
- On the server, at batch size 128, scaling the draft length from 4 to 16 adds 0.2% to 1.3% to the full-round latency over the DFlash baseline.[^chengDSparkConfidenceScheduledSpeculative2026]
- For DFlash alone, fewer layers cost acceptance: 3 layers against 5 gives $\tau$ 5.64 against 5.99 on Math500 and 3.18 against 3.37 on MT-Bench.[^chenDFlashBlockDiffusion2026]

### My drafter evaluation: the head's cost on the phone

In [my drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md) the released 5-layer DSpark and DFlash drafters for Qwen3-14B ran on the Galaxy S25 NPU at Q4_0, with DSpark's Markov head (42 MB) on the host CPU.[^drafter-evaluation]

| Shape | DSpark tok/round | DFlash tok/round | DSpark Markov head ms | DSpark draft ms | DFlash draft ms | DSpark tok/s | DFlash tok/s |
|---|---|---|---|---|---|---|---|
| chain7 | 3.83 | 3.45 | 8.48 | 38.8 | 30.4 | 26.5 | 25.5 |
| tree16 | 4.64 | 4.15 | 15.49 | 45.8 | 30.6 | 28.3 | 27.9 |
| own-best (budget 32) | 5.02 | 4.37 | 23.68 | 54.2 | 30.6 | 28.2 | 28.8 |

All rows: [^drafter-evaluation]

The report concludes that the Markov head costs as much as it gains, and that its cost grows with the tree.[^drafter-evaluation] On the host CPU the head is not small next to the parallel pass: 8.48 ms against a 29.4 ms NPU decode as a chain.[^drafter-evaluation] It is still untested whether the head runs faster on the NPU, or with fewer rows.

On the server GPU the same head is cheap. In my server-only chain7 runs (PyTorch bf16, eager), DSpark drafts in 27.2 ms against 24.2 ms for DFlash, so the Markov chain costs 3.0 ms per round, against 8.48 ms on the phone's host CPU. There DSpark (33.9 tok/s, 3.90 tok/round) is ahead of DFlash (31.0 tok/s, 3.43 tok/round).[^drafter-evaluation-server-only-chain] See [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md).

**Inference.** The condition $T_{\text{sequential}}\ll T_{\text{parallel}}$ is shown for a server GPU. On the phone the parallel pass is short and the head's two matrices span the full vocabulary, so the condition has to be measured there. With a tree draft, each branch needs its own head step.

## Conflicting claims

None.

## What would resolve it

1. ~~Evaluate the released DSpark and DFlash checkpoints for Qwen3-14B on the same prompts, to confirm the gap in this setup.~~ Done in [my drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md): DSpark accepts 0.38 to 0.65 more tok/round than DFlash.
2. ~~Port the sequential head to the phone client and measure its time on the CPU.~~ Done for the host CPU (see above). Still open: the head on the NPU, and DSpark with fewer Markov rows.
3. Train DSpark drafters with 2 and 3 layers for Qwen3-14B and compare tokens per second and joules per accepted token against the 5-layer DFlash drafter.

## Related

- [DFlash research directions for mobile SpecEdge](../analyses/dflash-research-directions-for-mobile-specedge.md)
- [DSpark](../methods/dspark.md), [DFlash](../methods/dflash.md), [Speculative decoding](../methods/speculative-decoding.md)
- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)
- [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md)
- [Does speculative decoding help on a mobile NPU?](speculative-decoding-on-mobile-npu.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)

[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
