import unittest
from backend.discovery_engine.strategy import expand_search_queries, parse_strategy_response

class StrategyTests(unittest.TestCase):
    def test_normalize_and_expand(self):
        source='{"industries":["Ecommerce"],"business_models":["Subscription"],"keywords":["WooCommerce"],"countries":["Denmark"],"company_sizes":["Small"],"job_titles":["Consultant"],"decision_makers":["Founder"],"search_queries":[],"negative_keywords":["agency"],"priority_sources":["Company Websites"]}'
        strategy=expand_search_queries(parse_strategy_response(source))
        self.assertGreaterEqual(len(strategy["search_queries"]),100)
        self.assertEqual(len(strategy["search_queries"]),len(set(strategy["search_queries"])))

if __name__=="__main__":
    unittest.main()
