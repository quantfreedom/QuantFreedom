from typing import NamedTuple, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
from IPython.paths import get_ipython_cache_dir


def delete_dir(
    p: Path,
):
    """
    Delete info in directory

    Parameters
    ----------
    p : path
        path to directory
    """
    for sub in p.iterdir():
        if sub.is_dir():
            delete_dir(sub)
        else:
            sub.unlink()
    p.rmdir()


def clear_cache():
    """
    clears the python cache and numba cache
    """
    for p in Path(get_ipython_cache_dir() + "\\numba_cache").rglob("*.nb*"):
        p.unlink()
    for p in Path(__file__).parent.parent.rglob("numba_cache"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("__pycache__"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("cdk.out"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("*.py[co]"):
        p.unlink()


def pretty_qf(
    named_tuple: NamedTuple,
):
    """
    Prints named tuples in a pretty way

    Parameters
    ----------
    named_tuple : namedtuple
        must only be a named tuple
    """
    try:
        named_tuple._fields[0]
        items = []
        indent = str("    ")
        for x in range(len(named_tuple)):
            items.append(indent + named_tuple._fields[x] + " = " + str(named_tuple[x]) + ",\n")
        return print(type(named_tuple).__name__ + "(" + "\n" + "".join(items) + ")")
    except:
        return named_tuple


def pretty_qf_string(
    named_tuple: NamedTuple,
):
    """
    Prints named tuples in a pretty way

    Parameters
    ----------
    named_tuple : namedtuple
        must only be a named tuple
    """
    try:
        named_tuple._fields[0]
        items = []
        indent = str("    ")
        for x in range(len(named_tuple)):
            items.append(indent + named_tuple._fields[x] + " = " + str(named_tuple[x]) + ",\n")
        return type(named_tuple).__name__ + "(" + "\n" + "".join(items) + ")"
    except:
        return named_tuple


def generate_candles(
    number_of_candles: int = 100,
    plot_candles: bool = False,
    seed: Optional[int] = None,
):
    """
    Generate a dataframe filled with random candles

    Parameters
    ----------
    number_of_candles : int, 100
        number of candles you want to create
    seed : int, None
        random seed number
    plot_candles : bool, False
        If the candles should be graphed or not.

    Returns
    -------
    pdFrame
        Dataframe of open high low close
    """
    np.random.seed(seed)

    periods = number_of_candles * 48

    prices = np.around(30000 + np.random.normal(scale=1, size=periods).cumsum(), 2)

    data = pd.DataFrame(
        prices,
        index=pd.Index(
            pd.date_range("01/01/2000", periods=periods, freq="30min"),
            name="open_time",
        ),
        columns=["price"],
    )
    data = data.price.resample("D").ohlc()

    data.columns = pd.MultiIndex.from_tuples(
        tuples=[
            ("QuantFreedom", "open"),
            ("QuantFreedom", "high"),
            ("QuantFreedom", "low"),
            ("QuantFreedom", "close"),
        ],
        name=["symbol", "candle_info"],
    )
    if plot_candles:
        fig = go.Figure(
            data=go.Candlestick(
                x=data.index,
                open=data.iloc[:, 0],
                high=data.iloc[:, 1],
                low=data.iloc[:, 2],
                close=data.iloc[:, 3],
            )
        )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()

    return data
