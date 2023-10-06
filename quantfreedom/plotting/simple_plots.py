import plotly.graph_objects as go
from plotly.subplots import make_subplots

from quantfreedom._typing import pdFrame

def plot_on_candles_1_chart(
    ta_lib_data: pdFrame,
    price_data: pdFrame,
):
    plot_index = price_data.index

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=plot_index,
                open=price_data.iloc[:, -4].values,
                high=price_data.iloc[:, -3].values,
                low=price_data.iloc[:, -2].values,
                close=price_data.iloc[:, -1].values,
                name="Candles",
            ),
            go.Scatter(
                x=plot_index,
                y=ta_lib_data.iloc[:, -1],
                mode="lines",
                line=dict(width=2, color="lightblue"),
            ),
        ]
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_layout(height=500, title="Last Column of the Results")
    fig.show()


def plot_results_candles_and_chart(
    ta_lib_data: pdFrame,
    price_data: pdFrame,
):
    plot_index = price_data.index
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.4],
    )

    fig.add_traces(
        data=go.Candlestick(
            x=plot_index,
            open=price_data.iloc[:, -4].values,
            high=price_data.iloc[:, -3].values,
            low=price_data.iloc[:, -2].values,
            close=price_data.iloc[:, -1].values,
            name="Candles",
        ),
        rows=1,
        cols=1,
    )
    fig.add_traces(
        data=go.Scatter(
            x=plot_index,
            y=ta_lib_data.iloc[:, -1],
            mode="lines",
            line=dict(width=2, color="lightblue"),
        ),
        rows=2,
        cols=1,
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_layout(height=700, title="Last Column of the Results")
    fig.show()
