"""Module to write in model flexible demand related constraints."""

import numpy as np
import xarray as xr
from linopy import Constraint, Model
from xarray import Dataset


def add_flexibility(
    model: Model,
    model_parameters: Dataset,
    operation_adequacy_constraint: Constraint,
) -> Model:
    m = model
    p = model_parameters

    flexibility_demand = p.flexibility_demand
    for dim in ["area","resource","year_op","hour"]:
        if dim not in flexibility_demand.dims:
            flexibility_demand = flexibility_demand.expand_dims(dim={dim: p[dim]})

    conservation_hrs = p.flexibility_conservation_hrs
    for dim in ["area","year_op","resource"]:
        if dim not in conservation_hrs.dims:
            conservation_hrs = conservation_hrs.expand_dims(dim={dim: p[dim]})


    # ------------
    # Variables
    # ------------

    operation_flexibility_demand = m.add_variables(
        name="operation_flexibility_demand",
        lower=0,
        coords=[p.area, p.resource, p.hour, p.year_op],
    )

    # --------------
    # Constraints
    # --------------
    #
    # Adequacy constraint

    operation_adequacy_constraint.lhs += -operation_flexibility_demand

    # Ratio constraints

    m.add_constraints(operation_flexibility_demand - p.flexibility_demand * p.flexibility_maxload_ratio <=0,
                      name="operation_flexibility_demand_max")

    m.add_constraints(operation_flexibility_demand - p.flexibility_demand * p.flexibility_minload_ratio >= 0,
                      name="operation_flexibility_demand_min")

    # Conservation constraint
    m.add_constraints(operation_flexibility_demand.sum("hour") - flexibility_demand.sum("hour") == 0,
                      name="operation_flexibility_demand_conservation"
    )



    for res in p.resource.values:
        for area in p.area.values:
            for year in p.year_op.values:
                cons_hr = conservation_hrs.sel(year_op=year, resource=res, area=area).values
                if cons_hr > 0:
                    hours = p.hour.values
                    hour_min = hours.min()
                    hour_max = hours.max()

                    # Calculate group labels relative to the minimum hour
                    hour_groups = (hours - hour_min) // cons_hr

                    # Filter to only include complete groups
                    max_complete_hour = (
                        hour_min + ((hour_max - hour_min) // cons_hr) * cons_hr
                    )
                    valid_mask = hours < max_complete_hour

                    # Create a DataArray with group labels
                    hour_group_da = xr.DataArray(
                        hour_groups, coords={"hour": hours}, dims=["hour"]
                    )

                    # Create constraint using groupby
                    flex_demand_sel = operation_flexibility_demand.sel(
                        resource=res, area=area, year_op=year
                    )
                    target_demand_sel = flexibility_demand.sel(
                        resource=res, area=area, year_op=year
                    )

                    # Apply mask and group by hour groups
                    constraint_lhs = flex_demand_sel.where(
                        valid_mask, drop=False
                    ).groupby(hour_group_da).sum(
                        "hour"
                    ) - target_demand_sel.where(
                        valid_mask, drop=False
                    ).groupby(hour_group_da).sum("hour")

                    m.add_constraints(
                        constraint_lhs == 0,
                        name=f"operation_flexibility_demand_conservation_{res}_{area}_{year}",
                    )

    # Ramp constraints
    m.add_constraints(
        (operation_flexibility_demand
        - operation_flexibility_demand.shift(hour=1)) / p.time_step_duration
        - p.flexibility_ramp_up * flexibility_demand
        <= 0,
        name="operation_flexibility_demand_ramp_up_constraint",
        mask=np.isfinite(p.flexibility_ramp_up) * (p.hour != p.hour[0]),
    )

    m.add_constraints(
        (operation_flexibility_demand.shift(hour=1)
        - operation_flexibility_demand) / p.time_step_duration
        -p.flexibility_ramp_down * flexibility_demand
        <= 0,
        name="operation_flexibility_demand_ramp_down_constraint",
        mask=np.isfinite(p.flexibility_ramp_down) * (p.hour != p.hour[0]),
    )



    # TODO add eventually some costs

    return m