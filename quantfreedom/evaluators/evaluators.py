import pandas as pd
import numpy as np
from quantfreedom._typing import pdFrame, Union, Array1d, Optional, pdSeries


def combine_evals(
    bigger_df: pdFrame,
    smaller_df: pdFrame,
):
    bigger_df_values = bigger_df.values
    smaller_df_values = smaller_df.values
    combine_array = np.empty(
        (bigger_df.shape[0], bigger_df.shape[1] * smaller_df.shape[1]), dtype=np.bool_
    )
    counter = 0
    pd_multind_tuples = ()
    pd_col_names = list(bigger_df.columns.names) + list(smaller_df.columns.names)

    for big_col in range(bigger_df.shape[1]):
        temp_bigger_df_array = bigger_df_values[:, big_col]
        for small_col in range(smaller_df.shape[1]):
            temp_smaller_df_array = smaller_df_values[:, small_col]

            combine_array[:, counter] = np.logical_and(
                temp_bigger_df_array == True, temp_smaller_df_array == True
            )

            pd_multind_tuples = pd_multind_tuples + (
                bigger_df.columns[big_col] + smaller_df.columns[small_col],
            )

            counter += 1

    return pd.DataFrame(
        combine_array,
        index=bigger_df.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples), names=pd_col_names
        ),
    )


def eval_is_below(
    want_to_evaluate: pdFrame,
    user_args: Optional[Union[list[int, float], int, float, Array1d]] = None,
    indicator_data: Optional[pdFrame] = None,
    df_prices: Optional[pdFrame] = None,
    cand_ohlc: Optional[str] = None,
) -> pdFrame:
    if not isinstance(want_to_evaluate, pdFrame):
        raise ValueError("Data must be a dataframe with multindex")

    want_to_evaluate_values = want_to_evaluate.values
    pd_col_names = list(want_to_evaluate.columns.names) + [
        want_to_evaluate.columns.names[0].split("_")[0] + "_is_below"
    ]
    pd_multind_tuples = ()

    if isinstance(user_args, (list, Array1d)):
        eval_array = np.empty(
            (want_to_evaluate.shape[0], want_to_evaluate.shape[1] * len(user_args)), dtype=np.bool_
        )
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError("user_args must be a list of ints or floats")
        eval_array_counter = 0
        for col in range(want_to_evaluate.shape[1]):
            temp_array = want_to_evaluate_values[:, col]
            for eval_col in range(user_args.size):
                eval_array[:, eval_array_counter] = np.where(
                    temp_array < user_args[eval_col], True, False
                )
                eval_array_counter += 1

                pd_multind_tuples = pd_multind_tuples + (
                    want_to_evaluate.columns[col] + (user_args[eval_col],),
                )

    elif isinstance(user_args, (int, float)):
        eval_array = np.where(want_to_evaluate_values < user_args, True, False)

        for col in range(want_to_evaluate.shape[1]):
            pd_multind_tuples = pd_multind_tuples + (
                want_to_evaluate.columns[col] + (user_args,),
            )

    elif isinstance(df_prices, pdFrame):
        eval_array = np.empty_like(want_to_evaluate, dtype=np.bool_)
        if cand_ohlc == None or cand_ohlc.lower() not in (
            "open",
            "high",
            "low",
            "close",
        ):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data"
            )
        price_values = getattr(df_prices, cand_ohlc).values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError("price data must be ints or floats")
        for col in range(want_to_evaluate.shape[1]):
            eval_array[:, col] = np.where(
                want_to_evaluate_values[:, col] < price_values, True, False
            )

            pd_multind_tuples = pd_multind_tuples + (
                want_to_evaluate.columns[col] + (cand_ohlc + "_price",),
            )

    elif isinstance(indicator_data, pdFrame):
        want_to_evaluate_name = want_to_evaluate.columns.names[-1].split("_")[1]
        indicator_data_name = indicator_data.columns.names[0].split("_")[0]

        pd_col_names = list(want_to_evaluate.columns.names) + [
            want_to_evaluate_name + "_is_below"
        ]

        want_to_evaluate_settings_tuple_list = want_to_evaluate.columns.to_list()

        eval_array = np.empty(
            (want_to_evaluate.shape[0], len(want_to_evaluate_settings_tuple_list)),
            dtype=np.bool_,
        )
        pd_multind_tuples = ()
        for count, value in enumerate(want_to_evaluate_settings_tuple_list):
            temp_evaluate_values = want_to_evaluate[value].values
            temp_indicator_values = indicator_data[value[0]].values.flatten()
            if not all(
                isinstance(x, (np.int_, np.float_)) for x in temp_evaluate_values
            ) and not all(isinstance(x, (np.int_, np.float_)) for x in temp_indicator_values):
                raise ValueError("want to eval or indicator data must be ints or floats")
            eval_array[:, count] = np.where(
                temp_evaluate_values < temp_indicator_values,
                True,
                False,
            )
            pd_multind_tuples = pd_multind_tuples + (value + (indicator_data_name,),)

    else:
        raise ValueError(
            "something is wrong with what you sent please make sure the type of variable you are sending matches with the type required"
        )

    return pd.DataFrame(
        eval_array,
        index=want_to_evaluate.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=pd_col_names,
        ),
    )


