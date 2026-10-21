# Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)

**Runs:** 2026-10-15 20:36 → 2026-10-16 03:45 KST · 37 live runs, all finished OK · workspace `kaist/ina/drafter-evaluation/`

This file describes the experiments (setup, procedure, metrics and how each was computed) and gives the full results for the three tree shapes, chain, matched tree and own-best tree, separately.
The file is generated: `report/drafter-evaluation.src.md` plus the tables from `analysis/shape_metrics.py`, `analysis/output_agreement.py` and the run metadata, assembled by `report/build_report.py`.

---

## 1. Summary

tok/s, steady state (prefill round excluded), mean over requests and then over repeats:

| Drafter | Chain (depth 7) | Matched tree (budget 16) | Own-best tree (budget 32) |
|---|---|---|---|
| PARD-2 (target-dependent) | 24.9 | **29.3** | **30.0** |
| DFlash | 25.5 | 27.9 | 28.8 |
| DSpark | **26.5** | 28.3 | 28.2 |
| PARD-1 | 22.1 | 26.7 | 26.7 |
| Qwen3-0.6B | 15.6 | 16.6 | 18.5 |
| EAGLE-3 (DeepSpec ttt7) | 13.0 | 15.9 | 17.6 |

**Main findings:**

1. **Block drafters beat autoregressive (AR) drafters by about 1.6–1.8×.**
   - PARD-1, PARD-2, DFlash and DSpark draft a whole tree from one decode, in 22–54 ms including host-side work.
   - Qwen3-0.6B and EAGLE-3 run one decode per tree level, 85–116 ms in total. Their acceptance is not higher enough to pay for that.
2. **PARD-2 is the best drafter with a tree. DSpark is the best chain drafter.**
   - PARD-2 has the lowest TTFT. Its feature rows are 1024 wide instead of 5120, so it downloads 5× less than DFlash, DSpark and EAGLE-3.
   - The top three drafters are within 2 tok/s of each other in every shape.
3. **PARD-1 is the best drafter that needs nothing from the server.** It needs no server-side drafter code and downloads close to 0 bytes per token. It is weak on translation.
4. **Own-best trees help the AR drafters (+11%) but barely change the block drafters (−0.4% to +3%).**
5. **DSpark's Markov head costs as much as it gains.** It has the highest acceptance in every shape, but the head adds 8.5–24 ms per round, and the extra cost grows with the tree.

---

## 2. Experimental setup

### 2.1 What one round does

Split speculative decoding, with one phone client and one GPU server.

**Each round:**
1. **Draft (phone).** The phone drafts a chain or tree of candidate tokens on its NPU.
2. **Request.** It sends the tree to the server as rows: the seed (last committed token) plus every drafted node.
3. **Verify (server).** The server runs one Qwen3-14B forward over all rows with a tree attention mask.
4. **Accept.** The server accepts the longest path that matches greedy target decoding, plus one bonus token.
5. **Response.** The server returns the accepted count and the bonus token, plus target features for drafters that use them.
6. **Commit (phone).** The phone commits those tokens and fixes up its KV cache.

**Steady and prefill rounds:**
- Round 0 (`step_idx` 0) is the **prefill round**. The prompt prefill on the server comes from a cache; see §2.4.
- All later rounds are **steady rounds**.

### 2.2 Hardware and network

| Part | What |
|---|---|
| Phone (drafts) | Samsung Galaxy S25 (Snapdragon 8 Elite, Hexagon v79 NPU). The draft runs on the NPU (`HTP0`) through llama.cpp's Hexagon backend. Options: flash attention on, `hexagon_oppoll`, 6 CPU threads, host-side top-k scoring (`draft_scoring: host`). Rebooted 10-15 20:26, before the first run. |
| Server (verifies) | `spark4` (34 runs) and `spark2` (3 runs: PARD-2 repeat 1): NVIDIA DGX Spark (GB10). Both nodes have identical hardware. specedge `batch_server.py`, one GPU (`cuda:0`), batch size 1, one client. |
| Network | Direct over the lab WiFi (SSID `inalab`), with no tunnel or relay. spark4 at 172.16.60.106:10100, spark2 at 172.16.61.114:10100. gRPC protobuf. |
| Host | MacBook (16 GB) runs the harness, which drives the phone over adb and the server over ssh. |

### 2.3 Target and drafters

**Target:** `Qwen/Qwen3-14B-FP8` on the server.
- FP8 weights, fp16 activations, with the sync-free FP8Linear patch.
- Thinking mode is off (`reasoning: false`, Jinja chat template with `enable_thinking=false`).

**Every draft model:**
- is converted to GGUF and quantised to pure **Q4_0**
- runs through the same evaluation build of llama.cpp (`dbe1a6c`: ce8caa6 + Hexagon scalar-scatter patch + EAGLE-3 DeepSpec patch).

| Drafter | Source checkpoint | Phone file (size) | Client mode | Server-side drafter code (`server:` key) | Sent back to the phone each round |
|---|---|---|---|---|---|
| Qwen3-0.6B | `Qwen/Qwen3-0.6B` | `Qwen3-0.6B-Q4_0.gguf` (409 MB) | AR tree (`GrowTree`), one `llama_decode` per level | none | nothing beyond tokens |
| EAGLE-3 | `deepseek-ai/eagle3_qwen3_14b_ttt7` (DeepSpec) | `…eagle3-deepspec-ttt7-Q4_0.gguf` (1108 MB; full-vocabulary LM head, q/k norm) | AR tree + target features | `eagle_model`: target layers tapped and passed through the head's `fc` | post-`fc` feature row per committed token (5120 × fp16 = 10 KB) |
| DFlash | `deepseek-ai/dflash_qwen3_14b_block7` | `Qwen3-14B-DFlash-Q4_0.gguf` (1741 MB) | block draft (`GrowBlock`): 7 positions in one decode, tree built on the host from per-position top-k | `dflash_model`: target layer taps + DFlash encoder | encoder feature row per committed token (5120 × fp16 = 10 KB) |
| DSpark | `deepseek-ai/dspark_qwen3_14b_block7` | `…DSpark-host-Q4_0.gguf` (1741 MB) + `…DSpark-markov-Q4_0.gguf` (42 MB) | block draft + Markov head on the host CPU (rescores each next position given the token chosen before it) | `dflash_model` (DSpark encoder) | encoder feature row per committed token (5120 × fp16 = 10 KB) |
| PARD-1 | `amd/PARD-Qwen3-0.6B` | `PARD-Qwen3-0.6B-pard-Q4_0.gguf` (409 MB, GGUF tag `specedge.pard.mask_token`) | block draft: one causal decode of [accepted tokens, K−1 mask tokens], tree built by `GrowBlock` | none | nothing beyond tokens |
| PARD-2 (target-dependent) | `amd/PARD2-Qwen3-14B` | `PARD2-Qwen3-14B-pard2-Q4_0.gguf` (409 MB, tag `specedge.pard2.feature_width=1024`) | block draft with input = token embedding + 1024-wide target feature, built on the host and passed as an embedding batch | `pard2_model`: target layers 17/25/33 + final post-norm, projected 20480→1024 by `target_proj` (40 MB, on the server) | feature row per committed token (1024 × fp16 = 2 KB) |

Feature drafters also receive one feature row per **prompt** token in round 0 (≈279 prompt tokens on average, so 2.8 MB per request at 5120 wide and 0.56 MB for PARD-2).

PARD-2's target-independent mode was dropped before the live runs: the offline oracle on 10-15 gave it 2.0 tok/round as a chain.

### 2.4 Workload

**Requests:**
- **Dataset:** SpecBench, 480 prompts (`mobile-specedge/data/specbench_prompts.jsonl`).
- **Sample:** every 8th prompt (`sample_req_cnt: 8`, `req_offset: 0`), giving 60 requests.
- **Per category:**
  - **MT-Bench:** 10 requests across its 8 sub-categories (writing, roleplay, reasoning, math, coding, extraction, STEM, humanities). They are pooled into one `mt_bench` category in the per-category tables.
  - **translation, summarization, qa, math_reasoning, rag:** 10 requests each.
- **The same 60 requests run in the same order in every arm.**

**Decoding:** temperature 0 (greedy), `max_new_tokens: 64`, `max_len: 2048`, seed 42.

**Concurrency:** one client and batch size 1, so the server never batches two requests together.

**`cache_prefill: true`:** the server loads each prompt's prefill KV from a cache built beforehand instead of computing it. TTFT therefore excludes the server's prompt compute, and is not real cold-start TTFT; see §7.

**Proactive drafting** (speculating during the verify wait) is **off** in every arm.

### 2.5 Arms (tree shapes)

Shape parameters, as defined in `harness/arms.yaml`:

| Parameter | Meaning |
|---|---|
| `max_n_beams` | beams kept per level (AR drafters only) |
| `max_beam_len` | depth |
| `max_branch_width` | children per node |
| `max_budget` | drafted nodes |

The server takes exactly `max_budget + 1` rows per round, so each (server key, budget) pair has its own server config. A server restart was needed between budgets.

| Shape | Block drafters (PARD-1/2, DFlash, DSpark) | AR drafters (Qwen3-0.6B, EAGLE-3) | Rows verified per round |
|---|---|---|---|
| **chain7** | depth 7, width 1, budget 7 | 1 beam, depth 7, width 1, budget 7 | 8 |
| **tree16** (matched) | depth 7, width 8, budget 16 | 8 beams × depth 6 × width 4, budget 16 | 17 |
| **own-best** | DFlash, DSpark: depth 7, width 8, budget 32 (`l7w8b32`)<br>PARD-1, PARD-2: depth 8, width 8, budget 32 (`l8w8b32`) | 8 beams × depth 6 × width 8, budget 32 (`n8l6w8b32`) | 33 |

**Block tree build:** a block tree is built best-first on the host from each position's top-k, under the budget.

**Depth limits:**
- **DFlash and DSpark** produce at most 7 positions per block, so their depth is capped at 7.
- **PARD** can draft 8 positions (8 rows of masks).

