# https://ta-lib.github.io/ta-lib-python/index.html
import pandas as pd
import numpy as np
from itertools import product
import plotly.graph_objects as go
from quantfreedom._typing import pdFrame, Optional, Array1d, Union
from plotly.subplots import make_subplots


def testing_combine_evals(
    first_eval_data: pdFrame,
    second_eval_data: pdFrame,
    plot_results: bool = False,
    first_eval_data_needs_prices: bool = False,
    second_eval_data_needs_prices: bool = False,
    prices: pdFrame = None,
    first_ind_data: pdFrame = None,
    second_ind_data: pdFrame = None,
) -> pdFrame:

    if plot_results and (first_ind_data is None or second_ind_data is None):
        raise ValueError(
            "Make sure you are sending first and second indicator data if you want to plot")
    elif plot_results:
        if first_eval_data_needs_prices and prices is None:
            raise ValueError("You need to provide prices to plot the candles")
        elif not first_eval_data_needs_prices and prices is not None:
            raise ValueError(
                "Make sure you set first_eval_data_needs_prices to true if you want to send price data")
    elif not plot_results and (
        first_eval_data_needs_prices or
        prices is not None or
        first_ind_data is not None or
        second_ind_data is not None
    ):
        raise ValueError(
            "Make sure you set plot_results to true if you want to send any plotting data.")

    if len(first_eval_data.columns.levels) < len(second_eval_data.columns.levels):
        temp = len(first_eval_data.columns.levels)
    else:
        temp = len(second_eval_data.columns.levels)

    list_for_product = []
    pd_col_names = []
    for x in range(temp):
        if list(first_eval_data.columns.levels[x]) == list(second_eval_data.columns.levels[x]):
            list_for_product.append(list(first_eval_data.columns.levels[x]))
            pd_col_names.append(first_eval_data.columns.names[x])
    levels = list(product(*list_for_product))

    pd_col_names = pd_col_names + list(first_eval_data.droplevel(pd_col_names, axis=1).columns.names) + \
        list(second_eval_data.droplevel(pd_col_names, axis=1).columns.names)

    combine_array = np.empty(
        (first_eval_data.shape[0], first_eval_data[levels[0]].shape[1] * second_eval_data[levels[0]].shape[1] * len(levels)), dtype=np.bool_
    )

    try:
        second_eval_data[levels[0]].columns[0][0]
        temp_smaller_def_columns = list(second_eval_data[levels[0]].columns)
    except:
        temp_smaller_def_columns = []
        for value in list(second_eval_data[levels[0]].columns):
            temp_smaller_def_columns.append((value,))

    try:
        first_eval_data[levels[0]].columns[0][0]
        temp_big_def_columns = list(first_eval_data[levels[0]].columns)
    except:
        temp_big_def_columns = []
        for value in list(first_eval_data[levels[0]].columns):
            temp_big_def_columns.append((value,))

    comb_counter = 0
    pd_multind_tuples = ()
    for level in levels:
        temp_big_df = first_eval_data[level]
        temp_small_df = second_eval_data[level]
        for big_count, big_values in enumerate(temp_big_df.values.T):

            for small_count, small_values in enumerate(temp_small_df.values.T):

                combine_array[:, comb_counter] = np.logical_and(
                    big_values == True, small_values == True
                )

                pd_multind_tuples = pd_multind_tuples + (
                    level + temp_big_def_columns[big_count] +
                    temp_smaller_def_columns[small_count],
                )

                comb_counter += 1

    if plot_results:
        plot_index = second_eval_data.index
        
        temp_first_ind_data = first_ind_data.iloc[:, -1]
        temp_second_ind_data = second_ind_data.iloc[:, -1]

        temp_combine_array = combine_array[:, -1]

        # candle data with subplot
        if first_eval_data_needs_prices and not second_eval_data_needs_prices:
            temp_prices = prices[list(prices.columns)[-1][0]]
            fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
            )
            fig.add_traces(
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
                        y=temp_first_ind_data,
                        mode="lines",
                        line=dict(width=3, color='#60BFE1'),
                        name="First Ind",
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            temp_combine_array,
                            temp_first_ind_data,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=3, color='yellow'),
                        name="Combo Signals",
                    ),
                ],
                rows=1,
                cols=1,
            )
            fig.add_traces(
                data=[
                    go.Scatter(
                        x=plot_index,
                        y=temp_second_ind_data,
                        mode="lines",
                        line=dict(width=2, color='#60BFE1'),
                        name="Second Ind",
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            temp_combine_array,
                            temp_second_ind_data,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=3, color='yellow'),
                        name="Combo Signals",
                    ),
                ],
                rows=2,
                cols=1,
            )
            fig.update_xaxes(rangeslider_visible=False)
            fig.update_layout(height=700, title="Last Column of the Results")
            fig.show()
        elif first_eval_data_needs_prices and second_eval_data_needs_prices:
            temp_prices = prices[list(prices.columns)[-1][0]]
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

                    # First Plot
                    go.Scatter(
                        x=plot_index,
                        y=temp_first_ind_data,
                        mode="lines",
                        line=dict(width=3, color='#60BFE1'),
                        name="First Ind",
                    ),

                    # Second Plot
                    go.Scatter(
                        x=plot_index,
                        y=temp_second_ind_data,
                        mode="lines",
                        line=dict(width=3, color='#84E5AC'),
                        name="Second Ind",
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            temp_combine_array,
                            temp_second_ind_data,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=3, color='yellow'),
                        name="Combo Signals",
                    ),
                ],
            )
            fig.update_xaxes(rangeslider_visible=False)
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()
        elif not first_eval_data_needs_prices and not second_eval_data_needs_prices:
            fig = go.Figure(
                data=[
                    # First Plot
                    go.Scatter(
                        x=plot_index,
                        y=temp_first_ind_data,
                        mode="lines",
                        line=dict(width=2, color='green'),
                        name="First Ind",
                    ),

                    # Second Plot
                    go.Scatter(
                        x=plot_index,
                        y=temp_second_ind_data,
                        mode="lines",
                        line=dict(width=3, color='red'),
                        name="Second Ind",
                    ),
                    go.Scatter(
                        x=plot_index,
                        y=np.where(
                            temp_combine_array,
                            temp_second_ind_data,
                            np.nan,
                        ),
                        mode="markers",
                        marker=dict(size=3, color='yellow'),
                        name="Combo Signals",
                    ),
                ],
            )
            fig.update_xaxes(rangeslider_visible=False)
            fig.update_layout(height=500, title="Last Column of the Results")
            fig.show()
   
    return pd.DataFrame(
        combine_array,
        index=second_eval_data.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=pd_col_names,
        ),
    )
