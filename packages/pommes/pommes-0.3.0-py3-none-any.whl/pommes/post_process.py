"""Module for extracting and processing results from optimisation models."""

from typing import TypeVar

import numpy as np
import xarray as xr

from pommes.utils import select_dataset_variables_from_dims

XarrayObject = TypeVar("XarrayObject", xr.DataArray, xr.Dataset)


def reindex_from_tech_to_asset(
    x: XarrayObject,
    category: str,
) -> XarrayObject:
    """
    Reindex the given DataArray or Dataset to asset.

    By renaming the "{category}_tech" dimension to "asset".

    This function renames the dimension in the input object from
    "<category>_tech" to "asset", and assigns a new coordinate named
    "category" that has the same dimension as "asset".

    Args:
        x (xarray.DataArray | xarray.Dataset):
            The input xarray object whose dimension will be renamed.
        category (str):
            The category name used to build the dimension name
            "<category>_tech". For instance, if `category` is "foo", the
            dimension to be renamed is "foo_tech".

    Returns:
        xarray.DataArray | xarray.Dataset:
            A new xarray object with the renamed dimension ("asset") and an
            added "category" coordinate. Delete the {category} from all
            variables.
    """
    x = x.rename({f"{category}_tech": "asset"})

    def delete_category_in_name(name: str, cat: str) -> str:
        """Delete the category from the name."""
        name_list = name.split("_")
        name_list.remove(cat)
        new_name = "_".join(name_list)
        return new_name

    if isinstance(x, xr.DataArray) and category in x.name:
        x = x.rename(delete_category_in_name(str(x.name), category))

    if isinstance(x, xr.Dataset):
        x = x.rename(
            {
                variable: delete_category_in_name(str(variable), category)
                for variable in x.data_vars
                if category in variable
            }
        )

    x = x.assign_coords({"category": xr.DataArray(category, coords=[x.asset])})
    return x


def extract_variables(
    solution: xr.Dataset,
    var_names: str | list[str],
    res_name: str,
    res_dim: str,
    categories: list[str] | None = None,
) -> xr.DataArray:
    """Extract and combine variables from a solution dataset.

    # TODO: add transports and other modules

    This function extracts variables from the provided `solution` dataset that
    contain one or more of the specified `var_names` and organizes them along a
    new dimension specified by `res_dim` with the resulting data variable named
    `res_name`. The extraction is performed for each category in `categories`
    (defaulting to ["combined", "conversion", "storage"]). For each category, the
    dataset is filtered by variables (using a helper function to select variables
    based on a dimension), reindexed (via another helper function), and sorted by
    the "asset" coordinate. The results are concatenated along the "asset" dimension.
    Finally, the variable names are cleaned by removing the original `var_names`
    substrings and extraneous underscores.

    Args:
        solution (xr.Dataset): The input solution dataset.
        var_names (str | list[str]): A single variable name or a list of variable names
            to extract.
        res_name (str): The name of the resulting data variable.
        res_dim (str): The dimension along which the resulting data array will be created.
        categories (list[str] | None, optional): Categories to process. Defaults to
            ["combined", "conversion", "storage"] if not provided.

    Returns:
        xr.DataArray: The resulting data array with the combined and renamed variables.
    """
    if categories is None:
        categories = [
            cat
            for cat in ["combined", "conversion", "storage"]
            if np.any([cat in str(var) for var in solution.data_vars])
        ]
    ds = xr.Dataset()
    if isinstance(var_names, str):
        var_names = [var_names]
    for category in categories:
        ds_ = select_dataset_variables_from_dims(solution, f"{category}_tech")
        for var_name in var_names:
            ds_ = ds_[[var for var in ds_.data_vars if var_name in var]]
        ds_ = reindex_from_tech_to_asset(ds_, category)
        ds_ = ds_.sortby("asset")

        if len(ds) == 0:
            ds = xr.combine_by_coords([ds, ds_])
        else:
            ds = xr.concat([ds, ds_], dim="asset")

    for variable in ds.data_vars:
        new_name = str(variable)
        for var_name in var_names:
            new_name = new_name.replace(var_name, "", 1)
        new_name = (
            new_name.replace("__", "_").removeprefix("_").removesuffix("_")
        )
        ds = ds.rename({variable: new_name})

    da = ds.to_dataarray(dim=res_dim, name=res_name)
    return da


