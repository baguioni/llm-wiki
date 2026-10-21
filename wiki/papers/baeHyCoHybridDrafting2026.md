---
type: Paper
title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
description: Mobile-cloud speculative decoding that runs the verifier's own MTP head on the phone NPU for draft depth and one SLM pass for alternative branches, with the server returning the head's inputs, and cuts server GPU time per output token against server-side MTP self-speculation by 38.6% on Spec-Bench.
tags: [speculative-decoding, device-cloud-collaborative-inference, multi-token-prediction, tree-based-speculation, mobile-npu, quantization, lossy-acceptance, edge-inference, mobile-specedge]
collections: ["mobile-specedge"]
authors: [Hanbin Bae, Heejin Choi, Joohyung Lee, Byoung Jin Choi, Sangjun Park, Hoon-Young Cho]
doi: 10.48550/arXiv.2610.21436
arxiv: "2610.21436"
arxiv_version: 2610.21436v1
sources:
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding

Text source: arXiv HTML, version `2610.21436v1`. Authors are from the AI Solution Team, Samsung Research, Seoul.[^baeHyCoHybridDrafting2026]

## Summary

Device-cloud [speculative decoding](../methods/speculative-decoding.md) puts a small language model (SLM) on the user's device and leaves verification to the server. Growing a deep draft tree with an autoregressive SLM needs one sequential pass per tree level on the mobile NPU. The four-level SpecEdge-style tree studied in the paper raises the mean number of tokens accepted per round (MAT), yet its four mobile SLM passes leave the user slower than the SLM alone.[^baeHyCoHybridDrafting2026]

[HyCo](../methods/hyco.md) splits the drafting work. The server LLM's native [multi-token prediction (MTP)](../methods/multi-token-prediction.md) head reads only a small slice of the LLM's state, so it runs on the phone as the *MTP Drafter* and supplies a chain that gives the tree its depth. The server (the *verifier*) returns the head's inputs with each verification instead of running the head's sequential steps itself. One pass of the device's *SLM Drafter* adds alternatives under the root and every planted node. Integer quantization, a restricted output vocabulary, and a 1K-token window fit both drafters to the NPU. An optional [$\epsilon$-threshold acceptance](../methods/lossy-acceptance.md) rule relaxes exact preservation of the verifier's sampling distribution.[^baeHyCoHybridDrafting2026]

With Gemma 4 26B-A4B on one RTX PRO 6000 and the drafters on a Galaxy S26 Ultra over LTE/5G, single-client runs show HyCo cutting server GPU time per output token against server-side MTP self-speculation (Cloud+MTP) by 38.6% on Spec-Bench and 29.2% on 32K-token summarization. With exact verification it saves 27.7% and 11.9%. On Spec-Bench it delivers 35.0 tokens/s, 1.9× the rate of an SLM-only drafter under the same acceptance rule and faster than the SLM alone.[^baeHyCoHybridDrafting2026]

## Contributions

- A division of drafting work between the verifier's native MTP head, executed on the mobile device, and one SLM pass, with the server returning the head's inputs (hidden state, input embedding, and key-value entries).[^baeHyCoHybridDrafting2026]
- An implementation that fits both drafters to a mobile NPU through quantization, a restricted output vocabulary, and a 1K-token window.[^baeHyCoHybridDrafting2026]
- $\epsilon$-threshold acceptance, which thresholds the verifier's sampling distribution after temperature and top-$k$/top-$p$ truncation, and an evaluation of its quality trade-off alongside an exact-verification ablation.[^baeHyCoHybridDrafting2026]

## Method

### Goals and cost metric

