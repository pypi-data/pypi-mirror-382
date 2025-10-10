import numpy as np
import pytest
import xarray as xr
from numpy.testing import assert_array_equal as assert_equal

from pommes.model.build_model import build_model


@pytest.fixture()
def parameter_net_import(parameters_dispatch_invest, net_import):
    p = xr.merge([parameters_dispatch_invest, net_import])
    return p


@pytest.fixture()
def parameter_net_import_single_horizon(parameter_net_import):
    p = parameter_net_import.sel(
        area=["area_1"],
        year_dec=[2040],
        year_inv=[2020],
        year_op=[2020],
    )
    return p


def test_net_import(parameter_net_import_single_horizon):
    p = parameter_net_import_single_horizon.sel(
        conversion_tech=["ocgt", "wind_onshore"],
        hour=[3, 4, 5],
        resource=["electricity", "methane"],
    )
    # Values here corresponds built for a 3 hours operation year duration
    p.operation_year_duration[:] = p.time_step_duration.sum().values
    model = build_model(p)
    model.solve(solver_name="highs")
    s = model.solution.dropna(dim="year_dec", how="all").squeeze()

    assert_equal(
        s.planning_conversion_power_capacity.to_numpy(), np.array([10, 25])
    )
    assert_equal(
        s.operation_conversion_power.to_numpy(),
        np.array([[10.0, 5.0, 0.0], [0.0, 5.0, 10.0]]),
    )
    assert_equal(
        s.operation_net_import_import.sel(resource="methane").to_numpy(),
        np.array([15, 7.5, 0]),
    )

    assert_equal(
        s.operation_load_shedding_power.to_numpy(),
        np.array([[np.nan, 0], [np.nan, 0], [np.nan, 0]]),
    )
    assert_equal(
        s.operation_spillage_power.to_numpy(), np.array([[0, 0], [0, 0], [0, 0]])
    )

    assert model.objective.value == 1120.0


def test_net_import_with_differentiated_prices(
    parameter_net_import_single_horizon,
):
    """
    Test the net import behavior of the model when export prices differ from import prices.
    """
    parameters = parameter_net_import_single_horizon.sel(
        conversion_tech=["wind_onshore"],
        hour=[3, 4, 5],
        resource=["electricity"],
    )

    # No limit for imports and export
    parameters.net_import_max_yearly_energy_import.loc[
        {"resource": "electricity"}
    ] = 1000
    parameters.net_import_max_yearly_energy_export.loc[
        {"resource": "electricity"}
    ] = 1000

    # Max wind capacity of 50 MW
    parameters["conversion_power_capacity_max"] = xr.DataArray(
        [50],
        dims="conversion_tech",
        coords={"conversion_tech": ["wind_onshore"]},
    )

    # Import price < wind LCOE, to avoid importing all the electricity
    parameters.net_import_import_price.loc[{"resource": "electricity"}] = 20
    # Export price > wind LCOE, to install the max wind capacity
    parameters.net_import_export_price.loc[{"resource": "electricity"}] = 18

    parameters.operation_year_duration[:] = (
        parameters.time_step_duration.sum().values
    )
    model = build_model(parameters)
    model.solve(solver_name="highs")
    solution = model.solution.dropna(dim="year_dec", how="all").squeeze()

    assert_equal(
        solution.operation_net_import_import.to_numpy(), np.array([10, 0, 0])
    )
    assert_equal(
        solution.operation_net_import_export.to_numpy(), np.array([0, 0, 10])
    )
    assert_equal(
        solution.planning_conversion_power_capacity.to_numpy(), np.array([50])
    )

    export_volumes = solution.operation_net_import_export.to_numpy()
    import_volumes = solution.operation_net_import_import.to_numpy()
    total_costs = (
        (import_volumes * parameters.net_import_import_price.values).sum()
        - (export_volumes * parameters.net_import_export_price.values).sum()
        + solution.planning_conversion_power_capacity.values * 10
    )
    assert np.isclose(
        model.objective.value, total_costs
    ), "Objective value mismatch"


def test_max_yearly_import_two_areas(parameters_dispatch_invest,
                                         transport, net_import):
    p = xr.merge([parameters_dispatch_invest, transport, net_import])

    p = p.sel(
              transport_tech=["power_line"], link=["link_1"], hour=[0],
        resource=["electricity"], year_dec=[2040, 2050], year_inv=[2030],
        year_op=[2030], ).copy(deep=True)
    p = p.drop_dims("conversion_tech")

    p["operation_year_duration"] = 1.

    p["demand"] = p["demand"].expand_dims(area=p.area).copy()
    p.demand.loc[dict(area="area_1")] = 0.

    max_import = "net_import_max_yearly_energy_import"
    p[max_import] = p[max_import].expand_dims(area=p.area).copy()
    p[max_import].loc[dict(resource="electricity")] = [np.nan, 0]

    p["conversion"] = False

    p["transport_power_capacity_investment_min"] = 10
    p["transport_power_capacity_investment_max"] = 10

    p["transport_invest_cost"] = 0
    p["transport_annuity_cost"] = 0
    p["transport_fixed_cost"] = 0

    p["net_import_import_price"] = 1

    model = build_model(p)
    model.solve(solver_name="highs")
    solution = model.solution.dropna(dim="year_dec", how="all").squeeze()

    assert_equal(solution.operation_net_import_import.to_numpy(),
        np.array([10, 0]))
    assert_equal(solution.operation_net_import_export.to_numpy(),
        np.array([0, 0]))

    assert np.isclose(model.objective.value, 10. + 10 * 0.01)


def test_max_yearly_export_two_areas(parameters_dispatch_invest,
                                         transport, net_import):
    p = xr.merge([parameters_dispatch_invest, transport, net_import])

    p = p.sel(conversion_tech=["wind_onshore"],
              transport_tech=["power_line"], link=["link_1"], hour=[0],
        resource=["electricity"], year_dec=[2040, 2050], year_inv=[2030],
        year_op=[2030], ).copy(deep=True)

    p["operation_year_duration"] = 1.

    p["demand"] = 0.
    p["conversion_invest_cost"] = 0
    p["conversion_annuity_cost"] = 0
    p["spillage_max_capacity"] = 0
    p["transport_invest_cost"] = 0
    p["transport_annuity_cost"] = 0
    p["transport_fixed_cost"] = 0
    p["net_import_import_price"] = 1

    p["transport_power_capacity_investment_min"] = 10
    p["transport_power_capacity_investment_max"] = 10

    max_export = "net_import_max_yearly_energy_export"
    p[max_export] = p[max_export].expand_dims(area=p.area).copy()
    p[max_export].loc[
        dict(area=["area_1", "area_2"], resource="electricity")
    ] = [0., 10.]

    c_inv_min = "conversion_power_capacity_investment_min"
    p[c_inv_min] = p[c_inv_min].expand_dims(area=p.area).copy()
    p[c_inv_min].loc[dict(area=["area_1", "area_2"])] = [20., 0.]

    c_inv_max = "conversion_power_capacity_investment_max"
    p[c_inv_max] = p[c_inv_max].expand_dims(area=p.area).copy()
    p[c_inv_max].loc[dict(area=["area_1", "area_2"])] = [20., 0.]

    model = build_model(p)
    model.solve(solver_name="highs")
    solution = model.solution.dropna(dim="year_dec", how="all").squeeze()

    assert_equal(solution.operation_net_import_import.to_numpy(),
        np.array([0, 0]))
    assert_equal(solution.operation_net_import_export.to_numpy(),
        np.array([0, 10]))

    assert np.isclose(model.objective.value, 10 * 0.01)
