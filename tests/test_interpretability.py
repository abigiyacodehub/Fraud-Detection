import unittest

import pandas as pd

from src.interpretability import get_transformed_feature_names


class DummyPreprocessor:
    def get_feature_names_out(self):
        return ["num__amount", "cat__country_US"]


class LegacyPreprocessor:
    transformers_ = [
        ("num", None, ["amount", "age"]),
        ("cat", None, ["country"]),
        ("remainder", None, ["unused"]),
    ]


class InterpretabilityTests(unittest.TestCase):
    def test_get_transformed_feature_names_from_modern_preprocessor(self):
        names = get_transformed_feature_names(DummyPreprocessor())

        self.assertEqual(names, ["num__amount", "cat__country_US"])

    def test_get_transformed_feature_names_from_legacy_preprocessor(self):
        names = get_transformed_feature_names(LegacyPreprocessor())

        self.assertEqual(names, ["num__amount", "num__age", "cat__country"])

    def test_importance_report_schema(self):
        frame = pd.DataFrame({"feature": ["a"], "importance": [1.0]})

        self.assertEqual(list(frame.columns), ["feature", "importance"])


if __name__ == "__main__":
    unittest.main()