def get_capacities(
    solution: xr.Dataset, model_parameters: xr.Dataset
) -> xr.DataArray:
    """
    Extract capacities from the solution dataset.

    Args:
        solution (xarray.Dataset): solution dataset.
        model_parameters (xarray.Dataset): model parameters.

    Returns:
        xarray.DataArray: capacities.

    """
    p = model_parameters

    da_combined, da_conversion, da_storage, da_transport = (
        xr.DataArray(),
    ) * 4

    if "combined" in p.keys() and p.combined:
        da = solution["operation_combined_power_capacity"]
        da = da.copy(deep=True)
        da = da.rename(None)
        da = da.expand_dims(
            category=np.array(["combined"], dtype=str),
            capacity_type=np.array(["power"], dtype=str),
        )
        da = da.rename(combined_tech="tech")
        da = da.stack(asset=["category", "capacity_type", "tech"])
        da_combined = da

    if "conversion" in p.keys() and p.conversion:
        da = solution["operation_conversion_power_capacity"]
        da = da.copy(deep=True)
        da = da.rename(None)
        da = da.expand_dims(
            category=np.array(["conversion"], dtype=str),
            capacity_type=np.array(["power"], dtype=str),
        )
        da = da.rename(conversion_tech="tech")
        da = da.stack(asset=["category", "capacity_type", "tech"])
        da_conversion = da

    if "storage" in p.keys() and p.storage:
        ds = solution[
            [
                "operation_storage_power_capacity",
                "operation_storage_energy_capacity",
            ]
        ]
        ds = ds.copy(deep=True)
        ds = ds.expand_dims(category=np.array(["storage"], dtype=str))
        ds = ds.rename(
            storage_tech="tech",
            operation_storage_power_capacity="power",
            operation_storage_energy_capacity="energy",
        )
        da = ds.to_dataarray(dim="capacity_type", name=None)
        da = da.stack(asset=["category", "capacity_type", "tech"])
        da_storage = da

    if "transport" in p.keys() and p.transport:
        da = solution["operation_transport_power_capacity"]
        da = da.copy(deep=True)
        da = da.rename(None)
        da = da.expand_dims(capacity_type=np.array(["power"], dtype=str))
        da = da.assign_coords(
            area_from=(["link", "transport_tech"], p.transport_area_from.data),
            area_to=(["link", "transport_tech"], p.transport_area_to.data),
        )
        da_imports = da.groupby(["area_from", "transport_tech"]).sum()
        da_imports = da_imports.expand_dims(
            category=np.array(["transport_import"], dtype=str)
        )
        da_imports = da_imports.rename(area_from="area")
        da_exports = da.groupby(["area_to", "transport_tech"]).sum()
        da_exports = da_exports.expand_dims(
            category=np.array(["transport_export"], dtype=str)
        )
        da_exports = da_exports.rename(area_to="area")

        da = xr.combine_by_coords([da_imports, da_exports])

        da = da.rename(transport_tech="tech")
        da = da.stack(asset=["category", "capacity_type", "tech"])
        da_transport = da

    da = xr.concat(
        [
            d
            for d in [da_combined, da_conversion, da_storage, da_transport]
            if not d.isnull().all()
        ],
        dim="asset",
    )

    return da


