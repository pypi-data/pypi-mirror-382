from __future__ import annotations

import re

import pytest

from cubetimer._scrambler import Scrambler

FACES = {"R", "L", "U", "D", "F", "B"}
MODIFIERS = {"", "'", "2"}
AXIS_OF = {"R": 0, "L": 0, "U": 1, "D": 1, "F": 2, "B": 2}

MOVE_REGEX = re.compile(r"^(R|L|U|D|F|B)(|\'|2)$")


@pytest.mark.parametrize("length", [1, 5, 20, 25, 40])
@pytest.mark.parametrize("seed", [0, 1, 42, 123456789])
def test_length_and_token_shape(seed: int, length: int) -> None:
    gen = Scrambler.with_seed(seed)
    s = gen.generate(length)
    tokens = s.split()
    assert len(tokens) == length

    for t in tokens:
        assert MOVE_REGEX.match(t), f"bad move token: {t}"
        face, modifier = (t[0], t[1:] if len(t) > 1 else "")
        assert face in FACES
        assert modifier in MODIFIERS


@pytest.mark.parametrize("seed", [7, 8, 9, 10, 11])
def test_no_consecutive_same_axis(seed: int) -> None:
    gen = Scrambler.with_seed(seed)
    s = gen.generate(50)
    tokens = s.split()
    axes = [AXIS_OF[t[0]] for t in tokens]
    assert all(a != b for a, b in zip(axes, axes[1:])), s


@pytest.mark.parametrize(
    ("seed_a", "seed_b", "length"),
    [(0, 1, 30), (2, 3, 30), (42, 99, 30)],
)
def test_seed(seed_a: int, seed_b: int, length: int) -> None:
    ga = Scrambler.with_seed(seed_a)
    gb = Scrambler.with_seed(seed_b)
    sa = ga.generate(length)
    sb = gb.generate(length)
    assert sa != sb


@pytest.mark.parametrize(
    ("seed", "length"),
    [(0, 20), (1, 20), (42, 30), (42, 10), (2025, 25)],
)
def test_seed_output_determinism(seed: int, length: int) -> None:
    g1 = Scrambler.with_seed(seed)
    g2 = Scrambler.with_seed(seed)
    assert g1.generate(length) == g2.generate(length)
