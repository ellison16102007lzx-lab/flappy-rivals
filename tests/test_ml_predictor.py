import unittest

from ml import OnlinePositionPredictor


class OnlinePositionPredictorTests(unittest.TestCase):
    def test_initial_prediction_extrapolates_at_configured_horizon(self):
        model = OnlinePositionPredictor(horizon_ticks=6)
        self.assertEqual(model.horizon_ticks, 6)
        self.assertAlmostEqual(model.predict(120, -5), 90)
        self.assertEqual(model.samples_seen, 0)

    def test_one_sample_moves_prediction_toward_target(self):
        model = OnlinePositionPredictor()
        before = model.predict(100, 2)
        model.update(100, 2, 150)
        after = model.predict(100, 2)
        self.assertLess(before, after)
        self.assertLess(after, 150)
        self.assertEqual(model.samples_seen, 1)

    def test_online_model_generalizes_to_unseen_inputs(self):
        model = OnlinePositionPredictor(horizon_ticks=5, position_scale=200)
        inputs = [(y, speed) for y in (20, 100, 180) for speed in (-20, 0, 20)]
        for _ in range(180):
            for y, speed in inputs:
                model.update(y, speed, 12 + 0.8 * y + 3 * speed)
        self.assertAlmostEqual(model.predict(130, 9), 143, delta=0.5)

    def test_invalid_configuration_is_rejected(self):
        for options in (
            {"horizon_ticks": 0},
            {"horizon_ticks": 1.5},
            {"learning_rate": 0},
            {"position_scale": float("inf")},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                OnlinePositionPredictor(**options)

    def test_invalid_samples_do_not_train_model(self):
        model = OnlinePositionPredictor()
        with self.assertRaises(ValueError):
            model.predict(float("nan"), 0)
        with self.assertRaises(ValueError):
            model.update(10, 0, float("inf"))
        self.assertEqual(model.samples_seen, 0)
