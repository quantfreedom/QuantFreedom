from datetime import datetime, timedelta
import logging
import pandas as pd
import re


class DownloadCandles:
    """
    since and until need to be in milliseconds ... i suggest using int(pd.Timestamp('2023-09-25 13:30:00', unit='ms').timestamp()*1000)
    since_date_ms: this is always the past date
    until_date_ms: this is always the future date

    example would be i want to download candles since aug 2020 (1596240000000) until july 2022 (1656633600000)
    """

    def __init__(
        self,
        exchange,
        symbol,
        timeframe,
        exchange_name,
        candles_to_dl=None,
        since_date_ms=None,
        until_date_ms=None,
        limit=None,
    ):
        self.params = {}
        self.symbol = symbol
        self.since_date_ms = since_date_ms
        self.until_date_ms = until_date_ms
        self.limit = limit
        self.timeframe = timeframe
        self.exchange = exchange
        self.candles_to_dl = candles_to_dl

        if candles_to_dl is not None and candles_to_dl < 1000 and candles_to_dl % 1000 != 0:
            logging.error(
                "Candles to download must be 2000 or more in multiples of 1000. If you want less than 1000 candles then please put the limit at that number because the default limit is 1000"
            )
        elif since_date_ms is None and until_date_ms is not None:
            logging.error("You can't have an until date without having a since date")
        elif until_date_ms is not None and candles_to_dl is not None:
            logging.error("You can't have candles to dl and an until date")

        self.get_since_date_ms = self._get_since_date_ms
        self.get_until_date_ms = self._get_current_time

        if candles_to_dl is not None:
            if since_date_ms is not None:
                self.get_until_date_ms = self._candles_dl_return_until
            else:
                self.get_until_date_ms = self._get_current_time
                self.get_since_date_ms = self._candles_dl_return_since

        if until_date_ms is not None:
            self.get_until_date_ms = self._get_until_date_ms

        if exchange_name in ["binance"]:
            self.keep_or_remove_last_candle = self._remove_last_candle
            self.limit = 1000
        else:
            self.keep_or_remove_last_candle = self._keep_last_candle

        timeframe_tuple = re.match(r"([0-9]+)([a-z]+)", timeframe, re.I).groups()
        period_number = int(timeframe_tuple[0])
        period_unit = timeframe_tuple[1]
        number_minutes = period_number
        if period_unit == "h":
            number_minutes = int(period_number) * 60
        elif period_unit == "d":
            number_minutes = int(period_number) * 60 * 24

        self.bar_duration_millisecs = timedelta(minutes=number_minutes).seconds * 1000

    def _get_since_date_ms(self, **vargs):
        return self.since_date_ms - 1

    def _get_until_date_ms(self, **vargs):
        return self.until_date_ms

    def _get_current_time(self, **vargs):
        return int(datetime.now().timestamp() * 1000)

    def _candles_dl_times_bar_duration(self):
        return (self.candles_to_dl + 1) * self.bar_duration_millisecs

    def _candles_dl_return_since(self, date_ms):
        return date_ms - self._candles_dl_times_bar_duration()

    def _candles_dl_return_until(self, date_ms):
        return date_ms + self._candles_dl_times_bar_duration()

    def _ccxt_candle_download(self, since_date_ms):
        candles = self.exchange.fetch_ohlcv(
            symbol=self.symbol,
            timeframe=self.timeframe,
            since=since_date_ms,
            limit=self.limit,
            params=self.params,
        )
        return candles

    def candle_downloader(self):
        self.candles_list = []
        until_date_ms = self.get_until_date_ms()
        since_date_ms = self.get_since_date_ms(date_ms=until_date_ms)

        since_pd_timestamp = pd.to_datetime(since_date_ms, unit="ms")
        until_pd_timestamp = pd.to_datetime(until_date_ms, unit="ms")
        start_time = datetime.now()
        while since_date_ms < until_date_ms:
            logging.info(f"since_date_ms={since_pd_timestamp}, until_date_ms={until_pd_timestamp}")
            try:
                new_candles = self._ccxt_candle_download(since_date_ms=since_date_ms)
            except Exception as e:
                logging.error(f"Got exception -> {e}")
                break

            logging.info(f"Got {len(new_candles)} new candles for since={since_pd_timestamp}")
            if len(new_candles) == 0:
                logging.warning(f"fetch_ohlcv for since={since_pd_timestamp} got 0 candles")
                break
            elif len(new_candles) < 2:
                break
            else:
                self.candles_list.extend(new_candles)
                since_date_ms = self.candles_list[-1][0]
                since_pd_timestamp = pd.to_datetime(since_date_ms, unit="ms")
        loop_duration = round((datetime.now() - start_time).total_seconds() / 60, 2)
        print(f"It took {loop_duration} minutes to complete the candle download")
        return self._turn_into_pandas()

    def _turn_into_pandas(self):
        candles = pd.DataFrame(
            self.keep_or_remove_last_candle(),
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        candles["timestamp"] = pd.to_datetime(candles["timestamp"], unit="ms")
        return candles

    def _remove_last_candle(self):
        return self.candles_list[:-1]

    def _keep_last_candle(self):
        return self.candles_list
