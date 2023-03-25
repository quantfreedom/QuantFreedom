# https://ta-lib.github.io/ta-lib-python/index.html
import pandas as pd
import numpy as np
from talib.abstract import Function
from talib import get_functions
from itertools import product
from quantfreedom._typing import (
   pdFrame
)

def from_talib(
    func_name: str,
    df_prices: pdFrame,
    cart_product: bool,
    combos: bool,
    **kwargs,
)-> pdFrame:
    users_args_list = []
    biggest = 1
    indicator_info = Function(func_name).info
    input_names_dict = {}
    in_names_key = ''
    output_names = indicator_info['output_names']
    ind_params = list(indicator_info["parameters"].keys())
    ind_name = indicator_info['name']

    if cart_product and combos:
        raise ValueError(
            f"you can't have cart product and combos both be true")
    if len(ind_params) == 1 and (cart_product or combos):
        raise ValueError(
            f"This indicator only has one paramater which is {ind_params[0]} therefore can't do combos or cart product.")

    for in_names_key, in_names_values in indicator_info['input_names'].items():
        filled = False
        if isinstance(in_names_values, list):
            for kwarg_keys, kwarg_values in kwargs.items():
                if in_names_key == kwarg_keys:
                    if not isinstance(kwarg_values, list):
                        raise ValueError(
                            f'{in_names_key} must be a list of strings')

                    if isinstance(kwarg_values, list):
                        if not all(isinstance(x, str) for x in kwarg_values):
                            raise ValueError(
                                f'{in_names_key} your list has to be made up of strings')

                        if len(kwarg_values) == 1:
                            raise ValueError(
                                f'{in_names_key} your list length must be greater than 1')

                        if len(kwarg_values) != len(in_names_values):
                            raise ValueError(
                                f"your list of {in_names_key} must be exactly {len(in_names_values)}")

                    input_names_dict[in_names_key] = kwarg_values
                    filled = True
                    break
                elif in_names_key == 'price' and kwarg_keys == 'prices':
                    raise ValueError(
                        f'you need to provide price instead of prices')
                elif in_names_key == 'prices' and kwarg_keys == 'price':
                    raise ValueError(
                        f'you need to provide prices instead of price')

            if not filled:
                input_names_dict[in_names_key] = in_names_values

        elif isinstance(in_names_values, str):
            for kwarg_keys, kwarg_values in kwargs.items():
                if in_names_key == kwarg_keys:
                    if not isinstance(kwarg_values, str):
                        raise ValueError(
                            f'{in_names_key} must be a string and not a list of strings')

                    input_names_dict[in_names_key] = kwarg_values
                    filled = True
                    break
                elif in_names_key == 'price' and kwarg_keys == 'prices':
                    raise ValueError(
                        f'you need to provide price instead of prices')
                elif in_names_key == 'prices' and kwarg_keys == 'price':
                    raise ValueError(
                        f'you need to provide prices instead of price')

            if not filled:
                input_names_dict[in_names_key] = in_names_values

    if bool(indicator_info['parameters']):
        param_dict = {}
        for param_names_key, param_names_values in indicator_info['parameters'].items():
            filled = False
            for kwarg_keys, kwarg_values in kwargs.items():
                if param_names_key == kwarg_keys:
                    if not isinstance(kwarg_values, (int, float, list)):
                        raise ValueError(
                            f'{param_names_key} must be a int float or a list of ints or floats')

                    if isinstance(kwarg_values, (int, float)):
                        users_args_list.append(np.asarray([kwarg_values]))

                    elif isinstance(kwarg_values, list):
                        if cart_product == False and combos == False and len(indicator_info['parameters']) > 1:
                            raise ValueError(
                                f"you can't have list(s) as args with indicators that have mutiple params without doing a combo or cart product")
                        if not all(isinstance(x, (int, float)) for x in kwarg_values):
                            raise ValueError(
                                f'{param_names_key} your list has to be filled with ints or floats')
                        if len(kwarg_values) == 1:
                            raise ValueError(
                                f'{param_names_key} your list length must be greater than 1')
                        if combos or cart_product:
                            if biggest == 1 and len(kwarg_values) > 1:
                                biggest = len(kwarg_values)
                            if biggest != len(kwarg_values) and combos:
                                raise ValueError(
                                    f'{param_names_key} when using combos, all listed items must be same length')

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
            f'You have to have a list for paramaters {ind_params} to use cart product or combos')
    
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
    ind_setings_len = final_user_args[0].size
    final_df = {}
    param_keys = ind_params.copy()
    
    if len(output_names) > 1:
        final_df = {}
        for o_names in output_names:
            final_df[o_names] = pd.DataFrame()
    else:
        final_df = pd.DataFrame()

    # c is the indicator result of the array within the tuple (array[x], array[x])
    for c in range(ind_setings_len):
        # x is the array object in the tuple (x,x)
        for x in final_user_args:
            if type(x[c]) == np.int_:
                ind_settings_tup = ind_settings_tup + (int(x[c]),)
            if type(x[c]) == np.float_:
                ind_settings_tup = ind_settings_tup + (float(x[c]),)

        if in_names_key == 'price':
            # these are the names called by the fun like talib('rsi').real - real is the output name
            if len(output_names) > 1:
                param_keys = [ind_name + '_' + x for x in param_keys] 
                for out_name in output_names:
                    # setting temp df of result out name
                    temp_df = Function(func_name)(
                        df_prices,
                        *ind_settings_tup,
                        price=input_names_dict[in_names_key]
                    )[out_name].to_frame()

                    # creating multindex for new results
                    temp_df.columns = pd.MultiIndex.from_tuples(
                        [ind_settings_tup],
                        names=param_keys
                    )
                    # param_keys = ind_params.copy()
                    # param_keys.insert(0, out_name + '_count')
                    # temp_df.columns = pd.MultiIndex.from_tuples(
                    #     [(c,) + ind_settings_tup],
                    #     names=param_keys
                    # )

                    # getting df from within list and concating to it
                    final_df[out_name] = pd.concat(
                        [final_df[out_name], temp_df], axis=1)
            else:
                # setting temp df of result out name
                temp_df = Function(func_name)(
                    df_prices,
                    *ind_settings_tup,
                    price=input_names_dict[in_names_key]
                ).to_frame()

                # creating multindex for new results
                temp_df.columns = pd.MultiIndex.from_tuples(
                        [ind_settings_tup],
                        names=[ind_name + '_' + param_keys[0]]
                    )

                # getting df from within list and concating to it
                final_df = pd.concat(
                    [final_df, temp_df], axis=1)

        elif in_names_key == 'prices':
            # these are the names called by the fun like talib('rsi').real - real is the output name
            if len(output_names) > 1:
                param_keys = [ind_name + '_' + x for x in param_keys] 
                for out_name in output_names:
                    # setting temp df of result out name
                    temp_df = Function(func_name)(
                        df_prices,
                        *ind_settings_tup,
                        prices=input_names_dict[in_names_key]
                    )[out_name].to_frame()

                    # creating multindex for new results
                    temp_df.columns = pd.MultiIndex.from_tuples(
                        [ind_settings_tup],
                        names=param_keys
                    )

                    # getting df from within list and concating to it
                    final_df[out_name] = pd.concat(
                        [final_df[out_name], temp_df], axis=1)
            else:
                # setting temp df of result out name
                temp_df = Function(func_name)(
                    df_prices,
                    *ind_settings_tup,
                    prices=input_names_dict[in_names_key]
                ).to_frame()

                # creating multindex for new results
                temp_df.columns = pd.MultiIndex.from_tuples(
                        [ind_settings_tup],
                        names=[ind_name + '_' + param_keys[0]]
                    )

                # getting df from within list and concating to it
                final_df = pd.concat(
                    [final_df, temp_df], axis=1)

        ind_settings_tup = ()
    return final_df

def talib_ind_info(func_name: str):
    return Function(func_name).info

def talib_func_list_website_link():
    print("https://ta-lib.github.io/ta-lib-python/funcs.html")
    
def talib_list_of_indicators():
    return get_functions()