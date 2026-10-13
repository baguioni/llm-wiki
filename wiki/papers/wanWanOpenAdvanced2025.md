---
type: Paper
title: "Wan: Open and Advanced Large-Scale Video Generative Models"
description: Open suite of diffusion-transformer video foundation models (1.3B and 14B) with a 3D causal VAE, a data and training pipeline, the Wan-Bench evaluation, and downstream image-to-video, editing, personalization, real-time, and audio models.
tags: [video-generation, diffusion-transformer, flow-matching, video-vae, text-to-video, image-to-video, inference-acceleration, ai899]
collections: [ai899]
authors: [Wan Team]
year: 2025
doi: 10.48550/arXiv.2503.20314
arxiv: "2503.20314"
arxiv_version: 2503.20314v2
code: https://github.com/Wan-Video/Wan2.1
sources:
  - id: wanWanOpenAdvanced2025
    resource: zotero://select/items/@wanWanOpenAdvanced2025
    title: "Wan: Open and Advanced Large-Scale Video Generative Models"
---

# Wan: Open and Advanced Large-Scale Video Generative Models

Text source: arXiv HTML, version `2503.20314v2`.

## Summary

[Wan](../methods/wan.md) is an open suite of video foundation models from the Wan Team at Alibaba Group, built on the [diffusion transformer](../methods/diffusion-transformer.md) (DiT) paradigm combined with [flow matching](../methods/flow-matching.md).[^wanWanOpenAdvanced2025] The suite has two text-to-video and image-to-video models, with 1.3B and 14B parameters, and covers up to eight tasks including image-to-video, instruction-guided video editing, and personal video generation.[^wanWanOpenAdvanced2025] The paper states that Wan is the first model that can generate visual text in both Chinese and English.[^wanWanOpenAdvanced2025]

The 14B model is trained on billions of images and videos, amounting to $\mathcal{O}(1)$ trillions of tokens in total.[^wanWanOpenAdvanced2025] The 1.3B model requires only 8.19 GB VRAM.[^wanWanOpenAdvanced2025] The paper reports that the 14B model reaches a weighted score of 0.724 on its own [Wan-Bench](../benchmarks/wan-bench.md) and a total score of 86.22% on the [VBench](../benchmarks/vbench.md) leaderboard, above Sora on both.[^wanWanOpenAdvanced2025] Source code and all models are released.[^wanWanOpenAdvanced2025]

## Contributions

- [Wan-VAE](../methods/wan-vae.md), a 3D causal VAE with $4\times 8\times 8$ spatio-temporal compression, 127M parameters, and a feature cache mechanism for arbitrarily long videos.[^wanWanOpenAdvanced2025]
- A DiT video model scaled to 14 billion parameters that uses cross-attention for text conditions, full spatio-temporal attention, and a shared time-embedding MLP.[^wanWanOpenAdvanced2025]
- A data pipeline: a four-step cleaning process, visual text data construction, post-training data selection, and an in-house dense caption model.[^wanWanOpenAdvanced2025]
- Training and inference efficiency techniques: 2D context parallelism, activation offloading, diffusion cache, FP8 GEMM, and 8-bit FlashAttention.[^wanWanOpenAdvanced2025]
- Wan-Bench, an automated benchmark with three core dimensions and 14 fine-grained metrics, weighted by human feedback.[^wanWanOpenAdvanced2025]
- Extended applications: image-to-video, unified video editing ([VACE](../methods/vace.md)), text-to-image, video personalization, camera motion control, real-time video generation, and video-to-audio generation.[^wanWanOpenAdvanced2025]

## Method

### Data

