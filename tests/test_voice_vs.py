import unittest

from voice.controller import volume_from_samples
from voice.versus import Architect, gap_bounds, guarded_gap, winner


class VoiceRules(unittest.TestCase):
    def test_microphone_range(self):
        self.assertEqual(volume_from_samples([0] * 8), 0)
        self.assertEqual(volume_from_samples([1, -1]), 1)
        self.assertLess(volume_from_samples([0.02]), volume_from_samples([0.07]))

    def test_hold_and_release(self):
        player = Architect()
        for _ in range(30):
            player.update(0.05, 0.78, axis=1, powers_enabled=True)
        self.assertAlmostEqual(player.pulse.energy, 60 + 29 * 0.4)
        player.update(0.05, 0, powers_enabled=True)
        player.update(0.05, 0.78, axis=1, powers_enabled=True)
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
        for volume, expected in [(0, 100), (0.5, 50), (1, 0), (0, 100)]:
            player = Architect()
            for _ in range(26):
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

    def test_half_width_energy_threshold(self):
        for width, energy in [(0.51, 100), (0.50, 97), (0.49, 97)]:
            with self.subTest(width=width):
                player = Architect()
                player.scale = width
                player.update(0.05, 1 - width)
                self.assertAlmostEqual(player.pulse.energy, energy)

    def test_holding_drains_sixty_energy_per_second(self):
        player = Architect()
        player.scale = 0
        for _ in range(20):
            player.update(0.05, 1)
        self.assertAlmostEqual(player.pulse.energy, 40)

    def test_sustained_voice_and_keyboard_force_reopening(self):
        for volume, axis, powers in [(1, 0, True), (0, -1, False), (0.9, 0, False)]:
            player = Architect()
            smallest = 1
            for _ in range(600):
                smallest = min(smallest, player.update(1/60, volume, axis, powers_enabled=powers))
            self.assertLessEqual(smallest, 0.101)
            self.assertTrue(player.recovering)
            self.assertEqual(player.scale, 1)
            player.update(0.05, 0)
            self.assertFalse(player.recovering)
            self.assertLess(player.update(0.05, 1), 1)

    def test_sensitivity_scales_signal_before_clipping(self):
        samples = [0.08, -0.08]
        normal = volume_from_samples(samples)
        self.assertAlmostEqual(volume_from_samples(samples, 0.5), normal / 2)
        self.assertEqual(volume_from_samples(samples, 3), 1)
        self.assertEqual(volume_from_samples([0], 3), 0)

    def test_late_full_energy_pulse_cannot_shrink_current_pipe(self):
        player = Architect()
        scale = player.update(0.1, 1, power_pressed=True, powers_enabled=True)
        self.assertLess(scale, 1)
        for entry, exit_distance in [(100, 190), (0, 90), (-90, 0)]:
            self.assertEqual(guarded_gap(100, scale, 100, entry, exit_distance, 100, 24), (100, True))
        for entry, exit_distance in [(101, 191), (-91, -1)]:
            self.assertEqual(guarded_gap(100, scale, 100, entry, exit_distance, 100, 24), (100 * scale, False))

    def test_protected_gap_allows_passage_and_can_widen(self):
        gap = 0
        for scale, expected in [(0, 36), (0.7, 70), (0, 70)]:
            gap, protected = guarded_gap(100, scale, gap, 0, 40, 120, 24)
            self.assertTrue(protected)
            self.assertEqual(gap, expected)
