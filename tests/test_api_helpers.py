import unittest

from src.api.main import risk_label, transaction_to_frame
from src.api.pydantic_models import CreditCardTransaction, EcommerceTransaction


class ApiHelperTests(unittest.TestCase):
    def test_ecommerce_transaction_to_frame_has_expected_columns(self):
        transaction = EcommerceTransaction(
            purchase_value=45,
            age=31,
            time_since_signup=8,
            hour_of_day=2,
            day_of_week=5,
            transaction_velocity=1.8,
            device_transaction_count=4,
            ip_transaction_count=3,
            source="Ads",
            browser="Chrome",
            sex="M",
            country="Unknown",
        )

        frame = transaction_to_frame("ecommerce", transaction)

        self.assertEqual(frame.shape, (1, 12))
        self.assertIn("transaction_velocity", frame.columns)
        self.assertEqual(frame.loc[0, "country"], "Unknown")

    def test_creditcard_transaction_to_frame_engineers_serving_features(self):
        transaction = CreditCardTransaction(
            Time=7200,
            Amount=120.5,
            merchant_risk=0.8,
            device_risk=0.6,
            international=1,
            card_age_days=90,
            num_items=3,
            online_order=1,
        )

        frame = transaction_to_frame("creditcard", transaction)

        self.assertEqual(frame.loc[0, "hour_of_day"], 2)
        self.assertAlmostEqual(frame.loc[0, "risk_score_mean"], 0.7)
        self.assertIn("amount_log1p", frame.columns)

    def test_risk_label_thresholds(self):
        self.assertEqual(risk_label(0.2), "low")
        self.assertEqual(risk_label(0.5), "medium")
        self.assertEqual(risk_label(0.8), "high")


if __name__ == "__main__":
    unittest.main()
