# Results

* [Discarding context at interceptions costs 37-40% of model forwarding time](recomputation-share-of-forwarding-time.md) - InferCept measures that recomputing discarded context takes 37-40% of total model forwarding time on a mixed augmented-LLM workload.
* [Speculative decoding speedup falls from 2.73× to 1.31× as batch size grows from 1 to 32](speculative-decoding-speedup-vs-batch-size.md) - Su et al. measure that the speedup of speculative decoding shrinks as batch size grows and that the best speculation length gets shorter.
* [Test-time scaling with a verifier raises SWE-bench Verified scores above single-attempt scores](swe-bench-verified-test-time-scaling.md) - R2E-Gym and SWE-RM both report large gains on SWE-bench Verified from selecting among many rollouts with a verifier.
* [WebRL lifts open models to 42.4-49.1 average success rate on WebArena-Lite](webrl-webarena-lite.md) - WebRL trains Llama3.1 and GLM-4 web agents to 42.4-49.1 average success rate on WebArena-Lite, above GPT-4-Turbo at 17.6.
