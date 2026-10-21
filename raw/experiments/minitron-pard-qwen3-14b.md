# Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1

**Runs:** prune 2026-10-17 on spark2 (DGX Spark GB10) · answer regeneration 2026-10-17 02:30 → 10:22 on spark4 (GB10, vLLM 0.20) · chat-KD recovery and PARD-1 2026-10-18 on nutella2 (one H100 PCIe 80 GB, run stamp `261018`) · K=7 re-evaluations 2026-10-19 on spark2 · workspaces `kaist/ina/drafter-optimization/` (pruning, recovery, evaluation) and `kaist/ina/pard/` (AMD's PARD training code)

This file describes one pipeline that turns the target model itself into a PARD-1 parallel drafter. It has three stages:

1. One Minitron pruning step takes Qwen3-14B down to the shape of Qwen3-0.6B, with no retraining inside the pruning step.
2. The pruned model is recovered by online logit distillation from Qwen3-14B, using answers that Qwen3-14B wrote itself ("chat-KD").
3. The recovered model is fine-tuned into a PARD-1 drafter with K=8 mask tokens.

Two references are scored on the same benchmark with the same evaluator. One is a PARD-1 drafter trained with the identical data and recipe on the off-the-shelf Qwen3-0.6B (the control). The other is AMD's released `amd/PARD-Qwen3-0.6B`.

Numbers come from:
- `drafter-optimization/README.md`, section "Qwen3-14B → 0.6B 모양 one-shot pruned 모델의 chat-KD recovery + PARD-1 (2026-10-18, nutella2 H100)"
- `daily-logs/10-17-26.md` and `daily-logs/10-19-26.md`
- The prune run folder on spark2, `drafter-optimization/runs/261017_minitronpaper_qwen3_14b_to0p6b/` (`results.json`, `stage0_plan.json`, `stage0/config.json`)
- The control and released-drafter evaluation folders on spark2: `runs/261017_pardmat_pard1_control_k8_{pard,ar}/`, `runs/261019_pardmat_pard1_{control,released}_k7/`

The recovery and PARD run folders for the pruned model are on the lab NAS (`/mnt/nas/vafbaguio/mobile-drafter/runs/261018_train_qwen3_14b__pruned0p6b_chatkd/`, `/mnt/nas/vafbaguio/mobile-drafter/pard_ckpt/pruned0p6b_chatkd/`). They were not readable when this file was written, so every number for the pruned model comes from the README and the 10-19 log.

An earlier version of this pipeline (10-17/10-18) recovered the same pruned model on SlimPajama text from a cached top-64 teacher, instead of chat answers. That version is superseded and is not reported here.

---

## 1. Summary

Spec-Bench, 480 questions, Qwen3-14B greedy non-thinking references, temperature 0:

| Drafter | Params | Backbone AR top-1 | PARD MAT K=8 | Macro MAT K=8 | First-offset top-1 | Same weights as AR draft, MAT γ=8 |
|---|---|---|---|---|---|---|
| **Pruned Qwen3-14B + chat-KD 57M tokens + PARD-1** | 751,632,384 | 0.572 | **1.96** | 1.92 | 0.570 | 2.26 |
| Qwen3-0.6B + PARD-1 (control, same data and recipe) | 596,049,920 | 0.747 | 2.66 | 2.73 | 0.751 | 3.55 |
| amd/PARD-Qwen3-0.6B (released) | 596,049,920 | 0.747 | 3.07 | 3.14 | 0.752 | 3.55 |

**Main findings:**

1. **The pruned drafter reaches 1.96 MAT at K=8: 74% of the control (2.66) and 64% of the released PARD drafter (3.07).**
2. **The PARD stage inherits the backbone's first-token accuracy unchanged.** The recovered backbone's AR top-1 is 0.572. The PARD drafter's first-offset top-1 is 0.570. The source attributes the remaining gap to the control to this number (0.570 vs 0.751), i.e. to the backbone.
3. **Chat-KD recovery took the pruned model from 1.04 to 2.17 MAT at γ=5 as an autoregressive draft** (top-1 0.038 → 0.572). Qwen3-0.6B reaches 3.12 (top-1 0.747).
4. **The recovery curve had flattened by the end.** On the 500 held-out answers it gained +0.001 top-1 per 250 steps in epoch 3. The source concludes that more epochs over the same 49,872 answers will not help. More answers (the Magpie pool has about 300K prompts) or lifting the 512-token answer cap would.
5. **Unlike the chat-free recovery, the PARD fine-tune did not lift the backbone's AR MAT further.** The backbone scores 2.24 at γ=7 before the PARD fine-tune and the PARD weights 2.26 at γ=8 after it. Once the backbone has been distilled on these answers, a second pass over the same answers is not further recovery.
6. **The eighth offset adds almost nothing.** The same pruned PARD weights give 1.958 at K=7 and 1.959 at K=8. For the released drafter, K=7 gives 3.031 and K=8 3.07, so its last offset is worth 0.04.

No live (phone or server) speculative-decoding run of the pruned drafter exists. All numbers here are offline greedy MAT against stored references.

---

## 2. Pipeline and setup

### 2.1 Models

| | Qwen3-14B (target, teacher) | Pruned stage0 / recovered backbone | Qwen3-0.6B (control backbone) |
|---|---|---|---|
| Parameters | 14,768,296,960 | 751,625,216 by the pruning budget; 751,632,384 counted by the evaluator | 596,049,920 |
| Layers | 40 | 28 | 28 |
| Hidden size | 5120 | 1024 | 1024 |
| Query heads / KV heads | 40 / 8 | 16 / 8 | 16 / 8 |
| Head dim | 128 | 128 | 128 |
| FFN (intermediate) | 17,408 | 3,072 (3.0 × hidden) | 3,072 |
| Embeddings | untied | untied (`tie_word_embeddings: false`) | tied |
| Vocab rows | 151,936 | 151,936 | 151,936 |

The pruned model has the Qwen3-0.6B shape but keeps untied input and output embeddings, so it is 0.75B and not 0.6B. It is 5.1% of the target's parameters. The 7,168-parameter difference between the two counts equals 28 layers × 2 × 128, i.e. the per-layer q/k-norm weights.

### 2.2 Stage 1: Minitron one-shot pruning (spark2, 2026-10-17)

Config `configs/prune/minitron_paper_qwen3_14b_0p6b.yaml`, code `src/drafter/prune/minitron_paper.py` and `src/drafter/prune/importance.py`. This is the repo's reproduction of Minitron (Muralidharan et al., NeurIPS 2024), run as one step with a single fixed candidate:

- **Search:** one candidate only: 28 layers, hidden 1024, 16 heads, MLP 3.0 × hidden. Budget 751,625,216 params, tolerance 5%, `hidden_min_frac` 0.2 (so 5120 → 1024 is allowed in one step), `max_candidates: 1`.
- **No retraining in this stage:** `lightweight_steps: 0`, `distill_steps: 0`. Recovery is a separate run (§2.4).
- **Residual-head trick (Minitron §2.3): off.** It is absent from the official implementation, and the literal version made zero-shot LM loss worse in the Llama-3.1 reproduction.
- **Calibration data:** SlimPajama-6B tokenized with Qwen3, 4096-token sequences, domain mix cc 0.67 / github 0.045 / book 0.045 / stackexchange 0.02 / wiki 0.045 / arxiv 0.025 / c4-rp 0.15. NVIDIA's Nemotron pretraining data is not public.
- **Calibration size:** 256 sequences for width importance (batch 4), 32 sequences for depth importance. Validation loss uses 24 sequences per domain.
- **Width importance** comes from forward passes only, aggregated as mean over the sequence then L2 over the batch:
  - **Heads:** the L2 norm of each head's output (the head's slice of the `o_proj` input).
  - **FFN neurons:** the `down_proj` input, i.e. act(gate)·up.
  - **Hidden channels:** RMSNorm outputs summed over the layers' norms, excluding the final norm, as in the official `mcore_minitron.py`.
