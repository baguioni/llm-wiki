---
type: Paper
title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
description: Framework that builds offline web training environments by HTTP-level caching of real sites and LLM-based synthesis of new sites, used to train screenshot-only web agents with SFT followed by RL.
tags: [web-agents, visual-web-agents, training-environments, synthetic-data, reinforcement-learning, test-time-scaling, ai899]
collections: [ai899]
authors: [Oğuzhan Fatih Kar, Roman Bachmann, Yuanzheng Gong, Anders Boesen Lindbo Larsen, Afshin Dehghan]
year: 2026
doi: 10.48550/arXiv.2605.06761
arxiv: "2605.06761"
arxiv_version: 2605.06761v1
sources:
  - id: karWeblicaScalableReproducible2026
    resource: zotero://select/items/@karWeblicaScalableReproducible2026
    title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
---

# Weblica: Scalable and Reproducible Training Environments for Visual Web Agents

Text source: arXiv HTML, version `2605.06761v1`.

## Summary

Training data for visual web agents is hard to scale. Offline trajectories for supervised fine-tuning lack interaction, simulated environments cover only a handful of manually defined domains, and training on live websites is brittle because of timeouts and bot detection and is hard to reproduce.[^karWeblicaScalableReproducible2026]

Weblica (Web Replica) is a framework for constructing reproducible and scalable web environments. It has two mechanisms: HTTP-level caching that records and replays real website interactions, and an LLM-based synthesis pipeline that generates interactive websites grounded in real websites and core web navigation skills. All environments are served locally.[^karWeblicaScalableReproducible2026] The authors fine-tune Qwen3-VL models, which act on screenshots only, with no set-of-marks annotations or DOM access.[^karWeblicaScalableReproducible2026] The 8B model reaches 39.2% pass@1 on Online-Mind2Web with only 30 steps, which the paper says outperforms open-weight models that use 3× more steps, and it improves further with more test-time compute.[^karWeblicaScalableReproducible2026]

## Contributions

- An HTTP-level caching system with automated, site-specific rule generation that enables deterministic replay of real websites under complete network isolation (Weblica-Cache).[^karWeblicaScalableReproducible2026]
- An LLM-based environment synthesis pipeline in which a coding agent generates self-contained websites and tasks, parameterized by navigation capability, website category, and visual style (Weblica-Synth).[^karWeblicaScalableReproducible2026]
- RL training scaled to thousands of environments and tasks, with a study of training stages, environment composition, model size, and test-time compute.[^karWeblicaScalableReproducible2026]

## Method

### Agent formulation

- Web navigation is a POMDP $(\mathcal{S},\mathcal{A},\mathcal{O},T,R)$, with the transition function implemented via Playwright.[^karWeblicaScalableReproducible2026]
- **Observation.** A browser screenshot rendered at 1280×720 pixels and the current URL.[^karWeblicaScalableReproducible2026]
- **Actions.** `click(x, y)`, `hover(x, y)`, `type(text, [x, y], [enter])`, `press(key)`, `scroll(direction, [amount])`, `go_back()`, `go_forward()`, `wait()`, and `stop(response)`. Coordinate-based actions take pixel positions.[^karWeblicaScalableReproducible2026]
- **Policy.** A vision-language model in a [ReAct](../methods/react.md)-style loop: it writes a reasoning trace, then selects an action, and both are appended to the history. The base model is Qwen3-VL-Instruct.[^karWeblicaScalableReproducible2026]

### HTTP-level caching (Weblica-Cache)

- **Recording and replay.** All HTTP traffic is captured with Playwright and responses are indexed by normalized request signatures. A rule-based normalization system filters volatile parameters (timestamps, session tokens) from URLs, headers, and POST bodies, with domain-specific rules and a multi-level fallback for progressive matching.[^karWeblicaScalableReproducible2026]
- **Automated rule generation.** A Qwen3-VL-32B-Instruct agent performs a browsing session that is recorded without filtering. A playback reveals cache misses, which are fuzzy-matched against the recording to find the parameters that changed. These reports are used to synthesize site-specific caching rules and synthetic responses for non-essential endpoints such as analytics. Rules are validated by playback under complete network isolation, and only sessions where the agent completes the task under cached conditions are kept.[^karWeblicaScalableReproducible2026]
- **Tasks.** The task pool is the InstaV3 dataset, which provides tasks across 146K websites. After matching tasks to cached environments and verifying solvability, 15.6K cached environments and tasks are retained.[^karWeblicaScalableReproducible2026]

