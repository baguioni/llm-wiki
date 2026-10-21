# Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)

**Runs:** 2026-10-19 16:52 → 17:55 KST on spark2 (hostname `spark-7653`) · 12 live runs (6 drafters × 2 repeats), all finished OK · offline replays against the C++ oracle on spark2 earlier that day · workspace `kaist/ina/drafter-evaluation/`, code on specedge branch `eval/so-chain`

This file describes a server-only counterpart of the phone chain7 arms in `drafter-evaluation-server-shapes.md`. Each of the six drafters (Qwen3-0.6B, EAGLE-3, DFlash, DSpark, PARD-1, PARD-2) was re-implemented in pure PyTorch. Each one drafts on the same GPU as the Qwen3-14B-FP8 target, in the same process, with no phone and no network. Only the chain shape (depth 7, 8 rows verified) was run. The phone numbers quoted here for comparison are the chain7 arms from `drafter-evaluation-server-shapes.md` §5.1 and are unchanged.

Numbers come from `results/2026-10-19/server-only-chain/` (per-round `server_only.jsonl`, per-request `trace.jsonl`, `run_meta.json`, replay `summary.json`), tabulated by `analysis/server_only_chain.py` into `results/final/server-only-chain.md`, plus the per-repeat figures, the histograms and the output agreement, computed from the same files with `analysis/server_only_metrics.py`'s `load`/`summarize`.

---

## 1. Summary

tok/s, steady state (round 0 excluded), mean over requests and then over the 2 repeats:

| Drafter | Server-only tok/s | Phone chain7 tok/s | Server / phone | Server tok/round | Phone tok/round | Server draft ms | Server round ms | Phone round ms |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (target-dependent) | **34.0** | 24.9 | 1.36× | 3.50 | 3.34 | 15.6 | 114.1 | 148.8 |
| DSpark | **33.9** | 26.5 | 1.28× | 3.90 | 3.83 | 27.2 | 127.4 | 160.3 |
| DFlash | **31.0** | 25.5 | 1.22× | 3.43 | 3.45 | 24.2 | 124.1 | 152.3 |
| PARD-1 | **28.0** | 22.1 | 1.27× | 2.86 | 2.76 | 13.0 | 111.3 | 137.0 |
| Qwen3-0.6B | **20.4** | 15.6 | 1.31× | 3.42 | 3.11 | 86.4 | 185.2 | 227.0 |
| EAGLE-3 (DeepSpec ttt7) | **17.2** | 13.0 | 1.32× | 2.81 | 2.71 | 88.8 | 188.0 | 239.4 |
| *Qwen3-0.6B, 10-16 specedge `server_only.py` (fp16)* | *17.0* | | | *3.37* | | *111.6* | *212.8* | |

The verify (target) time is 98.2–100.2 ms mean per round in every server-only arm.

**Main findings:**

1. **Every drafter is faster server-only than on the phone, by 1.22× (DFlash) to 1.36× (PARD-2).**
   - Every server-only round is 25.7–51.4 ms shorter than the phone round.
   - The verify wait drops from the phone's client wait of 114.8–129.2 ms to the bare target forward of 98.2–100.2 ms, with no network and no serialization.
   - Drafting is also faster on the GPU for five of the six drafters. The exception is Qwen3-0.6B, at 86.4 vs 84.9 ms.
2. **PARD-2 and DSpark tie for first (34.0 and 33.9 tok/s); on the phone DSpark led and PARD-2 was third.**
   - PARD-2 has the cheapest draft of the feature drafters (15.6 ms) and accepts 3.50 tok/round.
   - DSpark accepts the most (3.90 tok/round), but drafts in 27.2 ms. Its Markov head costs 3.0 ms per round over DFlash (27.2 vs 24.2 ms) on the GPU, against 8.48 ms on the phone's host CPU.
3. **The block drafters still beat the AR drafters by a wide margin: 28.0–34.0 vs 17.2–20.4 tok/s.** The AR drafters draft in 86–89 ms per round on the GB10, as on the phone. The block drafters draft in 13–27 ms.
4. **Three server-only chain arms beat the best phone arm overall** (PARD-2 own-best tree, 30.0 tok/s): PARD-2 34.0, DSpark 33.9 and DFlash 31.0. The 10-16 server-only baseline (Qwen3-0.6B, best shape tree16, 21.6 tok/s) beat none of the phone block-drafter arms.
5. **Acceptance is close to the phone's.** Server-only tok/round is within −0.02 to +0.16 of the phone's, except Qwen3-0.6B at +0.31.
   - The server drafts are bf16 and the phone drafts are Q4_0.
   - The offline replays show the same: bf16 is within +0.02 to +0.12 tok/round of the Q4_0 oracle, with the AR draft again the outlier at +0.27 (§6.2).