- **Depth importance:** the increase in LM loss when one layer is replaced by the identity. Base loss on the 32 calibration sequences is 2.326.

**What was kept:**

- **Layers:** the 28 with the largest loss increase. Kept: 0, 1, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 17, 24, 25, 27–39. Dropped: 2, 4, 10, 15, 16, 18, 19, 20, 21, 22, 23, 26. These are the 12 lowest-ranked layers, with removal costs of 0.022–0.033 nats each.
- **Most important layers by removal cost:** layer 0 (9.37 nats), layer 6 (0.97), layer 39 (0.54), layer 38 (0.22), layer 35 (0.099). Every other layer is under 0.075.
- **Heads:** in every kept layer, 2 of the 5 query heads in each of the 8 KV groups (16 query heads); all 8 KV heads are kept.
- **FFN:** the top 3,072 of 17,408 neurons per kept layer.
- **Hidden:** the top 1,024 of 5,120 channels.

**LM validation loss (SlimPajama, nats/token):**

| Domain | Qwen3-14B | Pruned stage0 (zero-shot) |
|---|---|---|
| avg | 1.907 | 9.60 |
| cc | 2.361 | 8.715 |
| github | 0.846 | 10.869 |
| book | 2.589 | 8.467 |
| stackexchange | 1.771 | 9.640 |
| wiki | 1.814 | 10.885 |
| arxiv | 1.202 | 10.051 |
| c4-rp | 2.765 | 8.584 |

