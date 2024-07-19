from typing import NamedTuple


class GridSLExec(NamedTuple):
    long_sl_hit_exec: str = """candle_low = current_candle.low_price
logger.debug(f"candle_low= {candle_low}")
sl_hit_bool = sl_price > candle_low
"""

    short_sl_hit_exec: str = """candle_high = current_candle.high_price
logger.debug(f"candle_high= {candle_high}")
sl_hit_bool = sl_price < candle_high"""

Grid_SL_Exec_Tuple = GridSLExec()