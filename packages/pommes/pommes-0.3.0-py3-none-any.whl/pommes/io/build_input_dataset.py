"""Module for the building of the xarray input Dataset."""

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
import yaml

from pommes.utils import crf, discount_factor

# Set up a logger for this module
logger = logging.getLogger(__name__)


def read_config_file(
    file_path: str | None = None,
) -> dict[str, Any]:
    """
    Reads the configuration file.

    Args:
        file_path (str | None): Path to the configuration file. If None, a
            default path based on `root/data` is used.

    Returns:
        dict[str, Any]: Dictionary containing the description of the inputs.
    """
    with open(file_path) as file:
        data = yaml.safe_load(file)

    if data.get("input") is None:
        logger.warning(f"'input' section is missing in file {file_path}.")
    else:
        if data["input"].get("path") is None:
            data["input"]["path"] = Path(file_path).parent / "data"
            logger.info("No data path specified. Using default path:")
            logger.info(data["input"]["path"])
        else:
            logger.info(f"Using relative path:\n {data['input']['path']}")
    return data


def build_coordinates(config_: dict[str, Any]) -> xr.Coordinates:
    """
    Build coordinates based on the configuration.

    Args:
        config_ (dict[str, Any]): Configuration dictionary.

    Returns:
        xarray.Coordinates: Xarray coordinates constructed from the
        configuration.
    """
    return xr.Coordinates(
        {
            coord_label: np.array(x["values"], dtype=x["type"])
            for coord_label, x in config_["coords"].items()
        }
    )


def load_inputs_as_dict_of_df(
    config_: dict[str, Any],
) -> dict[str, pd.DataFrame]:
    """
    Loads input data from all CSV files given in data variable descriptions.

    Args:
        config_ (dict[str, Any]): Configuration dictionary.

    Returns:
        dict[str, pandas.DataFrame]: Dictionary of DataFrames containing the
            loaded data.
    """
    parameters = config_["input"]["parameters"]
    path = config_["input"]["path"]

    file_index = {}

    for variable in parameters.keys():
        file = parameters[variable]["file"]
        index_input = parameters[variable]["index_input"]
        if file in file_index.keys():
            if file_index[file] != tuple(sorted(index_input)):
                raise ValueError(
                    f"Same file has not identical index in data variable "
                    f"descriptions!\n"
                    f'Check index of variable "{variable}".'
                )
        else:
            file_index[file] = tuple(sorted(index_input))

    dict_df = {}

    for file, index_input in file_index.items():
        logger.info("Start reading csv file: " + file + " ...")
        dict_df[file] = pd.read_csv(
            f"{path}/{file}",
            index_col=index_input,
            dtype={
                coord: np.dtype(config_["coords"][coord]["type"])
                for coord in index_input
            },
            sep=";",
        )
        logger.info("Completed reading csv file: " + file)

    return dict_df


def compute_end_of_life(ds: xr.Dataset) -> xr.Dataset:
    """
    Add annuity costs to all corresponding investment costs in input dataset.

    Args:
        ds (xarray.Dataset): Dataset built from the input parameters before
        pre-processing.

    Returns:
        xarray.Dataset: Updated dataset with new data variables
        'x_end_of_life' for all 'x_life_span'.
    """
    for data_var in ds.data_vars:
        if "life_span" in data_var:
            ds[str(data_var).replace("life_span", "end_of_life")] = (
                ds.year_dec.broadcast_like(ds.year_inv + ds[data_var])
                .where(ds.year_dec <= (ds.year_inv + ds[data_var]))
                .max("year_dec")
                .astype("int64")
            )
    return ds


def build_annuity_rate(
    years_dec_: xr.DataArray,
    years_inv_: xr.DataArray,
    max_finance_rate: float = 0.1,
    finance_rate_step: float = 0.005,
) -> xr.DataArray:
    """
    Build a DataArray containing capital recovery factor for financial data.

    Args:
        years_dec_ (xarray.DataArray): Decommissioning year coordinates.
        years_inv_ (xarray.DataArray): Investment year coordinates.
        max_finance_rate (float): Maximum financing rate. Default is 0.1.
        finance_rate_step (float): Step size for financing rate.
            Default is 0.005.

    Returns:
        xarray.DataArray: DataArray containing repayment rates indexed with
            financing rates, decommissioning year, and investment year.
    """
    temp = np.arange(0, max_finance_rate, finance_rate_step, dtype="float64")
    finance_rate = xr.DataArray(temp, coords=dict(finance_rate=temp))

    df = (
        xr.DataArray(np.nan, coords=[years_dec_, years_inv_, finance_rate])
        .to_dataframe(name="crf")
        .reset_index()
    )

    df["crf"] = df.apply(
        lambda row: crf(row.finance_rate, row.year_dec - row.year_inv), axis=1
    )
    return (
        df.set_index(["year_dec", "year_inv", "finance_rate"]).to_xarray().crf
    )


