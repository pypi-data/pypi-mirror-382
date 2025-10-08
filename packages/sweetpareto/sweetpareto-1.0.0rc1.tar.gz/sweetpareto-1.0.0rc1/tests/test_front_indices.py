# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import math

import hypothesis.strategies as st
import numpy as np
import pytest
from hypothesis import assume, given
from hypothesis.extra.numpy import (
    array_shapes,
    arrays,
    floating_dtypes,
    integer_dtypes,
)

from sweetpareto import pareto_indices
from sweetpareto.types import VectorT


@pytest.fixture
def test_data():
    return np.array(
        [
            [0.8, 0.2],
            [0.2, 0.8],
            [-0.2, 0.8],
            [-0.8, 0.2],
            [-0.8, -0.2],
            [-0.2, -0.8],
            [0.2, -0.8],
            [0.8, -0.2],
        ],
        order="F",
    )


def test_maxx_maxy(test_data: np.ndarray):
    mask = pareto_indices(test_data[:, 0], test_data[:, 1], maxx=True, maxy=True)
    front = test_data[mask].tolist()  # list helps the diff if there's a failure
    expected = {(0.8, 0.2), (0.2, 0.8)}
    assert len(front) == len(expected)
    for x, y in front:
        assert (x, y) in expected


def test_maxx_miny(test_data: np.ndarray):
    mask = pareto_indices(test_data[:, 0], test_data[:, 1], maxx=True, maxy=False)
    front = test_data[mask].tolist()
    expected = {(0.2, -0.8), (0.8, -0.2)}
    assert len(front) == len(expected)
    for x, y in front:
        assert (x, y) in expected


@pytest.mark.parametrize(
    ("maxx", "maxy", "expected"),
    [
        (True, True, ((0.8, 0.2), (0.2, 0.8))),
        (True, False, ((0.2, -0.8), (0.8, -0.2))),
        (False, False, ((-0.2, -0.8), (-0.8, -0.2))),
        (False, True, ((-0.8, 0.2), (-0.2, 0.8))),
    ],
    ids=["maxx-maxy", "maxx-miny", "minx-miny", "minx-maxy"],
)
def test_parametrized(
    test_data: np.ndarray,
    maxx: bool,
    maxy: bool,
    expected: tuple[tuple[float, ...]],
):
    mask = pareto_indices(test_data[:, 0], test_data[:, 1], maxx=maxx, maxy=maxy)
    front = test_data[mask].tolist()
    assert len(front) == len(expected)
    for x, y in front:
        assert (x, y) in expected


@given(
    arrays(float, st.tuples(st.integers(1, max_value=100), st.just(2))),
    st.booleans(),
    st.booleans(),
)
def test_random_data(a: np.ndarray, maxx: bool, maxy: bool):
    check_front(a[:, 0], a[:, 1], maxx, maxy)


def check_front(xs: VectorT, ys: VectorT, maxx: bool, maxy: bool):
    mask = pareto_indices(xs, ys, maxx=maxx, maxy=maxy)

    for mx, my in zip(xs[mask], ys[mask], strict=False):
        assert not math.isnan(mx)
        assert not math.isnan(my)
        dominates = (xs > mx) if maxx else (xs < mx)
        dominates &= (ys > my) if maxy else (ys < my)
        assert dominates.sum() == 0, (mx, my)


@st.composite
def equal_len_vectors(draw: st.DrawFn):
    rows = draw(st.integers(1, max_value=100))
    dtype_strat = st.sampled_from([integer_dtypes(), floating_dtypes()])
    vector_strat = arrays(dtype_strat, rows)
    x: VectorT = draw(vector_strat)
    y: VectorT = draw(vector_strat)
    return x, y


@given(equal_len_vectors(), st.booleans(), st.booleans())
def test_different_datatypes(xy: tuple[VectorT, VectorT], maxx: bool, maxy: bool):
    x, y = xy
    check_front(x, y, maxx, maxy)


@given(
    st.integers(1, 100),
    st.integers(1, 100),
    st.booleans(),
    st.booleans(),
)
def test_unequal_lengths(nx: int, ny: int, maxx: bool, maxy: bool):
    assume(nx != ny)
    x = np.empty(nx)
    y = np.empty(ny)
    with pytest.raises(ValueError, match="Vector sizes must be identical"):
        pareto_indices(x, y, maxx=maxx, maxy=maxy)


@given(st.booleans(), st.booleans())
def test_zero_length(maxx: bool, maxy: bool):
    x = np.empty(0)
    y = np.empty(0)
    with pytest.raises(IndexError, match="zero length vector"):
        pareto_indices(x, y, maxx=maxx, maxy=maxy)


@given(
    arrays(floating_dtypes(), shape=array_shapes(min_dims=2)),
    st.booleans(),
    st.booleans(),
)
def test_only_vector(x: np.ndarray, maxx: bool, maxy: bool):
    with pytest.raises(ValueError, match="X must be vector"):
        pareto_indices(x, x, maxx=maxx, maxy=maxy)
