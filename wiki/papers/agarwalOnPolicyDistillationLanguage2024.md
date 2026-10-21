---
type: Paper
title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
description: Generalized Knowledge Distillation (GKD) trains an autoregressive student on its own sampled outputs with token-level teacher feedback and a choice of divergence, and beats supervised KD and SeqKD for T5 students on summarization, translation, math reasoning, and instruction tuning.
tags: [knowledge-distillation, on-policy-distillation, gkd, model-compression, imitation-learning, speculative-drafter]
collections: [speculative drafter]
authors: [Rishabh Agarwal, Nino Vieillard, Yongchao Zhou, Piotr Stanczyk, Sabela Ramos, Matthieu Geist, Olivier Bachem]
doi: 10.48550/arXiv.2306.13649
arxiv: "2306.13649"
arxiv_version: 2306.13649v3
sources:
  - id: agarwalOnPolicyDistillationLanguage2024
    resource: zotero://select/items/@agarwalOnPolicyDistillationLanguage2024
    title: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes"
---

# On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes

Text source: arXiv HTML, version `2306.13649v3`.

## Summary

Knowledge distillation (KD) methods for autoregressive sequence models train on a fixed set of output sequences, either ground-truth or teacher-generated. The paper argues that this causes a distribution mismatch between the sequences seen in training and those the student generates at inference.[^agarwalOnPolicyDistillationLanguage2024] It also argues that the usual forward-KL objective can force a low-capacity student to put mass on tokens the teacher considers unlikely.[^agarwalOnPolicyDistillationLanguage2024]

[Generalized Knowledge Distillation](../methods/gkd.md) (GKD) treats distillation as imitation learning with an interactive expert. The student is trained on sequences it samples itself, with the teacher's token-level probabilities on those sequences as the labels, and the divergence between teacher and student is a free choice.[^agarwalOnPolicyDistillationLanguage2024] On-policy GKD can also be combined with RL fine-tuning.[^agarwalOnPolicyDistillationLanguage2024]

With supervised fine-tuned T5 models (T5-XL teacher; T5-small, base, and large students), on-policy GKD gives relative gains over the initial student of 2.1× on summarization, 1.7× on machine translation, and 1.9× on arithmetic reasoning compared with the gains of baseline KD methods, averaged over student sizes.[^agarwalOnPolicyDistillationLanguage2024] In task-agnostic distillation on FLAN it gives 2% and 1% absolute accuracy improvement on held-out BBH and MMLU.[^agarwalOnPolicyDistillationLanguage2024]

## Contributions

- GKD, which distills with on-policy student-generated outputs guided by token-level teacher probabilities, and outperforms commonly used methods in task-specific and task-agnostic KD.[^agarwalOnPolicyDistillationLanguage2024]
- A combination of on-policy GKD with RL fine-tuning (for example RLAIF), which the authors state had not been explored before.[^agarwalOnPolicyDistillationLanguage2024]
- A systematic evaluation of GKD design choices: the importance of on-policy student-generated sequences, and the task dependence of the best divergence.[^agarwalOnPolicyDistillationLanguage2024]

## Method

### Divergences

- Forward KL $\mathcal{D}_{KL}(P\|Q)$ and reverse KL $\mathcal{D}_{KL}(Q\|P)$. Forward KL under an empirical data distribution corresponds to maximum likelihood.[^agarwalOnPolicyDistillationLanguage2024] Figure A.16 shows reverse KL as mode-seeking and forward KL as mode-covering when a unimodal Gaussian approximates a mixture.[^agarwalOnPolicyDistillationLanguage2024]
- Generalized JSD($\beta$) interpolates between the two with a bounded coefficient $0<\beta<1$: $\mathcal{D}_{JSD(\beta)}(P\|Q)=\beta\mathcal{D}_{KL}(P\|\beta P+(1-\beta)Q)+(1-\beta)\mathcal{D}_{KL}(Q\|\beta P+(1-\beta)Q)$. Its gradients behave like forward KL for $\beta$ near 0 and like reverse KL for $\beta$ near 1. It is bounded even for distributions with disjoint supports.[^agarwalOnPolicyDistillationLanguage2024]
- The sequence-level discrepancy is the token-level divergence averaged over the $L_y$ positions of an output $y$ (Eq. 2).[^agarwalOnPolicyDistillationLanguage2024]

### Baselines expressed in the framework

