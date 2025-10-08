from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar, Literal

MOVES = Literal["R", "L", "U", "D", "F", "B"]
MODIFIERS = Literal["", "'", "2"]

# 0 -> R/L, 1 -> U/D, 2 -> F/B
_AXIS_OF: dict[MOVES, int] = {"R": 0, "L": 0, "U": 1, "D": 1, "F": 2, "B": 2}


# TODO: ensure compliance with WCA; I've written what could be called
# mostly a starting implementation for now with a basic constraint.
@dataclass
class Scrambler:
    """
    A 3x3x3 scramble generator
    """

    rng: random.Random

    MOVES: ClassVar[Sequence[MOVES]] = ("R", "L", "U", "D", "F", "B")
    MODIFIERS: ClassVar[Sequence[MODIFIERS]] = ("", "'", "2")

    @classmethod
    def with_seed(cls, seed: int | float | str | bytes | bytearray) -> Scrambler:
        return cls(random.Random(seed))

    def generate(self, length: int = 20) -> str:
        """Generate a WCA 3x3x3 scramble of given length."""
        scramble: list[str] = []
        last_axis: int | None = None

        for _ in range(length):
            # Moves whose axis is different from the previous axis.
            # We'll avoid repeating the same axes twice in a row.
            # R and L together are disallowed, for example, while
            # R and U, or U and D, are fine.
            candidates: list[MOVES] = [
                f for f in self.MOVES if last_axis is None or _AXIS_OF[f] != last_axis
            ]

            face: MOVES = self.rng.choice(candidates)
            modifier: MODIFIERS = self.rng.choice(self.MODIFIERS)

            scramble.append(f"{face}{modifier}")
            last_axis = _AXIS_OF[face]

        return " ".join(scramble)
