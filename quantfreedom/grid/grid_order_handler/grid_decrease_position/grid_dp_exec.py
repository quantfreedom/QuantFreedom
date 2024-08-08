from typing import NamedTuple
from logging import getLogger

logger = getLogger()


class GridDPFuncs(NamedTuple):

    def long_get_pnl(
        self,
        average_entry: float,
        exit_price: float,
        position_size_asset: float,
    ):
        pnl = round((exit_price - average_entry) * position_size_asset, 2)
        logger.debug(f"Long PnL: {pnl}")
        return pnl

    def short_get_pnl(
        self,
        average_entry: float,
        exit_price: float,
        position_size_asset: float,
    ):
        pnl = round((exit_price - average_entry) * position_size_asset, 2)
        logger.debug(f"Short PnL: {pnl}")
        return pnl


Grid_DP_Funcs = GridDPFuncs()