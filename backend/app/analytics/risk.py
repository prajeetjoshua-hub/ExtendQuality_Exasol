"""Descriptive inspection triage; never a failure probability or RUL model."""
from math import sqrt


def wilson_interval(rejected: int, eligible: int) -> tuple[float, float] | None:
    if eligible == 0:
        return None
    p, z = rejected / eligible, 1.96
    denominator = 1 + z * z / eligible
    center = (p + z * z / (2 * eligible)) / denominator
    width = z * sqrt(p * (1 - p) / eligible + z * z / (4 * eligible**2)) / denominator
    return max(0, center - width), min(1, center + width)


def assess_batch(total: int, eligible: int, rejected: int, daily: list[dict] | None = None) -> dict:
    if any(type(x) is not int for x in (total, eligible, rejected)) or not 0 <= rejected <= eligible <= total:
        raise ValueError("Counts must satisfy 0 <= rejected <= eligible <= total.")
    rate = rejected / eligible if eligible else None
    unknown = (total - eligible) / total if total else None
    result = {
        "method": "inspection-triage-v1", "score_type": "rule_based_score",
        "total": total, "eligible": eligible, "rejected": rejected,
        "reject_rate": rate, "unresolved_rate": unknown,
        "wilson_95": wilson_interval(rejected, eligible),
        "score": None, "level": "INSUFFICIENT_EVIDENCE", "trend": "insufficient_evidence",
        "reason": "At least 20 terminal dispositions are required; unresolved cases are not healthy.",
        "recommended_action": "Review unresolved cases and collect more independent inspections.",
        "limitations": "Descriptive effective-disposition triage (human decision when reviewed, otherwise model), not verified defect prevalence or failure probability. Repeated views violate independent-sample assumptions of the interval.",
    }
    if eligible < 20:
        return result
    score = round(100 * (0.8 * rate + 0.2 * unknown), 1)
    result.update(score=score, level="HIGH" if score >= 40 else "ELEVATED" if score >= 20 else "LOW",
                  reason=f"{rejected}/{eligible} terminal dispositions rejected; {total-eligible}/{total} unresolved. Score = 100 × (0.8 × reject rate + 0.2 × unresolved rate). Thresholds are uncalibrated demo policy.",
                  recommended_action="Increase sampling and have an inspector investigate surface/assembly evidence." if score >= 20 else "Continue controlled sampling; low score does not certify this batch.")
    periods = sorted(daily or [], key=lambda item: str(item["day"]))
    if len(periods) >= 2:
        previous, current = periods[-2:]
        for period in (previous, current):
            if not 0 <= int(period["rejected"]) <= int(period["eligible"]):
                raise ValueError("Invalid daily counts.")
        if min(int(previous["eligible"]), int(current["eligible"])) >= 20:
            delta = int(current["rejected"]) / int(current["eligible"]) - int(previous["rejected"]) / int(previous["eligible"])
            result.update(trend="rising" if delta > .05 else "falling" if delta < -.05 else "stable", change_percentage_points=round(delta * 100, 2))
            result["reason"] += " Trend compares the last two observed UTC days, not a forecast."
    return result
