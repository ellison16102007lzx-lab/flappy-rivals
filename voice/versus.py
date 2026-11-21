from .powers import Pulse


class Architect:
    def __init__(self):
        self.pulse = Pulse()
        self.scale = 1.0
        self.recovering = False

    def update(self, dt, volume, axis=0, power_pressed=False, powers_enabled=False):
        """每个游戏帧调用一次。返回相对于原始缺口高度的倍率。"""
        dt = min(0.1, max(0.0, dt))
        volume = max(0.0, min(1.0, volume))
        squeeze = max(0.0, min(1.0, -axis)) if axis else volume
        if self.recovering and self.scale >= 1.0 and self.pulse.energy >= 20 and squeeze <= 0.45:
            self.recovering = False
        holding = self.scale <= 0.5 and not self.recovering
        active = self.pulse.update(dt, volume, power_pressed, powers_enabled and not self.recovering, holding)
        if holding and self.pulse.energy <= 0:
            self.recovering = True
            self.pulse.remaining = 0.0
            active = False
        target = 1.0 if self.recovering else 1.0 - squeeze
        speed = 0.8  # Fraction of the full gap travelled per second.
        if active:
            speed *= 2
            target *= 0.90
        step = speed * dt
        self.scale += min(step, max(-step, target - self.scale))
        return self.scale


def guarded_gap(base_gap, scale, previous_gap, distance_to_entry, distance_to_exit,
                speed_px_per_second, bird_height):
    """Guard from first contact through last contact. Speed is retained for existing callers."""
    requested = base_gap * scale
    protected = distance_to_exit >= 0 and distance_to_entry <= 0
    if protected:
        clearance = min(base_gap, bird_height + 12)
        return max(requested, previous_gap, clearance), True
    return requested, False


def gap_bounds(center_y, base_gap, scale, min_gap=0):
    """按固定中心缩放。关卡应保证 base_gap >= min_gap。"""
    if scale <= 0:
        return center_y, center_y
    gap = min(base_gap, max(min_gap, base_gap * scale))
    return center_y - gap / 2, center_y + gap / 2


def winner(collided, passed, goal):
    if collided:
        return "Architect Win"
    if passed >= goal:
        return "Pilot Win"
    return None
