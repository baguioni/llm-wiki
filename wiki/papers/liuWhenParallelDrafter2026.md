---
type: Paper
title: When Parallel Drafter Meets Parallel Speculative Decoding
description: DPara is a parallel speculative decoding framework that precomputes a diffusion drafter backbone for every acceptance boundary during verification, so only a lightweight autoregressive head stays on the critical path and no serial fallback occurs.
tags: [speculative-decoding, parallel-speculative-decoding, parallel-drafter, diffusion-drafter, llm-inference, scheduling]
collections: ["scheduling"]
authors: [Fuliang Liu, Xue Li, Kun Qian, Zhibin Wang, Wanchun Dou, Wenyuan Yu, Chen Tian]
doi: 10.48550/arXiv.2609.27396
arxiv: "2609.27396"
arxiv_version: 2609.27396v1
sources:
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
---

# When Parallel Drafter Meets Parallel Speculative Decoding

Text source: arXiv HTML, version `2609.27396v1`.

## Summary

Diffusion-inspired parallel drafters such as [DFlash](../methods/dflash.md) predict logits for several future positions in one forward pass, and [DSpark](../methods/dspark.md) adds a lightweight autoregressive (AR) head that restores sequence consistency.[^liuWhenParallelDrafter2026] Under the conventional sequential draft-verify schedule, drafting still sits on the critical path, where it accounts for 24%–32% of end-to-end latency.[^liuWhenParallelDrafter2026]

[Parallel speculative decoding](../methods/parallel-speculative-decoding.md) (PSD) overlaps draft generation with target verification. Existing PSD methods such as [SSD](../methods/speculative-speculative-decoding.md) must guess the accepted prefix and the bonus token in advance, and a wrong guess reverts the whole batch to serial drafting. At batch size 16, up to 96% of SSD steps fall back.[^liuWhenParallelDrafter2026]

[DPara](../methods/dpara.md) is a PSD framework that makes the overlap independent of the verification outcome. While the target verifies, the diffusion backbone precomputes draft representations for every acceptance boundary with the bonus token left unspecified. After verification, a lightweight AR head combines the revealed outcome with the matching precomputed representation to emit the next round's draft tokens.[^liuWhenParallelDrafter2026] On Qwen3-8B and Qwen3-14B across seven math, coding, and chat benchmarks, DPara achieves average speedups of 3.21× and 3.52× over autoregressive decoding.[^liuWhenParallelDrafter2026]

## Contributions

- The first parallel speculative decoding framework powered by DSpark-style parallel drafters, according to the authors.[^liuWhenParallelDrafter2026]
- DPara, which covers all acceptance boundaries without any serial backbone fallback and hides the backbone latency within the verification window, enabled by [M-DFlash](../methods/m-dflash.md), a multiple-anchor backbone finetuned from a published DSpark checkpoint.[^liuWhenParallelDrafter2026]
- An evaluation on Qwen3-8B and Qwen3-14B with speedups up to 4.53× (averaging 3.21×/3.52× over AR), sustained from batch 1 to 16, plus explorations of heterogeneous drafting and single-GPU colocation.[^liuWhenParallelDrafter2026]

## Method

### Background

- In [speculative decoding](../methods/speculative-decoding.md), a drafter proposes a block of tokens that the target scores in one forward pass. Rejection sampling keeps an accepted prefix and appends a *bonus token*: a correction sampled at the first rejection, or an extra target sample after full acceptance.[^liuWhenParallelDrafter2026]
- PEARL and AMUSD generate continuations during verification under an all-accepted assumption. SpecBranch and SSD predict likely rejection positions and bonus tokens. In all of them, an unanticipated verification outcome can invalidate the precomputed continuation and fall back to serial speculation.[^liuWhenParallelDrafter2026]

### Backbone requirement

