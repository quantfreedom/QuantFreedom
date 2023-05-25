# https://ta-lib.github.io/ta-lib-python/index.html
from itertools import product

import numpy as np
import pandas as pd
import talib
import json
from talib import get_functions
from talib.abstract import Function
from collections.abc import Iterable

from quantfreedom._typing import Array1d
from quantfreedom.indicators.indicators_cls import Indicator
from quantfreedom.plotting.simple_plots import (plot_on_candles_1_chart,
                                                plot_results_candles_and_chart)

# this is an update

def validate(value, ref_name, ref_value):
    if not isinstance(value, list):
        raise ValueError(f"{ref_name} must be a list")

    if not all(isinstance(x, str) for x in value):
        raise ValueError(
            f"{ref_name} your list has to be made up of strings"
        )

    if len(value) != len(ref_value):
        raise ValueError(
            f"{ref_name} your list length must be {len(ref_value)}"
        )
    

def from_talib(
    func_name: str,
    price_data: pd.DataFrame = None,
    indicator_data: pd.DataFrame = None,
    column_wise_combos: bool = False,
    plot_results: bool = False,
    plot_on_data: bool = False,
    input_names: list = None,
    parameters: dict = {},
) -> pd.DataFrame:
    """
    Function Name
    -------------
    from_talib

    Summary
    -------
    Using talib to create indicator data. If you need a list of the indicators visit the talib website https://ta-lib.github.io/ta-lib-python/funcs.html

    Explainer Video
    ---------------
    Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

    ## Variables needed
    Parameters
    ----------
    func_name : str
        the short form name of the function like dema for Double Exponential Moving Average. Please look at https://ta-lib.github.io/ta-lib-python/funcs.html for a list of all the short form function names
    price_data : pd.DataFrame, None
        price data
    indicator_data : pd.DataFrame, None
        indicator data like if you want to put an ema on the rsi you send the rsi indicator data here and ema the for func name
    all_possible_combos : bool, False
        If you want all possible combinations, aka the cartesian product, or not. Example of what the cart product does
        ```
        [1,2]
        [a,b]
        answer: [(1,a), (1,b), (2,a), (2,b)]
        ```
    column_wise_combos : bool, False
        Standard column wise combos. An example is
        ```
        [1,2,3]
        [a,b,c]
        answer: [(1,a), (2,b), (3,c)]
        ```

    ## Function returns
    Returns
    -------
    pd.DataFrame
        Pandas Dataframe of indicator values
    """
    pd_index = indicator_data.index if indicator_data is not None and not indicator_data.empty else price_data.index
    indicator_info = Function(func_name).info
    output_names = indicator_info["output_names"]
    talib_func = getattr(talib, func_name.upper())

    if indicator_info.get("parameters"):
        indicator_info["parameters"].update(parameters)

    # Defaults to all possible combos, catesian product.
    if column_wise_combos:
        params_len = [len(p) for p in indicator_info["parameters"].values() if isinstance(p, list)]
        lenghts = list(set(params_len))
        if len(lenghts)>1:
            raise ValueError("The length of the parameters needs to be the same.")
        base_lenght = lenghts[0]
        final_user_args = []
        for v in indicator_info["parameters"].values():
            if not isinstance(v, list):
                final_user_args.append([v] * base_lenght)
            else:
                final_user_args.append(v)
        final_user_args = [list(x) for x in zip(*final_user_args)]
    else:
        list_params = []
        for v in indicator_info["parameters"].values():
            if not isinstance(v, list):
                list_params.append([v])
            else:
                list_params.append(v)
        final_user_args = list(product(*list_params))

    user_kwargs = []
    args_keys = indicator_info["parameters"].keys()
    for args in final_user_args:
        user_kwargs.append({k: v for k, v in zip(args_keys, args)})

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
            if input_name_len>1 and len(input_name) != input_name_len:
                raise ValueError("The length of the input names must be the same as the indicator input names")
            elif input_name_len==1:
                input_name = [input_name]
            input_names_kwargs.append({input_name_key: input_name})

    output_names_len = len(output_names)

    # sending price data as your data to work with
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
                indexes.append(combination+parameter)

        param_names = [f"{func_name}_{a}" for a in args_keys]
        columns_index = pd.MultiIndex.from_tuples(indexes, names=("symbol", "output", "candle_body") + tuple(param_names))
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

                    if output_names_len == 1:
                        talib_output = (talib_output, )

                    for i, output_name in enumerate(output_names):
                        ta_lib_data.loc[:, (symbol, output_name, json.dumps(input_name))+tuple(kwargs.values())] = talib_output[i]
    elif indicator_data is not None:
        symbols = list(indicator_data.columns.levels[0])
        parameters_values = [tuple(d.values()) for d in user_kwargs]
        if isinstance(input_names[0], list):
            raise("Indicator data does not support multiple inputs yet")
        else:
            input_names_json = [json.dumps(input_names)]


        talib_out = []
        for kwarg in user_kwargs:
            indicator_output = indicator_data.apply(axis=0, raw=True, func=lambda x: talib_func(x.astype(np.float_), **kwarg))
            index_values = [v + tuple(kwarg.values()) for v in indicator_output.columns.values]
            param_names = [f"{func_name}_{a}" for a in kwarg.keys()]
            index_names = indicator_output.columns.names + param_names
            indicator_output.columns = pd.MultiIndex.from_tuples(index_values, names=index_names)
            talib_out.append(indicator_output)
        ta_lib_data = pd.concat(talib_out, axis=1)

    ta_lib_data.index = pd_index
    ta_lib_data.sort_index(axis=1, inplace=True)
    ta_lib_data.dropna(how="all", axis=0, inplace=True)


    if plot_on_data:
        if price_data is not None:
            plot_on_candles_1_chart(
                ta_lib_data=ta_lib_data,
                price_data=price_data,
            )
    elif plot_results:
        if price_data is not None:
            plot_results_candles_and_chart(
                ta_lib_data=ta_lib_data,
                price_data=price_data,
            )

    ind = Indicator(data=ta_lib_data, name=func_name)
    return ind


def talib_ind_info(func_name: str):
    return Function(func_name).info


def talib_func_list_website_link():
    print("https://ta-lib.github.io/ta-lib-python/funcs.html")


def talib_list_of_indicators():
    return get_functions()