### LLM-based environment synthesis (Weblica-Synth)

- **Capability extraction.** Trajectories of Qwen3-VL-32B-Instruct on the Online-Mind2Web tasks are analyzed with GPT-5.2, giving 19,721 fine-grained capabilities, which are aggregated into 144 higher-level capability groups.[^karWeblicaScalableReproducible2026]
- **Website generation.** Claude Code (Opus 4.5) writes static HTML, JavaScript, and CSS with no external framework dependencies. Each generation is parameterized by a target capability group, a website category sampled from a pool of 1,160 domains, and a visual style sampled from 961 options. Without sampled categories and styles, generated websites converge to a narrow visual style and content.[^karWeblicaScalableReproducible2026]
- **Tasks and state.** At least 10 tasks of varying difficulty are generated per website. The websites have no backend and use JavaScript's localStorage to save values during a session.[^karWeblicaScalableReproducible2026]
- **Assets and validation.** Z-Image-Turbo generates visual assets. Claude Code self-validates each site by taking screenshots via Playwright and iterating until the website and tasks are functional and there are no CSS issues.[^karWeblicaScalableReproducible2026]
- **Environment server.** Local hosting and Playwright's animation skipping reduce time per action from ∼1.5s to 50-150ms, which gives an overall 30-40% speed improvement in end-to-end RL training.[^karWeblicaScalableReproducible2026]
- **Size.** 310 sites cover the higher-level capability groups and 2500 sites target the fine-grained capabilities sorted by frequency. 2560 environments covering 44,227 tasks are reserved for training (Weblica-train) and 250 sites covering 500 tasks for validation (Weblica-val).[^karWeblicaScalableReproducible2026]

### Training

- **Reward.** An [LLM-as-judge](../methods/llm-as-a-judge.md) reward: GPT-4o receives the task description, the agent's action sequence, and the resulting screenshots and decides whether the task was completed. The judge has 88% agreement with human evaluations. Samples labeled "website failure" are discarded from the training batch.[^karWeblicaScalableReproducible2026]
- **SFT data.** Trajectories from a Qwen3-VL-32B-Instruct agent on InstaV3 queries, filtered by the LLM judge to keep successful completions, with multiple rollouts per query: 51.7K SFT trajectories in total.[^karWeblicaScalableReproducible2026]
- **SFT warm-start.** The base VLM is fine-tuned on the verified trajectories before RL.[^karWeblicaScalableReproducible2026]
- **RL.** Dr. GRPO, a variant of [GRPO](../methods/grpo.md), with the LLM-as-judge reward. Rollouts are oversampled and filtered to keep groups with mixed success signals, similar to DAPO, and fallback mechanisms handle errors or timeouts.[^karWeblicaScalableReproducible2026]
- **RL data.** 10K tasks are subsampled from each of Weblica-Cache and Weblica-Synth, giving 20K tasks.[^karWeblicaScalableReproducible2026]
- **SFT hyperparameters.** Language model only is trainable (vision tower and projector frozen), cosine schedule, warmup ratio 0.1, cutoff length 80,000, effective batch size 8, bf16. Selected values: learning rate 1e-6, 2 or 3 epochs, image resolution 1280×720.[^karWeblicaScalableReproducible2026]
- **RL hyperparameters.** Constant schedule, PPO mini-batch size 32, max grad norm 1.0, max model context length 80,000, max new tokens per action 512. Selected values: SFT model as the starting point, learning rate 1e-5 or 5e-6, KL coefficient 0, 0.005, or 0.01, batch size 128 or 256, 4 or 8 rollouts per prompt, 25 rounds.[^karWeblicaScalableReproducible2026]
- **Compute.** 8 NVIDIA B200 GPUs, with environments served on the same node. Each RL training step generates 1024 rollouts (256 prompts × 4 rollouts per prompt), each with up to 25 interaction rounds, and completes in approximately 28 minutes.[^karWeblicaScalableReproducible2026]

## Experiments & Results

