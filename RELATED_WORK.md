# Related work and novelty boundary

This is a selective reading list, **not** a claim of exhaustive novelty. Before submitting a research paper, run a systematic literature review.

1. [SWE-bench Verified (OpenAI, 2024)](https://openai.com/index/introducing-swe-bench-verified/). Provides human-vetted tests and issue resolution evaluation. The benchmark evaluates task completion rather than an agent's self-reported evidence.
2. [Why we no longer evaluate SWE-bench Verified (OpenAI, February 2026)](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/). Describes contamination concerns and tests that can reject valid solutions. This motivates independent validation and careful task design but does not validate AgentEvidence.
3. [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents (Zheng et al., September 2026)](https://arxiv.org/abs/2609.08149). Studies evaluation integrity and task quality. It is related work, not evidence that AgentEvidence is novel or superior.

## Proposed, narrower contribution

Distinguish a coding agent's claimed completion and declared evidence from independently adjudicated task outcomes. Surface unclear or missing evidence explicitly, rather than classifying it as success or failure without verification.

## Unresolved research questions

How should partial correctness and authorized deviations be judged? Can independent evidence capture itself be subverted? Does requiring evidence change task success, cost, or completion-claim frequency? How should incomplete or censored runs affect reported rates?

No peer reviewed publication, academic affiliation, or experimental results are claimed.
