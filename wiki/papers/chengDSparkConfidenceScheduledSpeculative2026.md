---
type: Paper
title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
description: Speculative decoding framework that adds a lightweight sequential head to a parallel drafter and schedules per-request verification length from calibrated confidence and engine load, deployed in the DeepSeek-V4 serving system.
tags: [speculative-decoding, semi-autoregressive, parallel-drafting, confidence-estimation, verification-scheduling, llm-serving, mobile-specedge]
collections: ["mobile-specedge"]
authors: [Xin Cheng, Xingkai Yu, Chenze Shao, Jiashi Li, Yunfan Xiong, Yi Qian, Jiaqi Zhu, Shirong Ma, Xiaokang Zhang, Jiasheng Ye, Qinyu Chen, Chengqi Deng, Jiping Yu, Damai Dai, Zhengyan Zhang, Yixuan Wei, Yixuan Tan, Wenkai Yang, Runxin Xu, Yu Wu, Zhean Xu, Xuanyu Wang, Muyang Chen, Rui Tian, Xiao Bi, Zhewen Hao, Shaoyuan Chen, Huanqi Cao, Wentao Zhang, Anyi Xu, Huishuai Zhang, Dongyan Zhao, Wenfeng Liang]
doi: 10.48550/arXiv.2607.05147
arxiv: "2607.05147"
arxiv_version: 2607.05147v1
code: https://github.com/deepseek-ai/DeepSpec
sources:
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
---

# DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation

Text source: arXiv HTML, version `2607.05147v1`.

## Summary

Parallel drafters for [speculative decoding](../methods/speculative-decoding.md) produce a long draft block in one forward pass, but they predict each position independently, so acceptance decays rapidly at later positions. Verifying the whole block also wastes batch capacity on tokens that are likely to be rejected, which hurts throughput under high concurrency.[^chengDSparkConfidenceScheduledSpeculative2026]

