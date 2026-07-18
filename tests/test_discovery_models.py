import unittest

from backend.shared.models import Opportunity, OpportunityStatus


class DiscoveryModelTests(unittest.TestCase):
    def test_opportunity_defaults_are_isolated(self):
        first = Opportunity("Role", "Company", "web", "https://example.com/1")
        second = Opportunity("Role", "Company", "web", "https://example.com/2")
        first.raw_data["signal"] = True

        self.assertEqual(OpportunityStatus.NEW.value, "new")
        self.assertEqual(second.raw_data, {})


if __name__ == "__main__":
    unittest.main()
