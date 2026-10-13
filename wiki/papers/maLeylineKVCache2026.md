---
type: Paper
title: "Leyline: KV Cache Directives for Agentic Inference"
description: Serving-side primitive that lets an agent policy issue (span, replacement) directives to splice the KV cache in place, using a closed-form RoPE delta-rotation on MLA models so the unchanged prefix and downstream slots are not re-prefilled.
tags: [kv-cache, agentic-inference, llm-serving, prefix-caching, rope, mla, context-management, ai899]
collections: [ai899]
authors: [Bole Ma, Jan Eitzinger, Harald Köstler]
doi: 10.48550/arXiv.2606.01065
arxiv: "2606.01065"
arxiv_version: 2606.01065v1
sources:
  - id: maLeylineKVCache2026
    resource: zotero://select/items/@maLeylineKVCache2026
    title: "Leyline: KV Cache Directives for Agentic Inference"
---

# Leyline: KV Cache Directives for Agentic Inference

Text source: arXiv HTML, version `2606.01065v1`.

## Summary

KV cache management assumes a chatbot workload where the cache grows append-only, so prefix caching and forward-only eviction are correct by construction.[^maLeylineKVCache2026] Agentic LLMs break this in two ways. *Reuse*: identical content moves to new absolute positions between turns, which invalidates exact-prefix caches. *Mutation*: a policy needs to remove or replace a span of cached content (a failed tool call, a stale tool output) and continue without re-prefilling everything after it.[^maLeylineKVCache2026] The paper targets mutation, which today is handled by editing the message list and re-prefilling.[^maLeylineKVCache2026]

Leyline is a serving-side primitive for policy-driven cache editing. A policy emits a declarative directive that says what to edit, and a per-architecture kernel splices the cache in place and restores position correctness by rotating the cached positional key band of downstream slots (the $\delta$-rotation).[^maLeylineKVCache2026] The rotation kernel is borrowed from the authors' earlier Irminsul work, and the directive layer around it is the new contribution.[^maLeylineKVCache2026] The paper reports that the splice kernel lifts replay cache-hit by $+11.2$ pp and cuts latency by up to $241$ ms, and that a ten-line truncation policy routed through the same interface lifts agentic solve rate by $+14.3$ pp on debug-gym.[^maLeylineKVCache2026]

## Contributions

- A distinction between the reuse and mutation problems in agentic KV cache management, with mutation identified as the open sub-problem.[^maLeylineKVCache2026]
- The directive abstraction: a 4-tuple interface with a declared semantic mode and a pluggable policy layer that decouples what to edit (policy) from how to splice it (kernel).[^maLeylineKVCache2026]
- A semantic-edit channel as a new serving-stack interface: a span-level edit layer above block-level KV storage.[^maLeylineKVCache2026]
- A two-leg validation: a mechanism leg (three-arm microbenchmark on the live SGLang scheduler) and a policy leg (truncation policy on debug-gym).[^maLeylineKVCache2026]

## Method

### The directive

A directive is a 4-tuple $D=(s_{\mathrm{start}},\,s_{\mathrm{end}},\,R,\,m)$. $[s_{\mathrm{start}},s_{\mathrm{end}})$ is the token-index range being replaced, $R$ is the replacement token sequence (often a short stub), and $m\in\{\textsc{amortize},\,\textsc{forget}\}$ is the semantic mode.[^maLeylineKVCache2026] Multiple non-overlapping directives may be applied per turn, and an overlapping submission is rejected at apply-time.[^maLeylineKVCache2026]

- **amortize (default).** The contract is positional, not informational: after applying $D$, the cache produces outputs equivalent to one built from the *original* prompt with downstream positions reindexed by $\Delta=|R|-(s_{\mathrm{end}}-s_{\mathrm{start}})$. Downstream behavior reflects the cache's attention to the original chunk, not the stub. This is deliberately weaker than "equivalent to re-prefill of the substituted prompt".[^maLeylineKVCache2026]
- **forget.** For true content forgetting (redaction, retention-mandated deletion, correcting an upstream tool error), the serving stack routes the edit to a standard prefix-trimmed re-prefill. It adds no new kernel work.[^maLeylineKVCache2026]

### $\delta$-rotation