**Why the AR matched tree is 8 × 6 × 4:** with budget 16, a width-8 AR tree would be only two levels deep. 8 beams × 6 levels × width 4 is the best shape family from the 09-28 phone sweep, cut to budget 16.

### 2.6 How the own-best trees were chosen

The own-best shapes were picked offline, before the live runs, with the **acceptance oracle** (`oracle/`).

**How the oracle works:**
- It replays each drafter on the host (same Q4_0 GGUF, CPU) against the recorded greedy target outputs of the same 60 requests.
- It uses the recorded target feature rows (`oracle/features/`, written by `specedge/src/script/dump_features.py`).
- This gives exact tokens/round for any shape without a phone or server.

**How round time was estimated:** from the cost model in `oracle/cost_model.yaml`, not measured:
- **Draft time:** measured per-level and per-block times on the phone.
- **Verify time:** server forward time vs row count (8 → 92 ms, 17 → 99.5, 25 → 101.5, 33 → 106 ms), plus 11 ms server overhead and 16 ms network.

**Choice:** the best modelled tok/s per drafter (`oracle/ranking-quick.md`, `oracle/rank-quick.txt`).

**Budget 64:** budget-64 shapes tied with or beat budget 32 only through an extrapolated 65-row verify time, so budget 32 was taken.

---

## 3. Procedure

### 3.1 Per-arm steps (`harness/run_eval.sh`)

For every run of an arm:

1. **GPU-free check on the server node.**
   - `nvidia-smi --query-compute-apps`: any GPU process that is not our `batch_server` aborts the run before the arm starts.
   - The snapshot is saved as `nvidia-smi.txt`.
   - The run was set to stop rather than share a GPU with another user. Other users took the nodes several times; each time the run stopped cleanly at this check.
2. **Server check.**
   - Our server must be running this arm's server config (`configs/server/<node>-<key>-b<budget>.yaml`).
   - With `--start-servers`, the harness stops our previous server and starts this one in tmux. It then waits for "Inference controller initialized".
   - A server whose log does not change for 120 s before it is ready is restarted, up to 3 times. This is a workaround for the startup stall in §3.4.
3. **Phone wake.** `KEYCODE_WAKEUP` and keyguard dismiss, because a dozing phone stalls the decode loop.
4. **Thermal gate.** Wait until the phone's `thermal_zone0` is ≤ 36 °C, for up to 1200 s. The wait is recorded in `run_meta.json` (`cooldown`).
5. **Telemetry.** `harness/device/telemetry.sh` samples `phone_telemetry.csv` on the phone:
   - every 5 s: VmRSS/VmHWM, temperatures (tz0, CPU, NPU/HMX) and CPU frequency caps
   - every 30 s: client and total DMA-BUF
6. **Client run.**
   - The client (`client-htp-eval[-pard2]`) runs the arm's YAML (`configs/client/<arm>.yaml`) with the HTP0 environment, under a 60 s stall watchdog on its stderr.
   - A dropped adb connection triggers an alert and stops the run.
7. **Collect.** Into `results/<YYYY-MM-DD>/<arm>-r<k>/`:
   - client logs (`client_0.jsonl`, `requests.jsonl`, `trace.jsonl`, `run.out/err`)
   - the server's `server.jsonl` rows for this arm, selected by the arm's `exp_name` and timestamps
   - `phone_telemetry.csv`, `nvidia-smi.txt`, both configs
   - `run_meta.json`: status, SHA-256 of every config and of the binary on the phone, git SHAs, node, network path, start/end time, tz0 at start and end, cool-down

**Repeats and ordering:**
- Repeats are interleaved: all arms run once before any runs a second time.
- Within a repeat, arms are grouped by server config, so there is one server start per group.
- `--resume` skips arms that already have a finished run (status ok and 60 requests).

### 3.2 Run inventory

18 arms (6 drafters × 3 shapes). Every arm has 2 repeats; DFlash tree16 has a third, run on the newer binary as a cross-binary check. That is 37 runs, all with status `ok`, 60 requests, and server rows joined for every round.

| # | run | folder | node | binary | binary sha256 | client git | server git | start | end | cool-down s | tz0 at start °C |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | qwen3-0.6b-chain7-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 20:36 | 20:41 | 0 | 35.3 |
| 2 | pard1-chain7-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 20:45 | 20:48 | 220 | 35.7 |
| 3 | qwen3-0.6b-tree16-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 20:50 | 20:55 | 10 | 35.7 |
| 4 | pard1-tree16-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 21:01 | 21:04 | 400 | 35.7 |
| 5 | eagle3-chain7-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 21:07 | 21:12 | 30 | 35.7 |
| 6 | eagle3-tree16-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 21:22 | 21:26 | 440 | 35.7 |
| 7 | dflash-chain7-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 21:37 | 21:40 | 410 | 36.1 |
| 8 | dflash-tree16-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 21:44 | 21:47 | 160 | 35.7 |
| 9 | dspark-chain7-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 21:52 | 21:55 | 140 | 35.7 |
| 10 | dspark-tree16-r1 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 21:59 | 22:02 | 150 | 36.1 |
| 11 | dspark-tree16-r2 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 22:06 | 22:08 | 230 | 36.1 |
| 12 | dspark-chain7-r2 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 22:14 | 22:16 | 190 | 36.5 |
| 13 | dflash-tree16-r2 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 22:21 | 22:24 | 140 | 35.7 |
| 14 | dflash-chain7-r2 | 2026-10-15 | spark4 | …eval | 68efc013 | b300fed | 3c525f8 | 22:28 | 22:31 | 120 | 35.7 |
| 15 | pard2-chain7-r1 | 2026-10-15 | spark2 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 23:49 | 23:52 | 0 | 29.9 |
| 16 | pard2-tree16-r1 | 2026-10-15 | spark2 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 23:54 | 23:57 | 0 | 32.6 |
| 17 | pard2-own-l8w8b32-r1 | 2026-10-15 | spark2 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 23:59 | 00:01 | 0 | 33.4 |
| 18 | pard2-own-l8w8b32-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 00:45 | 00:47 | 0 | 29.9 |
| 19 | pard2-tree16-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 00:49 | 00:52 | 0 | 31.9 |
| 20 | pard2-chain7-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 00:54 | 00:57 | 0 | 33.0 |
| 21 | dflash-tree16-r3 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 01:04 | 01:07 | 0 | 31.9 |
| 22 | qwen3-0.6b-own-n8l6w8b32-r1 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 01:09 | 01:13 | 0 | 34.9 |
| 23 | pard1-own-l8w8b32-r1 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 01:17 | 01:20 | 230 | 36.1 |
| 24 | eagle3-own-n8l6w8b32-r1 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 01:47 | 01:51 | 0 | 30.7 |
| 25 | dflash-own-l7w8b32-r1 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 01:56 | 01:59 | 170 | 35.7 |
| 26 | dspark-own-l7w8b32-r1 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 02:02 | 02:05 | 70 | 36.1 |
| 27 | dspark-own-l7w8b32-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 02:08 | 02:11 | 180 | 36.1 |
| 28 | dflash-own-l7w8b32-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 02:14 | 02:17 | 90 | 35.7 |
| 29 | eagle3-own-n8l6w8b32-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 02:20 | 02:24 | 70 | 35.7 |
| 30 | pard1-own-l8w8b32-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 02:32 | 02:34 | 210 | 36.1 |
| 31 | qwen3-0.6b-own-n8l6w8b32-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 02:37 | 02:41 | 160 | 36.1 |
| 32 | eagle3-tree16-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 02:48 | 02:52 | 270 | 35.7 |
| 33 | eagle3-chain7-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 03:02 | 03:07 | 60 | 35.7 |
| 34 | pard1-tree16-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 03:17 | 03:20 | 320 | 36.1 |
| 35 | qwen3-0.6b-tree16-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 03:23 | 03:27 | 180 | 35.7 |
| 36 | pard1-chain7-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 03:34 | 03:37 | 290 | 35.7 |
| 37 | qwen3-0.6b-chain7-r2 | 2026-10-16 | spark4 | …eval-pard2 | 2854e2ab | 8f6353b | 9b89477 | 03:40 | 03:45 | 190 | 35.7 |

**Binaries on the phone:**
- `client-htp-eval`: sha256 `68efc013…`, from mobile-specedge `b300fed`.
- `client-htp-eval-pard2`: sha256 `2854e2ab…`, from `8f6353b`. It is `b300fed` plus the PARD-2 client mode.

**Server code** (specedge): `3c525f8` for the 10-15 runs before PARD-2, `9b89477` for PARD-2 and every run after it (adds `pard2_model`).

**Run time:** each run took 2–5 minutes, plus 0–440 s of cool-down.

### 3.3 Software versions

| Component | Version |
|---|---|
| mobile-specedge (client) | `eval/drafters`, `b300fed` (main matrix repeat 1, and 10-15 repeat 2 of DFlash/DSpark), `8f6353b` (everything else) |
| specedge (server) | `eval/drafters`, `3c525f8` (10-15 runs before PARD-2), `9b89477` (PARD-2 and every run after it) |
| llama.cpp (phone) | `dbe1a6c` = ce8caa6e6 + `hexagon-scalar-scatter-on-cpu.patch` + `eagle3-deepspec.patch` |
| Server Python | `venv312` (Python 3.12), copied from spark3 to spark4 |
| Harness/configs | `drafter-evaluation` repo; configs generated from `harness/arms.yaml` by `harness/make_arms.py` |

### 3.4 Incidents and deviations

- **Server startup stall.**
  - **What happens:** the server's inference child process, forked from a multi-threaded parent, sometimes deadlocks while loading the tokenizer, before "Initializing inference controller".
  - **When:** about 8 times over the night, mostly on EAGLE-3 server configs. The first time, it stopped the main matrix after DFlash/DSpark repeat 2.
  - **How it was handled:** the harness restarts the server.
  - **Effect on results:** none, because a stall happens before any request.
  - **Proper fix:** start the child with the spawn method. Not done yet.