- **Pre-training filtering.** Fundamental-dimension filters (text detection, aesthetic evaluation, NSFW score, watermark and logo detection, black border detection, overexposure detection, synthetic image detection, blur detection, duration and resolution) eliminate approximately 50% of the initial dataset.[^wanWanOpenAdvanced2025] Video duration must exceed 4 seconds.[^wanWanOpenAdvanced2025] The paper states that even minimal contamination ($<10\%$) by generated images can significantly degrade model performance.[^wanWanOpenAdvanced2025]
- **Visual quality.** Data are divided into 100 clusters, samples from each cluster are scored manually from 1 to 5, and an expert assessment model trained on the annotations scores the entire dataset.[^wanWanOpenAdvanced2025]
- **Motion quality.** Videos are classified into six tiers: optimal motion, medium-quality motion, static videos, camera-driven motion, low-quality motion, and shaky camera footage. The last two are excluded.[^wanWanOpenAdvanced2025]
- **Visual text data.** Hundreds of millions of text-containing images are synthesized by rendering Chinese characters on a pure white background, and real text-containing images are captioned by Qwen2-VL from OCR results.[^wanWanOpenAdvanced2025]
- **Post-training data.** The top 20% of images by expert-model score plus manually collected images give millions of curated images; millions of videos with simple movements and millions with complex movements are selected, covering 12 major categories.[^wanWanOpenAdvanced2025]
- **Dense caption model.** A LLaVA-style architecture: a ViT encoder, a two-layer perception, and the Qwen LLM.[^wanWanOpenAdvanced2025] Images are divided into a maximum of seven patches, each pooled to a 12$\times$12 grid.[^wanWanOpenAdvanced2025] Videos are sampled at 3 frames per second with an upper limit of 129 frames, with a slow-fast encoding that keeps the original resolution for every fourth frame.[^wanWanOpenAdvanced2025] The slow-fast mechanism improves performance from 67.6% to 69.1% on VideoMME without subtitles.[^wanWanOpenAdvanced2025]

### Wan-VAE

- Given a video $V\in\mathbb{R}^{(1+T)\times H\times W\times 3}$, Wan-VAE compresses its dimensions to $[1+T/4,H/8,W/8]$ and expands the number of channels to 16. The first frame is only spatially compressed.[^wanWanOpenAdvanced2025]
- All GroupNorm layers are replaced with RMSNorm layers to preserve temporal causality.[^wanWanOpenAdvanced2025]
- Halving the input feature channel in the spatial upsampling layer gives a 33% reduction in memory consumption during inference.[^wanWanOpenAdvanced2025]
- Training has three stages: a 2D image VAE; inflation to a 3D causal VAE trained on low-resolution (128$\times$128), 5-frame videos; and fine-tuning on high-quality videos with a GAN loss from a 3D discriminator.[^wanWanOpenAdvanced2025] The $L1$ reconstruction loss, KL loss, and LPIPS perceptual loss are weighted by 3, 3e-6, and 3.[^wanWanOpenAdvanced2025]
- **Feature cache.** The video is divided into $1+T/4$ chunks, each chunk has at most 4 frames, and frame-level features from preceding chunks are cached and reused in the causal convolutions of later chunks.[^wanWanOpenAdvanced2025]

### Video diffusion transformer

- The model has three components: Wan-VAE, the diffusion transformer, and a text encoder.[^wanWanOpenAdvanced2025]
- The patchifying module is a 3D convolution with kernel size $(1,2,2)$, giving sequence length $L=(1+T/4)\times H/16\times W/16$.[^wanWanOpenAdvanced2025]
- Text conditions enter through cross-attention.[^wanWanOpenAdvanced2025]
- An MLP with a Linear layer and a SiLU layer processes the time embeddings and predicts six modulation parameters. It is shared across all transformer blocks, and each block learns a distinct set of biases. The paper reports that this reduces the parameter count by approximately $25\%$.[^wanWanOpenAdvanced2025]
- The text encoder is [umT5](../methods/umt5.md), with a text embedding sequence 512 tokens long.[^wanWanOpenAdvanced2025]
- **Objective.** Rectified-flow interpolation $x_{t}=tx_{1}+(1-t)x_{0}$ with velocity target $v_{t}=x_{1}-x_{0}$ and an MSE loss; $t$ is sampled from a logit-normal distribution.[^wanWanOpenAdvanced2025]
- **Training schedule.** Low-resolution ($256$ px) text-to-image pre-training, then three joint image-video stages: $256$ px images with 5-second $192$ px, $16$ fps video; $480$ px; and $720$ px.[^wanWanOpenAdvanced2025] Post-training runs jointly at $480$ px and $720$ px.[^wanWanOpenAdvanced2025]
- **Configuration.** bf16-mixed precision, AdamW with weight decay $1e^{-3}$, and initial learning rate $1e^{-4}$ reduced on plateaus of FID and CLIP Score.[^wanWanOpenAdvanced2025]

### Training efficiency

- The DiT accounts for more than 85% of the overall computation during training.[^wanWanOpenAdvanced2025] When the sequence length reaches 1 million, attention can account for up to 95% of the end-to-end training time.[^wanWanOpenAdvanced2025]
- With a sequence length of 1 million tokens and micro-batch size 1, activation memory for the 14B DiT can exceed 8 TB.[^wanWanOpenAdvanced2025]
- The DiT uses FSDP for parameter sharding and a 2D context parallelism (CP) with Ring Attention as the outer layer and Ulysses as the inner layer.[^wanWanOpenAdvanced2025] With a sequence length of 256K and 16 GPUs across 2 machines, CP communication overhead falls from over $10\%$ with Ulysses to below $1\%$.[^wanWanOpenAdvanced2025]
- Example configuration with 128 GPUs: CP size 16 (Ulysses 8, Ring Attention 2), FSDP 32, DP 4.[^wanWanOpenAdvanced2025]
- Memory: activation offloading is prioritized and combined with gradient checkpointing.[^wanWanOpenAdvanced2025]

