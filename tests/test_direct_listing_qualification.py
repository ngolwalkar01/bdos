import json
import unittest

from backend.qualification_engine.direct_listing import qualify_direct_listings


class _Response:
    def __init__(self, output_text):
        self.output_text = output_text


class _Responses:
    def __init__(self, payload):
        self.payload = payload

    def create(self, **_kwargs):
        return _Response(json.dumps(self.payload))


class _Client:
    def __init__(self, payload):
        self.responses = _Responses(payload)


class DirectQualificationTests(unittest.TestCase):
    def test_only_explicit_high_score_is_promoted(self):
        listings = [{"title": "A", "raw_data": {}}, {"title": "B", "raw_data": {}}]
        client = _Client({"decisions": [
            {"index": 0, "qualified": True, "fit_score": 92, "fit_reasons": ["Strong fit"]},
            {"index": 1, "qualified": True, "fit_score": 70, "fit_reasons": ["Partial fit"]},
        ]})
        result = qualify_direct_listings(client, {"profile": "DNA"}, listings)
        self.assertEqual(["A"], [item["title"] for item in result])
        self.assertEqual("qualified", result[0]["status"])

    def test_missing_decision_is_rejected(self):
        result = qualify_direct_listings(_Client({"decisions": []}), {}, [{"title": "A"}])
        self.assertEqual([], result)


if __name__ == "__main__":
    unittest.main()
