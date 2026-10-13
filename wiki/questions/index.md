# Open Questions

* [Does offloading the KV cache to CPU memory help agentic workloads?](kv-cache-offloading-for-agent-workloads.md) - Agent-serving papers disagree on whether moving idle KV cache off the GPU during tool calls improves throughput.
* [Does speculative decoding still help at large batch sizes?](speculative-decoding-at-large-batch.md) - Papers disagree on whether speculative decoding keeps a speedup above 1 when the server batches many requests.
* [Is Deep Memory Retrieval an adequate benchmark for agent memory?](deep-memory-retrieval-adequacy.md) - MemGPT presents Deep Memory Retrieval as evidence that a memory system is needed, while Zep shows a full-conversation baseline that matches it.
* [Should agent training environments verify tasks with code or with an LLM judge?](code-verification-vs-llm-judge.md) - VeriEnv argues for deterministic code validators and Agent World Model argues that code-only verification is brittle.
* [What is the GSM8K score of Sheared-LLaMA 2.7B?](sheared-llama-gsm8k-discrepancy.md) - Two papers report GSM8K scores for Sheared-LLaMA 2.7B that differ widely (2.7 and 23.96).
* [Which SWE-bench Verified scores are comparable?](swe-bench-verified-comparability.md) - Papers quote the same systems on SWE-bench Verified with different scores and different rollout budgets.
* [Why do reported EAGLE-3 numbers differ so much between papers?](eagle-3-baseline-variance.md) - EAGLE-3 speedup and acceptance length for the same target model differ widely across the papers that re-measure it.
