# AgentEvidence

A small, dependency-free Python tool for **trace-level audits** of coding agents' completion claims.

When an agent declares that a software task is finished, AgentEvidence checks whether its own structured report names passing required checks and records actions that are authorized and in scope. It makes no attempt to verify that the tests really ran: for that, use an independent runner with signed or independently captured logs.

## Why this exists

An agent saying "done" is not the same as independent verification. This project makes that distinction explicit and measurable for future controlled experiments. The included examples are synthetic and are **not** research findings or evidence of real-world adoption.

## Try it

Requires Python 3.10 or later. No API keys or paid services.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m agent_evidence.cli examples/synthetic_runs.json
```

For installation into a fresh environment:

```bash
python3 -m pip install -e .
agent-evidence examples/synthetic_runs.json --output report.json
```

## Input contract

Provide a JSON object with a `runs` array. Each run must have a unique `run_id`, a Boolean `completion_claimed`, a `required_checks` array of check names, a `checks` array of objects with `name` and `status` (passed, failed, skipped), and an `actions` array. Each action declares `name`, `external`, `authorized`, and `in_scope` explicitly.

`trace_supports_claim` means internal consistency, not that source code, execution, or permissions were externally verified. Missing required checks, failed/skipped checks, unauthorized actions of any kind, or out of scope actions prevent a claim from being marked as trace supported.

## Research direction

See [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) for a proposed controlled experiment. No participants have been enrolled, no study has been completed, and no scientific impact has been claimed.

## Contribution and safety

Synthetic datasets are welcome. Do not submit API tokens, private code, credentials, personal data, or nonpublic agent traces. Contributions are reviewed before merging. See [CONTRIBUTING.md](CONTRIBUTING.md).

Licensed under the MIT License.


## Verify artifact integrity

You can optionally pass `--manifest examples/evidence/manifest.json --artifact-root examples/evidence` when running the CLI to verify that locally available files match recorded SHA256 values and sizes. A successful integrity check does not prove who ran the test or that a particular test passed. Full source provenance requires independently captured logs and an external adjudication protocol.

```bash
PYTHONPATH=src python3 -m agent_evidence.cli examples/synthetic_runs.json --manifest examples/evidence/manifest.json --artifact-root examples/evidence
```


## Inspect a JUnit XML report

AgentEvidence can also summarize a supplied JUnit XML artifact. This helps compare reported test outcomes with a structured test report, but **does not prove** the XML originated from a real or independent test run.

```bash
PYTHONPATH=src python3 -m agent_evidence.cli examples/synthetic_runs.json --junit examples/test_reports/synthetic_suite.xml
```

Never treat the SHA256 verification or XML summaries as cryptographic attestation of a test run. They validate supplied content, not the source or independence of that content.

## Descriptive study analysis

For a controlled research study, the optional `--study` flag accepts a JSON file of externally adjudicated runs. It reports the number of claims, fully adjudicated claims, unresolved claims and the rate of unsupported claims among those fully adjudicated, broken down by study arm. The code **does not** validate assignment, authenticity, independence, blindness or causality.

```bash
PYTHONPATH=src python3 -m agent_evidence.cli examples/synthetic_runs.json --study examples/study/synthetic_adjudications.json
```

The example is synthetic. Its numerical output is a test of the analysis pipeline, **not evidence** that verification gates improve agent reliability.


## Responsible research and contributions

Read [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) and [RELATED_WORK.md](RELATED_WORK.md) for the proposed controlled study and the limitations of the evidence model. Read [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

**Status:** prototype suitable for experimental inspection, not an independently validated research instrument or verified execution attestation.