**Time on the GB10:** 64 min for the whole stage (3,857 s): 11 min of activation importance, 44 min of depth importance, the rest pruning and evaluation.

### 2.3 Training data: Qwen3-14B's own answers (spark4, 2026-10-17)

- **Prompts:** 45,000 user prompts from `Magpie-Align/Magpie-Qwen2-Pro-1M-v0.1` (first user turn of `conversations`, seed 0) and 5,000 from `theblackcat102/evol-codealpaca-v1` (`instruction`, seed 0). 128 CodeAlpaca prompts over 1,024 tokens were dropped, leaving 4,872, for 49,872 prompts in all. This follows the prompt sources of PARD's Qwen recipe.
- **Answers:** Qwen3-14B, greedy, thinking off (`enable_thinking: false`), at most 512 new tokens, served by vLLM 0.20 with 256 concurrent sequences (`scripts/regenerate_vllm.py`). The chat template is applied locally and token ids are stored as generated.
- **Throughput:** 7.9 h at about 2 prompts/s and 700 output tokens/s.
- **Truncation:** 26,648 of the 49,872 answers (53%) hit the 512-token cap. They are kept (`drop_truncated: false`); the target text up to the cut is still target text.
- **Splits for recovery:** one seeded shuffle; the first 49,372 answers train (`configs/data/qwen3_14b_regen50k_train.yaml`), the last 500 are held out (`..._eval.yaml`, `skip: 49372`). The two do not overlap. `max_seq_len` 1,600 (prompt ≤ 1,024 + answer ≤ 512 + template).
- **PARD-1 data:** all 49,872 answers exported to PARD's JSONL format (`qwen3_14b_regen50k.jsonl`). This includes the 500 answers held out during recovery. They were used only for the recovery-stage curve in §3.1, not for the Spec-Bench numbers.

### 2.4 Stage 2: chat-KD recovery (nutella2 H100, 2026-10-18)

Config `configs/train/qwen3_14b__pruned0p6b_chatkd.yaml`, launched by `scripts/nutella2/h100_chain.sh` (stages H1 export → H2 train → H3 AR MAT → H4 convert + PARD-1 → H5 PARD MAT).