### Setup

- Web navigation benchmarks: [Online-Mind2Web](../benchmarks/online-mind2web.md) (diverse live websites), [DeepShop](../benchmarks/deepshop.md) (e-commerce), [WebTailBench](../benchmarks/webtailbench.md) (long-tail web tasks), and Weblica-val (500 held-out tasks on 250 unseen synthesized environments). Each benchmark's official judge is used; for WebTailBench the WebVoyager judge is used, following MolmoWeb.[^karWeblicaScalableReproducible2026]
- Test-time scaling: $k\in\{1,2,4,8\}$ independent attempts, reported as pass@$k$, with total step budget scaling linearly with $k$.[^karWeblicaScalableReproducible2026]
- Each experiment is repeated three times and the mean accuracy is reported.[^karWeblicaScalableReproducible2026]
- UI grounding benchmarks: MMBench-GUI, [ScreenSpot-v2](../benchmarks/screenspot-v2.md), and ScreenSpot-Pro.[^karWeblicaScalableReproducible2026]

### Main comparison (Table 1)

Avg. is the mean over the three live benchmarks. Baseline results are taken from the Fara and MolmoWeb papers. † Fara-7B and MolmoWeb-8B allow up to 5 and 10 retries per trajectory.[^karWeblicaScalableReproducible2026]

| Model | Total # Steps | Online-Mind2Web | DeepShop | WebTailBench | Avg. | Weblica-val |
|---|---|---|---|---|---|---|
| *API-only* | | | | | | |
| OpenAI CUA | 100 | 58.3 | 24.7 | 25.7 | 36.2 | – |
| Gemini CUA | 100 | 57.3 | 62.0 | 63.0 | 60.8 | – |
| Yutori Navigator | – | 64.7 | – | – | – | – |
| *Open-weight* | | | | | | |
| Qwen3-VL-Instruct-8B | 30 | 28.6 | 24.1 | 21.8 | 24.8 | 56.9 |
| UI-TARS-1.5-7B | 100 | 31.3 | 11.6 | 19.5 | 20.8 | – |
| GLM-4.1V-9B-Thinking | 100 | 33.9 | 32.0 | 22.4 | 29.4 | – |
| Fara-7B | ≥100† | 34.1 | 26.2 | 38.4 | 32.9 | – |
| MolmoWeb-8B | ≥100† | 35.3 | 42.3 | 49.5 | 42.4 | – |
| *Ours (pass@k)* | | | | | | |
| Weblica-8B (k=1) | 30 | 39.2 | 34.2 | 33.5 | 35.6 | 70.6 |
| Weblica-8B (k=2) | 60 | 50.3 | 45.4 | 47.0 | 47.6 | 79.0 |
| Weblica-8B (k=4) | 120 | 60.5 | 55.9 | 60.3 | 58.9 | 84.7 |
| Weblica-8B (k=8) | 240 | 68.8 | 65.8 | 72.2 | 68.9 | 88.6 |

All rows: [^karWeblicaScalableReproducible2026]

- At pass@1 with 30 steps, training improves the base Qwen3-VL-8B from 24.8% to 35.6% average across the three live benchmarks, an absolute gain of 10.8 percentage points, which the paper describes as a 44% improvement.[^karWeblicaScalableReproducible2026]
- With 60 total steps, Weblica-8B surpasses the best open-weight baseline average (47.6% vs 42.4% for MolmoWeb-8B at ≥100 steps).[^karWeblicaScalableReproducible2026]
- At pass@1 with 30 steps, Weblica-8B matches OpenAI computer-use-preview (35.6% vs 36.2% at 100 steps). With 120 total steps it reaches 58.9%, approaching Gemini computer-use-preview (60.8%).[^karWeblicaScalableReproducible2026]

### Pass@k across model sizes (Table 3)

Values are mean ± standard deviation.[^karWeblicaScalableReproducible2026]

