import unittest

from game.engine import GameEngine
from game.pipes import Pipe


class DemoIntegration(unittest.TestCase):
    def setUp(self):
        self.game = GameEngine(None, None)
        self.game.start()

    def test_touching_pipe_wall_is_fatal_before_guard(self):
        g = self.game
        g.bird.y = 90
        g.pipe_manager.pipes = [Pipe(g.bird.x + g.bird.width + 2, 220, 100, 2)]
        g.update(axis=-1)
        self.assertEqual((g.state, g.winner), ("gameover", "Architect Win"))

    def test_clean_entry_locks_gap_during_pulse(self):
        g = self.game
        g.set_level(2)
        pipe = Pipe(g.bird.x + g.bird.width + 3, g.bird.y + 12, 160, 3)
        g.pipe_manager.pipes = [pipe]
        g.update(axis=-1, power_pressed=True)
        self.assertEqual(pipe.gap_size, 160)
        self.assertTrue(g.protected)
        self.assertEqual(g.energy, 60)

    def test_level_five_forecast_is_scored_at_crossing(self):
        g = self.game
        g.set_level(5)
        g.bird.y = 200
        pipe = Pipe(g.bird.x + g.bird.width + 44, 225, 130, 4)
        g.pipe_manager.pipes = [pipe]
        for _ in range(11):
            g.update()
        self.assertEqual(g.model.samples_seen, 1)
        self.assertIsNotNone(g.prediction)
        self.assertIn("Prediction error", g.bluff_feedback)
        g.restart()
        self.assertIsNone(g.pending)

    def test_advance_through_all_five_levels(self):
        g = self.game
        for level in range(1, 6):
            self.assertEqual(g.level_manager.current_level, level)
            for _ in range(g.level_manager.get_config()["obstacles_to_clear"]):
                g.pipe_manager.pipes = [Pipe(0, 220, 160, 2)]
                g.update()
            self.assertEqual((g.state, g.winner), ("levelcomplete", "Pilot Win"))
            g.jump()
        self.assertEqual(g.level_manager.current_level, 1)