- **Student init:** the pruned `stage0` from §2.2.
- **Teacher:** Qwen3-14B bf16, run live on the same GPU (`kd.signal: online`, no cache on disk).
- **Loss:** forward KL over the full vocabulary, temperature 1.0, weight 1.0, computed in 1,024-position chunks. Loss is on answer tokens only.
- **Schedule:** 3 epochs, about 1,543 steps per epoch, about 18.9M target tokens per epoch, 57M in all.
- **Batch:** 8 per device × grad-accum 4 × 1 GPU = 32 sequences per step, about 14k target tokens. Batches are grouped by length.
- **Optimizer:** lr 3e-5, `cosine_with_min_lr` (min 0.1 × peak), warmup 3%, bf16, gradient checkpointing, seed 0.
- **Checkpoints:** model only (`save_only_model`), at most 2 kept, on the NAS.
- **Memory:** teacher bf16 about 28 GB, student fp32 + Adam about 12 GB, plus activations; 48 GB in use.
- **Time:** 3 h 44 min at 2.9 s/step. Final train loss 1.85.

### 2.5 Stage 3: PARD-1 (nutella2 H100, 2026-10-18)

Config `pard/config/train/qwen3_14b__pruned0p6b_chatkd_pard1.yaml`, AMD's `pard/pard_train.py` (TRL 0.14.0 `SFTTrainer`, transformers 4.51.3).

- **Checkpoint conversion:** the recovered checkpoint was converted with `pard/scripts/convert_tf5_checkpoint.py`. Without it, transformers 4.51.3 reads a transformers-5 Qwen3 save with the wrong `rope_theta` and crashes on its tokenizer config.
- **Loss:** hard-label cross-entropy on the target-written answers. No teacher logits are used in this stage.
- **PARD settings:**
  - K = 8 (`para_num: 8`).
  - Mask token id 151670, the first unused Qwen3 embedding row and the same id as `amd/PARD-Qwen3-0.6B`.
  - COD subsampling (`down_sample_ration` 0.7, `down_sample_ration_min` 0.2).
- **Schedule:** 1 epoch = 779 steps of 64 sequences (16 per device × grad-accum 4), `max_seq_length` 512.
- **Optimizer:** lr 3e-5 `cosine_with_min_lr` (min 0.1), warmup 3%, bf16, gradient checkpointing, seed 0.
- **Prompt template:** a `qwen3` non-thinking template (no system prompt, empty think block before the answer). It matches the context the target saw when it wrote the answers.
- **Time:** 88 min at 6.5 s/step. Train loss 3.70.
- **Upstream quirk:** `pard_train.py` sets pad to the end token, so `<|im_end|>` is never trained. This is left as upstream and is the same for the control.

### 2.6 Control: Qwen3-0.6B + PARD-1

`pard/config/train/qwen3_0p6b_control_pard1.yaml`, run on a DGX Spark GB10 on 2026-10-17:

- **Same as the pruned run:** data (the same 49,872 answers), template, K, mask token, COD, learning-rate schedule, epoch count and 64 sequences per step.
- **Differences:** the backbone (`Qwen/Qwen3-0.6B`, transformers-4 checkpoint, no conversion), the batch split (8 per device × grad-accum 8) and checkpoint retention (3 full checkpoints).
- **Time:** 779 steps, 12.0 h, mean train loss 2.84.

Released reference: `amd/PARD-Qwen3-0.6B`, revision `f9f650fbab180c26498817718f0db5cae8f25136`. AMD trained it on far more data (about 1M prompts, 4 epochs).

### 2.7 Evaluation

