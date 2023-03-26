import pandas as pd
import numpy as np
from quantfreedom._typing import (
    pdFrame, Union, Array1d, Optional,pdSeries
)


def combine_evals(
    bigger_df: pdFrame,
    smaller_df: pdFrame,
):
    bigger_df_values = bigger_df.values
    smaller_df_values = smaller_df.values
    combine_array = np.empty(
        (bigger_df.shape[0], bigger_df.shape[1]*smaller_df.shape[1]), dtype=np.bool_)
    counter = 0
    pd_multind_tuples = ()
    pd_col_names = list(bigger_df.columns.names) + \
        list(smaller_df.columns.names)

    for big_col in range(bigger_df.shape[1]):
        temp_bigger_df_array = bigger_df_values[:, big_col]
        for small_col in range(smaller_df.shape[1]):
            temp_smaller_df_array = smaller_df_values[:, small_col]

            combine_array[:, counter] = np.logical_and(
                temp_bigger_df_array == True,
                temp_smaller_df_array == True)

            pd_multind_tuples = pd_multind_tuples + \
                (bigger_df.columns[big_col] + smaller_df.columns[small_col],)

            counter += 1

    return pd.DataFrame(
        combine_array,
        index=bigger_df.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=pd_col_names
        )
    )


def eval_is_below(
    ind_data: pdFrame,
    user_args: Optional[Union[list[int, float], int, float, Array1d]] = None,
    ind_results: Optional[Union[pdFrame, pdSeries]] = None,
    df_prices: Optional[pdFrame] = None,
    cand_ohlc: Optional[str] = None,
) -> pdFrame:
    if not isinstance(ind_data, pdFrame):
        raise ValueError(
            "Data must be a dataframe with multindex")

    ind_data_values = ind_data.values
    pd_col_names = list(ind_data.columns.names) + \
        [ind_data.columns.names[0].split('_')[0] + '_is_below']
    pd_multind_tuples = ()

    if isinstance(user_args, (list, Array1d)):
        eval_array = np.empty(
            (ind_data.shape[0], ind_data.shape[1] * len(user_args)), dtype=np.bool_)
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError(
                "user_args must be a list of ints or floats")
        for col in range(ind_data.shape[1]):
            temp_array = ind_data_values[:, col]
            for eval_col in range(user_args.size):
                eval_array[:, eval_col] = np.where(
                    temp_array < user_args[eval_col], True, False)

                pd_multind_tuples = pd_multind_tuples + \
                    (ind_data.columns[col] + (user_args[eval_col],),)

    elif isinstance(user_args, (int, float)):
        eval_array = np.where(ind_data_values < user_args, True, False)

        for col in range(ind_data.shape[1]):
            pd_multind_tuples = pd_multind_tuples + \
                (ind_data.columns[col] + (user_args,),)

    elif isinstance(df_prices, pdFrame):
        eval_array = np.empty(ind_data, dtype=np.bool_)
        if cand_ohlc == None or cand_ohlc.lower() not in ('open', 'high', 'low', 'close'):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data")
        price_values = getattr(df_prices, cand_ohlc).values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError(
                "price data must be ints or floats")
        for col in range(ind_data.shape[1]):
            eval_array[:, col] = np.where(
                ind_data_values[:, col] < price_values, True, False)

            pd_multind_tuples = pd_multind_tuples + \
                (ind_data.columns[col] + (cand_ohlc,),)
    
    elif isinstance(ind_results, pdSeries):
        eval_array = np.empty_like(ind_data, dtype=np.bool_)
        price_values = ind_results.values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError(
                "price data must be ints or floats")
        for col in range(ind_data.shape[1]):
            eval_array[:, col] = np.where(
                ind_data_values[:, col] > price_values, True, False)

            pd_multind_tuples = pd_multind_tuples + \
                (ind_data.columns[col] + ('something',),)            
    else:
        raise ValueError(
            "user_args must be a list of ints or floats or int or float or you need to send price data")

    return pd.DataFrame(
        eval_array,
        index=ind_data.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=pd_col_names,
        )
    )


def eval_is_above(
    ind_data: pdFrame,
    user_args: Optional[Union[list[int, float], int, float, Array1d]] = None,
    ind_results: Optional[Union[pdFrame, pdSeries]] = None,
    df_prices: Optional[pdFrame] = None,
    cand_ohlc: Optional[str] = None,
) -> pdFrame:
    if not isinstance(ind_data, pdFrame):
        raise ValueError(
            "Data must be a dataframe with multindex")

    ind_data_values = ind_data.values
    pd_col_names = list(ind_data.columns.names) + \
        [ind_data.columns.names[0].split('_')[0] + '_is_above']
    pd_multind_tuples = ()

    if isinstance(user_args, (list, Array1d)):
        eval_array = np.empty(
            (ind_data.shape[0], ind_data.shape[1] * len(user_args)), dtype=np.bool_)
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError(
                "user_args must be a list of ints or floats")
        for col in range(ind_data.shape[1]):
            temp_array = ind_data_values[:, col]
            for eval_col in range(user_args.size):
                eval_array[:, eval_col] = np.where(
                    temp_array > user_args[eval_col], True, False)

                pd_multind_tuples = pd_multind_tuples + \
                    (ind_data.columns[col] + (user_args[eval_col],),)

    elif isinstance(user_args, (int, float)):
        eval_array = np.where(ind_data_values > user_args, True, False)

        for col in range(ind_data.shape[1]):
            pd_multind_tuples = pd_multind_tuples + \
                (ind_data.columns[col] + (user_args,),)

    elif isinstance(df_prices, pdFrame):
        eval_array = np.empty_like(ind_data, dtype=np.bool_)
        if cand_ohlc == None or cand_ohlc.lower() not in ('open', 'high', 'low', 'close'):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data")
        price_values = getattr(df_prices, cand_ohlc).values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError(
                "price data must be ints or floats")
        for col in range(ind_data.shape[1]):
            eval_array[:, col] = np.where(
                ind_data_values[:, col] > price_values, True, False)

            pd_multind_tuples = pd_multind_tuples + \
                (ind_data.columns[col] + (cand_ohlc,),)
    
    elif isinstance(ind_results, pdSeries):
        eval_array = np.empty_like(ind_data, dtype=np.bool_)
        price_values = ind_results.values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError(
                "price data must be ints or floats")
        for col in range(ind_data.shape[1]):
            eval_array[:, col] = np.where(
                ind_data_values[:, col] > price_values, True, False)

            pd_multind_tuples = pd_multind_tuples + \
                (ind_data.columns[col] + ('something',),)

    else:
        raise ValueError(
            "user_args must be a list of ints or floats or int or float or you need to send price as a pandas dataframe")

    return pd.DataFrame(
        eval_array,
        index=ind_data.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=pd_col_names,
        )
    )