Under Multi-head Latent Attention (MLA), cached K splits into $K_{\mathrm{nope}}$ (no position) and $K_{\mathrm{pe}}$ (rotated by RoPE by absolute position): $K_{\mathrm{pe}}[i]=R(i)\cdot K_{\mathrm{pe}}^{\mathrm{raw}}[i]$.[^maLeylineKVCache2026] After a splice, every downstream token at position $i\geq s_{\mathrm{end}}$ shifts by $\Delta$, and the correction is:[^maLeylineKVCache2026]

$$
K_{\mathrm{pe}}^{\mathrm{new}}[i]=R(\Delta)\cdot K_{\mathrm{pe}}[i]
$$

By RoPE's closure $R(a)R(b)=R(a+b)$ this equals the $K_{\mathrm{pe}}$ that a prefill at position $i+\Delta$ would have produced. The correction is one matmul per slot.[^maLeylineKVCache2026] The single-rotation bf16 drift bound is $4.7{\times}10^{-3}$ rel-L2, from the earlier Irminsul work.[^maLeylineKVCache2026]

### Kernel effect of one directive

1. Tokens before $s_{\mathrm{start}}$: the radix cache matches the prompt as usual, so the unedited prefix survives.[^maLeylineKVCache2026]
2. The evicted span's $K_{\mathrm{pe}}$, $K_{\mathrm{nope}}$, and $V$ are freed, and the replacement $R$ is prefilled fresh into new slots at $[s_{\mathrm{start}},s_{\mathrm{start}}+|R|)$.[^maLeylineKVCache2026]
3. Downstream slots have only $K_{\mathrm{pe}}$ rotated by $\Delta$ and are reindexed to $i+\Delta$. Their $K_{\mathrm{nope}}$ and $V$ are untouched.[^maLeylineKVCache2026]

No Q tensor is cached, so no Q reindexing is needed.[^maLeylineKVCache2026] Several directives in one turn are processed left-to-right, and $\Delta$ may be of either sign.[^maLeylineKVCache2026]

### Serving-stack integration

- An offline replay kernel loads the model via HuggingFace transformers and applies the rotation in process. A ${\sim}200$-LOC SGLang RadixCache patch populates a content-hash side index inside the live engine and routes matched directives through the same rotation kernel.[^maLeylineKVCache2026]
- *Role A* returns a patched match result with borrowed slots that the request frees at completion. *Role B* inserts the spliced range into the radix trie and re-runs the unwrapped `match_prefix`, so spliced KV is discoverable by future requests without a hook at lookup time.[^maLeylineKVCache2026]
- RoPE pairing: DSv2-Lite's MLA uses interleaved pairing and Llama- and Qwen2-style models use half-split. The kernel reads `rotary_is_neox_style` per layer. The post-fix kernel was validated bit-exact against full prefill across $\Delta\in\{1,21,48,76,512,2000\}$ and end-to-end for $|\Delta|$ up to $\approx 4531$ on DSv2-Lite.[^maLeylineKVCache2026]
- Policy interface: a single `Policy.transform(messages, turn_idx)` $\to$ `messages` method. Leyline computes the diff against the previous turn and applies it through the kernel.[^maLeylineKVCache2026]
- Only the rotation kernel is MLA-specific. The directive interface, radix-cache integration, and policy interface depend only on token spans.[^maLeylineKVCache2026]

### Positioning (Table 1)

| System | Targets | Correct? | Reuse? | Granularity |
|---|---|---|---|---|
| Anthropic prompt caching | read-side reuse | n/a | 5-min / 1-h TTL | breakpoint |
| Anthropic clear_tool_uses | mutation | re-prefill | no (radix gone) | turn |
| OpenAI prompt caching | read-side reuse | n/a | prefix only | token-prefix |
| Google context caching | read-side reuse | n/a | cached-object | object |
| H2O / SnapKV / StreamingLLM | neither | forward-only | n/a | token |
| [LMCache](../methods/lmcache.md) | storage | n/a | prefix | 256-tok block |
| [CacheBlend](../methods/cacheblend.md) | reuse (MHA) | dynamic 15% recompute | yes | chunk |
| [EPIC](../methods/epic.md) / LegoLink | reuse (MHA/GQA) | static $k$-first recompute | yes | chunk |
| In-place K/V splice (naïve) | mutation | no (stale RoPE) | yes | arbitrary |
| [Irminsul](../methods/irminsul.md) | reuse (MLA) | hash + $\delta$-rotation | yes | CDC |
| Leyline (this paper) | mutation (MLA) | directive + $\delta$-rotation | yes (radix kept) | turn |

