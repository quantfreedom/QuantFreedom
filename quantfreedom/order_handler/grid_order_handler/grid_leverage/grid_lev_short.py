from typing import NamedTuple


class GridLevExecShort(NamedTuple):
    short_get_bankruptcy_price_exec: str = "bankruptcy_price = average_entry * (leverage + 1) / leverage"
    short_get_liq_price_exec: str = "liq_price = average_entry * (1 + (1 / leverage) - self.mmr_pct)"
    short_liq_hit_bool_exec: str = """
    candle_high = current_candle[CandleBodyType.High]
    logger.debug(f"candle_high= {candle_high}")
    liq_hit_bool = liq_price < candle_high
    """