- Under the serial schedule, DFlash anchors on a single token (the bonus, which has no target feature of its own) appended to a fully featured prefix, and predicts the logits of the next $d$ positions in one backbone forward.[^liuWhenParallelDrafter2026]
- DPara launches the backbone while the target is still verifying. At launch the backbone knows neither the number of accepted drafts $r\in\{0,\dots,d\}$ nor the new bonus $b$. The accepted prefix forms $k=r+1$ anchor tokens that have not passed through the target and so carry no target features.[^liuWhenParallelDrafter2026]
- M-DFlash (Multiple-anchor-token DFlash) extends DFlash from a single anchor to multiple feature-less anchors.[^liuWhenParallelDrafter2026]

### Finetuning DFlash to M-DFlash

- M-DFlash introduces no new trainable network parameters. It is initialized from the official DSpark checkpoint, and only the backbone is adapted.[^liuWhenParallelDrafter2026]
- Trained: the backbone blocks (attention, MLP, and their normalizations), the projection that fuses the concatenated multi-layer target features, and the input and output normalizations. Frozen: the target model, the drafter's token embedding, its full-vocabulary LM projection, the AR head, and the confidence head.[^liuWhenParallelDrafter2026]
- **Attention mask.** The previous bonus and the draft tokens form a shared, feature-less causal spine. Each anchor attends to the cached target features, itself, and earlier anchors. One group of mask tokens per possible accepted prefix attends bidirectionally within the group, reads the cached target features, and sees only its own anchor prefix. This covers all $d+1$ acceptance boundaries in one backbone forward.[^liuWhenParallelDrafter2026]
- **Loss.** The frozen AR head adds a correction from the previously sampled token, $z_{i}=\ell_{i}+WE(y_{i-1})$ with $y_{0}=b$. The loss is a position-weighted mixture of 0.1 × cross-entropy and 0.9 × full-vocabulary probability distance $\sum_{v}\lvert q_{i}(v)-p_{i}(v)\rvert$, with weights $w_{i}=e^{-(i-1)/\gamma}$ and decay $\gamma=4$. The confidence loss is disabled, so the fixed budget $d$ is never dynamically truncated.[^liuWhenParallelDrafter2026]
- **Training recipe.** One epoch with AdamW under a linear-warmup cosine schedule (learning rate 3e-5, 4% warmup), effective global batch 128, each text truncated to 4096 tokens and sampled with up to 256 prediction windows that balance all legal anchor counts. The shared training set is built from responses generated by Qwen3-8B on prompts from [Open-PerfectBlend](../datasets/perfectblend.md).[^liuWhenParallelDrafter2026]

### One DPara round (Algorithm 1)

1. The M-DFlash backbone runs on the spine $t_{0:d}$ (previous bonus plus the drafts being scored) and emits base logits for all $d+1$ acceptance boundaries. The target verifies the same token block concurrently.[^liuWhenParallelDrafter2026]
2. When verification returns $(r,b)$, DPara selects the precomputed branch $r$ and runs only the AR head to produce the next draft $y_{1:d}$.[^liuWhenParallelDrafter2026]
3. The verified features of $t_{0:r}$ are appended to the feature cache, the rejected suffix is dropped, and the bonus $b$ becomes the feature-less $t_{0}$ of the next round.[^liuWhenParallelDrafter2026]

The round time is approximated as $T_{\text{step}}\approx\max(T_{\text{verify}},T_{\text{precompute}})+T_{\text{Head}}$.[^liuWhenParallelDrafter2026]

### Resource-constrained variants

- **DPara-A10** pairs the H800 target with an NVIDIA A10 for drafting. Only the diffusion backbone runs on the A10. Verification, branch selection, the LM head, and AR-head sampling run on the H800. The A10 ships only the backbone hidden states, roughly 1/30 the size of the logits (573 KB for Qwen3-14B, ≈0.14 ms to transfer).[^liuWhenParallelDrafter2026]
- **DPara-single** runs verification and backbone precomputation on two CUDA streams of one GPU, captured in a single CUDA graph.[^liuWhenParallelDrafter2026]

## Experiments & Results

### Setup

