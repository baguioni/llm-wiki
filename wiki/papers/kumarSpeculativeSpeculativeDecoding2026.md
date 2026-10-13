---
type: Paper
title: Speculative Speculative Decoding
description: Framework (SSD) and optimized algorithm (Saguaro) that run drafting in parallel with verification by pre-speculating for predicted verification outcomes on a separate device.
tags: [speculative-decoding, parallel-speculative-decoding, llm-inference, latency, mobile-specedge]
collections: ["mobile-specedge"]
authors: [Tanishq Kumar, Tri Dao, Avner May]
arxiv: "2603.03251"
arxiv_version: 2603.03251v3
code: https://github.com/tanishqkumar/ssd
sources:
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
---

# Speculative Speculative Decoding

Text source: arXiv HTML, version `2603.03251v3`.

## Summary

[Speculative decoding](../methods/speculative-decoding.md) (SD) has a sequential dependence: verification must complete before the next speculation can begin.[^kumarSpeculativeSpeculativeDecoding2026] The paper introduces [speculative speculative decoding](../methods/speculative-speculative-decoding.md) (SSD), a framework for methods that parallelize drafting and verification. While a verification is ongoing, the draft model predicts likely verification outcomes and pre-speculates for each of them. If the actual outcome is in the predicted set, the speculation is returned immediately, which avoids all draft overhead.[^kumarSpeculativeSpeculativeDecoding2026] SSD is lossless like ordinary SD, but unlike ordinary SD the draft model sits on distinct hardware from the target.[^kumarSpeculativeSpeculativeDecoding2026]

[Saguaro](../methods/saguaro.md) is the paper's optimized SSD algorithm. The authors report that their implementation is on average 30% faster than the strongest speculative decoding baselines and up to 5x faster than autoregressive decoding with open source inference engines.[^kumarSpeculativeSpeculativeDecoding2026]

## Contributions

- The SSD framework (Algorithm 1), with a speculator process and a verifier process that run in parallel on separate hardware, and a *speculation cache* that maps predicted verification outcomes to precomputed speculations.[^kumarSpeculativeSpeculativeDecoding2026]
- Speedup analysis: an expected-speedup formula relative to autoregressive decoding (Theorem 7), a proof that SSD with the same speculator does no worse than SD (Corollary 8), and bounds on the SSD-over-SD speedup (Corollary 9).[^kumarSpeculativeSpeculativeDecoding2026]
- Saguaro cache construction: verification-outcome prediction posed as constrained optimization, solved by a geometric fan-out (Theorem 12). The technique uses the most likely draft logits to predict the bonus token, with up to 90% accuracy.[^kumarSpeculativeSpeculativeDecoding2026]
- Saguaro sampling: a sampling scheme that trades acceptance rate for cache hit rate (Definition 14, Theorem 15).[^kumarSpeculativeSpeculativeDecoding2026]
- Saguaro fallback: a batch-size-dependent choice of backup speculator for cache misses (Theorem 17).[^kumarSpeculativeSpeculativeDecoding2026]

## Method

### SSD framework

- A *verification outcome* at round $T$ is $v^T = (k, t^*)$: $k$ accepted draft tokens from the previous round and the bonus token $t^*$ sampled from the residual distribution (or from the target distribution if all tokens are accepted).[^kumarSpeculativeSpeculativeDecoding2026]
- While the verifier verifies the drafted tokens of round $T$, the speculator predicts likely verification outcomes, prepares a speculation for each in parallel, and stores them in the speculation cache $\mathcal{S}^T$.[^kumarSpeculativeSpeculativeDecoding2026]
- A *cache hit* is when the actual outcome is in the cache; the speculation is returned immediately. On a *cache miss* the speculator defers to a fallback (backup) speculator. This is lossless because it reduces to ordinary SD.[^kumarSpeculativeSpeculativeDecoding2026]
- The space of verification outcomes has size approximately $(K+1)V$, where $K$ is the speculative lookahead and $V$ the vocabulary size, so the cache is built under a budget $B$ of outcomes.[^kumarSpeculativeSpeculativeDecoding2026]

### Theoretical results

With primary and backup speculators taking time $T_p$ and $T_b$ relative to the verifier, and $E_{hit}$, $E_{miss}$ the expected number of generated tokens from the primary and backup speculators (Theorem 7):[^kumarSpeculativeSpeculativeDecoding2026]

$$
speedup_{SSD} = \frac{p_{hit}\cdot E_{hit}+(1-p_{hit})\cdot E_{miss}}{p_{hit}\cdot\max(1,T_{p})+(1-p_{hit})\cdot(1+T_{b})}
$$

