import pandas as pd
import numpy as np
from quantfreedom._typing import (
   pdFrame, Union, Array1d
)

def eval_is_below(
    ind_data: pdFrame,
    user_args: Union[list[int, float], int, float, Array1d],
)-> pdFrame:
    if not isinstance(ind_data, pdFrame):
        raise ValueError(
            "Data must be a dataframe with multindex")

    data_values = ind_data.values
    eval_array = np.empty_like(data_values, dtype=np.bool_)
    final_df = pd.DataFrame()
    ind_name_below = ind_data.columns.names[0].split('_')[
        0] + '_is_below'

    if isinstance(user_args, (list, Array1d)):
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError(
                "user_args must be a list of ints or floats")
        for col in range(ind_data.shape[1]):
            temp_data_array = data_values[:, col]
            for x in range(len(user_args)):
                for bar in range(data_values.shape[0]):
                    eval_array[bar, col] = np.where(
                        temp_data_array[bar] < user_args[x], True, False)

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
            temp_data_array = data_values[:, col]
            for bar in range(data_values.shape[0]):
                eval_array[bar, col] = np.where(
                    temp_data_array[bar] < user_args, True, False)
            temp_df = pd.DataFrame(
                eval_array[:, col],
                index=ind_data.index,
                columns=pd.MultiIndex.from_tuples(
                    [ind_data.columns[col] + (user_args,)],
                    names=list(ind_data.columns.names) + [ind_name_below]
                )
            )
            final_df = pd.concat([final_df, temp_df], axis=1)
    else:
        raise ValueError(
            "user_args must be a list of ints or floats or int or float ")

    return final_df


def eval_is_above(
    ind_data: pdFrame,
    user_args: Union[list[int, float], int, float, Array1d],
)-> pdFrame:
    if not isinstance(ind_data, pdFrame):
        raise ValueError(
            "Data must be a dataframe with multindex")

    data_values = ind_data.values
    eval_array = np.empty_like(data_values, dtype=np.bool_)
    final_df = pd.DataFrame()
    ind_name_below = ind_data.columns.names[0].split('_')[
        0] + '_is_below'

    if isinstance(user_args, (list, Array1d)):
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError(
                "user_args must be a list of ints or floats")
        for col in range(ind_data.shape[1]):
            temp_data_array = data_values[:, col]
            for x in range(len(user_args)):
                for bar in range(data_values.shape[0]):
                    eval_array[bar, col] = np.where(
                        temp_data_array[bar] > user_args[x], True, False)

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
            temp_data_array = data_values[:, col]
            for bar in range(data_values.shape[0]):
                eval_array[bar, col] = np.where(
                    temp_data_array[bar] > user_args, True, False)
            temp_df = pd.DataFrame(
                eval_array[:, col],
                index=ind_data.index,
                columns=pd.MultiIndex.from_tuples(
                    [ind_data.columns[col] + (user_args,)],
                    names=list(ind_data.columns.names) + [ind_name_below]
                )
            )
            final_df = pd.concat([final_df, temp_df], axis=1)
    else:
        raise ValueError(
            "user_args must be a list of ints or floats or int or float ")

    return final_df