- **Other users on the GPU nodes.**
  - Jobs from another account (including under the shared `ina_spark4` login) took spark2 and spark4 several times.
  - Runs stopped at the pre-arm GPU check and resumed later with `--resume`.
  - No arm ran while a foreign process was on the GPU.
- **PARD-2 repeat 1 ran on spark2**, because spark4 was busy; every other run used spark4. The two nodes have identical hardware; see §6.2 for the comparison.
- **Two client binaries.** See §3.2 for which runs used which. §6.2 checks that the newer binary changes nothing for the drafters that both binaries support.
- **One stopped attempt.** `results/2026-10-15/pard2-own-l8w8b32-r2/` is empty, from a run stopped before it started. Ignore it. The real repeat 2 is in `2026-10-16/`.
- **Spurious thermal-gate warning.** "still above 36 C" appears when tz0 is re-read at 36.1 °C right after the gate passes. It is cosmetic.

---

## 4. Metrics

### 4.1 Where each metric is recorded

| File (per run folder) | Written by | Granularity | Contents |
|---|---|---|---|
| `client_0.jsonl` | phone client (`SpecExecClient::LogCycle`, `src/spec_exec_client.cpp`) | one line per round | `req_idx`, `step_idx`, `prompt_len`, `context_len`<br>draft shape: `draft.n_nodes`, `draft.depth`, `draft.n_beams[]`<br>per-level draft timings: `draft.decode[]`, `sync[]`, `readback[]`, `topk[]`, `markov[]`, `markov_rows[]`, `fork[]`, `forward[]`, `forward_log[]`, plus `draft.residual` and `draft.end_to_end`<br>`target.client_preprocess`, `client_wait`, `client_postprocess`, `end_to_end`<br>`net.rpc_ms`, `net.bytes_up`, `net.bytes_down`, `net.feature_bytes_down`<br>`num_accepted_tokens`; monotonic `t_send_ns`, `t_recv_ns`, `t_emit_ns`<br>proactive fields (unused here) |
| `server.jsonl` | server (`src/strategy/server_verify/specexec/grpc.py`) | one line per verify batch | `target.forward_t` (CUDA-event time of the verify forward), `target.server_end_to_end_t` (wall time), `target.prefill`<br>`batch.size`, `client_idx[]`, `req_idx[]`, `step_idx[]`, `n_rows[]`, `n_rows_computed[]`, `num_accepted_tokens[]`, `bytes_in[]`<br>`arrival_ts[]`, `start_ts`, `end_ts`, `queue_wait_t[]`, `idle_t`, `left_in_queue` |
| `requests.jsonl` | phone client | one line per request | `question_id`, `category`, `prompt_len`<br>`n_generated` (raw and trimmed to 64), `stop_reason`, `n_rounds`<br>`t_request_start_ns`, `t_first_emit_ns`, `t_last_emit_ns`, `ttft_ms`, `decode_ms`<br>`bytes_up`, `bytes_down`, `feature_bytes_down`, `prefill_bytes_down`, `prefill_feature_bytes_down`<br>`mem.vm_rss_kb`, `mem.vm_hwm_kb` (from `/proc/self/status` at request end)<br>echo of the shape config; steady/epoch clock pair |
| `trace.jsonl` | phone client | one line per request | prompt and output text and token IDs (used for the output-agreement check, §6.4) |
| `phone_telemetry.csv` | `harness/device/telemetry.sh` on the phone | every 5 s (DMA-BUF every 30 s) | client VmRSS/VmHWM, client DMA-BUF, total DMA-BUF<br>`thermal_zone0`, CPU and NPU (`nsphmx`) temperatures<br>`scaling_max_freq` and `scaling_cur_freq` of CPU0 (little cores) and CPU6 (prime core) |
| `nvidia-smi.txt` | harness, before the arm | once | GPU processes: ours vs others |
| `run_meta.json` | harness | once | status, exit code, config and binary SHA-256, git SHAs, node, network path, phone address, start/end, tz0 start/end, cool-down wait, stall kills |

**Clocks:**
- Client timings are wall-clock `steady_clock` on the phone.
- Server forward time uses CUDA events; server end-to-end is wall time on the server.
- The two clocks are never compared directly. Network time is derived as a difference of durations; see §4.2.

**Bytes:** protobuf payload bytes (`ByteSizeLong()`), excluding gRPC/HTTP2/TCP overhead.

**Joining client and server rows:** `analysis/eval_report.py` joins them exactly on (`client_idx`, `req_idx`, `step_idx`). All rounds of all 37 runs joined.

### 4.2 Definitions and how each metric is calculated

All per-round statistics use **steady rounds** (`step_idx ≥ 1`) unless the definition says otherwise.

**Acceptance**

