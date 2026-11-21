from dataclasses import dataclass


@dataclass
class Pulse:
    energy: float = 100.0
    remaining: float = 0.0
    armed: bool = True

    def update(self, dt, volume, key_pressed, enabled, holding=False):
        """A sound or key press costs 40 energy. A sustained sound triggers only once."""
        loud_onset = self.armed and volume >= 0.78
        if loud_onset:
            self.armed = False
        elif volume <= 0.45:
            self.armed = True
        self.remaining = max(0.0, self.remaining - dt) if enabled else 0.0
        rate = -60.0 if holding else 8.0
        self.energy = max(0.0, min(100.0, self.energy + rate * dt))
        if enabled and not self.remaining and self.energy >= 40 and (loud_onset or key_pressed):
            self.energy -= 40
            self.remaining = 0.8
        return self.remaining > 0
