---
type: Analysis
title: Quantization of the target and the draft in speculative decoding
description: What the wiki's sources say about 4-bit and 8-bit quantization in speculative decoding; a quantized target is faster but is a different model, which also shrinks the best draft budget, while a quantized draft loses only a few percent of acceptance (Q4_0 against fp16/bf16 in my runs; 4-bit QAT against BF16 in HyCo) and is much cheaper to run.
tags: [speculative-decoding, quantization, draft-model, verification, mobile-npu, on-device-inference, mobile-specedge]
question: How does heavy quantization (Q4/Q8) affect the performance of LLMs and/or draft models in speculative decoding?
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
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
  - id: drafter-evaluation-server-shapes
    resource: raw/experiments/drafter-evaluation-server-shapes.md
    title: "Drafter evaluation with server-only baselines at the SpecEdge, chain7, and tree16 shapes (§2.7, §5.5)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# Quantization of the target and the draft in speculative decoding

## Question

How does heavy quantization (Q4/Q8) affect the performance of LLMs and/or draft models in speculative decoding?

## Answer

Quantizing the target and quantizing the draft act on different parts of speculative decoding.

1. **Quantizing the target changes the model.** Speculative decoding preserves the output of the target it verifies with, so a quantized target is reproduced exactly, including any quality loss that quantization caused. AdaSPEC contrasts the two: quantization trades accuracy for speed, while speculative decoding preserves the target's predictive quality.[^huAdaSPECSelectiveKnowledge2025] The loss depends on the model. On a phone NPU, activation quantization (W4A16 against W4) raises WikiText-2 perplexity by +30.36% on Llama-3.2-1B and by +1.04% on Llama-3.2-3B.[^caiYourNPUReady2026]
2. **A quantized target is faster to verify, and that shrinks the best draft budget.** SpecExec runs Llama 2-70B with RAM offloading at 4–6 tokens per second with 4-bit quantization against 2–3 tokens per second with 16-bit weights.[^svirschevskiSpecExecMassivelyParallel2024] Quantized models take less time to load from RAM to GPU, so each target pass is cheaper.[^svirschevskiSpecExecMassivelyParallel2024] The best tree budget drops from 2048 to 128, fewer tokens are accepted per pass, and the speedup over the (also quantized) sequential baseline halves (table below). The paper states that RAM offloading works best with fewer draft tokens, and longer offloading (to SSD or with float16 weights) with larger budgets.[^svirschevskiSpecExecMassivelyParallel2024]
3. **A quantized draft loses a little acceptance.** In my runs, Q4_0 drafts accept 0.02 to 0.27 tokens per round less than bf16 or fp16 drafts of the same weights (table below).[^drafter-evaluation-server-shapes][^drafter-evaluation-server-only-chain] HyCo's on-device MTP head (W4, 86K keep set, 1K window) has 4.0% lower mean accepted tokens than the original BF16 server head.[^baeHyCoHybridDrafting2026]
4. **A quantized draft is much cheaper to run.** On a phone, quantizing the draft is what makes it run at all. HyCo fits both of its drafters to the NPU with integer quantization, a restricted vocabulary, and a 1K-token window, "at some cost in acceptance".[^baeHyCoHybridDrafting2026] Integer activations matter most for speed: 16-bit floating-point activations lengthened HyCo's SLM pass from 15.7 to 38–41 ms with no change in acceptance.[^baeHyCoHybridDrafting2026]
5. **8-bit against 4-bit.** HyCo's 8-bit MTP head keeps 98.8% top-1 agreement with BF16 without training but doubles weight storage. Its 4-bit head needs QAT to reach 91.0%.[^baeHyCoHybridDrafting2026] My phone profiling also covers Q8_0 against Q4_0 (see Evidence).

**Inference.** For a draft, Q4 seems the better trade when the draft runs on a bandwidth-bound device. Acceptance drops by a few percent, while draft time falls roughly with the number of weight bytes. No source measures acceptance at Q8 against Q4 for the same LLM draft, so this rests on HyCo's top-1 agreement and my Q4_0 against 16-bit runs.