- Two reference points. The server should spend less GPU time per output token than *Cloud+MTP*, which already runs the LLM's own MTP self-speculation. The user should receive tokens at least as fast as the SLM alone generates them on the device.[^baeHyCoHybridDrafting2026]
- Server cost $g$ is the total GPU time, including prefill, divided by output tokens. For decoding, this is server time per round divided by MAT.[^baeHyCoHybridDrafting2026]
- Settings are compared on UC-val, 60 prompts from the test split of [UltraChat 200k](../datasets/ultrachat.md). The default selection criterion minimizes $g$ among settings whose LLM-judge score falls in the observed lossless-run range, 58.7–63.0. The paper calls this a screening heuristic, not a quality-equivalence test: two runs of the same setting scored 57.1 and 61.5.[^baeHyCoHybridDrafting2026]

### Hybrid draft tree

- **MTP Drafter.** The verifier's own MTP head, quantized by the authors' quantization-aware training (QAT), drafts a chain of $K$ top-1 tokens. It reads the input embedding $e(x_{t+1})$ of the root, the last hidden state $h_t$ from which the verifier sampled $x_{t+1}$, and the keys and values of two verifier layers (the last full-attention and the last sliding-window layer).[^baeHyCoHybridDrafting2026]
- **Hand-off.** The server returns these inputs with each verification, 5.6 KB per round plus 6.1 KB per output token at 8 bits, and skips the $K$ sequential head steps that Cloud+MTP runs after every verification pass. The first reply seeds the head's window with the prompt's last 1,024 tokens, at most 6.3 MB.[^baeHyCoHybridDrafting2026]
- Moving the MTP head from the server to the phone shortens the server's median round from 26.8 to 21.7 ms and lowers $g$ by 15.2%, at about 20 ms more per round on the phone.[^baeHyCoHybridDrafting2026]
- **Runner-up siblings.** At its first two steps the MTP Drafter also plants its second-ranked token beside the chain token.[^baeHyCoHybridDrafting2026]
- **SLM Drafter.** Gemma 4 E2B from Google's QAT checkpoint proposes, in one pass, children under the root and every planted node, which gives the tree its width.[^baeHyCoHybridDrafting2026]
- **Scoring and trimming.** Each depth along a node's path costs $\ln 0.66\approx-0.42$, because the chain's per-depth acceptance rate is 0.65–0.68 at every depth, with a geometric mean of 0.66 (measured over 7,513 rounds with exact verification). A runner-up sibling pays this cost twice on its own edge, and an SLM candidate adds its token's log-probability. The tree is trimmed by score to $B=32$ nodes, closed under ancestors, and sent as token IDs and parent indices, 2.2 KB per round.[^baeHyCoHybridDrafting2026]
- **Verification.** One forward pass with a tree attention mask, as in [SpecInfer](../methods/specinfer.md). Under exact verification the verifier samples at each node from its sampling distribution $\tilde{p}$ and descends to the matching child, so verification is lossless. The first sample that matches no child is the bonus token and the root of the next tree.[^baeHyCoHybridDrafting2026]
- The chain supplies most accepted tokens. An SLM leaf extends a fully accepted chain to a fifth token in 17% of rounds under exact verification.[^baeHyCoHybridDrafting2026]
- Chosen on UC-val: $K=4$ and runner-up siblings at depths 1–2. Cumulative chain acceptance reaches 18.9% at depth 4. The 32-node budget matches SpecEdge-style, and the verifier uses the same 33-row CUDA graphs. A second SLM pass is kept as the HyCo-2P option.[^baeHyCoHybridDrafting2026]

### Quantization

- In a diagnostic comparison, 16-bit floating-point activations lengthened the SLM Drafter's 32-row pass from 15.7 to 38–41 ms at unchanged acceptance.[^baeHyCoHybridDrafting2026]
- The SLM's QAT checkpoint has 2-, 4-, or 8-bit weights but computes in floating point. The authors convert it to integer graphs through graph surgery and activation calibration, without retraining its weights.[^baeHyCoHybridDrafting2026]
- The MTP head is released in BF16. The authors apply 4-bit QAT to its linear weights, training 100 steps to minimize KL divergence from the BF16 head on the verifier's greedy answers to 60 UC-tr prompts. On UC-val this raises top-1 agreement with BF16 from 87.4% to 91.0%. 8-bit weights retain 98.8% without training but double weight storage.[^baeHyCoHybridDrafting2026]
- Both drafters use 16-bit fixed-point activations and static graphs compiled with the Qualcomm AI Runtime (QAIRT 2.47.1). No operator falls back to floating point.[^baeHyCoHybridDrafting2026]