- Target models: Qwen3-8B and Qwen3-14B.[^liuWhenParallelDrafter2026]
- Hardware: training on NVIDIA GB200 GPUs (4 GPUs, 268 GB). Main results on an NVIDIA H800 node (8 GPUs, 80 GB each). PSD methods (PEARL, SSD, DPara) use one additional GPU dedicated to drafting.[^liuWhenParallelDrafter2026]
- Datasets: [GSM8K](../datasets/gsm8k.md) and [MATH-500](../datasets/math-500.md) (math); [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), and [CodeAlpaca](../datasets/codealpaca.md) (coding); [Alpaca](../datasets/alpaca.md) and [MT-Bench](../datasets/mt-bench.md) (chat).[^liuWhenParallelDrafter2026]
- Baselines: serial SD ([EAGLE3](../methods/eagle-3.md), DFlash, DSpark, SD) and PSD (SSD, SSD-E3, [PEARL](../methods/pearl.md)). SSD-E3 uses the EAGLE3 weight of the target as draft model. SSD and PEARL on Qwen3-14B use Qwen3-0.6B as draft model.[^liuWhenParallelDrafter2026]

### Main results, greedy decoding (Table 1)

Batch size 1, greedy decoding, up to 512 new tokens, draft length 7. Each cell is speedup over AR / average acceptance length $\tau$.[^liuWhenParallelDrafter2026]

Qwen3-8B:

| Method | GSM8K | MATH-500 | HumanEval | MBPP | CodeAlpaca | Alpaca | MT-Bench | Avg. |
|---|---|---|---|---|---|---|---|---|
| SSD-E3 | 1.51× / 2.39 | 1.54× / 2.42 | 1.72× / 2.75 | 1.58× / 2.49 | 1.67× / 2.62 | 1.29× / 2.17 | 1.34× / 2.26 | 1.52× / 2.44 |
| EAGLE3 | 1.44× / 2.83 | 1.46× / 2.84 | 1.67× / 3.26 | 1.51× / 2.98 | 1.58× / 3.18 | 1.18× / 2.45 | 1.27× / 2.57 | 1.44× / 2.87 |
| DFlash | 3.38× / 6.08 | 3.28× / 5.88 | 2.93× / 5.25 | 2.80× / 4.95 | 2.77× / 4.95 | 1.81× / 3.28 | 1.94× / 3.56 | 2.70× / 4.85 |
| DSpark | 3.48× / 6.51 | 3.46× / 6.39 | 3.15× / 5.82 | 3.00× / 5.51 | 3.01× / 5.55 | 2.00× / 3.72 | 2.13× / 4.01 | 2.89× / 5.36 |
| DPara | 4.17× / 5.82 | 3.95× / 5.41 | 3.50× / 4.78 | 3.27× / 4.48 | 3.25× / 4.47 | 2.10× / 2.92 | 2.25× / 3.12 | 3.21× / 4.43 |

Qwen3-14B:

| Method | GSM8K | MATH-500 | HumanEval | MBPP | CodeAlpaca | Alpaca | MT-Bench | Avg. |
|---|---|---|---|---|---|---|---|---|
| SSD | 2.70× / 5.47 | 2.80× / 5.63 | 2.36× / 4.87 | 2.18× / 4.47 | 2.05× / 4.39 | 1.39× / 3.17 | 1.51× / 3.47 | 2.14× / 4.50 |
| SSD-E3 | 1.76× / 2.48 | 1.80× / 2.48 | 2.02× / 2.80 | 1.82× / 2.54 | 1.91× / 2.68 | 1.48× / 2.17 | 1.57× / 2.28 | 1.77× / 2.49 |
| PEARL | 3.35× / 3.70 | 3.58× / 3.85 | 2.95× / 3.18 | 2.47× / 2.81 | 2.58× / 2.81 | 1.84× / 1.98 | 2.03× / 2.20 | 2.68× / 2.93 |
| SD | 2.21× / 5.47 | 2.28× / 5.65 | 1.99× / 4.86 | 1.85× / 4.46 | 1.76× / 4.39 | 1.31× / 3.17 | 1.42× / 3.47 | 1.83× / 4.50 |
| EAGLE3 | 1.76× / 2.94 | 1.74× / 2.93 | 2.01× / 3.35 | 1.80× / 3.04 | 1.86× / 3.24 | 1.42× / 2.42 | 1.51× / 2.57 | 1.73× / 2.93 |
| DFlash | 3.86× / 6.03 | 3.76× / 5.92 | 3.36× / 5.20 | 3.16× / 4.89 | 3.13× / 4.97 | 2.07× / 3.24 | 2.25× / 3.55 | 3.08× / 4.83 |
| DSpark | 4.07× / 6.53 | 4.01× / 6.39 | 3.66× / 5.79 | 3.46× / 5.48 | 3.45× / 5.60 | 2.32× / 3.71 | 2.50× / 4.02 | 3.35× / 5.36 |
| DPara | 4.53× / 5.73 | 4.32× / 5.37 | 3.84× / 4.76 | 3.58× / 4.45 | 3.49× / 4.46 | 2.32× / 2.91 | 2.53× / 3.16 | 3.52× / 4.41 |

