"""This module parses yml files into types."""

from pathlib import Path


# from schema import Schema, And, Or, Use, Optional, SchemaError
from schema import Schema, And, Or, SchemaError
import yaml


# from figio.xytypes import Resource
#
## Define the schema for the 'resource' key
# resource_schema = Schema(
#    Or(
#        {
#            "folder": And(Path, len),  # "folder" must be a non-empty Path
#            "file": And(str, len),  # "file" must be a non-empty string
#        },
#        None,
#    )
# )
#
## Define the main schema that includes the "base" key
# main_schema = Schema(
#    {
#        "resource": resource_schema,
#    },
#    ignore_extra_keys=True,  # Allow any additional keys
# )


def parse_model(input: dict) -> Model:
    """Parse the input dictionary into a Resource object."""
    # Validate the input data
    validated_data = resource_schema.validate(input)

    # Extract the "resource" data
    base_data = validated_data["resource"]

    # Create a Resource object
    if base_data is not None:
        return Resource(
            folder=Path(base_data["folder"]).expanduser(),
            file=Path(base_data["folder"])
            .expanduser()
            .joinpath(base_data["file"]),
        )
    else:
        return None


# Example data to validate
vd0 = {
    "base": {
        "folder": "~/autotwin/figio/tests/input",
        "file": "base.yml",
    }
}

vd1 = {"base": None}

fa = Path(__file__).parent.joinpath("displacement_sr2_new.yml")
assert fa.is_file()
with open(str(fa), "r") as file:
    da = yaml.safe_load(file)

# Validate the example data
for item in (vd0, vd1, da):
    try:
        validated_data = main_schema.validate(item)
        print(f"Valid: Validated data for {item}:\n\n", validated_data)
    except SchemaError as e:
        print(f"Error: Validation error for {item}:\n\n", e)

# for item in (vd0, vd1, da):
for item in (da,):
    if item.get("base") is not None:
        print("base is not None")
        base = Resource(
            folder=Path(item["base"]["folder"]).expanduser(),
            file=Path(item["base"]["folder"])
            .expanduser()
            .joinpath(item["base"]["file"]),
        )
        print(f"base.folder = {base.folder}")
        print(f"base.file = {base.file}")
        # breakpoint()
        assert base.folder.is_dir(), f"Error: folder not found {base.folder}"
        assert base.file.is_file(), f"Error: file not found {base.file}"
    else:
        print("base is None")

# breakpoint()


# fb = Path(__file__).parent.joinpath("displacement_sr2_new.yml")
# assert fb.is_file()
# with open(str(fb), "r") as file:
#    db = yaml.safe_load(file)

aa = 4
