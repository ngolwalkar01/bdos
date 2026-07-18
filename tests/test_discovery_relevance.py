import unittest

from backend.discovery_engine.relevance import direct_listing_evidence


class DiscoveryRelevanceTests(unittest.TestCase):
    def setUp(self):
        self.strategy = {
            "keywords": ["WooCommerce", "Subscription Commerce", "Stripe"],
            "job_titles": ["WooCommerce Consultant"],
        }

    def test_relevant_direct_listing_is_accepted(self):
        evidence = direct_listing_evidence(
            "WooCommerce Consultant", ["Stripe"], "Build subscription checkout flows", self.strategy
        )
        self.assertTrue(evidence["accepted"])

    def test_generic_service_page_is_not_direct_evidence(self):
        evidence = direct_listing_evidence(
            "Our WordPress Development Services", [], "Hire our expert developer team", self.strategy
        )
        self.assertFalse(evidence["accepted"])

    def test_single_description_keyword_is_not_enough(self):
        evidence = direct_listing_evidence(
            "General Developer", [], "Some experience with WooCommerce", self.strategy
        )
        self.assertFalse(evidence["accepted"])


if __name__ == "__main__":
    unittest.main()
