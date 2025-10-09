"""The histogram type, constructor, and methods."""

from typing import NamedTuple
from pathlib import Path

import numpy as np
from schema import Schema, And, Or, Use, Optional, SchemaError

from figio import utility

# Define the schema for plot_kwargs
plot_kwargs_schema = Schema(
    {
        Optional("alpha", default=1.0): And(
            Or(Use(float), Use(int)),  # must be a float or an int
            lambda n: n >= 0 and n <= 1,  # must be between 0 and 1
        ),  # Ensure alpha is a float between 0 and 1
        Optional("bins", default=20): And(
            Use(int), lambda n: n > 0
        ),  # Ensure bins is a positive integer
        Optional("color", default="black"): str,
        Optional("histtype", default="step"): str,
        Optional("label", default=""): str,
        Optional("linewidth", default=1.0): And(
            Or(Use(float), Use(int)),  # must be a float or an int
            lambda n: n > 0,  # must be positive
        ),  # Ensure linewidth is a positive float
        Optional("log", default=True): bool,
    },
    ignore_extra_keys=True,
)


class Histogram(NamedTuple):
    """The histogram type."""

    # bins: int
    # density: bool
    type: str
    data: np.ndarray
    folder: Path
    file: Path
    guid: str
    # histtype: str
    # orientation: str
    plot_kwargs: dict
    # rwidth: float
    skip_rows: int
    # stacked: bool
    # x: list[float]
    # y: list[float]
    ycolumn: int
    # yerr: list[float] | None


def validate_plot_kwargs(din: dict) -> bool:
    """Determines if the input dictionary is a valid plot_kwargs schema."""

    # TODO: DRY out code, repeated here at in figure.py
    try:
        validated_data = plot_kwargs_schema.validate(din)
        print("Valid: Validated data:", validated_data)
        return True
    except SchemaError as e:
        print("Error: Validation error:", e)
        return False


def new(guid: str, db: dict) -> Histogram:
    """Given a globally unique identifier string and a dictionary,
    validates the data from the dictionary, and if valid,
    creates a Histogram."""

    plot_kwargs = utility.get_default_values(schema=plot_kwargs_schema)
    print(f"Histogram default plot_kwargs: {plot_kwargs}")

    if "plot_kwargs" in db:
        user_kwargs = db["plot_kwargs"]
        plot_kwargs.update(user_kwargs)
        print(f"Histogram updated plot_kwargs: {plot_kwargs}")

    validate_plot_kwargs(plot_kwargs)

    type = db["type"]
    folder = Path(db["folder"]).expanduser()
    file = Path(db["folder"]).expanduser().joinpath(db["file"])
    assert folder.is_dir(), f"Folder does not exist: {folder}"
    assert file.is_file, f"File does not exist: {file}"

    # TODO: validate the entire schema, not just the kwargs below
    # then the next two checks are obsolete
    skip_rows = db["skip_rows"]
    ycolumn = db["ycolumn"]
    assert skip_rows >= 0, f"skip_rows must be >= 0: {skip_rows}"
    assert ycolumn >= 0, f"ycolumn must be >= 0: {ycolumn}"

    # load the data into the Histogram
    try:
        data = np.genfromtxt(
            str(file),
            dtype="float",
            delimiter=",",
            skip_header=db["skip_rows"],
            skip_footer=0,
            usecols=(db["ycolumn"]),
        )
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except OSError as e:
        print(f"I/O error: {e}")
    except TypeError as e:
        print(f"Type error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    hh = Histogram(
        type=type,
        folder=Path(db["folder"]).expanduser(),
        file=Path(db["folder"]).expanduser().joinpath(db["file"]),
        guid=guid,
        data=data,
        plot_kwargs=plot_kwargs,
        skip_rows=skip_rows,
        ycolumn=ycolumn,
    )

    return hh
