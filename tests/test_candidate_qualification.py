import unittest

from backend.qualification_engine.candidate import enforce_qualification


class CandidateQualificationTests(unittest.TestCase):
    def test_company_fit_without_opportunity_signal_is_rejected(self):
        decision = enforce_qualification({
            "verdict": "qualified", "score": 95, "hard_mismatches": [],
            "dimensions": {"opportunity_signal": {"status": "unknown", "evidence": []}},
        })
        self.assertEqual("rejected", decision["verdict"])

    def test_strong_evidenced_opportunity_passes(self):
        decision = enforce_qualification({
            "verdict": "qualified", "score": 90, "hard_mismatches": [],
            "dimensions": {"opportunity_signal": {"status": "match", "evidence": ["Hiring a WooCommerce consultant"]}},
        })
        self.assertTrue(decision["gate_passed"])

    def test_hard_mismatch_blocks_high_score(self):
        decision = enforce_qualification({
            "verdict": "qualified", "score": 92, "hard_mismatches": ["Onsite-only mismatch"],
            "dimensions": {"opportunity_signal": {"status": "match", "evidence": ["Active contract"]}},
        })
        self.assertEqual("rejected", decision["verdict"])


if __name__ == "__main__":
    unittest.main()