- **Supervised FT:** negative log-likelihood of ground-truth outputs.[^agarwalOnPolicyDistillationLanguage2024]
- **SeqKD** (Kim & Rush 2016): supervised FT on teacher-generated outputs.[^agarwalOnPolicyDistillationLanguage2024]
- **Supervised KD:** forward KL to the teacher's token-level distributions on a fixed dataset (Eq. 3).[^agarwalOnPolicyDistillationLanguage2024]
- **ImitKD** and **f-distill** are "mixed" data variants of GKD ($\lambda=0.5$) with forward KL and total variation distance, respectively.[^agarwalOnPolicyDistillationLanguage2024]

### On-policy KD and GKD

- **On-policy KD** samples $y\sim p_{\text{S}}(\cdot|x)$ from the student and minimizes the forward KL to the teacher on those sequences (Eq. 4). Gradients are not backpropagated through the student's sampling distribution, which the paper says makes training stable and computationally efficient. The student samples at temperature $\gamma=1$ during training.[^agarwalOnPolicyDistillationLanguage2024]
- **GKD** mixes fixed-dataset and on-policy sequences and allows any divergence $\mathcal{D}$:
  $L_{\mathrm{GKD}}(\theta)=(1-\lambda)\mathbb{E}_{(x,y)\sim(X,Y)}[\mathcal{D}(p_{\text{T}}\|p_{\text{S}}^{\theta})(y|x)]+\lambda\mathbb{E}_{x\sim X}[\mathbb{E}_{y\sim p_{\text{S}}(\cdot|x)}[\mathcal{D}(p_{\text{T}}\|p_{\text{S}}^{\theta})(y|x)]]$, where $\lambda\in[0,1]$ is the student data fraction. Supervised KD and on-policy KD are GKD with forward KL and $\lambda=0$ and $\lambda=1$.[^agarwalOnPolicyDistillationLanguage2024]
- Algorithm 1 draws $u\sim Uniform(0,1)$ each step and uses a student-generated batch if $u\leq\lambda$, otherwise a batch from $(X,Y)$.[^agarwalOnPolicyDistillationLanguage2024]
- The student is assumed to already generate sequences of adequate quality; all experiments start from supervised fine-tuned students, analogous to SFT followed by online RL in RLHF.[^agarwalOnPolicyDistillationLanguage2024]
- **Choice of divergence.** Forward KL requires the student to cover the whole support of the teacher, which can lead to mass on low-probability tokens, hallucination, and low-quality generations, especially with temperature sampling and a much smaller student. Mode-seeking divergences such as reverse KL avoid this at the cost of less diverse generations. The best divergence appears to be task-dependent.[^agarwalOnPolicyDistillationLanguage2024]

### RL fine-tuning with on-policy GKD

The regularized objective is $\mathbb{E}_{x\sim X}[(1-\alpha)E_{y\sim p_{\text{S}}^{\theta}(\cdot|x)}[r(y)]-\alpha\mathbb{E}_{y\sim p_{\text{S}}(\cdot|x)}[\mathcal{D}(p_{\text{T}}\|p_{\text{S}}^{\theta})(y|x)]]$, with $\alpha\in[0,1]$ setting the strength of distillation against the reward (Eq. 5). For minimal changes to existing RL fine-tuning workflows the paper recommends reverse KL or JSD (0.9).[^agarwalOnPolicyDistillationLanguage2024]

## Experiments & Results

### Setup

- Teacher: supervised fine-tuned T5-XL ($\sim$3B). Students: T5-small (77M), T5-base (250M), T5-large (800M), smaller than the teacher by $38\times$, $12\times$, and $3.8\times$. All start from LM-adapted T5v1.1 checkpoints with further supervised FT.[^agarwalOnPolicyDistillationLanguage2024]
- GKD variants: forward KL, reverse KL, JSD (0.1), JSD (0.5), JSD (0.9); student data fraction $\lambda=1$ (on-policy), $0.5$ (mixed), $0$ (supervised). All baselines start from the same supervised fine-tuned student.[^agarwalOnPolicyDistillationLanguage2024]
- Optimizer: Adafactor.[^agarwalOnPolicyDistillationLanguage2024]

