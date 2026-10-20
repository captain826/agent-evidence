"""Descriptive outcomes for independently adjudicated agent runs.

The code never determines if external observations are independent.
Researchers must authenticate provenance and preregister their study design.
"""
from __future__ import annotations

from typing import Any
from .core import InvalidTrace

ARMS = {"baseline", "evidence_gate"}


def describe_study(dataset: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(dataset, dict) or not isinstance(dataset.get("runs"), list):
        raise InvalidTrace("A study dataset must contain an array of runs.")
    runs = dataset["runs"]
    seen = set()
    for entry in runs:
        if not isinstance(entry, dict):
            raise InvalidTrace("Every study run must be a JSON object.")
        rid = entry.get("run_id")
        if not isinstance(rid, str) or not rid.strip() or rid in seen:
            raise InvalidTrace("Study run IDs must be unique and nonempty.")
        seen.add(rid)
        if not isinstance(entry.get("arm"), str) or entry["arm"] not in ARMS:
            raise InvalidTrace("Study arm must be baseline or evidence_gate.")
        if type(entry.get("completion_claimed")) is not bool:
            raise InvalidTrace("completion_claimed must be Boolean.")
        for key in ("verified_completion", "approved_actions"):
            if entry.get(key) is not None and type(entry.get(key)) is not bool:
                raise InvalidTrace(f"{key} must be Boolean or null.")

    def bucket(sample: list[dict[str, Any]]) -> dict[str, Any]:
        claims = [r for r in sample if r["completion_claimed"]]
        adjudicated = [r for r in claims
                       if r.get("verified_completion") is not None
                       and r.get("approved_actions") is not None]
        unresolved = len(claims) - len(adjudicated)
        unsupported = sum(
            not (r["verified_completion"] and r["approved_actions"])
            for r in adjudicated
        )
        positive = sum(r.get("verified_completion") is True for r in sample)
        return {
            "runs": len(sample),
            "completion_claims": len(claims),
            "adjudicated_claims": len(adjudicated),
            "unresolved_claims": unresolved,
            "unsupported_adjudicated_claims": unsupported,
            "unsupported_claim_rate_among_adjudicated": (
                unsupported / len(adjudicated) if adjudicated else None
            ),
            "verified_completions": positive,
            "observations_missing_verified_completion": sum(
                r.get("verified_completion") is None for r in sample
            ),
        }
    return {
        "summary": bucket(runs),
        "arms": {arm: bucket([r for r in runs if r["arm"] == arm]) for arm in sorted(ARMS)},
        "data_status": "externally supplied adjudications, not authenticated by this software",
        "causal_claims_supported": False,
        "interpretation": (
            "Descriptive results only. A causal estimate requires verified randomization, "
            "independent outcome collection and an appropriate predeclared analysis."
        ),
    }
