"""Analyze JUnit XML test reports, without assuming the source is trusted."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .core import InvalidTrace

MAX_JUNIT_BYTES = 5_000_000


def summarize_junit(path: Path) -> dict[str, Any]:
    """Summarize test outcomes from local JUnit XML.

    This is a record of XML contents, not proof that tests actually ran.
    The caller is responsible for verifying provenance of the test artifact.
    """
    if not path.is_file():
        raise InvalidTrace("JUnit path must identify an existing regular file.")
    if path.stat().st_size > MAX_JUNIT_BYTES:
        raise InvalidTrace("JUnit XML is too large.")
    # Refuse DTD/entity declarations: there is no reason to expand them in
    # test summaries, and this avoids XML entity amplification.
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise InvalidTrace(f"Could not read JUnit XML: {type(exc).__name__}") from exc
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise InvalidTrace("DTD and entity declarations are not supported.")
    try:
        xml = ET.fromstring(raw)
    except (ET.ParseError, OSError) as exc:
        raise InvalidTrace(f"Invalid JUnit XML: {type(exc).__name__}") from exc
    if xml.tag not in ("testsuite", "testsuites"):
        raise InvalidTrace("JUnit XML root must be testsuite or testsuites.")
    suites = [xml] if xml.tag == "testsuite" else list(xml.iter("testsuite"))
    cases = []
    for suite in suites:
        for case in suite.findall("testcase"):
            name = case.get("name")
            if not isinstance(name, str) or not name.strip():
                raise InvalidTrace("Every JUnit testcase must have a nonempty name.")
            status = (
                "error" if case.find("error") is not None
                else "failed" if case.find("failure") is not None
                else "skipped" if case.find("skipped") is not None
                else "passed"
            )
            cases.append({"name": name, "classname": case.get("classname"), "status": status})
    totals = {name: sum(c["status"] == name for c in cases) for name in ("passed", "failed", "error", "skipped")}
    return {
        "testcases": len(cases),
        "passed": totals["passed"],
        "failed": totals["failed"],
        "errors": totals["error"],
        "skipped": totals["skipped"],
        "all_testcases_pass": bool(cases) and totals["failed"] == 0 and totals["error"] == 0 and totals["skipped"] == 0,
        "evidence_level": "supplied_xml_contents_only",
        "provenance_verified": False,
    }