| Task | Training steps | Batch size | LR | Max input / output length | Teacher softmax temperature | Evaluation |
|---|---|---|---|---|---|---|
| XSum | 40,000 | 32 | 0.0003 | 1024 / 64 | 1 (greedy eval), 0.1 (temperature-sampling eval) | Greedy & temp. sampling |
| GSM8K | 40,000 | 32 | 0.0003 | 512 / 320 | 0.1 | Greedy sampling |
| WMT en-de | 100,000 | 32 | 0.0003 | 80 / 80 | 1.0 | Beam search |
| FLAN instruction tuning | 50,000 | 128 | 0.0001 | 2048 / 256 | 1.0 | Greedy sampling |

All rows: [^agarwalOnPolicyDistillationLanguage2024]

On XSum, T5-small uses LR 0.001, and reverse KL uses 0.0003 for all models because it was more sensitive to higher LRs.[^agarwalOnPolicyDistillationLanguage2024]

### Summarization ([XSum](../datasets/xsum.md), ROUGE-2)

- GKD improves consistently over SeqKD and supervised KD across student sizes, and lets a T5 model $7000\times$ smaller than PaLM (540B) surpass PaLM's few-shot performance.[^agarwalOnPolicyDistillationLanguage2024]
- On-policy GKD with JSD (0.9) outperforms ImitKD and f-distill under both greedy and temperature sampling ($\gamma=1$).[^agarwalOnPolicyDistillationLanguage2024]
- **Data efficiency.** With T5-small and subsampled training sets of 1K (0.5%), 10K (5%), and 50K (25%) examples, on-policy GKD on the 5% subset without any ground-truth summaries outperforms supervised KD and ImitKD trained on the entire dataset with ground-truth summaries.[^agarwalOnPolicyDistillationLanguage2024]
- **Ablations.** On-policy and mixed variants consistently outperform supervised variants. Mode-seeking divergences do better under temperature sampling; with greedy sampling the divergence does not matter much.[^agarwalOnPolicyDistillationLanguage2024] With temperature-sampling evaluation, on-policy GKD with reverse KL and JSD (0.9) performs best and forward KL performs poorly.[^agarwalOnPolicyDistillationLanguage2024]
- Greedy-evaluation reference scores: teacher ROUGE-2 22; students T5-small 13.4, base 17.9, large 19.6.[^agarwalOnPolicyDistillationLanguage2024]
- **Quality vs diversity.** Moving from forward KL through JSD to reverse KL lowers diversity (measured with Self-BLEU) and often raises quality, especially at temperature $\gamma=1$. Lowering the temperature narrows the quality gap between divergences.[^agarwalOnPolicyDistillationLanguage2024]
- **RL + on-policy GKD.** With a T5-base student, a T5-XXL NLI textual-entailment reward, and JSD (0.9), raising $\alpha$ increases ROUGE-2 and decreases the gain in factual consistency. GKD + RL reaches higher ROUGE-2 than RLEF\* (which regularizes toward the original student) while generating summaries more factually consistent than the teacher's.[^agarwalOnPolicyDistillationLanguage2024]

### Machine translation ([WMT14 en-de](../datasets/wmt14-en-de.md), BLEU)

- Teacher BLEU 28; T5-small student 25.58; T5-base student 26.98.[^agarwalOnPolicyDistillationLanguage2024]
- Generalized JSD performs better than forward or reverse KL, with a smaller gap for the larger student. On-policy and mixed data outperform variants that use only the fixed supervised dataset.[^agarwalOnPolicyDistillationLanguage2024]
- The best WMT variant ($\lambda=1$, JSD (0.1)) gives 53% higher BLEU improvement than ImitKD and 162% higher than f-distill, averaged over small and base students.[^agarwalOnPolicyDistillationLanguage2024]

### Arithmetic reasoning ([GSM8K](../datasets/gsm8k.md), 4-shot CoT, accuracy)

