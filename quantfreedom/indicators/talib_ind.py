# https://ta-lib.github.io/ta-lib-python/index.html
import pandas as pd
import numpy as np
from talib.abstract import Function
from talib import get_functions
from itertools import product
from quantfreedom._typing import pdFrame, Optional, pdSeries, Array1d


def from_talib(
    func_name: str,
    cart_product: bool,
    combos: bool,
    df_prices: Optional[pdFrame] = None,
    user_ind_df: Optional[pdFrame] = None,
    **kwargs,
) -> pdFrame:

    if all(x is None for x in (df_prices, user_ind_df)):
        raise ValueError(
            f"You need to send either a dataframe of prices 'df_prices' or a dataframe with multindexed values 'user_ind_df'"
        )
    elif all(x is not None for x in (df_prices, user_ind_df)):
        raise ValueError(
            f"You can't send both prices and values ... please pick one or the other"
        )
    elif (
        not isinstance(user_ind_df, pdFrame)
        and user_ind_df is not None
        or not isinstance(df_prices, pdFrame)
        and df_prices is not None
    ):
        raise ValueError(f"You must send this as a pandas dataframe")
    elif isinstance(user_ind_df, pdFrame):
        pd_index = user_ind_df.index
    elif isinstance(df_prices, pdFrame):
        pd_index = df_prices.index

    users_args_list = []
    biggest = 1
    indicator_info = Function(func_name).info
    input_names_dict = {}
    in_names_key = ""
    output_names = indicator_info["output_names"]
    ind_params = list(indicator_info["parameters"].keys())
    ind_name = indicator_info["name"]

    if cart_product and combos:
        raise ValueError(
            f"you can't have cart product and combos both be true")
    if len(ind_params) == 1 and (cart_product or combos):
        raise ValueError(
            f"This indicator only has one paramater which is {ind_params[0]} therefore can't do combos or cart product."
        )

    for in_names_key, in_names_values in indicator_info["input_names"].items():
        filled = False
        if isinstance(in_names_values, list):
            for kwarg_keys, kwarg_values in kwargs.items():
                if in_names_key == kwarg_keys:
                    if not isinstance(kwarg_values, list):
                        raise ValueError(
                            f"{in_names_key} must be a list of strings")

                    if isinstance(kwarg_values, list):
                        if not all(isinstance(x, str) for x in kwarg_values):
                            raise ValueError(
                                f"{in_names_key} your list has to be made up of strings"
                            )

                        if len(kwarg_values) == 1:
                            raise ValueError(
                                f"{in_names_key} your list length must be greater than 1"
                            )

                        if len(kwarg_values) != len(in_names_values):
                            raise ValueError(
                                f"your list of {in_names_key} must be exactly {len(in_names_values)}"
                            )

                    input_names_dict[in_names_key] = kwarg_values
                    filled = True
                    break
                elif in_names_key == "price" and kwarg_keys == "prices":
                    raise ValueError(
                        f"you need to provide price instead of prices")
                elif in_names_key == "prices" and kwarg_keys == "price":
                    raise ValueError(
                        f"you need to provide prices instead of price")

            if not filled:
                input_names_dict[in_names_key] = in_names_values

        elif isinstance(in_names_values, str):
            for kwarg_keys, kwarg_values in kwargs.items():
                if in_names_key == kwarg_keys:
                    if not isinstance(kwarg_values, str):
                        raise ValueError(
                            f"{in_names_key} must be a string and not a list of strings"
                        )

                    input_names_dict[in_names_key] = kwarg_values
                    filled = True
                    break
                elif in_names_key == "price" and kwarg_keys == "prices":
                    raise ValueError(
                        f"you need to provide price instead of prices")
                elif in_names_key == "prices" and kwarg_keys == "price":
                    raise ValueError(
                        f"you need to provide prices instead of price")

            if not filled:
                input_names_dict[in_names_key] = in_names_values

    if bool(indicator_info["parameters"]):
        param_dict = {}
        for param_names_key, param_names_values in indicator_info["parameters"].items():
            filled = False
            for kwarg_keys, kwarg_values in kwargs.items():
                if param_names_key == kwarg_keys:
                    if not isinstance(kwarg_values, (int, float, list, Array1d)):
                        raise ValueError(
                            f"{param_names_key} must be a int float or a list or np.array of ints or floats"
                        )

                    if isinstance(kwarg_values, (int, float)):
                        users_args_list.append(np.asarray([kwarg_values]))

                    elif isinstance(kwarg_values, (list, Array1d)):
                        if (
                            cart_product == False
                            and combos == False
                            and len(indicator_info["parameters"]) > 1
                        ):
                            raise ValueError(
                                f"you can't have list(s) as args when the {func_name} has mutiple params without doing a combo or cart product"
                            )
                        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in kwarg_values):
                            raise ValueError(
                                f"{param_names_key} your list has to be filled with ints or floats"
                            )
                        if len(kwarg_values) == 1:
                            raise ValueError(
                                f"{param_names_key} your list or array length must be greater than 1"
                            )
                        if combos or cart_product:
                            if biggest == 1 and len(kwarg_values) > 1:
                                biggest = len(kwarg_values)
                            if biggest != len(kwarg_values) and combos:
                                raise ValueError(
                                    f"{param_names_key} when using combos, all listed items must be same length"
                                )

                        users_args_list.append(np.asarray(kwarg_values))
                    param_dict[param_names_key] = kwarg_values
                    filled = True
                    break

            if not filled:
                param_dict[param_names_key] = param_names_values
                users_args_list.append(np.asarray([param_names_values]))
    else:
        param_dict = ()

    if biggest == 1 and (combos or cart_product):
        raise ValueError(
            f"You have to have a list for paramaters for {ind_params} to use cart product or combos"
        )

    elif combos:
        final_user_args = []
        for x in users_args_list:
            if x.size == 1:
                final_user_args.append(np.broadcast_to(x, biggest))
            else:
                final_user_args.append(x)
        final_user_args = tuple(final_user_args)

    elif cart_product:
        final_user_args = np.array(list(product(*users_args_list))).T

    else:
        final_user_args = tuple(users_args_list)

    ind_settings_tup = ()
    pd_multind_tuples = ()
    ind_setings_len = final_user_args[0].size
    output_names_len = len(output_names)
    symbols = list(df_prices.columns.levels[0])
    num_of_symbols = len(symbols)

    # sending indicator data as the data you want to work with
    if user_ind_df is not None:
        counter = 0
        user_ind_settings = tuple(user_ind_df.columns)
        user_ind_values = user_ind_df.values
        user_ind_names = list(user_ind_df.columns.names)
        user_ind_name = user_ind_names[0].split("_")[0]
        param_keys = [user_ind_name + "_" +
                      ind_name + "_" + x for x in ind_params]
        # param_keys = param_keys + user_ind_names
        param_keys = user_ind_names + param_keys
        final_array = np.empty(
            (
                user_ind_df.shape[0],
                ind_setings_len * output_names_len * user_ind_df.shape[1],
            )
        )
        if len(output_names) > 1:
            param_keys = [ind_name + "_output_names"] + param_keys

            # these are the names called by the fun like talib('rsi').real - real is the output name
            for out_count, out_name in enumerate(output_names):
                for col in range(user_ind_values.shape[1]):
                    # c is the indicator result of the array within the tuple (array[x], array[x])
                    for c in range(ind_setings_len):
                        # x is the array object in the tuple (x,x)
                        for x in final_user_args:
                            if type(x[c]) == np.int_:
                                ind_settings_tup = ind_settings_tup + \
                                    (int(x[c]),)
                            if type(x[c]) == np.float_:
                                ind_settings_tup = ind_settings_tup + \
                                    (float(x[c]),)
                        final_array[:, counter] = Function(func_name)(
                            user_ind_values[:, col],
                            *ind_settings_tup,
                        )[out_count]
                        pd_multind_tuples = pd_multind_tuples + (
                            (out_name,) +
                            user_ind_settings[col] + ind_settings_tup,
                        )
                        counter += 1
                        ind_settings_tup = ()
        elif len(output_names) == 1:
            for col in range(user_ind_values.shape[1]):
                # c is the indicator result of the array within the tuple (array[x], array[x])
                for c in range(ind_setings_len):
                    # x is the array object in the tuple (x,x)
                    for x in final_user_args:
                        if type(x[c]) == np.int_:
                            ind_settings_tup = ind_settings_tup + (int(x[c]),)
                        if type(x[c]) == np.float_:
                            ind_settings_tup = ind_settings_tup + \
                                (float(x[c]),)
                    final_array[:, counter] = Function(func_name)(
                        user_ind_values[:, col],
                        *ind_settings_tup,
                    )
                    pd_multind_tuples = pd_multind_tuples + (
                        user_ind_settings[col] + ind_settings_tup,
                    )
                    counter += 1
                    ind_settings_tup = ()

        else:
            raise ValueError(
                "Something is wrong with the output name length for user ind data"
            )

    # sending price data as your data to work with
    else:
        final_array = np.empty(
            (df_prices.shape[0], ind_setings_len * output_names_len * num_of_symbols))
        counter = 0
        if output_names_len > 1:
            param_keys = [list(df_prices.columns.names)[
                0]] + [ind_name + "_output_names"] + [ind_name + "_" + x for x in ind_params]
            for symbol in symbols:
                temp_df_prices = df_prices[symbol]
                current_symbol_tuple = (symbol,)
                # these are the names called by the fun like talib('rsi').real - real is the output name
                for out_name in output_names:
                    # c is the indicator result of the array within the tuple (array[x], array[x])
                    for c in range(ind_setings_len):
                        # x is the array object in the tuple (x,x)
                        for x in final_user_args:
                            if type(x[c]) == np.int_:
                                ind_settings_tup = ind_settings_tup + \
                                    (int(x[c]),)
                            if type(x[c]) == np.float_:
                                ind_settings_tup = ind_settings_tup + \
                                    (float(x[c]),)
                        if in_names_key == "price":
                            final_array[:, counter] = Function(func_name)(
                                temp_df_prices,
                                *ind_settings_tup,
                                price=input_names_dict[in_names_key],
                            )[out_name]

                            pd_multind_tuples = pd_multind_tuples + (
                                current_symbol_tuple +
                                (out_name,) + ind_settings_tup,
                            )
                        elif in_names_key == "prices":
                            final_array[:, counter] = Function(func_name)(
                                temp_df_prices,
                                *ind_settings_tup,
                                prices=input_names_dict[in_names_key],
                            )[out_name]

                            pd_multind_tuples = pd_multind_tuples + (
                                current_symbol_tuple +
                                (out_name,) + ind_settings_tup,
                            )

                        ind_settings_tup = ()
                        counter += 1

        elif output_names_len == 1:
            param_keys = [list(df_prices.columns.names)[0]] + \
                [ind_name + "_" + x for x in ind_params]
            for symbol in symbols:
                temp_df_prices = df_prices[symbol]
                current_symbol_tuple = (symbol,)
                for c in range(ind_setings_len):
                    # x is the array object in the tuple (x,x)
                    for x in final_user_args:
                        if type(x[c]) == np.int_:
                            ind_settings_tup = ind_settings_tup + (int(x[c]),)
                        if type(x[c]) == np.float_:
                            ind_settings_tup = ind_settings_tup + \
                                (float(x[c]),)

                    if in_names_key == "price":
                        final_array[:, counter] = Function(func_name)(
                            temp_df_prices,
                            *ind_settings_tup,
                            price=input_names_dict[in_names_key],
                        ).values

                        pd_multind_tuples = pd_multind_tuples + \
                            (current_symbol_tuple + ind_settings_tup,)
                    elif in_names_key == "prices":
                        final_array[:, counter] = Function(func_name)(
                            temp_df_prices,
                            *ind_settings_tup,
                            prices=input_names_dict[in_names_key],
                        ).values

                        pd_multind_tuples = pd_multind_tuples + \
                            (current_symbol_tuple + ind_settings_tup,)

                    ind_settings_tup = ()
                    counter += 1

        else:
            raise ValueError("Something is wrong with the output name length")

    return pd.DataFrame(
        final_array,
        index=pd_index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=param_keys,
        ),
    )


def talib_ind_info(func_name: str):
    return Function(func_name).info


def talib_func_list_website_link():
    print("https://ta-lib.github.io/ta-lib-python/funcs.html")


def talib_list_of_indicators():
    return get_functions()
