# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
sweetpareto

A python package for inspecting and plotting 2-D pareto fronts
"""

from sweetpareto._engines import engine_factory
from sweetpareto._front import pareto_index, pareto_indices

__version__ = "1.0.0rc1"

__all__ = ["engine_factory", "pareto_index", "pareto_indices", "__version__"]