- Training data: about 5.3K (problem, CoT) pairs with CoT outputs generated by PaLM-540B (Magister et al. 2022). Students and teacher are FLAN-T5 models fine-tuned for 10K steps on these CoTs. The fine-tuned FLAN T5-XL teacher reaches 27.9 test accuracy.[^agarwalOnPolicyDistillationLanguage2024]
- Student reference accuracies: T5-small 4.585, T5-base 20.5 (Figure A.14); Figure 7 gives 10.16 for the T5-base student.[^agarwalOnPolicyDistillationLanguage2024]
- Using only the fixed CoT dataset, or mixing it with student CoTs, falls short of using only student-generated CoTs. Forward KL performs well; reverse KL also performs well, especially with only a fixed dataset.[^agarwalOnPolicyDistillationLanguage2024]
- Performance improves as the fraction of on-policy data grows, provided at least 25% of the data is on-policy.[^agarwalOnPolicyDistillationLanguage2024]
- On-policy GKD outperforms baseline KD methods across all student sizes.[^agarwalOnPolicyDistillationLanguage2024]
- **Self-distillation.** With FLAN T5-large as both teacher (supervised fine-tuned on GSM8K, 20.5%) and student (not trained on GSM8K, 14.4%), self-distilled students surpass the teacher, and on-policy GKD performs best.[^agarwalOnPolicyDistillationLanguage2024]
- **Compute.** On GSM8K, student sampling costs approximately $1.8\times$, $2\times$, and $2.2\times$ the cost of sampling from a fixed dataset, for student-teacher ratios of $38\times$, $12\times$, and $3.8\times$.[^agarwalOnPolicyDistillationLanguage2024]

### Task-agnostic distillation (FLAN2021)

- FLAN T5-XL teacher, FLAN T5-Base student, distilled on FLAN2021 (5.36 million examples, 62 tasks), checkpoints after 50K steps. Evaluation on held-out [MMLU](../datasets/mmlu.md) (57 tasks) and BBH (23 tasks), few-shot exact match, unweighted task average. SeqKD is not run because generating teacher data during training is too expensive.[^agarwalOnPolicyDistillationLanguage2024]
- On-policy GKD with reverse KL substantially outperforms supervised KD and ImitKD, and reverse KL does much better than forward KL here. The authors hypothesize that mode-seeking helps the model focus on the main intent of an instruction.[^agarwalOnPolicyDistillationLanguage2024]
- The Figure 10 caption gives the teacher at 52.4% on MMLU and 41% on BBH, and a "student T5-large" at 35.6% on MMLU and 31.25% on BBH, while the setup text names FLAN T5-Base as the student.[^agarwalOnPolicyDistillationLanguage2024]

### Use in speculative decoding

The related-work section states that Zhou et al. (2023, [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md)) and Liu et al. (2023, online speculative decoding) apply GKD to improve the alignment between draft and target model for a better speculative decoding speedup.[^agarwalOnPolicyDistillationLanguage2024]

## Limitations

- GKD assumes a student that already generates sequences of adequate quality; all experiments start from supervised fine-tuned students.[^agarwalOnPolicyDistillationLanguage2024]
- On-policy sampling adds training compute ($1.8\times$ to $2.2\times$ on GSM8K). The authors argue that serving cost usually dominates fine-tuning cost.[^agarwalOnPolicyDistillationLanguage2024]
- The best divergence is task- and temperature-dependent, so it has to be chosen per task.[^agarwalOnPolicyDistillationLanguage2024]
- All experiments use T5 encoder-decoder models up to T5-XL as the teacher.[^agarwalOnPolicyDistillationLanguage2024]
- Most comparative results are shown only in figures; the text gives few exact numbers.
- Section 2 states that minimizing reverse and forward KL "results in mean and mode-seeking behavior", in that order, while Figure A.16 labels reverse KL mode-seeking and forward KL mode-covering.[^agarwalOnPolicyDistillationLanguage2024]
- The paper has no dedicated limitations section.

## Related

- Methods proposed: [GKD](../methods/gkd.md)
- Methods built on or compared: [Knowledge distillation](../methods/knowledge-distillation.md), [Chain-of-Thought prompting](../methods/chain-of-thought.md), [SeqKD](../methods/seqkd.md), [f-Distill](../methods/f-distill.md)
- Applied to drafters by: [DistillSpec](../methods/distillspec.md), and indirectly [AdaSPEC](../methods/adaspec.md), which builds on DistillSpec
- Datasets: [XSum](../datasets/xsum.md), [WMT14 en-de](../datasets/wmt14-en-de.md), [GSM8K](../datasets/gsm8k.md), [MMLU](../datasets/mmlu.md), [BIG-Bench Hard](../datasets/bbh.md)

## Open questions and results

- [Training budgets for pruning recovery and drafter distillation](../analyses/recovery-and-distillation-training-budgets.md)
- [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md)

[^agarwalOnPolicyDistillationLanguage2024]: Agarwal et al. 2024