### Inference acceleration

Inference typically uses around 50 sampling steps.[^wanWanOpenAdvanced2025]

| Technique | What it does | Reported gain |
|---|---|---|
| 2D context parallel + FSDP | Multi-GPU scaling of one video | Nearly linear speedup on Wan 14B |
| Diffusion cache | Attention cache and [classifier-free guidance](../methods/classifier-free-guidance.md) (CFG) cache, reusing results across sampling steps | 1.62× on the Wan 14B text-to-video model |
| FP8 GEMM | FP8 for all GEMM operations in the DiT block | 1.13× speedup in the DiT module |
| 8-bit FlashAttention | Int8 for $S=QK^{T}$, FP8 for $O=PV$, FP32 cross-block accumulation | more than 1.27× inference efficiency |

All rows: [^wanWanOpenAdvanced2025]

The 8-bit FlashAttention achieves 95% MFU on NVIDIA H20 GPUs.[^wanWanOpenAdvanced2025] User prompts are rewritten by Qwen2.5-Plus to match the distribution of training captions.[^wanWanOpenAdvanced2025]

### Extended applications

- **Image-to-video.** The condition image is concatenated with zero-filled frames, compressed by Wan-VAE, and concatenated with the noise latent and a binary mask along the channel axis. CLIP image features pass through a three-layer MLP and are injected by decoupled cross-attention.[^wanWanOpenAdvanced2025] The same framework covers video continuation and first-last frame transformation.[^wanWanOpenAdvanced2025]
- **Unified video editing.** VACE unifies inputs as a Video Condition Unit $V=[T;F;M]$ and offers full fine-tuning or a pluggable Context Adapter. The editing model is pre-trained on Wan-T2V-14B and supports resolutions up to 720p.[^wanWanOpenAdvanced2025]
- **Video personalization.** $K$ face frames are prepended in the Wan-VAE latent space and the model is conditioned in an inpainting fashion through self-attention, without an ID feature extractor.[^wanWanOpenAdvanced2025] The dataset has about $\mathcal{O}(10)$M personalized videos and about $\mathcal{O}(1)$M videos with faces synthesized by Instant-ID.[^wanWanOpenAdvanced2025]
- **Camera motion control.** A camera pose encoder turns Plücker coordinates into multi-level features, and a camera pose adapter applies $f_{i}=(\gamma_{i}+1)*f_{i-1}+\beta_{i}$ in each DiT block.[^wanWanOpenAdvanced2025]
- **Real-time generation.** *Streamer* denoises a sliding window of tokens in a queue. It is distilled with a [latent consistency model](../methods/latent-consistency-model.md) into a four-step model, which gives a 10 - 20 $\times$ acceleration and 8 - 16 FPS.[^wanWanOpenAdvanced2025] With int8 and TensorRT quantization the text reports 8 FPS on a single 4090 GPU.[^wanWanOpenAdvanced2025]
- **Video-to-audio.** A flow-matching DiT with a 1D-VAE on raw waveforms generates stereo audio of at most 12 seconds at 44.1 kHz. Training data is $\mathcal{O}(1)$ thousand hours.[^wanWanOpenAdvanced2025]

## Experiments & Results

### Wan-Bench (Table 2)

1,035 samples per model. The weighted score uses weights from the Pearson correlation between model-generated and human-rated scores, from over 5,000 pairwise comparisons.[^wanWanOpenAdvanced2025]