**Benchmark:** Spec-Bench, 480 questions (`question.jsonl` sha256 `4b6d33e79484f9841c487ee87d1cf6aa8c6066f61d5d482ff09e5a007fafdf04`), built by `scripts/prepare_specbench.py` on spark4.
- **References:** Qwen3-14B bf16 greedy responses with `enable_thinking: false` (`data/bench/specbench_qwen3_14b_greedy`).
- **Positions:** 154,651 response positions, 154,091 anchors.
- **Reference sanity check:** the teacher's argmax equals the stored token at 98.0% of positions (97.5% on first turns, 99.3% on second turns). The first-turn gap comes from the Qwen3 template dropping the empty think block from history turns, plus bf16 batch effects.
- **Response positions per task:** mt_bench 73,539, qa 22,475, rag 20,347, math_reasoning 18,988, summarization 17,230, translation 2,072.

**Metrics:**
- **MAT (mean accepted tokens)** is greedy τ: draft tokens accepted per verify plus the target's bonus token. MAT 1.0 means the draft never matches; with γ draft tokens the maximum is γ + 1.
- **top-1** is the fraction of positions where the draft's argmax equals the target's argmax.
- **Macro MAT** averages MAT over the six tasks.

**Evaluators:**
- **AR drafts:** `scripts/eval_mat.py`.
- **PARD drafts:** `scripts/eval_pard_mat.py` (`src/drafter/pard_eval.py`). It builds PARD's block attention mask, gets the argmax at every anchor × offset in one forward pass (window 1024), and replays greedy chain acceptance over the resulting [anchor × offset] agreement matrix. `top1_by_offset[j]` is the top-1 at draft offset j. `survival[j]` is the probability that offsets 0…j are all correct.
- **`--mode ar`** scores the same PARD weights as an ordinary autoregressive draft. At K=1 it matches `eval_mat.py` to within 1e-6.
- **Timing:** Spec-Bench AR evaluation takes 11 s on the H100.

---

## 3. Results

### 3.1 Recovery curve on the 500 held-out answers (training distribution, AR τ at γ=5)

| Step | Target tokens | top-1 | Forward KL | τ |
|---|---|---|---|---|
| 0 | 0 | 0.023 | 9.78 | 1.02 |
| 250 | 3.2M | 0.379 | 3.41 | 1.59 |
| 500 | 6.4M | 0.460 | 2.67 | 1.80 |
| 1000 | 12.8M | 0.521 | 2.16 | 1.99 |
| 1543 (end of epoch 1) | 19M | 0.548 | 1.95 | 2.09 |
| 2250 | 28.8M | 0.580 | 1.73 | 2.21 |
| 3000 | 38M | 0.594 | 1.64 | 2.27 |
| 4500 | 57.6M | 0.605 | 1.57 | 2.31 |

Held-out top-1 at the end (0.605) is close to the Spec-Bench top-1 (0.572). The 0.03 difference is the gap between the training distribution and the benchmark.

### 3.2 Recovered backbone as an autoregressive draft (Spec-Bench)

| Backbone | Recovery | top-1 | MAT γ=3 | MAT γ=5 | MAT γ=7 |
|---|---|---|---|---|---|
| Pruned stage0, no recovery | none | 0.038 | 1.04 | 1.04 | 1.04 |
| **Pruned + chat-KD** | 57M tokens, 3 epochs | **0.572** | **2.00** | **2.17** | **2.24** |
| Qwen3-0.6B (off the shelf) | pretrained | 0.747 | 2.65 | 3.12 | 3.39 |

Per task, MAT at γ=5:

| Task | Pruned + chat-KD | Qwen3-0.6B | Pruned / Qwen3-0.6B |
|---|---|---|---|
| math_reasoning | 3.43 | 4.64 | 0.74 |
| mt_bench | 2.22 | 3.19 | 0.70 |
| rag | 2.05 | 2.91 | 0.70 |
| qa | 1.93 | 2.67 | 0.72 |
| summarization | 1.78 | 2.74 | 0.65 |
| translation | 1.39 | 3.13 | 0.44 |

The last column is computed for this file from the two columns before it. Translation is the weakest task relative to Qwen3-0.6B.

### 3.3 PARD-1 drafters, K=8 (Spec-Bench)

