import unittest

from backend.research_engine.service import _parse_json


class ResearchEngineTests(unittest.TestCase):
    def test_fenced_json_is_parsed(self):
        result = _parse_json('```json\n{"results": []}\n```')
        self.assertEqual([], result["results"])


if __name__ == "__main__":
    unittest.main()
