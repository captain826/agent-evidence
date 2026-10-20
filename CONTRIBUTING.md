# Contributing

The project is at an early stage. Outside contributions and broad adoption are not claimed.

## Before contributing

Please keep changes narrow, propose an independently testable problem, and include a synthetic reproduction. No credentials, proprietary code, private execution traces, personal data, or unconsented real user records.

## Run the test suite

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

For a code change, include at least one regression test that fails before the fix and passes after it. Explain assumptions about the authenticity of supplied evidence.

## Good starter tasks (draft proposals)

* Improve actionable input validation for malformed trace structures.
* Add schema versioning with backward compatibility tests.
* Document integration recipes for existing CI artifacts.
* Add robustness tests for malformed or large JUnit XML.

These are ideas only. No public issues or contributor invitations have been posted.