| Size | Benchmark | Model | pass@1 | pass@2 | pass@4 | pass@8 |
|---|---|---|---|---|---|---|
| 2B | Online-Mind2Web | Qwen3-VL | 13.3 ± 0.3 | 20.1 ± 0.6 | 28.6 ± 0.9 | 38.2 ± 1.3 |
| 2B | Online-Mind2Web | Weblica-2B | 24.1 ± 0.8 | 33.9 ± 1.1 | 44.7 ± 1.2 | 55.6 ± 2.2 |
| 2B | DeepShop | Qwen3-VL | 3.3 ± 0.4 | 6.3 ± 0.8 | 11.6 ± 1.3 | 19.6 ± 1.9 |
| 2B | DeepShop | Weblica-2B | 18.0 ± 0.6 | 27.8 ± 0.5 | 38.8 ± 0.7 | 50.2 ± 0.8 |
| 2B | WebTailBench | Qwen3-VL | 8.2 ± 0.2 | 13.3 ± 0.4 | 19.9 ± 0.7 | 27.5 ± 0.6 |
| 2B | WebTailBench | Weblica-2B | 17.0 ± 0.4 | 27.3 ± 0.8 | 40.0 ± 1.4 | 53.8 ± 1.9 |
| 2B | Weblica-val | Qwen3-VL | 30.0 ± 0.3 | 40.5 ± 0.1 | 50.1 ± 0.3 | 58.1 ± 0.6 |
| 2B | Weblica-val | Weblica-2B | 50.1 ± 0.6 | 62.7 ± 0.5 | 72.9 ± 0.2 | 80.3 ± 0.2 |
| 4B | Online-Mind2Web | Qwen3-VL | 23.2 ± 0.2 | 31.3 ± 0.4 | 39.4 ± 0.3 | 46.9 ± 0.2 |
| 4B | Online-Mind2Web | Weblica-4B | 35.2 ± 0.3 | 46.0 ± 0.6 | 55.8 ± 1.0 | 64.1 ± 1.6 |
| 4B | DeepShop | Qwen3-VL | 17.1 ± 0.5 | 25.5 ± 0.9 | 33.8 ± 1.5 | 41.8 ± 2.7 |
| 4B | DeepShop | Weblica-4B | 27.8 ± 0.5 | 38.9 ± 1.5 | 49.7 ± 2.7 | 60.0 ± 3.1 |
| 4B | WebTailBench | Qwen3-VL | 16.0 ± 0.7 | 22.8 ± 0.9 | 30.2 ± 1.2 | 37.7 ± 1.4 |
| 4B | WebTailBench | Weblica-4B | 23.8 ± 0.4 | 35.4 ± 0.3 | 47.9 ± 0.3 | 59.6 ± 0.3 |
| 4B | Weblica-val | Qwen3-VL | 51.6 ± 0.7 | 61.4 ± 0.7 | 69.1 ± 0.7 | 74.9 ± 0.9 |
| 4B | Weblica-val | Weblica-4B | 64.2 ± 0.5 | 74.5 ± 0.3 | 81.3 ± 0.2 | 86.2 ± 0.6 |
| 8B | Online-Mind2Web | Qwen3-VL | 28.6 ± 0.4 | 37.6 ± 0.2 | 46.3 ± 0.3 | 54.4 ± 1.7 |
| 8B | Online-Mind2Web | Weblica-8B | 39.2 ± 0.9 | 50.3 ± 0.7 | 60.5 ± 0.9 | 68.8 ± 1.7 |
| 8B | DeepShop | Qwen3-VL | 24.1 ± 0.8 | 33.5 ± 1.2 | 41.6 ± 2.0 | 49.1 ± 3.4 |
| 8B | DeepShop | Weblica-8B | 34.2 ± 1.7 | 45.4 ± 2.3 | 55.9 ± 3.1 | 65.8 ± 3.8 |
| 8B | WebTailBench | Qwen3-VL | 21.8 ± 0.2 | 31.5 ± 0.5 | 42.0 ± 1.2 | 52.4 ± 1.8 |
| 8B | WebTailBench | Weblica-8B | 33.5 ± 0.9 | 47.0 ± 1.1 | 60.3 ± 1.3 | 72.2 ± 1.7 |
| 8B | Weblica-val | Qwen3-VL | 56.9 ± 0.7 | 65.4 ± 0.6 | 72.5 ± 0.7 | 77.9 ± 1.0 |
| 8B | Weblica-val | Weblica-8B | 70.6 ± 0.5 | 79.0 ± 0.7 | 84.7 ± 1.1 | 88.6 ± 1.5 |

