---
type: Analysis
title: "Choosing what to verify: Learning to Draft vs. DSpark"
description: How Learning to Draft picks draft tree depth and verification size with two RL policies, how DSpark picks a per-request chain prefix with calibrated confidence and a profiled throughput curve, and where the two differ.
tags: [speculative-decoding, verification-scheduling, draft-tree, adaptive-drafting, confidence-estimation]
sources:
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
---

# Choosing what to verify: Learning to Draft vs. DSpark

## Question

How does [Learning to Draft (LTD)](../papers/zhangLearningDraftAdaptive2026.md) decide the tree or chain that the target model verifies, and how does [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) do it?

## Answer

Both methods start from the same objective, accepted tokens per unit of time, but they reach the verify set differently. LTD learns two policies over an [Eagle3](../methods/eagle-3.md) draft tree for one request. DSpark computes an explicit throughput objective over a chain per request, across every request in the batch.

### LTD: two learned policies over a draft tree

LTD maximizes the throughput of each draft-and-verify cycle, $\lambda_{c}=L_{A}/(T_{\text{draft}}+T_{\text{verify}})$. Draft time grows linearly with draft depth $D$, and verification time grows step-wise with verification size $V$.[^zhangLearningDraftAdaptive2026] It controls these two knobs with two policies:

1. **Tree shape (depth policy).** The tree is grown like a beam search with beam width $W$: the top-$W$ tokens form the first level, and each later round expands every leaf into $W$ children and keeps the top-$W$ of the $W^2$ pool by cumulative path probability.[^zhangLearningDraftAdaptive2026] After each draft forward pass the depth policy outputs CONTINUE or STOP. It sees the log-probabilities of the $W^2$ frontier candidates, the current depth $D$, and the input length $L$.[^zhangLearningDraftAdaptive2026] Eagle3 instead uses a fixed depth of 8.[^zhangLearningDraftAdaptive2026]
2. **Verify set (size policy).** When the depth policy stops, the tree holds $V_{all}=1+W+(D-2)\cdot W^{2}$ candidates. The size policy chooses $V$ from 12 discrete actions mapped linearly from 20 to 240, using the log-probability scores of all tree candidates plus $D$ and $L$.[^zhangLearningDraftAdaptive2026] The $V$ candidates with the highest overall probabilities are flattened with a tree attention mask and verified in one target forward pass.[^zhangLearningDraftAdaptive2026]

So the policies choose only how deep to grow and how many tokens to keep. Which tokens are kept is still a top-$V$ cut by draft probability.[^zhangLearningDraftAdaptive2026]

The reward is the measured cycle throughput $R_{t}=L_{A}/(T_{draft}+T_{verify})$. The depth policy receives it only on STOP, with discount factor $\gamma=0.999$ to counter a bias towards stopping early.[^zhangLearningDraftAdaptive2026] Both policies are trained with [PPO](../methods/ppo.md) on [HumanEval](../datasets/humaneval.md), first separately and then alternately, freezing one while the other trains.[^zhangLearningDraftAdaptive2026]

Because the reward is time, not acceptance, LTD often accepts fewer tokens than grid-searched Eagle3 and is still faster. The paper explains that the policies drop candidates whose time cost is disproportionately high.[^zhangLearningDraftAdaptive2026] With the size policy alone on Vicuna-13B, a throughput reward gives 4.13 mean speedup, against 3.59 for an acceptance-length reward and 3.45 for a time-cost reward.[^zhangLearningDraftAdaptive2026]

### DSpark: a calibrated chain prefix per request, scheduled across the batch

DSpark verifies a chain. The parallel backbone and sequential head draft one $\gamma$-token block per request, and the scheduler picks how long a prefix of that block to send to the target.[^chengDSparkConfidenceScheduledSpeculative2026] The paper argues against trees for serving: tree verification compensates for short blocks, but the large number of verification tokens reduces overall serving throughput.[^chengDSparkConfidenceScheduledSpeculative2026]