| Metric | Definition / calculation |
|---|---|
| k (`k_incl_bonus`) | tokens a round commits = accepted draft tokens + 1 bonus token (the client's `num_accepted_tokens`) |
| `k_draft` | k − 1, accepted draft tokens only |
| **tok/round** | Σ k / number of steady rounds, pooled over all of the arm's rounds (includes the bonus token) |
| rounds | number of rounds over all 60 requests (including round 0) |
| P(k=0) | fraction of steady rounds that accepted no draft token (only the bonus token was committed) |
| P(full depth) | fraction of steady rounds with `k_draft` = the shape's depth (`max_beam_len`) |
| survival aj | P(`k_draft` ≥ j), j = 1…depth: the fraction of rounds whose accepted path reached depth j |
| accepted-length histogram | distribution of `k_draft` over steady rounds |

**Phone draft time** (ms per round, summed over a round's tree levels)

| Metric | Definition / calculation |
|---|---|
| draft total (`draft_end_to_end`) | the whole draft phase of a round |
| decode | `llama_decode` on the NPU, LM head included |
| host top-k | log-softmax + top-k over the vocabulary on the CPU |
| Markov | all of DSpark's host Markov head. Part of it runs during the tree build and is therefore also counted inside fork, so for DSpark draft total ≈ decode + top-k + Markov. |
| readback | logits/feature reads |
| fork | tree build: KV `seq_cp` forks for AR drafters, best-first build for block drafters (for DSpark this includes the Markov rows already counted in Markov) |
| residual | draft total − forward − fork |
| post-processing (`client_postprocess`) | after the response: acceptance, KV cache fix-up, and for AR drafters re-decoding the accepted tip |

**Round and server time** (ms)

| Metric | Definition / calculation |
|---|---|
| client wait | the blocking Validate RPC round trip, seen by the phone |
| round time | draft total + client preprocess + client wait + client postprocess |
| verify | server end-to-end time for the batch (wall time, including sync) |
| server forward | CUDA-event time of the target forward |
| queue wait | server-side wait before the batch starts |
| rows / round | rows the server verified (`batch.n_rows`) |
| **network time** | client wait − verify, per joined round: everything in the round trip the server's timer does not cover (WiFi, gRPC, serialisation, server IPC) |
| GPU ms / token | Σ (server forward / batch size) / Σ k over steady joined rounds |

**Throughput** (tok/s)

| Metric | Definition / calculation |
|---|---|
| **tok/s (steady)** | per request: Σ k over its steady rounds / Σ round time of those rounds × 1000; then the mean over the 60 requests; then the mean over repeats |
| tok/s incl. prefill | the same over all rounds, round 0 included |
| pooled tok/s | Σ k / Σ round time over all of the arm's steady rounds; long requests weigh more |
| network-normalised tok/s | as tok/s, with each round's network time replaced by one reference (14.5 ms, the median network time over all 37 runs): round′ = round − network + 14.5. This removes WiFi variance between arms. |
| emit decode tok/s | tokens after round 0 / (last emit − first emit), from emit timestamps |
| 95% CI | bootstrap over requests (1000 resamples, seed 0) of the mean per-request tok/s; shown for repeat 1 |

**Latency** (ms)

| Metric | Definition / calculation |
|---|---|
| **TTFT** | request start → round 0's emit (`t_first_emit_ns − t_request_start_ns`); p50/p95/mean over the 60 requests<br>Drafters without target features (Qwen3-0.6B, PARD-1) prefill the prompt on the phone in round 0. Feature drafters send the seed alone and get the prompt's features back. |
| round gap | emitᵢ − emitᵢ₋₁ for consecutive rounds, one value per steady round, pooled over requests |
| ITL | per-token gaps: the first token of a round gets that round's gap, and the other k−1 tokens get 0, because they arrive together. With more than 2 tokens/round the p50 is 0 by construction, which is why the round gap is reported alongside. |

**Network traffic** (KB)

| Metric | Definition / calculation |
|---|---|
| KB up / KB down per round | mean protobuf request / response payload over steady rounds |
| KB down / token, steady | Σ response bytes / Σ k over steady rounds: the cost per generated token after the first round |
| prompt features / request | round 0's feature bytes (`prefill_feature_bytes_down`): one feature row per prompt token |
| KB per token, all rounds | Σ bytes over all rounds (round 0 included) / Σ k. At 64 new tokens it is dominated by the prompt features. |
| feature KB down | the feature field of the response, which is almost all of the download for feature drafters |

**Phone memory and telemetry**

| Metric | Definition / calculation |
|---|---|
| client peak memory (VmHWM) | maximum over the run of the client's peak resident set (`/proc/self/status`)<br>Does **not** include HTP buffers, which live in DMA-BUF |
| client DMA-BUF | peak over the run of the DMA-BUF bytes held by the client process (NPU weights, KV, compute buffers), from `phone_telemetry.csv` |
| peak temperatures, lowest CPU caps | max (temperatures) or min (`scaling_max_freq`) over a run's telemetry samples |

**Per category:**
- **tok/s:** the mean of the per-request steady tok/s over that category's 10 requests.
- **tok/round:** pooled within the category.
- **MT-Bench:** its 8 sub-categories are pooled into one row.

**Over repeats:** every metric is computed per run and then averaged over the repeats. tok/s also shows the min–max over repeats.

### 4.3 Analysis pipeline

```
results/<date>/<arm>-r<k>/             raw logs (§4.1)
  └─ analysis/eval_report.py --compare <all 37 run folders> --out results/final/per-run
        → per-run/<arm>-r<k>/{rounds.csv, requests.csv, summary.json}, compare_overall.csv, compare_by_category.csv
  └─ analysis/final_tables.py results/final/per-run                → results/final/tables.md
  └─ analysis/shape_metrics.py results/final/per-run <chain7|tree16|own> → results/final/<shape>-all-metrics.md
  └─ analysis/output_agreement.py results/2026-10-15 results/2026-10-16 → results/final/output-agreement.md
  └─ report/build_report.py                                        → report/drafter-evaluation.md (this file)
```

---

## 5. Results

Rows are drafters. The number in brackets after a name is the number of repeats averaged (own-best rows also give the shape). Values are means over repeats unless the column says otherwise.

### 5.1 Chain (depth 7, 8 rows verified)

#### Throughput

| drafter | tok/s steady | min..max | 95% CI (r1) | tok/s incl. prefill | pooled tok/s | network-normalised tok/s | emit decode tok/s |
|---|---|---|---|---|---|---|---|
| PARD-2 (2) | **24.9** | 24.6..25.3 | 23.2..27.5 | 23.5 | 22.5 | 25.3 | 24.9 |
| DSpark (2) | **26.5** | 26.5..26.6 | 24.3..28.8 | 24.3 | 23.9 | 26.9 | 26.5 |
| DFlash (2) | **25.5** | 25.5..25.6 | 23.1..28.0 | 23.4 | 22.7 | 25.9 | 25.5 |
| PARD-1 (2) | **22.1** | 22.1..22.2 | 20.1..24.4 | 20.8 | 20.2 | 21.9 | 22.1 |
| Qwen3-0.6B (2) | **15.6** | 15.5..15.6 | 14.1..17.1 | 15.2 | 13.7 | 16.7 | 15.6 |
| EAGLE-3 (2) | **13.0** | 12.9..13.2 | 11.6..14.3 | 12.4 | 11.3 | 13.4 | 13.0 |

#### Acceptance

aj = fraction of rounds whose accepted path reached depth j (survival curve); depth = deepest drafted level.

| drafter | tok/round | rounds | P(k=0) | depth | P(full depth) | a1 | a2 | a3 | a4 | a5 | a6 | a7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 3.34 | 1116 | 0.252 | 7 | 0.093 | 0.748 | 0.548 | 0.384 | 0.255 | 0.188 | 0.128 | 0.093 |
| DSpark (2) | 3.83 | 995 | 0.214 | 7 | 0.160 | 0.786 | 0.611 | 0.462 | 0.346 | 0.263 | 0.198 | 0.160 |
| DFlash (2) | 3.45 | 1083 | 0.205 | 7 | 0.104 | 0.795 | 0.539 | 0.386 | 0.277 | 0.203 | 0.150 | 0.104 |
| PARD-1 (2) | 2.76 | 1321 | 0.363 | 7 | 0.062 | 0.637 | 0.410 | 0.262 | 0.178 | 0.125 | 0.088 | 0.062 |
| Qwen3-0.6B (2) | 3.11 | 1191 | 0.354 | 7 | 0.113 | 0.646 | 0.459 | 0.331 | 0.236 | 0.179 | 0.143 | 0.113 |
| EAGLE-3 (2) | 2.71 | 1365 | 0.408 | 7 | 0.081 | 0.592 | 0.376 | 0.244 | 0.177 | 0.133 | 0.107 | 0.081 |

#### Accepted-length histogram (% of rounds)

| drafter | k=0 | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 25.2 | 20.0 | 16.5 | 12.9 | 6.7 | 6.0 | 3.5 | 9.3 |
| DSpark (2) | 21.4 | 17.5 | 14.9 | 11.6 | 8.3 | 6.5 | 3.7 | 16.0 |
| DFlash (2) | 20.5 | 25.6 | 15.2 | 10.9 | 7.3 | 5.3 | 4.7 | 10.4 |
| PARD-1 (2) | 36.3 | 22.7 | 14.8 | 8.3 | 5.3 | 3.7 | 2.6 | 6.2 |
| Qwen3-0.6B (2) | 35.4 | 18.7 | 12.8 | 9.5 | 5.7 | 3.6 | 3.0 | 11.3 |
| EAGLE-3 (2) | 40.8 | 21.6 | 13.3 | 6.7 | 4.4 | 2.6 | 2.6 | 8.1 |

#### Phone draft stages (ms, mean)

markov = all of DSpark's host Markov head; the part of it that runs during the tree build is also inside fork, so draft e2e ≈ decode + top-k + markov (+ fork for the other drafters).

| drafter | draft e2e | p95 | decode | host top-k | markov | readback | fork | postprocess |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 27.8 | 49.1 | 21.6 | 0.91 | 0.00 | 0.01 | 0.01 | 0.26 |
| DSpark (2) | 38.8 | 43.6 | 29.4 | 0.96 | 8.48 | 0.01 | 0.01 | 0.79 |
| DFlash (2) | 30.4 | 32.7 | 29.6 | 0.82 | 0.00 | 0.01 | 0.01 | 0.94 |
| PARD-1 (2) | 21.9 | 29.0 | 21.0 | 0.89 | 0.00 | 0.01 | 0.01 | 0.25 |
| Qwen3-0.6B (2) | 84.9 | 114.6 | 82.3 | 2.60 | 0.00 | 0.01 | 0.01 | 12.91 |
| EAGLE-3 (2) | 114.5 | 126.2 | 111.8 | 2.62 | 0.00 | 0.03 | 0.01 | 0.68 |

#### Round and server (ms)

network = client wait − server end-to-end.

| drafter | round mean | round p95 | client wait | verify e2e | verify p95 | server forward | queue wait | rows / round | network median | network p95 | GPU ms / token |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 148.8 | 196.3 | 120.7 | 103.2 | 106.6 | 92.4 | 0.61 | 8.0 | 12.2 | 53.2 | 27.6 |
| DSpark (2) | 160.3 | 179.9 | 120.6 | 104.3 | 107.9 | 93.5 | 0.62 | 8.0 | 14.3 | 33.4 | 24.4 |
| DFlash (2) | 152.3 | 173.1 | 120.9 | 105.1 | 108.7 | 94.3 | 0.59 | 8.0 | 13.4 | 35.3 | 27.3 |
| PARD-1 (2) | 137.0 | 155.4 | 114.8 | 101.6 | 105.2 | 90.8 | 0.61 | 8.0 | 9.9 | 32.4 | 32.9 |
| Qwen3-0.6B (2) | 227.0 | 309.8 | 129.2 | 101.5 | 105.0 | 90.7 | 0.60 | 8.0 | 13.8 | 115.2 | 29.2 |
| EAGLE-3 (2) | 239.4 | 271.6 | 124.3 | 102.8 | 106.4 | 92.0 | 0.62 | 8.0 | 16.5 | 50.0 | 33.9 |

#### Latency (ms)

ITL p50 is 0 for every arm (tokens accepted in one round are emitted together), so the round gap is the useful per-round latency.

| drafter | TTFT p50 | TTFT p95 | TTFT mean | round gap p50 | round gap p95 | round gap p99 | ITL mean | ITL p95 | ITL p99 |
|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 137 | 255 | 160 | 139 | 197 | 333 | 44.6 | 155 | 212 |
| DSpark (2) | 159 | 500 | 234 | 158 | 180 | 200 | 41.9 | 165 | 183 |
| DFlash (2) | 160 | 488 | 235 | 150 | 173 | 196 | 44.1 | 157 | 179 |
| PARD-1 (2) | 170 | 445 | 236 | 134 | 156 | 207 | 49.6 | 144 | 167 |
| Qwen3-0.6B (2) | 262 | 527 | 323 | 214 | 310 | 350 | 73.1 | 260 | 316 |
| EAGLE-3 (2) | 176 | 654 | 292 | 235 | 272 | 321 | 88.4 | 253 | 284 |

#### Network bytes and phone memory

Steady = rounds 1+ (Σ bytes / Σ committed tokens). Round 0 also ships the prompt's feature rows (prompt features / request), which dominate the all-rounds per-token figure at 64 new tokens.

| drafter | KB up / round | KB down / round | KB down / token, steady | prompt features KB / request | KB up / token, all rounds | KB down / token, all rounds | client VmHWM MB | client VmRSS max MB |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 32.3 | 6.8 | 2.0 | 558 | 9.6 | 11.3 | 301 | 298 |
| DSpark (2) | 32.3 | 38.3 | 10.0 | 2790 | 8.4 | 55.9 | 668 | 623 |
| DFlash (2) | 32.3 | 34.6 | 10.0 | 2790 | 9.3 | 56.4 | 596 | 551 |
| PARD-1 (2) | 32.3 | 0.1 | 0.0 | 0 | 11.9 | 0.0 | 260 | 259 |
| Qwen3-0.6B (2) | 32.3 | 0.1 | 0.0 | 0 | 10.4 | 0.0 | 196 | 196 |
| EAGLE-3 (2) | 32.3 | 27.2 | 10.0 | 2790 | 11.8 | 56.4 | 611 | 564 |

#### Phone telemetry (phone_telemetry.csv, 5 s samples; per-run peak, mean over repeats)

DMA-BUF holds the HTP (NPU) buffers: weights, KV cache and compute buffers. Caps are cpufreq scaling_max_freq (thermal throttling); uncapped is 4.47 GHz prime / 3.53 GHz little.

| drafter | peak tz0 °C | peak CPU °C | peak NPU (HMX) °C | peak client DMA-BUF MB | lowest prime-core cap GHz | lowest little-core cap GHz |
|---|---|---|---|---|---|---|
| PARD-2 (2) | 48.6 | 78.4 | 55.4 | 885 | 4.09 | 3.32 |
| DSpark (2) | 52.6 | 66.1 | 60.8 | 1707 | 2.25 | 2.23 |
| DFlash (2) | 51.9 | 59.8 | 60.5 | 1707 | 2.25 | 2.23 |
| PARD-1 (2) | 50.2 | 73.6 | 55.0 | 885 | 3.18 | 2.83 |
| Qwen3-0.6B (2) | 59.0 | 73.4 | 67.5 | 885 | 1.97 | 2.01 |
| EAGLE-3 (2) | 64.2 | 68.6 | 73.8 | 1052 | 1.69 | 1.79 |

#### tok/s by category (MT-Bench sub-categories pooled; 10 requests each)

| drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 (2) | 28.3 | 22.8 | 18.4 | 19.3 | 37.2 | 23.5 |
| DSpark (2) | 26.8 | 25.5 | 19.1 | 21.8 | 40.3 | 25.4 |
| DFlash (2) | 27.0 | 23.8 | 18.0 | 19.0 | 40.7 | 24.7 |
| PARD-1 (2) | 25.0 | 16.5 | 17.2 | 17.5 | 35.2 | 21.4 |
| Qwen3-0.6B (2) | 17.7 | 16.9 | 11.3 | 11.9 | 22.1 | 13.4 |
| EAGLE-3 (2) | 13.5 | 11.9 | 10.2 | 8.7 | 21.7 | 12.1 |

#### tok/round by category

| drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 (2) | 3.48 | 2.87 | 2.72 | 2.60 | 4.98 | 3.31 |
| DSpark (2) | 3.85 | 3.51 | 2.96 | 3.14 | 5.89 | 3.56 |
| DFlash (2) | 3.43 | 3.17 | 2.67 | 2.73 | 5.73 | 3.34 |
| PARD-1 (2) | 2.96 | 2.07 | 2.31 | 2.31 | 4.43 | 2.68 |
| Qwen3-0.6B (2) | 3.26 | 3.61 | 2.73 | 2.54 | 4.51 | 3.00 |
| EAGLE-3 (2) | 2.63 | 2.56 | 2.38 | 1.98 | 4.68 | 2.65 |

### 5.2 Matched tree (budget 16, 17 rows verified)

Block drafters use depth 7 × width 8. AR drafters use 8 beams × depth 6 × width 4, so their "depth" and "P(full depth)" columns refer to depth 6 and are not directly comparable with the block drafters'.

#### Throughput

| drafter | tok/s steady | min..max | 95% CI (r1) | tok/s incl. prefill | pooled tok/s | network-normalised tok/s | emit decode tok/s |
|---|---|---|---|---|---|---|---|
| PARD-2 (2) | **29.3** | 29.2..29.3 | 27.3..31.3 | 27.5 | 27.5 | 29.7 | 29.2 |
| DSpark (2) | **28.3** | 28.2..28.4 | 26.2..30.6 | 25.7 | 26.0 | 29.3 | 28.2 |
| DFlash (3) | **27.9** | 27.3..28.5 | 25.8..30.1 | 25.4 | 25.6 | 28.8 | 27.9 |
| PARD-1 (2) | **26.7** | 26.4..27.0 | 24.4..28.6 | 24.8 | 24.9 | 26.6 | 26.7 |
| Qwen3-0.6B (2) | **16.6** | 16.5..16.6 | 15.5..17.7 | 16.1 | 15.2 | 17.6 | 16.6 |
| EAGLE-3 (2) | **15.9** | 15.8..16.1 | 14.6..17.1 | 15.1 | 14.6 | 16.4 | 15.9 |

#### Acceptance

aj = fraction of rounds whose accepted path reached depth j (survival curve); depth = deepest drafted level.

| drafter | tok/round | rounds | P(k=0) | depth | P(full depth) | a1 | a2 | a3 | a4 | a5 | a6 | a7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 4.21 | 898 | 0.050 | 7 | 0.128 | 0.950 | 0.778 | 0.561 | 0.371 | 0.252 | 0.173 | 0.128 |
| DSpark (2) | 4.64 | 825 | 0.080 | 7 | 0.224 | 0.920 | 0.771 | 0.633 | 0.459 | 0.349 | 0.281 | 0.224 |
| DFlash (3) | 4.15 | 912 | 0.089 | 7 | 0.154 | 0.911 | 0.729 | 0.527 | 0.370 | 0.275 | 0.190 | 0.154 |
| PARD-1 (2) | 3.54 | 1054 | 0.121 | 7 | 0.074 | 0.879 | 0.635 | 0.403 | 0.259 | 0.172 | 0.113 | 0.074 |
| Qwen3-0.6B (2) | 4.06 | 925 | 0.144 | 6 | 0.244 | 0.856 | 0.699 | 0.547 | 0.402 | 0.311 | 0.244 | — |
| EAGLE-3 (2) | 3.60 | 1044 | 0.193 | 6 | 0.168 | 0.807 | 0.612 | 0.458 | 0.320 | 0.234 | 0.168 | — |

#### Accepted-length histogram (% of rounds)

| drafter | k=0 | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 5.0 | 17.2 | 21.7 | 19.0 | 11.9 | 7.9 | 4.5 | 12.8 |
| DSpark (2) | 8.0 | 14.9 | 13.9 | 17.4 | 11.0 | 6.8 | 5.8 | 22.4 |
| DFlash (3) | 8.9 | 18.2 | 20.2 | 15.7 | 9.5 | 8.5 | 3.6 | 15.4 |
| PARD-1 (2) | 12.1 | 24.4 | 23.1 | 14.5 | 8.7 | 5.9 | 3.8 | 7.4 |
| Qwen3-0.6B (2) | 14.5 | 15.6 | 15.3 | 14.5 | 9.1 | 6.7 | 24.4 | 0.0 |
| EAGLE-3 (2) | 19.3 | 19.5 | 15.3 | 13.8 | 8.6 | 6.6 | 16.8 | 0.0 |

#### Phone draft stages (ms, mean)

markov = all of DSpark's host Markov head; the part of it that runs during the tree build is also inside fork, so draft e2e ≈ decode + top-k + markov (+ fork for the other drafters).

| drafter | draft e2e | p95 | decode | host top-k | markov | readback | fork | postprocess |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 29.3 | 52.6 | 21.7 | 0.93 | 0.00 | 0.01 | 0.02 | 0.28 |
| DSpark (2) | 45.8 | 55.6 | 29.3 | 0.93 | 15.49 | 0.01 | 7.70 | 0.78 |
| DFlash (3) | 30.6 | 32.8 | 29.7 | 0.78 | 0.00 | 0.01 | 0.02 | 1.04 |
| PARD-1 (2) | 22.8 | 29.3 | 21.7 | 1.03 | 0.00 | 0.01 | 0.02 | 0.27 |
| Qwen3-0.6B (2) | 116.4 | 160.4 | 110.4 | 4.95 | 0.00 | 0.01 | 0.73 | 15.16 |
| EAGLE-3 (2) | 114.8 | 134.6 | 109.3 | 4.48 | 0.00 | 0.05 | 0.59 | 1.73 |

#### Round and server (ms)

network = client wait − server end-to-end.

| drafter | round mean | round p95 | client wait | verify e2e | verify p95 | server forward | queue wait | rows / round | network median | network p95 | GPU ms / token |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 153.1 | 196.1 | 123.4 | 106.4 | 110.2 | 95.5 | 0.90 | 17.0 | 13.3 | 40.6 | 22.7 |
| DSpark (2) | 178.1 | 210.3 | 131.4 | 110.0 | 113.9 | 99.1 | 0.83 | 17.0 | 16.7 | 52.4 | 21.4 |
| DFlash (3) | 162.4 | 192.6 | 130.7 | 110.8 | 114.9 | 99.9 | 0.85 | 17.0 | 14.6 | 49.6 | 24.0 |
| PARD-1 (2) | 141.8 | 160.6 | 118.7 | 104.9 | 108.6 | 94.1 | 0.82 | 17.0 | 11.2 | 32.2 | 26.6 |
| Qwen3-0.6B (2) | 267.4 | 350.1 | 135.8 | 104.7 | 108.1 | 93.8 | 0.84 | 17.0 | 16.7 | 104.5 | 23.1 |
| EAGLE-3 (2) | 246.3 | 282.2 | 129.7 | 108.2 | 117.6 | 97.1 | 0.84 | 17.0 | 17.2 | 46.5 | 27.0 |

#### Latency (ms)

ITL p50 is 0 for every arm (tokens accepted in one round are emitted together), so the round gap is the useful per-round latency.

| drafter | TTFT p50 | TTFT p95 | TTFT mean | round gap p50 | round gap p95 | round gap p99 | ITL mean | ITL p95 | ITL p99 |
|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 133 | 246 | 156 | 144 | 196 | 350 | 36.4 | 152 | 210 |
| DSpark (2) | 160 | 526 | 245 | 174 | 210 | 254 | 38.5 | 183 | 211 |
| DFlash (3) | 160 | 451 | 239 | 157 | 193 | 256 | 39.1 | 165 | 197 |
| PARD-1 (2) | 176 | 396 | 236 | 140 | 161 | 185 | 40.2 | 148 | 167 |
| Qwen3-0.6B (2) | 285 | 630 | 365 | 255 | 350 | 415 | 65.9 | 304 | 358 |
| EAGLE-3 (2) | 169 | 573 | 275 | 243 | 282 | 354 | 68.5 | 259 | 293 |

#### Network bytes and phone memory

Steady = rounds 1+ (Σ bytes / Σ committed tokens). Round 0 also ships the prompt's feature rows (prompt features / request), which dominate the all-rounds per-token figure at 64 new tokens.

| drafter | KB up / round | KB down / round | KB down / token, steady | prompt features KB / request | KB up / token, all rounds | KB down / token, all rounds | client VmHWM MB | client VmRSS max MB |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (2) | 68.5 | 8.6 | 2.0 | 558 | 16.1 | 11.3 | 291 | 287 |
| DSpark (2) | 68.5 | 46.5 | 10.0 | 2790 | 14.6 | 56.3 | 678 | 632 |
| DFlash (3) | 68.5 | 41.7 | 10.0 | 2790 | 16.3 | 56.4 | 592 | 546 |
| PARD-1 (2) | 68.5 | 0.1 | 0.0 | 0 | 19.9 | 0.0 | 250 | 249 |
| Qwen3-0.6B (2) | 68.5 | 0.1 | 0.0 | 0 | 16.9 | 0.0 | 538 | 538 |
| EAGLE-3 (2) | 68.5 | 36.1 | 10.0 | 2790 | 18.8 | 56.4 | 704 | 659 |

#### Phone telemetry (phone_telemetry.csv, 5 s samples; per-run peak, mean over repeats)

DMA-BUF holds the HTP (NPU) buffers: weights, KV cache and compute buffers. Caps are cpufreq scaling_max_freq (thermal throttling); uncapped is 4.47 GHz prime / 3.53 GHz little.

| drafter | peak tz0 °C | peak CPU °C | peak NPU (HMX) °C | peak client DMA-BUF MB | lowest prime-core cap GHz | lowest little-core cap GHz |
|---|---|---|---|---|---|---|
| PARD-2 (2) | 48.8 | 83.6 | 54.4 | 885 | 4.38 | 3.53 |
| DSpark (2) | 51.9 | 66.1 | 59.4 | 1707 | 2.25 | 2.23 |
| DFlash (3) | 51.9 | 66.6 | 57.9 | 1707 | 2.86 | 2.59 |
| PARD-1 (2) | 48.6 | 66.5 | 52.2 | 885 | 3.08 | 2.91 |
| Qwen3-0.6B (2) | 60.5 | 67.5 | 68.4 | 885 | 1.82 | 1.89 |
| EAGLE-3 (2) | 64.8 | 72.1 | 91.8 | 1094 | 1.69 | 1.79 |

#### tok/s by category (MT-Bench sub-categories pooled; 10 requests each)

| drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 (2) | 32.8 | 26.1 | 22.0 | 25.4 | 41.9 | 27.5 |
| DSpark (2) | 31.3 | 25.8 | 21.8 | 23.0 | 41.5 | 26.2 |
| DFlash (3) | 29.6 | 26.6 | 20.5 | 22.1 | 41.2 | 27.6 |
| PARD-1 (2) | 30.8 | 21.1 | 21.6 | 21.8 | 39.3 | 25.6 |
| Qwen3-0.6B (2) | 18.0 | 17.7 | 12.6 | 13.8 | 22.5 | 14.9 |
| EAGLE-3 (2) | 16.3 | 14.3 | 13.0 | 12.4 | 24.8 | 15.0 |

#### tok/round by category

| drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 (2) | 4.24 | 3.43 | 3.41 | 3.49 | 5.71 | 4.08 |
| DSpark (2) | 4.91 | 3.90 | 3.65 | 3.68 | 6.60 | 4.31 |
| DFlash (3) | 4.22 | 3.59 | 3.17 | 3.41 | 6.09 | 4.01 |
| PARD-1 (2) | 3.84 | 2.66 | 3.03 | 2.97 | 5.23 | 3.34 |
| Qwen3-0.6B (2) | 4.34 | 4.11 | 3.57 | 3.37 | 5.41 | 4.13 |
| EAGLE-3 (2) | 3.47 | 2.98 | 3.15 | 2.79 | 5.62 | 3.41 |

### 5.3 Own-best tree (budget 32, 33 rows verified)

#### Throughput

| drafter | tok/s steady | min..max | 95% CI (r1) | tok/s incl. prefill | pooled tok/s | network-normalised tok/s | emit decode tok/s |
|---|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | **30.0** | 29.9..30.1 | 27.9..32.2 | 28.0 | 28.0 | 30.9 | 29.9 |
| DSpark (l7w8b32, 2) | **28.2** | 28.1..28.3 | 26.2..30.2 | 25.9 | 26.4 | 29.0 | 28.2 |
| DFlash (l7w8b32, 2) | **28.8** | 28.7..28.8 | 26.6..31.1 | 26.1 | 26.4 | 29.4 | 28.7 |
| PARD-1 (l8w8b32, 2) | **26.7** | 25.9..27.4 | 23.5..28.6 | 24.7 | 24.4 | 27.7 | 26.7 |
| Qwen3-0.6B (n8l6w8b32, 2) | **18.5** | 18.4..18.5 | 17.2..19.7 | 17.8 | 16.9 | 19.7 | 18.5 |
| EAGLE-3 (n8l6w8b32, 2) | **17.6** | 17.5..17.6 | 16.3..19.0 | 16.5 | 16.3 | 18.2 | 17.5 |

#### Acceptance

aj = fraction of rounds whose accepted path reached depth j (survival curve); depth = deepest drafted level.

| drafter | tok/round | rounds | P(k=0) | depth | P(full depth) | a1 | a2 | a3 | a4 | a5 | a6 | a7 | a8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 4.58 | 833 | 0.045 | 8 | 0.106 | 0.955 | 0.832 | 0.618 | 0.426 | 0.290 | 0.203 | 0.149 | 0.106 |
| DSpark (l7w8b32, 2) | 5.02 | 764 | 0.067 | 7 | 0.270 | 0.933 | 0.832 | 0.702 | 0.534 | 0.419 | 0.327 | 0.270 | — |
| DFlash (l7w8b32, 2) | 4.37 | 872 | 0.071 | 7 | 0.177 | 0.929 | 0.765 | 0.576 | 0.406 | 0.300 | 0.220 | 0.177 | — |
| PARD-1 (l8w8b32, 2) | 3.81 | 979 | 0.110 | 8 | 0.058 | 0.890 | 0.684 | 0.469 | 0.295 | 0.205 | 0.128 | 0.084 | 0.058 |
| Qwen3-0.6B (n8l6w8b32, 2) | 4.53 | 839 | 0.092 | 6 | 0.313 | 0.908 | 0.775 | 0.633 | 0.498 | 0.399 | 0.313 | — | — |
| EAGLE-3 (n8l6w8b32, 2) | 3.92 | 969 | 0.147 | 6 | 0.207 | 0.853 | 0.660 | 0.525 | 0.391 | 0.286 | 0.207 | — | — |

#### Accepted-length histogram (% of rounds)

| drafter | k=0 | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 | k=8 |
|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 4.5 | 12.3 | 21.3 | 19.3 | 13.6 | 8.7 | 5.4 | 4.3 | 10.6 |
| DSpark (l7w8b32, 2) | 6.7 | 10.1 | 13.1 | 16.8 | 11.5 | 9.2 | 5.7 | 27.0 | 0.0 |
| DFlash (l7w8b32, 2) | 7.1 | 16.4 | 18.8 | 17.0 | 10.6 | 8.0 | 4.3 | 17.7 | 0.0 |
| PARD-1 (l8w8b32, 2) | 11.0 | 20.6 | 21.5 | 17.4 | 9.0 | 7.6 | 4.5 | 2.6 | 5.8 |
| Qwen3-0.6B (n8l6w8b32, 2) | 9.2 | 13.2 | 14.2 | 13.5 | 9.9 | 8.6 | 31.3 | 0.0 | 0.0 |
| EAGLE-3 (n8l6w8b32, 2) | 14.7 | 19.3 | 13.5 | 13.4 | 10.5 | 7.9 | 20.7 | 0.0 | 0.0 |

#### Phone draft stages (ms, mean)

markov = all of DSpark's host Markov head; the part of it that runs during the tree build is also inside fork, so draft e2e ≈ decode + top-k + markov (+ fork for the other drafters).

| drafter | draft e2e | p95 | decode | host top-k | markov | readback | fork | postprocess |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 30.2 | 54.8 | 22.0 | 0.96 | 0.00 | 0.01 | 0.03 | 0.32 |
| DSpark (l7w8b32, 2) | 54.2 | 67.9 | 29.5 | 0.90 | 23.68 | 0.01 | 16.20 | 0.79 |
| DFlash (l7w8b32, 2) | 30.6 | 33.0 | 29.7 | 0.85 | 0.00 | 0.01 | 0.03 | 0.99 |
| PARD-1 (l8w8b32, 2) | 23.2 | 30.2 | 22.1 | 1.05 | 0.00 | 0.01 | 0.03 | 0.32 |
| Qwen3-0.6B (n8l6w8b32, 2) | 110.4 | 143.8 | 102.1 | 6.14 | 0.00 | 0.01 | 1.69 | 16.78 |
| EAGLE-3 (n8l6w8b32, 2) | 104.0 | 120.0 | 96.3 | 5.75 | 0.00 | 0.06 | 1.29 | 2.88 |

#### Round and server (ms)

network = client wait − server end-to-end.

| drafter | round mean | round p95 | client wait | verify e2e | verify p95 | server forward | queue wait | rows / round | network median | network p95 | GPU ms / token |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 163.6 | 230.2 | 132.9 | 112.0 | 118.1 | 101.1 | 1.05 | 33.0 | 15.1 | 53.8 | 22.1 |
| DSpark (l7w8b32, 2) | 190.3 | 216.9 | 135.1 | 115.6 | 119.5 | 104.6 | 1.06 | 33.0 | 16.4 | 38.9 | 20.9 |
| DFlash (l7w8b32, 2) | 165.4 | 190.1 | 133.6 | 115.3 | 119.5 | 104.3 | 1.03 | 33.0 | 15.0 | 40.4 | 23.8 |
| PARD-1 (l8w8b32, 2) | 156.2 | 199.7 | 132.5 | 110.2 | 115.2 | 99.3 | 1.01 | 33.0 | 13.8 | 65.8 | 26.1 |
| Qwen3-0.6B (n8l6w8b32, 2) | 268.1 | 342.1 | 140.8 | 109.7 | 113.2 | 98.8 | 1.06 | 33.0 | 17.2 | 99.7 | 21.8 |
| EAGLE-3 (n8l6w8b32, 2) | 240.1 | 272.6 | 133.1 | 111.1 | 115.3 | 100.2 | 1.10 | 33.0 | 17.9 | 46.3 | 25.6 |

#### Latency (ms)

ITL p50 is 0 for every arm (tokens accepted in one round are emitted together), so the round gap is the useful per-round latency.

| drafter | TTFT p50 | TTFT p95 | TTFT mean | round gap p50 | round gap p95 | round gap p99 | ITL mean | ITL p95 | ITL p99 |
|---|---|---|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 136 | 236 | 155 | 152 | 230 | 370 | 35.8 | 163 | 235 |
| DSpark (l7w8b32, 2) | 153 | 424 | 220 | 188 | 217 | 248 | 38.0 | 196 | 217 |
| DFlash (l7w8b32, 2) | 157 | 451 | 231 | 162 | 191 | 227 | 37.9 | 168 | 195 |
| PARD-1 (l8w8b32, 2) | 196 | 476 | 258 | 148 | 200 | 253 | 41.0 | 165 | 209 |
| Qwen3-0.6B (n8l6w8b32, 2) | 299 | 631 | 373 | 254 | 342 | 416 | 59.3 | 292 | 348 |
| EAGLE-3 (n8l6w8b32, 2) | 163 | 579 | 276 | 236 | 273 | 331 | 61.3 | 250 | 280 |

#### Network bytes and phone memory

Steady = rounds 1+ (Σ bytes / Σ committed tokens). Round 0 also ships the prompt's feature rows (prompt features / request), which dominate the all-rounds per-token figure at 64 new tokens.

| drafter | KB up / round | KB down / round | KB down / token, steady | prompt features KB / request | KB up / token, all rounds | KB down / token, all rounds | client VmHWM MB | client VmRSS max MB |
|---|---|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 133.0 | 9.4 | 2.1 | 558 | 28.7 | 11.3 | 289 | 286 |
| DSpark (l7w8b32, 2) | 133.0 | 50.4 | 10.1 | 2790 | 26.2 | 56.5 | 691 | 645 |
| DFlash (l7w8b32, 2) | 133.0 | 44.0 | 10.1 | 2790 | 30.0 | 56.2 | 587 | 541 |
| PARD-1 (l8w8b32, 2) | 133.0 | 0.3 | 0.1 | 0 | 35.7 | 0.1 | 243 | 242 |
| Qwen3-0.6B (n8l6w8b32, 2) | 133.0 | 0.3 | 0.1 | 0 | 29.4 | 0.1 | 457 | 456 |
| EAGLE-3 (n8l6w8b32, 2) | 133.0 | 39.5 | 10.1 | 2790 | 33.5 | 56.1 | 763 | 717 |

#### Phone telemetry (phone_telemetry.csv, 5 s samples; per-run peak, mean over repeats)

DMA-BUF holds the HTP (NPU) buffers: weights, KV cache and compute buffers. Caps are cpufreq scaling_max_freq (thermal throttling); uncapped is 4.47 GHz prime / 3.53 GHz little.

| drafter | peak tz0 °C | peak CPU °C | peak NPU (HMX) °C | peak client DMA-BUF MB | lowest prime-core cap GHz | lowest little-core cap GHz |
|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 48.6 | 79.3 | 50.4 | 885 | 4.38 | 3.53 |
| DSpark (l7w8b32, 2) | 51.5 | 61.1 | 58.2 | 1707 | 2.25 | 2.23 |
| DFlash (l7w8b32, 2) | 52.7 | 58.1 | 59.5 | 1707 | 2.25 | 2.23 |
| PARD-1 (l8w8b32, 2) | 50.5 | 59.0 | 53.4 | 885 | 3.29 | 2.91 |
| Qwen3-0.6B (n8l6w8b32, 2) | 57.5 | 64.3 | 65.1 | 885 | 2.10 | 2.11 |
| EAGLE-3 (n8l6w8b32, 2) | 62.8 | 66.1 | 77.4 | 1052 | 1.82 | 1.89 |

#### tok/s by category (MT-Bench sub-categories pooled; 10 requests each)

| drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 33.5 | 26.3 | 23.7 | 26.2 | 43.5 | 26.6 |
| DSpark (l7w8b32, 2) | 31.8 | 25.8 | 21.4 | 23.9 | 39.7 | 26.7 |
| DFlash (l7w8b32, 2) | 31.0 | 28.0 | 21.1 | 23.3 | 41.7 | 27.5 |
| PARD-1 (l8w8b32, 2) | 30.5 | 20.5 | 20.6 | 21.3 | 40.9 | 26.4 |
| Qwen3-0.6B (n8l6w8b32, 2) | 19.5 | 20.1 | 14.0 | 15.3 | 25.2 | 16.8 |
| EAGLE-3 (n8l6w8b32, 2) | 18.7 | 14.9 | 14.3 | 13.8 | 27.4 | 16.3 |

#### tok/round by category

| drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 (l8w8b32, 2) | 4.58 | 3.62 | 3.79 | 3.76 | 6.15 | 4.33 |
| DSpark (l7w8b32, 2) | 5.30 | 4.11 | 3.85 | 4.18 | 6.85 | 4.56 |
| DFlash (l7w8b32, 2) | 4.48 | 3.79 | 3.32 | 3.64 | 6.25 | 4.15 |
| PARD-1 (l8w8b32, 2) | 4.12 | 2.81 | 3.14 | 3.20 | 5.78 | 3.75 |
| Qwen3-0.6B (n8l6w8b32, 2) | 4.83 | 4.64 | 3.90 | 3.84 | 6.12 | 4.56 |
| EAGLE-3 (n8l6w8b32, 2) | 3.96 | 3.05 | 3.34 | 3.04 | 5.92 | 3.75 |

### 5.4 Across shapes

| Drafter | tok/s chain → tree16 → own | tok/round chain → tree16 → own | draft ms chain → tree16 → own | verify ms chain → tree16 → own |
|---|---|---|---|---|
| PARD-2 | 24.9 → 29.3 → 30.0 | 3.34 → 4.21 → 4.58 | 27.8 → 29.3 → 30.2 | 103.2 → 106.4 → 112.0 |
| DFlash | 25.5 → 27.9 → 28.8 | 3.45 → 4.15 → 4.37 | 30.4 → 30.6 → 30.6 | 105.1 → 110.8 → 115.3 |
| DSpark | 26.5 → 28.3 → 28.2 | 3.83 → 4.64 → 5.02 | 38.8 → 45.8 → 54.2 | 104.3 → 110.0 → 115.6 |
| PARD-1 | 22.1 → 26.7 → 26.7 | 2.76 → 3.54 → 3.81 | 21.9 → 22.8 → 23.2 | 101.6 → 104.9 → 110.2 |
| Qwen3-0.6B | 15.6 → 16.6 → 18.5 | 3.11 → 4.06 → 4.53 | 84.9 → 116.4 → 110.4 | 101.5 → 104.7 → 109.7 |
| EAGLE-3 | 13.0 → 15.9 → 17.6 | 2.71 → 3.60 → 3.92 | 114.5 → 114.8 → 104.0 | 102.8 → 108.2 → 111.1 |

**What the shape comparison shows:**

- **PARD-2 gains the most from a tree.**
  - P(k=0) falls from 0.25 (chain) to 0.05 (tree16) and 0.045 (own-best), while its draft time barely changes.
  - Its draft has a latency tail: p95 is 49–55 ms against a 28–30 ms mean.
  - About 6–8 ms of its draft time is spent outside the NPU decode: total 27.8–30.2 ms vs decode 21.6–22.0 ms. This is consistent with building the input embeddings on the host.
- **DSpark's Markov head grows with the tree:** 8.5 ms (chain), 15.5 ms (tree16), 23.7 ms (own-best). That is why its own-best tree is no faster than its matched tree, even though it has the highest acceptance in every shape.
- **Verify time grows with rows:** 101–105 ms (8 rows), 105–111 ms (17), 110–116 ms (33). At one shape, drafters differ by at most 6 ms. DFlash and DSpark sit at the top of each range because the server also runs their encoder.
- **Upload size is set by the row count, not the drafter:** 32.3 / 68.5 / 133 KB per round.
- **Download is target features for the feature drafters.**
  - **After round 0:** 10 KB per generated token for DFlash, DSpark and EAGLE-3, 2 KB for PARD-2, about 0 for PARD-1 and Qwen3-0.6B.
  - **Round 0:** feature drafters also download the prompt's features, 2.8 MB per request (PARD-2: 0.56 MB).
  - **All rounds counted:** about 56 KB/token for DFlash, DSpark and EAGLE-3 and 11.3 KB/token for PARD-2, at 64 new tokens.
- **Phone memory:**
  - Qwen3-0.6B's resident memory (VmHWM) grows from 196 MB (chain) to 538 MB (tree16) and 457 MB (own-best), because each beam keeps its own KV sequence.
  - NPU DMA-BUF is about 885 MB for the 0.6B-shaped drafters (Qwen3-0.6B, PARD-1, PARD-2), about 1.05 GB for EAGLE-3, and about 1.7 GB for DFlash/DSpark.
- **By category:**
  - Every drafter is fastest on math_reasoning (35–44 tok/s for block drafters). Most are slowest on summarization or qa, and PARD-1 on translation.
  - PARD-1's weak spot is translation: 2.07–2.81 tok/round vs 3.2–4.1 for DFlash/DSpark.
  - Qwen3-0.6B accepts unusually well on translation (3.61 / 4.11 / 4.64), but it is too slow per round for this to matter.

---

## 6. Validity checks

### 6.1 Repeatability

- **Identical rounds:** in every arm, all repeats produced **identical round counts and committed-token counts**, so acceptance is deterministic at temperature 0 (e.g. DFlash tree16: 912 rounds and 3600 tokens in all three repeats).
- **tok/s spread:** the spread between repeats is at most 1.5 tok/s (PARD-1 own-best 25.9 vs 27.5) and usually ≤ 0.7. It comes from timing (WiFi, thermal state), not acceptance.

### 6.2 Node and binary

- **Node.** PARD-2 repeat 1 (spark2) and repeat 2 (spark4) have identical rounds:
  - verify 103.5 vs 102.8 ms (chain), 106.5 vs 106.2 (tree16), 113.3 vs 110.8 (own-best)
  - tok/s within 0.7
- **Binary.** Repeats on the newer binary (`8f6353b`) reproduce repeats on the older one (`b300fed`) round for round:
  - PARD-1 chain/tree16, Qwen3-0.6B chain/tree16 and EAGLE-3 chain/tree16 have repeat 1 on the old binary and repeat 2 on the new
  - DFlash tree16 repeats 1–2 on the old binary vs repeat 3 on the new: 27.97 / 27.32 / 28.45 tok/s, all 912 rounds

### 6.3 Oracle vs live acceptance (tok/round)

Oracle = host replay against the recorded target outputs (§2.6).

| Drafter | chain7 oracle → live | tree16 oracle → live | own-best oracle → live |
|---|---|---|---|
| Qwen3-0.6B | 3.11 → 3.11 | 4.07 → 4.06 | 4.51 → 4.53 |
| EAGLE-3 | 2.80 → 2.71 | 3.61 → 3.60 | 4.00 → 3.92 |
| DFlash | 3.42 → 3.45 | 4.15 → 4.15 | 4.42 → 4.37 |
| DSpark | 3.86 → 3.83 | 4.68 → 4.64 | 5.13 → 5.02 |
| PARD-1 | 2.78 → 2.76 | (not scored at depth 7) → 3.54 | 3.81 → 3.81 |
| PARD-2 | (no Q4_0 oracle) → 3.34 | (no Q4_0 oracle) → 4.21 | 4.65 → 4.58 |

**How close they are:**
- 11 of the 15 scored pairs agree within ±0.05 tok/round.
- The other four: DSpark own-best (−0.11), EAGLE-3 chain (−0.09), EAGLE-3 own-best (−0.08), PARD-2 own-best (−0.07).
- Live is never more than 0.03 above the oracle.

**Likely cause of the gaps:** the live target outputs differ from the recorded trace the oracle uses; see §6.4.

### 6.4 Output agreement

Speculative decoding at temperature 0 should reproduce the target's greedy output exactly. This check compares the first 64 output tokens of every arm (repeat 1) against three reference arms.

| arm | vs dflash-chain7: identical / median first diff | vs pard1-chain7: identical / median first diff | vs dflash-tree16: identical / median first diff |
|---|---|---|---|
| dflash-chain7 | 60/60 | 53/60 / tok 35 | 32/60 / tok 38 |
| dflash-own-l7w8b32 | 33/60 / tok 37 | 31/60 / tok 30 | 54/60 / tok 45 |
| dflash-tree16 | 32/60 / tok 38 | 30/60 / tok 34 | 60/60 |
| dspark-chain7 | 60/60 | 53/60 / tok 35 | 32/60 / tok 38 |
| dspark-own-l7w8b32 | 28/60 / tok 38 | 27/60 / tok 35 | 44/60 / tok 44 |
| dspark-tree16 | 28/60 / tok 39 | 28/60 / tok 34 | 47/60 / tok 47 |
| eagle3-chain7 | 60/60 | 53/60 / tok 35 | 32/60 / tok 38 |
| eagle3-own-n8l6w8b32 | 30/60 / tok 30 | 27/60 / tok 31 | 39/60 / tok 43 |
| eagle3-tree16 | 28/60 / tok 34 | 27/60 / tok 31 | 42/60 / tok 45 |
| pard1-chain7 | 53/60 / tok 35 | 60/60 | 30/60 / tok 34 |
| pard1-own-l8w8b32 | 31/60 / tok 32 | 31/60 / tok 35 | 39/60 / tok 45 |
| pard1-tree16 | 31/60 / tok 21 | 28/60 / tok 34 | 36/60 / tok 39 |
| pard2-chain7 | 60/60 | 53/60 / tok 35 | 32/60 / tok 38 |
| pard2-own-l8w8b32 | 30/60 / tok 30 | 28/60 / tok 26 | 47/60 / tok 36 |
| pard2-tree16 | 30/60 / tok 34 | 30/60 / tok 28 | 48/60 / tok 40 |
| qwen3-0.6b-chain7 | 53/60 / tok 35 | 60/60 | 30/60 / tok 34 |
| qwen3-0.6b-own-n8l6w8b32 | 28/60 / tok 39 | 28/60 / tok 42 | 33/60 / tok 38 |
| qwen3-0.6b-tree16 | 29/60 / tok 26 | 29/60 / tok 26 | 40/60 / tok 42 |

**Results by group:**
- **All four feature-drafter chains** (DFlash, DSpark, EAGLE-3, PARD-2) produce identical outputs on all 60 requests.
- **The two plain-server chains** (PARD-1, Qwen3-0.6B) are identical to each other, and match the feature-drafter chains on 53/60 requests.
- **Tree arms match the chain outputs on only 28–33 of 60 requests.** They also differ from each other: 33–54/60 agree with the DFlash tree16 output. The first differing token is at a median position of about 21–47.

**Not a drafter bug, as far as can be checked:**
- **The divergences are near-ties.** The texts stay fluent and differ by one plausible word choice, after which they continue differently. Examples: "a severe hazing incident" vs "a hazing incident"; "first published in 1912" vs "first recorded in 1912".
- **Divergence depends on how many rows the server verifies.** 8-row chains agree with each other, and trees (17 or 33 rows) diverge. The plain and feature-tap servers differ slightly even at 8 rows.
- **This matches the earlier measurement** of a "budget-dependent" 4.6–7.1% divergence of the FP8 verifier (`specedge-server-trace-generation`). The FP8 target's logits shift slightly with the batch's row count and contents (kernel choice, tiling and accumulation order), which flips near-tied argmaxes.
- **Every repeat of an arm reproduced its own output exactly.**

**Consequences:**
- The system is lossless only up to the FP8 verifier's numerics.
- Arms are measured on slightly different continuations of the same prompts.
- Acceptance is compared on matched prompts but not on identical outputs. The effect on tok/round should be small (§6.3 shows ≤ 0.11), but it is not zero.
- It has **not** been proved that the tree verify path has no bug. An exact check would compare tree-arm outputs against a target-only greedy run that uses the same row count.

### 6.5 Thermal state

- **Every run started at tz0 ≤ 36.5 °C.** The gate waited 0–440 s.
- **During runs:**
  - tz0 peaked at 47–54 °C for block drafters and 57–65 °C for the AR drafters. The AR drafters run longer and keep the NPU busier; EAGLE-3's NPU reached 91–93 °C in tree16.
  - Thermal throttling lowered the prime-core frequency cap to 2.25 GHz in every DFlash/DSpark run except DFlash tree16 repeat 3, and to 1.69–2.25 GHz in the EAGLE-3/Qwen3-0.6B runs, against 4.47 GHz uncapped. PARD-1 runs went down to 2.6–3.5 GHz, and PARD-2 runs stayed close to uncapped (4.09–4.47 GHz).
- **The caps don't show up in the results.** The draft runs on the NPU, and repeats with different cap levels give the same tok/s. For example, DFlash tree16 repeat 3 hit a lowest cap of 4.09 GHz against 2.25 GHz in repeats 1–2, and its tok/s is within the repeat spread. Host-side parts (top-k, Markov head, AR post-processing) can still be slowed by the caps.

---

## 7. Limitations

- **TTFT uses cached prefill** (`cache_prefill: true`), so it excludes the server's prompt compute.
  - It measures the phone's round-0 work plus one verify.
  - The planned cold-prefill side pass (`configs/server/*-nocache.yaml`, arms `ttft-<drafter>`) was not run.
- **Single client, batch size 1.** These results say nothing about server throughput under concurrency.
- **64 new tokens per request.**
  - Longer generations would weight steady-state speed more and TTFT less.
  - They would also run the phone hotter: the AR drafters already reach 57–65 °C at 64 tokens.
- **No energy measurement**, by decision on 10-15.
- **Memory is reported two ways:**
  - **VmHWM** is the CPU-side resident set.
  - **DMA-BUF** holds the NPU buffers, sampled every 30 s.
  - Neither is the full system cost, e.g. the HTP's own reservations.
- **The own-best shapes were chosen with a modelled round time** (§2.6), not by live search.
  - Live results agree with the oracle on acceptance.
  - Shapes outside the modelled sweep were not tried, e.g. DSpark with fewer Markov rows, or budget 24.
- **Output divergence between arms** (§6.4): lossless only up to FP8 verifier numerics.
- **One phone and one WiFi network.** Network time had a median of 10–18 ms with p95 up to 115 ms (Qwen3-0.6B chain); the network-normalised tok/s removes most of this.

---

## 8. Reproducing

```bash
E=/Users/vafbaguio/kaist/ina/drafter-evaluation
cd $E
python3 harness/make_arms.py                         # configs/client/*.yaml, configs/server/*.yaml, configs/schedule.json
bash harness/push_device.sh --fast                   # binary + models + configs to the phone
bash harness/sync_server.sh spark4 --yes             # server worktree to the node
bash harness/run_eval.sh --node spark4 --path direct --repeat 2 --yes --resume --start-servers \
     --only 'dflash-*'                               # one stage; add --binary client-htp-eval-pard2 for PARD-2
python3 analysis/eval_report.py --compare results/2026-10-1*/*-r[0-9] --out results/final/per-run
python3 analysis/shape_metrics.py results/final/per-run chain7 > results/final/chain7-all-metrics.md
python3 report/build_report.py                       # rebuilds this file
```

**Rule for the shared nodes:** start servers only on a node whose `nvidia-smi` shows no other users. The harness enforces this before every arm.