All rows: [^liuWhenParallelDrafter2026]

- DPara has the highest speedup on every model-dataset pair, with a tie with DSpark on Qwen3-14B Alpaca.[^liuWhenParallelDrafter2026]
- On Qwen3-14B, DPara improves the average speedup over PEARL and SSD by 31% and 64%.[^liuWhenParallelDrafter2026]
- DPara improves average speedup over DSpark by 11.1% on Qwen3-8B and 5.1% on Qwen3-14B, although its average acceptance length (4.43 and 4.41) is below DSpark's 5.36.[^liuWhenParallelDrafter2026]
- Figure 1 (Qwen3-14B, $b{=}1$): DPara reaches an arithmetic mean of 3.62× across the four benchmarks shown.[^liuWhenParallelDrafter2026]

### Batched inference (Table 2)

Throughput in tok/s, with speedup over AR in parentheses.[^liuWhenParallelDrafter2026]

| Model | Task | Method | b=1 | b=2 | b=4 | b=8 | b=16 |
|---|---|---|---|---|---|---|---|
| Qwen3-8B | GSM8K | AR | 141 | 277 | 529 | 937 | 1520 |
| Qwen3-8B | GSM8K | DSpark | 491 (3.48×) | 901 (3.25×) | 1507 (2.85×) | 2426 (2.59×) | 3627 (2.39×) |
| Qwen3-8B | GSM8K | DPara | 588 (4.17×) | 1052 (3.80×) | 1772 (3.35×) | 2736 (2.92×) | 3869 (2.55×) |
| Qwen3-8B | HumanEval | AR | 141 | 269 | 532 | 957 | 1684 |
| Qwen3-8B | HumanEval | DSpark | 445 (3.15×) | 815 (3.02×) | 1464 (2.75×) | 2283 (2.39×) | 3382 (2.01×) |
| Qwen3-8B | HumanEval | DPara | 495 (3.50×) | 914 (3.39×) | 1565 (2.94×) | 2567 (2.68×) | 3654 (2.17×) |
| Qwen3-14B | GSM8K | AR | 87 | 171 | 330 | 597 | 1020 |
| Qwen3-14B | GSM8K | DSpark | 355 (4.07×) | 647 (3.79×) | 1142 (3.47×) | 1813 (3.03×) | 2847 (2.79×) |
| Qwen3-14B | GSM8K | DPara | 395 (4.53×) | 721 (4.22×) | 1269 (3.85×) | 1999 (3.35×) | 3010 (2.95×) |
| Qwen3-14B | HumanEval | AR | 87 | 170 | 333 | 622 | 1080 |
| Qwen3-14B | HumanEval | DSpark | 319 (3.66×) | 598 (3.52×) | 1082 (3.25×) | 1688 (2.71×) | 2523 (2.34×) |
| Qwen3-14B | HumanEval | DPara | 335 (3.84×) | 634 (3.74×) | 1140 (3.42×) | 1824 (2.93×) | 2724 (2.52×) |

