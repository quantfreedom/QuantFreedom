# https://ta-lib.github.io/ta-lib-python/index.html
import json
from itertools import product

import numpy as np
import pandas as pd
import talib
from talib import get_functions
from talib.abstract import Function

from quantfreedom.indicators.indicators_cls import Indicator


def validate(value, ref_name, ref_value):
    if not isinstance(value, list):
        raise ValueError(f"{ref_name} must be a list")

    if not all(isinstance(x, str) for x in value):
        raise ValueError(f"{ref_name} your list has to be made up of strings")

    if len(value) != len(ref_value):
        raise ValueError(f"{ref_name} your list length must be {len(ref_value)}")


def column_wise_combos(parameters: dict) -> list:
    """Create the column wise combos for the parameters"""
    params_len = [len(p) for p in parameters if isinstance(p, list)]
    lenghts = list(set(params_len))
    if len(lenghts) > 1:
        raise ValueError("The length of the parameters needs to be the same.")
    base_lenght = lenghts[0]
    final_user_args = []
    for v in parameters.values():
        if not isinstance(v, list):
            final_user_args.append([v] * base_lenght)
        else:
            final_user_args.append(v)
    return [list(x) for x in zip(*final_user_args)]


def catesian_product_combos(parameters: dict) -> list:
    """Create the cartesian product for the parameters"""
    list_params = []
    for v in parameters:
        if not isinstance(v, list):
            list_params.append([v])
        else:
            list_params.append(v)
    return list(product(*list_params))


def from_talib(
    func_name: str,
    price_data: pd.DataFrame = None,
    indicator_data: pd.DataFrame = None,
    column_wise_combos: bool = False,
    input_names: list = None,
    parameters: dict = {},
) -> pd.DataFrame:

    indicator_info = Function(func_name).info
    output_names = indicator_info["output_names"]
    talib_func = getattr(talib, func_name.upper())

    # Update the parameters with the user input
    if indicator_info.get("parameters"):
        indicator_info["parameters"].update(parameters)

    # Defaults to all possible combos, catesian product.
    param_values = indicator_info["parameters"].values()
    if column_wise_combos:
        final_user_args = column_wise_combos(param_values)
    else:
        final_user_args = catesian_product_combos(param_values)

    user_kwargs = []
    args_keys = indicator_info["parameters"].keys()
    for args in final_user_args:
        user_kwargs.append({k: v for k, v in zip(args_keys, args)})

    # Prepare the input names
    input_names_kwargs = []
    input_name_key = list(indicator_info["input_names"].keys())[0]
    if input_names is None:
        input_names_kwargs.append(indicator_info["input_names"])
        input_names = list(indicator_info["input_names"].values())
    else:
        indicator_base_input_name = list(indicator_info["input_names"].values())[0]
        if isinstance(indicator_base_input_name, list):
            input_name_len = len(indicator_base_input_name)
        else:
            input_name_len = 1
        for input_name in input_names:
            if input_name_len > 1 and len(input_name) != input_name_len:
                raise ValueError(
                    "The length of the input names must be the same as the indicator input names"
                )
            elif input_name_len == 1:
                input_name = [input_name]
            input_names_kwargs.append({input_name_key: input_name})

    # Apply indicator to price data
    if price_data is not None:
        symbols = list(price_data.columns.levels[0])
        parameters_values = [tuple(d.values()) for d in user_kwargs]
        if isinstance(input_names[0], list):
            input_names_json = [json.dumps(a) for a in input_names]
        else:
            input_names_json = [json.dumps(input_names)]
        input_combinations = list(product(symbols, output_names, input_names_json))
        indexes = []
        for parameter in parameters_values:
            for combination in input_combinations:
                indexes.append(combination + parameter)

        param_names = [f"{func_name}_{a}" for a in args_keys]
        columns_index = pd.MultiIndex.from_tuples(
            indexes, names=("symbol", "output", "candle_body") + tuple(param_names)
        )
        ta_lib_data = pd.DataFrame(columns=columns_index)

        for symbol in symbols:
            for input_names in input_names_kwargs:
                for input_name in input_names.values():
                    temp_price_data_tuple = price_data[symbol][input_name].values.T
                for kwargs in user_kwargs:
                    talib_output = talib_func(
                        *temp_price_data_tuple,
                        **kwargs,
                    )

                    if len(output_names) == 1:
                        talib_output = (talib_output,)

                    for i, output_name in enumerate(output_names):
                        ta_lib_data.loc[
                            :,
                            (symbol, output_name, json.dumps(input_name))
                            + tuple(kwargs.values()),
                        ] = talib_output[i]
        ta_lib_data.index = price_data.index

    # Apply indicator to indicator data
    elif indicator_data is not None:
        symbols = list(indicator_data.columns.levels[0])
        parameters_values = [tuple(d.values()) for d in user_kwargs]
        if isinstance(input_names[0], list):
            raise ("Indicator data does not support multiple inputs yet")
        else:
            input_names_json = [json.dumps(input_names)]

        talib_out = []
        for kwarg in user_kwargs:
            ind_output = indicator_data.apply(
                axis=0,
                raw=True,
                func=lambda x: talib_func(x.astype(np.float_), **kwarg),
            )
            index_values = [
                v + tuple(kwarg.values()) for v in ind_output.columns.values
            ]
            param_names = [f"{func_name}_{a}" for a in kwarg.keys()]
            index_names = ind_output.columns.names + param_names
            ind_output.columns = pd.MultiIndex.from_tuples(
                index_values, names=index_names
            )
            talib_out.append(ind_output)
        ta_lib_data = pd.concat(talib_out, axis=1)

    # Clean and sort the output data
    ta_lib_data.sort_index(axis=1, inplace=True)
    ta_lib_data.dropna(how="all", axis=0, inplace=True)

    ind = Indicator(data=ta_lib_data, name=func_name)
    return ind


def talib_ind_info(func_name: str):
    return Function(func_name).info


def talib_func_list_website_link():
    print("https://ta-lib.github.io/ta-lib-python/funcs.html")


def talib_list_of_indicators():
    return get_functions()
