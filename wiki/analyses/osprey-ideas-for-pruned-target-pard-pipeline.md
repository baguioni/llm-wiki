---
type: Analysis
title: Where Osprey's ideas fit a pruned-target PARD pipeline
description: Maps Osprey's four stages onto my pipeline of Minitron pruning of the target, off-policy KD recovery, and PARD fine-tuning; zero-initialized feature injection and recovery-budget checks transfer directly, a pretrained small-LM source is an alternative first step, and vocabulary alignment, TTT, and cross-target reuse mostly do not apply.
tags: [speculative-decoding, draft-model, parallel-drafting, structured-pruning, knowledge-distillation, speculative-drafter, mobile-specedge, pard]
question: For a pipeline of Minitron pruning + off-policy KD recovery + PARD fine-tuning, where could Osprey's ideas be inserted, added, or used as replacements?
sources:
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Where Osprey's ideas fit a pruned-target PARD pipeline

## Question

My pipeline is (1) Minitron pruning of the target, (2) off-policy KD recovery of the pruned model, and (3) PARD fine-tuning into a parallel drafter. Where could [Osprey](../methods/osprey.md)'s ideas be inserted, added, or used as replacements? The pipeline is the one described in [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md); it is my plan, not a paper's. It has since been run once on Qwen3-14B; see section F.

## Answer

| My step | Osprey counterpart | Verdict |
|---|---|---|
| (1) Minitron-prune the target | Stage 1: depth-prune an off-the-shelf small LM | **Alternative**, not an add-on |
| (2) Off-policy KD recovery from the target | Stage 2: generic NTP pretraining, target-agnostic | **Keep (2)**; borrow the budget check, data breadth, and AL-based evaluation |
| between (2) and (3), if PARD-2 features are used | Stage 3: zero-initialized feature injection | **Insert** |
| (2) → (3) vocabulary | Stage 3: vocabulary alignment | Not needed (same tokenizer) |
| (3) PARD fine-tuning | Stage 4: online target distillation with TTT | **Add** live target logits; TTT does not transfer |

### A. Step 1: a pretrained small LM is an alternative source, not an addition

Osprey keeps the first $N$ blocks of an off-the-shelf small LM ($N\in\{1,2,3,4\}$) and states that the source "may belong to a different model family and may use a different tokenizer" from the target.[^bieOspreyTargetagnosticPretraining2026] One Qwen3-4B backbone, pruned to 2 layers, was adapted to Qwen3-8B, Llama-3.3-70B-Instruct, and MiniMax-M2.5.[^bieOspreyTargetagnosticPretraining2026] This is a different answer to the same problem my step 1 solves, a target without a small sibling. The two routes trade off:

- Pruning the target keeps its tokenizer and weights, but the compression ratio is extreme. Qwen3-14B to a 0.6B shape is about 23× (arithmetic in the [open question](../questions/pruned-target-to-parallel-drafter.md)), while Minitron's largest tested cut removes 73.3% of the weights.[^muralidharanCompactLanguageModels2024]
- Pruning a small LM starts from a model that is already small, but Osprey's 2-layer body works as an EAGLE-3 drafter that receives target features.[^bieOspreyTargetagnosticPretraining2026] A PARD-1 drafter has no target features,[^anPARDAcceleratingLLM2025] so whether a 2-layer body is enough for it is untested.
- Osprey prunes by depth. Minitron's best practice for models up to 15B is to prefer width pruning over depth.[^muralidharanCompactLanguageModels2024]

### B. Step 2: keep the KD recovery, borrow three things from Stage 2

Osprey's Table 5 compares pruning followed directly by target adaptation with pruning, a separate recovery stage, then adaptation. The recovery stage adds $+0.185$ overall AL and wins all 16 domain pairs.[^bieOspreyTargetagnosticPretraining2026] That supports keeping a separate step 2 before PARD training. My step 2 already uses a stronger signal than Osprey's: Minitron recommends retraining exclusively with distillation loss using KLD instead of conventional training,[^muralidharanCompactLanguageModels2024] and Osprey's recovery is plain next-token prediction with no teacher.[^bieOspreyTargetagnosticPretraining2026] So Stage 2 should not replace step 2. Three parts of it are worth taking:

1. **Budget.** Osprey's 10k-step checkpoint adapts to AL 3.552 against 3.578 for 55k steps.[^bieOspreyTargetagnosticPretraining2026] Yan et al. recover a pruned draft's TAR with 1 million tokens of distillation in under 10 minutes.[^yanDecodingSpeculativeDecoding2025] Both suggest checking short recovery budgets first.
2. **Data breadth.** Osprey recovers on generic web text (FineWeb) and gains on every in-domain and out-of-domain pair.[^bieOspreyTargetagnosticPretraining2026] If step 2's KD data is narrow, mixing in generic text is a candidate. No paper here tests generic data inside KD recovery.
3. **What to measure.** Track the drafter's AL after PARD training, not only the recovered model's perplexity. Osprey tracks perplexity but reports AL as the result,[^bieOspreyTargetagnosticPretraining2026] and Yan et al. find that a draft model's language-modeling capability does not correlate strongly with its speculative decoding performance.[^yanDecodingSpeculativeDecoding2025]

### C. Between steps 2 and 3: zero-initialize the target-feature path (if PARD-2 style)

PARD-2 fuses low-, middle-, and high-level target hidden states with a lightweight projection and adds the result to the draft input embeddings, $e^{d^{\prime}}=e^{d}+\xi\cdot t$.[^anPARD2TargetAlignedParallel2026] The paper does not say how the projection is initialized. Osprey adds target features through zero-initialized QKV columns so that "the attention layers therefore retain their target-agnostic pretrained behavior at initialization".[^bieOspreyTargetagnosticPretraining2026] Applied to PARD-2, a zero-initialized projection makes $t=0$ at the start, so the drafter begins exactly as the recovered model. That is my transfer of the idea; neither paper tests it on PARD-2.

