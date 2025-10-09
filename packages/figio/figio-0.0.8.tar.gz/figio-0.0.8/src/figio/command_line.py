"""This module, command_line.py, is the new command line entry point, which
accepts input files of type .yml.
"""

import argparse
from pathlib import Path

# import figio.constants as cc
from figio.factory import XYFactory
from figio import composite, figure, histogram
from figio.xymodel import XYModel, XYModelAbaqus
from figio.xyview import XYView, XYViewAbaqus
from figio.yml_to_dict import yml_to_dict


def command_line(fin: Path) -> bool:
    """Given a .yml file, processes it to create a figure.

    Args:
        fin: The fully pathed input file.

    Returns
        True if successful, False otherwise.
    """
    processed = False

    db = yml_to_dict(fin=fin)

    items = []  # cart of items is empty, fill from factory
    # factory = XYFactory()  # it's static!

    print("====================================")
    print("Information")
    print("For (x, y) data and time series data:")
    print("  type: xymodel items associate with type: xyview items.")
    print("For histogram data:")
    print("  type: hmodel items associate with type: hview items.")
    print("====================================")

    for item in db:

        # if item.startswith("hmodel"):
        if db[item]["type"] == "hmodel":
            i = histogram.new(guid=item, db=db[item])
            items.append(i)

        # elif item.startswith("hfigure"):
        elif db[item]["type"] == "hview":
            i = figure.new(db[item])
            items.append(i)

        else:
            kwargs = db[item]
            i = XYFactory.create(item, **kwargs)
            if i:
                items.append(i)
            else:
                warn_msg = "Item is None from factory,"
                warn_msg += " nothing added to command_line items."
                print(warn_msg)

    hists = [i for i in items if isinstance(i, histogram.Histogram)]
    figures = [i for i in items if isinstance(i, figure.Figure)]

    # TODO: finish iteration
    for item in figures:

        print(f"Draw models: {item.models} on: {item.file.name}")
        models = [hh for hh in hists if hh.guid in item.models]

        # make a composite view
        # a_view = view.View(figure=item, models=view_models)
        a_comp = composite.Composite(figure=item, models=models)

        composite.plot_composite(a_comp)

    # TODO: refactor old models and views into above form
    models = [i for i in items if isinstance(i, (XYModel, XYModelAbaqus))]
    views = [i for i in items if isinstance(i, (XYView, XYViewAbaqus))]

    for view in views:
        print(f'Creating view with guid = "{view.guid}"')

        if view.model_keys:  # register only selected models with current view
            print(f"  Adding {view.model_keys} model(s) to current view.")
            view.models = [m for m in models if m.guid in view.model_keys]
            if len(view.models) == 0:
                warn_msg = "Warning:\n"
                warn_msg += "  Current view has no associated models.\n"
                warn_msg += "  Check the view 'model_keys' match with'\n"
                warn_msg += "  'xymodel_*' in the .yml file."
                print(warn_msg)
            view.figure()  # must be within this subset scope
        else:
            print("  Adding all models to current view.")
            view.models = models  # register all models with current view
            view.figure()  # must be within this subset scope

    print("====================================")
    print("End of figio execution.")

    processed = True  # overwrite
    return processed  # success if we reach this line


def main():
    """Runs the module from the command line."""
    # print(cl.BANNER)
    # print(cl.CLI_DOCS)
    parser = argparse.ArgumentParser(
        prog="figio",
        description="Generate a figure.",
        epilog="figio finished",
    )
    parser.add_argument(
        "input_file", help="the .yml recipe used to create the figure"
    )

    args = parser.parse_args()
    if args.input_file:
        aa = Path(args.input_file).expanduser()
        if aa.is_file():
            print(f"Processing file: {aa}")
            command_line(fin=aa)
        else:
            print(f"Error: could not find file: {aa}")


if __name__ == "__main__":
    main()
