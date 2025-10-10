"""Module adding retrofit to the linopy Model."""

from linopy import Constraint, Model
from xarray import Dataset


def add_retrofit(
    model: Model,
    model_parameters: Dataset,
    annualised_totex_def: Constraint,
    operation_year_normalization: float,
    operation_adequacy_constraint: Constraint,
) -> Model:
    """
        Add retrofit-related components to the Linopy model.

        Including variables, constraints, and costs related to retrofit.

    Args:
        model (linopy.Model):
            The Linopy model to which retrofit-related elements will be added.

        model_parameters (xarray.Dataset):
            Dataset containing energy system parameters, including retrofit
            transition factors and eligible technologies.
        annualised_totex_def (linopy.Constraint):
            Constraint defining annualised total expenditures (totex), which
            will be updated with retrofit-specific costs.
        operation_adequacy_constraint (linopy.Constraint):
            Constraint ensuring operational adequacy, enforcing supply-demand
            balance, which will be updated with retrofit-related contributions.
        operation_year_normalization (linopy.Constraint):
            Normalization factor for operational year durations.

    Returns:
        linopy.Model:
            The updated Linopy model with added retrofit-related variables,
            constraints, and transition mechanics.

    Note:
        This function introduces the following elements into the model:

        **Variables**

       -  *Planning*
          - planning_retrofit_power_capacity:
          Decision variables representing the capacity transferred from a source technology
          to a target technology via retrofit. It is indexed by area, year of investment,
          source technology, retrofit year, target technology, and year of decommissioning.
          - retrofit_factor:
          retrofit factor from conversion technology c_1 to c [%]




      -  *Costs*
         - planning_retrofit_costs:
           investment cost associated with retrofit by area and operation year

        **Constraints**

      - *Planning*
        - retrofit_capacity_def:
        ensures that the operational conversion capacity for a technology c is equal to the sum
         of the capacity directly invested in techno c and the capacity resulting from
         retrofitting a technology c1 to c weighted by a retrofit factor.

        - retrofit_cap_constraint:
        ensures that the transferred capacity from a source technology (c) to a retrofitted
        technology (c2) can not exceed the sum of the directly invested capacity in tech c
        and the capacity of c obtained from retrofitting another technology c1

        - Transoperation_conversion_power_max_constraint:
        Limits retrofit investments to the available operational
        conversion capacity from previous years.

      - *Costs*
        - retrofit_costs_def:
        defines planning costs for retrofitting by area and year of operation

    """
    m = model
    p = model_parameters

    # ------------
    # Variables
    # ------------
    # Planning - retrofit
    planning_retrofit_power_capacity = m.add_variables(
        name="planning_retrofit_power_capacity",
        lower=0,
        coords=[
            p.area,
            p.year_inv,
            p.retrofit_tech_from,
            p.retrofit_year,
            p.retrofit_tech_to,
            p.year_dec,
        ],
        mask=p.retrofit_factor > 0,
    )

    # Costs - retrofit
    planning_retrofit_costs = m.add_variables(
        name="planning_retrofit_costs",
        lower=0,
        coords=[p.area, p.year_op],
    )

    # ------------
    # Objective function
    # ------------
    annualised_totex_def.lhs += planning_retrofit_costs.sum(
        dim=["area", "year_op"]
    )

    # ------------
    # Constraints
    # ------------
    # Planning - retrofit
    # retrofit_capacity_def
    m.add_constraints(
        -m.variables.operation_conversion_power_capacity
        + (
            p.planning_conversion_power_capacity.where(
                (p.year_inv <= p.year_op) & (p.year_op < p.year_dec)
            ).sum(dim=["year_inv", "year_dec"])
            + (planning_retrofit_power_capacity * p.retrofit_factor)
            .where((p.retrofit_year <= p.year_op) & (p.year_op < p.year_dec))
            .sum(
                dim=[
                    "year_inv",
                    "retrofit_tech_from",
                    "retrofit_year",
                    "retrofit_tech_to",
                    "year_dec",
                ]
            )
        )
        == 0,
        name="retrofit_capacity_def",
    )

    # retrofit_cap_constraint
    retrofit_subset = planning_retrofit_power_capacity.where(
        planning_retrofit_power_capacity.coords["year_dec"]
        == planning_retrofit_power_capacity.coords["retrofit_year"],
        drop=True,
    )
    lhs = retrofit_subset.sum(dim=["retrofit_tech_to", "year_dec"])
    # direct investment capacity
    rhs_direct = (
        m.variables.planning_conversion_power_capacity.sel(
            conversion_tech="smr_ccs", drop=True
        )
        .where(
            m.variables.planning_conversion_power_capacity.coords["year_dec"]
            == retrofit_subset.coords["retrofit_year"],
            drop=True,
        )
        .sum(dim=["year_inv"])
    )
    # retrofit investment from techno source smr
    rhs_retro = retrofit_subset.where(
        retrofit_subset.coords["tech_to"]
        == retrofit_subset.coords["tech_from"],
        drop=True,
    ).sum(dim=["year_inv", "retrofit_tech_from"])

    # rhs total
    rhs = rhs_retro + rhs_direct

    m.add_constraints(lhs <= rhs, name="retrofit_cap_constraint")

    m.add_constraints(
        planning_retrofit_power_capacity.sum(dim="retrofit_tech_to").rename(
            {"retrofit_tech_from": "conversion_tech"}
        )
        - m.variables.operation_conversion_power_capacity.rename(
            {"year_op": "year_inv"}
        )
        .sel(conversion_tech=p.retrofit_tech_from.values)
        .shift(year_inv=1)
        <= 0,
        name="Transoperation_conversion_power_max_constraint",
    )

    # Costs - retrofit
    m.add_constraints(
        -planning_retrofit_costs
        + (
            (planning_retrofit_power_capacity * p.retrofit_annuity_cost)
            .where((p.retrofit_year <= p.year_op) & (p.year_op < p.year_dec))
            .sum(
                dim=[
                    "year_inv",
                    "retrofit_tech_from",
                    "retrofit_year",
                    "retrofit_tech_to",
                    "year_dec",
                ]
            )
        ).where(
            cond=p.retrofit_annuity_perfect_foresight,
            other=(
                (
                    planning_retrofit_power_capacity.sum("year_dec")
                    * p.retrofit_annuity_cost.min(
                        [
                            dim
                            for dim in p.retrofit_annuity_cost.dims
                            if dim == "year_dec"
                        ]
                    )
                )
                .where(
                    (p.year_retrofit <= p.year_op)
                    * (p.year_op < p.retrofit_tech_from_end_of_life)
                )
                .sum(["year_retrofit"])
            ),
        )
        == 0,
        name="planning_retrofit_costs_def",
    )
    return m
