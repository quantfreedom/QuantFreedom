import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
    pd_col_names = list(bigger_df.columns.names) + \
        list(smaller_df.columns.names)

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
    prices: Optional[pdFrame] = None,
    cand_ohlc: Optional[str] = None,
    plot_results: bool = False,
) -> pdFrame:
    """eval_is_below _summary_

    _extended_summary_

    Parameters
    ----------
    want_to_evaluate : pdFrame
        I think of this like I want to evaluate if the thing i am sending like EMA is below the price or is below the indicator data which could be rsi. So it would be i want to evalute if the EMA is below the RSI.
    user_args : Optional[Union[list[int, float], int, float, Array1d]], optional
        _description_, by default None
    indicator_data : Optional[pdFrame], optional
        _description_, by default None
    prices : Optional[pdFrame], optional
        _description_, by default None
    cand_ohlc : Optional[str], optional
        _description_, by default None

    Returns
    -------
    pdFrame
    """
    if not isinstance(want_to_evaluate, pdFrame):
        raise ValueError("Data must be a dataframe with multindex")

    want_to_evaluate_values = want_to_evaluate.values
    want_to_evaluate_name = want_to_evaluate.columns.names[1].split("_")[0]
    pd_col_names = list(want_to_evaluate.columns.names) + [
        want_to_evaluate_name + "_is_below"
    ]
    pd_multind_tuples = ()

    if isinstance(user_args, (list, Array1d)):
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError("user_args must be a list of ints or floats")
        user_args = np.asarray(user_args)

        eval_array = np.empty(
            (want_to_evaluate.shape[0], want_to_evaluate.shape[1] * user_args.size), dtype=np.bool_
        )

        eval_array_counter = 0
        temp_eval_values = want_to_evaluate.values.T
        for count, value in enumerate(want_to_evaluate.values.T):
            for eval_col in range(user_args.size):
                eval_array[:, eval_array_counter] = np.where(
                    value < user_args[eval_col], True, False
                )
                eval_array_counter += 1

                pd_multind_tuples = pd_multind_tuples + (
                    want_to_evaluate.columns[count] + (user_args[eval_col],),
                )

        if plot_results:
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=4),
                        name="Signals",
                    ),
                ]
            )
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()

    elif isinstance(prices, pdFrame):
        if cand_ohlc == None or cand_ohlc.lower() not in (
            "open",
            "high",
            "low",
            "close",
        ):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data"
            )

        eval_array = np.empty_like(want_to_evaluate, dtype=np.bool_)
        symbols = list(prices.columns.levels[0])
        eval_array_counter = 0

        for symbol in symbols:
            temp_prices_values = prices[symbol][cand_ohlc].values
            if not all(isinstance(x, (np.int_, np.float_)) for x in temp_prices_values):
                raise ValueError("price data must be ints or floats")

            temp_eval_values = want_to_evaluate[symbol].values.T

            for values in temp_eval_values:
                eval_array[:, eval_array_counter] = np.where(
                    values < temp_prices_values, True, False
                )

                pd_multind_tuples = pd_multind_tuples + (
                    want_to_evaluate.columns[eval_array_counter] +
                    (cand_ohlc,),
                )
                eval_array_counter += 1

        if plot_results:
            temp_prices = prices[prices.columns.levels[0][-1]]
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=plot_index,
                        open=temp_prices.open,
                        high=temp_prices.high,
                        low=temp_prices.low,
                        close=temp_prices.close,
                        name="Candles",
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=4, color='lightblue'),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=3, color='yellow'),
                        name="Signals",
                    ),
                ]
            )
            fig.update_xaxes(rangeslider_visible=False)
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()

    elif isinstance(indicator_data, pdFrame):
        want_to_evaluate_name = want_to_evaluate.columns.names[-1].split("_")[
            1]
        indicator_data_name = indicator_data.columns.names[-1].split("_")[0]

        pd_col_names = list(want_to_evaluate.columns.names) + [
            want_to_evaluate_name + "_is_below"
        ]

        want_to_evaluate_settings_tuple_list = want_to_evaluate.columns.to_list()

        eval_array = np.empty_like(want_to_evaluate,  dtype=np.bool_,)
        pd_multind_tuples = ()

        indicator_data_levels = list(indicator_data.columns)
        eval_array_counter = 0

        for level in indicator_data_levels:
            temp_indicator_values = indicator_data[level].values
            temp_evaluate_values = want_to_evaluate[level].values.T

            for values in temp_evaluate_values:
                eval_array[:, eval_array_counter] = np.where(
                    values < temp_indicator_values,
                    True,
                    False,
                )
                pd_multind_tuples = pd_multind_tuples + \
                    (want_to_evaluate_settings_tuple_list[eval_array_counter] + (
                        indicator_data_name,),)
                eval_array_counter += 1

        if plot_results:
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            temp_ind_values = indicator_data.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=plot_index,
                        y=temp_ind_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=4),
                        name="Signals",
                    ),
                ]
            )
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()

    elif isinstance(user_args, (int, float)):
        eval_array = np.where(want_to_evaluate_values < user_args, True, False)

        for col in range(want_to_evaluate.shape[1]):
            pd_multind_tuples = pd_multind_tuples + (
                want_to_evaluate.columns[col] + (user_args,),
            )

        if plot_results:
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=4),
                        name="Signals",
                    ),
                ]
            )
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()
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
    prices: Optional[pdFrame] = None,
    cand_ohlc: Optional[str] = None,
    plot_results: bool = False,
) -> pdFrame:
    """eval_is_above _summary_

    _extended_summary_

    Parameters
    ----------
    want_to_evaluate : pdFrame
        I think of this like I want to evaluate if the thing i am sending like EMA is above the price or is above the indicator data which could be rsi. So it would be i want to evalute if the EMA is above the RSI.
    user_args : Optional[Union[list[int, float], int, float, Array1d]], optional
        _description_, by default None
    indicator_data : Optional[pdFrame], optional
        _description_, by default None
    prices : Optional[pdFrame], optional
        _description_, by default None
    cand_ohlc : Optional[str], optional
        _description_, by default None

    Returns
    -------
    pdFrame
    """
    if not isinstance(want_to_evaluate, pdFrame):
        raise ValueError("Data must be a dataframe with multindex")

    want_to_evaluate_values = want_to_evaluate.values
    want_to_evaluate_name = want_to_evaluate.columns.names[1].split("_")[0]
    pd_col_names = list(want_to_evaluate.columns.names) + [
        want_to_evaluate_name + "_is_above"
    ]
    pd_multind_tuples = ()

    if isinstance(user_args, (list, Array1d)):
        if not all(isinstance(x, (int, float, np.int_, np.float_)) for x in user_args):
            raise ValueError("user_args must be a list of ints or floats")
        user_args = np.asarray(user_args)

        eval_array = np.empty(
            (want_to_evaluate.shape[0], want_to_evaluate.shape[1] * user_args.size), dtype=np.bool_
        )

        eval_array_counter = 0
        temp_eval_values = want_to_evaluate.values.T
        for count, value in enumerate(want_to_evaluate.values.T):
            for eval_col in range(user_args.size):
                eval_array[:, eval_array_counter] = np.where(
                    value > user_args[eval_col], True, False
                )
                eval_array_counter += 1

                pd_multind_tuples = pd_multind_tuples + (
                    want_to_evaluate.columns[count] + (user_args[eval_col],),
                )

        if plot_results:
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=4),
                        name="Signals",
                    ),
                ]
            )
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()

    elif isinstance(prices, pdFrame):
        if cand_ohlc == None or cand_ohlc.lower() not in (
            "open",
            "high",
            "low",
            "close",
        ):
            raise ValueError(
                "cand_ohlc must be open, high, low or close when sending price data"
            )

        eval_array = np.empty_like(want_to_evaluate, dtype=np.bool_)
        symbols = list(prices.columns.levels[0])
        eval_array_counter = 0

        for symbol in symbols:
            temp_prices_values = prices[symbol][cand_ohlc].values
            if not all(isinstance(x, (np.int_, np.float_)) for x in temp_prices_values):
                raise ValueError("price data must be ints or floats")

            temp_eval_values = want_to_evaluate[symbol].values.T

            for values in temp_eval_values:
                eval_array[:, eval_array_counter] = np.where(
                    values > temp_prices_values, True, False
                )

                pd_multind_tuples = pd_multind_tuples + (
                    want_to_evaluate.columns[eval_array_counter] +
                    (cand_ohlc,),
                )
                eval_array_counter += 1

        if plot_results:
            temp_prices = prices[prices.columns.levels[0][-1]]
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=plot_index,
                        open=temp_prices.open,
                        high=temp_prices.high,
                        low=temp_prices.low,
                        close=temp_prices.close,
                        name="Candles",
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=4, color='lightblue'),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=3, color='yellow'),
                        name="Signals",
                    ),
                ]
            )
            fig.update_xaxes(rangeslider_visible=False)
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()

    elif isinstance(indicator_data, pdFrame):
        want_to_evaluate_name = want_to_evaluate.columns.names[-1].split("_")[
            1]
        indicator_data_name = indicator_data.columns.names[-1].split("_")[0]

        pd_col_names = list(want_to_evaluate.columns.names) + [
            want_to_evaluate_name + "_is_above"
        ]

        want_to_evaluate_settings_tuple_list = want_to_evaluate.columns.to_list()

        eval_array = np.empty_like(want_to_evaluate,  dtype=np.bool_,)
        pd_multind_tuples = ()

        indicator_data_levels = list(indicator_data.columns)
        eval_array_counter = 0

        for level in indicator_data_levels:
            temp_indicator_values = indicator_data[level].values
            temp_evaluate_values = want_to_evaluate[level].values.T

            for values in temp_evaluate_values:
                eval_array[:, eval_array_counter] = np.where(
                    values > temp_indicator_values,
                    True,
                    False,
                )
                pd_multind_tuples = pd_multind_tuples + \
                    (want_to_evaluate_settings_tuple_list[eval_array_counter] + (
                        indicator_data_name,),)
                eval_array_counter += 1

        if plot_results:
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            temp_ind_values = indicator_data.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=plot_index,
                        y=temp_ind_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=4),
                        name="Signals",
                    ),
                ]
            )
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()

    elif isinstance(user_args, (int, float)):
        eval_array = np.where(want_to_evaluate_values > user_args, True, False)

        for col in range(want_to_evaluate.shape[1]):
            pd_multind_tuples = pd_multind_tuples + (
                want_to_evaluate.columns[col] + (user_args,),
            )

        if plot_results:
            temp_eval_values = want_to_evaluate.iloc[:, -1].values
            plot_index = want_to_evaluate.index

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=plot_index,
                        y=temp_eval_values,
                        mode="lines",
                        line=dict(width=2),
                        name=want_to_evaluate_name,
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            eval_array[:, -1],
                            temp_eval_values,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=4),
                        name="Signals",
                    ),
                ]
            )
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()
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