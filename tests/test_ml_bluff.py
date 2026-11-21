import unittest

from ml import BluffDetector, BluffResult, OnlinePositionPredictor


class BluffDetectorTests(unittest.TestCase):
    def test_small_deviation_is_not_flagged(self):
        detector = BluffDetector(threshold_px=10)
        self.assertEqual(detector.evaluate(100, 107), BluffResult(7, 7, False))

    def test_threshold_is_inclusive_in_either_direction(self):
        detector = BluffDetector(threshold_px=10)
        self.assertEqual(detector.evaluate(100, 110), BluffResult(10, 10, True))
        self.assertEqual(detector.evaluate(100, 90), BluffResult(-10, 10, True))
        self.assertTrue(detector.evaluate(100, 80).is_bluff)

    def test_invalid_threshold_or_positions_are_rejected(self):
        for threshold in (0, -1, float("nan"), float("inf")):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                BluffDetector(threshold_px=threshold)
        with self.assertRaises(ValueError):
            BluffDetector().evaluate(100, float("inf"))

    def test_saved_forecast_can_be_scored_before_training(self):
        model = OnlinePositionPredictor(horizon_ticks=3, learning_rate=1)
        detector = BluffDetector(threshold_px=20)
        initial_y, initial_velocity = 120, 0
        saved_forecast = model.predict(initial_y, initial_velocity)
        actual_y = 150
        self.assertTrue(detector.evaluate(saved_forecast, actual_y).is_bluff)
        model.update(initial_y, initial_velocity, actual_y)
        self.assertAlmostEqual(model.predict(initial_y, initial_velocity), actual_y)
        self.assertTrue(detector.evaluate(saved_forecast, actual_y).is_bluff)
