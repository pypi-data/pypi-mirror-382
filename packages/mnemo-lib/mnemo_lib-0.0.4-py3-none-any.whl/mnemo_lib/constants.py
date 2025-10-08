from __future__ import annotations

from enum import IntEnum

MNEMO_SUPPORTED_VERSIONS = list(range(2, 6))


# `MN2OVER` message in ascii values
MN2OVER = [77, 78, 50, 79, 118, 101, 114]


class Direction(IntEnum):
    In = 0
    Out = 1


class ShotType(IntEnum):
    CSA = 0  # Reference Shot A
    CSB = 1  # Reference Shot B
    STD = 2  # Standard aka. Real
    EOC = 3  # End of Cave


class UnitType(IntEnum):
    METRIC = 0
    IMPERIAL = 1
