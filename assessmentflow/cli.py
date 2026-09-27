"""Interactive command-line interface for AssessmentFlow."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from .core import (
    days_until,
    focus_recommendation,
    parse_date,
    priority_score,
    remaining_hours,
    sort_by_priority,
    status_label,
    weekly_metrics,
)
from .storage import load_data, next_id, save_data


def line() -> None:
    print("-" * 78)


def prompt_nonempty(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Please enter a value.")


def prompt_float(label: str, minimum: float, maximum: float) -> float:
    while True:
        raw = input(label).strip()
        try:
            value = float(raw)
        except ValueError:
            print("Enter a number.")
            continue
        if minimum <= value <= maximum:
            return value
        print(f"Enter a value from {minimum:g} to {maximum:g}.")


def prompt_int(label: str, minimum: int, maximum: int) -> int:
    while True:
        raw = input(label).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Enter a whole number.")
            continue
        if minimum <= value <= maximum:
            return value
        print(f"Enter a whole number from {minimum} to {maximum}.")


def prompt_date(label: str) -> str:
    while True:
        value = input(label).strip()
        try:
            parse_date(value)
            return value
        except ValueError:
            print("Use YYYY-MM-DD, for example 2026-10-09.")


def find_assessment(data: Dict[str, Any], assessment_id: str) -> Optional[Dict[str, Any]]:
    assessment_id = assessment_id.strip().upper()
    for item in data.get("assessments", []):
        if str(item.get("id", "")).upper() == assessment_id:
            return item
    return None


def print_assessments(data: Dict[str, Any]) -> None:
    items = sort_by_priority(data.get("assessments", []))
    line()
    print("ASSESSMENTS - highest planning priority first")
    line()
    if not items:
        print("No assessments recorded yet.")
        return

    header = (
        f"{'ID':<5} {'UNIT':<11} {'DUE':<10} {'DAYS':>5} {'WT%':>5} "
        f"{'PROG%':>6} {'LEFT(h)':>7} {'SCORE':>6} {'STATUS':<10} TITLE"
    )
    print(header)
    print("-" * len(header))
    for item in items:
        days = days_until(str(item["due_date"]))
        print(
            f"{item['id']:<5} {str(item['unit'])[:11]:<11} {item['due_date']:<10} "
            f"{days:>5} {float(item['weight']):>5.1f} {float(item['progress']):>6.1f} "
            f"{remaining_hours(item):>7.1f} {priority_score(item):>6.1f} "
            f"{status_label(item):<10} {item['title']}"
        )


def add_assessment(data: Dict[str, Any], data_path: Path) -> None:
    line()
    print("ADD ASSESSMENT")
    unit = prompt_nonempty("Unit code: ").upper()
    title = prompt_nonempty("Assessment title: ")
    due_date = prompt_date("Due date (YYYY-MM-DD): ")
    weight = prompt_float("Weight percentage (0-100): ", 0.0, 100.0)
    estimated_hours = prompt_float("Estimated total study hours (0-500): ", 0.0, 500.0)
    progress = prompt_float("Current progress percentage (0-100): ", 0.0, 100.0)

    item = {
        "id": next_id(data),
        "unit": unit,
        "title": title,
        "due_date": due_date,
        "weight": round(weight, 1),
        "estimated_hours": round(estimated_hours, 1),
        "progress": round(progress, 1),
        "created": date.today().isoformat(),
    }
    data.setdefault("assessments", []).append(item)
    save_data(data_path, data)
    print(f"Saved {item['id']} - {unit} {title}.")


def update_progress(data: Dict[str, Any], data_path: Path) -> None:
    print_assessments(data)
    if not data.get("assessments"):
        return
    item = find_assessment(data, input("Assessment ID to update: "))
    if not item:
        print("Assessment not found.")
        return
    new_progress = prompt_float("New progress percentage (0-100): ", 0.0, 100.0)
    item["progress"] = round(new_progress, 1)
    save_data(data_path, data)
    print(f"Updated {item['id']} to {new_progress:.1f}%.")


def log_session(data: Dict[str, Any], data_path: Path) -> None:
    print_assessments(data)
    if not data.get("assessments"):
        return
    item = find_assessment(data, input("Assessment ID studied: "))
    if not item:
        print("Assessment not found.")
        return
    session_date = input(f"Session date [{date.today().isoformat()}]: ").strip() or date.today().isoformat()
    try:
        parse_date(session_date)
    except ValueError:
        print("Invalid date. Session was not saved.")
        return
    minutes = prompt_int("Minutes studied (1-1440): ", 1, 1440)
    note = input("Short note (optional): ").strip()
    data.setdefault("sessions", []).append(
        {
            "assessment_id": item["id"],
            "date": session_date,
            "minutes": minutes,
            "note": note,
        }
    )
    save_data(data_path, data)
    print(f"Logged {minutes} minutes for {item['id']}.")


def show_focus(data: Dict[str, Any]) -> None:
    item = focus_recommendation(data.get("assessments", []))
    line()
    print("TODAY'S FOCUS")
    line()
    if not item:
        print("Everything is complete, or there are no assessments yet.")
        return
    print(f"Focus on: {item['id']} - {item['unit']} - {item['title']}")
    print(f"Due: {item['due_date']} ({days_until(str(item['due_date']))} day(s) from today)")
    print(f"Progress: {float(item['progress']):.1f}%")
    print(f"Estimated work remaining: {remaining_hours(item):.1f} hours")
    print(f"Priority score: {priority_score(item):.1f}/100")
    print("Why: the transparent score combines urgency (50%), assessment weight (25%),")
    print("and remaining work (25%). It is a planning aid that you can override.")


def show_weekly_insights(data: Dict[str, Any]) -> None:
    metrics = weekly_metrics(data)
    line()
    print("WEEKLY INSIGHTS")
    line()
    print(f"Study logged in last 7 days: {metrics['study_hours_last_7']:.1f} hours")
    print(f"Estimated work remaining across incomplete tasks: {metrics['remaining_hours_all']:.1f} hours")
    print(f"Indicative daily workload for next 7 days: {metrics['required_daily_hours_next_7']:.1f} hours/day")
    print(f"Your configured daily capacity: {metrics['daily_capacity_hours']:.1f} hours/day")
    print(f"Workload risk indicator: {metrics['workload_risk']}")
    print()
    if metrics["due_next_7"]:
        print("Due within 7 days:")
        for item in metrics["due_next_7"]:
            print(
                f"  {item['id']} {item['unit']} - {item['title']} - "
                f"{item['due_date']} - priority {priority_score(item):.1f}"
            )
    else:
        print("No incomplete assessment is due within the next 7 days.")


def set_capacity(data: Dict[str, Any], data_path: Path) -> None:
    current = float(data.get("settings", {}).get("daily_capacity_hours", 3.0))
    print(f"Current daily study capacity: {current:.1f} hours")
    capacity = prompt_float("New daily capacity (0.5-16 hours): ", 0.5, 16.0)
    data.setdefault("settings", {})["daily_capacity_hours"] = round(capacity, 1)
    save_data(data_path, data)
    print("Capacity updated.")


def export_csv(data: Dict[str, Any], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id",
        "unit",
        "title",
        "due_date",
        "weight",
        "estimated_hours",
        "progress",
        "remaining_hours",
        "priority_score",
        "status",
    ]
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in sort_by_priority(data.get("assessments", [])):
            writer.writerow(
                {
                    "id": item["id"],
                    "unit": item["unit"],
                    "title": item["title"],
                    "due_date": item["due_date"],
                    "weight": item["weight"],
                    "estimated_hours": item["estimated_hours"],
                    "progress": item["progress"],
                    "remaining_hours": remaining_hours(item),
                    "priority_score": priority_score(item),
                    "status": status_label(item),
                }
            )
    print(f"Exported summary to {destination}.")


def delete_assessment(data: Dict[str, Any], data_path: Path) -> None:
    print_assessments(data)
    if not data.get("assessments"):
        return
    item = find_assessment(data, input("Assessment ID to delete: "))
    if not item:
        print("Assessment not found.")
        return
    confirm = input(f"Type DELETE to remove {item['id']} and its study sessions: ").strip()
    if confirm != "DELETE":
        print("Deletion cancelled.")
        return
    data["assessments"] = [a for a in data["assessments"] if a.get("id") != item["id"]]
    data["sessions"] = [s for s in data.get("sessions", []) if s.get("assessment_id") != item["id"]]
    save_data(data_path, data)
    print(f"Deleted {item['id']}.")


def print_summary(data: Dict[str, Any]) -> None:
    print_assessments(data)
    print()
    show_focus(data)
    print()
    show_weekly_insights(data)


def run(data_path: Path) -> None:
    try:
        data = load_data(data_path)
    except (ValueError, OSError) as exc:
        print(f"Could not load data: {exc}")
        return

    actions = {
        "1": ("List assessments", lambda: print_assessments(data)),
        "2": ("Add assessment", lambda: add_assessment(data, data_path)),
        "3": ("Update progress", lambda: update_progress(data, data_path)),
        "4": ("Log study session", lambda: log_session(data, data_path)),
        "5": ("Show today's focus", lambda: show_focus(data)),
        "6": ("Show weekly insights", lambda: show_weekly_insights(data)),
        "7": ("Set daily study capacity", lambda: set_capacity(data, data_path)),
        "8": (
            "Export assessment summary to CSV",
            lambda: export_csv(data, Path("exports") / "assessment_summary.csv"),
        ),
        "9": ("Delete assessment", lambda: delete_assessment(data, data_path)),
    }

    while True:
        line()
        print("ASSESSMENTFLOW - Personal Assessment Sprint Planner")
        print(f"Data file: {data_path}")
        line()
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye. Your local data remains on this device.")
            return
        action = actions.get(choice)
        if not action:
            print("Choose a number from 0 to 9.")
            continue
        print()
        action[1]()
        input("\nPress Enter to continue...")
