import unittest

import numpy as np

from src.modeling import evaluate_classifier, results_to_frame


class ConstantProbabilityModel:
    def predict_proba(self, X):
        return np.array([[0.8, 0.2], [0.3, 0.7], [0.4, 0.6], [0.9, 0.1]])


class ModelingTests(unittest.TestCase):
    def test_evaluate_classifier_returns_required_metrics(self):
        result = evaluate_classifier(
            "TestDataset",
            "TestModel",
            ConstantProbabilityModel(),
            np.zeros((4, 2)),
            np.array([0, 1, 1, 0]),
        )

        self.assertEqual(result.dataset, "TestDataset")
        self.assertEqual(result.model_name, "TestModel")
        self.assertGreaterEqual(result.auc_pr, 0)
        self.assertGreaterEqual(result.f1_score, 0)
        self.assertEqual((result.tn, result.fp, result.fn, result.tp), (2, 0, 0, 2))

    def test_results_to_frame_sorts_by_dataset_and_auc_pr(self):
        result = evaluate_classifier(
            "TestDataset",
            "TestModel",
            ConstantProbabilityModel(),
            np.zeros((4, 2)),
            np.array([0, 1, 1, 0]),
        )
        frame = results_to_frame([result])

        self.assertEqual(list(frame.columns)[0], "dataset")
        self.assertEqual(frame.iloc[0]["model_name"], "TestModel")


if __name__ == "__main__":
    unittest.main()
