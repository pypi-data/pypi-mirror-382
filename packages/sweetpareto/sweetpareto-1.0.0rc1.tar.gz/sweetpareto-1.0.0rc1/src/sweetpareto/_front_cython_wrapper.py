# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import typing

from sweetpareto._front_cython import cython_indices_with_sorted_rows
from sweetpareto.types import VectorT

if typing.TYPE_CHECKING:
    import array


def wrapped_cython(x: VectorT, y: VectorT, maxx: bool, maxy: bool, /) -> list[int]:
    """Engine-API compliant wrapper.

    Necessary because, at present, the cython engine does not have support for
    the argsort behavior. It must take in the indices that sort x.
    """
    rows = x.argsort()
    if maxx:
        rows = rows[::-1]
    indices: array.array[int] = cython_indices_with_sorted_rows(x, y, rows, maxy)
    return indices.tolist()