All rows: [^maLeylineKVCache2026]

## Experiments & Results

### Setup

- Models (parameter counts total / active): DeepSeek-V2-Lite (16B / 2.4B), JoyAI-LLM Flash (48B / 3B), GLM-4.7-Flash (30B / 3B), Moonlight-16B-A3B (16B / 3B). All four are MLA models.[^maLeylineKVCache2026]
- Hardware: GLM-4.7-Flash and JoyAI-LLM Flash on $4{\times}$ NVIDIA H200 with SGLang tensor-parallelism (TP$=$4); Moonlight-16B-A3B on $2{\times}$ H100; DeepSeek-V2-Lite on $1{\times}$ H100.[^maLeylineKVCache2026]
- Software: SGLang 0.5.2 with the Leyline patch; debug-gym 1.3.0.[^maLeylineKVCache2026]
- All correctness replays use greedy decoding over bf16 model weights.[^maLeylineKVCache2026]

### Single-prompt replay equivalence

The prompt buries the calculation $25+9=34$ (57 tokens) mid-prompt, and a directive replaces it with an 11-token stub ($\Delta{=}-46$).[^maLeylineKVCache2026]

| Path | Predicted answer |
|---|---|
| Full-context (original prompt prefilled) | '34' |
| Re-prefill (stub-substituted prompt prefilled) | '0' |
| Leyline (original prefilled, then directive applied) | '34' |

All rows: [^maLeylineKVCache2026]

### Mechanism leg: three-arm message-edit microbenchmark (Table 3)

DeepSeek-V2-Lite on a single H100, greedy decode, $N_{\mathrm{sessions}}{=}16$, $K{=}6$ turns/session, $L_{\mathrm{sys}}{\approx}4096$, $L_{\mathrm{turn}}{\approx}2048$, $L_{\mathrm{out}}{=}128$, anchored CDC active. Final-turn prompt length is $\approx 17$ K tokens. Arms: cache-off (SGLang with `--disable-radix-cache`), radix (vanilla SGLang), splice (Leyline).[^maLeylineKVCache2026]

| $C$ | Replay p50 e2e, cache-off (ms) | radix (ms) | splice (ms) | splice vs radix | Cache hit, cache-off (%) | radix (%) | splice (%) | Chunks spliced |
|---|---|---|---|---|---|---|---|---|
| 1 | 4278 | 4087 | 4036 | $-51$ | 0.0 | 49.6 | 60.8 | 203 |
| 4 | 5481 | 4729 | 4644 | $-85$ | 0.0 | 49.6 | 60.8 | 167 |
| 8 | 7120 | 5533 | 5292 | $-241$ ($-4.4\%$) | 0.0 | 49.6 | 60.8 | 203 |
| 16 | 10217 | 7166 | 7211 | $+45$ (noise) | 0.0 | 49.6 | 60.8 | 203 |

All rows: [^maLeylineKVCache2026]

- Replay-phase p99 e2e at $C{=}8$: splice $5298$ ms against radix $5543$ ms ($-245$ ms, $-4.4\%$). At $C{=}16$: $7218$ ms vs $7171$ ms.[^maLeylineKVCache2026]
- Splice-vs-radix first-token argmax agreement: $100\%/97.7\%/98.4\%/94.5\%$ at $C{\in}\{1,4,8,16\}$; full 16-token head: $99.2\%/95.3\%/93.0\%/67.2\%$. The cache-off vs radix reference floor is $97.7\%/97.7\%/97.7\%/94.5\%$ first-token and $85.2\%/93.8\%/90.6\%/68.8\%$ full head.[^maLeylineKVCache2026]
- Cumulative bytes_rotated $\geq 740$ MB; cumulative in-place rotation-kernel time $\leq 2.9$ ms per run.[^maLeylineKVCache2026]
- Without the anchored CDC chunker, the content-hash match rate at $C{=}16$ collapses to zero. An earlier small-prompt sweep ($L_{\mathrm{sys}}{=}512$, $L_{\mathrm{turn}}{=}256$, $L_{\mathrm{out}}{=}64$) with the legacy chunker produced $0$ chunks_spliced.[^maLeylineKVCache2026]

### Policy leg: debug-gym mini_nightmare (Table 2)

