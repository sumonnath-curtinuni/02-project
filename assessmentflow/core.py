"""Core calculations for AssessmentFlow.

The functions in this module contain no input/output code so they are easy to test.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional

DATE_FORMAT = "%Y-%m-%d"


def parse_date(value: str) -> date:
    """Parse an ISO date (YYYY-MM-DD) or raise ValueError."""
    return datetime.strptime(value.strip(), DATE_FORMAT).date()


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def days_until(due_date: str, today: Optional[date] = None) -> int:
    today = today or date.today()
    return (parse_date(due_date) - today).days


def remaining_hours(assessment: Dict[str, Any]) -> float:
    estimated = float(assessment.get("estimated_hours", 0.0))
    progress = clamp(float(assessment.get("progress", 0.0)), 0.0, 100.0)
    return round(max(0.0, estimated * (1.0 - progress / 100.0)), 1)


def priority_score(assessment: Dict[str, Any], today: Optional[date] = None) -> float:
    """Return a transparent 0-100 heuristic priority score.

    The score combines:
    - urgency (50%): nearer dates score higher,
    - assessment weight (25%), and
    - remaining work (25%).

    Overdue tasks receive a small capped boost. This is a planning aid, not a
    scientific or institutional grading formula.
    """
    today = today or date.today()
    days = days_until(str(assessment["due_date"]), today)

    if days < 0:
        urgency = 100.0
    else:
        urgency = 100.0 - clamp(days, 0.0, 30.0) * (100.0 / 30.0)

    weight = clamp(float(assessment.get("weight", 0.0)), 0.0, 100.0)
    progress = clamp(float(assessment.get("progress", 0.0)), 0.0, 100.0)
    work_left = 100.0 - progress

    score = 0.50 * urgency + 0.25 * weight + 0.25 * work_left
    if days < 0:
        score += 10.0
    return round(clamp(score, 0.0, 100.0), 1)


def status_label(assessment: Dict[str, Any], today: Optional[date] = None) -> str:
    days = days_until(str(assessment["due_date"]), today)
    progress = float(assessment.get("progress", 0.0))
    if progress >= 100.0:
        return "COMPLETE"
    if days < 0:
        return "OVERDUE"
    if days == 0:
        return "DUE TODAY"
    if days <= 3:
        return "DUE SOON"
    return "ACTIVE"


def sort_by_priority(
    assessments: Iterable[Dict[str, Any]], today: Optional[date] = None
) -> List[Dict[str, Any]]:
    today = today or date.today()
    return sorted(
        list(assessments),
        key=lambda item: (
            -priority_score(item, today),
            parse_date(str(item["due_date"])),
            str(item.get("unit", "")),
        ),
    )


def focus_recommendation(
    assessments: Iterable[Dict[str, Any]], today: Optional[date] = None
) -> Optional[Dict[str, Any]]:
    today = today or date.today()
    incomplete = [a for a in assessments if float(a.get("progress", 0.0)) < 100.0]
    ordered = sort_by_priority(incomplete, today)
    return ordered[0] if ordered else None


def sessions_in_window(
    sessions: Iterable[Dict[str, Any]],
    start: date,
    end: date,
) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    for session in sessions:
        try:
            session_date = parse_date(str(session["date"]))
        except (KeyError, ValueError):
            continue
        if start <= session_date <= end:
            output.append(session)
    return output


def weekly_metrics(data: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
    today = today or date.today()
    assessments = list(data.get("assessments", []))
    sessions = list(data.get("sessions", []))

    week_end = today + timedelta(days=7)
    due_next_7 = [
        a
        for a in assessments
        if 0 <= days_until(str(a["due_date"]), today) <= 7
        and float(a.get("progress", 0.0)) < 100.0
    ]

    start = today - timedelta(days=6)
    recent_sessions = sessions_in_window(sessions, start, today)
    studied_minutes = sum(int(s.get("minutes", 0)) for s in recent_sessions)

    incomplete = [a for a in assessments if float(a.get("progress", 0.0)) < 100.0]
    total_remaining = round(sum(remaining_hours(a) for a in incomplete), 1)
    active_days = max(1, min(7, (week_end - today).days))
    required_daily_hours = round(total_remaining / active_days, 1)
    capacity = float(data.get("settings", {}).get("daily_capacity_hours", 3.0))

    if required_daily_hours > capacity * 1.5:
        workload_risk = "HIGH"
    elif required_daily_hours > capacity:
        workload_risk = "MEDIUM"
    else:
        workload_risk = "LOW"

    return {
        "due_next_7": sort_by_priority(due_next_7, today),
        "study_minutes_last_7": studied_minutes,
        "study_hours_last_7": round(studied_minutes / 60.0, 1),
        "remaining_hours_all": total_remaining,
        "required_daily_hours_next_7": required_daily_hours,
        "daily_capacity_hours": capacity,
        "workload_risk": workload_risk,
    }
