import unittest
from datetime import date

from assessmentflow.core import (
    focus_recommendation,
    priority_score,
    remaining_hours,
    status_label,
    weekly_metrics,
)


class AssessmentFlowCoreTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 9, 25)
        self.near = {
            "id": "A001",
            "unit": "ISYS5002",
            "title": "Programming Project",
            "due_date": "2026-10-01",
            "weight": 40,
            "estimated_hours": 20,
            "progress": 50,
        }
        self.later = {
            "id": "A002",
            "unit": "DATA5001",
            "title": "Data Report",
            "due_date": "2026-10-20",
            "weight": 30,
            "estimated_hours": 10,
            "progress": 20,
        }

    def test_remaining_hours(self):
        self.assertEqual(remaining_hours(self.near), 10.0)

    def test_nearer_task_has_higher_priority_in_example(self):
        self.assertGreater(
            priority_score(self.near, self.today),
            priority_score(self.later, self.today),
        )

    def test_focus_recommendation(self):
        focus = focus_recommendation([self.later, self.near], self.today)
        self.assertIsNotNone(focus)
        self.assertEqual(focus["id"], "A001")

    def test_completed_status(self):
        completed = dict(self.near)
        completed["progress"] = 100
        self.assertEqual(status_label(completed, self.today), "COMPLETE")

    def test_weekly_metrics(self):
        data = {
            "assessments": [self.near, self.later],
            "sessions": [
                {
                    "assessment_id": "A001",
                    "date": "2026-09-25",
                    "minutes": 90,
                    "note": "Testing",
                }
            ],
            "settings": {"daily_capacity_hours": 3.0},
        }
        metrics = weekly_metrics(data, self.today)
        self.assertEqual(metrics["study_minutes_last_7"], 90)
        self.assertEqual(len(metrics["due_next_7"]), 1)
        self.assertEqual(metrics["due_next_7"][0]["id"], "A001")


if __name__ == "__main__":
    unittest.main()
