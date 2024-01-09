import numpy as np
import pandas as pd
from quantfreedom.enums import CandleBodyType
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_candles_1_ind_same_pane(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "yellow",
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = go.Figure()
    fig.add_candlestick(
        x=datetimes,
        open=candles[:, 1],
        high=candles[:, 2],
        low=candles[:, 3],
        close=candles[:, 4],
        name="Candles",
    )
    fig.add_scatter(
        x=datetimes,
        y=indicator,
        name=ind_name,
        line_color=ind_color,
    )
    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    return fig


def plot_candles_1_ind_dif_pane(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "yellow",
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = make_subplots(
        cols=1,
        rows=2,
        shared_xaxes=True,
        subplot_titles=["Candles", ind_name],
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1,
    )
    fig.add_trace(
        go.Candlestick(
            x=datetimes,
            open=candles[:, CandleBodyType.Open],
            high=candles[:, CandleBodyType.High],
            low=candles[:, CandleBodyType.Low],
            close=candles[:, CandleBodyType.Close],
            name="Candles",
        ),
        col=1,
        row=1,
    )
    fig.add_trace(
        go.Scatter(
            x=datetimes,
            y=indicator,
            name=ind_name,
            line_color=ind_color,
        ),
        col=1,
        row=2,
    )

    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()


def plot_vwap(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "yellow",
):
    fig = plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name="VWAP",
        ind_color=ind_color,
    )
    fig.update_layout(
        title=dict(
            x=0.5,
            text="VWAP",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()


def plot_rma(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "yellow",
):
    fig = plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name="RMA",
        ind_color=ind_color,
    )

    fig.update_layout(
        title=dict(
            x=0.5,
            text="RMA",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()


def plot_wma(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "yellow",
):
    fig = plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name="WMA",
        ind_color=ind_color,
    )

    fig.update_layout(
        title=dict(
            x=0.5,
            text="WMA",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()


def plot_sma(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "yellow",
):
    fig = plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name="SMA",
        ind_color=ind_color,
    )

    fig.update_layout(
        title=dict(
            x=0.5,
            text="SMA",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()


def plot_ema(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "yellow",
):
    fig = plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name="EMA",
        ind_color=ind_color,
    )

    fig.update_layout(
        title=dict(
            x=0.5,
            text="EMA",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()


def plot_rsi(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "yellow",
):
    return plot_candles_1_ind_dif_pane(
        candles=candles,
        indicator=indicator,
        ind_name="RSI",
        ind_color=ind_color,
    )


def plot_atr(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "red",
):
    return plot_candles_1_ind_dif_pane(
        candles=candles,
        indicator=indicator,
        ind_name="ATR",
        ind_color=ind_color,
    )


def plot_stdev(
    candles: np.array,
    indicator: np.array,
    ind_color: str = "yellow",
):
    return plot_candles_1_ind_dif_pane(
        candles=candles,
        indicator=indicator,
        ind_name="STDEV",
        ind_color=ind_color,
    )


def plot_bollinger_bands(
    candles: np.array,
    indicator: np.array,
    ul_rgb: str = "48, 123, 255",
    basis_color_rgb: str = "255, 176, 0",
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = go.Figure(
        data=[
            go.Scatter(
                x=datetimes,
                y=indicator[:, 2],
                name="lower",
                line_color=f"rgb({ul_rgb})",
            ),
            go.Scatter(
                x=datetimes,
                y=indicator[:, 1],
                name="upper",
                line_color=f"rgb({ul_rgb})",
                fillcolor=f"rgba({ul_rgb}, 0.07)",
                fill="tonexty",
            ),
            go.Scatter(
                x=datetimes,
                y=indicator[:, 0],
                name="basis",
                line_color=f"rgb({basis_color_rgb})",
            ),
            go.Candlestick(
                x=datetimes,
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
        ]
    )
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        title=dict(
            x=0.5,
            text="Bollinger Bands",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()


def plot_macd(
    candles: np.array,
    indicator: np.array,
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = make_subplots(
        cols=1,
        rows=2,
        shared_xaxes=True,
        subplot_titles=["Candles", "MACD"],
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1,
    )
    # Candlestick chart for pricing
    fig.append_trace(
        go.Candlestick(
            x=datetimes,
            open=candles[:, CandleBodyType.Open],
            high=candles[:, CandleBodyType.High],
            low=candles[:, CandleBodyType.Low],
            close=candles[:, CandleBodyType.Close],
            name="Candles",
        ),
        col=1,
        row=1,
    )
    histogram = indicator[:, 0]
    ind_shift = np.roll(histogram, 1)
    ind_shift[0] = np.nan
    colors = np.where(
        histogram >= 0,
        np.where(ind_shift < histogram, "#26A69A", "#B2DFDB"),
        np.where(ind_shift < histogram, "#FFCDD2", "#FF5252"),
    )
    fig.append_trace(
        go.Bar(
            x=datetimes,
            y=histogram,
            name="histogram",
            marker_color=colors,
        ),
        row=2,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=datetimes,
            y=indicator[:, 1],
            name="macd",
            line_color="#2962FF",
        ),
        row=2,
        col=1,
    )
    fig.append_trace(
        go.Scatter(x=datetimes, y=indicator[:, 2], name="signal", line_color="#FF6D00"),
        row=2,
        col=1,
    )
    # Update options and show plot
    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()


def plot_squeeze_mom_lazybear(
    candles: np.array,
    indicator: np.array,
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = make_subplots(
        cols=1,
        rows=2,
        shared_xaxes=True,
        subplot_titles=["Candles", "Squeeze LazyBear"],
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1,
    )
    # Candlestick chart for pricing
    fig.append_trace(
        go.Candlestick(
            x=datetimes,
            open=candles[:, CandleBodyType.Open],
            high=candles[:, CandleBodyType.High],
            low=candles[:, CandleBodyType.Low],
            close=candles[:, CandleBodyType.Close],
            name="Candles",
        ),
        col=1,
        row=1,
    )
    ind_shift = np.roll(indicator, 1)
    ind_shift[0] = np.nan
    colors = np.where(
        (indicator >= 0),
        np.where(ind_shift < indicator, "#00E676", "#4CAF50"),
        np.where(ind_shift < indicator, "#FF5252", "#880E4F"),
    )
    fig.append_trace(
        go.Bar(
            x=datetimes,
            y=indicator,
            name="Squeeze LazyBear",
            marker_color=colors,
        ),
        row=2,
        col=1,
    )
    # Update options and show plot
    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()


def plot_or_results(
    candles: np.array,
    order_records_df: pd.DataFrame,
):
    fig = make_subplots(
        cols=1,
        rows=2,
        shared_xaxes=True,
        subplot_titles=["Candles", "Cumulative Realized PnL"],
        row_heights=[0.7, 0.3],
        vertical_spacing=0.1,
    )

    try:
        # Candles
        fig.add_trace(
            go.Candlestick(
                x=candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]"),
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
            col=1,
            row=1,
        )
    except:
        pass

    try:
        entries_df = order_records_df[order_records_df["order_status"] == "EntryFilled"]
        entries_dt = entries_df["datetime"]
        # Entries
        fig.add_trace(
            go.Scatter(
                x=entries_dt,
                y=entries_df["entry_price"],
                mode="markers",
                name="Entries",
                marker=dict(
                    size=10,
                    symbol="circle",
                    color="#00F6FF",
                    line=dict(
                        width=1,
                        color="DarkSlateGrey",
                    ),
                ),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        fig.add_trace(
            # Stop Losses
            go.Scatter(
                x=entries_dt,
                y=entries_df["sl_price"],
                mode="markers",
                name="Stop Losses",
                marker=dict(
                    size=10,
                    symbol="square",
                    color="#FFCA00",
                    line=dict(
                        width=1,
                        color="DarkSlateGrey",
                    ),
                ),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Take Profits
        fig.add_trace(
            go.Scatter(
                x=entries_dt,
                y=entries_df["tp_price"],
                mode="markers",
                name="Take Profits",
                marker=dict(
                    size=10,
                    symbol="triangle-up",
                    color="#FF7B00",
                    line=dict(
                        width=1,
                        color="DarkSlateGrey",
                    ),
                ),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Stop Loss Filled
        sl_filled_df = order_records_df[order_records_df["order_status"] == "StopLossFilled"]
        fig.add_trace(
            go.Scatter(
                x=sl_filled_df["datetime"],
                y=sl_filled_df["exit_price"],
                mode="markers",
                name="Stop Loss Filled",
                marker=dict(
                    size=10,
                    symbol="x",
                    color=np.where(
                        sl_filled_df["realized_pnl"] > 0,
                        "#14FF00",
                        "#FF00BB",
                    ),
                    line=dict(
                        width=1,
                        color="DarkSlateGrey",
                    ),
                ),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Take Profit Filled
        tp_filled_df = order_records_df[order_records_df["order_status"] == "TakeProfitFilled"]
        fig.add_trace(
            go.Scatter(
                x=tp_filled_df["datetime"],
                y=tp_filled_df["exit_price"],
                name="Take Profit Filled",
                mode="markers",
                marker=dict(
                    size=10,
                    symbol="star",
                    color="#14FF00",
                    line=dict(
                        width=1,
                        color="DarkSlateGrey",
                    ),
                ),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Moved SL
        move_sl_df = order_records_df[order_records_df["order_status"].isin(["MovedTSL", "MovedSLToBE"])]
        fig.add_trace(
            go.Scatter(
                x=move_sl_df["datetime"],
                y=move_sl_df["sl_price"],
                mode="markers",
                name="Moved SL",
                marker=dict(
                    size=10,
                    symbol="diamond-cross",
                    color="#F1FF00",
                    line=dict(
                        width=1,
                        color="DarkSlateGrey",
                    ),
                ),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        pnl_dt_df = order_records_df[~order_records_df["realized_pnl"].isna()]["datetime"]
        dt_list = pnl_dt_df.to_list()
        dt_list.insert(0, candles[0, 0].astype("datetime64[ms]"))

        pnl_df = order_records_df[~order_records_df["realized_pnl"].isna()]["realized_pnl"]
        pnl_list = pnl_df.to_list()
        pnl_list.insert(0, 0)
        cumulative_pnl = np.array(pnl_list).cumsum()
        # Cumulative Realized PnL
        fig.add_trace(
            go.Scatter(
                x=dt_list,
                y=cumulative_pnl,
                name="Cumulative Realized PnL",
                line_color="#3EA3FF",
            ),
            col=1,
            row=2,
        )
    except:
        pass
    fig.update_layout(height=1000, xaxis_rangeslider_visible=False)
    fig.update_yaxes(tickformat="$,")
    fig.show()


def plot_supertrend(
    candles: np.array,
    indicator: np.array,
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    lower = np.where(indicator[:, 1] < 0, indicator[:, 0], np.nan)
    upper = np.where(indicator[:, 1] > 0, indicator[:, 0], np.nan)
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=datetimes,
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
            go.Scatter(
                x=datetimes,
                y=upper,
                name="Upper Band",
            ),
            go.Scatter(
                x=datetimes,
                y=lower,
                name="Lower Band",
            ),
        ]
    )
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        title=dict(
            x=0.5,
            text="Super Trend",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()


def plot_linear_regression_candles_ugurvu_tv(
    lin_reg_candles: np.array,
    signal: np.array,
):
    datetimes = lin_reg_candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=datetimes,
                open=lin_reg_candles[:, CandleBodyType.Open],
                high=lin_reg_candles[:, CandleBodyType.High],
                low=lin_reg_candles[:, CandleBodyType.Low],
                close=lin_reg_candles[:, CandleBodyType.Close],
                name="Linear Regression Candles",
            ),
            go.Scatter(
                x=datetimes,
                y=signal,
                name="Signal",
                line_color="yellow",
            ),
        ]
    )
    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()


def plot_revolution_volatility_bands_tv(
    candles: np.array,
    upper_smooth: np.array,
    upper_falling: np.array,
    lower_smooth: np.array,
    lower_rising: np.array,
    ind_color: str = "yellow",
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = go.Figure()
    fig.add_candlestick(
        x=datetimes,
        open=candles[:, 1],
        high=candles[:, 2],
        low=candles[:, 3],
        close=candles[:, 4],
        name="Candles",
    )
    fig.add_scatter(
        x=datetimes,
        y=upper_smooth,
        name="Upper Smooth",
        line_color=ind_color,
    )
    fig.add_scatter(
        x=datetimes,
        y=upper_falling,
        name="Upper Falling",
        line=dict(color="blue", width=6),
    )
    fig.add_scatter(
        x=datetimes,
        y=lower_smooth,
        name="Lower Smooth",
        line_color=ind_color,
    )
    fig.add_scatter(
        x=datetimes,
        y=lower_rising,
        name="Lower Rising",
        line=dict(color="blue", width=6),
    )
    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()


def plot_volume(
    candles: np.array,
    moving_average: np.array = None,
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    close_prices = candles[:, CandleBodyType.Close]
    open_prices = candles[:, CandleBodyType.Open]
    volume = candles[:, CandleBodyType.Volume]

    fig = go.Figure()
    fig.add_bar(
        x=datetimes,
        y=volume,
        marker=dict(color=np.where(close_prices < open_prices, "red", "green")),
    )
    if moving_average:
        fig.add_scatter(
            x=datetimes,
            y=moving_average,
            name="Lower Rising",
        )
    fig.update_layout(height=400, xaxis_rangeslider_visible=False)
    fig.show()


"""
def plot_range_detextor_LuxAlgo(
    candles: np.array,
    box_x: np.array,
    box_y: np.array,
):
    datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=datetimes,
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
            go.Scatter(
                x=box_x,
                y=box_y,
                name="Range Detector",
                fill="toself",
            ),
        ]
    )
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        title=dict(
            x=0.5,
            text="Range Detector [LuxAlgo]",
            xanchor="center",
            font=dict(
                size=50,
            ),
        ),
    )
    fig.show()
"""