| | SLM Drafter | MTP Drafter |
|---|---|---|
| Weight bit map | the checkpoint's 2/4/8 bits | W4 (W8: post-training) |
| Activations | 16-bit | 16-bit |
| KV / inputs | 8-bit KV cache | 16-bit (8-bit on the wire) |
| Embeddings | 2/4-bit LUT | 8-bit LUT, 242 MB |
| Size | 754 MB NPU graph | 123 MB NPU graph at W4 |
| Authors' training | none (graph surgery only) | QAT, 100 steps (W4) |

All rows: [^baeHyCoHybridDrafting2026]

### Restricted output vocabulary

- Both drafters' output layers span 262,144 tokens. The full vocabulary lengthens the phone's time per round from 52.9 to 77.9 ms.[^baeHyCoHybridDrafting2026]
- As in [FR-Spec](../methods/fr-spec.md), both drafters predict from one keep set of 86,089 tokens: 24 special tokens, 256 byte tokens, all 4,678 Hangul tokens, and the 81,131 tokens most frequent in the assistant turns of 20,000 UC-tr conversations.[^baeHyCoHybridDrafting2026]
- Tokens outside the keep set make up 3.0% of the verifier's bonus tokens on UC-val and 6.8% on a 150-question Spec-Bench subset. The verifier still samples them from its full vocabulary, so the restriction costs only acceptance and exact verification stays lossless.[^baeHyCoHybridDrafting2026]

Keep-set selection on UC-val ($g$: server ms per output token; device: on-device ms per round):[^baeHyCoHybridDrafting2026]

| Keep set | MAT | $g$ | Device |
|---|---|---|---|
| 21K | 2.98 | 7.00 | 45.7 |
| 45K | 3.25 | 6.44 | 47.8 |
| 86K (chosen) | 3.36 | 6.23 | 52.9 |
| 262K, full vocabulary | 2.85 | 7.57 | 77.9 |

All rows: [^baeHyCoHybridDrafting2026]

### 1K-token context window

- Both drafters read only the last 1,024 tokens of the context. The SLM Drafter keeps its KV cache as a ring of the last 1,024 committed tokens (512 in its sliding-window layers). The MTP Drafter reads the verifier's keys and values over the same window and prefills nothing on the device. The verifier prefills the whole prompt.[^baeHyCoHybridDrafting2026]
- On UC-val an SLM context of 4,096 instead of 1,024 moves $g$ from 6.82 to 6.77 ms, and MTP head windows of 512–2,048 tokens (head on the server) give 7.75–7.89 ms, both within noise.[^baeHyCoHybridDrafting2026]

### $\epsilon$-threshold acceptance

- A drafted child $c$ of node $v$ is accepted if it matches the verifier's sample or if $\tilde{p}(c\mid v)\geq\epsilon$, where $\tilde{p}$ is the verifier's sampling distribution after temperature scaling and top-$k$/top-$p$ truncation, not its raw softmax. The verifier selects the deepest accepted path, preferring among equally deep paths the one with more verifier-sampled edges, then the highest product of $\tilde{p}$.[^baeHyCoHybridDrafting2026]
- The rule is lossy: it can commit tokens the verifier did not sample and changes their selection probabilities. $\epsilon=1$ gives the exact-verification ablation. With a one-hot greedy distribution the threshold adds no token.[^baeHyCoHybridDrafting2026]
- At $\epsilon=0.005$, applying the threshold at every node rather than only at rejections lowers $g$ from 5.62 to 5.10 ms at the same judge score of 60.0. Medusa's typical acceptance at its defaults falls below the lossless range. The chosen setting is $\epsilon=0.005$ at every node.[^baeHyCoHybridDrafting2026]
- On the fixed logged trees of one run, $\epsilon=0.005$ gives MAT 4.364 against 4.366 if every drafted token in the verifier's sampling support were accepted.[^baeHyCoHybridDrafting2026]

