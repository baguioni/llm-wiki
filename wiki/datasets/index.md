# Datasets

* [ALFWorld](alfworld.md) - Suite of text-based interactive environments for multi-step household tasks, used in the wiki's papers to test agent decision-making and to generate an agent serving workload.
* [Alpaca](alpaca.md) - Instruction-following prompt set that the wiki's speculative-decoding papers use for measuring speedup and acceptance length.
* [BIG-Bench Hard (BBH)](bbh.md) - Suite of 23 BIG-Bench tasks on which PaLM 540B scores below average human raters, used in the wiki's papers as a held-out test for task-agnostic distillation and for the transfer of a distilled draft model.
* [C4](c4.md) - Text corpus used in the wiki's papers as a prompt source for speculative decoding speed tests, and one of the seven domains of RedPajama.
* [Chatbot Instruction Prompts](chatbot-instruction-prompts.md) - Huggingface dataset of general assistant-style prompts that two of the wiki's papers use as an input stream for speculative-decoding serving experiments.
* [CNN/Daily Mail](cnn-dailymail.md) - News summarization dataset, used in the wiki's papers as the summarization workload for measuring speculative decoding speedup.
* [Evol-CodeAlpaca](evol-codealpaca.md) - Code instruction dataset that the PARD papers combine with Magpie to train parallel draft models.
* [FineWeb](fineweb.md) - Web text corpus whose 100B-token sample (sample-100BT) Osprey uses for target-agnostic next-token pretraining of its pruned drafter backbone.
* [GSM8K](gsm8k.md) - Grade-school math word problem dataset that the wiki's papers use as a math prompt set for speculative-decoding speed measurements and as a math accuracy test.
* [HellaSwag](hellaswag.md) - Commonsense completion dataset, used in the wiki's papers as an accuracy test for compressed and on-device models and as a prompt source for speed measurements.
* [HotpotQA](hotpotqa.md) - Wikipedia-based multi-hop question answering dataset, used in the wiki's papers to test agent reasoning and to generate agent serving workloads.
* [HumanEval](humaneval.md) - Code generation benchmark that the wiki's papers use as a coding prompt set for speculative-decoding speed measurements and as a pass@1 accuracy test.
* [InfiniteBench](infinitebench.md) - Long-context evaluation suite beyond 100K tokens whose English novel summarization task (En.Sum, written ∞Bench Sum) HyCo uses, truncated to 32K tokens, as its long-input speculative-decoding workload.
* [LiveCodeBench](livecodebench.md) - Code benchmark that the wiki's speculative-decoding papers use as a coding prompt set for measuring speedup and acceptance length.
* [Magpie](magpie.md) - Synthetic instruction dataset that the PARD papers use, with regenerated answers, to train parallel draft models.
* [MATH-500](math-500.md) - Math problem set that the wiki's speculative-decoding papers use as a prompt set for measuring speedup and acceptance length.
* [MBPP](mbpp.md) - Code generation benchmark used in the wiki's papers as a coding prompt set for speculative-decoding speed measurements and as a pass@1 accuracy test.
* [MMLU](mmlu.md) - Multiple-choice benchmark with 57 subtasks, used in the wiki's papers as an accuracy test for compressed, agentic, and fine-tuned LLMs and as a prompt source for speed measurements.
* [MT-Bench](mt-bench.md) - Multi-turn conversation benchmark that the wiki's papers use mostly as a chat prompt set for speculative-decoding speed measurements, and once as a quality score.
* [Multi-Session Chat](multi-session-chat.md) - Dataset of multi-session, persona-consistent chat logs written by human labelers, which MemGPT extends into the deep memory retrieval and conversation opener tasks.
* [Nemotron Post-Training Dataset](nemotron-post-training.md) - NVIDIA post-training dataset (v2, and possibly v3) that DFlash, PARD-2, and Osprey use as training data for draft models or a draft warm-start model.
* [Open-PerfectBlend](perfectblend.md) - Mixed chat, math, code, and instruction-following conversation dataset that the wiki's papers use to train speculative-decoding draft models.
* [OpenThoughts-114k](openthoughts.md) - Reasoning dataset that PARD and EAGLE-3 use to train draft models for DeepSeek-R1-distilled reasoning targets.
* [R2E-Gym](r2e-gym.md) - Procedurally curated gym of 8,135 executable software engineering tasks built from GitHub commits with generated tests and back-translated issues, used to train SWE agents and verifiers.
* [RedPajama](redpajama.md) - Replicated pre-training dataset of the LLaMA1 models with seven domains, used in the wiki's papers as the data for structured pruning and continued pre-training.
* [ShareGPT](sharegpt.md) - Dataset of real user conversations with ChatGPT, used in the wiki's papers as a chatbot serving trace and as training data for draft models and instruction tuning.
* [Spider](spider.md) - Text-to-SQL dataset that two of the wiki's papers use as a structured-output workload for speculative-decoding experiments under distribution shift.
* [SWE-Gym](swe-gym.md) - Training environment of executable GitHub issue-resolution tasks with human-written issues and tests, used in the wiki's papers as a training source, a baseline model family, and a verifier baseline.
* [TOPv2](topv2.md) - Multi-domain task-oriented compositional semantic parsing dataset, used by LayerSkip to finetune a 1.5B Llama model and measure early exit and self-speculative decoding by exact match.
* [UltraChat](ultrachat.md) - Instructional conversation dataset (used as UltraChat-200K) that the wiki's papers pair with ShareGPT to train speculative-decoding draft models, including the official EAGLE-3 drafters.
* [WikiText-2](wikitext-2.md) - Text dataset used in the wiki's papers as a prompt source for speculative decoding speed tests, as a perplexity test set for quantization, and as a calibration set for layer pruning.
* [WMT14 en-de](wmt14-en-de.md) - WMT 2014 English-to-German machine translation task, scored with BLEU, used in the wiki's papers to test knowledge distillation of T5 students and draft models.
* [XSum](xsum.md) - Extreme Summarization dataset of BBC news articles, used in the wiki's papers to measure speculative decoding speedup and ROUGE-2.
