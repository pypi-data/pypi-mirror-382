# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Type hint information to try and make type checkers happy."""

import typing

import numpy as np

ValueT = float | int
VectorT = np.ndarray[tuple[int], ValueT]
EngineT = typing.Callable[[VectorT, VectorT, bool, bool], list[int]]
SupportedEngineT = typing.Literal["python", "cython"] | EngineT
