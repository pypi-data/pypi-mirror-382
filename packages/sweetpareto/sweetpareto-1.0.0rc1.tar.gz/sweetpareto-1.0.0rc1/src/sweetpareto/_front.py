# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pandas as pd

from sweetpareto._engines import engine_factory
from sweetpareto.types import SupportedEngineT, VectorT


def pareto_indices(
    x: VectorT,
    y: VectorT,
    /,
    *,
    maxx: bool,
    maxy: bool,
    engine: SupportedEngineT = "python",
) -> list[int]:
    """Find the positions that make up the pareto front.

    Parameters
    ----------
    x
    y
        Vector data of all possible points in the space.
    maxx
        Should we maximize the x vector?
    maxy
        Should we maximize the y vector

    Returns
    -------
    list[int]
        Positions in ``x`` and ``y`` that make up the pareto front.
        The values are obtainable with e.g.,::

        >>> ix = front_mask(x, y, maxx=True, maxy=False)
        >>> x[ix]
        >>> y[ix]

    Raises
    ------
    ValueError
        If x is not a vector. If x and y have dissimilar shapes.
    IndexError
        If x has no data

    Notes
    -----
    Implements the "maxima of a point set" algorithm from
    https://en.wikipedia.org/wiki/Maxima_of_a_point_set

        A point p in a finite set of points S is said to be maximal or
        non-dominated if there is no other point q in S whose coordinates are
        all greater than or equal to the corresponding coordinates of p

    """
    if x.ndim != 1:
        msg = f"X must be vector, not {x.shape=}"
        raise ValueError(msg)
    if x.size == 0:
        msg = "Cannot provide zero length vectors."
        raise IndexError(msg)
    if y.shape != x.shape:
        msg = f"Vector sizes must be identical. {x.shape=} != {y.shape=}"
        raise ValueError(msg)
    solver = engine_factory(engine)
    return solver(x, y, maxx, maxy)


def pareto_index(
    d: pd.DataFrame,
    /,
    x: str,
    y: str,
    *,
    maxx: bool,
    maxy: bool,
    engine: SupportedEngineT = "python",
) -> pd.Index:
    """Produce a :class:`pandas.Index` of the pareto front.

    Parameters
    ----------
    d
        Dataframe of interest
    x
    y
        Columns in ``d`` that should make up the pareto front.
    maxx
        Should we maximize the x column?
    maxy
        Should we maximize the y column?

    Returns
    -------
    Indices along ``d`` that make up the pareto front.
    """
    mask = pareto_indices(d[x].values, d[y].values, maxx=maxx, maxy=maxy, engine=engine)
    return d.index[mask]