## Experiments & Results

### Setup

- **Verifier.** Gemma 4 26B-A4B (25.2B parameters, 3.8B active) with 4-bit AWQ, on one 96 GB RTX PRO 6000 (AWS g7e.2xlarge). Sampling at temperature 1, top-$k$ 64, top-$p$ 0.95, so exact verification preserves this sampling distribution, not a fixed greedy output.[^baeHyCoHybridDrafting2026]
- **Device.** Galaxy S26 Ultra (SM8850) running the drafters on its Hexagon Tensor Processor v81, over a commercial LTE/5G connection (LTE-CA or 5G NSA, as assigned by the operator). The MTP head has 420M parameters; Gemma 4 E2B has 2.3B effective parameters.[^baeHyCoHybridDrafting2026]
- **Engine.** All configurations use SpecEdge's verification server, extended with the verifier and its MTP head, the same kernels, and one client at a time. Attention projections run as 4-bit Marlin matrix products and the experts (8 of 128 per token) through [vLLM](../methods/vllm.md)'s fused Marlin MoE kernel.[^baeHyCoHybridDrafting2026]
- **Data.** All 480 [Spec-Bench](../benchmarks/spec-bench.md) questions (SB-480), including both MT-bench turns, with a 1,024-token output cap. For long inputs, the first 50 English novels of [InfiniteBench](../datasets/infinitebench.md) En.Sum ($\infty$Bench Sum) in HELMET's seed-42 order, truncated to 32K tokens (median 30.6K Gemma tokens), with a 1,200-token output cap.[^baeHyCoHybridDrafting2026]
- **Quality.** GPT-5.4 scores first-turn Spec-Bench answers from 0 to 100 from the question alone. The aggregate covers non-QA tasks (398 questions for HyCo against Cloud+MTP). Long summaries use ROUGE-L-Sum and HELMET's model-based F1, recall, and precision.[^baeHyCoHybridDrafting2026]
- HyCo and SpecEdge-$\epsilon$ have three Spec-Bench generations each; all other configurations, the 32K set, and Cloud+MTP have one. $\pm$ values are run-level sample SDs. Paired 95% CIs use 2,000 question-level bootstrap samples.[^baeHyCoHybridDrafting2026]

### Configurations

| Configuration | MTP head place / weights / vocabulary / window | $K$ | Siblings | SLM passes | Nodes / rows | Acceptance |
|---|---|---|---|---|---|---|
| Cloud+MTP | server / BF16 / 262K / whole prefix | 4 | – | – | 4 / 5 | exact |
| SpecEdge-style | – | 0 | – | 4 | 32 / 33 | exact |
| SpecEdge-style + PD | – | 0 | – | 4 + PD | 32 / 33 | exact |
| SpecEdge-$\epsilon$ | – | 0 | – | 4 | 32 / 33 | $\epsilon=0.005$ |
| HyCo | mobile / W4 / 86K / 1,024 | 4 | depths 1–2 | 1 | 32 / 33 | $\epsilon=0.005$ |
| HyCo-2P | mobile / W4 / 86K / 1,024 | 4 | depths 1–2 | 2 | 32 / 33 | $\epsilon=0.005$ |
| HyCo exact | mobile / W4 / 86K / 1,024 | 4 | depths 1–2 | 1 | 32 / 33 | exact ($\epsilon=1$) |
| HyCo server head | server / BF16 / 86K / 1,024 | 4 | – | 1 | 32 / 33 | exact |
| On-device 8K | the SLM alone: 8,192-token context, 262K vocabulary, greedy decoding, no verifier | | | | | |

All rows: [^baeHyCoHybridDrafting2026]