The overall cache hit rate is $p_{hit} = \frac{p_{hit,b}}{1+p_{hit,b}-p_{hit,p}}$, where $p_{hit,p}$ and $p_{hit,b}$ are the hit rates conditioned on the previous round being speculated by the primary or the backup speculator.[^kumarSpeculativeSpeculativeDecoding2026]

For $T_p<1$ and $T_b=0$ (Corollary 9):[^kumarSpeculativeSpeculativeDecoding2026]

$$
(1+T_{SD})\cdot\frac{E_{hit}}{E_{SD}}\cdot p_{hit}\leq\frac{speedup_{SSD}}{speedup_{SD}}\leq(1+T_{SD})\cdot\frac{E_{hit}}{E_{SD}}
$$

At batch size $b$ the denominator of Theorem 7 becomes $p_{hit}^{b}\cdot\max(1,T_{p})+(1-p_{hit}^{b})\cdot(1+T_{b})$, because the whole batch waits for the backup speculator when any element misses (Corollary 16).[^kumarSpeculativeSpeculativeDecoding2026]

### Saguaro optimizations

| Component | What it does | Key result |
|---|---|---|
| Cache construction (Sec. 4.1) | The *fan-out* $F_k$ is the number of cached outcomes with $k$ accepted tokens. Saguaro takes the top-$F_k$ tokens of the draft logits at each lookahead position $k$, excluding the sampled token sent for verification. | Under an $r$ power-law cache hit rate ($1-p_{hit,*}(F)=1/F^{r}$) and acceptance rate $a_p$, the optimal fan-out is a capped geometric series: $F_k = F_0\cdot a_p^{k/(1+r)}$ for $k<K$ and $F_K = F_0\cdot a_p^{K/(1+r)}\cdot(1-a_p)^{-1/(1+r)}$ (Theorem 12). |
| Sampling (Sec. 4.2) | $\sigma_{F,C}(z)\propto C\cdot\exp(z_t)$ if $t\in\text{top}_F(z)$, else $\exp(z_t)$, with downweighting constant $C\in[0,1]$ chosen empirically. Lowering draft probability on the cached tokens pushes residual mass onto them. | The cache hit rate increases monotonically as $C\rightarrow 0$ (Theorem 15). Lower $C$ gives higher cache hit rates and lower acceptance rates. |
| Fallback (Sec. 4.3) | Backup speculator equals the primary speculator at low batch size, and a low-latency speculator for batch sizes $b>b^*$. | The slow, accurate speculator is the optimal backup for $b<b^*$ and the fast one otherwise (Theorem 17). $b^*$ has a closed form in Appendix A. |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]

In the implementation, the fast backup strategy returns random tokens and the slow strategy is just-in-time speculation with the primary speculator. The paper notes that extremely fast non-neural speculators such as n-gram based ones (it cites [SuffixDecoding](oliaroSuffixDecodingExtremeSpeculative2024.md)) could improve on random tokens.[^kumarSpeculativeSpeculativeDecoding2026]

### System design

- Custom inference engine in PyTorch with [PagedAttention](../methods/paged-attention.md), continuous batching, tensor parallelism, BF16 mixed precision, torch compilation, and CUDAGraphs.[^kumarSpeculativeSpeculativeDecoding2026]
- The target model is split across 4 devices and the draft runs on a separate device. They communicate through NCCL once per speculation round. The target sends only the previous round's result (number of accepted tokens, bonus token). No KV cache is ever transferred between the devices.[^kumarSpeculativeSpeculativeDecoding2026]
- All $F(K+1)$ branches of each sequence are decoded in parallel with a custom sparse attention mask, so each branch attends to the verified trunk and its own forking path.[^kumarSpeculativeSpeculativeDecoding2026]

### Overhead (Appendix C)

| Resource | SSD cost |
|---|---|
| Compute | The draft decodes $BK(K+1)F$ tokens per round in SSD versus $BK$ in SD, a factor of $\hat{c}(K+1)F$ more draft FLOPs ($\hat{c}$ = draft forward-pass compute in units of target FLOPs). |
| Memory | The speculation cache stores $O(BFK(K+1)(V+1))$ bits, around hundreds of megabytes in practice. |
| Communication | Target to draft: $O(B)$ bits. Draft to target (tokens and logits): $O(BKV)$ bits, over NCCL via NVLink. |

Here $B$ is the target batch size, $K$ the lookahead, and $F$ the uniform fan-out. All rows: [^kumarSpeculativeSpeculativeDecoding2026]