6. **The 2 repeats are identical round for round in every arm**: same accepted lengths and same output tokens. Only the timings differ: tok/s moves by at most 0.52 between repeats.

---

## 2. Experimental setup

### 2.1 What one round does

Everything runs in one Python process on one GB10, one request at a time, temperature 0.

**Per request:**
1. **Prefill (target).**
   - **Feature drafters (EAGLE-3, DFlash, DSpark, PARD-2):** the target prefills the whole prompt, which commits the first output token and returns one feature row per prompt position. The drafter takes those rows. This is round 0 and drafts nothing, as in the phone client.
   - **Token drafters (Qwen3-0.6B, PARD-1):** the target prefills the prompt up to its last token. The last prompt token is round 0's anchor, and round 0 drafts and verifies like any later round, as in the phone client.
2. **Each round,** the anchor is the last committed token:
   - **Draft:** 7 tokens, greedy (see §2.3 for each drafter).
   - **Verify:** the target runs [anchor, d1 … d7] as 8 rows in one causal forward. The same pass returns the feature rows for the drafter.
   - **Accept:** the longest prefix of drafts that matches the target's greedy choice, plus one bonus token from the target. k counts both (accepted drafts + bonus), as the phone's k does.
   - **Commit:** the drafter takes the accepted tokens and the feature rows of the accepted positions. This happens at the start of the next round's draft and is timed as draft time.
3. **Stop:** when an EOS is committed in a decode round, or when the number of generated tokens reaches 64 plus the tokens committed in round 0. This is the phone client's rule. The last round can overshoot 64 by up to 7 tokens.

**Steady and prefill rounds:** round 0 (`step_idx` 0) is the prefill round. Every later round is a steady round, as in the phone report.

### 2.2 Hardware