def get_net_generation(
    solution: xr.Dataset, model_parameters: xr.Dataset
) -> xr.DataArray:
    """
    Compute the net generation for different assets based on the solution.

    Args:
        solution (xarray.Dataset): The solution dataset from an optimization
        model.
        model_parameters (xarray.Dataset): The dataset containing model
        parameters.

    Returns:
        xr.DataArray: A concatenated DataArray representing the net generation for
            various categories
            (e.g., demand, load shedding, spillage, conversion, combined).
            Dimensions include:
            - category: Different types of generation or consumption
                (e.g., demand, spillage).
            - other relevant dimensions depending on the data.
    """
    p = model_parameters
    s = solution

    demand = (-1 * p.demand).expand_dims(category=["demand"])

    if "load_shedding" not in s.data_vars:
        load_shedding = xr.DataArray(
            [0], coords=dict(category=["load_shedding"])
        )
    else:
        load_shedding = s.operation_load_shedding.expand_dims(
            category=["load_shedding"]
        )

    if "spillage" not in s.data_vars:
        spillage = xr.DataArray([0], coords=dict(category=["spillage"]))
    else:
        spillage = (-1 * s.operation_spillage).expand_dims(
            category=["spillage"]
        )

    conversion = s.operation_conversion_net_generation.rename(
        dict(conversion_tech="category")
    )
    combined = xr.DataArray([], coords=dict(category=[]))
    storage = xr.DataArray([], coords=dict(category=[]))
    net_import = xr.DataArray([], coords=dict(category=[]))
    transport = xr.DataArray([], coords=dict(category=[]))

    if "combined" in p.keys() and p.combined.any():
        combined = s.operation_combined_net_generation.rename(
            dict(combined_tech="category")
        )
    if "storage" in p.keys() and p.storage.any():
        storage = s.operation_storage_net_generation.rename(
            dict(storage_tech="category")
        )
    if "net_import" in p.keys() and p.net_import.any():
        net_import = s.operation_net_import_net_generation.expand_dims(
            category=["net_import"]
        )
    if "transport" in p.keys() and p.transport.any():
        transport = s.operation_transport_net_generation.rename(
            dict(transport_tech="category")
        )

    da = xr.concat(
        [
            demand,
            load_shedding,
            spillage,
            combined,
            conversion,
            storage,
            net_import,
            transport,
        ],
        dim="category",
        coords="all",
        join="outer",
        compat="broadcast_equals",
    )
    return da


