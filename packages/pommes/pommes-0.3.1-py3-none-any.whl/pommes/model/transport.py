"""Module related to inter-zone resource transport."""

import numpy as np
import xarray as xr
from linopy import Constraint, Model
from xarray import Dataset


def add_transport(
    model: Model,
    model_parameters: Dataset,
    annualised_totex_def: Constraint,
    operation_adequacy_constraint: Constraint,
) -> Model:
    """
    Add transport-related components to the Linopy model.

    Including variables, constraints, and costs related to energy transport
    between areas.

    Args:
        model (linopy.Model):
            The Linopy model to which transport-related elements will be added.
        model_parameters (xarray.Dataset):
            Dataset containing energy system parameters, including transport
            capacity limits, network topology, and costs.
        annualised_totex_def (linopy.Constraint):
            Constraint defining annualised total expenditures (totex), which
            will be updated with transport-specific costs.
        operation_adequacy_constraint (linopy.Constraint):
            Constraint ensuring operational adequacy, enforcing supply-demand
            balance, which will be updated with transport-related contributions.

    Returns:
        linopy.Model:
            The updated Linopy model with added transport-related variables,
            costs, and constraints.

    Note:
        This function introduces the following elements into the model:

        **Variables**

        - *Operation*
            - ``operation_transport_power_capacity``
                Represents the operational power capacity for transport
                technologies on each link and operational year.
            - ``operation_transport_power``
                Represents the power flow for transport technologies by link,
                hour, and operational year.
            - ``operation_transport_net_generation``
                Represents the net energy transferred between areas, accounting
                for inflows and outflows.
            - ``operation_transport_costs``
                Represents operational costs associated with transport
                technologies for each area and operational year.

        - *Planning*
            - ``planning_transport_power_capacity``
                Represents the planned power capacity investments in transport
                infrastructure.
            - ``planning_transport_costs``
                Represents planning costs associated with transport investments.

        **Constraints**

        - *Operation*
            - ``operation_transport_power_max_constraint``
                Limits operational power flow to available capacity.
            - ``operation_transport_net_generation_def``
                Defines net energy flow for transport between different areas.

        - *Planning*
            - ``planning_transport_power_capacity_min_constraint``
                Enforces a lower limit on planned transport power investments.
            - ``planning_transport_power_capacity_max_constraint``
                Enforces an upper limit on planned transport power investments.

        - *Costs*
            - ``operation_transport_costs_def``
                Defines operational transport costs based on fixed costs and
                power capacity.
            - ``planning_transport_costs_def``
                Defines planning costs for transport investments, considering
                annuities.

        These additions ensure that transport infrastructure operates within
        technical and economic limits, allowing the model to simulate energy
        transport flows realistically.
    """
    m = model
    p = model_parameters

    # ------------
    # Variables
    # ------------

    # Operation - transport

    operation_transport_power_capacity = m.add_variables(
        name="operation_transport_power_capacity",
        lower=0,
        coords=[p.link, p.transport_tech, p.year_op],
    )

    operation_transport_power = m.add_variables(
        name="operation_transport_power",
        lower=0,
        coords=[p.link, p.transport_tech, p.hour, p.year_op],
    )

    # Operation - transport intermediate variables

    operation_transport_net_generation = m.add_variables(
        name="operation_transport_net_generation",
        coords=[p.area, p.hour, p.transport_tech, p.resource, p.year_op],
        mask=np.equal(p.transport_resource, p.resource).any(
            [dim for dim in ["link"] if dim in p.transport_resource.dims]
        ),
    )

    # Planning - transport

    planning_transport_power_capacity = m.add_variables(
        name="planning_transport_power_capacity",
        lower=0,
        coords=[p.link, p.transport_tech, p.year_dec, p.year_inv],
        mask=xr.where(
            cond=p.transport_early_decommissioning,
            x=(p.year_inv < p.year_dec)
            * (p.year_dec <= p.transport_end_of_life)
            * np.logical_or(
                p.year_dec <= p.year_inv.max(),
                p.year_dec == p.transport_end_of_life,
            ),
            y=p.year_dec == p.transport_end_of_life,
        ),
    )

    # Costs - transport

    operation_transport_costs = m.add_variables(
        name="operation_transport_costs",
        lower=0,
        coords=[p.area, p.transport_tech, p.year_op],
    )

    planning_transport_costs = m.add_variables(
        name="planning_transport_costs",
        lower=0,
        coords=[p.area, p.transport_tech, p.year_op],
    )

    # ------------------
    # Objective function
    # ------------------

    m.objective += (operation_transport_power * p.transport_hurdle_costs).sum()
    annualised_totex_def.lhs += (
        operation_transport_costs + planning_transport_costs
    ).sum(["transport_tech"])

    # --------------
    # Constraints
    # --------------

    # Adequacy constraint

    operation_adequacy_constraint.lhs += (
        operation_transport_net_generation.sum("transport_tech")
    )

    # Operation - transport

    m.add_constraints(
        operation_transport_power - operation_transport_power_capacity <= 0,
        name="operation_transport_power_max_constraint",
    )

    # Operation - transport intermediate variables

    m.add_constraints(
        -operation_transport_power_capacity
        + planning_transport_power_capacity.where(
            (p.year_inv <= p.year_op) * (p.year_op < p.year_dec)
        ).sum(["year_dec", "year_inv"])
        == 0,
        name="operation_transport_power_capacity_def",
    )

    m.add_constraints(
        -operation_transport_net_generation
        + p.time_step_duration
        * (
            operation_transport_power.where(p.area == p.transport_area_to).sum(
                "link"
            )
            - operation_transport_power.where(
                p.area == p.transport_area_from
            ).sum("link")
        ).where(
            np.equal(p.transport_resource, p.resource).any(
                [
                    dim
                    for dim in ["link", "year_inv"]
                    if dim in p.transport_resource.dims
                ]
            )
        )
        == 0,
        name="operation_transport_net_generation_def",
        mask=np.equal(p.transport_resource, p.resource).any(
            [dim for dim in ["link"] if dim in p.transport_resource.dims]
        ),
    )

    # Planning - transport

    m.add_constraints(
        planning_transport_power_capacity.sum("year_dec")
        >= p.transport_power_capacity_investment_min,
        name="planning_transport_power_capacity_min_constraint",
        mask=np.isfinite(p.transport_power_capacity_investment_min)
        * np.not_equal(
            p.transport_power_capacity_investment_min,
            p.transport_power_capacity_investment_max,
        ),
    )

    m.add_constraints(
        planning_transport_power_capacity.sum("year_dec")
        <= p.transport_power_capacity_investment_max,
        name="planning_transport_power_capacity_max_constraint",
        mask=np.isfinite(p.transport_power_capacity_investment_max)
        * np.not_equal(
            p.transport_power_capacity_investment_min,
            p.transport_power_capacity_investment_max,
        ),
    )

    m.add_constraints(
        planning_transport_power_capacity.sum("year_dec")
        == p.transport_power_capacity_investment_min,
        name="planning_transport_power_capacity_def",
        mask=np.isfinite(p.transport_power_capacity_investment_max)
        * np.equal(
            p.transport_power_capacity_investment_min,
            p.transport_power_capacity_investment_max,
        ),
    )

    # Costs - transport

    m.add_constraints(
        -operation_transport_costs
        # No variable costs in the model for transport
        + 0.5
        * (
            (p.transport_fixed_cost * operation_transport_power_capacity)
            .where(
                np.logical_or(
                    p.area == p.transport_area_from,
                    p.area == p.transport_area_to,
                )
            )
            .sum("link")
        )
        == 0,
        name="operation_transport_costs_def",
    )

    m.add_constraints(
        -planning_transport_costs
        + 0.5
        * (
            (
                p.transport_annuity_cost * planning_transport_power_capacity
            ).where(
                np.logical_or(
                    p.area == p.transport_area_from,
                    p.area == p.transport_area_to,
                )
            )
        )
        .sum(["link"])
        .where((p.year_inv <= p.year_op) * (p.year_op < p.year_dec))
        .sum(["year_dec", "year_inv"])
        .where(
            cond=p.transport_annuity_perfect_foresight,
            other=(
                (
                    (
                        planning_transport_power_capacity.sum("year_dec")
                        * p.transport_annuity_cost.min(
                            [
                                dim
                                for dim in ["year_dec"]
                                if dim in p.transport_annuity_cost.dims
                            ]
                        )
                    ).where(
                        np.logical_or(
                            p.area == p.transport_area_from,
                            p.area == p.transport_area_to,
                        )
                    )
                )
                .where(
                    (p.year_inv <= p.year_op)
                    * (p.year_op < p.transport_end_of_life)
                )
                .sum(["link", "year_inv"])
            ),
        )
        == 0,
        name="planning_transport_costs_def",
    )

    return m
