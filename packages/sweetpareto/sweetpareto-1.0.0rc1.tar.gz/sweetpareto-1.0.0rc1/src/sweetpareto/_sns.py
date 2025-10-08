# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Seaborn stat interface."""

from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Literal

import pandas as pd
from seaborn import axes_style
from seaborn.objects import Dots, Line, Plot, Stat

from sweetpareto import engine_factory, pareto_index
from sweetpareto.types import SupportedEngineT


@dataclass
class Pareto(Stat):
    """A seaborn stat object for reducing plot data down to the pareto front.

    Parameters
    ----------
    maxx
        Bool to maximize x or not
    maxy
        Bool to maximize y or not
    engine
        String or function to determine the indices.
    """

    maxx: bool = field(kw_only=True)
    maxy: bool = field(kw_only=True)
    engine: SupportedEngineT = field(kw_only=True, default="python")

    def __post_init__(self):
        self.engine = engine_factory(self.engine)

    def _apply(self, data):
        ix = pareto_index(data, "x", "y", maxx=self.maxx, maxy=self.maxy, engine=self.engine)
        return data.loc[ix]

    def __call__(self, data, groupby, orient, scales):  # noqa: ARG002
        return groupby.apply(data, self._apply)


def pareto_plot(
    df: pd.DataFrame,
    /,
    x: Hashable,
    y: Hashable,
    *,
    maxx: bool,
    maxy: bool,
    engine: SupportedEngineT = "python",
    show_points: bool = False,
    color: Hashable | None = None,
    marker: Hashable | None = None,
    col: Hashable | None = None,
    col_wrap: int | None = None,
    col_order: list[Hashable] | None = None,
    sharex: bool | Literal["col"] = True,
    sharey: bool | Literal["row"] = True,
    height: float = 3,
    aspect: float = 1,
    theme: str | None = None,
):
    """Visualize pareto fronts across a dataset.

    Parameters
    ----------
    df
        Dataframe to be examined
    x
    y
        Columns to make up the x and y axis, respectively.
    maxx
        Boolean to maximize the x axis or not.
    maxy
        Boolean to maximize the y-axis or not.
    engine
        Engine to use (e.g., ``"python"``, ``"cython"``) to extract the pareto front.
        Follows rules from :func:`sweetpareto.engine_factory`
    show_points
        Switch to enable plotting the values off the pareto
        fronts. Defaults to False to just plot the fronts.
    color
        Column to use when separating the dataset into groups
        and coloring them in the same plot. Defaults to ``None``
        and will use one un-separated color.
    marker
        Apply a unique marker based on this column. Defaults
        to ``None`` and will use the default seaborn marker.
    col
        Column to use to create subplots by a unique value
        in this column. Defaults to ``None`` and will make
        one plot.
    col_wrap
        Number of subplots per row of the resulting figure.
        Defaults to ``None`` and will put all subplots
        in the same row.
    size
        Width and height of the resulting figure, including any
        subplots.
    sharex
        Should subplots share the same x-axis? Defaults to True.
        Setting to ``False`` will give a unique x-axis per subplots.
        Setting to ``col`` will use the same x-axis for subplots
        in the same column.
    sharey
        Should subplots share the same y-axis? Defaults to True.
        Setting to ``False`` will give a unique y-axis per subplot.
        Setting to ``row`` will use the same y-axis for subplots
        in the same row.
    height
        Height of a given subplot.
    aspect
        Ratio of width to height for a given subplot
    theme
        Additional theme to apply to the grid. **NOT** the
        same as a matplotlib stylesheet as these are what
        seaborn considers "themes" e.g., ``"whitegrid"``,
        ``"dark"`` - https://seaborn.pydata.org/tutorial/aesthetics.html
    """
    plt = Plot(df, x, y, color=color, marker=marker)
    if show_points:
        plt = plt.add(Dots())
    plt = plt.add(Line(), Pareto(maxx=maxx, maxy=maxy, engine=engine))
    if col is not None:
        plt = plt.facet(col, wrap=col_wrap, order=col_order).share(x=sharex, y=sharey).label(col=f"{col}=")
        if height is not None:
            n_figs = df[col].unique().size
            if col_wrap is None:
                ncols = n_figs
                nrows = 1
            else:
                ncols = min(col_wrap, n_figs)
                nrows = 1 + n_figs % ncols
            total_height = height * nrows
            total_width = height * aspect * ncols
            plt = plt.layout(size=(total_width, total_height))
    elif height is not None:
        plt = plt.layout(size=(height * aspect, height))
    if theme is not None:
        plt = plt.theme({**axes_style(theme)})
    return plt