| Drafter | PARD MAT K=8 | Macro | First-offset top-1 | Same weights, AR mode MAT γ=8 | AR-mode macro |
|---|---|---|---|---|---|
| **Pruned + chat-KD + PARD-1** | **1.96** (1.959) | 1.92 | 0.570 | 2.26 | |
| Qwen3-0.6B + PARD-1 (control) | 2.66 (2.663) | 2.73 | 0.751 | 3.55 (3.552) | 3.73 |
| amd/PARD-Qwen3-0.6B (released) | 3.07 | 3.14 | 0.752 | 3.55 | 3.59 |

PARD MAT at the PARD-1 checkpoints:

| Step | Pruned + chat-KD | Control |
|---|---|---|
| 200 | 1.89 | 2.53 |
| 400 | 1.94 | 2.61 |
| 600 | 1.96 | 2.65 |
| 779 (final) | 1.96 | 2.66 |

The released drafter at K=16 scores 3.15 (macro 3.30); its top-1 at offset 15 is 0.100 and survival to offset 15 is 0.017.

#### Per-offset top-1 at K=8

| Offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Pruned + chat-KD + PARD-1 | .570 | .400 | .290 | .215 | .165 | .133 | .112 | .096 |
| Control | .751 | .560 | .432 | .338 | .274 | .225 | .189 | .159 |
| Released | .752 | .618 | .520 | .444 | .385 | .337 | .298 | .264 |
| Pruned / control (computed) | 0.76 | 0.71 | 0.67 | 0.64 | 0.60 | 0.59 | 0.59 | 0.60 |

Survival (all offsets up to j correct) at K=8:

| Offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Control | .751 | .499 | .328 | .219 | .148 | .100 | .067 | .043 |
| Released | .752 | .555 | .418 | .325 | .260 | .213 | .177 | .147 |

Survival for the pruned drafter is not recorded in the sources.

Top-1 at offset 7 relative to offset 0: pruned 0.17, control 0.21, released 0.35.

#### Per task, PARD mode

| Task | Pruned + chat-KD (K=8) | Control (K=8) | Released (K=7) | Control, AR mode (γ=8) |
|---|---|---|---|---|
| math_reasoning | 2.91 | 4.30 | 5.26 | 6.24 |
| mt_bench | 2.00 | 2.71 | 3.12 | 3.65 |
| rag | 1.84 | 2.46 | 2.80 | 3.29 |
| qa | 1.79 | 2.31 | 2.58 | 2.95 |
| summarization | 1.63 | 2.24 | 2.46 | 2.92 |
| translation | 1.35 | 2.37 | 2.21 | 3.30 |

The released drafter's per-task numbers are at K=7, the only setting with a per-task file on spark2. Its overall K=7 MAT is 3.031 against 3.07 at K=8.

Per-task first-offset top-1 for the control (K=8, PARD mode): math 0.913, mt_bench 0.760, rag 0.716, translation 0.711, qa 0.676, summarization 0.673. For the released drafter (K=7): math 0.914, mt_bench 0.767, rag 0.714, qa 0.680, summarization 0.661, translation 0.609.

### 3.4 K=7 versus K=8 (re-evaluation without retraining, spark2, 2026-10-19)

| Drafter | MAT K=7 | MAT K=8 | Worth of the eighth offset |
|---|---|---|---|
| Pruned + chat-KD + PARD-1 | 1.958 | 1.959 | 0.001 |
| Control | 2.655 | 2.663 | 0.008 |
| Released | 3.031 | 3.07 | 0.04 |

Control macro MAT at K=7: 2.720. Released macro at K=7: 3.075. The released drafter keeps 0.298 top-1 at offset 6.

### 3.5 Run times