| Wan-Bench Dimension | CNTopB | Hunyuan | Mochi | CNTopA | Sora | Wan 1.3B | Wan 14B |
|---|---|---|---|---|---|---|---|
| Large Motion Generation | 0.405 | 0.413 | 0.420 | 0.284 | **0.482** | 0.468 | 0.415 |
| Human Artifacts | 0.712 | 0.734 | 0.622 | **0.833** | 0.786 | 0.707 | 0.691 |
| Pixel-level Stability | 0.977 | **0.983** | 0.981 | 0.974 | 0.952 | 0.976 | 0.972 |
| ID Consistency | 0.940 | 0.935 | 0.930 | 0.936 | 0.925 | 0.938 | **0.946** |
| Physical Plausibility | 0.836 | 0.898 | 0.728 | 0.759 | 0.933 | 0.912 | **0.939** |
| Smoothness | 0.765 | 0.890 | 0.530 | 0.880 | **0.930** | 0.790 | 0.910 |
| Comprehensive Image Quality | 0.621 | 0.605 | 0.530 | **0.668** | 0.665 | 0.596 | 0.640 |
| Scene Generation Quality | 0.369 | 0.373 | 0.368 | 0.386 | **0.388** | 0.385 | 0.386 |
| Stylization Ability | **0.623** | 0.386 | 0.403 | 0.346 | 0.606 | 0.430 | 0.328 |
| Single Object Accuracy | **0.987** | 0.912 | 0.949 | 0.942 | 0.932 | 0.930 | 0.952 |
| Multiple Object Accuracy | 0.840 | 0.850 | 0.693 | 0.880 | **0.882** | 0.859 | 0.860 |
| Spatial Position Accuracy | 0.518 | 0.464 | 0.512 | 0.434 | 0.458 | 0.476 | **0.590** |
| Camera Control | 0.465 | 0.406 | **0.605** | 0.529 | 0.380 | 0.483 | 0.527 |
| Action Instruction Following | **0.917** | 0.735 | 0.907 | 0.783 | 0.721 | 0.844 | 0.860 |
| **Weighted Score** | 0.690 | 0.673 | 0.639 | 0.693 | 0.700 | 0.689 | **0.724** |

All rows: [^wanWanOpenAdvanced2025]

### VBench leaderboard (Table 4)

| Model Name | Quality Score | Semantic Score | Total Score |
|---|---|---|---|
| MiniMax-Video-01 | 84.85% | 77.65% | 83.41% |
| [Hunyuan](../methods/hunyuanvideo.md) (Open-Source Version) | 85.09% | 75.82% | 83.24% |
| Gen-3 (2024-07) | 84.11% | 75.17% | 82.32% |
| CogVideoX1.5-5B (5s SAT prompt-optimized) | 82.78% | 79.76% | 82.17% |
| Kling (2024-07 high-performance mode) | 83.39% | 75.68% | 81.85% |
| [Sora](../methods/sora.md) | 85.51% | 79.35% | 84.28% |
| Wan 1.3B | 84.92% | 80.10% | 83.96% |
| Wan 14B (2025-02-24) | **86.67%** | **84.44%** | **86.22%** |

All rows: [^wanWanOpenAdvanced2025]

### Human evaluation, text-to-video (Table 3, "Win rate gap of T2V")

Over 700 evaluation tasks annotated by more than 20 individuals. The table note says the values are the proportion of instances in which Wan 14B outperformed the other model in pairwise comparisons.[^wanWanOpenAdvanced2025]

| | CN-TopA | CN-TopB | CN-TopC | Runway | All Rounds |
|---|---|---|---|---|---|
| Visual Quality | 30.6% | 15.9% | 27.8% | 48.1% | 5710 |
| Motion Quality | 16.1% | 9.7% | 14.9% | 40.3% | 5785 |
| Matching | 46.0% | 57.9% | 56.7% | 69.1% | 5578 |
| Overall Ranking | 44.0% | 44.0% | 48.9% | 67.6% | 5560 |

All rows: [^wanWanOpenAdvanced2025]

### Human evaluation, image-to-video (Table 7, "Win rate gap of I2V models")

| | CN-TopA | CN-TopB | CN-TopC | CN-TopD | All Rounds |
|---|---|---|---|---|---|
| Visual Quality | 29.2% | 60.8% | 24.6% | 55.6% | 896 |
| Motion Quality | 21.7% | 21.7% | 32.5% | 67.0% | 890 |
| Matching | -4.2% | 35.0% | 51.7% | 72.2% | 896 |
| Overall Ranking | 10.8% | 47.5% | 50.8% | 81.6% | 890 |

All rows: [^wanWanOpenAdvanced2025]

### Wan-VAE

- Evaluated on 200 videos of 25 frames at $720\times 720$ resolution, by PSNR and frames per second of latency. The per-model values are given only in Figure 7.[^wanWanOpenAdvanced2025]
- Under the same hardware environment, Wan-VAE reconstruction is 2.5 times faster than HunYuan Video.[^wanWanOpenAdvanced2025]

### Ablations (1.3B version)

