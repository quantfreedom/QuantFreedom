from typing import NamedTuple


class GridLevExec(NamedTuple):
    long_get_bankruptcy_price_exec: str = "bankruptcy_price = average_entry * (leverage - 1) / leverage"
    long_get_liq_price_exec: str = "liq_price = average_entry * (1 - (1 / leverage) + mmr_pct)"
    long_liq_hit_bool_exec: str = """candle_low = current_candle[CandleBodyType.Low]
logger.debug(f"candle_low= {candle_low}")
liq_hit_bool = liq_price > candle_low"""

    short_get_bankruptcy_price_exec: str = "bankruptcy_price = average_entry * (leverage + 1) / leverage"
    short_get_liq_price_exec: str = "liq_price = average_entry * (1 + (1 / leverage) - mmr_pct)"
    short_liq_hit_bool_exec: str = """candle_high = current_candle[CandleBodyType.High]
logger.debug(f"candle_high= {candle_high}")
liq_hit_bool = liq_price < candle_high"""


Grid_Lev_Exec_Tuple = GridLevExec()
