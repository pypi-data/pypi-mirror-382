"""This modules test that schema."""

from pathlib import Path
import yaml

from figio.schema import valid_model


def test_model_schema():
    """WIP"""

    fa = Path(__file__).parent.joinpath("input", "rigid_body_ang_pos.yml")
    # breakpoint()
    assert fa.is_file()
    with open(str(fa), "r") as file:
        da = yaml.safe_load(file)

    assert valid_model(da)
    # assert not valid_model({"folder": "folder", "file": "file"})
