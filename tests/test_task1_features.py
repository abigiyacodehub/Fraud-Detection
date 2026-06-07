import unittest

import pandas as pd

from src.feature_engineering import (
    add_ecommerce_time_velocity_features,
    add_geolocation_features,
    country_fraud_summary,
)
from src.preprocessing import clean_creditcard_data, clean_fraud_data


class Task1FeatureTests(unittest.TestCase):
    def test_clean_fraud_data_corrects_types_and_removes_duplicates(self):
        df = pd.DataFrame(
            {
                "user_id": [1, 1],
                "signup_time": ["2015-01-01 00:00:00", "2015-01-01 00:00:00"],
                "purchase_time": ["2015-01-01 00:00:05", "2015-01-01 00:00:05"],
                "purchase_value": [10, 10],
                "device_id": ["abc", "abc"],
                "source": ["SEO", "SEO"],
                "browser": ["Chrome", "Chrome"],
                "sex": ["M", "M"],
                "age": [30, 30],
                "ip_address": [120000000.0, 120000000.0],
                "class": [1, 1],
            }
        )

        cleaned, report = clean_fraud_data(df)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(report.duplicate_rows_removed, 1)
        self.assertTrue(str(cleaned["signup_time"].dtype).startswith("datetime64"))
        self.assertEqual(cleaned["class"].dtype, int)

    def test_clean_creditcard_data_fills_numeric_missing_values(self):
        df = pd.DataFrame(
            {
                "Time": [1, 2],
                "Amount": [10.0, None],
                "merchant_risk": [0.1, 0.2],
                "device_risk": [0.3, 0.4],
                "international": [0, 1],
                "card_age_days": [100, 50],
                "num_items": [1, 2],
                "online_order": [1, 0],
                "Class": [0, 1],
            }
        )

        cleaned, report = clean_creditcard_data(df)

        self.assertEqual(report.missing_values_before, 1)
        self.assertEqual(report.missing_values_after, 0)
        self.assertEqual(cleaned["Amount"].isna().sum(), 0)

    def test_geolocation_and_velocity_features_are_created(self):
        fraud = pd.DataFrame(
            {
                "user_id": [1, 2],
                "signup_time": ["2015-01-01 00:00:00", "2015-01-01 00:00:00"],
                "purchase_time": ["2015-01-01 00:00:05", "2015-01-02 01:00:00"],
                "purchase_value": [10, 20],
                "device_id": ["shared", "shared"],
                "source": ["SEO", "Ads"],
                "browser": ["Chrome", "Firefox"],
                "sex": ["M", "F"],
                "age": [30, 35],
                "ip_address": [120000000.0, 175000000.0],
                "class": [1, 0],
            }
        )
        ip_ranges = pd.DataFrame(
            {
                "lower_bound_ip_address": [100000000, 150000000],
                "upper_bound_ip_address": [149999999, 199999999],
                "country": ["United States", "Canada"],
            }
        )

        enriched = add_geolocation_features(fraud, ip_ranges)
        featured = add_ecommerce_time_velocity_features(enriched)
        country_summary = country_fraud_summary(featured)

        self.assertEqual(set(featured["country"]), {"United States", "Canada"})
        self.assertEqual(featured.loc[0, "time_since_signup"], 5)
        self.assertEqual(featured.loc[0, "hour_of_day"], 0)
        self.assertEqual(featured.loc[0, "day_of_week"], 3)
        self.assertIn("transaction_velocity", featured.columns)
        self.assertEqual(country_summary["transactions"].sum(), 2)


if __name__ == "__main__":
    unittest.main()