All rows: [^liuWhenParallelDrafter2026]

- At batch size 16, DPara's throughput exceeds DSpark's by approximately 6%–8% across these four settings.[^liuWhenParallelDrafter2026]
- Batching reduces the relative benefit of speculation: speedup over the correspondingly batched AR baseline declines for both methods.[^liuWhenParallelDrafter2026]

### Sampling (Table 3)

Batch size 1, temperature 1.0 for both the target and the drafter, top-$p$ 1.0, up to 512 new tokens, draft length 7, 80 requests per benchmark. Each cell is speedup over AR / $\tau$.[^liuWhenParallelDrafter2026]

| Model | Method | GSM8K | MATH-500 | HumanEval | MBPP | CodeAlpaca | Alpaca | MT-Bench | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B | DFlash | 2.71× / 5.28 | 2.66× / 5.15 | 2.39× / 4.64 | 2.31× / 4.47 | 2.30× / 4.46 | 1.56× / 2.98 | 1.65× / 3.18 | 2.23× / 4.31 |
| Qwen3-8B | DSpark | 3.06× / 6.15 | 3.00× / 5.96 | 2.78× / 5.53 | 2.64× / 5.24 | 2.63× / 5.22 | 1.80× / 3.54 | 1.89× / 3.74 | 2.54× / 5.05 |
| Qwen3-8B | DPara | 3.45× / 5.29 | 3.17× / 4.77 | 2.95× / 4.46 | 2.83× / 4.28 | 2.77× / 4.20 | 1.89× / 2.81 | 1.97× / 2.93 | 2.72× / 4.11 |
| Qwen3-14B | DFlash | 3.29× / 5.35 | 3.13× / 5.04 | 2.86× / 4.61 | 2.76× / 4.53 | 2.73× / 4.45 | 1.85× / 2.96 | 1.94× / 3.19 | 2.65× / 4.30 |
| Qwen3-14B | DSpark | 3.74× / 6.18 | 3.61× / 5.91 | 3.33× / 5.46 | 3.13× / 5.25 | 3.15× / 5.17 | 2.16× / 3.54 | 2.26× / 3.79 | 3.05× / 5.04 |
| Qwen3-14B | DPara | 4.00× / 5.31 | 3.74× / 4.88 | 3.38× / 4.39 | 3.14× / 4.17 | 3.16× / 4.15 | 2.18× / 2.79 | 2.28× / 2.93 | 3.13× / 4.09 |

All rows: [^liuWhenParallelDrafter2026]

### Latency breakdown (Appendix A; Qwen3-14B, GSM8K, H800)

| Method | Step latency, batch 1 | On the critical path besides verification | Step latency, batch 16 |
|---|---|---|---|
| DFlash | 17.3 ms | 4.1 ms (24%) | not stated |
| DSpark | 17.7 ms | 4.4 ms (25%): backbone 2.7 ms, AR head 0.3 ms, context bookkeeping 1.4 ms | 23.3 ms (+32%) |
| DPara | 13.8 ms | 1.3 ms (10%) on top of a 12.5 ms verify | 18.0 ms (+30%) |
| DPara-A10 | 14.3 ms | target-side LM head 0.3 ms; A10 backbone 7.3 ms and hidden-state push 1.5 ms fit in the verification window | not stated |
| DPara-single | 15.1 ms | not stated | not stated |

All rows: [^liuWhenParallelDrafter2026]

- DPara's 13.8 ms step is 1.21× the AR per-token forward.[^liuWhenParallelDrafter2026]
- DSpark's step stays 28%–30% longer than DPara's at every batch size. At batch size 1, DSpark's higher $\tau$ (6.5 vs. 5.7) does not offset its longer step (2.71 vs. 2.41 ms per token).[^liuWhenParallelDrafter2026]

### SSD fallback rate (Appendix B; Qwen3-14B, seven benchmarks)