## Experiments & Results

### Setup

- Unless otherwise specified: batch size 1, greedy decoding, target model on 4×H100. In SD the draft is collocated on the same hardware. In SSD it sits on a separate device (1×H100), so SSD uses 5 GPUs and AR and SD use 4.[^kumarSpeculativeSpeculativeDecoding2026]
- Models: Llama-3.1-70B-Instruct with Llama-3.2-1B-Instruct as draft, and Qwen3-32B with Qwen3-0.6B as draft.[^kumarSpeculativeSpeculativeDecoding2026]
- Datasets: [Alpaca](../datasets/alpaca.md), [GSM8k](../datasets/gsm8k.md), [UltraFeedback](../datasets/ultrafeedback.md), [HumanEval](../datasets/humaneval.md). The paper takes 128 prompts from each dataset and samples 512 decoding tokens for each, with vanilla sampling (not top-p or top-k). It measures decoding throughput, excluding prefill.[^kumarSpeculativeSpeculativeDecoding2026]
- Baselines: [vLLM](../methods/vllm.md) (v0.16.0) and [SGLang](../methods/sglang.md) (v0.5.9), each with autoregressive decoding, standalone speculative decoding, and [EAGLE-3](../methods/eagle-3.md); tensor parallelism across 4×H100 80GB GPUs, greedy decoding, radix caching disabled, a single concurrent request, 5 draft tokens per step for speculative decoding. The paper also compares against its own SD implementation.[^kumarSpeculativeSpeculativeDecoding2026]

### End-to-end decoding speed (Appendix B.3)

AR, SD, and SSD here are the paper's own implementations.[^kumarSpeculativeSpeculativeDecoding2026]

| Model (target/draft) | Dataset | AR tok/s | SD tok/s | SSD tok/s | SSD/SD | SSD/AR |
|---|---|---|---|---|---|---|
| Llama-3.1-Instruct 70B/1B | HumanEval | 54.7 | 176 | 283 | 1.60× | 5.17× |
| Llama-3.1-Instruct 70B/1B | Ultrafeedback | 54.7 | 138 | 215 | 1.55× | 3.93× |
| Llama-3.1-Instruct 70B/1B | Alpaca | 54.7 | 145 | 224 | 1.55× | 4.10× |
| Llama-3.1-Instruct 70B/1B | GSM8k | 54.7 | 188 | 301 | 1.60× | 5.50× |
| Llama-3.1-Instruct 70B/1B | Average | 54.7 | 161.8 | 255.8 | 1.58× | 4.68× |
| Qwen-3 32B/0.6B | HumanEval | 88.8 | 146 | 222 | 1.52× | 2.50× |
| Qwen-3 32B/0.6B | Ultrafeedback | 88.8 | 122 | 174 | 1.43× | 1.96× |
| Qwen-3 32B/0.6B | Alpaca | 88.8 | 127 | 185 | 1.47× | 2.08× |
| Qwen-3 32B/0.6B | GSM8k | 88.8 | 152 | 234 | 1.54× | 2.64× |
| Qwen-3 32B/0.6B | Average | 88.8 | 136.8 | 203.8 | 1.49× | 2.29× |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]

The main text states almost a 5x speedup on average over the autoregressive baseline and an average 30% speedup over the strongest speculative decoding baselines.[^kumarSpeculativeSpeculativeDecoding2026] The paper also states that SSD improves the throughput-latency Pareto frontier across batch sizes, with the biggest gains at lower batch sizes, and that Saguaro outperforms SD by 20% even at larger batch sizes. These are shown in Figure 7 (right) and Figure 6, and the paper gives no table for them.[^kumarSpeculativeSpeculativeDecoding2026]

### Baseline sweeps, Llama-3.1-70B/1B (decode tok/s)

Best configuration per method, from sweeps over speculative lookahead (and tree size for SGLang). `†` cells in the source mark configurations that are incompatible because of known bugs in the library version used.[^kumarSpeculativeSpeculativeDecoding2026]

| Engine | Method | Best tok/s | Best configuration |
|---|---|---|---|
| SGLang 0.5.9 | EAGLE-3 | 192.8 | steps 8, topk 3 |
| SGLang 0.5.9 | Standalone SD | 201.9 | steps 10, topk 3 |
| vLLM 0.16.0 | EAGLE-3 | 197.6 | $K=6$ |
| vLLM 0.16.0 | Standalone SD | 136.0 | $K=2$ |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]

