import unittest

from backend.learning_engine.feedback import build_feedback


class OpportunityFeedbackTests(unittest.TestCase):
    def test_not_relevant_requires_reason(self):
        with self.assertRaises(ValueError):
            build_feedback("opportunity", "user", "not_relevant")

    def test_details_are_trimmed_and_bounded(self):
        result = build_feedback("opportunity", "user", "not_relevant", "other", "  " + "x" * 600)
        self.assertEqual(500, len(result["details"]))

    def test_saved_feedback_does_not_require_reason(self):
        result = build_feedback("opportunity", "user", "saved")
        self.assertIsNone(result["reason"])


if __name__ == "__main__":
    unittest.main()
