import unittest

from voice.controller import volume_from_samples
from voice.versus import Architect, gap_bounds, winner


class VoiceRules(unittest.TestCase):
    def test_microphone_range(self):
        self.assertEqual(volume_from_samples([0] * 8), 0)
        self.assertEqual(volume_from_samples([1, -1]), 1)
        self.assertLess(volume_from_samples([0.02]), volume_from_samples([0.07]))

    def test_hold_and_release(self):
        player = Architect()
        for _ in range(30):
            player.update(0.05, 1, powers_enabled=True)
        self.assertAlmostEqual(player.pulse.energy, 60 + 29 * 0.4)
        player.update(0.05, 0, powers_enabled=True)
        player.update(0.05, 1, powers_enabled=True)
        self.assertLess(player.pulse.energy, 40)

    def test_level_and_energy(self):
        player = Architect()
        player.update(0.02, 1)
        self.assertEqual(player.pulse.energy, 100)
        player.pulse.energy = 10
        player.update(0.02, 0, power_pressed=True, powers_enabled=True)
        self.assertEqual(player.pulse.remaining, 0)

    def test_keyboard_bounds_and_results(self):
        player = Architect()
        self.assertLess(player.update(0.05, 0, axis=-1), 1)
        player.update(0.05, 0, power_pressed=True, powers_enabled=True)
        self.assertEqual(player.pulse.energy, 60)
        self.assertEqual(gap_bounds(150, 100, 0.5, 60), (120, 180))
        self.assertIsNone(winner(False, 2, 3))
        self.assertEqual(winner(False, 3, 3), "Pilot Win")
        self.assertEqual(winner(True, 3, 3), "Architect Win")

    def test_voice_changes_size_and_preserves_center(self):
        player = Architect()
        for volume, expected in [(0, 100), (0.5, 50), (1, 0), (0, 100)]:
            for _ in range(51):
                scale = player.update(0.05, volume)
            top, bottom = gap_bounds(150, 100, scale)
            self.assertAlmostEqual(bottom - top, expected)
            self.assertEqual((top + bottom) / 2, 150)

    def test_normal_travel_time(self):
        player = Architect()
        for volume, end in [(1, 0.0), (0, 1.0)]:
            for _ in range(24):
                player.update(0.05, volume)
            self.assertAlmostEqual(abs(player.scale - end), 0.04)
            self.assertAlmostEqual(player.update(0.05, volume), end)

    def test_x_doubles_travel_speed_then_returns_to_normal(self):
        player = Architect()
        player.update(0.05, 0, axis=-1, powers_enabled=True)
        self.assertAlmostEqual(player.scale, 0.96)
        player.update(0.05, 0, axis=-1, power_pressed=True, powers_enabled=True)
        self.assertAlmostEqual(player.scale, 0.88)
        for _ in range(20):
            player.update(0.05, 0, axis=-1, powers_enabled=True)
        self.assertEqual(player.scale, 0)
        self.assertAlmostEqual(player.update(0.05, 0, powers_enabled=True), 0.04)