- At batch size 1, 8%–32% of SSD steps fall back. At batch size 16 the rate reaches 57%–96%.[^liuWhenParallelDrafter2026]
- A per-request bonus-mismatch probability $p$ becomes a per-step fallback probability $1-(1-p)^{B}$ for a batch of $B$ requests.[^liuWhenParallelDrafter2026]
- Chat workloads have the highest rate: 29%–32% at batch 1 and 91%–96% at batch 16. Math workloads fall back in 8% of steps at batch 1 and over half of all steps at batch 16.[^liuWhenParallelDrafter2026]
- DPara records no such events at any batch size.[^liuWhenParallelDrafter2026]

### Resource-constrained drafting

- DPara-A10 retains about 98% of DPara's speedup on all four benchmarks shown while cutting the drafting-device cost by ∼90%. Averaged over all seven benchmarks it reaches 3.14× on Qwen3-8B and 3.43× on Qwen3-14B, versus 3.21× and 3.52× for DPara.[^liuWhenParallelDrafter2026]
- DPara-single on Qwen3-8B with GB200 reaches 2.62× speedup over AR at batch size 1, compared with 2.34× for DSpark and 2.77× for DPara. It retains 90%–95% of DPara's speedup across batch sizes 1–4 while halving the GPU count.[^liuWhenParallelDrafter2026]

### Ablation: backbone finetuning (Qwen3-8B, DPara with the same frozen AR head)

| Dataset | $\tau$ with original DSpark checkpoint | $\tau$ with M-DFlash | Relative gain |
|---|---|---|---|
| GSM8K | 4.07 | 5.82 | 43.1% |
| MATH-500 | 4.06 | 5.41 | 33.3% |
| HumanEval | 3.81 | 4.78 | 25.5% |
| Alpaca | 2.55 | 2.92 | 14.4% |
| Mean of the four | 3.62 | 4.73 | 30.7% |

All rows: [^liuWhenParallelDrafter2026]

## Limitations

- DPara's acceptance length is lower than DSpark's (4.43 and 4.41 versus 5.36). The paper attributes this to the information constraints of PSD: the backbone starts without the accepted length, the new bonus, or fresh target features for the carried-over draft tokens.[^liuWhenParallelDrafter2026]
- The default DPara uses one additional GPU dedicated to drafting.[^liuWhenParallelDrafter2026]
- Speedup over the batched AR baseline declines as batch size grows; outcome-independent overlap does not imply batch-invariant speedup.[^liuWhenParallelDrafter2026]
- DPara-single's advantage over DSpark disappears at batch sizes 8 and 16, where the colocated backbone competes with the target for execution resources and bandwidth.[^liuWhenParallelDrafter2026]
- Evaluation covers two target models from one family (Qwen3-8B and Qwen3-14B). The Qwen3-8B block of Table 1 has no SSD (Qwen3-0.6B drafter) or PEARL rows, and the sampling comparison (Table 3) includes only serial baselines.[^liuWhenParallelDrafter2026]
- The paper has no dedicated limitations section.

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [Parallel speculative decoding](../methods/parallel-speculative-decoding.md), [DPara](../methods/dpara.md), [M-DFlash](../methods/m-dflash.md)
- Methods compared or built on: [DSpark](../methods/dspark.md), [DFlash](../methods/dflash.md), [EAGLE-3](../methods/eagle-3.md), [SSD](../methods/speculative-speculative-decoding.md), [PEARL](../methods/pearl.md)
- Datasets: [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md), [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [CodeAlpaca](../datasets/codealpaca.md), [Alpaca](../datasets/alpaca.md), [MT-Bench](../datasets/mt-bench.md), [Open-PerfectBlend](../datasets/perfectblend.md)
- Papers in this wiki cited by this paper: [DSpark](chengDSparkConfidenceScheduledSpeculative2026.md), [DFlash](chenDFlashBlockDiffusion2026.md), [Speculative Speculative Decoding](kumarSpeculativeSpeculativeDecoding2026.md), [EAGLE-3](liEAGLE3ScalingInference2025.md)

[^liuWhenParallelDrafter2026]: Liu et al. 2026
