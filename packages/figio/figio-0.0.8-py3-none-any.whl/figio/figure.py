"""The figure type, constructor, and methods."""

from typing import NamedTuple
from pathlib import Path

import matplotlib.pyplot as plt
from schema import Schema, And, Optional, SchemaError, Use

from figio import histogram
from figio import utility

# Define the schema for the figure
figure_schema = Schema(
    {
        Optional("details", default=True): bool,
        Optional("display", default=True): bool,
        Optional("dpi", default=100): int,
        "folder": And(str, len),  # non-empty string
        "file": And(str, len),  # non-empty string
        Optional("latex", default=False): bool,
        "models": And(
            [Use(str)],  # each item in the list must be a string
            lambda lst: len(lst) >= 1,  # list must have at least 1 item
        ),
        Optional("save", default=False): bool,
        Optional("size", default=[8.0, 6.0]): list[float | int],
        Optional("title", default=""): str,
        Optional("xlabel", default=""): str,
        Optional("ylabel", default=""): str,
    },
    ignore_extra_keys=True,
)


class Figure(NamedTuple):
    """The figure type."""

    details: str
    display: bool
    dpi: int
    folder: Path
    file: Path
    latex: bool
    models: list[str]
    save: bool
    size: list[float | int]
    title: str
    type: str
    xlabel: str
    ylabel: str
    # yaxis_rhs: RhsAxis | None


def validate_schema(din: dict) -> bool:
    """Determines if the input dictionary is a valid Figure schema."""

    # TODO: DRY out code, repeated here at in histogram.py
    try:
        validated_data = figure_schema.validate(din)
        print("Valid: Validated data:", validated_data)
    except SchemaError as e:
        print("Error: Validation error:", e)

    return True


def new(db: dict) -> Figure:
    """Given a dictionary, validates the data from the
    dictionary, and if valid, creates a Figure."""

    validate_schema(db)

    ff = Figure(
        details=db["details"],
        display=db["display"],
        dpi=db["dpi"],
        folder=Path(db["folder"]).expanduser(),
        file=Path(db["folder"]).expanduser().joinpath(db["file"]),
        latex=db["latex"],
        models=db["models"],
        save=db["save"],
        size=db["size"],
        title=db["title"],
        type=db["type"],
        xlabel=db["xlabel"],
        ylabel=db["ylabel"],
    )

    assert ff.folder.is_dir(), f"Folder {ff.folder} does not exist."
    ext = ff.file.suffix
    file_types = (".pdf", ".png", ".svg")
    assert ext in file_types, f"File type {ext} not in {file_types}"

    # TODO: finish
    return ff


def plot_histogram(ff: Figure, hh: histogram.Histogram) -> None:
    """Plot the figure and histogram."""

    print(f"Number of elements: {len(hh.data)}")
    # n_neg = [x <= 0.0 for x in bb]

    # breakpoint()
    # Create the histogram
    fig, ax = plt.subplots(dpi=ff.dpi)
    # plt.hist(data, bins=20, color="blue", alpha=0.7, log=True)
    ax.hist(
        hh.data,
        **hh.plot_kwargs,
    )

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
