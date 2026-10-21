---
type: Open Question
title: How much acceptance does quantizing the draft or the target cost?
description: No source in the wiki varies only the bit width (4-bit, 8-bit, 16-bit) of the draft or the target and measures acceptance and speedup; the comparisons that exist also change placement, budget, vocabulary, or activation format.
tags: [speculative-decoding, quantization, draft-model, verification, mobile-npu, mobile-specedge]
sources:
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
  - id: drafter-evaluation-server-shapes
    resource: raw/experiments/drafter-evaluation-server-shapes.md
    title: "Drafter evaluation with server-only baselines at the SpecEdge, chain7, and tree16 shapes (§2.7, §5.5)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# How much acceptance does quantizing the draft or the target cost?

## Question

For a fixed draft and target pair, how do acceptance length and wall-clock speedup change when the draft, the target, or both are quantized to 8 or 4 bits? Does a draft trained against the full-precision target lose more acceptance against a quantized target?

## Why it matters

- A phone drafter must be quantized to run on the NPU. HyCo fits its drafters to the NPU with integer quantization "at some cost in acceptance".[^baeHyCoHybridDrafting2026] My phone drafters all run as Q4_0.[^drafter-evaluation-server-shapes]
- The choice between Q8 and Q4 sets both draft time and acceptance, and the wiki has numbers only for the cost side.

## Evidence so far

- My Qwen3-0.6B draft accepts 3.11 tok/round as Q4_0 on the phone NPU against 3.37 as fp16 on the server GPU in chain7, with identical outputs. In tree16 it is 4.06 against 4.14.[^drafter-evaluation-server-shapes]
- In my offline chain7 replays, bf16 drafts sit +0.02 to +0.12 tok/round above the Q4_0 oracle, and the Qwen3-0.6B draft +0.27.[^drafter-evaluation-server-only-chain]
- HyCo's on-device MTP head (W4, 86K keep set, 1K window) has 4.0% lower MAT than the original BF16 server head (95% CI: 3.0–4.9%). Top-1 agreement with BF16 is 87.4% for the 4-bit head, 91.0% after 100 steps of QAT, and 98.8% for 8-bit weights without training.[^baeHyCoHybridDrafting2026]
- SpecExec's 7B draft beats smaller drafts in accepted tokens both unquantized and with 4-bit GPTQ, but the paper reports the comparison only as a figure.[^svirschevskiSpecExecMassivelyParallel2024] Its 16-bit and GPTQ targets are run at different budgets (gen. rate 20.60 at budget 2048 against 12.10 at budget 128, OpenAssistant, t=0.6).[^svirschevskiSpecExecMassivelyParallel2024]
- On a phone NPU, activation quantization raises WikiText-2 perplexity by +30.36% on Llama-3.2-1B and +1.04% on Llama-3.2-3B, so a quantized target's quality cost depends on the model.[^caiYourNPUReady2026]

## Conflicting claims

None. The sources do not disagree; each comparison changes something besides bit width.

- My Q4_0 against fp16 runs also move the draft from the phone NPU to the server GPU.[^drafter-evaluation-server-shapes]
- HyCo's paired comparison also changes placement, vocabulary, and window.[^baeHyCoHybridDrafting2026]
- SpecExec's comparison also changes the budget.[^svirschevskiSpecExecMassivelyParallel2024]

## What would resolve it

- Replay each of my six drafters offline at Q4_0, Q8_0, and bf16 against the same recorded Qwen3-14B targets, which separates precision from placement. The server-only report already gives the bf16 and Q4_0 points for chain7.[^drafter-evaluation-server-only-chain]
- Run the server-only draft in Q4_0, or the phone draft in fp16 (already listed as a next step in [my phone evaluation](../experiments/drafter-evaluation-qwen3-14b.md)).
- Verify the same drafter against a bf16 target and a 4-bit target, and test whether distilling the draft against the quantized target recovers acceptance.

## Related

- [Quantization of the target and the draft in speculative decoding](../analyses/quantization-in-speculative-decoding.md)
- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md), [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md), [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)
- [Why do tree-verified outputs diverge from chain outputs at temperature 0?](fp8-verifier-tree-output-divergence.md)
- [Does speculative decoding help on a mobile NPU?](speculative-decoding-on-mobile-npu.md)
- [SpecExec](../methods/specexec.md), [HyCo](../methods/hyco.md), [Speculative decoding](../methods/speculative-decoding.md)

[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^caiYourNPUReady2026]: Cai et al. 2026
[^drafter-evaluation-server-shapes]: Drafter evaluation with server-only baselines, raw/experiments/drafter-evaluation-server-shapes.md
[^drafter-evaluation-server-only-chain]: Drafter evaluation, server-only chain7, raw/experiments/drafter-evaluation-server-only-chain.md