[DSpark](../methods/dspark.md) addresses both problems. A [semi-autoregressive](../methods/semi-autoregressive-generation.md) drafter couples a parallel backbone ([DFlash](../methods/dflash.md) in the paper's instantiation) with a lightweight sequential head that models dependencies inside the block. [Confidence-scheduled verification](../methods/confidence-scheduled-verification.md) then sets the verification length of each request from estimated prefix survival probabilities and a profiled engine throughput curve.[^chengDSparkConfidenceScheduledSpeculative2026]

Offline, on Qwen3-4B, 8B, and 14B, DSpark improves the macro-average accepted length over Eagle3 by 30.9%, 26.7%, and 30.0%, and over DFlash by 16.3%, 18.4%, and 18.3%.[^chengDSparkConfidenceScheduledSpeculative2026] Deployed in the DeepSeek-V4 serving system under live user traffic, DSpark accelerates per-user generation speed over the MTP-1 production baseline by 60%–85% (V4-Flash) and 57%–78% (V4-Pro) at matched aggregate throughput.[^chengDSparkConfidenceScheduledSpeculative2026]

## Contributions

- A semi-autoregressive drafter: a fully parallel backbone plus a lightweight serial output head (Markov or RNN) that injects local transition information.[^chengDSparkConfidenceScheduledSpeculative2026]
- A confidence head that estimates per-position prefix survival probabilities, calibrated post hoc with Sequential Temperature Scaling (STS).[^chengDSparkConfidenceScheduledSpeculative2026]
- A hardware-aware prefix scheduler that formulates verification length selection as a global throughput maximization problem and solves it greedily while preserving losslessness.[^chengDSparkConfidenceScheduledSpeculative2026]
- A position-wise conditional acceptance analysis that explains why parallel drafters can beat autoregressive ones.[^chengDSparkConfidenceScheduledSpeculative2026]
- A production deployment in DeepSeek-V4 with results under live traffic.[^chengDSparkConfidenceScheduledSpeculative2026]
- Open-source release of DSpark checkpoints for DeepSeek-V4-Flash (preview) and DeepSeek-V4-Pro (preview), and of DeepSpec, a training repository that includes Eagle3, DFlash, and DSpark.[^chengDSparkConfidenceScheduledSpeculative2026]

## Method

Per-token latency is $L=\frac{T_{\text{draft}}+T_{\text{verify}}}{\tau}$ (Eq. 1). The paper names three levers: lower $T_{\text{draft}}$ (draft faster), raise $\tau$ (draft better), or reduce the effective $T_{\text{verify}}$ (verify smarter).[^chengDSparkConfidenceScheduledSpeculative2026]

### Semi-autoregressive generation

- **Parallel stage.** The backbone runs one forward pass over the block and produces hidden states $h_{1},\ldots,h_{\gamma}$ and base logits $U_{1},\ldots,U_{\gamma}$. It keeps DFlash's [KV injection](../methods/kv-injection.md) of target context features. One change from DFlash: the anchor itself is the first prediction position, so $\gamma$ input tokens (anchor $+$ $\gamma{-}1$ masks) yield $\gamma$ draft logits.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Sequential stage.** A prefix-dependent transition bias $B_{k}$ is added to the base logits, giving the causal factorization $p_{k}(v\mid x_{0},x_{<k})=\frac{\exp\left(U_{k}(v)+B_{k}(x_{0},x_{<k},v)\right)}{\sum_{u\in\mathcal{V}}\exp\left(U_{k}(u)+B_{k}(x_{0},x_{<k},u)\right)}$ (Eq. 4). Sampling runs left to right, so the block must satisfy $T_{\text{sequential}}\ll T_{\text{parallel}}$.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Markov head.** $B_{k}$ depends only on the preceding token. The $V\times V$ transition matrix is approximated as $B=W_{1}W_{2}$ with $W_{1}\in\mathbb{R}^{V\times r}$, $W_{2}\in\mathbb{R}^{r\times V}$, and $r{=}256$ by default.[^chengDSparkConfidenceScheduledSpeculative2026]
- **RNN head.** A recurrent state $s_{k}$ accumulates the full prefix history in the block. The input is $z_{k}=[s_{k-1};\,W_{1}[x_{k-1}];\,h_{k}]\in\mathbb{R}^{2r+d}$, followed by a single gated update. $s_{0}$ is zero.[^chengDSparkConfidenceScheduledSpeculative2026]
- Per-token probabilities remain exact softmax evaluations because the sequential correction is local. The paper contrasts this with CRF-NAT and CTC-drafter.[^chengDSparkConfidenceScheduledSpeculative2026]

### Confidence head and calibration

- $c_{k}=\sigma\bigl(w^{\top}[h_{k};\,W_{1}[x_{k-1}]]\bigr)$ (Eq. 7) models the probability that the draft token at position $k$ survives verification given that all preceding tokens in the block were accepted.[^chengDSparkConfidenceScheduledSpeculative2026]
- It is supervised with the analytical per-step acceptance rate $c_{k}^{*}=1-\tfrac{1}{2}\|p_{k}^{d}-p_{k}^{t}\|_{1}$ (Eq. 8).[^chengDSparkConfidenceScheduledSpeculative2026]
- **Sequential Temperature Scaling.** On a held-out validation set, for each position $k$ from left to right, a 1D grid search finds the temperature that minimizes the Expected Calibration Error (ECE) of the cumulative product $\prod_{i\leqslant k}c_{i}$, with earlier positions fixed. Temperature scaling preserves the ranking of draft tokens.[^chengDSparkConfidenceScheduledSpeculative2026]

### Hardware-aware prefix scheduler (Algorithm 1)

- For $R$ active requests, the prefix survival probability is $a_{r,j}=\prod_{i\leqslant j}c_{r,i}$. The verification batch size in tokens is $B=\sum_{r=1}^{R}(1+\ell_{r})$ and the expected accepted tokens are $\tau=\sum_{r=1}^{R}\bigl(1+\sum_{j=1}^{\ell_{r}}a_{r,j}\bigr)$.[^chengDSparkConfidenceScheduledSpeculative2026]
- $\text{SPS}(B)$ is engine throughput in steps per second for forward-pass batch size $B$, profiled once at engine initialization and stored as a cost table. The scheduler maximizes $\Theta=\tau\cdot\text{SPS}(B)$.[^chengDSparkConfidenceScheduledSpeculative2026]
- Greedy solution: sort all candidates $(r,j)$ by $a_{r,j}$ in descending order, admit them one at a time, and stop at the first step where $\Theta$ does not improve.[^chengDSparkConfidenceScheduledSpeculative2026]
- The early stop keeps the scheduler non-anticipating, which lossless speculative decoding requires. Appendix A gives a counterexample: without the break, the output distribution becomes $(0.85,0.15)$ where the target distribution is $(0.7,0.3)$.[^chengDSparkConfidenceScheduledSpeculative2026]
- The early stop reaches the global maximum if and only if $\Theta$ is unimodal.[^chengDSparkConfidenceScheduledSpeculative2026]

### Training

- Multiple anchor positions are sampled from each target sequence to form $\gamma$-token blocks. The target is frozen. The drafter shares the target's embedding layer and LM head, both frozen, and updates only the backbone drafter, sequential block, and confidence head.[^chengDSparkConfidenceScheduledSpeculative2026]
- Loss: $\mathcal{L}=\alpha_{\text{ce}}\,\mathcal{L}_{\text{ce}}+\alpha_{\text{tv}}\,\mathcal{L}_{\text{tv}}+\alpha_{\text{conf}}\,\mathcal{L}_{\text{conf}}$ with defaults $\alpha_{\text{ce}}=0.1$, $\alpha_{\text{tv}}=0.9$, $\alpha_{\text{conf}}=1.0$. $\mathcal{L}_{\text{tv}}$ penalizes the total variation distance between draft and target distributions, and $\mathcal{L}_{\text{conf}}$ is a binary cross-entropy on $c_{k}^{*}$. All three terms are position-weighted by $w_{k}=\exp(-(k{-}1)/\gamma)$.[^chengDSparkConfidenceScheduledSpeculative2026]

### Production adaptations

- **Drafter in production.** Three MoE layers with mHC and a sliding window attention of 128, maximum block size $\gamma=5$, Markov head, confidence head calibrated with STS.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Training optimizations.** Hidden state communication sends only the hidden states before the LM head instead of full-vocabulary logits ($V\approx 10^{5}$), which reduces per-token communication complexity to $O(d)$. Anchor-bounded sequence packing samples a fixed number of anchors and packs the blocks into dense batches using token-level attention indices.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Asynchronous scheduler.** The real $\text{SPS}(B)$ curve is jagged and step-wise, and per-step dynamic scheduling clashes with CUDA graph replay and Zero-Overhead Scheduling (ZOS). In production the batch capacity limit $K$ is set from confidence outputs of two steps prior, and current candidates are still sorted by their up-to-date cumulative confidence, a dynamic top-$K$ selection.[^chengDSparkConfidenceScheduledSpeculative2026]
- **No early stop in production.** The break is removed to allow a global search across SPS cliffs. The paper argues this stays lossless because the truncation length depends only on information from two steps prior.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Variable-length verification.** All tokens across requests are flattened and processed as independent elements, with intra-sequence dependencies conveyed by a marker tensor in the sparse attention implementation. On DeepSeek-V4 only the index-attention and compress kernels needed modification.[^chengDSparkConfidenceScheduledSpeculative2026]

## Experiments & Results

### Setup

- Targets: Qwen3-{4B, 8B, 14B} and Gemma4-12B.[^chengDSparkConfidenceScheduledSpeculative2026]
- Drafters compared: DFlash (parallel) and [Eagle3](../methods/eagle-3.md) (autoregressive). All drafters are retrained in the same training framework on the same data. Eagle3's TTT horizon (7) is aligned with the block size (7) of DFlash and DSpark, and all use the same target feature layers. Eagle3 has 1 draft layer. DSpark and DFlash have 5.[^chengDSparkConfidenceScheduledSpeculative2026]
- Training data: prompts from Open-PerfectBlend, 1.3 million samples: chat (17.6%), math (39.4%), code (38.9%), instruction-following (4.1%). Responses are regenerated by each target model. Each drafter is trained for 10 epochs. Non-thinking mode.[^chengDSparkConfidenceScheduledSpeculative2026]
- Benchmarks. Math: [GSM8K](../datasets/gsm8k.md), [MATH500](../datasets/math-500.md), AIME25. Code: [MBPP](../datasets/mbpp.md), [HumanEval](../datasets/humaneval.md), [LiveCodeBench](../datasets/livecodebench.md). Chat: [MT-Bench](../datasets/mt-bench.md), [Alpaca](../datasets/alpaca.md), Arena-Hard.[^chengDSparkConfidenceScheduledSpeculative2026]
- Protocol: standard speculative decoding, sampling temperature $1.0$, chain-based drafting for all drafters. The metric is accepted length $\tau$ per decoding round, including the bonus token. The confidence scheduler is disabled offline, so every drafter proposes a fixed block.[^chengDSparkConfidenceScheduledSpeculative2026]
- DSpark means the Markov-head variant unless stated.[^chengDSparkConfidenceScheduledSpeculative2026]

### Accepted length (Table 1)

| Target | Drafter | GSM8K | MATH | AIME25 | MBPP | HumanEval | LCB | MT-Bench | Alpaca | Arena-Hard |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-4B | Eagle3 | 5.14 | 4.62 | 3.92 | 3.69 | 4.16 | 3.77 | 2.39 | 2.26 | 2.55 |
| Qwen3-4B | DFlash | 5.40 | 4.85 | 4.15 | 4.40 | 4.74 | 4.18 | 3.07 | 2.96 | 2.83 |
| Qwen3-4B | DSpark | 6.11 | 5.70 | 4.89 | 5.13 | 5.38 | 4.86 | 3.64 | 3.54 | 3.29 |
| Qwen3-8B | Eagle3 | 5.30 | 4.77 | 3.91 | 3.96 | 4.33 | 4.17 | 2.66 | 2.54 | 2.54 |
| Qwen3-8B | DFlash | 5.33 | 4.91 | 4.07 | 4.36 | 4.64 | 4.39 | 3.11 | 2.98 | 2.81 |
| Qwen3-8B | DSpark | 6.17 | 5.78 | 5.01 | 5.16 | 5.52 | 5.17 | 3.72 | 3.58 | 3.21 |
| Qwen3-14B | Eagle3 | 5.24 | 4.60 | 3.71 | 3.81 | 4.14 | 4.01 | 2.62 | 2.47 | 2.48 |
| Qwen3-14B | DFlash | 5.41 | 4.84 | 3.98 | 4.44 | 4.59 | 4.33 | 3.10 | 2.94 | 2.72 |
| Qwen3-14B | DSpark | 6.21 | 5.74 | 4.94 | 5.26 | 5.43 | 5.02 | 3.70 | 3.58 | 3.13 |
| Gemma4-12B | Eagle3 | 5.87 | 5.46 | 4.83 | 4.72 | 5.37 | 4.16 | 3.19 | 3.06 | 2.72 |
| Gemma4-12B | DFlash | 5.45 | 5.04 | 4.22 | 4.39 | 4.95 | 3.70 | 2.98 | 2.84 | 2.59 |
| Gemma4-12B | DSpark | 6.05 | 5.78 | 5.12 | 5.11 | 5.64 | 4.51 | 3.49 | 3.35 | 2.92 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

- DSpark has the highest accepted length in every cell.[^chengDSparkConfidenceScheduledSpeculative2026]
- On Gemma4-12B, Eagle3 is above DFlash in every column of the table.[^chengDSparkConfidenceScheduledSpeculative2026]
- Domain effect for DSpark on Qwen3-4B: 5.57 on math, 5.12 on code, 3.49 on chat.[^chengDSparkConfidenceScheduledSpeculative2026]

### Position-wise conditional acceptance (Qwen3-4B, Figure 2)

The metric is the acceptance rate at position $k$ over only those rounds where positions $1$ to $k-1$ were all accepted.[^chengDSparkConfidenceScheduledSpeculative2026]

| Observation | Values stated in the text |
|---|---|
| Position 1, DFlash vs. Eagle3 | 0.88 vs. 0.81 on Math; 0.72 vs. 0.53 on Chat |
| Eagle3 along the block | from 0.53 to 0.74 on Chat |
| DFlash along the block | from 0.87 to 0.78 on Code; 0.72 to 0.63 on Chat |
| DSpark at position 1 | 0.93 on Math |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

The paper's explanation: an autoregressive drafter is limited to a shallow network by its $O(\gamma)$ latency, while an $O(1)$ parallel drafter can be deeper and so is more accurate at position 1, which has the highest leverage because a rejection there invalidates the whole block. At later positions the parallel drafter suffers multi-modal collision.[^chengDSparkConfidenceScheduledSpeculative2026]

### Depth, proposal length, and latency (Qwen3-4B, Figures 3 and 4)

- With block size 7 and 1 to 5 DSpark layers, accepted length improves monotonically with depth, with the steepest gain from one to two layers. A 2-layer DSpark outperforms the 5-layer DFlash baseline across all domains.[^chengDSparkConfidenceScheduledSpeculative2026]
- With 5 layers and draft length (proposal length $\gamma$ plus one anchor token) in $\{4,8,12,16\}$, DSpark outperforms DFlash at every length and the gap widens with $\gamma$.[^chengDSparkConfidenceScheduledSpeculative2026]

| Proposal length | Gain in accepted length over DFlash: math | code | chat |
|---|---|---|---|
| $\gamma=7$ | 16% | 15% | 18% |
| $\gamma=15$ | 30% | 26% | 22% |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

- The RNN head gives only marginal gains over the Markov head, mainly at longer proposal lengths, so the Markov head is the default.[^chengDSparkConfidenceScheduledSpeculative2026]
- Per-round engine latency (one target verification pass, the parallel draft forward, and the serial sampling loop) at batch size 128, averaged over context lengths $\{512,1024,2048,4096\}$ tokens: scaling the draft length from 4 to 16 adds 0.2% to 1.3% to the full-round latency over the DFlash baseline.[^chengDSparkConfidenceScheduledSpeculative2026]

### Confidence head (Qwen3-4B, Figures 5 and 6)

Static confidence threshold sweep. A threshold of 0 is fixed-length verification.[^chengDSparkConfidenceScheduledSpeculative2026]

| Domain | Acceptance rate, from → to as the threshold rises |
|---|---|
| Chat | 45.7% → 95.7% |
| Math | 76.9% → 92.5% |
| Code | 67.6% → 92.0% |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

The raw confidence model has ROC-AUC from 0.81 to 0.90 and ECE of 3%–8%. STS reduces the average ECE to $\sim$1%.[^chengDSparkConfidenceScheduledSpeculative2026]

### Live traffic in DeepSeek-V4 (Figures 7 and 8)

DSpark-5 (maximum draft length $\gamma=5$) against [MTP-1](../methods/multi-token-prediction.md), the former production setup, in the serving engines of DeepSeek-V4-Flash (preview) and DeepSeek-V4-Pro (preview). An SLA here is the minimum per-user generation speed in tok/s/user.[^chengDSparkConfidenceScheduledSpeculative2026]

| Engine | Condition | DSpark vs. MTP-1 |
|---|---|---|
| V4-Flash | 80 tok/s/user SLA | 51% higher aggregate throughput |
| V4-Flash | 120 tok/s/user SLA | nominal 661% higher aggregate throughput |
| V4-Flash | matched practical throughput levels | 60% to 85% faster per-user generation |
| V4-Pro | 35 tok/s/user SLA | 52% higher aggregate throughput |
| V4-Pro | 50 tok/s/user SLA | nominal 406% relative throughput advantage |
| V4-Pro | matched system capacities | 57% to 78% faster per-user generation |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

- At the strict SLAs (120 and 50 tok/s/user) MTP-1 can sustain only a very small concurrent batch. The paper reads those ratios as evidence that DSpark extends the feasible interactivity frontier, and not as a representative multiplicative speedup.[^chengDSparkConfidenceScheduledSpeculative2026]
- Under moderate concurrency (fewer than 200 concurrent requests for V4-Flash and 150 for V4-Pro) the scheduler extends the verification budget from MTP-1's static 2 tokens to roughly 4–6 tokens per request. As concurrency rises the average verification length decreases smoothly.[^chengDSparkConfidenceScheduledSpeculative2026]
- MTP-1 was kept in production because a static multi-token drafter (e.g., MTP-3/5) degrades aggregate throughput under high concurrency. DSpark superseded MTP-1 two weeks after the DeepSeek-V4-preview release.[^chengDSparkConfidenceScheduledSpeculative2026]

## Limitations

- DSpark still pays a fixed draft-side cost to generate the initial $\gamma$-token block. For complex queries with inherently low acceptance rates, this drafting compute is unrecoverable. The paper suggests difficulty-aware early exiting in the draft model as future work.[^chengDSparkConfidenceScheduledSpeculative2026]
- The scheduler assumes that engine throughput depends predominantly on the verification batch size $B$, not on context length.[^chengDSparkConfidenceScheduledSpeculative2026]
- The early-stopping scheduler of Algorithm 1 is globally optimal only for a unimodal $\Theta$, while real hardware capacity curves are jagged. The deployed scheduler approximates capacity with predictions from two steps prior, which introduces a slight temporal offset.[^chengDSparkConfidenceScheduledSpeculative2026]
- The hardware-aware prefix scheduler is evaluated only in live production. Offline experiments report accepted length with the scheduler disabled, and no offline wall-clock speedup is reported.[^chengDSparkConfidenceScheduledSpeculative2026]
- Production results are raw telemetry from live traffic with fitted frontiers, under the measured traffic and engine configurations.[^chengDSparkConfidenceScheduledSpeculative2026]
- In the paper's deployment the effective batch size stays well below the GPU's compute-saturating threshold, so per-GPU throughput and per-user speed are highly correlated objectives there.[^chengDSparkConfidenceScheduledSpeculative2026]

## Related

- Methods: [DSpark](../methods/dspark.md), [Speculative decoding](../methods/speculative-decoding.md), [Semi-autoregressive generation](../methods/semi-autoregressive-generation.md), [Confidence-scheduled verification](../methods/confidence-scheduled-verification.md), [KV injection](../methods/kv-injection.md)
- Systems compared or built on: [DFlash](../methods/dflash.md), [EAGLE-3](../methods/eagle-3.md), [MTP](../methods/multi-token-prediction.md)
- Datasets: [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md), [MBPP](../datasets/mbpp.md), [HumanEval](../datasets/humaneval.md), [LiveCodeBench](../datasets/livecodebench.md), [MT-Bench](../datasets/mt-bench.md), [Alpaca](../datasets/alpaca.md)
- Papers in this wiki cited by this paper: [DFlash](chenDFlashBlockDiffusion2026.md), [EAGLE-3](liEAGLE3ScalingInference2025.md), [SGLang](zhengSGLangEfficientExecution2024.md), [Optimizing Speculative Decoding for Serving LLMs Using Goodput](240614066v2OptimizingSpeculative.md)

## Open questions and results

- [Choosing what to verify: Learning to Draft vs. DSpark](../analyses/choosing-what-to-verify-ltd-vs-dspark.md)
- [Learned policy or calibrated confidence for choosing the verify set?](../questions/learned-vs-confidence-scheduled-verification.md)

[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
