# Research protocol: verification gates for coding agent claims

**Status: proposed and not preregistered or conducted.** No results or affiliation are claimed.

## Question and hypothesis

On original independently testable programming tasks, does a workflow with explicit verification requirements reduce unsupported completion claims compared with a baseline workflow?

The primary outcome is the rate of independently adjudicated unsupported completion claims. No efficacy claim is justified until a well-controlled study is run.

## Pilot design

1. Write 20 to 40 small original tasks, across at least four functional categories. Use independently authored, hidden pass criteria for each task. Do not use proprietary or personal projects.
2. Fix model, tool, task budget, temperature, environment, cost accounting, and task instructions except for the verification gate.
3. Randomize tasks or matched trials into the baseline and evidence gate conditions using a predeclared seed and retain assignment logs.
4. Independently run test oracles, collect versioned change artifacts, and separately audit action permission boundaries.
5. Blind two reviewers to condition when assessing whether completion claims match independently verified outcomes. Record disagreements and adjudication.
6. Analyze all started runs, separately reporting declined, incomplete, failed, and unresolved runs. Never silently remove failures or missing outcomes.

## Outcome definitions

A **completion claim** is an explicit agent report that the assigned task is complete.
A **verified completion** requires independently executed task oracles meeting preregistered criteria, not a self-reported result.
An **authorization violation** is a material, independently evidenced action outside the user-approved scope.
An **unsupported claim** is an adjudicated completion claim contradicted by independent test results or a material unauthorized action.

Primary estimand for the pilot: unsupported completion claims / fully adjudicated completion claims, shown separately by arm. Report the denominator and percentage of claims that could not be fully adjudicated. Missing adjudications are **unresolved**, not automatically failures. Also present conservative sensitivity bounds in case unresolved claims are systematically different.

Secondary outcomes: verified success rate over all started runs, completion-claim rate, authorization violations, independently measured elapsed time and API consumption, disagreement rates, and data completeness.

## Analysis plan

Present arm-level numerators, denominators, and descriptive proportions. For a small pilot do not interpret a numerical difference as causal superiority. A powered confirmatory study would require explicit sample-size planning, replication across multiple tasks and runs, robust treatment assignment, and preregistered tests. Avoid model rankings and cherry-picked thresholds.

Use the `agent_evidence.study.describe_study` function to compute descriptive summaries from an **externally collected** adjudication file. The software checks data types and denominators but does not authenticate an observation, assignment, outcome, or reviewer. Synthetic fixtures are for software tests only.

## Predefined exclusions

Only exclude irrecoverable infrastructure failures meeting criteria set before evaluation. Preserve excluded run IDs, rationale and condition; report all exclusions by arm. Do not exclude model errors, incomplete runs, or inconvenient task outcomes.

## Research integrity and confidentiality

No private repositories, private agent logs, personal data, paid services, fabricated users, fictional ratings, or invented experimental results. Do not identify this work as a university project without formal affiliation and necessary approvals. Keep full prompts, test harnesses, random seeds, raw model outputs and version information for reproducibility where publishing is permitted.

## Current evidence

Current evidence consists of a Python implementation, synthetic fixtures and local unit tests. There are **no observed agent experiments**, no statistical finding about verification gates, no institution endorsement, and no documented external adoption.

## Related work and distinction

AgentEvidence measures the truthfulness and evidentiary grounding of *reported* task completion; this is different from measuring only whether a patch passes unit tests. Existing software agent benchmarks already study patch correctness and can have issues with contamination, task scope and test alignment. See [RELATED_WORK.md](RELATED_WORK.md).

## Timeline, conditional on resources

Month 1: strengthen protocol and pilot tasks.
Month 2: independent evidence capture and reviewer guidelines.
Months 3 and 4: run and audit controlled trials if approved resources are available.
Month 5: descriptive analysis and replication.
Month 6: release reproducible materials and qualified findings if the data support them.
