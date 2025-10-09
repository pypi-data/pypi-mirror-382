"""This module is the factory, creator of models and views."""

from figio.xymodel import XYModel, XYModelAbaqus
from figio.xyview import XYView, XYViewAbaqus

# Figure Factory
FACTORY_ITEMS = {
    # "model": XYModel,
    # "view": XYView,
    "xymodel": XYModel,
    "xyview": XYView,
    "model_abaqus": XYModelAbaqus,
    "view_abaqus": XYViewAbaqus,
}


class XYFactory:
    """The one and only (singleton) factory for XY items."""

    @staticmethod
    def create(item, **kwargs):
        "Main factory method, returns XY objects."
        # if item.startswith("xymodel"):
        #     instance = XYModel
        # elif item.startswith("xyfigure"):
        #     instance = XYView
        # else:
        #     # instance = FACTORY_ITEMS.get(kwargs["class"], None)
        #     instance = FACTORY_ITEMS.get(kwargs["type"], None)
        # instance = FACTORY_ITEMS.get(kwargs["class"], None)
        instance = FACTORY_ITEMS.get(kwargs["type"], None)
        if instance:
            return instance(item, **kwargs)

        # If we get here, we did not return an instance, so warn.
        print(f"Warning: key 'class' specified uknown 'value' of '{item}'.")
        print("This key will be skipped.")
        return None