| Stage | Hardware | Time | Rate |
|---|---|---|---|
| Minitron one-shot prune | GB10 (spark2) | 64 min | |
| Answer regeneration, 49,872 answers | GB10 (spark4), vLLM 0.20 | 7.9 h | ~2 prompts/s, ~700 output tok/s |
| Chat-KD recovery, 3 epochs | H100 PCIe 80 GB (nutella2) | 3 h 44 min | 2.9 s per 32-sequence step |
| PARD-1 on the pruned backbone, 779 steps | H100 PCIe 80 GB (nutella2) | 88 min | 6.5 s/step |
| PARD-1 on Qwen3-0.6B (control), 779 steps | GB10 | 12.0 h | |

The H100 ran the recovery student at 2.9 s per 32-sequence step, teacher included. The source estimates this as roughly 10× faster per token than the earlier cached-teacher recovery on the GB10 (59 s per 131k-token step), with different sequence lengths.

---

## 4. Interpretation (as recorded in the sources)

- **The backbone sets the ceiling.** Backbone top-1 0.572 → PARD first-offset top-1 0.570 → MAT 1.96. The PARD stage passes the first offset through and adds the later offsets on top. The README and the 10-19 log attribute the whole gap to the control (1.96 vs 2.66) to the first offset (0.570 vs 0.751).
  - Caveat, computed for this file: the per-offset ratio to the control falls from 0.76 at offset 0 to about 0.60 at offsets 4–7, and offset-7 retention is 0.17 against 0.21. So the later offsets also decay somewhat faster for the pruned drafter.
- **Why chat answers worked:** the teacher's greedy answers have lower entropy than web text and are easier to match. Spec-Bench references are the same teacher's chat answers, so the advantage carries over to the benchmark. The chat-KD learning rate (3e-5) was also 3× that of the SlimPajama recovery.
- **More epochs would not help:** the held-out curve was flat in epoch 3. The next levers are more answers or a longer answer cap.

## 5. How this pipeline classifies against distillation-for-speculative-decoding recipes

This classification is a description of the recipe above, not a measured comparison.

- **Draft initialization:** structured pruning of the target itself.
- **Recovery (stage 2):**
  - white-box logit distillation;
  - forward KL only, temperature 1;
  - fixed teacher-generated data;
  - no student-generated (on-policy) samples and no other divergence (RKL, JSD, TVD), although the training code supports `fkl`, `rkl`, `jsd` and `tvd` (`src/drafter/losses.py`).
- **PARD-1 (stage 3):** sequence-level distillation only (hard labels on teacher outputs), no teacher distribution.

## 6. Caveats

- **Offline only:** every number is greedy offline MAT on stored references. No live run of the pruned drafter was made, so there is no wall-clock or tok/s figure for it.
- **Held-out set reused:** the 500 answers held out during recovery were included in the PARD-1 training data (§2.3). Only the recovery curve in §3.1 uses them.
- **AR-mode comparison mismatch:** the backbone is scored at γ=7 (2.24) and the PARD weights in AR mode at γ=8 (2.26), so the "no further lift" comparison is between different γ.
- **Batch split differs:** the pruned PARD-1 run used 16 × 4 per step against the control's 8 × 8; both are 64 sequences per step.
- **Optimizer state not saved:** `save_only_model: true` means any resume restarts the optimizer state. The recovery and PARD runs finished without a resume.
- **Different evaluation sets:** the held-out 500 answers (training distribution) are for watching the curve. Spec-Bench is the result.
- **Environment:** on nutella2, `scripts/check_env.py` fails its fla kernel self-test (a known Hopper + Triton < 3.7.1 issue). Qwen3 does not use fla.
- **Paper comparison:** the PARD paper's Qwen3-14B K=16 τ of 5.14 is averaged over HumanEval, GSM8K, MATH-500 and MT-Bench. Spec-Bench includes translation, summarization, QA and RAG, so lower numbers here are expected.

## 7. Next steps named in the sources

- Generate more Qwen3-14B answers (the Magpie pool has about 300K prompts) or lift the 512-token answer cap. More epochs on the current 49,872 answers will not help.
