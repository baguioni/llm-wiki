---
type: Dataset
title: Spider
description: Text-to-SQL dataset that two of the wiki's papers use as a structured-output workload for speculative-decoding experiments under distribution shift.
tags: [text-to-sql, speculative-decoding, distribution-shift]
sources:
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
---

# Spider

## Overview

Spider is a dataset of manually-annotated questions and SQL responses over 200 different databases with multiple tables, covering 138 different domains.[^oliaroSuffixDecodingExtremeSpeculative2024] The model generates executable SQL queries from natural-language questions given a database schema.[^wangWhenRLMeets2026] Two papers in this wiki use it as a structured-output workload for [speculative decoding](../methods/speculative-decoding.md), in both cases to study a shift in the request distribution.[^oliaroSuffixDecodingExtremeSpeculative2024][^wangWhenRLMeets2026] Neither reports text-to-SQL accuracy.

## Composition

- Aurora characterizes it as strongly structured SQL generation with strict syntax constraints and frequent keywords and punctuation.[^wangWhenRLMeets2026]
- SuffixDecoding measures an average empirical entropy of 2.50 for Spider, against 3.43 for WildChat and 2.95 for Magicoder.[^oliaroSuffixDecodingExtremeSpeculative2024]
- SuffixDecoding calls its workload SpiderSQL and uses the instructions from DAIL-SQL, which are LLM prompts with instructions to answer Spider questions with structured SQL code.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Aurora samples 7k prompts from it.[^wangWhenRLMeets2026]

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) | Target workload of the input-distribution-shift ablation: a suffix tree built from 4,000 WildChat output examples is then served SpiderSQL requests | Simulated verifier | 1.5× speedup and 8% acceptance rate without adaptation, against 2.6× and 20% for a tree trained on 500 SpiderSQL examples[^oliaroSuffixDecodingExtremeSpeculative2024] |
| [Aurora](../papers/wangWhenRLMeets2026.md) | Source of the Text-to-SQL prompts, 7k of a 44k mixed-domain request stream used in ordered (domain shift) and mixed traffic | Online draft training with EAGLE-3; Qwen3-8B target in the day-0 study | No per-dataset number. On the whole mixed stream the acceptance length reaches 3.08 and throughput stabilizes at 302.3 tokens/s[^wangWhenRLMeets2026] |

## Speed metrics

These are speculative-decoding numbers measured with this dataset's prompts. They say nothing about text-to-SQL accuracy.

### [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md): input distribution shift

This ablation uses the paper's simulated verifier on offline traces, which simulates speculative verification for greedy sampling by comparing draft tokens with ground-truth responses. The paper does not name the model behind those traces in this ablation.[^oliaroSuffixDecodingExtremeSpeculative2024]

| Model | Temp. | Method | Speedup | Acceptance rate |
|---|---|---|---|---|
| not stated | 0 (greedy, simulated) | SuffixDecoding, tree from 4,000 WildChat output examples, no adaptation | $1.5\times$ | $8\%$ |
| not stated | 0 (greedy, simulated) | SuffixDecoding, tree trained on 500 SpiderSQL examples | $2.6\times$ | $20\%$ |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

After observing 500 SpiderSQL requests and adapting online, SuffixDecoding's performance is almost indistinguishable from offline training on the 500 SpiderSQL examples.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md)
- Datasets in the same request stream: [GSM8K](gsm8k.md), [chatbot_instruction_prompts](chatbot-instruction-prompts.md)

[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^wangWhenRLMeets2026]: Wang et al. 2026
