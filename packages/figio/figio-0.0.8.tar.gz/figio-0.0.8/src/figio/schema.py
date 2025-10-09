"""Module to define schema types."""

# from pathlib import Path
from typing import NamedTuple, Any
from schema import Schema, And, Use, Optional, SchemaError


def valid_model(din: dict) -> bool:
    """Determines if the input dictionary is a valid Model schema."""
    # Validate the example data

    # Define the schema for the Model class
    model_schema = Schema(
        {
            "folder": And(str, len),  # "folder" must be a non-empty string
            "file": And(str, len),  # "file" must be a non-empty string
            "plot_kwargs": dict,  # "plot_kwargs" must be a dictionary
            "skip_rows": And(
                Use(int), lambda n: n >= 0
            ),  # "skip_rows" must be a non-negative integer
            "ycolumn": And(
                Use(int), lambda n: n >= 0
            ),  # "ycolumn" must be a non-negative integer
        }
    )

    try:
        validated_data = model_schema.validate(din)
        print("Valid: Validated data:", validated_data)
    except SchemaError as e:
        print("Error: Validation error:", e)

    return True