def eval_is_above(
    want_to_evaluate: pdFrame,
    user_args: Optional[Union[list[int, float], int, float, Array1d]] = None,
    indicator_data: Optional[pdFrame] = None,
    df_prices: Optional[pdFrame] = None,
    cand_ohlc: Optional[str] = None,
) -> pdFrame:
    if not isinstance(want_to_evaluate, pdFrame):
        raise ValueError("Data must be a dataframe with multindex")

    want_to_evaluate_values = want_to_evaluate.values
    pd_col_names = list(want_to_evaluate.columns.names) + [
        want_to_evaluate.columns.names[0].split("_")[0] + "_is_above"
    ]
    pd_multind_tuples = ()

    if isinstance(user_args, (list, Array1d)):
        eval_array = np.empty(
            (want_to_evaluate.shape[0], want_to_evaluate.shape[1] * len(user_args)), dtype=np.bool_
        )
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError("user_args must be a list of ints or floats")
        eval_array_counter = 0
        for col in range(want_to_evaluate.shape[1]):
            temp_array = want_to_evaluate_values[:, col]
            for eval_col in range(user_args.size):
                eval_array[:, eval_array_counter] = np.where(
                    temp_array > user_args[eval_col], True, False
                )
                eval_array_counter += 1
                pd_multind_tuples = pd_multind_tuples + (
                    want_to_evaluate.columns[col] + (user_args[eval_col],),
                )

    elif isinstance(user_args, (int, float)):
        eval_array = np.where(want_to_evaluate_values > user_args, True, False)

        for col in range(want_to_evaluate.shape[1]):
            pd_multind_tuples = pd_multind_tuples + (
                want_to_evaluate.columns[col] + (user_args,),
            )

    elif isinstance(df_prices, pdFrame):
        eval_array = np.empty_like(want_to_evaluate, dtype=np.bool_)
        if cand_ohlc == None or cand_ohlc.lower() not in (
            "open",
            "high",
            "low",
            "close",
        ):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data"
            )
        price_values = getattr(df_prices, cand_ohlc).values
        if not all(isinstance(x, (np.int_, np.float_)) for x in price_values):
            raise ValueError("price data must be ints or floats")
        for col in range(want_to_evaluate.shape[1]):
            eval_array[:, col] = np.where(
                want_to_evaluate_values[:, col] > price_values, True, False
            )

            pd_multind_tuples = pd_multind_tuples + (
                want_to_evaluate.columns[col] + (cand_ohlc + "_price",),
            )

    elif isinstance(indicator_data, pdFrame):
        want_to_evaluate_name = want_to_evaluate.columns.names[-1].split("_")[1]
        indicator_data_name = indicator_data.columns.names[0].split("_")[0]

        pd_col_names = list(want_to_evaluate.columns.names) + [
            want_to_evaluate_name + "_is_above"
        ]

        want_to_evaluate_settings_tuple_list = want_to_evaluate.columns.to_list()

        eval_array = np.empty(
            (want_to_evaluate.shape[0], len(want_to_evaluate_settings_tuple_list)),
            dtype=np.bool_,
        )
        pd_multind_tuples = ()
        for count, value in enumerate(want_to_evaluate_settings_tuple_list):
            temp_evaluate_values = want_to_evaluate[value].values
            temp_indicator_values = indicator_data[value[0]].values.flatten()
            if not all(
                isinstance(x, (np.int_, np.float_)) for x in temp_evaluate_values
            ) and not all(isinstance(x, (np.int_, np.float_)) for x in temp_indicator_values):
                raise ValueError("want to eval or indicator data must be ints or floats")
            eval_array[:, count] = np.where(
                temp_evaluate_values > temp_indicator_values,
                True,
                False,
            )
            pd_multind_tuples = pd_multind_tuples + (value + (indicator_data_name,),)

    else:
        raise ValueError(
            "user_args must be a list of ints or floats or int or float or you need to send price as a pandas dataframe"
        )

    return pd.DataFrame(
        eval_array,
        index=want_to_evaluate.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=pd_col_names,
        ),
    )
