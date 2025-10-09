"""Test for the histogram type."""

import figio.histogram as histogram


def test_plot_kwargs():
    """Assures that known valid kwargs return True."""
    # Test with valid float linewidth
    valid = {"color": "blue", "linewidth": 2.0}
    assert histogram.validate_plot_kwargs(valid)

    # Test with valid integer linewidth
    valid_int = {"color": "red", "linewidth": 3}
    assert histogram.validate_plot_kwargs(valid_int)

    # Test with missing color (should be valid)
    valid_missing_color = {"linewidth": 1.5}
    assert histogram.validate_plot_kwargs(valid_missing_color)

    # Test with missing linewidth (should be valid)
    valid_missing_linewidth = {"color": "green"}
    assert histogram.validate_plot_kwargs(valid_missing_linewidth)

    # Test with negative linewidth
    invalid_negative = {"color": "blue", "linewidth": -4.0}  # Negative number
    assert not histogram.validate_plot_kwargs(invalid_negative)

    # Test with zero linewidth
    invalid_zero = {"color": "red", "linewidth": 0}  # Zero value
    assert not histogram.validate_plot_kwargs(invalid_zero)

    # Test with non-numeric linewidth
    invalid_non_numeric = {
        "color": "green",
        "linewidth": "thick",
    }  # Not a number
    assert not histogram.validate_plot_kwargs(invalid_non_numeric)

    # Test with extra keys (should still be valid)
    valid_extra_keys = {
        "color": "blue",
        "linewidth": 2.0,
        "extra_key": "value",
    }
    assert histogram.validate_plot_kwargs(valid_extra_keys)