The evidence that the injection path matters is indirect. Under DFlash's KV injection, Osprey's warm start gains at most $0.07$ accepted tokens. An EAGLE-style variant with zero-initialized target-side projections raises out-of-domain mean AL from $1.68$ to $2.00$, though it also changes the attention pattern.[^bieOspreyTargetagnosticPretraining2026]

The same principle could set the initial embedding of PARD's mask token, which is a new input the recovered model has never seen. PARD reports that one shared mask token ID works better than distinct IDs,[^anPARDAcceleratingLLM2025] but the wiki has no source on how it is initialized. Initializing it from existing rows, in the spirit of Osprey's vocabulary rule, is my idea only.

### D. Step 3: add live target logits; TTT does not transfer

Osprey's Stage 4 distills the frozen target with logits computed online.[^bieOspreyTargetagnosticPretraining2026] PARD-1 trains with cross-entropy and no target model,[^anPARDAcceleratingLLM2025] while PARD-2 adds a KD term and CAT weights computed from the target's probabilities.[^anPARD2TargetAlignedParallel2026] Because my step 2 already runs the target as teacher, step 3 can reuse the same target pass for PARD-2's KD and CAT terms. That would make step 3 target-aware like Osprey's Stage 4.

TTT does not carry over. It unrolls an autoregressive drafter over several steps,[^bieOspreyTargetagnosticPretraining2026] and PARD predicts all $K$ positions in one pass with mask tokens. PARD's counterpart is its per-offset subtasks with COD.[^anPARDAcceleratingLLM2025]

Osprey's warm start loses only $0.11$ AL when the adaptation learning rate drops from $10^{-4}$ to $10^{-5}$, against $1.07$ for EAGLE-3 from scratch.[^bieOspreyTargetagnosticPretraining2026] A recovered pruned model may be similarly robust in step 3, which would make a learning-rate sweep cheaper to skip. That is untested.

### E. What does not transfer

- **Vocabulary alignment.** A model pruned from the target keeps the target's tokenizer, so Osprey's vocabulary alignment is not needed.
- **Cross-target reuse.** Osprey's case for its 3,040 H100-hour pretraining rests on reusing one backbone across targets.[^bieOspreyTargetagnosticPretraining2026] A pruned target is target-specific. The exception is a family: PARD-1 serves a whole target family with one drafter,[^anPARDAcceleratingLLM2025] so steps 1–2 done once on Qwen3-14B might serve other Qwen3 sizes. That is untested.

### F. What the first run showed

[Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) ran steps 1–3 on Qwen3-14B: a one-shot Minitron prune to the Qwen3-0.6B shape, forward-KL recovery against Qwen3-14B on 49,372 of its own greedy answers, and PARD-1 with hard labels only. Offline on Spec-Bench the drafter reaches MAT 1.96 at K=8, against 2.66 for the same PARD recipe on Qwen3-0.6B.[^minitron-pard-qwen3-14b] Against the suggestions above:

- **Budget (B.1).** The recovery curve on held-out answers had flattened by the third epoch (+0.001 top-1 per 250 steps), at 57M target tokens. Most of the gain came in the first epoch (τ at γ=5 from 1.02 to 2.09 by 19M tokens, 2.31 at the end).[^minitron-pard-qwen3-14b]
- **Data breadth (B.2).** The run went the other way: it recovered on the target's own chat answers instead of web text. The report states that an earlier SlimPajama recovery was superseded, gives no numbers for it, and explains the chat advantage by the answers' lower entropy and their match with Spec-Bench's references, which are the same teacher's chat answers.[^minitron-pard-qwen3-14b] Mixing in generic text remains untested.
- **What to measure (B.3).** The run tracks AR τ on held-out answers during recovery and reports PARD MAT on Spec-Bench as the result.[^minitron-pard-qwen3-14b]
- **Live target logits in step 3 (D).** Not tried. The PARD stage used hard labels only, and it did not lift the backbone's AR MAT further (2.24 at γ=7 before, 2.26 at γ=8 after).[^minitron-pard-qwen3-14b]
- **Where the gap is.** The PARD drafter's first-offset top-1 equals the backbone's (0.570 against 0.572), and the report attributes the gap to the control to it.[^minitron-pard-qwen3-14b] **Inference.** That points at step 2, not step 3, as the place to improve, which is where Osprey's budget and data findings apply.

## Caveats

- All of Osprey's ablations use a Qwen3-4B source with a Qwen3-8B target and an EAGLE-3 drafter, and most results are single runs.[^bieOspreyTargetagnosticPretraining2026] None of them involves a parallel drafter, except the DFlash appendix.
- DistillSpec finds that the best distillation data source varies by task and decoding mode, and that draft-generated data is competitive.[^zhouDistillSpecImprovingSpeculative2024] "Off-policy" in step 2 is therefore a choice to test, not a given.

## Related

- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- [Do PARD-2's CAT and KD losses help a drafter trained without target features?](../questions/feature-free-pard-2-losses.md)
- [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md)
- [Target-aware recovery of compressed drafters](target-aware-recovery-of-compressed-drafters.md), [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- [Building a parallel drafter for on-device use without training it from scratch](building-parallel-drafters-for-on-device-use.md)
- Methods: [Osprey](../methods/osprey.md), [PARD](../methods/pard.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Training-time test](../methods/training-time-test.md)

[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
