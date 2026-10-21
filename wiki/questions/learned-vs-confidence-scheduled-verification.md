---
type: Open Question
title: Learned policy or calibrated confidence for choosing the verify set?
description: Learning to Draft picks tree depth and verification size with RL policies and DSpark picks chain prefixes with calibrated confidence and a profiled throughput curve, but no paper compares the two or tests either on the other's drafter.
tags: [speculative-decoding, verification-scheduling, draft-tree, confidence-estimation]
sources:
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
---

# Learned policy or calibrated confidence for choosing the verify set?

## Question

To decide how many draft tokens the target verifies, is it better to use a learned RL policy rewarded by measured throughput (LTD) or calibrated acceptance confidence with a profiled cost table (DSpark)? Does the answer change between tree and chain drafts, and between a single request and a loaded batch?

## Why it matters

Both methods report gains from adapting the verify set, but on different drafters, baselines, and hardware. A choice between them for a new setting, such as a block drafter or a phone NPU with step-wise verify cost, has no direct evidence behind it.

## Evidence so far

- LTD trains a depth policy and a size policy with PPO on Eagle3 trees, rewarded by cycle throughput, and reports up to 36.4% over Eagle3.[^zhangLearningDraftAdaptive2026] Its baselines are other dynamic depth and size methods on Eagle3 (DDD, SVIP, Gammatune, C2T, Disco, SpecDec++), only on Llama-3.1-8B and Vicuna-13B.[^zhangLearningDraftAdaptive2026]
- DSpark sorts chain-prefix candidates across requests by calibrated survival probability and maximizes $\tau\cdot\text{SPS}(B)$.[^chengDSparkConfidenceScheduledSpeculative2026] Its scheduler is evaluated only in live DeepSeek-V4 traffic against MTP-1, and its offline experiments disable the scheduler.[^chengDSparkConfidenceScheduledSpeculative2026]
- DSpark finds that raw confidence is miscalibrated (ECE 3%–8%) and calibrates it with STS to $\sim$1%.[^chengDSparkConfidenceScheduledSpeculative2026] LTD feeds raw draft log-probabilities to its policies, and adding entropy or hidden states did not improve the size policy (4.13 vs. 4.11 and 4.10 mean speedup on Vicuna-13B).[^zhangLearningDraftAdaptive2026]

## Conflicting claims

None directly. The papers address different settings: LTD a single request's tree,[^zhangLearningDraftAdaptive2026] DSpark a batch of chains under serving load.[^chengDSparkConfidenceScheduledSpeculative2026]

## What would resolve it

- Run both selectors on the same drafter, target, and hardware: for example, DSpark's scheduler on an Eagle3 tree with top-$V$ selection by calibrated confidence, against LTD's size policy.
- Run LTD's size policy on a DSpark or DFlash chain, at batch size 1 and under concurrency.
- Report wall-clock speedup offline for DSpark's scheduler, which the paper does not do.[^chengDSparkConfidenceScheduledSpeculative2026]

## Related

- [Choosing what to verify: Learning to Draft vs. DSpark](../analyses/choosing-what-to-verify-ltd-vs-dspark.md)
- [Does speculative decoding still help at large batch sizes?](speculative-decoding-at-large-batch.md)
- Papers: [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md), [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md)

[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