| Part | What |
|---|---|
| Node | spark2 (hostname `spark-7653`), NVIDIA DGX Spark, GB10, driver 580.142, CUDA 13.0. `cuda:0` for both models. |
| GPU check | Before every run (replay and live), `run_chain.sh` reads `nvidia-smi --query-compute-apps` and aborts if any compute process is present. None was. Each live run saved `nvidia-smi.txt` at its start: only Xorg and gnome-shell, no compute process. |
| Software | Python 3.12.3, torch 2.9.0+cu130, transformers 4.57.6 (`~/vafbaguio/venv312`, the phone arms' server venv with the sync-free FP8Linear patch). |
| Network | none: draft and target share one process. |

### 2.3 Target and drafters

**Target:** `Qwen/Qwen3-14B-FP8`, the server's own `Qwen3ForCausalLM` behind specedge's `BatchGraphEngine`, fp16 activations, no CUDA graph, batch size 1, thinking off. These are the same model code and patch as the phone arms' server and the 10-16 server-only runs. The drafter's feature hook is attached to the target with the same server code the phone arms used:

| Drafter | Hook (`util.load_*`) | Feature row per position |
|---|---|---|
| EAGLE-3 | `load_eagle_head` | head `fc` over target hidden states of layers 2, 11, 20, 29, 38 (5120 wide) |
| DFlash, DSpark | `load_dflash_encoder` | DFlash encoder `fc` + RMS norm (5120 wide) |
| PARD-2 | `load_pard2_proj` | 0.02 · `target_proj`(cat of target layers 17, 25, 33 and the final post-norm hidden state) (1024 wide) |
| Qwen3-0.6B, PARD-1 | none | none |

Feature rows reach the drafter as GPU tensors, cast from fp16 to bf16. There is no fp16 serialization and no gRPC.

**Drafters:** new code in specedge `src/chain/` (branch `eval/so-chain`, commit `3c22ed0`), bf16 weights and activations, one checkpoint each, loaded from the Hugging Face cache:

| Drafter | Checkpoint | How one round drafts 7 tokens | CUDA graph |
|---|---|---|---|
| Qwen3-0.6B (`ar`) | `Qwen/Qwen3-0.6B` | AR chain: decode the pending committed tokens (≤ 2, one row each, as the client does), then 6 single-token steps. The last draft is never decoded. Rejected tokens are dropped by moving the KV length pointer back. | no (eager; see §3.3) |
| PARD-1 (`pard`) | `amd/PARD-Qwen3-0.6B` | One causal forward of [committed tokens the cache lacks, anchor last, then 6 mask tokens (id from the checkpoint's `pard_token`)]. The anchor's and the masks' rows give the 7 drafts. Mask K/V is dropped afterwards. Before the first round, the prompt is prefilled into the draft separately. | yes, one graph at 14 rows (block padded to 2k) |
| PARD-2 (`pard2`) | `amd/PARD2-Qwen3-14B` | As PARD-1, but each row's input is embed(token at p) + F[p − 1]. Mask rows take the anchor's F[anchor − 1], and F[−1] = 0. | yes, as PARD-1 |
| DFlash (`dflash`) | `deepseek-ai/dflash_qwen3_14b_block7` | The new feature rows are injected as context K/V (k-norm and RoPE, no layernorm on the context), then one non-causal block forward over [anchor, 6 mask tokens (id 151669)]. Row i is the draft for anchor + 1 + i. | no |
| DSpark (`dspark`) | `deepseek-ai/dspark_qwen3_14b_block7` | As DFlash, then the vanilla Markov bias W2·W1[prev] is added row by row, chained greedily from the anchor. | no |
| EAGLE-3 (`eagle3`) | `deepseek-ai/eagle3_qwen3_14b_ttt7` (DeepSpec, 1 layer, full-vocabulary LM head) | Cell P holds (token[P + 1], F[P]). d1 comes from the last committed cell's output. 6 single-cell steps then feed the head's own pre-norm output back. At commit, the scratch cells are dropped and the committed tokens are re-extended with their target features. | no |

**Reference implementations:**
- DFlash, DSpark and EAGLE-3 follow DeepSpec's `eval/dspark` and `eval/eagle3` modules.
- PARD-1 and PARD-2 follow AMD's PARD repository and `graph_engine.cpp`'s `pard_draft_block`.
- Every drafter mirrors the C++ phone client's chain (`spec_exec_client.cpp` `GrowTree`/`GrowBlock` at width 1), so acceptance can be compared with the phone arms up to draft numerics.

**Shared parts:**
- Every drafter keeps a static KV cache indexed by absolute position, with a length pointer for rollback.
- Every CUDA graph is captured once at load, before any request. A graph captured lazily would overwrite live K/V at position 0.

### 2.4 Workload

Identical to the phone arms:
- **Requests:** SpecBench, every 8th prompt (`sample_req_cnt: 8`, `req_offset: 0`), 60 requests, 10 per category (MT-Bench's 8 sub-categories pooled into `mt_bench`). The request order is the same shuffle as specedge's `server_only.py` (seed 0).
- **Decoding:** temperature 0, `max_new_tokens: 64`, `max_len: 2048`, seed 42, batch size 1, thinking off.
- **Prefill:** computed live. No prefill cache (`SPECEDGE_CACHE_PREFILL=False`).
- **Warm-up:** 1 request (the first in the order) before the measured 60, not logged.

The phone arms used `cache_prefill: true`, so their round 0 and TTFT exclude the target's prompt compute. The server-only round 0 includes it (§5.4).

---

## 3. Procedure

### 3.1 Validation before the live runs

1. **Against DeepSpec upstream (`tests/test_chain_upstream.py`).**
   - **Setup:** tiny random checkpoints, run through both `src/chain` and DeepSpec's own modules, in a separate scratch venv with transformers 5.10.2 (DeepSpec does not import under 4.57).
   - **Result:** DFlash, DSpark and EAGLE-3 give identical drafts and logits over 4 rounds.
2. **Against the C++ oracle, offline (`src/script/chain_replay.py`).**
   - **What it does:** replays the 60 requests with the target replaced by the recorded trace and dumped target features, the same dumps that `oracle_replay` reads (`oracle/features/{dflash,dspark,eagle,pard2}`). Selection at position p is the trace's token p + 1, or EOS past its end. Feature rows past the dump are zero.
   - **Where:** bf16 on spark2's GPU.
   - **Compared against:** the C++ `oracle_replay` chain7 `rounds.jsonl` of the Q4_0 GGUFs. PARD-2 has no Q4_0 oracle, so it is compared with the fp32 HF oracle in `oracle/pard2_td/scores.txt` (semantics B: per-kind round 0, EOS stop, 64 new tokens, decode rounds).
   - **Results:** §6.2.
3. **Smoke test:** `run_chain.sh live-smoke`, 16 requests per drafter.

### 3.2 Live runs

`bash run_chain.sh live` on spark2, from `~/vafbaguio/specedge-so-chain` (a `git archive` copy, not a checkout).
- **Code:** the md5 of `src/chain/{layers,models,drafters,loop,verifiers}.py` and `src/script/server_only_chain.py` on spark2 matches commit `3c22ed0`.
- **Order:** repeat 1 of all six drafters, then repeat 2 (pard, ar, pard2, dflash, dspark, eagle3 within each repeat).
- **Per run:** a GPU check, then the config is written to `config/so-chain/<run>.yaml`, then `server_only_chain.py`. `run_meta.json` records the node, start, end, exit code and number of requests traced.

| Run | Start → end (KST) | Status | Requests |
|---|---|---|---|
| so-chain-pard-chain7-r1 | 16:52:28 → 16:57:27 | ok | 60 |
| so-chain-ar-chain7-r1 | 16:57:27 → 17:03:23 | ok | 60 |
| so-chain-pard2-chain7-r1 | 17:03:23 → 17:07:53 | ok | 60 |
| so-chain-dflash-chain7-r1 | 17:07:53 → 17:12:48 | ok | 60 |
| so-chain-dspark-chain7-r1 | 17:12:48 → 17:17:56 | ok | 60 |
| so-chain-eagle3-chain7-r1 | 17:17:56 → 17:24:24 | ok | 60 |
| so-chain-pard-chain7-r2 | 17:24:24 → 17:29:05 | ok | 60 |
| so-chain-ar-chain7-r2 | 17:29:05 → 17:34:45 | ok | 60 |
| so-chain-pard2-chain7-r2 | 17:34:45 → 17:39:14 | ok | 60 |
| so-chain-dflash-chain7-r2 | 17:39:14 → 17:44:33 | ok | 60 |
| so-chain-dspark-chain7-r2 | 17:44:33 → 17:49:19 | ok | 60 |
| so-chain-eagle3-chain7-r2 | 17:49:19 → 17:55:50 | ok | 60 |

Every run's config differs only in `exp_name` and the `chain` block (`kind`, `model`). All use `depth: 7`, `dtype: bf16`, `warmup_requests: 1`, target `Qwen/Qwen3-14B-FP8` with `base.dtype: fp16`, and `temperature: 0.0`.

### 3.3 Incidents and deviations

- **CUDA graphs:**
  - The first replays ran every drafter eagerly (commit `8473c98`).
  - Graphs were then added for the two Qwen3-shaped drafts (`d8f570c`, plus the fix `633d49e` for a NameError in the eager path).
  - The PARD block graph cut the replay draft time from 15.2 to 12.6 ms (PARD-1) and from 18.7 to 15.4 ms (PARD-2).
  - The AR 1-row step was slower as a graph: replay draft 86.1 vs 83.0 ms per round, and 13.2 vs 11.7 ms per step in isolation. A 1-row step is bound by weight reads (about 150 GB/s on bf16 GEMVs in torch on the GB10), and the graph's attention reads a whole 256-key bucket. So the AR drafter went back to eager (`3c22ed0`) before the live runs.
  - Graphs do not change acceptance beyond numerics: replay tok/round with graph vs eager was 2.906 vs 2.901 (PARD-1), 3.598 vs 3.606 (PARD-2) and 3.374 vs 3.384 (AR).
- **Lazy graph capture** would corrupt live K/V at position 0. Graphs are therefore captured up front, at load.
- **Replay of the recorded traces:**
  - Near the end of a trace, the replay asks for feature rows past the dump. These rows are zero-padded.
  - The committed tokens are checked against the trace only where the two overlap.
- **Live progress logging:** a nohup redirect mistake sent the driver's combined stdout (`live.out`) to /dev/null. Each run's own `stdout.log` and `run_meta.json` were unaffected.

---

## 4. Metrics

Definitions are those of `analysis/server_only_metrics.py`, the same as for the 10-16 server-only runs:
- **k** = `num_accepted_tokens` = accepted drafts + bonus. It sums to `n_generated` for every request.
- **Round time** = `draft.end_to_end` + `target.end_to_end`, in ms.
  - Each is wall-clock with a CUDA synchronize at both ends.
  - Draft time includes the commit of the previous round's tokens and features (`draft.commit` is logged separately).
  - There is no network term.
- **tok/s steady** = for each request, Σk / Σ round time over steady rounds. The table shows the mean over the 60 requests, then the mean over the 2 repeats. The 95% CI is a bootstrap over requests (1000 resamples, seed 0), repeat 1.
- **Pooled tok/s** = Σk / Σ round time over all steady rounds of the run.
- **tok/round** = mean k over steady rounds.
- **P(k=0)** = fraction of steady rounds that accepted no draft (only the bonus).
- **aj** = fraction of steady rounds whose accepted path reached depth j.
- **By category** uses the same pooling as the phone report (MT-Bench sub-categories pooled).
- **Prefill and TTFT:** `trace.jsonl` records `prefill_ms`, the target prefill plus a feature drafter's `start()`. For feature drafters this is also round 0's round time. For token drafters round 0 is a separate draft + verify round after the prefill.

Phone-side figures (client wait, draft e2e, round mean) are copied from `drafter-evaluation-server-shapes.md` §5.1.

---

## 5. Results

### 5.1 Throughput

| Drafter | tok/s steady | r1 / r2 | 95% CI (r1) | pooled tok/s | Phone tok/s | Server / phone |
|---|---|---|---|---|---|---|
| PARD-2 | **34.0** | 33.71 / 34.23 | 30.67..36.60 | 30.7 | 24.9 | 1.36× |
| DSpark | **33.9** | 33.80 / 33.93 | 30.87..36.72 | 30.6 | 26.5 | 1.28× |
| DFlash | **31.0** | 31.08 / 31.02 | 28.29..34.02 | 27.7 | 25.5 | 1.22× |
| PARD-1 | **28.0** | 28.07 / 27.97 | 25.42..30.87 | 25.7 | 22.1 | 1.27× |
| Qwen3-0.6B | **20.4** | 20.51 / 20.38 | 18.81..22.32 | 18.5 | 15.6 | 1.31× |
| EAGLE-3 | **17.2** | 17.17 / 17.13 | 15.38..19.02 | 14.9 | 13.0 | 1.32× |

### 5.2 Acceptance

| Drafter | tok/round | Phone tok/round | rounds (all / steady) | P(k=0) | P(full depth) | a1 | a2 | a3 | a4 | a5 | a6 | a7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PARD-2 | 3.50 | 3.34 | 1068 / 1008 | 0.227 | 0.116 | 0.773 | 0.559 | 0.405 | 0.285 | 0.204 | 0.161 | 0.116 |
| DSpark | 3.90 | 3.83 | 978 / 918 | 0.202 | 0.162 | 0.798 | 0.629 | 0.476 | 0.363 | 0.272 | 0.198 | 0.162 |
| DFlash | 3.43 | 3.45 | 1088 / 1028 | 0.223 | 0.108 | 0.777 | 0.545 | 0.383 | 0.277 | 0.200 | 0.143 | 0.108 |
| PARD-1 | 2.86 | 2.76 | 1284 / 1224 | 0.337 | 0.066 | 0.663 | 0.436 | 0.279 | 0.197 | 0.132 | 0.088 | 0.066 |
| Qwen3-0.6B | 3.42 | 3.11 | 1090 / 1030 | 0.308 | 0.143 | 0.692 | 0.500 | 0.384 | 0.294 | 0.222 | 0.183 | 0.143 |
| EAGLE-3 | 2.81 | 2.71 | 1325 / 1265 | 0.398 | 0.092 | 0.602 | 0.398 | 0.258 | 0.191 | 0.149 | 0.119 | 0.092 |

The two repeats give identical acceptance, so each row is one repeat and also the mean.

#### Accepted-length histogram (% of steady rounds; k = accepted drafts, bonus excluded)

| Drafter | k=0 | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 |
|---|---|---|---|---|---|---|---|---|
| PARD-2 | 22.7 | 21.4 | 15.4 | 12.0 | 8.0 | 4.4 | 4.5 | 11.6 |
| DSpark | 20.2 | 17.0 | 15.3 | 11.3 | 9.0 | 7.4 | 3.6 | 16.2 |
| DFlash | 22.3 | 23.2 | 16.1 | 10.6 | 7.7 | 5.7 | 3.5 | 10.8 |
| PARD-1 | 33.7 | 22.6 | 15.8 | 8.2 | 6.5 | 4.4 | 2.2 | 6.6 |
| Qwen3-0.6B | 30.8 | 19.2 | 11.6 | 9.0 | 7.2 | 4.0 | 4.0 | 14.3 |
| EAGLE-3 | 39.8 | 20.4 | 14.0 | 6.7 | 4.2 | 3.0 | 2.7 | 9.2 |

### 5.3 Round time (ms, steady rounds, mean over repeats)

| Drafter | draft mean | draft p95 | target (verify) mean | target p95 | round mean | round p95 | Phone draft e2e | Phone client wait | Phone round mean |
|---|---|---|---|---|---|---|---|---|---|
| PARD-2 | 15.6 | 23.9 | 98.6 | 104.2 | 114.1 | 123.7 | 27.8 | 120.7 | 148.8 |
| DSpark | 27.2 | 29.2 | 100.2 | 107.2 | 127.4 | 135.5 | 38.8 | 120.6 | 160.3 |
| DFlash | 24.2 | 25.8 | 100.0 | 106.2 | 124.1 | 131.4 | 30.4 | 120.9 | 152.3 |
| PARD-1 | 13.0 | 18.9 | 98.2 | 103.7 | 111.3 | 119.2 | 21.9 | 114.8 | 137.0 |
| Qwen3-0.6B | 86.4 | 96.4 | 98.9 | 102.8 | 185.2 | 196.1 | 84.9 | 129.2 | 227.0 |
| EAGLE-3 | 88.8 | 93.5 | 99.2 | 105.6 | 188.0 | 197.6 | 114.5 | 124.3 | 239.4 |

**Draft-time notes:**
- **Commit:** the commit step inside the draft time averages 3.66 ms for EAGLE-3, which re-extends the committed cells through the head. It is 0.00–0.02 ms for the other drafters, which only store features or move pointers.
- **DSpark vs DFlash:** DSpark's draft is 3.0 ms longer than DFlash's (27.2 vs 24.2), which is the cost of its Markov chain. On the phone the host Markov head took 8.48 ms.
- **Qwen3-0.6B:** 7–8 single-row forwards per round at about 11.7 ms each.
- **EAGLE-3:** 6 single-layer head steps and 7 full-vocabulary LM-head reads per round.

### 5.4 Prefill and time to first token (ms, mean over requests and repeats)

| Drafter | target prefill (`prefill_ms`) | round 0 | first token committed after |
|---|---|---|---|
| PARD-2 | 306.4 | (= prefill) | 306.4 |
| DSpark | 315.8 | (= prefill) | 315.8 |
| DFlash | 318.0 | (= prefill) | 318.0 |
| PARD-1 | 304.1 (prompt minus its last token) | 153.8 | 457.9 |
| Qwen3-0.6B | 303.2 (prompt minus its last token) | 216.5 | 519.7 |
| EAGLE-3 | 318.3 | (= prefill) | 318.3 |

These include the cold prompt compute. They are not comparable with the phone arms' TTFT, which used cached prefill. A token drafter's round 0 commits at least 1 token and up to 8.

### 5.5 By category (MT-Bench sub-categories pooled; 10 requests each)

#### tok/s, server-only (phone chain7 in parentheses)

| Drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 | 37.5 (28.3) | 32.0 (22.8) | 24.7 (18.4) | 25.6 (19.3) | 52.1 (37.2) | 31.9 (23.5) |
| DSpark | 35.1 (26.8) | 32.3 (25.5) | 24.2 (19.1) | 27.4 (21.8) | 50.6 (40.3) | 33.5 (25.4) |
| DFlash | 31.8 (27.0) | 29.5 (23.8) | 22.5 (18.0) | 23.3 (19.0) | 48.7 (40.7) | 30.4 (24.7) |
| PARD-1 | 32.0 (25.0) | 20.3 (16.5) | 21.4 (17.2) | 23.1 (17.5) | 44.3 (35.2) | 27.1 (21.4) |
| Qwen3-0.6B | 21.8 (17.7) | 21.1 (16.9) | 15.9 (11.3) | 15.3 (11.9) | 30.1 (22.1) | 18.5 (13.4) |
| EAGLE-3 | 18.0 (13.5) | 15.1 (11.9) | 13.4 (10.2) | 11.0 (8.7) | 29.1 (21.7) | 16.2 (12.1) |

#### tok/round, server-only, steady rounds (phone chain7 in parentheses)

| Drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 | 3.81 (3.48) | 3.36 (2.87) | 2.91 (2.72) | 2.75 (2.60) | 5.67 (4.98) | 3.56 (3.31) |
| DSpark | 4.12 (3.85) | 3.97 (3.51) | 3.04 (2.96) | 3.30 (3.14) | 6.36 (5.89) | 3.89 (3.56) |
| DFlash | 3.48 (3.43) | 3.51 (3.17) | 2.75 (2.67) | 2.81 (2.73) | 5.93 (5.73) | 3.49 (3.34) |
| PARD-1 | 3.05 (2.96) | 2.10 (2.07) | 2.41 (2.31) | 2.48 (2.31) | 4.72 (4.43) | 2.88 (2.68) |
| Qwen3-0.6B | 3.64 (3.26) | 3.53 (3.61) | 2.91 (2.73) | 2.74 (2.54) | 5.58 (4.51) | 3.26 (3.00) |
| EAGLE-3 | 2.88 (2.63) | 2.74 (2.56) | 2.49 (2.38) | 2.03 (1.98) | 5.25 (4.68) | 2.86 (2.65) |

The phone's per-category tok/round pools all rounds of repeat 1, and the server-only figures are steady rounds, as in `results/final/server-only-chain.md`. So the two are not strictly the same statistic.

---

## 6. Validity checks

### 6.1 Repeatability

In every arm, repeat 2 reproduces repeat 1 exactly:
- the same k for every round of every request
- the same output tokens
- the same stop reasons (EOS: 11 requests for PARD-2, DFlash, PARD-1 and EAGLE-3; 12 for DSpark and Qwen3-0.6B; the rest stopped at the token limit)

Only the timings differ: steady tok/s moves by 0.04–0.52 between repeats.

### 6.2 Offline replay vs the C++ oracle (chain7, 60 requests, tok/round over decode rounds)

| Drafter | PyTorch bf16 replay | C++ oracle | Oracle precision | Live server-only | Live phone |
|---|---|---|---|---|---|
| DFlash | 3.44 | 3.42 | Q4_0 | 3.43 | 3.45 |
| DSpark | 3.88 | 3.86 | Q4_0 | 3.90 | 3.83 |
| EAGLE-3 | 2.86 | 2.80 | Q4_0 | 2.81 | 2.71 |
| PARD-1 | 2.90 | 2.78 (fp32 HF oracle: 2.909) | Q4_0 | 2.86 | 2.76 |
| Qwen3-0.6B | 3.38 | 3.11 | Q4_0 | 3.42 | 3.11 |
| PARD-2 | 3.61 | 3.580 | fp32 HF (`oracle/pard2_td`, semantics B) | 3.50 | 3.34 |

- **Interpretation:**
  - The bf16 replay sits at or slightly above the Q4_0 oracle for every drafter. The size of the gap matches what quantisation costs.
  - PARD-1's bf16 replay (2.90) matches its fp32 oracle (2.909).
  - Qwen3-0.6B's +0.27 matches the 10-16 fp16 PyTorch AR run (3.37 tok/round).
- **Round-for-round agreement with the Q4_0 oracle rounds:** 513/1078 (DFlash), 599/974 (DSpark), 740/1288 (EAGLE-3), 326/1269 (PARD-1, eager) and 224/1097 (Qwen3-0.6B). Exact round agreement is not expected across precisions: one changed draft shifts every later round of that request.
- **Replay draft time** (GPU, no target): DFlash 24.2, DSpark 26.7, EAGLE-3 87.0, PARD-1 12.6 (graph), PARD-2 15.4 (graph), Qwen3-0.6B 83.0 ms (eager). These are within 0–3.4 ms of the live draft times (§5.3).

### 6.3 Output agreement (first 64 output tokens, repeat 1)

| Comparison | Identical requests | Median first difference |
|---|---|---|
| The four feature drafters (PARD-2, DSpark, DFlash, EAGLE-3) with each other, server-only | 60/60 | n/a |
| The two token drafters (PARD-1, Qwen3-0.6B) with each other, server-only | 60/60 | n/a |
| Token drafters vs feature drafters, server-only | 57/60 | token 58 |
| Each token drafter vs its own phone chain7 arm | 60/60 | n/a |
| Each feature drafter vs its own phone chain7 arm | 52/60 | token 49 |
| On the phone, PARD-1 chain7 vs DFlash chain7 (from `results/final/output-agreement.md`) | 53/60 | token 35 |

- **Two groups of outputs.**
  - Within a server-only run, every drafter of the same group produces the same output. The groups differ by how the target sees the last prompt token: a feature drafter's prefill covers the whole prompt, while a token drafter's prompt ends in round 0's 8-row verify.
  - Together with the 52/60 for the feature drafters vs their phone arms, this shows that the output depends on the target's numerics (FP8, fp16 activations, the exact batch shape), not on the drafter. Speculative decoding at t=0 is lossless only up to those numerics.
- **The cause of the 8 feature-drafter differences vs the phone was not investigated.** The phone arms' server prefilled from a cache, and the server-only runs compute the prefill live.

---

## 7. Limitations

- **Chain only (depth 7).** There are no server-only trees for the block or feature drafters. The phone's best arms are trees: PARD-2 own-best reaches 30.0 tok/s on the phone.
- **bf16 drafts vs Q4_0 on the phone.** The comparison mixes the drafter's location with its precision. The acceptance gain is +0.02 to +0.16 tok/round for five drafters (DFlash −0.02), and +0.31 for Qwen3-0.6B.
- **Little GPU-specific optimisation of the drafts:**
  - CUDA graphs only for the PARD block. AR and EAGLE-3 steps are eager. DFlash and DSpark use eager PyTorch with SDPA.
  - No fused kernels, no quantised drafts.
  - The target runs without CUDA graphs (as `server_only.py`).
- **Single process, batch size 1, one request at a time.**
  - The draft and the target share the GPU. They never run concurrently, because drafting and verifying alternate.
  - These results say nothing about serving several clients.
- **Target numerics.** Verify rows are padded to 8 with a causal mask. Feature rows are cast from fp16 to bf16 inside the process rather than serialized.
- **64 new tokens per request, cold prefill.** TTFT (§5.4) includes the prompt compute and is not comparable with the phone arms' TTFT.
- **One node (spark2), two repeats.** The repeats are bit-identical in acceptance. Their steady tok/s agree within 0.52.
- **Not merged:** branch `eval/so-chain` is not merged into `eval/drafters`.

---

## 8. Reproducing

```bash
# code: specedge branch eval/so-chain (commit 3c22ed0), worktree drafter-evaluation/wt/so-chain/specedge
# on spark2, from ~/vafbaguio/specedge-so-chain (git archive of that commit; venv ../venv312)
bash run_chain.sh replay-smoke            # 3 requests per drafter vs the oracle
bash run_chain.sh replay                  # 60-request replays, result/so-chain/replay-<kind>/summary.json
bash run_chain.sh live-smoke              # 16 requests per drafter
bash run_chain.sh live                    # 2 repeats x {pard ar pard2 dflash dspark eagle3}, result/so-chain/so-chain-<kind>-chain7-r<k>/
# one live run by hand:
HF_HUB_OFFLINE=1 SPECEDGE_CACHE_PREFILL=False PYTHONPATH=src \
  ../venv312/bin/python -O src/script/server_only_chain.py --config config/so-chain/so-chain-dflash-chain7-r1.yaml
# tables, on the Mac
cd /Users/vafbaguio/kaist/ina/drafter-evaluation/analysis
uv run --no-project --with numpy --with pyyaml python server_only_chain.py \
  ../results/2026-10-19/server-only-chain > ../results/final/server-only-chain.md
```

**Rule for the shared nodes:** start a GPU job only on a node whose `nvidia-smi` shows no other compute process. `run_chain.sh` checks this before every run.