- **Adaptive normalization.** Four configurations trained on text-to-image for 200,000 steps with global batch size 1536: Full-shared-adaLN-1.3B (30 blocks), Half-shared-adaLN-1.5B, Full-shared-adaLN-1.5B (35 layers), and Non-shared-AdaLN-1.7B. Full-shared-AdaLN-1.5B consistently achieves the lowest training loss. The curves are given only in Figure 16.[^wanWanOpenAdvanced2025]
- **Text encoder.** umT5 (5.3B) is compared with Qwen2.5-7B-Instruct and GLM-4-9B by training loss (Figure 17), where umT5 performs most favorably.[^wanWanOpenAdvanced2025]

| Models | umT5 | Qwen-VL-7B (last layer) | Qwen-VL-7B (second last layer) |
|---|---|---|---|
| FID (↓) | 43.01 | 43.72 | **42.91** |

All rows: [^wanWanOpenAdvanced2025]

- **Autoencoder.** VAE-D replaces the reconstruction loss with a diffusion loss. FID (↓), Table 5:[^wanWanOpenAdvanced2025]

| Model | VAE | VAE-D |
|---|---|---|
| 10k steps | **42.60** | 44.21 |
| 15k steps | **40.55** | 41.16 |

All rows: [^wanWanOpenAdvanced2025]

### Other reported numbers

| Item | Value |
|---|---|
| Caption model vs Google Gemini 1.5 Pro | F1 on ten dimensions, 1,000 videos each; values only in Figure 4. Wan's model is better on event, camera angle, camera motion, style, and object color |
| Video personalization, ArcFace similarity (Table 8) | Wan 0.5526, CN-TopA 0.5655, CN-TopB 0.5197, CN-TopC 0.4998 |
| Real-time generation (Figure 30 caption) | 15 minutes video with 8 A100 GPUs at 8 FPS |
| Real-time generation (Figure 31 caption) | single RTX 4090 GPU, int8 and TensorRT quantization, 20 FPS |
| Video-to-audio vs [MMAudio](../methods/mmaudio.md) | qualitative comparison only (Figure 33) |

All rows: [^wanWanOpenAdvanced2025]

## Limitations

- Preserving fine-grained details in scenarios with large motion remains a challenge.[^wanWanOpenAdvanced2025]
- Inference on the 14B model currently requires approximately 30 minutes on a single GPU without additional optimization.[^wanWanOpenAdvanced2025]
- Performance in specific domains such as education and medicine may be insufficient.[^wanWanOpenAdvanced2025]
- The video-to-audio model cannot generate human vocal sounds such as laughter, crying, and speech, because speech-related data is excluded from its training set.[^wanWanOpenAdvanced2025]
- TensorRT quantization introduces a modest increase in network error, seen as minor artifacts and in some cases flickering or temporal incoherence.[^wanWanOpenAdvanced2025]
- On Wan-Bench the 14B model is not the best on every dimension. It scores 0.328 on Stylization Ability against 0.623 for CNTopB, and 0.691 on Human Artifacts against 0.833 for CNTopA.[^wanWanOpenAdvanced2025]
- Wan-Bench is defined by the authors, and its weights come from comparisons that include Wan outputs.[^wanWanOpenAdvanced2025]
- Dataset sizes are given only as orders of magnitude ("billions", "millions", $\mathcal{O}(1)$M), and the commercial baselines CN-TopA to CN-TopD are not named.[^wanWanOpenAdvanced2025]
- Internal inconsistencies in the source text: Table 5 labels its rows "10k steps" and "15k steps", but the text says FID is measured at 100,000 and 150,000 steps.[^wanWanOpenAdvanced2025] The Figure 31 caption gives 20 FPS on a single RTX 4090, but the text gives 8 FPS on a single 4090.[^wanWanOpenAdvanced2025] The human-evaluation text says Wan 14B "consistently excels across all visual quality dimensions", while several Table 3 win rates are below 50%; the table title calls the values a "win rate gap" and the note calls them a proportion.[^wanWanOpenAdvanced2025]

## Related

- Methods proposed: [Wan](../methods/wan.md), [Wan-VAE](../methods/wan-vae.md), [VACE](../methods/vace.md)
- Methods built on: [Diffusion transformer](../methods/diffusion-transformer.md), [Flow matching](../methods/flow-matching.md), [umT5](../methods/umt5.md), [Classifier-free guidance](../methods/classifier-free-guidance.md), [Latent consistency model](../methods/latent-consistency-model.md)
- Systems compared against: [HunyuanVideo](../methods/hunyuanvideo.md), [Sora](../methods/sora.md), [MMAudio](../methods/mmaudio.md)
- Benchmarks: [Wan-Bench](../benchmarks/wan-bench.md), [VBench](../benchmarks/vbench.md)

[^wanWanOpenAdvanced2025]: Wan et al. 2025
