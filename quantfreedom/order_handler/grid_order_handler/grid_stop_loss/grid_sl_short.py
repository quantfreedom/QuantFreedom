from typing import NamedTuple


class GridSLExecShort(NamedTuple):
    short_sl_hit_exec: str = """
        candle_high = current_candle.high_price
        logger.debug(f"candle_high= {candle_high}")
        sl_hit_bool = sl_price < candle_high    
        """