JoyAI-LLM Flash on H200 TP=4 via SGLang. Baseline `keep_all` (32 trials, 8 tasks $\times$ 4 seeds). Treatment `truncate_older_than(n=2)` with `max_chars=200` (33 trials), which truncates tool messages older than 2 turns to a 200-character head/tail stub. max=50 agent steps per task. Both arms use the standard re-prefill path.[^maLeylineKVCache2026]

| Task | Baseline | Treatment |
|---|---|---|
| counter | 4/4 | 4/4 |
| grader | 1/4 | 1/4 |
| patcher | 0/4 | 0/4 |
| purr | 2/4 | 2/4 |
| sci_calculator | 2/4 | 2/4 |
| shopping_cart | 0/4 | 3/4 |
| sum_tree | 1/4 | 2/4 |
| tomorrow_date | 0/4 | 0/4 |
| Overall | 31.2% | 45.5% |

All rows: [^maLeylineKVCache2026]

- Overall: $10/32=31.2\%$ (baseline) to $15/33=45.5\%$ (treatment), a $+14.3$ pp absolute gain.[^maLeylineKVCache2026]
- Across the 31 paired (task, seed) cells, the policies agree on 17 outcomes. Of the 14 cells where they disagree, the treatment wins 9 and the baseline wins 5.[^maLeylineKVCache2026]
- A ninth task, pandas_dataframe, was excluded because it needs a dataset fetched over the network.[^maLeylineKVCache2026]

### Real-trace long-context replay

50-step debug-gym trajectory (07be28b9/shopping_cart), prompts growing from 334 to ${\sim}28$K tokens, $C{=}1$.[^maLeylineKVCache2026]

| Arm | sum-e2e | Replay cache-hit |
|---|---|---|
| Vanilla SGLang RadixCache | $52.65$ s | $27.6\%$ |
| Leyline (Role B Level 2 + fp32 rotation) | $49.85$ s | $27.8\%$ |

All rows: [^maLeylineKVCache2026]

- This is a $5.3\%$ e2e improvement with $48/50$ first-token argmax agreement against the radix arm. $\sim$95% of the timing win is attributable to the fp32 rotation mitigation. fp32 rotation on / Role B L2 off reaches $49.62$ s.[^maLeylineKVCache2026]
- On a second trajectory (0f724375/shopping_cart, $91.6\%$ RadixCache hit-rate) the splice is $0.6\%$ slower than radix and $20/20$ bit-identical.[^maLeylineKVCache2026]

### Cross-tenant workload and KV accounting

- Cross-tenant Zipf workload at $C{=}4$ (two tenants, 8 articles, $1500$-character bodies, $32$ requests/tenant): without warm-start, cand_total${=}6$ and chunks_spliced${=}2$. With manifest warm-start, cand_total${=}96$ and chunks_spliced${=}16$, and tenant-1 e2e $p_{50}$ drops from $1.016$ s to $0.953$ s ($-6.2\%$). The manifest has $15$ unique chunks ($\sim$4 KB) and warm-up completes in ${\sim}1.2$ s.[^maLeylineKVCache2026]
- Per-token KV in the DSv2-Lite MLA pool is $(512+64)\times 27\times 2=31{,}104$ bytes.[^maLeylineKVCache2026]
- KV reused: $52.5$ MB on the long-context replay ($+1{,}750$ tokens over the radix arm); $27.9$ MB on the cross-tenant $C{=}4$ workload with warm-start vs $3.98$ MB without.[^maLeylineKVCache2026]
- Splice-OFF peak pool occupancy at $C{=}4$: 2-tenant $53.6$ MB, 3-tenant $74.3$ MB, 4-tenant $97.5$ MB, 8-tenant $182.0$ MB. Splice ON does not reduce peak pool occupancy: at 4-tenant both peaks are $3{,}135$ slots of $1{,}698{,}846$. 2-tenant ON + warmup is $65.7$ MB and 4-tenant ON + warmup is $112.4$ MB.[^maLeylineKVCache2026]

### Cross-architecture counter-trajectory replay (Table 4)

12-step counter trajectory, 6 edit steps, 128-token greedy decode. Mean CP is the mean common-prefix length in tokens out of 128. Mean CP values are taken from the paper's body text, because the table cells are garbled in the extracted source.[^maLeylineKVCache2026]

