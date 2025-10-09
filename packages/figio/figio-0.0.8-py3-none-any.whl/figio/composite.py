"""A composite is a single figure with one or more models."""

from typing import NamedTuple

import matplotlib.pyplot as plt

from figio import figure, histogram, utility


class Composite(NamedTuple):
    """The view type."""

    figure: figure.Figure
    models: list[histogram.Histogram]


def plot_composite(cc: Composite) -> None:
    """Plot the figure and histogram."""

    ff = cc.figure
    hists = cc.models

    # breakpoint()
    # Create the histogram
    fig, ax = plt.subplots(dpi=ff.dpi)
    # plt.hist(data, bins=20, color="blue", alpha=0.7, log=True)

    for hh in hists:
        print(f"Number of elements in histgram: {len(hh.data)}")
        # n_neg = [x <= 0.0 for x in bb]
        ax.hist(
            hh.data,
            **hh.plot_kwargs,
        )

    # Add a legend
    plt.legend()

    # Add title and labels
    # ax.set_title(ff.title)
    fig.suptitle(ff.title)
    ax.set_xlabel(ff.xlabel)
    ax.set_ylabel(ff.ylabel)

    if ff.details:
        ss = ff.file.name
        details = utility.timestamp(figure_name=ss)
        ax.set_title(details, fontsize=8, ha="center", color="dimgray")

    # plt.xticks(np.arange(-0.1, 1.0, 0.1))
    # xt = [-0.25, 0.0, 0.25, 0.5, 0.75, 1.00]
    # plt.xticks(xt)
    # plt.xlim([xt[0], xt[-1]])
    # plt.ylim([1, 2.0e6])

    # x_ticks = list(range(nxp))
    # y_ticks = list(range(nyp))
    # z_ticks = list(range(nzp))

    # ax.set_xlim(float(x_ticks[0]), float(x_ticks[-1]))

    # Save the plot
    if ff.save:
        # fn = Path(ff.file).stem + "_msj" + ".png"
        fn = ff.file
        plt.savefig(fn)
        print(f"Saved file: {fn}")

    # Show the plot
    if ff.display:
        plt.show()

    # Clear the current figure
    # plt.clf()
