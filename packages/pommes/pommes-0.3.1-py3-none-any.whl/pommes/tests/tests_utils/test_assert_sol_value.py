"""Module to test assert_sol_value in utils."""

import numpy as np
import pytest
import xarray as xr

from pommes.model.build_model import build_model
from pommes.utils import assert_sol_value


def test_assert_sol_value_vector_match():
    s = xr.Dataset({"v": (["t"], np.array([1.0, 2.0], dtype=float))})
    assert_sol_value(s, "v", [1.0, 2.0])


def test_assert_sol_value_matrix_match_with_nested_list():
    s = xr.Dataset(
        {"m": (["i", "j"], np.array([[1.0, 2.0], [3.0, 4.0]], dtype=float))}
    )
    assert_sol_value(s, "m", [[1.0, 2.0], [3.0, 4.0]])


def test_assert_sol_value_with_decimal_tolerance_passes():
    s = xr.Dataset({"v": (["t"], np.array([1.0000001], dtype=float))})
    # Close enough at 6 decimals
    assert_sol_value(s, "v", [1.0], decimal=6)


def test_assert_sol_value_raises_on_mismatch():
    s = xr.Dataset({"v": (["t"], np.array([1.01], dtype=float))})
    # 0.01 difference should fail at 3 decimals
    with pytest.raises(AssertionError):
        assert_sol_value(s, "v", [1.0], decimal=3)


def test_assert_sol_value_raises_on_missing_variable():
    s = xr.Dataset({"v": (["t"], np.array([1.0], dtype=float))})
    with pytest.raises(KeyError):
        assert_sol_value(s, "nonexistent", [1.0])


def test_assert_sol_value(parameters_simple):
    p = parameters_simple.copy(deep=True)

    p["load_shedding_max_capacity"] = np.nan
    p["load_shedding_cost"] = 100  # €/Mwh

    model = build_model(p)
    model.solve(solver_name="highs")
    s = model.solution.squeeze()

    assert_sol_value(s, "operation_load_shedding_power", [0, 0])
    assert_sol_value(s, "operation_conversion_power", [10, 10])
    assert_sol_value(s, "operation_conversion_power_capacity", [20, 20])
    assert_sol_value(s, "planning_conversion_costs", [200.0, 200.0])