## Evidence

### Quantized target: SpecExec, Llama 2-70B with RAM offloading, A100, OpenAssistant

Gen. rate is the average number of draft tokens accepted per target pass. The paper also quantizes the 7B draft with GPTQ when it quantizes the target.[^svirschevskiSpecExecMassivelyParallel2024]

| Draft / Target | t | Budget | Gen. rate | tok/s | Speedup |
|---|---|---|---|---|---|
| Llama 2-7B / 70B (16-bit) | 0.6 | 2048 | 20.60 | 3.12 | 18.7x |
| Llama 2-7B / 70B GPTQ | 0.6 | 128 | 12.10 | 6.02 | 8.9x |
| Llama 2-7B / 70B (16-bit) | 0 | 1024 | 18.8 | 2.74 | 16.4x |
| Llama 2-7B / 70B GPTQ | 0 | 256 | 13.43 | 6.17 | 9.1x |

All rows: [^svirschevskiSpecExecMassivelyParallel2024]

On WikiText-2 (base models) the pattern is the same: 16-bit at t=0.6 gives 1.54 tok/s (9.2x) at budget 2048, and GPTQ gives 3.72 tok/s (5.5x) at budget 256.[^svirschevskiSpecExecMassivelyParallel2024]

### Quantized draft: acceptance

| Source | Draft | Low precision | High precision | Acceptance (low / high) |
|---|---|---|---|---|
| My server-shapes run, chain7, identical outputs on 60/60[^drafter-evaluation-server-shapes] | Qwen3-0.6B | Q4_0 (phone NPU) | fp16 (GPU) | 3.11 / 3.37 tok/round |
| Same, tree16, outputs agree on 41/60[^drafter-evaluation-server-shapes] | Qwen3-0.6B | Q4_0 | fp16 | 4.06 / 4.14 tok/round |
| My offline replay, chain7[^drafter-evaluation-server-only-chain] | DFlash | Q4_0 oracle | bf16 replay | 3.42 / 3.44 tok/round |
| | DSpark | Q4_0 | bf16 | 3.86 / 3.88 |
| | EAGLE-3 | Q4_0 | bf16 | 2.80 / 2.86 |
| | PARD-1 | Q4_0 | bf16 | 2.78 / 2.90 |
| | Qwen3-0.6B | Q4_0 | bf16 | 3.11 / 3.38 |
| HyCo, paired 150 questions[^baeHyCoHybridDrafting2026] | Gemma 4 MTP head | W4, 86K keep set, 1K window, on device | BF16 server head | 4.0% lower MAT (95% CI: 3.0–4.9%) |
| HyCo, UC-val, top-1 agreement with BF16[^baeHyCoHybridDrafting2026] | Gemma 4 MTP head | 4-bit, 100 steps of QAT | — | 87.4% before QAT, 91.0% after |
| | | 8-bit, no training | — | 98.8% |

- The report on my server-only chain runs reads the gap between the bf16 replay and the Q4_0 oracle as the cost of quantization. The gap is +0.02 to +0.12 tok/round, and +0.27 for the Qwen3-0.6B autoregressive draft.[^drafter-evaluation-server-only-chain]
- **Inference.** In these runs, the small autoregressive draft loses the most to Q4_0 (about 8% of its tok/round), and the drafters that read target features (DFlash, DSpark, EAGLE-3) lose the least. The runs do not show why.
- SpecExec compares draft models by accepted tokens. The 7B draft beats JackFram/llama-160m and TinyLlama 1.1B Chat both unquantized and quantized to 4 bits with GPTQ. The unquantized 13B draft accepts slightly more, but it needs 26GB of memory.[^svirschevskiSpecExecMassivelyParallel2024] So a large 4-bit draft beats a small 16-bit one.

### Quantized draft: cost