PD is proactive drafting, which continues drafting while a verification reply is in flight (see [Proactive edge drafting](../methods/proactive-edge-drafting.md)). SpecEdge-$\epsilon$ applies exactly the same threshold and path-selection rule as HyCo to an SLM-only tree.[^baeHyCoHybridDrafting2026]

### Server cost, acceptance, and delivery speed (Table 2)

$\Delta g$ is the paired change from Cloud+MTP, whose reference $g$ is 7.81 ms per token on SB-480 and 23.91 ms on 32K. Lower is better. Tok/s is delivery speed: pooled output tokens divided by mobile wall time from request start to last token.[^baeHyCoHybridDrafting2026]

| Configuration | Rule | SB-480 $\Delta g$ (%) | SB-480 MAT | SB-480 Tok/s | 32K $\Delta g$ (%) | 32K MAT | 32K Tok/s |
|---|---|---|---|---|---|---|---|
| Cloud+MTP | exact | 0.0 | 3.05 | – | 0.0 | 2.37 | – |
| SpecEdge-style | exact | −20.6 | 3.53 | 16.1 | −2.9 | 2.52 | 10.0 |
| SpecEdge-style + PD | exact | −23.9 | 3.69 | 12.1 | −2.9 | 2.52 | 8.2 |
| SpecEdge-$\epsilon$ | $\epsilon$ | −29.6 ± 0.2 | 4.13 | 18.9 ± 0.1 | −15.7 | 3.08 | 12.4 |
| HyCo | $\epsilon$ | −38.6 ± 0.2 | 4.71 | 35.0 ± 0.7 | −29.2 | 3.73 | 21.0 |
| HyCo-2P | $\epsilon$ | −44.7 | 5.27 | 29.0 | −31.9 | 3.95 | 18.8 |
| HyCo exact | exact | −27.7 | 3.84 | 28.2 | −11.9 | 2.81 | 16.8 |
| HyCo server head | exact | −14.6 | 3.79 | 36.1 | −3.8 | 2.70 | 19.8 |

All rows: [^baeHyCoHybridDrafting2026]

- Cloud+MTP was measured without the phone, so it has no mobile delivery rate. MAT run SDs are both 0.012 for the repeated systems. The paper notes that matching rules does not enforce equal quality.[^baeHyCoHybridDrafting2026]
- On 32K summarization the reductions of HyCo and SpecEdge-$\epsilon$ are 29.2% (95% CI: 27.8–30.6%) and 15.7% (14.1–17.1%).[^baeHyCoHybridDrafting2026]
- Under the same $\epsilon$ rule, HyCo saves 9.0 percentage points more on Spec-Bench than SpecEdge-$\epsilon$. The hybrid tree reaches MAT 4.71 with one SLM pass, the SLM-only tree 4.13 with four.[^baeHyCoHybridDrafting2026]
- HyCo-2P saves more server time but delivers fewer tokens per second than default HyCo. On $\infty$Bench Sum the second pass adds only 2.7 percentage points of server saving and reduces delivery speed by 10%; prefill, which drafting does not shorten, accounts for about a fifth of $g$.[^baeHyCoHybridDrafting2026]
- PD raises SpecEdge-style's Spec-Bench saving from 20.6% to 23.9% but lowers delivery from 16.1 to 12.1 tokens/s. On 32K both save 2.9% (rounded) and PD lowers delivery from 10.0 to 8.2 tokens/s. The paper concludes that neither more passes nor overlapping draft work is uniformly beneficial in this deployment.[^baeHyCoHybridDrafting2026]
- Per-question analysis finds 2, 1, and 0 non-saving cases among the 480 questions in HyCo's three runs. They are short RAG answers of about 40 tokens.[^baeHyCoHybridDrafting2026]

### System metrics (Table 11)

