from __future__ import annotations

import importlib.metadata

import cubetimer


def test_version():
    assert importlib.metadata.version("cubetimer") == cubetimer.__version__