def get_costs(
    solution: xr.Dataset, model_parameters: xr.Dataset
) -> xr.DataArray:
    """
    Calculate and return the costs (operation and planning).

    Args:
        solution (xarray.Dataset): The solution dataset from an optimization
        model.
        model_parameters (xarray.Dataset): The dataset containing model
        parameters.

    Returns:
        xr.DataArray: A concatenated DataArray representing the costs of various
            assets (combined, conversion,
            storage, transport, net import).
            Dimensions include:
            - asset: Stack of category, cost type, and technology (tech) for each
                asset type.
            - area
            - year_op
    """
    p = model_parameters

    da_combined, da_conversion, da_net_import, da_storage, da_transport = (
        xr.DataArray(),
    ) * 5

    da_carbon, da_adequacy, da_turpe = (xr.DataArray(),) * 3

    if "combined" in p.keys() and p.combined:
        ds = solution[["operation_combined_costs", "planning_combined_costs"]]
        ds = ds.copy()
        ds = ds.expand_dims(category=np.array(["combined"], dtype=str))
        ds = ds.rename(
            combined_tech="tech",
            operation_combined_costs="operation",
            planning_combined_costs="planning",
        )
        da = ds.to_dataarray(dim="cost_type", name=None)
        da = da.stack(asset=["category", "cost_type", "tech"])
        da_combined = da

    if "conversion" in p.keys() and p.conversion:
        ds = solution[
            ["operation_conversion_costs", "planning_conversion_costs"]
        ]
        ds = ds.copy()
        ds = ds.expand_dims(category=np.array(["conversion"], dtype=str))
        ds = ds.rename(
            conversion_tech="tech",
            operation_conversion_costs="operation",
            planning_conversion_costs="planning",
        )
        da = ds.to_dataarray(dim="cost_type", name=None)
        da = da.stack(asset=["category", "cost_type", "tech"])
        da_conversion = da

    if "net_import" in p.keys() and p.net_import:
        da = solution["operation_net_import_costs"]
        da = da.copy()
        da = da.expand_dims(
            category=np.array(["net_import"], dtype=str),
            cost_type=np.array(["operation"], dtype=str),
        )
        da = da.rename(resource="tech")
        da = da.rename(None)
        da = da.stack(asset=["category", "cost_type", "tech"])
        da_net_import = da

    if "storage" in p.keys() and p.storage:
        ds = solution[["operation_storage_costs", "planning_storage_costs"]]
        ds = ds.copy()
        ds = ds.expand_dims(category=np.array(["storage"], dtype=str))
        ds = ds.rename(
            storage_tech="tech",
            operation_storage_costs="operation",
            planning_storage_costs="planning",
        )
        da = ds.to_dataarray(dim="cost_type", name=None)
        da = da.stack(asset=["category", "cost_type", "tech"])
        da_storage = da

    if "transport" in p.keys() and p.transport:
        ds = solution[
            ["operation_transport_costs", "planning_transport_costs"]
        ]
        ds = ds.copy()
        ds = ds.expand_dims(category=np.array(["transport"], dtype=str))
        ds = ds.rename(
            transport_tech="tech",
            operation_transport_costs="operation",
            planning_transport_costs="planning",
        )
        da = ds.to_dataarray(dim="cost_type", name=None)
        da = da.stack(asset=["category", "cost_type", "tech"])
        da_transport = da

    if "carbon" in p.keys() and p.carbon:
        ds = solution[["operation_carbon_costs"]]
        ds = ds.copy()
        ds = ds.expand_dims(
            category=np.array(["carbon"], dtype=str),
            tech=np.array(["conversion"], dtype=str),
        )
        ds = ds.rename(
            operation_carbon_costs="operation",
        )
        da = ds.to_dataarray(dim="cost_type", name=None)
        da = da.stack(asset=["category", "cost_type", "tech"])
        da_carbon = da

    if "turpe" in p.keys() and p.turpe:
        ds = solution[
            ["operation_turpe_fixed_costs", "operation_turpe_variable_costs"]
        ]
        ds = ds.copy()
        ds = ds.expand_dims(
            category=np.array(["turpe"], dtype=str),
            tech=np.array(["electricity"], dtype=str),
        )
        ds = ds.rename(
            operation_turpe_fixed_costs="planning",
            operation_turpe_variable_costs="operation",
        )
        da = ds.to_dataarray(dim="cost_type", name=None)
        da = da.stack(asset=["category", "cost_type", "tech"])
        da_turpe = da

    ds = solution[
        ["operation_load_shedding_costs", "operation_spillage_costs"]
    ]
    ds = ds.copy()
    ds = ds.expand_dims(
        category=np.array(["adequacy"], dtype=str),
        cost_type=np.array(["operation"], dtype=str),
    )
    ds = ds.rename(
        operation_load_shedding_costs="load_shedding",
        operation_spillage_costs="spillage",
    )
    da = ds.to_dataarray(dim="tech", name=None)
    da = da.stack(asset=["category", "cost_type", "tech"])
    da_adequacy = da

    da = xr.concat(
        [
            d
            for d in [
                da_combined,
                da_conversion,
                da_net_import,
                da_storage,
                da_transport,
                da_carbon,
                da_adequacy,
                da_turpe,
            ]
            if not d.isnull().all()
        ],
        dim="asset",
    )

    return da


def get_storage_duration(s: xr.Dataset) -> xr.DataArray:
    """Compute the storage duration for each storage technology.

    Args:
        s (xr.Dataset): Solution dataset.

    Returns:
        A DataArray representing the storage duration for each storage
        technology.
    """
    duration = (
        s.operation_storage_energy_capacity
        / s.operation_storage_power_capacity
    )
    return duration


def get_conversion_load_factor(s: xr.Dataset, p: xr.Dataset) -> xr.DataArray:
    """Compute the conversion load factor for each conversion technology.

    Args:
        s (xr.Dataset): Solution dataset.
        p (xr.Dataset): Model parameters.

    Returns:
        A DataArray representing the conversion load factor for each conversion
        technology.
    """
    clf = (
        s.operation_conversion_power.sum(["hour"])
        / p.time_step_duration.sum("hour")
        / s.operation_conversion_power_capacity
    )
    return clf