| Configuration | $g$ (ms/token) | Tok/s | Draft ms/token | Tokens/GPU-busy s | GPU-h/1M tokens |
|---|---|---|---|---|---|
| *SB-480* | | | | | |
| Cloud+MTP | 7.81 | – | – | 128.1 | 2.17 |
| SpecEdge-style | 6.20 | 16.1 | 42.8 | 161.3 | 1.72 |
| SpecEdge-style + PD | 5.94 | 12.1 | 40.1 | 168.4 | 1.65 |
| SpecEdge-$\epsilon$ | 5.50 | 18.9 | 37.0 | 181.9 | 1.53 |
| HyCo | 4.80 | 35.0 | 12.1 | 208.5 | 1.33 |
| HyCo-2P | 4.32 | 29.0 | 18.2 | 231.5 | 1.20 |
| HyCo exact | 5.64 | 28.2 | 14.7 | 177.2 | 1.57 |
| HyCo server head | 6.67 | 36.1 | 9.2 | 149.9 | 1.85 |
| On-device 8K | – | 26.4 | 36.8 | – | – |
| *$\infty$Bench Sum 32K* | | | | | |
| Cloud+MTP | 23.91 | – | – | 41.8 | 6.64 |
| SpecEdge-style | 23.20 | 10.0 | 60.3 | 43.1 | 6.45 |
| SpecEdge-style + PD | 23.18 | 8.2 | 58.9 | 43.1 | 6.44 |
| SpecEdge-$\epsilon$ | 20.16 | 12.4 | 48.9 | 49.6 | 5.60 |
| HyCo | 16.92 | 21.0 | 16.4 | 59.1 | 4.70 |
| HyCo-2P | 16.27 | 18.8 | 24.9 | 61.5 | 4.52 |
| HyCo exact | 21.07 | 16.8 | 21.1 | 47.5 | 5.85 |
| HyCo server head | 23.00 | 19.8 | 12.8 | 43.5 | 6.39 |

All rows: [^baeHyCoHybridDrafting2026]

Mobile draft time excludes verification waits and prefill. For PD, subtracting the verification wait also excludes drafting overlapped with that wait, so its draft time is not its total active compute.[^baeHyCoHybridDrafting2026]

### Mobile costs

- On Spec-Bench HyCo delivers 35.0 tokens/s against 26.4 for the SLM alone (32.5% faster), and its 12.1 ms of mobile draft time per output token is about a third of the SLM alone's 36.8 ms. SpecEdge-style exact delivers 16.1 tokens/s and uses 42.8 ms of mobile draft time per token.[^baeHyCoHybridDrafting2026]
- In a separate paired 150-question experiment, the device-head configuration (W4, 86K keep set, 1K window) has 4.0% lower MAT than the original BF16 server head (95% CI: 3.0–4.9%). Relaxing HyCo exact raises MAT from 3.84 to 4.71.[^baeHyCoHybridDrafting2026]
- Among the exact configurations, server head uses 9.2 ms of mobile draft time per output token against 14.7 ms for HyCo exact, with 13.1 percentage points less server saving on Spec-Bench.[^baeHyCoHybridDrafting2026]
- Time to first token, single-run traces (mean/p90): HyCo 846/1,922 ms on Spec-Bench and 4,604/4,842 ms on 32K; HyCo-2P 967/2,147 ms and 3,759/3,908 ms; HyCo exact 920/2,050 ms and 4,014/4,344 ms.[^baeHyCoHybridDrafting2026]
- Recorded Spec-Bench summaries put network and serialization at roughly 40–58 ms per round. With the screen off, each round trip took 14 ms longer.[^baeHyCoHybridDrafting2026]

### Quality (Table 7)

| Configuration | Generations | Judge mean | Paired $\Delta$ vs. Cloud+MTP [95% CI] | Paired $n$ |
|---|---|---|---|---|
| Cloud+MTP | 1 | 90.15 | – | – |
| SpecEdge-style | 1 | 90.21 | +0.1 [−1.3, +1.4] | 398 |
| SpecEdge-style + PD | 1 | 90.05 | −0.1 [−1.6, +1.2] | 398 |
| SpecEdge-$\epsilon$ | 3 | 90.60 ± 0.61 | +0.5 [−0.7, +1.8] | 396 |
| HyCo | 3 | 90.34 ± 0.50 | +0.2 [−0.9, +1.3] | 398 |
| HyCo-2P | 1 | 90.38 | +0.2 [−1.0, +1.5] | 398 |
| HyCo exact | 1 | 90.76 | +0.6 [−0.7, +1.9] | 398 |
| HyCo server head | 1 | 90.72 | +0.6 [−0.4, +1.6] | 398 |
| On-device 8K | 1 | 54.59 | −35.6 [−39.2, −32.0] | 398 |