| Model | Tool-name agreement | 1st-tok vs full | 1st-tok vs re-prefill | Mean CP vs full | Mean CP vs re-prefill |
|---|---|---|---|---|---|
| DSv2-Lite | 6/6 | 6/6 | 6/6 | 128 | 128 |
| JoyAI-LLM Flash | 4/4 | 3/6 | 3/6 | $41.8$ (rounded to $42$) | $41.8$ (rounded to $42$) |
| GLM-4.7-Flash | 2/2 | 4/6 | 4/6 | $6.2$ (table $6$) | $9.7$ (table $10$) |
| Moonlight-16B-A3B | 3/3 | 6/6 | 5/6 | $75$ | $50$ |

All rows: [^maLeylineKVCache2026]

### Randomized edit-suite stress test (Table 5)

$N{=}40$ trials per model per stub mode, span sizes uniform in $[8,200]$ tokens, 1-2 non-overlapping edits per turn, $\Delta$ over both signs. *rand*: stub is uniform in-vocab tokens. *sem*: stub is a tokenized placeholder string.[^maLeylineKVCache2026]

| Model (stub) | 1st-tok vs full | 1st-tok vs rp | Leyline = full only (when full ≠ rp) | Leyline = rp only (when full ≠ rp) |
|---|---|---|---|---|
| DSv2-Lite (rand) | 40/40 | 40/40 | 0/0 (vacuous) | 0/0 (vacuous) |
| DSv2-Lite (sem) | 40/40 | 40/40 | 0/0 (vacuous) | 0/0 (vacuous) |
| Moonlight (rand) | 37/40 | 23/40 | 14/17 | 0/17 |
| Moonlight (sem) | 38/40 | 27/40 | 11/13 | 0/13 |
| JoyAI-LLM Flash (rand) | 0/40 | 10/40 | 0/10 | 10/10 |
| JoyAI-LLM Flash (sem) | 0/40 | 20/40 | 0/20 | 20/20 |
| GLM-4.7-Flash (rand) | 1/40 | 6/40 | 1/23 | 6/23 |
| GLM-4.7-Flash (sem) | 2/40 | 2/40 | 2/28 | 2/28 |

All rows: [^maLeylineKVCache2026]

The paper attributes the JoyAI and GLM results to edit position: the random harness splices at arbitrary token offsets that cut across chat-template structure, while policy-derived edits splice at chat-message boundaries.[^maLeylineKVCache2026]

### Long-horizon replay (Table 7)

50-step sum_tree trajectory, first-token agreement against the full-context baseline.[^maLeylineKVCache2026]

| Model | Valid edit steps | 1st-tok @ single-edit | 1st-tok @ multi-edit |
|---|---|---|---|
| DSv2-Lite | 49 | 16/16 (100%) | 33/33 (100%) |
| GLM-4.7-Flash | 45 | 13/16 (81%) | 26/29 (90%) |
| Moonlight-16B-A3B | 39 | 9/16 (56%) | 13/23 (57%) |
| JoyAI-LLM Flash | 43 | 2/16 (12%) | 1/27 (4%) |

All rows: [^maLeylineKVCache2026]

On JoyAI, Leyline tracks the references at $67\%$ (single-edit) and $72\%$ (multi-edit) on tool-name under a permissive multi-format parser.[^maLeylineKVCache2026]

### Numerics

Chained-rotation drift in bf16 against a fresh-RoPE-at-target-position reference (Table 6), $10$ seeds per row.[^maLeylineKVCache2026]

| $N$ | rel-L2 vs fresh | max-abs vs fresh |
|---|---|---|
| 2 | $4.3{\times}10^{-3}$ | $4.7{\times}10^{-2}$ |
| 5 | $5.6{\times}10^{-3}$ | $6.2{\times}10^{-2}$ |
| 10 | $7.5{\times}10^{-3}$ | $7.8{\times}10^{-2}$ |
| 20 | $1.1{\times}10^{-2}$ | $1.2{\times}10^{-1}$ |
| 50 | $1.7{\times}10^{-2}$ | $1.9{\times}10^{-1}$ |
| 100 | $2.6{\times}10^{-2}$ | $3.3{\times}10^{-1}$ |

All rows: [^maLeylineKVCache2026]

