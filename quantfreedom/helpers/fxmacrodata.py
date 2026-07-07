"""Helpers for loading FXMacroData forex history into QuantFreedom candles.

FXMacroData provides one daily spot reference rate per currency pair. These
helpers map that rate to open, high, low, and close so it can be used anywhere a
``FootprintCandlesTuple`` is accepted.
"""

from __future__ import annotations

import json
import os
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

from quantfreedom.core.enums import FootprintCandlesTuple


FXMACRODATA_API_BASE_URL = "https://fxmacrodata.com/api/v1"


def split_currency_pair(pair: str) -> tuple[str, str]:
    """Return normalized base and quote currency codes from EURUSD or EUR/USD."""
    normalized = pair.replace("/", "").replace("-", "").replace("_", "").upper()
    if len(normalized) != 6:
        raise ValueError("currency pair must look like 'EURUSD' or 'EUR/USD'")
    return normalized[:3], normalized[3:]


def _first_present(row: dict, keys: tuple[str, ...]):
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value
    return None


def fxmacrodata_rows_to_footprint_candles(
    rows: Iterable[dict],
    *,
    duration_seconds: int = 86_400,
) -> FootprintCandlesTuple:
    """Convert FXMacroData forex rows to a QuantFreedom ``FootprintCandlesTuple``.

    Parameters
    ----------
    rows : Iterable[dict]
        Rows from the FXMacroData forex endpoint. Each row must include a date
        key such as ``date`` or ``timestamp`` and a rate key such as ``value`` or
        ``rate``.
    duration_seconds : int
        Candle duration to assign to every daily FXMacroData observation.

    Returns
    -------
    FootprintCandlesTuple
        Candles with the FX spot rate mapped to open, high, low, and close, and
        zero volume fields.
    """
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")

    records = []
    for row in rows:
        date_value = _first_present(row, ("date", "time", "timestamp", "datetime"))
        rate = _first_present(row, ("value", "val", "rate", "close", "fx_rate"))
        if date_value is None or rate is None:
            continue
        records.append({"timestamp": pd.to_datetime(date_value, utc=True), "rate": float(rate)})

    if not records:
        raise ValueError("FXMacroData response did not include dated rate rows")

    candles_df = pd.DataFrame.from_records(records)
    candles_df = candles_df.drop_duplicates(subset="timestamp").sort_values("timestamp")
    open_timestamps = (candles_df["timestamp"].astype("int64") // 1_000_000).to_numpy(dtype=np.int64)
    rates = candles_df["rate"].to_numpy(dtype=float)
    zeros = np.zeros(rates.shape[0], dtype=float)

    return FootprintCandlesTuple(
        candle_open_datetimes=open_timestamps.astype("datetime64[ms]"),
        candle_open_timestamps=open_timestamps,
        candle_durations_seconds=np.full(rates.shape[0], duration_seconds),
        candle_open_prices=rates,
        candle_high_prices=rates,
        candle_low_prices=rates,
        candle_close_prices=rates,
        candle_asset_volumes=zeros,
        candle_usdt_volumes=zeros,
    )


def fetch_fxmacrodata_candles(
    pair: str,
    start_date: str,
    end_date: str,
    *,
    api_key: str | None = None,
    base_url: str = FXMACRODATA_API_BASE_URL,
    timeout: float = 30,
    duration_seconds: int = 86_400,
) -> FootprintCandlesTuple:
    """Fetch FXMacroData forex history as QuantFreedom candles."""
    base_currency, quote_currency = split_currency_pair(pair)
    params = {"start_date": start_date, "end_date": end_date}
    headers = {}
    api_key = api_key or os.getenv("FXMACRODATA_API_KEY") or os.getenv("FXMD_API_KEY")
    if api_key:
        headers["X-API-Key"] = api_key

    request = Request(
        f"{base_url.rstrip('/')}/forex/{base_currency}/{quote_currency}?{urlencode(params)}",
        headers=headers,
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)

    rows = payload.get("data") if isinstance(payload, dict) else payload
    return fxmacrodata_rows_to_footprint_candles(rows, duration_seconds=duration_seconds)
