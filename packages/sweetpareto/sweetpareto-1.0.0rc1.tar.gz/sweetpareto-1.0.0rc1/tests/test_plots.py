# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pandas as pd
import pytest
import seaborn as sns
from matplotlib import pyplot as plt

from sweetpareto import vis as spv


@pytest.fixture(scope="module")
def penguins():
    return sns.load_dataset("penguins")


@pytest.mark.mpl_image_compare
def test_simple_plot(penguins: pd.DataFrame):
    fig = plt.gcf()
    spv.pareto_plot(penguins, "bill_depth_mm", "flipper_length_mm", maxx=True, maxy=True).on(fig).plot()
    return fig


@pytest.mark.xfail
@pytest.mark.mpl_image_compare
def test_faceted_plot(penguins: pd.DataFrame):
    """Test the ability to save a complicated, faceted plot.

    Notes
    -----
    Currently not what I would like in terms of spacing. The generated
    plot is made with an aspect ratio of 0.75 to make the actual subplots
    look square and nicely spaced. Additionally, the legend is too far away
    from the plot when we save to file. I think there's some additional magic
    going on in the seaborn facet grid backend when it's rendering to a jupyter
    notebook vs. a "plain" matplotlib figure.
    """
    fig = plt.gcf()

    spv.pareto_plot(
        penguins,
        "flipper_length_mm",
        "body_mass_g",
        maxx=False,
        maxy=True,
        col="sex",
        color="species",
        marker="species",
        height=4,
        aspect=1,
        theme="whitegrid",
        show_points=True,
    ).on(fig).plot()
    return fig