- Growth from $N{=}2$ to $N{=}100$ is $6.1{\times}$ in rel-L2.[^maLeylineKVCache2026]
- bf16 K-storage floor: a uniform $\sim$1-3% per-entry error from bf16 storage, independent of $\Delta$, vs fp32 where the same kernel returns $<\!10^{-3}$ error at every tested $(p,\Delta)$.[^maLeylineKVCache2026]
- Rotation algebra across architectures (Table 8), worst rel-L2 in bf16: MLA ($d{=}64$, rope_theta $3.2{\times}10^{7}$) $4.3{\times}10^{-3}$; MLA alternative tuning $4.8{\times}10^{-3}$; GQA Llama-3.1-style $4.6{\times}10^{-3}$; GQA Qwen-3-style $4.7{\times}10^{-3}$; GQA Phi-3-style $4.9{\times}10^{-3}$.[^maLeylineKVCache2026]

### Live-model GQA microbenchmark (Table 9)

| Model | Trials | Refs diverge | Leyline ≡ full / diverging | Leyline ≡ rp / diverging |
|---|---|---|---|---|
| Llama-3.1-Minitron-4B-Width-Base | 8 | 8/8 | 1/8 | 1/8 |
| Qwen3-4B | 8 | 6/8 | 0/6 | 6/6 |

All rows: [^maLeylineKVCache2026]

### Stub-content ablation

A $4\times 3\times 2$ ablation (stub modes faithful, pad, scrambled, empty; trajectories counter, shopping_cart, sum_tree; models DeepSeek-V2-Lite, JoyAI-LLM Flash). On DeepSeek-V2-Lite all four stub modes produce bit-identical character-level outputs within each trajectory. On JoyAI-LLM Flash, tool-name agreement holds at $\geq 0.98$ across all 12 cells.[^maLeylineKVCache2026]

## Limitations

- **Architecture coverage.** The rotation kernel is MLA-specific. On live GQA models the rotation acts on dimensions that also carry content, and the model-side sensitivity to ill-formed cache state is stronger. A boundary-token recomputation pass is named as the next step.[^maLeylineKVCache2026]
- **Numerics.** $100$ chained rotations show $2.6{\times}10^{-2}$ rel-L2. Drift for a slot re-rotated thousands of times per session was not measured.[^maLeylineKVCache2026]
- **bf16 storage floor.** Argmax flips happen on $\sim$4% of prompts on the long-context replay. Outputs are byte-identical to a full prefill only on prompts with logit margin above the noise floor.[^maLeylineKVCache2026]
- **Position sensitivity.** JoyAI and GLM are highly sensitive to position-arbitrary (mid-message, mid-template-tag) splices.[^maLeylineKVCache2026]
- **Workload coverage.** The deployment covers 8 debug-gym mini_nightmare tasks $\times$ 4 seeds $\times$ 2 policies at a single truncation threshold on one model. No hyperparameter search was run.[^maLeylineKVCache2026]
- **No composed ablation.** The mechanism leg runs on synthetic prompts and the policy leg runs under the standard re-prefill arm. The solve-rate gain is a property of the truncation policy and does not isolate any contribution from the splice kernel.[^maLeylineKVCache2026]
- **Warm-start scope.** Discovery activation is shown only at 2-tenant $C{=}4$. The 3-, 4-, and 8-tenant $C{=}4$ runs and the 2-tenant $C{=}8$ run all reach cand_total${=}0$ because of a candidate-filter issue.[^maLeylineKVCache2026]
- **Memory.** The savings are re-prefill compute and pool writes avoided, not peak allocator memory.[^maLeylineKVCache2026]
- **Workload-conditional wins.** When RadixCache already covers the workload, there is no headroom for the splice.[^maLeylineKVCache2026]
- The DECAY, PIN, SCRATCH, and SHARE verbs are sketched, and their experimental validation is future work.[^maLeylineKVCache2026]

## Related

- Methods proposed or built on: [Leyline](../methods/leyline.md), [Irminsul](../methods/irminsul.md), [RoPE](../methods/rope.md), [Multi-head Latent Attention](../methods/mla.md), [KV cache](../methods/kv-cache.md), [Prefix caching](../methods/prefix-caching.md)
- Systems compared or built on: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md), [LMCache](../methods/lmcache.md), [CacheBlend](../methods/cacheblend.md), [EPIC](../methods/epic.md)
- Benchmarks: [debug-gym](../benchmarks/debug-gym.md)
- Papers in this wiki cited by this paper: [SGLang](zhengSGLangEfficientExecution2024.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md)

[^maLeylineKVCache2026]: Ma et al. 2026