### Test-time scaling and ablations

- On Online-Mind2Web, raising the action budget from 15 to 30 steps improves Weblica-8B pass@1 from 32.6% to 39.2%. The base model's 15- and 30-step curves nearly overlap.[^karWeblicaScalableReproducible2026]

Environment type, pass@1 (8B):[^karWeblicaScalableReproducible2026]

| Benchmark | Weblica-Synth only | Weblica-Cache only |
|---|---|---|
| Online-Mind2Web | 39.2% | 35.3% |
| WebTailBench | 33.5% | 30.2% |
| DeepShop | 34.2% | 35.8% |

- Initial attempts with different mixture ratios of cached and synthesized environments did not yield further improvements.[^karWeblicaScalableReproducible2026]

Training stages, pass@1 on Online-Mind2Web, base model to full SFT+RL pipeline:[^karWeblicaScalableReproducible2026]

| Model size | Base | SFT+RL |
|---|---|---|
| 2B | 13.3% | 24.1% |
| 4B | 23.2% | 35.2% |
| 8B | 28.6% | 39.2% |

- RL on top of SFT gives a larger improvement than SFT alone at every scale. SFT initialization is critical for smaller models, but SFT data has diminishing returns at larger scales.[^karWeblicaScalableReproducible2026]
- Values for the SFT-only and Base→RL configurations appear only in Figure 5 and are not transcribed here.

### Grounding (Table 2)

| Model | MMBench-GUI | ScreenSpot-v2 | ScreenSpot-Pro |
|---|---|---|---|
| Fara-7B | — | 89.3 | — |
| MolmoWeb-Ground-8B | — | 91.8 | — |
| Qwen3-VL-Instruct-8B | 82.85 | 93.95 | 54.71 |
| Weblica-8B | 83.74 | 94.50 | 55.28 |

All rows: [^karWeblicaScalableReproducible2026]

The training data contains no grounding-specific data, and grounding is preserved after training.[^karWeblicaScalableReproducible2026]

## Limitations

- **Cached environments** are static snapshots. They give a narrow and partial view of live websites, do not reflect updates over time, and do not capture the full complexity of dynamic web applications. Caching is also limited to domains where stable recordings can be obtained.[^karWeblicaScalableReproducible2026]
- **Synthesized environments** do not yet model all aspects of real websites, so a sim-to-real gap remains.[^karWeblicaScalableReproducible2026]
- **Single-turn tasks.** Agents are evaluated on isolated tasks with a fixed goal. Multi-turn sessions with evolving goals, human-in-the-loop interaction, and personalization are not covered.[^karWeblicaScalableReproducible2026]
- **Training.** The RL formulation is vanilla. Long-horizon RL, scaling RL compute, and richer SFT data such as error recovery trajectories are left for future work.[^karWeblicaScalableReproducible2026]
- **Beyond web.** The framework targets web navigation only, not mobile or desktop applications.[^karWeblicaScalableReproducible2026]
- The comparison with Fara-7B and MolmoWeb-8B uses different protocols: those baselines use retry-based evaluation, while Weblica reports pass@$k$ over independent attempts.[^karWeblicaScalableReproducible2026]

## Related

- Methods proposed: [Weblica](../methods/weblica.md), [HTTP-level caching](../methods/http-level-caching.md), [LLM-based environment synthesis](../methods/llm-based-environment-synthesis.md)
- Methods built on: [GRPO](../methods/grpo.md), [LLM-as-judge](../methods/llm-as-a-judge.md), [ReAct](../methods/react.md), [Test-time scaling](../methods/test-time-scaling.md)
- Datasets: [InstaV3](../datasets/instav3.md)
- Benchmarks: [Online-Mind2Web](../benchmarks/online-mind2web.md), [DeepShop](../benchmarks/deepshop.md), [WebTailBench](../benchmarks/webtailbench.md), [ScreenSpot-v2](../benchmarks/screenspot-v2.md), [WebArena](../benchmarks/webarena.md)
- Papers in this wiki cited by this paper: [WebRL](qiWebRLTrainingLLM2025.md), [WebArena](zhouWebArenaRealisticWeb2024.md)

[^karWeblicaScalableReproducible2026]: Kar et al. 2026
