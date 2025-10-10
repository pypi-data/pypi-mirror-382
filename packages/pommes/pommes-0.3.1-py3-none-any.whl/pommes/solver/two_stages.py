"""
Module to run two stage optimisation.

First stage is run to get the optimal capacities for the given investment
horizon.

Second stage is run with the investment capacities found first stage with
other parameters for the further investment horizons.
"""

import linopy
import xarray as xr


def add_second_stage_constraints(
    model: linopy.Model, solution: xr.Dataset, horizon: int
) -> None:
    """
    Add the constraints fixing the invested capacities before the horizon.

    Args:
        model (linopy.Model): The Linopy model.
        solution (xr.Dataset): The solution dataset of the first stage problem.
        horizon (int): The Investment year threshold for the second stage.

    Returns:
        None.
    """
    v = model.variables
    s = solution
    year_dec = v.coords["year_dec"]
    year_inv = v.coords["year_inv"]

    model.add_constraints(
        v.planning_conversion_power_capacity
        == s.planning_conversion_power_capacity,
        name="pre_horizon_decommissioning_conversion_capacity_set",
        mask=year_dec <= horizon,
    )

    model.add_constraints(
        v.planning_conversion_power_capacity.sum("year_dec")
        == s.planning_conversion_power_capacity.sum("year_dec"),
        name="pre_horizon_investment_conversion_capacity_set",
        mask=year_inv < horizon,
    )
    return
