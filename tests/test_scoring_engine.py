import unittest

from backend.scoring_engine.service import score_opportunity


class ScoringEngineTests(unittest.TestCase):
    def test_evidence_and_opportunity_signal_raise_score(self):
        result = score_opportunity({"raw_data": {"candidate_qualification": {
            "score": 90, "fit_reasons": ["Strong domain fit"], "risk_signals": [],
            "dimensions": {
                "opportunity_signal": {"status": "match", "evidence": ["Active hiring"]},
                "opportunity_type_fit": {"status": "match", "evidence": ["Contract role"]},
                "budget_fit": {"status": "unknown", "evidence": []},
            },
        }, "research_profile": {"hiring_signals": ["Hiring"]}, "research_evidence": [{"url": "x"}]}})
        self.assertGreaterEqual(result["score"], 70)
        self.assertIn("business_dna_fit", result["breakdown"])

    def test_risks_reduce_score(self):
        base = {"fit_score": 90, "qualified": True, "fit_reasons": []}
        clean = score_opportunity({"source_url": "x", "summary": "y", "country": "z", "opportunity_type": "Contract", "raw_data": {"business_dna_qualification": base}})
        risky = score_opportunity({"source_url": "x", "summary": "y", "country": "z", "opportunity_type": "Contract", "raw_data": {"business_dna_qualification": {**base, "mismatch_reasons": ["Budget unknown", "Location risk"]}}})
        self.assertLess(risky["score"], clean["score"])

    def test_score_is_bounded(self):
        result = score_opportunity({"raw_data": {"business_dna_qualification": {"fit_score": 500}}})
        self.assertLessEqual(result["score"], 100)


if __name__ == "__main__":
    unittest.main()
