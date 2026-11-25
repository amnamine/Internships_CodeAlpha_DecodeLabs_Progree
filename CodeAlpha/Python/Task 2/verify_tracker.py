import portfolio_tracker
import unittest

class TestPortfolioLogic(unittest.TestCase):
    def test_stock_prices_exist(self):
        # Verify database is populated correctly
        self.assertIn("AAPL", portfolio_tracker.STOCK_PRICES)
        self.assertEqual(portfolio_tracker.STOCK_PRICES["AAPL"], 180.00)
        self.assertIn("TSLA", portfolio_tracker.STOCK_PRICES)
        self.assertEqual(portfolio_tracker.STOCK_PRICES["TSLA"], 250.00)

if __name__ == "__main__":
    unittest.main()
