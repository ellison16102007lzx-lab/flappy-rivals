"""Classify a resolved forecast by its vertical prediction error."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class BluffResult:
    """Signed error (actual minus prediction), its magnitude, and a flag."""

    residual_px: float
    absolute_error_px: float
    is_bluff: bool


class BluffDetector:
    """Flag deviations at or above a configurable pixel threshold.

    Pass a forecast saved at tick t and the actual y observed at its target
    tick, before training on that sample. The caller chooses when to enable
    scoring, how to tune the threshold, and how to display a flag. A flag
    represents a large deviation from the forecast.
    """

    def __init__(self, threshold_px: float = 40.0) -> None:
        if not isfinite(threshold_px) or threshold_px <= 0:
            raise ValueError("threshold_px must be finite and positive")
        self._threshold_px = threshold_px

    def evaluate(self, predicted_y: float, actual_y: float) -> BluffResult:
        """Return the deviation and flag for one matched pair in pixels."""
        if not isfinite(predicted_y) or not isfinite(actual_y):
            raise ValueError("predicted_y and actual_y must be finite")
        residual = actual_y - predicted_y
        magnitude = abs(residual)
        return BluffResult(residual, magnitude, magnitude >= self._threshold_px)