- HyCo's drafters on the NPU: the SLM keeps its QAT checkpoint's 2/4/8-bit weights as a 754 MB graph, and the MTP head is a 123 MB graph at W4. Both use 16-bit activations and an 8-bit KV cache or 8-bit inputs on the wire.[^baeHyCoHybridDrafting2026]
- On the phone NPU, W4A16 against W4 improves decode throughput by $2.63\times$ and $2.34\times$ on Llama-3.2-1B and Llama-3.2-3B, and cuts energy per token by $53.5\%$–$66.9\%$.[^caiYourNPUReady2026]
- My own profiling on the Galaxy S25 NPU ([On-device draft cost](../experiments/npu-draft-cost-profiling-galaxy-s25.md)) finds that single-token draft latency follows the weight bytes read per token, and that Q8_0 costs 1.4 to 1.9 times Q4_0 per token at the same shape. Its data files are outside `raw/`, so these numbers carry no footnote here.

### Quantized systems in the wiki

| System | Target | Draft |
|---|---|---|
| SpecExec | Llama 2-70B in 16 bits or 4-bit GPTQ[^svirschevskiSpecExecMassivelyParallel2024] | Llama 2-7B, also GPTQ when the target is quantized[^svirschevskiSpecExecMassivelyParallel2024] |
| HyCo | Gemma 4 26B-A4B, 4-bit AWQ[^baeHyCoHybridDrafting2026] | MTP head W4 (QAT) and SLM at 2/4/8 bits[^baeHyCoHybridDrafting2026] |
| Lever | Q4_0, streamed from flash[^wangLeverSpeculativeLLM2026a] | EAGLE-3 draft, Q4_0[^wangLeverSpeculativeLLM2026a] |
| My phone evaluation | Qwen3-14B-FP8[^drafter-evaluation-server-only-chain] | Six drafters, Q4_0 on the phone NPU[^drafter-evaluation-server-shapes] |

## Caveats

- No source in the wiki varies only the bit width of the draft or the target and measures acceptance. My Q4_0 against fp16 comparison also changes where the draft runs (phone NPU against server GPU).[^drafter-evaluation-server-shapes] HyCo's paired comparison changes placement, vocabulary, and window together with the bit width, and the paper calls its server-head variant "an alternative configuration, not a placement-only ablation".[^baeHyCoHybridDrafting2026]
- SpecExec's 16-bit and GPTQ rows use different budgets, so the gen-rate gap mixes quantization with budget choice.[^svirschevskiSpecExecMassivelyParallel2024]
- Cai et al. measure activation quantization (W4 against W4A16), not 4-bit against 8-bit weights.[^caiYourNPUReady2026]
- Exactness depends on the target's numerics. My FP8 verifier gives different greedy outputs depending on the number of verified rows ([open question](../questions/fp8-verifier-tree-output-divergence.md)), so "lossless" holds only up to those numerics.[^drafter-evaluation-server-only-chain]
- See [How much acceptance does quantizing the draft or the target cost?](../questions/quantization-and-acceptance.md) for what would close these gaps.

## Related

- [Speculative decoding](../methods/speculative-decoding.md), [SpecExec](../methods/specexec.md), [HyCo](../methods/hyco.md), [Multi-token prediction](../methods/multi-token-prediction.md), [GPTQ](../methods/gptq.md), [Activation quantization](../methods/activation-quantization.md), [llama.cpp](../methods/llama-cpp.md), [Lever](../methods/lever.md)
- Papers: [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md), [HyCo](../papers/baeHyCoHybridDrafting2026.md), [Is Your NPU Ready for LLMs?](../papers/caiYourNPUReady2026.md)
- Experiments: [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md), [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md), [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)
- [Applying the speculative drafter papers to a mobile phone NPU](speculative-drafter-papers-on-mobile-npu.md), which suggests distilling the draft against the quantized target as deployed

[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^caiYourNPUReady2026]: Cai et al. 2026
[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
[^drafter-evaluation-server-shapes]: Drafter evaluation with server-only baselines, raw/experiments/drafter-evaluation-server-shapes.md
[^drafter-evaluation-server-only-chain]: Drafter evaluation, server-only chain7, raw/experiments/drafter-evaluation-server-only-chain.md