1. **Confidence per position.** A confidence head $c_{k}=\sigma\bigl(w^{\top}[h_{k};\,W_{1}[x_{k-1}]]\bigr)$ estimates the probability that draft token $k$ survives, given that every earlier token in the block was accepted. It is trained against the analytical acceptance rate $c_{k}^{*}=1-\tfrac{1}{2}\|p_{k}^{d}-p_{k}^{t}\|_{1}$.[^chengDSparkConfidenceScheduledSpeculative2026]
2. **Calibration.** Sequential Temperature Scaling fits one temperature per position, left to right, to minimize the ECE of the cumulative product $\prod_{i\leqslant k}c_{i}$. Raw ECE is 3%–8%, and STS lowers the average to $\sim$1%.[^chengDSparkConfidenceScheduledSpeculative2026]
3. **Expected gain.** Prefix survival is $a_{r,j}=\prod_{i\leqslant j}c_{r,i}$. Over $R$ requests, the verify batch is $B=\sum_{r=1}^{R}(1+\ell_{r})$ tokens and the expected accepted tokens are $\tau=\sum_{r=1}^{R}\bigl(1+\sum_{j=1}^{\ell_{r}}a_{r,j}\bigr)$.[^chengDSparkConfidenceScheduledSpeculative2026]
4. **Cost.** $\text{SPS}(B)$, the engine's steps per second at batch size $B$, is profiled once when the engine starts and stored as a table.[^chengDSparkConfidenceScheduledSpeculative2026]
5. **Greedy selection.** The scheduler maximizes $\Theta=\tau\cdot\text{SPS}(B)$. It sorts all candidates $(r,j)$ from every request by $a_{r,j}$, admits them one at a time, and stops at the first one that does not raise $\Theta$.[^chengDSparkConfidenceScheduledSpeculative2026] The early stop keeps the scheduler non-anticipating, which losslessness requires. Without it, a counterexample in Appendix A outputs $(0.85,0.15)$ where the target is $(0.7,0.3)$.[^chengDSparkConfidenceScheduledSpeculative2026] The early stop reaches the global maximum if and only if $\Theta$ is unimodal.[^chengDSparkConfidenceScheduledSpeculative2026]

In production the real SPS curve is jagged and step-wise, and per-step scheduling conflicts with CUDA graph replay. DSpark therefore sets a batch capacity $K$ from the confidences of two steps earlier and takes a dynamic top-$K$ of the current candidates, sorted by up-to-date cumulative confidence. The early stop is removed, and the paper argues this stays lossless because the cutoff depends only on information from two steps earlier.[^chengDSparkConfidenceScheduledSpeculative2026] Under moderate concurrency the verify budget grows from MTP-1's static 2 tokens to about 4–6 tokens per request, and it shrinks smoothly as concurrency rises.[^chengDSparkConfidenceScheduledSpeculative2026]

## Evidence