def compute_annuity_cost(
    ds: xr.Dataset, config_: dict[str, Any]
) -> xr.Dataset:
    """
    Add annuity costs to all corresponding investment costs in input dataset.

    Args:
        ds (xarray.Dataset): Dataset built from the input parameters before
            pre-processing.
        config_ (dict[str, Any]): Configuration dictionary.

    Returns:
        xarray.Dataset: Updated dataset with new data variables
            'x_annuity_cost' for all 'x_invest_cost'.
    """
    annuity_rate = build_annuity_rate(ds.year_inv, ds.year_dec)
    annuity_to_compute = config_.get("pre_process", {}).get(
        "annuity_computation"
    )

    if annuity_to_compute is None:
        return ds

    for category, dict_annuity in annuity_to_compute.items():
        if ds[category].any():
            for name, param in dict_annuity.items():
                ds = ds.assign(
                    {
                        name: ds[param["invest_cost"]]
                        * xr.where(
                            cond=(
                                (ds.year_inv < ds.year_dec)
                                * (
                                    ds.year_dec
                                    <= (ds.year_inv + ds[param["life_span"]])
                                )
                                * np.isfinite(ds[param["finance_rate"]])
                            ),
                            x=annuity_rate.sel(
                                finance_rate=ds[param["finance_rate"]].where(
                                    ds[param["finance_rate"]].isin(
                                        annuity_rate.finance_rate
                                    ),
                                    0,
                                )
                            ).drop_vars("finance_rate"),
                            y=np.nan,
                        )
                    }
                )
    return ds


def compute_discount(ds: xr.Dataset, config_: dict[str, Any]) -> xr.Dataset:
    """
    Build a DataArray containing the discount factor and add it to the input.

    Args:
        ds (xarray.Dataset): Dataset built from the input parameters before
            pre-processing.
        config_ (dict[str, Any]): Configuration dictionary.

    Returns:
        xarray.Dataset: Updated dataset with a new data variable 'discount
            factor'.
    """
    if config_.get("pre_process", {}).get("discount_factor") is None:
        return ds

    discount_rate = ds[
        config_["pre_process"]["discount_factor"]["discount_rate"]
    ]
    year_ref = ds[config_["pre_process"]["discount_factor"]["year_ref"]]

    discount_rate = xr.broadcast(xr.DataArray(discount_rate), ds.year_op)[0]

    ds = ds.assign(
        discount_factor=xr.DataArray(
            np.array(
                np.vectorize(discount_factor, excluded=["year_ref"])(
                    r=discount_rate,
                    year=ds.year_op.astype(np.float64),
                    year_ref=year_ref,
                ),
                dtype=np.float64,
            ),
            coords=[ds.year_op],
        )
    )

    return ds


def build_input_parameters(
    config_: dict[str, Any], dict_df: dict[str, pd.DataFrame] | None = None
) -> xr.Dataset:
    """
    Constructs and validates the input parameters based on the configuration.

    Args:
        config_ (dict[str, Any]): Configuration dictionary containing
            information about input parameters, modules, and coordinate types.
        dict_df (dict[str, pandas.DataFrame] | None): Dictionary of DataFrames

    Raises:
        ValueError: If there is an inconsistency between the index input and
            index set for any parameter.

    Returns:
        xarray.Dataset: Dataset built from the input parameters, with modules,
            coordinates, and parameters set according to the configuration.
            Missing data is filled with default values where necessary,
            and annuity cost and discount values are computed.

    Notes:
        - This function first builds the dataset coordinates and assigns
            modules based on the `config_` dictionary.
        - Parameters are validated against their expected index sets. If there
            is any inconsistency, a `ValueError` is raised.
        - The parameter data is loaded from the source files and columns, cast
            to the required data type, and broadcast to match the dataset's
            coordinates.
        - Any missing data in the parameter arrays is filled with the specified
            fill values.
        - After assigning all parameters, additional computations for annuity
            costs and discounting are performed using `compute_annuity_cost`
            and `compute_discount`.
    """
    parameters = config_["input"]["parameters"]

    if dict_df is None:
        dict_df = load_inputs_as_dict_of_df(config_)

    ds = xr.Dataset(coords=build_coordinates(config_))

    for module, boolean in config_["add_modules"].items():
        ds = ds.assign({module: boolean})

    for key, param in parameters.items():
        logger.debug(f"Start building parameter: {key} ...")
        series = dict_df[param["file"]][param["column"]].astype(param["type"])
        logger.info(f"Converting {key} to xarray.DataArray")
        if series.index.names[0] is None:
            da = xr.DataArray(np.array(series[0]))
        else:
            da = series.to_xarray().astype(param["type"])

            da = da.broadcast_like(ds[list(da.dims)])

            da = da.assign_coords(
                {
                    coord: da[coord].astype(config_["coords"][coord]["type"])
                    for coord in da.dims
                }
            )

        if np.any(da.isnull()):
            da = da.fillna(np.array(param["fill"], dtype=param["type"]))
        ds = ds.assign({key: da})
        logger.debug(f"Parameter: {key} built.")

    ds = compute_end_of_life(ds)
    ds = compute_annuity_cost(ds, config_)
    ds = compute_discount(ds, config_)

    return ds
