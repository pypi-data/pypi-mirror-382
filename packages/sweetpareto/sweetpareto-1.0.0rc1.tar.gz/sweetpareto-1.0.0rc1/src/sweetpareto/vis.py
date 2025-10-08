# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
try:
    from sweetpareto._sns import Pareto, pareto_plot
except ImportError:
    msg = (
        "Plotting capabilities rely on seaborn. Please install the plot dependencies"
        "with e.g., pip install sweetpareto[plot]"
    )
    raise ImportError(msg) from None

__all__ = ["Pareto", "pareto_plot"]
