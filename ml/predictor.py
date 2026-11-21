"""Online prediction of a bird's vertical position at a fixed tick horizon."""

from math import isfinite


def _require_finite(value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")


class OnlinePositionPredictor:
    """Fit an affine model of position and vertical velocity using SGD.

    Use one instance per bird. Supply positions in pixels and velocities in
    pixels per simulation tick, with matching sign conventions. Set
    `position_scale` near the playing field height for feature scaling.
    Predictions start with constant-velocity extrapolation.

    At tick t, save the inputs and the result of `predict`. At tick
    t + horizon_ticks, score that saved prediction against the observed
    position, then call `update` with the saved inputs and the observation.
    Keep the pending samples in the caller and discard samples that cross a
    round reset or lack a matching observation.
    """

    def __init__(
        self,
        horizon_ticks: int = 10,
        learning_rate: float = 0.1,
        position_scale: float = 480.0,
    ) -> None:
        if type(horizon_ticks) is not int or horizon_ticks <= 0:
            raise ValueError("horizon_ticks must be a positive integer")
        if not 0 < learning_rate <= 1:
            raise ValueError("learning_rate must be in (0, 1]")
        if not isfinite(position_scale) or position_scale <= 0:
            raise ValueError("position_scale must be finite and positive")
        self._horizon_ticks = horizon_ticks
        self._learning_rate = learning_rate
        self._position_scale = position_scale
        self._weights = [0.0, 1.0, 1.0]
        self._samples_seen = 0

    @property
    def horizon_ticks(self) -> int:
        """Number of simulation ticks between a forecast and its target."""
        return self._horizon_ticks

    @property
    def samples_seen(self) -> int:
        """Number of labeled samples used to update the model."""
        return self._samples_seen

    def _features(self, y: float, velocity_y: float) -> tuple[float, ...]:
        _require_finite(y, "y")
        _require_finite(velocity_y, "velocity_y")
        return (1.0, y / self._position_scale,
                velocity_y / self._position_scale * self._horizon_ticks)

    def predict(self, y: float, velocity_y: float) -> float:
        """Return the future y in pixels without changing the model."""
        features = self._features(y, velocity_y)
        return sum(w * x for w, x in zip(self._weights, features)) * self._position_scale

    def update(self, y: float, velocity_y: float, actual_future_y: float) -> None:
        """Take one SGD step using the original inputs and matched future y."""
        _require_finite(actual_future_y, "actual_future_y")
        features = self._features(y, velocity_y)
        estimate = sum(w * x for w, x in zip(self._weights, features))
        error = actual_future_y / self._position_scale - estimate
        # Normalize the step by feature energy to limit overshoot.
        step = self._learning_rate * error / sum(x * x for x in features)
        for index, feature in enumerate(features):
            self._weights[index] += step * feature
        self._samples_seen += 1