All rows: [^baeHyCoHybridDrafting2026]

- HyCo against SpecEdge-$\epsilon$ on common questions: −0.2 points (95% CI: −1.2 to +0.8). HyCo against HyCo exact: −0.4 points (−1.5 to +0.6). The paper states that intervals spanning zero do not establish quality equivalence.[^baeHyCoHybridDrafting2026]
- Translation is an exception: HyCo scores 2.6 points below SpecEdge-$\epsilon$ (95% CI: −5.2 to −0.2), while its difference from Cloud+MTP spans zero. The 15 task-wise contrasts are exploratory and unadjusted for multiple comparisons.[^baeHyCoHybridDrafting2026]
- Reference checks on HyCo's first Spec-Bench generation against Cloud+MTP: [GSM8K](../datasets/gsm8k.md) numeric-answer accuracy 95.0% vs 95.0%, RAG contains-gold accuracy 65.7% vs 67.1%, [CNN/DailyMail](../datasets/cnn-dailymail.md) ROUGE-L 19.2 vs 19.8, WMT14 corpus BLEU 33.9 vs 33.7.[^baeHyCoHybridDrafting2026]
- On 32K summaries, HyCo's HELMET F1 differs from Cloud+MTP by +0.4 points (−2.3 to +3.1) and its precision by +1.9 (−2.6 to +6.2). ROUGE-L-Sum is 37.5 against 38.5, a difference of −1.0 (−2.1 to +0.1). SpecEdge-$\epsilon$ combines higher precision with lower recall.[^baeHyCoHybridDrafting2026]
- A fixed ±20-point screen of HyCo's per-question means against Cloud+MTP selects 13 decreases and 12 increases. Manual inspection finds six substantive HyCo errors among the decreases. In one question, identical answer text received scores of 15 and 95.[^baeHyCoHybridDrafting2026]
- In the UC-val replay, about two thirds of threshold-only accepted tokens come from the MTP chain, a tenth from runner-up siblings, and a quarter from the SLM.[^baeHyCoHybridDrafting2026]

### Cross-family runs (Appendix H)

On a Galaxy Z Fold8 (same SM8850 chipset), the SLM Drafter drafted without retraining for Muse-Glimmer-30B in NVFP4 through a token bridge. Glimmer's own DFlash2 head, which reads five of its layers, drafted eight-token chains on the server. Over all 480 Spec-Bench questions, a SpecEdge-style tree of four SLM passes and 127 nodes reached MAT 3.16, and a 32-node tree of the chain and a single SLM pass reached 4.07. These runs used another verifier, server GPU, engine, and output cap (2,048 tokens), so they are not comparable with Table 2.[^baeHyCoHybridDrafting2026]

### Compute

The MTP head's QAT is 100 steps of about 1.5 s each on one NVIDIA DGX Spark. The final-run records account for 5.04 GPU-busy hours and 31.00 cumulative mobile-request hours, excluding setup, calibration, validation sweeps, and cross-family experiments.[^baeHyCoHybridDrafting2026]

## Limitations

