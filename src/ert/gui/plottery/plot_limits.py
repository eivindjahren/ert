from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from beartype import beartype
from beartype.typing import Optional

Num = float | int


@beartype
@dataclass
class PlotLimits:
    value_limits: tuple[Optional[float], Optional[float]] = (None, None)
    index_limits: tuple[Optional[int], Optional[int]] = (None, None)
    count_limits: tuple[Optional[int], Optional[int]] = (None, None)
    density_limits: tuple[Optional[Num], Optional[Num]] = (None, None)
    depth_limits: tuple[Optional[Num], Optional[Num]] = (None, None)
    date_limits: tuple[Optional[datetime], Optional[datetime]] = (None, None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlotLimits):
            return False
        equality = self.value_limits == other.value_limits
        equality = equality and self.index_limits == other.index_limits
        equality = equality and self.count_limits == other.count_limits
        equality = equality and self.depth_limits == other.depth_limits
        equality = equality and self.date_limits == other.date_limits
        equality = equality and self.density_limits == other.density_limits

        return equality

    def copyLimitsFrom(self, other: "PlotLimits") -> None:
        self.value_limits = other.value_limits
        self.density_limits = other.density_limits
        self.depth_limits = other.depth_limits
        self.index_limits = other.index_limits
        self.date_limits = other.date_limits
        self.count_limits = other.count_limits
