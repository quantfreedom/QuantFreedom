# https://ta-lib.github.io/ta-lib-python/index.html
import pandas as pd
import numpy as np
from itertools import product
import plotly.graph_objects as go
from quantfreedom._typing import pdFrame, Optional, Array1d, Union


def testing_combine_evals(
    first_data: pdFrame,
    second_data: pdFrame,
    plot_results: bool = False,
    first_data_needs_prices: bool = False,
    prices: Optional[pdFrame] = None
):
    if len(first_data.columns.levels) < len(second_data.columns.levels):
        temp = len(first_data.columns.levels)
    else:
        temp = len(second_data.columns.levels)

    list_for_product = []
    pd_col_names = []
    for x in range(temp):
        if list(first_data.columns.levels[x]) == list(second_data.columns.levels[x]):
            list_for_product.append(list(first_data.columns.levels[x]))
            pd_col_names.append(first_data.columns.names[x])
    levels = list(product(*list_for_product))

    pd_col_names = pd_col_names + list(first_data.droplevel(pd_col_names, axis=1).columns.names) + \
        list(second_data.droplevel(pd_col_names, axis=1).columns.names)

    combine_array = np.empty(
        (first_data.shape[0], second_data[levels[0]].shape[1] * first_data[levels[0]].shape[1] * len(levels)), dtype=np.bool_
    )
    
    try :
        second_data[levels[0]].columns[0][0]
        temp_smaller_def_columns = list(second_data[levels[0]].columns)
    except:
        temp_smaller_def_columns = []
        for value in list(second_data[levels[0]].columns):
            temp_smaller_def_columns.append((value,))
    
    try :
        first_data[levels[0]].columns[0][0]
        temp_big_def_columns = list(first_data[levels[0]].columns)
    except:
        temp_big_def_columns = []
        for value in list(first_data[levels[0]].columns):
            temp_big_def_columns.append((value,))

    comb_counter = 0
    pd_multind_tuples = ()
    for level in levels:
        temp_big_df = first_data[level]
        temp_small_df = second_data[level]
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

    if plot_results and prices is not None:
        temp_first_data_values = first_data.iloc[:-1]
        plot_index = second_data.index

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=plot_index,
                    open=prices.open,
                    high=prices.high,
                    low=prices.low,
                    close=prices.close,
                    name="Candles",
                ),
                go.Scatter(
                    x=plot_index,
                    y=temp_first_data_values,
                    mode="lines",
                    line=dict(width=4, color='lightblue'),
                    name="Name",
                ),
                go.Scatter(
                    x=plot_index,
                    y=np.where(
                        combine_array[:, -1],
                        temp_first_data_values,
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

    return pd.DataFrame(
        combine_array,
        index=second_data.index,
        columns=pd.MultiIndex.from_tuples(
            tuples=list(pd_multind_tuples),
            names=pd_col_names,
        ),
    )
