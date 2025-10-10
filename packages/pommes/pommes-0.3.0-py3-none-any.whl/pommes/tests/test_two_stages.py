"""Module to test the twos tage optimisation."""

import numpy as np
import pytest

from pommes.model.build_model import build_model
from pommes.solver.two_stages import add_second_stage_constraints
from pommes.utils import assert_sol_value


@pytest.fixture()
def parameters_two_stages(parameters_simple):
    """Fixture for two stage optimisation."""
    p = parameters_simple.copy()
    p.operation_year_duration[:] = p.time_step_duration.sum().values
    return parameters_simple


def test_two_stages_two_horizons(parameters_two_stages):
    p = parameters_two_stages.copy()

    # First stage scenario
    p["load_shedding_max_capacity"] = np.nan
    p["load_shedding_cost"] = 25  # €/Mwh
    p["conversion_must_run"][0] = 0

    # First stage model
    model1 = build_model(p)
    model1.solve(solver_name="highs")
    s1 = model1.solution.squeeze()

    assert_sol_value(s1, "operation_load_shedding_power", [0, 0])
    assert_sol_value(s1, "operation_conversion_power", [10, 10])
    assert_sol_value(s1, "operation_conversion_power_capacity", [20, 20])
    assert_sol_value(s1, "planning_conversion_costs", [200.0, 200.0])
    assert model1.objective.value == 200 * 2

    # Second stage scenario
    p["load_shedding_cost"] = (
        p["load_shedding_cost"].broadcast_like(p.year_op).copy()
    )
    p["load_shedding_cost"][1] = 1  # €/Mwh
    p["conversion_variable_cost"] = (
        p["conversion_variable_cost"].broadcast_like(p.year_op).copy()
    )
    p["conversion_variable_cost"][1] = 30  # €/Mwh

    # No non-anticipativity constraint
    model2 = build_model(p)
    model2.solve(solver_name="highs")
    s2 = model2.solution.squeeze()

    assert_sol_value(s2, "operation_load_shedding_power", [10, 10])
    assert_sol_value(s2, "operation_conversion_power", [0, 0])
    assert_sol_value(s2, "operation_conversion_power_capacity", [0, 0])
    assert_sol_value(s2, "planning_conversion_costs", [0, 0])
    assert model2.objective.value == 25 * 10 + 1 * 10

    # With non-anticipativity constraint
    horizon = 2040
    model3 = build_model(p)
    add_second_stage_constraints(model3, s1, horizon)
    model3.solve(solver_name="highs")
    s3 = model3.solution.squeeze()

    assert_sol_value(s3, "operation_load_shedding_power", [0, 10])
    assert_sol_value(s3, "operation_conversion_power", [10, 0])
    assert_sol_value(s3, "operation_conversion_power_capacity", [20, 20])
    assert_sol_value(s3, "planning_conversion_costs", [200.0, 200.0])
    assert model3.objective.value == 200 * 2 + 10 * 1

    assert True
