from quantfreedom.core.enums import FootprintCandlesTuple
from typing import NamedTuple
import pandas as pd
import numpy as np
import os
import glob
from time import gmtime, strftime, perf_counter
from logging import getLogger

logger = getLogger()


class PrinterV3:
    candle_buy_count = 0
    candle_buy_vol = 0
    candle_close = 0
    candle_close_time = 0
    candle_cvd = 0
    candle_duration_s = 0
    candle_high = 0
    candle_high_low = 0
    candle_low = 0
    candle_open = 0
    candle_open_time = 0
    candle_sell_count = 0
    candle_sell_vol = 0
    candle_trade_count = 0
    candle_volume = 0
    prices_buy_count = 0
    prices_buy_vol = 0
    prices_delta = 0
    prices_delta_percent = 0
    prices_sell_count = 0
    prices_sell_vol = 0
    prices_trade_count = 0
    prices_volume = 0
    prices_real = 0
    since_timestamp = 0
    until_timestamp = 0
    tick_idx = 0
    num_row = 0

    def __init__(self):
        pass

    def custom_round_five(
        self,
        number: int,
    ):
        number = round(number)
        last_digit = number % 10

        if 0 <= last_digit <= 2:
            rounded_number = number - last_digit
        elif 3 <= last_digit <= 7:
            rounded_number = number - last_digit + 5
        elif 8 <= last_digit <= 9.99:
            rounded_number = number - last_digit + 10

        return rounded_number

    def set_data(
        self,
        since_timestamp: int,
        until_timestamp: int,
    ):
        if not (self.since_timestamp == since_timestamp and self.until_timestamp == until_timestamp):
            self.since_timestamp = since_timestamp
            self.until_timestamp = until_timestamp

            self.og_data = pd.read_hdf(
                "dbs/mar_apr.h5",
                key="BTCUSDT",
                where=f"timestamp >= {since_timestamp} & timestamp < {until_timestamp}",
            )

            self.og_data.reset_index(inplace=True)
            self.data_len = self.og_data.shape[0]

    def vol_candle_volume(self):

        # accumulate tick data until it reaches the given volume size
        while self.candle_volume < self.vol_size and self.tick_idx <= self.data_len - 1:
            self.candle_volume += self.usdt_size[self.tick_idx]
            self.tick_idx += 1

        self.candle_open_time = self.timestamp[self.open_row : self.tick_idx].min()
        self.candle_close_time = self.timestamp[self.open_row : self.tick_idx].max()
        self.candle_duration_s = (self.candle_close_time - self.candle_open_time) / 1000
        self.candle_open = self.prices[self.open_row]
        self.candle_high = self.prices[self.open_row : self.tick_idx].max()
        self.candle_low = self.prices[self.open_row : self.tick_idx].min()
        self.candle_close = self.prices[self.tick_idx - 1]
        self.candle_high_low = self.candle_high - self.candle_low

    def time_candle_volume(self):
        self.candle_open_time = self.timestamp[self.tick_idx] - (self.timestamp[self.tick_idx] % 100000)
        target_time = self.candle_open_time + self.time_frame_ms

        while self.tick_idx <= self.data_len - 1 and self.timestamp[self.tick_idx] < target_time:
            self.candle_volume += self.usdt_size[self.tick_idx]
            self.tick_idx += 1

        self.candle_duration_s = self.time_frame_ms / 1000
        self.candle_close_time = target_time - 1000
        self.candle_open = self.prices[self.open_row]
        self.candle_high = self.prices[self.open_row : self.tick_idx].max()
        self.candle_low = self.prices[self.open_row : self.tick_idx].min()
        self.candle_close = self.prices[self.tick_idx - 1]
        self.candle_high_low = self.candle_high - self.candle_low

    def set_new_candle_variables(self):
        self.candle_buy_vol = 0
        self.candle_buy_count = 0
        self.candle_sell_vol = 0
        self.candle_sell_count = 0
        self.candle_trade_count = 0

    def Convert_tick_data_volume_candles(
        self,
        tick_value: int,
        vol_size: str = None,
        time_frame: str = None,
    ):
        start = perf_counter()
        logger.info("Starting")
        self.data = self.og_data.copy().drop("datetime", axis=1)

        # changing the price data to the nearest tick value
        price_data = self.data["price"]
        price_data_div = price_data // tick_value
        price_data_modulo = price_data % tick_value
        price_ticked = price_data_div * tick_value
        self.prices = np.where(price_data_modulo < tick_value / 2, price_ticked, price_ticked + tick_value)

        # global timestamp, side, usdt_size
        self.timestamp = self.data["timestamp"].values
        self.side = self.data["is_buyer"].values
        self.usdt_size = self.data["usdt_size"].values

        # initialize variables
        self.open_row = 0
        imb_candles = np.full(shape=(1000000, 27), fill_value=np.nan, dtype=object)
        candle_counter = 0

        if vol_size:
            self.vol_size = self.user_vol_size(vol_size)
            self.create_candle = self.vol_candle_volume
        elif time_frame:
            self.time_frame_ms = self.user_time_frame(time_frame)
            self.create_candle = self.time_candle_volume

        # iterate through tick data
        while self.tick_idx < self.data_len:

            self.create_candle()

            self.set_new_candle_variables()

            # Combine the side, price, and USD size columns into a single array
            original_vol_candle = np.column_stack(
                tup=(
                    self.side[self.open_row : self.tick_idx],
                    self.prices[self.open_row : self.tick_idx],
                    self.usdt_size[self.open_row : self.tick_idx],
                )
            )

            # Find the unique prices in the original volume candle and sort them in ascending order
            uni_prices_in_og_vol_can = np.sort(np.unique(original_vol_candle[:, 1]))

            # Create an array of real prices, starting from the smallest unique price in the original volume candle and ending at the largest unique price plus 0.5
            self.prices_real = np.arange(uni_prices_in_og_vol_can[0], uni_prices_in_og_vol_can[-1] + 1, tick_value)

            len_real_prices = self.prices_real.size
            self.prices_buy_count = np.empty(len_real_prices)
            self.prices_buy_vol = np.empty(len_real_prices)
            self.prices_sell_count = np.empty(len_real_prices)
            self.prices_sell_vol = np.empty(len_real_prices)
            self.prices_delta = np.empty(len_real_prices)
            self.prices_delta_percent = np.empty(len_real_prices)
            self.prices_volume = np.empty(len_real_prices)
            self.prices_trade_count = np.empty(len_real_prices)

            for idx, real_price in enumerate(self.prices_real):
                uni_prices_indexes = original_vol_candle[:, 1] == real_price

                if uni_prices_indexes.any():
                    grouped_by_uni_prices = original_vol_candle[uni_prices_indexes]

                    sell_indexes = np.where(grouped_by_uni_prices[:, 0] == 0)
                    if sell_indexes:
                        sell_array = grouped_by_uni_prices[sell_indexes]
                        self.prices_sell_vol[idx] = sell_array[:, 2].sum()
                        self.prices_sell_count[idx] = sell_array.shape[0]
                    else:
                        self.prices_sell_vol[idx] = 0
                        self.prices_sell_count[idx] = 0

                    buy_indexes = np.where(grouped_by_uni_prices[:, 0] == 1)
                    if buy_indexes:
                        buy_array = grouped_by_uni_prices[buy_indexes]
                        self.prices_buy_vol[idx] = buy_array[:, 2].sum()
                        self.prices_buy_count[idx] = buy_array.shape[0]
                    else:
                        self.prices_buy_vol[idx] = 0
                        self.prices_buy_count[idx] = 0

                    self.prices_delta[idx] = self.prices_buy_vol[idx] - self.prices_sell_vol[idx]
                    self.prices_volume[idx] = self.prices_buy_vol[idx] + self.prices_sell_vol[idx]
                    self.prices_delta_percent[idx] = self.prices_delta[idx] / self.prices_volume[idx]
                    self.prices_trade_count[idx] = self.prices_buy_count[idx] + self.prices_sell_count[idx]

                else:
                    self.prices_buy_vol[idx] = 0
                    self.prices_buy_count[idx] = 0
                    self.prices_sell_vol[idx] = 0
                    self.prices_sell_count[idx] = 0
                    self.prices_delta[idx] = 0
                    self.prices_delta_percent[idx] = 0
                    self.prices_volume[idx] = 0
                    self.prices_trade_count[idx] = 0

            # Aggregate volumes and counts
            self.candle_trade_count = self.prices_trade_count.sum()
            self.candle_sell_vol = self.prices_sell_vol.sum()
            self.candle_sell_count = self.prices_sell_count.sum()
            self.candle_buy_vol = self.prices_buy_vol.sum()
            self.candle_buy_count = self.prices_buy_count.sum()
            self.candle_volume = self.prices_volume.sum()

            self.candle_delta = self.candle_buy_vol - self.candle_sell_vol
            self.candle_delta_percent = self.candle_delta / self.candle_volume
            self.candle_cvd = self.candle_cvd + self.candle_delta

            candle_poc_vol = self.prices_volume.max()
            candle_poc_index = np.where(self.prices_volume == candle_poc_vol)[0][0]
            self.candle_poc = self.prices_real[candle_poc_index]

            imb_candles[candle_counter, 0] = self.candle_open_time
            imb_candles[candle_counter, 1] = self.candle_close_time
            imb_candles[candle_counter, 2] = round(self.candle_duration_s, 3)
            imb_candles[candle_counter, 3] = round(self.candle_open)
            imb_candles[candle_counter, 4] = round(self.candle_high)
            imb_candles[candle_counter, 5] = round(self.candle_low)
            imb_candles[candle_counter, 6] = round(self.candle_close)
            imb_candles[candle_counter, 7] = round(self.candle_volume, 2)
            imb_candles[candle_counter, 8] = round(self.candle_trade_count)
            imb_candles[candle_counter, 9] = round(self.candle_delta, 2)
            imb_candles[candle_counter, 10] = round(self.candle_delta_percent, 4)
            imb_candles[candle_counter, 11] = round(self.candle_buy_vol, 2)
            imb_candles[candle_counter, 12] = round(self.candle_buy_count)
            imb_candles[candle_counter, 13] = round(self.candle_sell_vol, 2)
            imb_candles[candle_counter, 14] = round(self.candle_sell_count)
            imb_candles[candle_counter, 15] = round(self.candle_cvd, 2)
            imb_candles[candle_counter, 16] = round(self.candle_poc)
            imb_candles[candle_counter, 17] = round(self.candle_high_low)
            imb_candles[candle_counter, 18] = np.around(self.prices_real)
            imb_candles[candle_counter, 19] = np.around(self.prices_buy_vol, 2)
            imb_candles[candle_counter, 20] = np.around(self.prices_buy_count)
            imb_candles[candle_counter, 21] = np.around(self.prices_sell_vol, 2)
            imb_candles[candle_counter, 22] = np.around(self.prices_sell_count)
            imb_candles[candle_counter, 23] = np.around(self.prices_delta, 2)
            imb_candles[candle_counter, 24] = np.around(self.prices_delta_percent, 4)
            imb_candles[candle_counter, 25] = np.around(self.prices_volume, 2)
            imb_candles[candle_counter, 26] = np.around(self.prices_trade_count)

            self.open_row = self.tick_idx
            candle_counter += 1
            self.candle_volume = 0

        final_imb_candles = imb_candles[:candle_counter]

        Volume_Candles_Tuple = FootprintCandlesTuple(
            candle_open_datetimes=final_imb_candles[:, 0].astype("datetime64[ms]"),
            candle_open_timestamps=final_imb_candles[:, 0].astype(np.int64),
            candle_close_datetimes=final_imb_candles[:, 1].astype("datetime64[ms]"),
            candle_close_timestamps=final_imb_candles[:, 1].astype(np.int64),
            candle_durations_seconds=final_imb_candles[:, 2].astype(np.float_),
            candle_open_prices=final_imb_candles[:, 3].astype(np.float_),
            candle_high_prices=final_imb_candles[:, 4].astype(np.float_),
            candle_low_prices=final_imb_candles[:, 5].astype(np.float_),
            candle_close_prices=final_imb_candles[:, 6].astype(np.float_),
            candle_asset_volumes=final_imb_candles[:, 7].astype(np.float_) / final_imb_candles[:, 6].astype(np.float_),
            candle_usdt_volumes=final_imb_candles[:, 7].astype(np.float_),
            candle_trade_counts=final_imb_candles[:, 8].astype(np.int_),
            candle_deltas=final_imb_candles[:, 9].astype(np.float_),
            candle_delta_percents=final_imb_candles[:, 10].astype(np.float_),
            candle_buy_volumes=final_imb_candles[:, 11].astype(np.float_),
            candle_buy_counts=final_imb_candles[:, 12].astype(np.int_),
            candle_sell_volumes=final_imb_candles[:, 13].astype(np.float_),
            candle_sell_counts=final_imb_candles[:, 14].astype(np.int_),
            candle_cvds=final_imb_candles[:, 15].astype(np.float_),
            candle_pocs=final_imb_candles[:, 16].astype(np.float_),
            candle_high_lows=final_imb_candles[:, 17].astype(np.float_),
            prices_tuple=tuple(final_imb_candles[:, 18]),
            prices_buy_vol_tuple=tuple(final_imb_candles[:, 19]),
            prices_buy_count_tuple=tuple(final_imb_candles[:, 20]),
            prices_sell_vol_tuple=tuple(final_imb_candles[:, 21]),
            prices_sell_count_tuple=tuple(final_imb_candles[:, 22]),
            prices_delta_tuple=tuple(final_imb_candles[:, 23]),
            prices_delta_percent_tuple=tuple(final_imb_candles[:, 24]),
            prices_volume_tuple=tuple(final_imb_candles[:, 25]),
            prices_trade_count_tuple=tuple(final_imb_candles[:, 26]),
        )

        end = perf_counter()
        logger.info(strftime("%M:%S func", gmtime(int(end - start))))

        return Volume_Candles_Tuple

    def user_time_frame(self, split_me: str):
        time_frame = split_me.split("-")
        if time_frame[1] == "m":
            return float(time_frame[0]) * 60000
        elif time_frame[1] == "h":
            return float(time_frame[0]) * 3600000

    def user_vol_size(
        self,
        split_me: str,
    ):
        vol_size = split_me.split("-")
        if vol_size[1] == "m":
            return float(vol_size[0]) * 1000000
        elif vol_size[1] == "k":
            return float(vol_size[0]) * 1000

    def concat_btcusdt_csv_files(self):
        all_files = glob.glob(os.path.join("BTCUSDT*.csv"))
        data = pd.concat(
            (
                pd.read_csv(
                    f,
                    names=[
                        "agg_trade_id",
                        "price",
                        "asset_size",
                        "first_trade_id",
                        "last_trade_id",
                        "timestamp",
                        "is_buyer",
                    ],
                    header=0,
                )
                for f in all_files
            ),
            ignore_index=True,
        )
        data.drop(columns=["agg_trade_id", "first_trade_id", "last_trade_id"], inplace=True)
        data["is_buyer"] = np.where(data.is_buyer == False, 1, 0)  # 1 = Buy 0 = Sell
        data.sort_values(by=["timestamp"], ignore_index=True, inplace=True)
        data.price = np.around(data.price.to_numpy())
        data = data.groupby(["timestamp", "price", "is_buyer"])["asset_size"].sum().reset_index()
        data["usdt_size"] = round(data.price * data.asset_size, 3)
        data["datetime"] = pd.to_datetime(data["timestamp"], unit="ms")
        data = data[["datetime", "timestamp", "price", "asset_size", "usdt_size", "is_buyer"]]
        data.to_csv("", index=False)

    def create_data_hdf(
        self,
        data: pd.DataFrame,
        key: str,
        db_name: str,
    ):
        data.to_hdf(db_name, key=key, data_columns=True, index=True, format="table")

    def append_to_database(
        self,
        db_name: str,
        data: pd.DataFrame,
    ):
        store = pd.HDFStore(db_name)
        store.put("BTCUSDT", data, format="t", append=True, data_columns=True)

    # pd.read_csv("2024-03-01-11.csv").to_hdf("dbs/mar_apr.h5", key="BTCUSDT", data_columns=True, format="table", index=False)
