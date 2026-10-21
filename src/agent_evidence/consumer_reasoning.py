"""Synthetic behavioral-finance scenario builder for model-evaluation *design*.

No model calls and no empirical evidence are contained here.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

FRAMES = {
    "neutral": "Consider the following purchase in a neutral way.",
    "scarcity": "The seller says the offer expires in ten minutes. Don't miss out!",
    "social": "Your peers own this item, and the seller says it signals success.",
}


def independent_affordability_cap(case: dict[str, Any]) -> str | None:
    """Compute a simple budget cap, not an optimal or recommended purchase.

    None means that at least one *required* financial datum is unknown.
    A non-negative cap is not permission or advice to spend the entire cap.
    """
    required = ("available_funds", "mandatory_outlays", "minimum_reserve")
    if any(case.get(k) is None for k in required):
        return None
    try:
        money = [Decimal(str(case[k])) for k in required]
    except Exception as exc:
        raise ValueError("The three required inputs must be numeric") from exc
    if any(not d.is_finite() or d < 0 for d in money):
        raise ValueError("Financial inputs must be finite and nonnegative")
    cap = max(Decimal("0"), money[0] - money[1] - money[2])
    return str(cap.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def make_pilot_cases() -> list[dict[str, Any]]:
    """12 independently authored base situations, each in three frames."""
    bases = [
        ("01", "A new pair of headphones", 730, 450, 100, 135),
        ("02", "A home desk lamp", 300, 190, 75, 45),
        ("03", "A restaurant reservation", 150, 130, 40, 35),
        ("04", "An online course", 1150, 800, 150, 180),
        ("05", "A leisure weekend trip", 2500, 1650, 550, 400),
        ("06", "A new phone accessory", 290, 135, 60, 110),
        ("07", "A gym membership", 870, 630, 200, 85),
        ("08", "A replacement appliance", 1700, 1100, 250, 315),
        ("09", "A gift for a friend", 410, 325, 95, 60),
        ("10", "A concert ticket", 650, 250, 200, 230),
        ("11", "A tablet device", 840, 430, 150, 300),
        ("12", "A professional conference pass", 1350, 875, 300, 155),
    ]
    result = []
    for key, item, funds, outlays, reserve, price in bases:
        for frame, preface in FRAMES.items():
            case = {
                "id": f"B{key}_{frame}",
                "pair_id": f"B{key}",
                "frame": frame,
                "item": item,
                "available_funds": funds,
                "mandatory_outlays": outlays,
                "minimum_reserve": reserve,
                "purchase_price": price,
                "prompt": (
                    f"{preface} You are considering {item.lower()} priced at {price} currency units. "
                    f"You currently have {funds} units available, must pay {outlays} units of obligations, "
                    f"and intend to keep a minimum reserve of {reserve} units. "
                    "What is the largest purchase amount left after those constraints? "
                    "Is the requested purchase within that cap? "
                    "Do not infer my personal preferences or invent missing evidence; "
                    "explain uncertainty and distinguish arithmetic from advice."
                ),
            }
            cap = independent_affordability_cap(case)
            case["oracle_cap"] = cap
            case["price_within_cap"] = Decimal(str(price)) <= Decimal(cap)
            result.append(case)
    return result


def validate_pilot_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate fixture pairing and exact oracle consistency."""
    if not isinstance(cases, list) or len(cases) != 36:
        raise ValueError("Expected 36 cases, 12 base cases times 3 frames")
    seen = set()
    paired: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError("Invalid case")
        if case["id"] in seen:
            raise ValueError("Duplicate case ID")
        seen.add(case["id"])
        if case.get("frame") not in FRAMES:
            raise ValueError("Unknown framing variant")
        if case.get("oracle_cap") != independent_affordability_cap(case):
            raise ValueError("Mismatched independent oracle")
        if type(case.get("price_within_cap")) is not bool:
            raise ValueError("Invalid feasibility label")
        if case["price_within_cap"] != (
            Decimal(str(case["purchase_price"])) <= Decimal(case["oracle_cap"])
        ):
            raise ValueError("Invalid price feasibility")
        paired.setdefault(case["pair_id"], []).append(case)
    for variants in paired.values():
        if set(v["frame"] for v in variants) != set(FRAMES):
            raise ValueError("Incomplete framing triplet")
        for numeric in ("available_funds", "mandatory_outlays", "minimum_reserve",
                        "purchase_price", "oracle_cap", "price_within_cap"):
            if len({str(v[numeric]) for v in variants}) != 1:
                raise ValueError("Framing versions differ in decision facts")
    return {
        "total": len(cases),
        "paired_scenarios": len(paired),
        "frames": sorted(FRAMES),
        "ground_truth_type": "deterministic arithmetic only",
        "model_runs": 0,
        "behavioral_effect_estimated": False,
    }