- Default HyCo does not preserve the verifier's sampling distribution. The judge-score interval permits a modest quality decrease, and translation favors SpecEdge-$\epsilon$ in an exploratory comparison. The judge covers non-QA first turns only, and the paper does not establish how relaxed acceptance changes output diversity.[^baeHyCoHybridDrafting2026]
- One mobile device, one commercial cellular network, one cloud GPU type, one verifier family, and one client at a time. The paper measures GPU execution time and mobile draft time, not loaded-service capacity, monetary cost, or device and radio energy.[^baeHyCoHybridDrafting2026]
- Each round waits for one network round trip, which bounds mobile delivery speed. Higher average delivery speed does not imply a lower first-token delay.[^baeHyCoHybridDrafting2026]
- HyCo needs the verifier's native head, intermediate hidden states, and KV entries, which closed model services may not expose. The SLM needs a shared tokenizer or a token bridge. Heads that read more verifier layers, such as DFlash, can need a larger hand-off.[^baeHyCoHybridDrafting2026]
- The MTP Drafter adds about 20 ms per mobile round and up to 6.3 MB to the first reply of a long prompt. The device stores 365 MB for it alongside the SLM's 754 MB graph.[^baeHyCoHybridDrafting2026]
- The UltraChat-derived keep set and the 1K window need not suit every language or domain. The SLM sees earlier context only indirectly through the MTP chain. Text only.[^baeHyCoHybridDrafting2026]
- Each client holds the MTP head and part of the verifier's input embeddings, and transmitted activations may expose information beyond the text. No safeguard is evaluated.[^baeHyCoHybridDrafting2026]
- Only HyCo and SpecEdge-$\epsilon$ have three Spec-Bench generations. One judge evaluation per output does not separate judging from generation variability.[^baeHyCoHybridDrafting2026]

# Contradictions

HyCo's proactive-drafting result on a phone (delivery speed falls from 16.1 to 12.1 tokens/s on Spec-Bench while server saving rises) runs against the SpecEdge paper's finding that proactive drafting lowers inter token latency on RTX 4090 edges.[^baeHyCoHybridDrafting2026] The SpecEdge claim is on the [SpecEdge paper page](parkSpecEdgeScalableEdgeAssisted2025.md). The settings differ in hardware, network, models, and metric. See [Does proactive drafting help when the drafter runs on a phone?](../questions/proactive-drafting-on-a-phone.md).

## Related

- Methods: [HyCo](../methods/hyco.md), [Multi-Token Prediction (MTP)](../methods/multi-token-prediction.md), [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md), [Lossy acceptance rules](../methods/lossy-acceptance.md), [FR-Spec](../methods/fr-spec.md), [SpecInfer](../methods/specinfer.md), [Medusa](../methods/medusa.md) (typical acceptance), [vLLM](../methods/vllm.md) (Marlin kernels), [DFlash](../methods/dflash.md) (cross-family server head)
- Device-cloud systems compared or cited: [SpecEdge](../methods/specedge.md) ([paper](parkSpecEdgeScalableEdgeAssisted2025.md)), [Proactive edge drafting](../methods/proactive-edge-drafting.md), [HAT](../methods/hat.md) ([paper](xieNovelHatShapedDeviceCloud2025.md))
- Drafter-training papers it calls orthogonal: [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md), [PARD](anPARDAcceleratingLLM2025.md)
- Benchmarks and datasets: [Spec-Bench](../benchmarks/spec-bench.md), [InfiniteBench](../datasets/infinitebench.md), [UltraChat](../datasets/ultrachat.md), [MT-Bench](../datasets/mt-bench.md), [GSM8K](../datasets/gsm8k.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md)
- Result: [HyCo cuts server GPU time per token by 38.6% against server-side MTP on Spec-Bench](../results/hyco-server-gpu-time-vs-cloud-mtp.md)
- Open questions: [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md), [Does proactive drafting help when the drafter runs on a phone?](../questions/proactive-drafting-on-a-phone.md), [How can a mobile-efficient drafter be built cheaply for a new target?](../questions/cost-efficient-drafter-construction.md)
- Analysis: [Quantization of the target and the draft in speculative decoding](../analyses/quantization-in-speculative-decoding.md); open question: [How much acceptance does quantizing the draft or the target cost?](../questions/quantization-and-acceptance.md)

[^baeHyCoHybridDrafting2026]: Bae et al. 2026