| | LTD | DSpark |
|---|---|---|
| Verified structure | Tree from Eagle3 beam expansion, flattened with a tree attention mask[^zhangLearningDraftAdaptive2026] | Chain: a prefix of the drafted block for each request[^chengDSparkConfidenceScheduledSpeculative2026] |
| Controls draft length? | Yes, depth policy stops after any draft pass[^zhangLearningDraftAdaptive2026] | No, always drafts the full $\gamma$-token block; the paper lists this fixed draft cost as a limitation[^chengDSparkConfidenceScheduledSpeculative2026] |
| Controls verify length? | Yes, size policy picks $V$ from 20 to 240[^zhangLearningDraftAdaptive2026] | Yes, per-request prefix length $\ell_r$[^chengDSparkConfidenceScheduledSpeculative2026] |
| Which tokens are kept | Top-$V$ by draft probability[^zhangLearningDraftAdaptive2026] | Top candidates by calibrated prefix survival $a_{r,j}$, pooled across requests[^chengDSparkConfidenceScheduledSpeculative2026] |
| Acceptance signal | Raw draft log-probabilities as policy inputs[^zhangLearningDraftAdaptive2026] | Separate confidence head, calibrated with STS[^chengDSparkConfidenceScheduledSpeculative2026] |
| Cost model | None explicit; measured cycle time enters the reward[^zhangLearningDraftAdaptive2026] | Profiled $\text{SPS}(B)$ table[^chengDSparkConfidenceScheduledSpeculative2026] |
| Scope of decision | One request's tree per cycle[^zhangLearningDraftAdaptive2026] | All active requests in the verify batch[^chengDSparkConfidenceScheduledSpeculative2026] |
| Training needed | PPO, under 30 GPU hours for three iterations, per target model[^zhangLearningDraftAdaptive2026] | Confidence head trained with the drafter (BCE loss weight 1.0) plus STS on a validation set[^chengDSparkConfidenceScheduledSpeculative2026] |
| Reported effect | Up to 36.4% over Eagle3; 2.24× to 4.32× speedup[^zhangLearningDraftAdaptive2026] | 60%–85% (V4-Flash) and 57%–78% (V4-Pro) faster per-user generation than MTP-1 at matched throughput, live traffic[^chengDSparkConfidenceScheduledSpeculative2026] |

LTD's observation ablation is relevant to DSpark's design choice. Adding entropy or hidden states to the size policy's input did not help: P+D+L gives 4.13 mean speedup, P+D+L+H 4.10, and P+D+L+E 4.11 on Vicuna-13B.[^zhangLearningDraftAdaptive2026] DSpark instead feeds the drafter hidden state into a trained confidence head.[^chengDSparkConfidenceScheduledSpeculative2026] The two results come from different drafters and decision problems, so they do not contradict each other.

## Caveats

- The two methods are not compared in any paper in the wiki. LTD is built on Eagle3 tree drafting.[^zhangLearningDraftAdaptive2026] DSpark's offline experiments use chain drafting with the scheduler disabled, and the scheduler is evaluated only in live DeepSeek-V4 traffic.[^chengDSparkConfidenceScheduledSpeculative2026] See [the open question](../questions/learned-vs-confidence-scheduled-verification.md).
- DSpark gives an argument for why its scheduler is lossless.[^chengDSparkConfidenceScheduledSpeculative2026] LTD states that speculative decoding does not change the target's output distribution, and on that ground does not evaluate generation quality.[^zhangLearningDraftAdaptive2026] The raw text of LTD contains no analysis of whether its policies' choices could bias the output, which is the issue DSpark's Appendix A raises.
- Reading of this wiki, not a claim of either paper: since DSpark drafts the whole block in one parallel pass, an LTD-style depth policy has no sequential passes to stop. The nearest counterpart is the difficulty-aware early exit that DSpark lists as future work.[^chengDSparkConfidenceScheduledSpeculative2026]
- DSpark's scheduler assumes that engine throughput depends mainly on $B$, not on context length.[^chengDSparkConfidenceScheduledSpeculative2026]

## Related

- Papers: [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md), [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md)
- Methods: [DSpark](../methods/dspark.md), [LTD](../methods/ltd.md), [Confidence-scheduled verification](../methods/confidence-scheduled-verification.md), [Tree-based speculation](../methods/tree-based-speculation.md), [EAGLE-3](../methods/eagle-3.md), [Speculative decoding](../methods/speculative-decoding.md)
- Analyses: [DFlash, DSpark, and EAGLE-3 drafting comparison](dflash-dspark-eagle-3-drafting-comparison.md), [Speculative drafter papers on a mobile NPU](speculative-drafter-papers-on-mobile-npu.md)
- Open questions: [Learned policy or calibrated confidence for choosing the verify set?](../questions/learned-vs-confidence-scheduled-verification.md), [Does speculative decoding still help at large batch sizes?](../questions/speculative-decoding-at-large-batch.md)

[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
