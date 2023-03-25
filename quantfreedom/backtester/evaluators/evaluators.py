import pandas as pd
import numpy as np
from quantfreedom._typing import (
    pdFrame, Union, Array1d, pdSeries, Optional
)


def combine_evals(
    bigger_df: pdFrame,
    smaller_df: pdFrame,
):
    bigger_df_values = bigger_df.values
    smaller_df_values = smaller_df.values
    combine_array = np.empty(
        (bigger_df.shape[0], bigger_df.shape[1]*smaller_df.shape[1]), dtype=np.bool_)
    final_df = pd.DataFrame()
    counter = 0
    
    for big_col in range(bigger_df.shape[1]):
        temp_bigger_df_array = bigger_df_values[:, big_col]
        for small_col in range(smaller_df.shape[1]):
            temp_smaller_df_array = smaller_df_values[:, small_col]
            combine_array[:, counter] = np.logical_and(
                temp_bigger_df_array == True,
                temp_smaller_df_array == True)
            temp_df = pd.DataFrame(
                combine_array[:, counter],
                index=bigger_df.index,
                columns=pd.MultiIndex.from_tuples(
                    [bigger_df.columns[big_col] + smaller_df.columns[small_col]],
                    names=list(bigger_df.columns.names) +
                    list(smaller_df.columns.names)
                )
            )
            final_df = pd.concat([final_df, temp_df], axis=1)
            counter += 1
    return final_df


def eval_is_below(
    ind_data: pdFrame,
    user_args: Optional[Union[list[int, float], int, float, Array1d]] = None,
    price: Optional[Union[pdFrame, pdSeries]] = None,
    cand_ohlc: Optional[str] = None,
) -> pdFrame:
    if not isinstance(ind_data, pdFrame):
        raise ValueError(
            "Data must be a dataframe with multindex")

    ind_data_values = ind_data.values
    eval_array = np.empty_like(ind_data_values, dtype=np.bool_)
    final_df = pd.DataFrame()
    ind_name_below = ind_data.columns.names[0].split('_')[
        0] + '_is_below'

    if isinstance(user_args, (list, Array1d)):
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError(
                "user_args must be a list of ints or floats")
        for col in range(ind_data.shape[1]):
            temp_ind_data_array = ind_data_values[:, col]
            for x in range(len(user_args)):
                for bar in range(ind_data_values.shape[0]):
                    eval_array[bar, col] = np.where(
                        temp_ind_data_array[bar] < user_args[x], True, False)

                temp_df = pd.DataFrame(
                    eval_array[:, col],
                    index=ind_data.index,
                    columns=pd.MultiIndex.from_tuples(
                        [ind_data.columns[col] + (user_args[x],)],
                        names=list(ind_data.columns.names) +
                        [ind_name_below]
                    )
                )
                final_df = pd.concat([final_df, temp_df], axis=1)

    elif isinstance(user_args, (int, float)):
        for col in range(ind_data.shape[1]):
            temp_ind_data_array = ind_data_values[:, col]
            for bar in range(ind_data_values.shape[0]):
                eval_array[bar, col] = np.where(
                    temp_ind_data_array[bar] < user_args, True, False)
            temp_df = pd.DataFrame(
                eval_array[:, col],
                index=ind_data.index,
                columns=pd.MultiIndex.from_tuples(
                    [ind_data.columns[col] + (user_args,)],
                    names=list(ind_data.columns.names) + [ind_name_below]
                )
            )
            final_df = pd.concat([final_df, temp_df], axis=1)

    elif isinstance(price, pdSeries):
        if cand_ohlc == None or cand_ohlc.lower() not in ('open', 'high', 'low', 'close'):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data")
        price_values = price.values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError(
                "price data must be ints or floats")
        for col in range(ind_data.shape[1]):
            temp_ind_data_array = ind_data_values[:, col]
            for bar in range(ind_data_values.shape[0]):
                eval_array[bar, col] = np.where(
                    price_values[bar] < temp_ind_data_array[bar], True, False)

            temp_df = pd.DataFrame(
                eval_array[:, col],
                index=ind_data.index,
                columns=pd.MultiIndex.from_tuples(
                    [ind_data.columns[col] + (cand_ohlc.capitalize(),)],
                    names=list(ind_data.columns.names) +
                    [ind_name_below]
                )
            )
            final_df = pd.concat([final_df, temp_df], axis=1)
    else:
        raise ValueError(
            "user_args must be a list of ints or floats or int or float or you need to send price data")

    return final_df


def eval_is_above(
    ind_data: pdFrame,
    user_args: Optional[Union[list[int, float], int, float, Array1d]] = None,
    price: Optional[Union[pdFrame, pdSeries]] = None,
    cand_ohlc: Optional[str] = None,
) -> pdFrame:
    if not isinstance(ind_data, pdFrame):
        raise ValueError(
            "Data must be a dataframe with multindex")

    ind_data_values = ind_data.values
    eval_array = np.empty_like(ind_data_values, dtype=np.bool_)
    final_df = pd.DataFrame()
    ind_name_above = ind_data.columns.names[0].split('_')[
        0] + '_is_above'

    if isinstance(user_args, (list, Array1d)):
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError(
                "user_args must be a list of ints or floats")
        for col in range(ind_data.shape[1]):
            temp_ind_data_array = ind_data_values[:, col]
            for x in range(len(user_args)):
                for bar in range(ind_data_values.shape[0]):
                    eval_array[bar, col] = np.where(
                        temp_ind_data_array[bar] > user_args[x], True, False)

                temp_df = pd.DataFrame(
                    eval_array[:, col],
                    index=ind_data.index,
                    columns=pd.MultiIndex.from_tuples(
                        [ind_data.columns[col] + (user_args[x],)],
                        names=list(ind_data.columns.names) +
                        [ind_name_above]
                    )
                )
                final_df = pd.concat([final_df, temp_df], axis=1)

    elif isinstance(user_args, (int, float)):
        for col in range(ind_data.shape[1]):
            temp_ind_data_array = ind_data_values[:, col]
            for bar in range(ind_data_values.shape[0]):
                eval_array[bar, col] = np.where(
                    temp_ind_data_array[bar] > user_args, True, False)
            temp_df = pd.DataFrame(
                eval_array[:, col],
                index=ind_data.index,
                columns=pd.MultiIndex.from_tuples(
                    [ind_data.columns[col] + (user_args,)],
                    names=list(ind_data.columns.names) + [ind_name_above]
                )
            )
            final_df = pd.concat([final_df, temp_df], axis=1)

    elif isinstance(price, pdSeries):
        if cand_ohlc == None or cand_ohlc.lower() not in ('open', 'high', 'low', 'close'):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data")
        price_values = price.values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError(
                "price data must be ints or floats")
        for col in range(ind_data.shape[1]):
            temp_ind_data_array = ind_data_values[:, col]
            for bar in range(ind_data_values.shape[0]):
                eval_array[bar, col] = np.where(
                    price_values[bar] > temp_ind_data_array[bar], True, False)

            temp_df = pd.DataFrame(
                eval_array[:, col],
                index=ind_data.index,
                columns=pd.MultiIndex.from_tuples(
                    [ind_data.columns[col] + (cand_ohlc.capitalize(),)],
                    names=list(ind_data.columns.names) +
                    [ind_name_above]
                )
            )
            final_df = pd.concat([final_df, temp_df], axis=1)
    else:
        raise ValueError(
            "user_args must be a list of ints or floats or int or float or you need to send price data")

    return final_df