Full vLLM sweep over lookahead $K$:[^kumarSpeculativeSpeculativeDecoding2026]

| Method | $K=2$ | $K=4$ | $K=6$ | $K=8$ | $K=10$ | $K=12$ |
|---|---|---|---|---|---|---|
| vLLM EAGLE-3 | 143.7 | 181.4 | 197.6 | 197.0 | 191.8 | 187.9 |
| vLLM Standalone | 136.0 | 117.9 | 100.9 | 89.1 | 78.5 | 70.5 |

- The authors find that SGLang usually outperforms vLLM and use it as the main baseline.[^kumarSpeculativeSpeculativeDecoding2026]
- In their experiments Llama-3.2-1B outperforms EAGLE-3 as a draft model for Llama-3.1-70B in SGLang.[^kumarSpeculativeSpeculativeDecoding2026]
- Their own vanilla SD implementation has speed comparable to vLLM and SGLang.[^kumarSpeculativeSpeculativeDecoding2026]

### Component findings (figures only)

- Rejection rates (cache misses) fall as a power law in the draft fan-out, for Llama-3 and for Qwen-3 (Figures 3 and 10).[^kumarSpeculativeSpeculativeDecoding2026]
- Geometric fan-out improves cache hit rate and end-to-end speed over uniform fan-out, especially at higher temperatures. At all temperatures SSD with either fan-out strategy outperforms ordinary SD (Figure 4, averaged over four datasets).[^kumarSpeculativeSpeculativeDecoding2026]
- As batch size increases, a fast backup speculator that returns random tokens outperforms a slow but more accurate neural speculator (Figure 6, left, temperature 0).[^kumarSpeculativeSpeculativeDecoding2026]
- Figure 6 (right) is a projection, not a measurement: speedups at batch size 16 if more GPUs are given to drafting, computed from the cache hit rate curves.[^kumarSpeculativeSpeculativeDecoding2026]

## Limitations

- Speculative decoding is generally ineffective for throughput-bound workloads such as large-scale RL and offline data generation, because it adds verification workload to an already compute-bound process.[^kumarSpeculativeSpeculativeDecoding2026]
- SSD needs additional hardware: the draft runs on its own device, and SSD spends more draft FLOPs than SD. Entire chains decoded for anticipated outcomes that do not occur are wasted compute.[^kumarSpeculativeSpeculativeDecoding2026]
- Materializing the custom attention masks is substantial overhead. Sparse, non-coalesced memory access in the custom-mask attention kernels dominates the critical path and limits how many steps can be profitably drafted, so most of the end-to-end speedup comes from hiding draft latency rather than increasing lookahead.[^kumarSpeculativeSpeculativeDecoding2026]
- Cache misses happen increasingly often at large batch sizes and temperatures, and on a miss the whole batch waits for the backup speculator.[^kumarSpeculativeSpeculativeDecoding2026]
- Returns from scaling the number of draft devices will eventually diminish.[^kumarSpeculativeSpeculativeDecoding2026]
- Combining SSD with EAGLE-3: the SSD draft does not yet have target activations from round $T$, so with lookahead $K$ it conditions on up to $2K$ self-generated tokens, which lowers acceptance on the latter $K$. The joint design space with EAGLE and token-tree speculation is largely unexplored.[^kumarSpeculativeSpeculativeDecoding2026]

## Related

- Proposed: [Speculative speculative decoding (SSD)](../methods/speculative-speculative-decoding.md), [Saguaro](../methods/saguaro.md)
- Builds on: [Speculative decoding](../methods/speculative-decoding.md), [PagedAttention](../methods/paged-attention.md)
- Baselines and engines: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md), [EAGLE-3](../methods/eagle-3.md)
- Prior parallel speculative decoding, discussed but not benchmarked: [PEARL](../methods/pearl.md) and AMUSD prepare only for the all-tokens-accepted outcome; [SwiftSpec](../methods/swiftspec.md) and [SpecBranch](../methods/specbranch.md) cache a token tree branching off the speculation, with fallback strategies that the paper says do not work at large batch sizes.[^kumarSpeculativeSpeculativeDecoding2026]
- Datasets: [Alpaca](../datasets/alpaca.md), [GSM8k](../datasets/gsm8k.md), [UltraFeedback](../datasets/ultrafeedback.md), [HumanEval](../datasets/humaneval.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [SpecExec](svirschevskiSpecExecMassivelyParallel2024.md), [SuffixDecoding](oliaroSuffixDecodingExtremeSpeculative2024.md), [DFlash](chenDFlashBlockDiffusion2026.md)

[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
