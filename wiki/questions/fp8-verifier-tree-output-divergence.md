---
type: Open Question
title: Why do tree-verified outputs diverge from chain outputs at temperature 0?
description: In my drafter evaluation, tree arms reproduce the chain arms' greedy output on only 28-33 of 60 requests; the report attributes this to FP8 verifier numerics that change with the number of verified rows, but a tree-verify bug has not been ruled out.
tags: [speculative-decoding, tree-based-speculation, verification, fp8, mobile-specedge, reproducibility]
sources:
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: drafter-evaluation-server-shapes
    resource: raw/experiments/drafter-evaluation-server-shapes.md
    title: "Drafter evaluation with server-only baselines at the SpecEdge, chain7, and tree16 shapes (§2.7, §5.5)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# Why do tree-verified outputs diverge from chain outputs at temperature 0?

## Question

At temperature 0, speculative decoding should reproduce the target's greedy output exactly. In my drafter evaluation, the tree arms do not reproduce the chain arms' output. Is this only the FP8 verifier's numerics, or is there a bug in the tree verify path?

## Why it matters

- Speculative sampling is described as a lossless acceleration technique,[^liEAGLE3ScalingInference2025] and DFlash reports its speedups as lossless acceleration.[^chenDFlashBlockDiffusion2026] My results rely on the same property.
- If the arms decode different continuations, acceptance is compared on matched prompts but not on identical outputs.[^drafter-evaluation]

## Evidence so far

All from the output-agreement check of [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md), first 64 output tokens of every arm, repeat 1:[^drafter-evaluation]

- All four feature-drafter chains (DFlash, DSpark, EAGLE-3, PARD-2) produce identical outputs on all 60 requests.
- The two plain-server chains (PARD-1, Qwen3-0.6B) are identical to each other and match the feature-drafter chains on 53/60 requests.
- Tree arms match the chain outputs on only 28–33 of 60 requests, and agree with the DFlash tree16 output on 33–54 of 60. The first differing token is at a median position of about 21–47.
- The divergences are near-ties: the texts stay fluent and differ by one plausible word ("first published in 1912" against "first recorded in 1912").
- Divergence depends on how many rows the server verifies: 8-row chains agree with each other, and trees with 17 or 33 rows diverge.
- Every repeat of an arm reproduced its own output exactly.
- An earlier measurement found a budget-dependent 4.6–7.1% divergence of the FP8 verifier. The report's explanation is that the FP8 target's logits shift with the batch's row count and contents (kernel choice, tiling, accumulation order), which flips near-tied argmaxes.
- The effect on acceptance should be small: oracle and live tok/round differ by at most 0.11.

From the server-only runs, where the draft runs on the server GPU with no phone:[^drafter-evaluation-server-shapes]

- Server-only chain7 and server-only tree16 agree on only 28/60 requests, the same divergence as between the phone chain and tree arms. The report concludes that it depends on the verified row count, not on where the drafter runs.
- Server-only chain7 matches the phone chain7 on 60/60 requests (both verify 8 rows). Server-only tree16 matches the phone tree16 on 41/60 (both verify 17 rows). The report notes that the Python and C++ tree builders also pick nodes slightly differently.

From the server-only chain7 runs of all six drafters (PyTorch bf16 drafts, cold prefill, 8 verified rows):[^drafter-evaluation-server-only-chain]

- The four feature drafters produce identical outputs on 60/60 requests, and so do the two token drafters. Token drafters against feature drafters agree on 57/60, with the first difference at a median of token 58.
- The report explains the two groups by how the target sees the last prompt token: a feature drafter's prefill covers the whole prompt, while a token drafter's prompt ends in round 0's 8-row verify. It concludes that the output depends on the target's numerics (FP8, fp16 activations, the exact batch shape), not on the drafter, and that speculative decoding at temperature 0 is lossless only up to those numerics.
- Each token drafter matches its phone chain7 arm on 60/60. Each feature drafter matches its phone arm on only 52/60 (median first difference at token 49). The cause was not investigated; the phone arms' server prefilled from a cache, and these runs compute the prefill live.
- Repeats are identical round for round in every arm.

**Inference.** These chain-only runs show the same kind of divergence without any tree: a change in how a position is first computed (prefill against verify, cached against live prefill) is enough to change the output. That supports the numerics explanation, but it does not test the tree verify path itself.

## Conflicting claims

None between sources. The report itself states that it has not been proved that the tree verify path has no bug.[^drafter-evaluation]

## What would resolve it

- Compare tree-arm outputs against a target-only greedy run that uses the same row count.[^drafter-evaluation]
- Repeat the tree arms with a bf16 or fp16 verifier. If the divergence disappears, it comes from FP8 numerics.

## Related

- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)
- [Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md)
- [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md)
- [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- [How much acceptance does quantizing the draft or the target cost?](quantization-and-acceptance.md)

[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^drafter-evaluation-server-shapes]: My drafter evaluation report with the server-only baselines, runs of 2026-10-16
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
