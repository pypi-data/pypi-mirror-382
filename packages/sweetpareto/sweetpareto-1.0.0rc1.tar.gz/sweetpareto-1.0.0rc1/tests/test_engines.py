# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from unittest.mock import patch

import hypothesis.strategies as st
import numpy as np
import pytest
from hypothesis import given
from hypothesis.extra.numpy import arrays

import sweetpareto

pytest.importorskip("sweetpareto._front_cython_wrapper", reason="Need cython")


def test_cython_engine_factory():
    x = np.arange(-5, 5, dtype=float)
    y = x * x
    with patch("sweetpareto._engines._pure_py_front_indices") as pure_py:
        sweetpareto.pareto_indices(x, y, maxx=True, maxy=False, engine="cython")
    pure_py.assert_not_called()


@given(
    arrays(float, st.tuples(st.integers(1, max_value=100), st.just(2))),
    st.booleans(),
    st.booleans(),
)
def test_equiv_cython(
    data,
    maxx: bool,
    maxy: bool,
):
    x = data[:, 0]
    y = data[:, 1]
    reference = sweetpareto.pareto_indices(x, y, maxx=maxx, maxy=maxy, engine="python")
    cyth = sweetpareto.pareto_indices(x, y, maxx=maxx, maxy=maxy, engine="cython")
    assert cyth == reference
