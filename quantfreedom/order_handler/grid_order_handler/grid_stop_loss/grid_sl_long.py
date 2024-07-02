from typing import NamedTuple


class GridSLExecLong(NamedTuple):
    sl_hit_exec: str = """
        candle_low = current_candle.low_price
        logger.debug(f"candle_low= {candle_low}")
        sl_hit_bool = sl_price > candle_low    
        """
