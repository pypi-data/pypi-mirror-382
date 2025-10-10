import numpy as np
import pytest
import xarray as xr

from pommes.model.build_model import build_model


@pytest.fixture()
def parameters_flexible_demand(parameters_dispatch_invest, flexibility):
    return xr.merge([parameters_dispatch_invest, flexibility])


@pytest.fixture()
def parameters_flexible_demand_single_horizon(parameters_flexible_demand):
    p = parameters_flexible_demand
    p = p.sel(
        area=["area_1"],
        year_dec=[2040],
        year_inv=[2020],
        year_op=[2020],
    )
    return p.copy(deep=True)


def test_flexible_demand_single_horizon(parameters_flexible_demand_single_horizon):
    p = parameters_flexible_demand_single_horizon
    p = p.sel(
        conversion_tech=["wind_onshore"],
        resource=["electricity"],
        hour=[4, 5, 6, 7, 8, 9],
    )

    model = build_model(p)
    model.solve(solver_name="highs")
    s = model.solution.squeeze()

    np.testing.assert_array_equal(
        s.planning_conversion_power_capacity.to_numpy(), np.array([90.])
    )
    np.testing.assert_array_equal(
        s.operation_conversion_power.to_numpy(), np.array([18.0, 36.0, 72.0, 81.0, 54.0, 27.0])
    )

    np.testing.assert_array_equal(
        s.operation_flexibility_demand.to_numpy(), np.array([8.0, 12.0, 12.0, 8.0, 8.0, 12.0])
    )


    assert model.objective.value == 900.